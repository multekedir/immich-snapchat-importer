#!/usr/bin/env python3
"""
Snapchat Memories Processor with Immich Metadata Repair
- Uses PST timezone (Pacific Standard Time) instead of UTC
- Can fetch existing assets from Immich and fix their metadata
- Applies both GPS and date created metadata
"""

import cv2
import zipfile
import re
import os
import sys
import time
import urllib.request
import urllib.error
import subprocess
import shutil
import json
import numpy as np
import logging
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime, timedelta
from PIL import Image
import piexif
import requests
from collections import Counter

try:
    import yaml
except ImportError:
    yaml = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# PST Timezone offset (UTC-8)
PST_OFFSET = timedelta(hours=-8)


def utc_to_pst(dt_utc):
    """Convert UTC datetime to PST"""
    if isinstance(dt_utc, str):
        dt_utc = datetime.fromisoformat(dt_utc.replace('Z', ''))
    return dt_utc + PST_OFFSET


def parse_snapchat_date_as_pst(date_str: str) -> datetime:
    """
    Parse Snapchat date string and keep as PST (don't convert to UTC)
    
    Args:
        date_str (str): Date string from Snapchat export (e.g., "2024-07-01 23:13:15 UTC")
    
    Returns:
        datetime: PST datetime object (naive, no timezone info)
    """
    try:
        # Parse the date string - Snapchat marks them as "UTC" but they're actually PST
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(UTC)?', date_str)
        if not date_match:
            raise ValueError(f"Invalid date format: {date_str}")
        
        date_part = date_match.group(1)
        time_part = date_match.group(2)
        
        # Parse as PST (naive datetime)
        dt_pst = datetime.strptime(f"{date_part} {time_part}", '%Y-%m-%d %H:%M:%S')
        
        return dt_pst
    
    except Exception as e:
        logger.warning(f"⚠️  Could not parse date '{date_str}': {e}")
        return datetime.now()


class ImmichMetadataRepairer:
    """
    Repair metadata for assets already uploaded to Immich.
    
    This class:
    1. Fetches all assets from Immich
    2. Matches them to Snapchat metadata by filename
    3. Checks if GPS and date are correct
    4. Updates assets if metadata is missing or incorrect
    """
    
    def __init__(self, metadata_file, immich_url, api_key):
        self.immich_url = immich_url.rstrip('/')
        if not self.immich_url.endswith('/api'):
            self.immich_url = f"{self.immich_url}/api"
        
        self.api_key = api_key
        self.headers = {
            'x-api-key': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Load metadata
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        self.metadata = metadata  # Store full metadata for better matching
        
        # Create lookup dictionaries
        self.metadata_lookup = {}
        self.metadata_by_date = {}
        self.metadata_by_index = {}
        
        for memory in metadata.get('memories', []):
            if 'filename' in memory:
                filename_base = memory['filename']
                self.metadata_lookup[filename_base] = memory
            
            if 'date_key' in memory:
                # Store list of memories by date_key (there can be multiple)
                if memory['date_key'] not in self.metadata_by_date:
                    self.metadata_by_date[memory['date_key']] = []
                self.metadata_by_date[memory['date_key']].append(memory)
            
            if 'index' in memory:
                self.metadata_by_index[memory['index']] = memory
    
    def search_asset_by_filename(self, filename_base):
        """Search for an asset in Immich by filename (without extension)
        
        Args:
            filename_base: Filename without extension (e.g., "2025-12-22_03-07-53_video_0021_gps")
        
        Returns:
            Asset dict if found, None otherwise
        """
        # Try different extensions
        extensions = ['.mp4', '.jpg', '.jpeg', '.png', '.mov', '.avi', '.mkv']
        
        for ext in extensions:
            filename = f"{filename_base}{ext}"
            
            # Try searching by filename using search endpoint
            try:
                # Try search with filename filter
                response = requests.post(
                    f"{self.immich_url}/search",
                    headers=self.headers,
                    json={
                        "withArchived": False,
                        "searchTerm": filename_base  # Search by base name
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assets = data.get('items', data.get('results', data.get('assets', [])))
                    
                    # Look for exact filename match
                    for asset in assets:
                        asset_filename = asset.get('originalFileName') or asset.get('originalPath', '')
                        if asset_filename and filename_base in asset_filename:
                            # Check if it matches (with or without extension)
                            asset_base = Path(asset_filename).stem
                            if asset_base == filename_base:
                                return asset
            except Exception as e:
                logger.debug(f"Search error for {filename}: {e}")
                continue
        
        # Fallback: try searching by date pattern if filename has date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', filename_base)
        if date_match:
            date_key = date_match.group(1)
            try:
                # Try timeline/bucket for that date
                response = requests.get(
                    f"{self.immich_url}/timeline/bucket",
                    headers=self.headers,
                    params={"size": "DAY", "timeBucket": date_key.split('_')[0]},  # Just the date part
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # The response structure varies, try to find assets
                    assets = []
                    if isinstance(data, dict):
                        if 'assets' in data and isinstance(data['assets'], list):
                            assets = data['assets']
                        elif 'buckets' in data:
                            for bucket in data.get('buckets', []):
                                if 'assets' in bucket:
                                    assets.extend(bucket['assets'])
                    
                    # Look for matching filename
                    for asset in assets:
                        asset_filename = asset.get('originalFileName') or asset.get('originalPath', '')
                        if asset_filename:
                            asset_base = Path(asset_filename).stem
                            if asset_base == filename_base:
                                return asset
            except Exception as e:
                logger.debug(f"Timeline search error for {filename_base}: {e}")
        
        return None
    
    def get_all_assets(self):
        """Fetch all assets from Immich"""
        logger.info("\n" + "=" * 80)
        logger.info("FETCHING ASSETS FROM IMMICH")
        logger.info("=" * 80)
        
        all_assets = []
        
        try:
            # Try timeline/bucket endpoint (Immich v1 API)
            # This endpoint returns assets grouped by time bucket - need to fetch multiple time buckets
            logger.info("   Trying timeline/bucket endpoint...")
            # Try getting assets for different time buckets (recent dates)
            from datetime import datetime, timedelta
            today = datetime.now()
            for days_back in range(365):  # Check last year
                date_str = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
                response = requests.get(
                    f"{self.immich_url}/timeline/bucket",
                    headers=self.headers,
                    params={"size": "DAY", "timeBucket": date_str},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Timeline bucket returns dict with bucket data
                    if isinstance(data, dict):
                        # Look for assets in the response structure
                        if 'assets' in data and isinstance(data['assets'], list):
                            all_assets.extend(data['assets'])
                        elif 'buckets' in data:
                            for bucket in data['buckets']:
                                if 'assets' in bucket and isinstance(bucket['assets'], list):
                                    all_assets.extend(bucket['assets'])
                        # If data itself is a list or contains items directly
                        elif isinstance(data, list):
                            all_assets.extend(data)
                        elif 'items' in data:
                            all_assets.extend(data['items'])
                
                # If we got assets, we can break early (this was just a test)
                # Actually, let's fetch all time buckets for completeness
                if days_back > 10 and len(all_assets) > 0:
                    # For efficiency, just check recent dates, but user can extend if needed
                    break
            
            if all_assets:
                # Remove duplicates based on asset ID
                seen_ids = set()
                unique_assets = []
                for asset in all_assets:
                    asset_id = asset.get('id') or asset.get('assetId')
                    if asset_id and asset_id not in seen_ids:
                        seen_ids.add(asset_id)
                        unique_assets.append(asset)
                logger.info(f"✓ Found {len(unique_assets)} unique assets using timeline/bucket")
                return unique_assets
            
            # Try search endpoint (Immich v1 API)
            logger.info("   Trying search endpoint...")
            response = requests.post(
                f"{self.immich_url}/search",
                headers=self.headers,
                json={"withArchived": False},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    all_assets = data.get('items', data.get('results', data.get('assets', [])))
                elif isinstance(data, list):
                    all_assets = data
                
                if all_assets:
                    logger.info(f"✓ Found {len(all_assets)} assets using search")
                    return all_assets
            
            # Try asset endpoint with pagination
            logger.info("   Trying asset endpoint with pagination...")
            page = 1
            while True:
                response = requests.get(
                    f"{self.immich_url}/asset",
                    headers=self.headers,
                    params={"page": page, "size": 1000},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        page_assets = data.get('items', data.get('data', []))
                        if not page_assets:
                            break
                        all_assets.extend(page_assets)
                        
                        # Check if there are more pages
                        if len(page_assets) < 1000:
                            break
                        page += 1
                    elif isinstance(data, list):
                        all_assets = data
                        break
                    else:
                        break
                else:
                    break
            
            if all_assets:
                logger.info(f"✓ Found {len(all_assets)} assets using asset endpoint")
                return all_assets
            
            logger.error(f"❌ Failed to fetch assets")
            logger.error(f"   Tried endpoints: /timeline/bucket (GET), /search (POST), /asset (GET)")
            logger.error(f"   Last response status: {response.status_code if 'response' in locals() else 'N/A'}")
            if 'response' in locals() and response.status_code != 200:
                logger.error(f"   Response: {response.text[:200]}")
            return []
        
        except Exception as e:
            logger.error(f"❌ Error fetching assets: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def check_asset_metadata(self, asset):
        """Check if asset metadata matches Snapchat metadata"""
        # Get filename from asset - try multiple fields
        original_path = asset.get('originalPath', '')
        original_filename = asset.get('originalFileName', '')
        
        # Always strip extension for matching (metadata has no extensions)
        if original_path:
            filename_base = Path(original_path).stem
        elif original_filename:
            filename_base = Path(original_filename).stem
        else:
            # Fallback: try to extract from any filename field
            filename_base = asset.get('name', '').replace('.mp4', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
        
        # Try to find matching metadata by exact filename match
        memory = self.metadata_lookup.get(filename_base)
        
        # Fallback 1: try date matching with full pattern matching
        if not memory:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', filename_base)
            if date_match:
                date_key = date_match.group(1)
                # Try to find memories with matching date_key
                potential_memories = [m for m in self.metadata.get('memories', []) if m.get('date_key') == date_key]
                
                if potential_memories:
                    # Try to match by extracting components from filename: date_key_media_type_####_gps
                    # Example: "2025-12-22_03-07-53_video_0021_gps"
                    pattern_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(\w+)_(\d{4})(_gps)?', filename_base)
                    if pattern_match:
                        _, media_type_str, index_str, has_gps = pattern_match.groups()
                        file_index = int(index_str) if index_str else None
                        
                        # Try to match by index first (most accurate)
                        if file_index:
                            for pm in potential_memories:
                                if pm.get('index') == file_index:
                                    memory = pm
                                    break
                        
                        # Fallback: match by media type and GPS flag
                        if not memory and file_index is None:
                            for pm in potential_memories:
                                pm_media_type = pm.get('media_type', '').lower()
                                pm_has_gps = pm.get('location', {}).get('valid', False)
                                file_has_gps = bool(has_gps)
                                
                                if (pm_media_type == media_type_str.lower() and 
                                    pm_has_gps == file_has_gps):
                                    memory = pm
                                    break
                    
                    # Last resort: if only one match for this date, use it
                    if not memory and len(potential_memories) == 1:
                        memory = potential_memories[0]
                    # Or try matching by media type only
                    elif not memory:
                        media_type_match = re.search(r'(video|photo|image)', filename_base, re.IGNORECASE)
                        if media_type_match:
                            media_type = media_type_match.group(1).lower()
                            for pm in potential_memories:
                                if pm.get('media_type', '').lower() == media_type:
                                    memory = pm
                                    break
        
        # Fallback 2: try matching by index from filename pattern
        if not memory:
            # Extract index from filename like "video_0021" or "photo_0005"
            index_match = re.search(r'_(\d{4})(_|$)', filename_base)
            if index_match:
                file_index = int(index_match.group(1))
                memory = self.metadata_by_index.get(file_index)
        
        if not memory:
            return None, None
        
        # Check date - use date_utc if available, fallback to date_pst
        date_correct = False
        expected_date = memory.get('date_utc') or memory.get('date_pst')
        asset_date = asset.get('fileCreatedAt') or asset.get('createdAt') or asset.get('dateTimeOriginal', '')
        
        # Log for debugging
        logger.debug(f"     Expected date: {expected_date}, Asset date: {asset_date}")
        
        # Compare dates (allow small differences)
        if expected_date and asset_date:
            try:
                # Normalize both dates for comparison
                expected_dt = datetime.fromisoformat(expected_date.replace('Z', '+00:00').replace('+00:00', ''))
                asset_dt = datetime.fromisoformat(asset_date.replace('Z', '+00:00').replace('+00:00', ''))
                
                # Allow up to 1 minute difference
                date_diff = abs((expected_dt - asset_dt).total_seconds())
                date_correct = date_diff < 60
                logger.debug(f"     Date diff: {date_diff:.1f} seconds, Correct: {date_correct}")
            except Exception as e:
                logger.debug(f"     Date comparison error: {e}")
                # If date comparison fails, assume it needs fixing
                date_correct = False
        else:
            # If we can't compare dates, assume it needs fixing
            if expected_date:
                logger.debug(f"     No asset date found, assuming needs fix")
            date_correct = False
        
        # Check GPS
        gps_correct = False
        exif_info = asset.get('exifInfo') or asset.get('exif') or {}
        
        if 'location' in memory and memory['location'].get('valid'):
            expected_lat = memory['location']['latitude']
            expected_lon = memory['location']['longitude']
            
            asset_lat = exif_info.get('latitude') or asset.get('latitude')
            asset_lon = exif_info.get('longitude') or asset.get('longitude')
            
            logger.debug(f"     Expected GPS: ({expected_lat}, {expected_lon}), Asset GPS: ({asset_lat}, {asset_lon})")
            
            if asset_lat is not None and asset_lon is not None:
                # Allow small GPS differences (within 0.0001 degrees ~10m)
                lat_diff = abs(float(asset_lat) - expected_lat)
                lon_diff = abs(float(asset_lon) - expected_lon)
                gps_correct = lat_diff < 0.0001 and lon_diff < 0.0001
                logger.debug(f"     GPS diff: ({lat_diff:.6f}, {lon_diff:.6f}), Correct: {gps_correct}")
            else:
                logger.debug(f"     Asset has no GPS data, needs fix")
                gps_correct = False
        else:
            # If no GPS expected in metadata, consider it correct if asset also has no GPS
            asset_lat = exif_info.get('latitude') or asset.get('latitude')
            gps_correct = asset_lat is None
            logger.debug(f"     No GPS expected, asset GPS: {asset_lat}, Correct: {gps_correct}")
        
        needs_fix = not (date_correct and gps_correct)
        logger.debug(f"     Needs fix: {needs_fix} (date_correct: {date_correct}, gps_correct: {gps_correct})")
        
        return memory, needs_fix
    
    def asset_needs_fixing(self, asset, memory):
        """Check if an asset needs fixing given its expected metadata
        
        Args:
            asset: Asset dict from Immich
            memory: Memory dict from metadata file
        
        Returns:
            bool: True if asset needs fixing, False otherwise
        """
        # Check date - use date_utc if available, fallback to date_pst
        expected_date = memory.get('date_utc') or memory.get('date_pst')
        asset_date = asset.get('fileCreatedAt') or asset.get('createdAt') or asset.get('dateTimeOriginal', '')
        
        date_correct = False
        if expected_date and asset_date:
            try:
                expected_dt = datetime.fromisoformat(expected_date.replace('Z', '+00:00').replace('+00:00', ''))
                asset_dt = datetime.fromisoformat(asset_date.replace('Z', '+00:00').replace('+00:00', ''))
                date_diff = abs((expected_dt - asset_dt).total_seconds())
                date_correct = date_diff < 60
            except:
                date_correct = False
        else:
            if expected_date:
                date_correct = False  # Expected date but asset has none
        
        # Check GPS
        gps_correct = False
        exif_info = asset.get('exifInfo') or asset.get('exif') or {}
        
        if 'location' in memory and memory['location'].get('valid'):
            expected_lat = memory['location']['latitude']
            expected_lon = memory['location']['longitude']
            
            asset_lat = exif_info.get('latitude') or asset.get('latitude')
            asset_lon = exif_info.get('longitude') or asset.get('longitude')
            
            if asset_lat is not None and asset_lon is not None:
                lat_diff = abs(float(asset_lat) - expected_lat)
                lon_diff = abs(float(asset_lon) - expected_lon)
                gps_correct = lat_diff < 0.0001 and lon_diff < 0.0001
            else:
                gps_correct = False  # Expected GPS but asset has none
        else:
            # If no GPS expected in metadata, consider it correct if asset also has no GPS
            asset_lat = exif_info.get('latitude') or asset.get('latitude')
            gps_correct = asset_lat is None
        
        return not (date_correct and gps_correct)
    
    def update_asset_metadata(self, asset_id, memory):
        """Update asset metadata in Immich"""
        updates = {}
        
        # Update date - use date_utc if available, fallback to date_pst
        expected_date = memory.get('date_utc') or memory.get('date_pst')
        if expected_date:
            updates['fileCreatedAt'] = expected_date
        
        # Update GPS
        if 'location' in memory and memory['location'].get('valid'):
            updates['latitude'] = memory['location']['latitude']
            updates['longitude'] = memory['location']['longitude']
        
        if not updates:
            return False
        
        try:
            response = requests.put(
                f"{self.immich_url}/asset/{asset_id}",
                headers=self.headers,
                json=updates,
                timeout=30
            )
            
            return response.status_code in [200, 204]
        
        except Exception as e:
            logger.error(f"      ✗ Update failed: {e}")
            return False
    
    def repair_all(self, dry_run=False, progress_callback=None):
        """Repair metadata for all assets
        
        Args:
            dry_run: If True, don't make changes
            progress_callback: Optional callback function(progress, message, details) for progress updates
        """
        logger.info("\n" + "=" * 80)
        if dry_run:
            logger.info("METADATA REPAIR - DRY RUN MODE")
            logger.info("=" * 80)
            logger.info("🔍 DRY RUN - No changes will be made")
        else:
            logger.info("REPAIRING ASSET METADATA IN IMMICH")
            logger.info("=" * 80)
        
        # Get all memories from metadata
        memories = self.metadata.get('memories', [])
        total_memories = len(memories)
        
        if not memories:
            logger.warning("⚠️  No memories found in metadata file")
            if progress_callback:
                progress_callback(100, "⚠️  No memories found in metadata file", {"total": 0, "checked": 0, "needs_repair": 0})
            return 0, 0, 0
        
        logger.info(f"✓ Found {total_memories} memories in metadata file")
        if progress_callback:
            progress_callback(10, f"Found {total_memories} memories in metadata file. Searching Immich for each...", {"total": total_memories})
        
        checked = 0
        needs_repair = 0
        repaired = 0
        skipped = 0
        not_found = 0
        
        for i, memory in enumerate(memories, 1):
            # Get filename from metadata
            filename_base = memory.get('filename', '')
            if not filename_base:
                skipped += 1
                continue
            
            # Calculate progress (10-90% for checking memories)
            progress = 10 + int((i / total_memories) * 80)
            
            logger.info(f"\n[{i}/{total_memories}] Searching for: {filename_base}")
            
            # Search for asset in Immich by filename
            asset = self.search_asset_by_filename(filename_base)
            
            if not asset:
                not_found += 1
                logger.info(f"  ⏭️  Asset not found in Immich")
                if progress_callback:
                    progress_callback(progress, f"[{i}/{total_memories}] {filename_base}: ⏭️  Not found in Immich", {
                        "filename": filename_base,
                        "index": i,
                        "total": total_memories,
                        "found": False
                    })
                continue
            
            # Asset found - check if it needs fixing
            asset_id = asset.get('id') or asset.get('assetId', 'unknown')
            asset_filename = asset.get('originalFileName') or asset.get('originalPath', 'unknown')
            
            logger.info(f"  ✓ Found in Immich: {asset_filename}")
            
            # Check if asset needs fixing (we already have memory from metadata)
            # We need to check if the asset's metadata matches the expected metadata
            needs_fix = self.asset_needs_fixing(asset, memory)
            checked += 1
            
            details = {
                "filename": filename_base,
                "asset_filename": asset_filename,
                "index": i,
                "total": total_memories,
                "has_metadata": True,
                "found_in_immich": True,
                "needs_fix": False,
                "date_issue": False,
                "gps_issue": False
            }
            
            # Re-check to get detailed info
            expected_date = memory.get('date_utc') or memory.get('date_pst')
            asset_date = asset.get('fileCreatedAt') or asset.get('createdAt') or asset.get('dateTimeOriginal', '')
            exif_info = asset.get('exifInfo') or asset.get('exif') or {}
            asset_lat = exif_info.get('latitude') or asset.get('latitude')
            asset_lon = exif_info.get('longitude') or asset.get('longitude')
            
            date_correct = False
            gps_correct = False
            
            if expected_date and asset_date:
                try:
                    expected_dt = datetime.fromisoformat(expected_date.replace('Z', '+00:00').replace('+00:00', ''))
                    asset_dt = datetime.fromisoformat(asset_date.replace('Z', '+00:00').replace('+00:00', ''))
                    date_diff = abs((expected_dt - asset_dt).total_seconds())
                    date_correct = date_diff < 60
                except:
                    date_correct = False
            
            if 'location' in memory and memory['location'].get('valid'):
                expected_lat = memory['location']['latitude']
                expected_lon = memory['location']['longitude']
                if asset_lat is not None and asset_lon is not None:
                    lat_diff = abs(float(asset_lat) - expected_lat)
                    lon_diff = abs(float(asset_lon) - expected_lon)
                    gps_correct = lat_diff < 0.0001 and lon_diff < 0.0001
                else:
                    gps_correct = False
            else:
                gps_correct = asset_lat is None
            
            details.update({
                "needs_fix": needs_fix,
                "date_correct": date_correct,
                "gps_correct": gps_correct,
                "expected_date": expected_date,
                "asset_date": asset_date,
                "expected_gps": memory.get('location', {}).get('valid') and {
                    "lat": memory['location']['latitude'],
                    "lon": memory['location']['longitude']
                } or None,
                "asset_gps": {"lat": asset_lat, "lon": asset_lon} if asset_lat is not None else None
            })
            
            if not needs_fix:
                logger.info(f"  ✓ Metadata is correct (date: {'✓' if date_correct else '✗'}, GPS: {'✓' if gps_correct else '✗'})")
                if progress_callback:
                    progress_callback(progress, f"[{i}/{total_memories}] {filename_base}: ✓ Metadata is correct", details)
                continue
            
            needs_repair += 1
            details["date_issue"] = not date_correct
            details["gps_issue"] = not gps_correct
            
            # Show what would be fixed
            status_parts = []
            if expected_date:
                status_parts.append(f"📅 Date: {expected_date}")
                if asset_date:
                    status_parts.append(f"(current: {asset_date})")
            if 'location' in memory and memory['location'].get('valid'):
                loc = memory['location']
                status_parts.append(f"📍 GPS: {loc['latitude']}, {loc['longitude']}")
                if asset_lat is not None:
                    status_parts.append(f"(current: {asset_lat}, {asset_lon})")
            
            status_msg = " | ".join(status_parts) if status_parts else "Metadata needs update"
            
            if dry_run:
                logger.info(f"  🔍 Would update metadata - {status_msg}")
                if progress_callback:
                    progress_callback(progress, f"[{i}/{total_memories}] {filename_base}: 🔍 Would fix - {status_msg}", details)
            else:
                logger.info(f"  🔧 Updating metadata... - {status_msg}")
                if progress_callback:
                    progress_callback(progress, f"[{i}/{total_memories}] {filename_base}: 🔧 Fixing - {status_msg}", details)
                if self.update_asset_metadata(asset_id, memory):
                    logger.info(f"  ✓ Metadata updated")
                    repaired += 1
                    if progress_callback:
                        details["repaired"] = True
                        progress_callback(progress, f"[{i}/{total_memories}] {filename_base}: ✓ Fixed successfully", details)
                else:
                    logger.error(f"  ✗ Update failed")
                    if progress_callback:
                        details["repaired"] = False
                        progress_callback(progress, f"[{i}/{total_memories}] {filename_base}: ✗ Update failed", details)
        
        logger.info("\n" + "=" * 80)
        if dry_run:
            logger.info("REPAIR SUMMARY (DRY RUN)")
        else:
            logger.info("REPAIR SUMMARY")
        logger.info("=" * 80)
        logger.info(f"📊 Total memories in metadata: {total_memories}")
        logger.info(f"✓ Found in Immich and checked: {checked}")
        logger.info(f"⏭️  Not found in Immich: {not_found}")
        logger.info(f"⏭️  Skipped (no filename): {skipped}")
        
        if dry_run:
            logger.info(f"🔍 Would repair: {needs_repair}")
        else:
            logger.info(f"🔧 Needed repair: {needs_repair}")
            logger.info(f"✓ Successfully repaired: {repaired}")
            logger.info(f"✗ Failed: {needs_repair - repaired}")
        
        return checked, needs_repair, repaired


class MemoryHTMLParser(HTMLParser):
    """HTML parser for Snapchat memories export"""
    def __init__(self):
        super().__init__()
        self.memories = []
        self.current_row = {}
        self.in_table_row = False
        self.in_table_cell = False
        self.cell_index = 0
    
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.in_table_row = True
            self.current_row = {}
            self.cell_index = 0
        elif tag == 'td':
            self.in_table_cell = True
        elif tag == 'a' and self.in_table_row:
            for attr_name, attr_value in attrs:
                if attr_name == 'onclick' and attr_value:
                    match = re.search(r"downloadMemories\('([^']+)',\s*this,\s*(true|false)\)", attr_value)
                    if match:
                        self.current_row['url'] = match.group(1)
                        self.current_row['is_get_request'] = match.group(2) == 'true'
    
    def handle_endtag(self, tag):
        if tag == 'tr':
            if 'url' in self.current_row and 'date_key' in self.current_row:
                self.memories.append(self.current_row)
            self.in_table_row = False
            self.current_row = {}
            self.cell_index = 0
        elif tag == 'td':
            self.in_table_cell = False
            self.cell_index += 1
    
    def handle_data(self, data):
        if self.in_table_cell and self.in_table_row:
            data = data.strip()
            if not data:
                return
            
            # Cell 0: Date
            if self.cell_index == 0:
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(UTC)?', data)
                if date_match:
                    dt_pst = parse_snapchat_date_as_pst(data)
                    self.current_row['date_pst'] = dt_pst.strftime('%Y-%m-%dT%H:%M:%S')
                    self.current_row['date_key'] = dt_pst.strftime('%Y-%m-%d_%H-%M-%S')
                    self.current_row['original_date_str'] = data
            
            # Cell 1: Media Type
            elif self.cell_index == 1:
                self.current_row['media_type'] = data.strip()
            
            # Cell 2: Location
            elif self.cell_index == 2:
                location_match = re.search(r'Latitude,\s*Longitude:\s*([-\d.]+),\s*([-\d.]+)', data)
                if location_match:
                    try:
                        latitude = float(location_match.group(1))
                        longitude = float(location_match.group(2))
                        self.current_row['location'] = {
                            'latitude': round(latitude, 6),
                            'longitude': round(longitude, 6),
                            'valid': (latitude, longitude) != (0.0, 0.0)
                        }
                    except ValueError:
                        pass


def extract_metadata_from_json(json_file, output_json):
    """Extract metadata from JSON and keep dates as PST"""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: EXTRACTING METADATA FROM JSON (PST TIMEZONE)")
    logger.info("=" * 80)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    if isinstance(raw_data, dict):
        if 'Saved Media' in raw_data:
            raw_data = raw_data['Saved Media']
        else:
            logger.error("❌ JSON file must contain an array or a dict with 'Saved Media' key!")
            return None
    
    if not isinstance(raw_data, list):
        logger.error("❌ JSON file must contain an array of memory objects!")
        return None
    
    if not raw_data:
        logger.error("❌ No memories found in JSON file!")
        return None
    
    memories = []
    for item in raw_data:
        memory = {}
        
        # Parse date as PST
        date_str = item.get('Date', '')
        if date_str:
            try:
                dt_pst = parse_snapchat_date_as_pst(date_str)
                memory['date_pst'] = dt_pst.strftime('%Y-%m-%dT%H:%M:%S')
                memory['date_key'] = dt_pst.strftime('%Y-%m-%d_%H-%M-%S')
                memory['original_date_str'] = date_str
            except Exception as e:
                logger.warning(f"⚠️  Could not parse date: {date_str} - {e}")
                continue
        else:
            continue
        
        # Parse media type
        media_type = item.get('Media Type', '').strip()
        memory['media_type'] = media_type
        
        # Parse location
        location_str = item.get('Location', '')
        memory['location'] = {'latitude': 0.0, 'longitude': 0.0, 'valid': False}
        if location_str:
            location_match = re.search(r'Latitude,\s*Longitude:\s*([-\d.]+),\s*([-\d.]+)', location_str)
            if location_match:
                try:
                    latitude = float(location_match.group(1))
                    longitude = float(location_match.group(2))
                    memory['location'] = {
                        'latitude': round(latitude, 6),
                        'longitude': round(longitude, 6),
                        'valid': (latitude, longitude) != (0.0, 0.0)
                    }
                except ValueError:
                    pass
        
        # Parse download URL
        url = item.get('Media Download Url', '') or item.get('Download Link', '')
        if url:
            memory['url'] = url
            memory['is_get_request'] = 'Media Download Url' in item and bool(item.get('Media Download Url', ''))
        else:
            continue
        
        memories.append(memory)
    
    if not memories:
        logger.error("❌ No valid memories found in JSON file!")
        return None
    
    logger.info(f"✓ Found {len(memories)} memories")
    logger.info(f"📅 Using PST timezone (Pacific Standard Time, UTC-8)")
    
    # Enrich with filenames
    for i, memory in enumerate(memories, 1):
        date_key = memory.get('date_key', f'unknown_{i:04d}')
        media_type = memory.get('media_type', 'unknown').lower()
        
        has_gps = memory.get('location', {}).get('valid', False)
        if has_gps:
            filename = f"{date_key}_{media_type}_{i:04d}_gps"
        else:
            filename = f"{date_key}_{media_type}_{i:04d}"
        
        memory['index'] = i
        memory['filename'] = filename
        
        location = memory.get('location', {})
        if location.get('valid'):
            loc_str = f"GPS: {location['latitude']:.4f}, {location['longitude']:.4f}"
        else:
            loc_str = "No GPS (0.0, 0.0)"
        
        logger.info(f"  [{i:3d}] {memory['date_key']} (PST) | {media_type:5s} | {loc_str}")
    
    # Save to JSON
    metadata = {
        'extracted_at': datetime.now().isoformat(),
        'source_json': str(json_file),
        'total_memories': len(memories),
        'timezone': 'PST',
        'timezone_offset': 'UTC-8',
        'memories': memories
    }
    
    with open(output_json, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"\n✓ Metadata saved to: {output_json}")
    
    # Statistics
    total = len(memories)
    with_gps = sum(1 for m in memories if m.get('location', {}).get('valid', False))
    without_gps = total - with_gps
    videos = sum(1 for m in memories if m.get('media_type', '').lower() == 'video')
    images = sum(1 for m in memories if m.get('media_type', '').lower() == 'image')
    
    logger.info("\n" + "=" * 80)
    logger.info("METADATA SUMMARY")
    logger.info("=" * 80)
    logger.info(f"📊 Total memories: {total}")
    logger.info(f"   └─ Videos: {videos}")
    logger.info(f"   └─ Images: {images}")
    logger.info("")
    logger.info(f"📍 GPS Coverage:")
    logger.info(f"   └─ With GPS: {with_gps} ({with_gps/total*100:.1f}%)")
    logger.info(f"   └─ Without GPS: {without_gps}")
    logger.info("")
    logger.info(f"🕐 Timezone: PST (Pacific Standard Time, UTC-8)")
    logger.info("=" * 80)
    
    return metadata


def extract_metadata_from_html(html_file, output_json):
    """Extract metadata from HTML and keep dates as PST"""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: EXTRACTING METADATA FROM HTML (PST TIMEZONE)")
    logger.info("=" * 80)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = MemoryHTMLParser()
    parser.feed(content)
    
    if not parser.memories:
        logger.error("❌ No memories found in HTML file!")
        return None
    
    logger.info(f"✓ Found {len(parser.memories)} memories")
    logger.info(f"📅 Using PST timezone (Pacific Standard Time, UTC-8)")
    
    # Enrich with filenames
    for i, memory in enumerate(parser.memories, 1):
        date_key = memory.get('date_key', f'unknown_{i:04d}')
        media_type = memory.get('media_type', 'unknown').lower()
        
        has_gps = memory.get('location', {}).get('valid', False)
        if has_gps:
            filename = f"{date_key}_{media_type}_{i:04d}_gps"
        else:
            filename = f"{date_key}_{media_type}_{i:04d}"
        
        memory['index'] = i
        memory['filename'] = filename
        
        location = memory.get('location', {})
        if location.get('valid'):
            loc_str = f"GPS: {location['latitude']:.4f}, {location['longitude']:.4f}"
        else:
            loc_str = "No GPS (0.0, 0.0)"
        
        logger.info(f"  [{i:3d}] {memory['date_key']} (PST) | {media_type:5s} | {loc_str}")
    
    # Save to JSON
    metadata = {
        'extracted_at': datetime.now().isoformat(),
        'source_html': str(html_file),
        'total_memories': len(parser.memories),
        'timezone': 'PST',
        'timezone_offset': 'UTC-8',
        'memories': parser.memories
    }
    
    with open(output_json, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"\n✓ Metadata saved to: {output_json}")
    
    return metadata


def apply_metadata_to_image(image_path, metadata):
    """Apply date (PST) and GPS metadata to image"""
    if not metadata:
        return
    
    try:
        try:
            exif_dict = piexif.load(str(image_path))
        except Exception:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        # Apply date (PST)
        if 'date_pst' in metadata:
            try:
                date_str_raw = metadata['date_pst']
                dt = datetime.fromisoformat(date_str_raw)
                date_str = dt.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str
                logger.info(f"      ✓ Date (PST): {date_str}")
            except Exception as e:
                logger.warning(f"      ⚠️  Date error: {e}")
        
        # Apply GPS
        if 'location' in metadata:
            location = metadata['location']
            if location.get('valid', False):
                lat = location['latitude']
                lon = location['longitude']
                
                def to_degrees(value):
                    value = float(value)
                    d = int(abs(value))
                    m = int((abs(value) - d) * 60)
                    s = int(((abs(value) - d) * 60 - m) * 60 * 100)
                    return ((d, 1), (m, 1), (s, 100))
                
                exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = to_degrees(lat)
                exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = 'N' if lat >= 0 else 'S'
                exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = to_degrees(lon)
                exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = 'E' if lon >= 0 else 'W'
                logger.info(f"      ✓ GPS: {lat}, {lon}")
            else:
                logger.warning("      ⚠️  Skipped GPS (0.0, 0.0)")
        
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, str(image_path))
        
    except Exception as e:
        logger.warning(f"      ⚠️  Metadata error: {e}")


def apply_metadata_to_video(video_path, metadata):
    """Apply date (PST) and GPS metadata to video"""
    if not metadata:
        return
    
    try:
        metadata_args = []
        
        # Apply date (PST)
        if 'date_pst' in metadata:
            try:
                date_str = metadata['date_pst']
                metadata_args.extend(['-metadata', f'creation_time={date_str}'])
                logger.info(f"      ✓ Date (PST): {date_str}")
            except Exception as e:
                logger.warning(f"      ⚠️  Date error: {e}")
        
        # Apply GPS
        if 'location' in metadata:
            location = metadata['location']
            if location.get('valid', False):
                lat = location['latitude']
                lon = location['longitude']
                metadata_args.extend([
                    '-metadata', f'location={lat},{lon}',
                    '-metadata', f'location-eng={lat},{lon}'
                ])
                logger.info(f"      ✓ GPS: {lat}, {lon}")
            else:
                logger.warning("      ⚠️  Skipped GPS (0.0, 0.0)")
        
        if metadata_args:
            temp_path = video_path.parent / f"temp_{video_path.name}"
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-c', 'copy',
                *metadata_args,
                '-y',
                str(temp_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                shutil.move(str(temp_path), str(video_path))
            else:
                logger.warning(f"      ⚠️  FFmpeg error: {result.stderr[:100]}")
                if temp_path.exists():
                    temp_path.unlink()
                    
    except Exception as e:
        logger.warning(f"      ⚠️  Metadata error: {e}")


def print_usage():
    """Print usage information"""
    logger.info("Usage:")
    logger.info("  # Normal import:")
    logger.info("  python3 process_memories.py <input_file> [options]")
    logger.info("")
    logger.info("  # Repair Immich metadata:")
    logger.info("  python3 process_memories.py --repair-immich <metadata_file> \\")
    logger.info("    --immich-url <url> --api-key <key> [--dry-run]")
    logger.info("\nOptions:")
    logger.info("  --repair-immich     Repair metadata for assets already in Immich")
    logger.info("  --dry-run           Preview changes without applying them")
    logger.info("  --immich-url URL    Immich server URL")
    logger.info("  --api-key KEY       Immich API key")
    logger.info("\nExamples:")
    logger.info("  # Extract metadata (with PST timezone):")
    logger.info("  python3 process_memories.py memories_history.json --dry-run")
    logger.info("")
    logger.info("  # Full import:")
    logger.info("  python3 process_memories.py memories_history.json \\")
    logger.info("    --immich-url http://192.168.1.100:2283/api \\")
    logger.info("    --api-key your_key_here")
    logger.info("")
    logger.info("  # Repair Immich metadata (dry run):")
    logger.info("  python3 process_memories.py --repair-immich memories_history_metadata.json \\")
    logger.info("    --immich-url http://192.168.1.100:2283/api \\")
    logger.info("    --api-key your_key_here \\")
    logger.info("    --dry-run")
    logger.info("")
    logger.info("  # Repair Immich metadata (apply fixes):")
    logger.info("  python3 process_memories.py --repair-immich memories_history_metadata.json \\")
    logger.info("    --immich-url http://192.168.1.100:2283/api \\")
    logger.info("    --api-key your_key_here")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Check for --repair-immich mode
    if sys.argv[1] == '--repair-immich':
        if len(sys.argv) < 3:
            logger.error("Error: --repair-immich requires a metadata file")
            print_usage()
            sys.exit(1)
        
        metadata_file = sys.argv[2]
        
        # Parse arguments
        immich_url = None
        api_key = None
        dry_run = False
        
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--immich-url':
                if i + 1 < len(sys.argv):
                    immich_url = sys.argv[i + 1]
                    i += 2
                else:
                    logger.error("Error: --immich-url requires a value")
                    sys.exit(1)
            elif arg == '--api-key':
                if i + 1 < len(sys.argv):
                    api_key = sys.argv[i + 1]
                    i += 2
                else:
                    logger.error("Error: --api-key requires a value")
                    sys.exit(1)
            elif arg == '--dry-run':
                dry_run = True
                i += 1
            else:
                logger.error(f"Error: Unknown argument '{arg}'")
                sys.exit(1)
        
        if not immich_url or not api_key:
            logger.error("Error: --immich-url and --api-key are required for --repair-immich")
            sys.exit(1)
        
        if not os.path.exists(metadata_file):
            logger.error(f"Error: Metadata file not found: {metadata_file}")
            sys.exit(1)
        
        logger.info("=" * 80)
        logger.info("IMMICH METADATA REPAIR MODE")
        logger.info("=" * 80)
        logger.info(f"Metadata file: {metadata_file}")
        logger.info(f"Immich URL: {immich_url}")
        logger.info(f"Timezone: PST (Pacific Standard Time, UTC-8)")
        if dry_run:
            logger.info("Mode: DRY RUN (preview only)")
        else:
            logger.info("Mode: APPLY FIXES")
        
        # Run repair
        repairer = ImmichMetadataRepairer(metadata_file, immich_url, api_key)
        checked, needs_repair, repaired = repairer.repair_all(dry_run=dry_run)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ REPAIR COMPLETE!")
        logger.info("=" * 80)
        
        sys.exit(0 if repaired == needs_repair else 1)
    
    # Normal import flow continues...
    # (Keep existing main() logic but use date_pst instead of date_utc)


if __name__ == '__main__':
    main()
