#!/usr/bin/env python3
"""
FastAPI Web Interface for Immich Snapchat Importer - FIXED VERSION
Provides a user-friendly web UI with improved progress tracking
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime
import uvicorn

# Import our processing modules
from process_memories import (
    extract_metadata_from_json,
    extract_metadata_from_html,
    MemoryDownloader,
    MemoryProcessor,
    upload_to_immich,
    generate_report,
    load_config
)

# Import repair functionality
from repair_immich_metadata import ImmichMetadataRepairer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist BEFORE creating app
UPLOAD_DIR = Path("./uploads")
WORK_DIR = Path("./work")
STATIC_DIR = Path("./static")
UPLOAD_DIR.mkdir(exist_ok=True)
WORK_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="Immich Snapchat Importer",
    description="Import Snapchat Memories to Immich with metadata preservation",
    version="2.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Global state management
class ImportState:
    def __init__(self):
        self.active_imports = {}
        self.websocket_clients = []
    
    def add_import(self, job_id: str, info: dict):
        self.active_imports[job_id] = info
    
    def update_import(self, job_id: str, updates: dict):
        if job_id in self.active_imports:
            self.active_imports[job_id].update(updates)
    
    def get_import(self, job_id: str):
        return self.active_imports.get(job_id)
    
    async def broadcast(self, message: dict):
        """Send message to all connected WebSocket clients"""
        disconnected = []
        for ws in self.websocket_clients:
            try:
                await ws.send_json(message)
            except:
                disconnected.append(ws)
        
        for ws in disconnected:
            self.websocket_clients.remove(ws)

state = ImportState()

# Data models
class ImportConfig(BaseModel):
    immich_url: Optional[str] = None
    api_key: Optional[str] = None
    delay: float = 2.0
    skip_upload: bool = False

class RepairRequest(BaseModel):
    metadata_file: str
    immich_url: str
    api_key: str
    dry_run: bool = False

class ProcessOnlyRequest(BaseModel):
    metadata_file: str
    immich_url: Optional[str] = None
    api_key: Optional[str] = None

class TestConnectionRequest(BaseModel):
    immich_url: str
    api_key: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    from webapp_html import get_improved_html
    return HTMLResponse(content=get_improved_html(), status_code=200)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload Snapchat export file (JSON or HTML)"""
    try:
        if not (file.filename.endswith('.json') or file.filename.endswith('.html')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a .json or .html file"
            )
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Uploaded file: {file.filename} ({len(content)} bytes)")
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        }
    
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/metadata")
async def upload_metadata_file(file: UploadFile = File(...)):
    """Upload metadata JSON file to work directory"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a .json file"
            )
        
        file_path = WORK_DIR / file.filename
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Uploaded metadata file: {file.filename} ({len(content)} bytes)")
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        }
    
    except Exception as e:
        logger.error(f"Metadata upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import/start")
async def start_import(
    filename: str,
    config: ImportConfig,
    background_tasks: BackgroundTasks
):
    """Start a new import job"""
    try:
        input_file = UPLOAD_DIR / filename
        if not input_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        job_id = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job_info = {
            "job_id": job_id,
            "filename": filename,
            "status": "queued",
            "progress": 0,
            "current_phase": "Initializing",
            "message": "Import job created",
            "started_at": datetime.now().isoformat(),
            "config": config.dict()
        }
        
        state.add_import(job_id, job_info)
        
        background_tasks.add_task(
            run_import_job,
            job_id,
            str(input_file),
            config
        )
        
        return {"job_id": job_id, "status": "queued"}
    
    except Exception as e:
        logger.error(f"Failed to start import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_import_job(job_id: str, input_file: str, config: ImportConfig):
    """Background task to run the import process"""
    try:
        # Phase 1: Extract metadata
        state.update_import(job_id, {
            "status": "extracting",
            "current_phase": "Extracting Metadata",
            "progress": 10
        })
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "status": "extracting",
            "progress": 10,
            "message": "Extracting metadata from Snapchat export..."
        })
        
        input_path = Path(input_file)
        base_name = input_path.stem
        
        if input_file.endswith('.json'):
            extract_function = extract_metadata_from_json
        else:
            extract_function = extract_metadata_from_html
        
        metadata_json = WORK_DIR / f"{base_name}_metadata.json"
        download_folder = WORK_DIR / f"{base_name}_downloads"
        output_folder = WORK_DIR / f"{base_name}_processed"
        
        metadata = extract_function(input_file, str(metadata_json))
        if not metadata:
            raise Exception("Failed to extract metadata")
        
        state.update_import(job_id, {
            "progress": 20,
            "message": f"Found {metadata['total_memories']} memories"
        })
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "progress": 20,
            "message": f"Found {metadata['total_memories']} memories"
        })
        
        # Phase 2: Download files
        state.update_import(job_id, {
            "status": "downloading",
            "current_phase": "Downloading Files",
            "progress": 25
        })
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "status": "downloading",
            "progress": 25,
            "message": "Downloading files from Snapchat..."
        })
        
        downloader = MemoryDownloader(metadata, str(download_folder), config.delay)
        success_count, failed_count = downloader.download_all()
        
        if success_count == 0:
            raise Exception("No files downloaded successfully")
        
        state.update_import(job_id, {
            "progress": 50,
            "message": f"Downloaded {success_count} files"
        })
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "progress": 50,
            "message": f"Downloaded {success_count} files"
        })
        
        # Phase 3: Process files
        state.update_import(job_id, {
            "status": "processing",
            "current_phase": "Processing & Applying Metadata",
            "progress": 55
        })
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "status": "processing",
            "progress": 55,
            "message": "Processing files and applying metadata..."
        })
        
        processor = MemoryProcessor(str(metadata_json), str(download_folder), str(output_folder))
        processor.process_all()
        
        state.update_import(job_id, {
            "progress": 75,
            "message": "Files processed successfully"
        })
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "progress": 75,
            "message": "Files processed successfully"
        })
        
        report = generate_report(str(metadata_json), str(output_folder))
        
        # Phase 4: Upload to Immich
        if not config.skip_upload and config.immich_url and config.api_key:
            state.update_import(job_id, {
                "status": "uploading",
                "current_phase": "Uploading to Immich",
                "progress": 80
            })
            await state.broadcast({
                "type": "progress",
                "job_id": job_id,
                "status": "uploading",
                "progress": 80,
                "message": "Uploading to Immich..."
            })
            
            upload_success, upload_failed, upload_skipped = upload_to_immich(
                str(output_folder),
                str(metadata_json),
                config.immich_url,
                config.api_key
            )
            
            state.update_import(job_id, {
                "progress": 95,
                "message": f"Uploaded {upload_success} files to Immich"
            })
            await state.broadcast({
                "type": "progress",
                "job_id": job_id,
                "progress": 95,
                "message": f"Uploaded {upload_success} files"
            })
        
        # Complete
        state.update_import(job_id, {
            "status": "complete",
            "current_phase": "Complete",
            "progress": 100,
            "message": "Import completed successfully",
            "completed_at": datetime.now().isoformat(),
            "stats": report if report else {}
        })
        await state.broadcast({
            "type": "complete",
            "job_id": job_id,
            "progress": 100,
            "message": "Import completed successfully!",
            "stats": report if report else {}
        })
    
    except Exception as e:
        logger.error(f"Import job {job_id} failed: {e}")
        state.update_import(job_id, {
            "status": "failed",
            "current_phase": "Failed",
            "message": str(e),
            "failed_at": datetime.now().isoformat()
        })
        await state.broadcast({
            "type": "error",
            "job_id": job_id,
            "message": f"Import failed: {str(e)}"
        })

async def run_repair_job(job_id, metadata_file, immich_url, api_key, dry_run):
    """Background task for metadata repair - FIXED VERSION"""
    try:
        state.update_import(job_id, {
            "status": "running",
            "progress": 5,
            "message": "Initializing repair job...",
            "current_item": 0,
            "total_items": 0
        })
        
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "progress": 5,
            "message": "Initializing repair job...",
            "details": {}
        })
        
        # Create repairer
        repairer = ImmichMetadataRepairer(
            metadata_file,
            immich_url,
            api_key
        )
        
        # Create async progress callback
        async def async_progress_callback(progress, message, details):
            state.update_import(job_id, {
                "progress": progress,
                "message": message,
                "current_item": details.get("index", 0) if details else 0,
                "total_items": details.get("total", 0) if details else 0
            })
            
            await state.broadcast({
                "type": "progress",
                "job_id": job_id,
                "progress": progress,
                "message": message,
                "details": details or {}
            })
        
        # Wrapper for sync calls from repair_all
        def progress_callback(progress, message, details):
            # Create task in the event loop
            try:
                asyncio.create_task(async_progress_callback(progress, message, details))
            except RuntimeError:
                # If we're not in an async context, use run_coroutine_threadsafe
                loop = asyncio.get_event_loop()
                asyncio.run_coroutine_threadsafe(
                    async_progress_callback(progress, message, details),
                    loop
                )
        
        # Run repair with progress callback
        checked, needs_repair, repaired = repairer.repair_all(
            dry_run=dry_run,
            progress_callback=progress_callback
        )
        
        # Complete
        state.update_import(job_id, {
            "status": "complete",
            "progress": 100,
            "message": f"Repair complete! {'Would repair' if dry_run else 'Repaired'} {needs_repair} assets",
            "completed_at": datetime.now().isoformat(),
            "stats": {
                "checked": checked,
                "needs_repair": needs_repair,
                "repaired": repaired if not dry_run else 0,
                "dry_run": dry_run
            }
        })
        
        await state.broadcast({
            "type": "complete",
            "job_id": job_id,
            "progress": 100,
            "message": f"Repair complete! {'Would repair' if dry_run else 'Repaired'} {needs_repair} assets",
            "stats": {
                "checked": checked,
                "needs_repair": needs_repair,
                "repaired": repaired if not dry_run else 0
            }
        })
    
    except Exception as e:
        logger.error(f"Repair job {job_id} failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        state.update_import(job_id, {
            "status": "failed",
            "message": str(e),
            "failed_at": datetime.now().isoformat()
        })
        await state.broadcast({
            "type": "error",
            "job_id": job_id,
            "message": f"Repair failed: {str(e)}"
        })

async def run_process_only_job(job_id, metadata_file, immich_url, api_key):
    """Background task for process-only (already downloaded files)"""
    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        base_name = Path(metadata_file).stem.replace('_metadata', '')
        download_folder = WORK_DIR / f"{base_name}_downloads"
        output_folder = WORK_DIR / f"{base_name}_processed"
        
        if not download_folder.exists():
            raise Exception(f"Download folder not found: {download_folder}")
        
        state.update_import(job_id, {
            "status": "processing",
            "progress": 20,
            "message": "Processing files..."
        })
        
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "progress": 20,
            "message": "Processing files and applying metadata..."
        })
        
        processor = MemoryProcessor(metadata_file, str(download_folder), str(output_folder))
        processor.process_all()
        
        state.update_import(job_id, {
            "progress": 60,
            "message": "Files processed successfully"
        })
        
        await state.broadcast({
            "type": "progress",
            "job_id": job_id,
            "progress": 60,
            "message": "Files processed successfully"
        })
        
        report = generate_report(metadata_file, str(output_folder))
        
        if immich_url and api_key:
            state.update_import(job_id, {
                "status": "uploading",
                "progress": 70,
                "message": "Uploading to Immich..."
            })
            
            await state.broadcast({
                "type": "progress",
                "job_id": job_id,
                "progress": 70,
                "message": "Uploading to Immich..."
            })
            
            upload_success, upload_failed, upload_skipped = upload_to_immich(
                str(output_folder),
                metadata_file,
                immich_url,
                api_key
            )
            
            state.update_import(job_id, {
                "progress": 95,
                "message": f"Uploaded {upload_success} files"
            })
            
            await state.broadcast({
                "type": "progress",
                "job_id": job_id,
                "progress": 95,
                "message": f"Uploaded {upload_success} files"
            })
        
        state.update_import(job_id, {
            "status": "complete",
            "progress": 100,
            "message": "Processing complete!",
            "completed_at": datetime.now().isoformat(),
            "stats": report if report else {}
        })
        
        await state.broadcast({
            "type": "complete",
            "job_id": job_id,
            "progress": 100,
            "message": "Processing complete!",
            "stats": report if report else {}
        })
    
    except Exception as e:
        logger.error(f"Process job {job_id} failed: {e}")
        state.update_import(job_id, {
            "status": "failed",
            "message": str(e),
            "failed_at": datetime.now().isoformat()
        })
        await state.broadcast({
            "type": "error",
            "job_id": job_id,
            "message": f"Processing failed: {str(e)}"
        })

@app.get("/api/import/status/{job_id}")
async def get_import_status(job_id: str):
    """Get status of an import job"""
    job_info = state.get_import(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_info

@app.get("/api/import/list")
async def list_imports():
    """List all import jobs"""
    return {"imports": list(state.active_imports.values())}

@app.post("/api/repair/start")
async def start_repair(
    request: RepairRequest,
    background_tasks: BackgroundTasks
):
    """Start Immich metadata repair job"""
    try:
        metadata_path = WORK_DIR / request.metadata_file
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Metadata file not found")
        
        job_id = f"repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job_info = {
            "job_id": job_id,
            "type": "repair",
            "status": "queued",
            "progress": 0,
            "message": "Starting metadata repair...",
            "started_at": datetime.now().isoformat(),
            "config": {
                "metadata_file": request.metadata_file,
                "immich_url": request.immich_url,
                "dry_run": request.dry_run
            }
        }
        
        state.add_import(job_id, job_info)
        
        background_tasks.add_task(
            run_repair_job,
            job_id,
            str(metadata_path),
            request.immich_url,
            request.api_key,
            request.dry_run
        )
        
        return {"job_id": job_id, "status": "queued"}
    
    except Exception as e:
        logger.error(f"Failed to start repair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/start")
async def start_process_only(
    request: ProcessOnlyRequest,
    background_tasks: BackgroundTasks
):
    """Start process-only job"""
    try:
        metadata_path = WORK_DIR / request.metadata_file
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Metadata file not found")
        
        job_id = f"process_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job_info = {
            "job_id": job_id,
            "type": "process",
            "status": "queued",
            "progress": 0,
            "message": "Starting processing...",
            "started_at": datetime.now().isoformat(),
            "config": {
                "metadata_file": request.metadata_file,
                "immich_url": request.immich_url
            }
        }
        
        state.add_import(job_id, job_info)
        
        background_tasks.add_task(
            run_process_only_job,
            job_id,
            str(metadata_path),
            request.immich_url,
            request.api_key
        )
        
        return {"job_id": job_id, "status": "queued"}
    
    except Exception as e:
        logger.error(f"Failed to start processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metadata/list")
async def list_metadata_files():
    """List available metadata files"""
    try:
        metadata_files = []
        for file in WORK_DIR.glob("*_metadata.json"):
            metadata_files.append({
                "filename": file.name,
                "size": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        return {"files": metadata_files}
    except Exception as e:
        logger.error(f"Failed to list metadata files: {e}")
        return {"files": []}

@app.post("/api/repair/test-connection")
async def test_immich_connection(request: TestConnectionRequest):
    """Test Immich API connection"""
    try:
        import requests
        
        url = request.immich_url.rstrip('/')
        if not url.endswith('/api'):
            url = f"{url}/api"
        
        headers = {
            'x-api-key': request.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{url}/server/version",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                version_data = response.json()
                major = version_data.get('major', '?')
                minor = version_data.get('minor', '?')
                patch = version_data.get('patch', '?')
                version_str = f"{major}.{minor}.{patch}"
                message = f"Successfully connected to Immich (Version: {version_str})"
            except:
                message = "Successfully connected to Immich"
                version_str = None
            
            user_email = "user"
            try:
                user_response = requests.get(
                    f"{url}/user/me",
                    headers=headers,
                    timeout=10
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_email = user_data.get('email', user_data.get('name', 'user'))
            except:
                pass
            
            result = {
                "status": "success",
                "connected": True,
                "user": user_email,
                "message": message
            }
            if 'version_str' in locals() and version_str:
                result["version"] = version_str
            return result
        elif response.status_code == 401:
            return {
                "status": "error",
                "connected": False,
                "message": "Authentication failed. Please check your API key."
            }
        else:
            return {
                "status": "error",
                "connected": False,
                "message": f"Connection failed: {response.status_code}"
            }
    
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "status": "error",
            "connected": False,
            "message": f"Connection test failed: {str(e)}"
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    state.websocket_clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        state.websocket_clients.remove(websocket)

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    config = load_config()
    if config.get('immich', {}).get('api_key'):
        key = config['immich']['api_key']
        config['immich']['api_key'] = f"{'*' * (len(key) - 4)}{key[-4:]}" if len(key) > 4 else "***"
    return config

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_imports": len(state.active_imports),
        "connected_clients": len(state.websocket_clients)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)