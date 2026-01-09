# Immich Snapchat Importer

A community tool to import your Snapchat Memories into Immich while preserving dates, GPS locations, and captions.

## 🌟 Why use this?

Snapchat exports are messy. If you just drag-and-drop them into Immich:
- ❌ All photos will show as "Today" (metadata is lost).
- ❌ Videos will lose their date and location.
- ❌ Captions/Overlays might be missing or separated.

This tool fixes that. It reads the JSON metadata from Snapchat, embeds it directly into the image/video files (EXIF/XMP), and automatically uploads them to your Immich server.

## ✨ Features

- **Complete Metadata Fix**: Injects correct Date, Time, and GPS coordinates into every file.
- **Overlay Merging**: Automatically burns Snapchat text captions and overlays onto images and videos.
- **Automatic Upload**: Seamlessly uploads processed files directly to your Immich server.
- **Duplicate Detection**: Skips files that have already been imported (both locally and in Immich).
- **Memory Efficient**: Downloads, processes, and uploads files in batches.
- **Resume Support**: If the script crashes, it picks up exactly where it left off.
- **4-Phase Architecture**: Extract → Download → Process → Upload (can run phases independently)
- **🆕 Web Interface**: User-friendly web UI with real-time progress tracking

## 🚀 Quick Start

> **New to this tool?** Check out the [Quick Start Guide](QUICKSTART.md) for a 5-minute setup!

You have two options to run this tool:

### Option 1: Web Interface (Recommended) 🌐

The easiest way with a beautiful web UI and real-time progress tracking.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/immich-snapchat-importer.git
cd immich-snapchat-importer

# 2. Copy environment file and configure
cp .env.example .env
# Edit .env with your Immich URL and API key

# 3. Start the web interface
# If your Docker Compose supports profiles (v1.28+):
docker compose --profile web up -d
# Or use separate compose file (works with older versions):
docker-compose -f docker-compose.web.yml up -d

# 4. Open your browser
# Navigate to http://localhost:8000
```

The web interface provides:
- 📁 Drag & drop file upload
- ⚙️ Easy configuration
- 📊 Real-time progress tracking
- 📈 Import statistics dashboard
- 🔄 WebSocket-based live updates

### Option 2: Command Line (Advanced) ⌨️

For automated workflows or headless servers.

```bash
# 1. Prepare your data
# Place memories_history.json in ./snapchat-data/

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Run the CLI import
# If your Docker Compose supports profiles (v1.28+):
docker compose --profile cli up
# Or use separate compose file (works with older versions):
docker-compose -f docker-compose.cli.yml up

# Monitor logs
docker compose logs -f snapchat-importer-cli
```

## 📋 Prerequisites

### For Web Interface
- Docker and Docker Compose
- Immich server running
- Port 8000 available (or change in docker-compose.yml)

### For CLI Mode
- Docker and Docker Compose
- Snapchat export file (memories_history.json or memories_history.html)

### Getting Your Snapchat Export

1. Open Snapchat → Settings → My Data
2. Click "Submit Request"
3. Wait for email (usually 24-48 hours)
4. Download ZIP file
5. Extract and locate `json/memories_history.json`

### Getting Your Immich API Key

1. Open Immich in your browser
2. Go to **Account Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the key (you won't see it again!)
5. Add to `.env` file or enter in web interface

## 🐳 Docker Deployment

### Web Interface with Immich

Add to your existing `docker-compose.yml`:

```yaml
services:
  # ... your existing immich services ...

  snapchat-importer:
    image: yourusername/immich-snapchat-importer:web
    container_name: immich_snapchat_importer
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./snapchat-data:/app/uploads
      - ./snapchat-work:/app/work
    environment:
      - IMMICH_URL=http://immich-server:2283/api
      - IMMICH_API_KEY=${IMMICH_API_KEY}
    networks:
      - default  # Use same network as Immich
```

Then access the web UI at `http://your-server:8000`

### Standalone Docker Run

```bash
docker run -d \
  --name snapchat-importer \
  -p 8000:8000 \
  -v $(pwd)/snapchat-data:/app/uploads \
  -v $(pwd)/snapchat-work:/app/work \
  -e IMMICH_URL=http://your-immich:2283/api \
  -e IMMICH_API_KEY=your_key \
  yourusername/immich-snapchat-importer:web
```

## 🛠️ Manual Installation (Without Docker)

### Prerequisites

- Python 3.10+
- ffmpeg (must be in system PATH)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/immich-snapchat-importer.git
cd immich-snapchat-importer

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from ffmpeg.org
```

### Running Web Interface

```bash
# Start the web server
python webapp.py

# Access at http://localhost:8000
```

### Running CLI

```bash
# Full import with Immich upload
python process_memories.py memories_history.json \
  --immich-url "http://192.168.1.100:2283/api" \
  --api-key "your_key_here"

# Dry run (extract metadata only)
python process_memories.py memories_history.json --dry-run

# Process-only mode (skip download)
python process_memories.py --process-only memories_history.json \
  --immich-url "http://localhost:2283/api" \
  --api-key "your_key_here"
```

## ⚙️ Configuration

Configuration can be set via three methods (in priority order):

### 1. Web Interface (Easiest)
- Configure via the web UI form
- Settings saved per-import

### 2. Environment Variables
```bash
export IMMICH_URL="http://localhost:2283/api"
export IMMICH_API_KEY="your_key_here"
export DELAY="2.0"
```

### 3. Config File (`config.yaml`)
```yaml
immich:
  url: http://immich-server:2283/api
  api_key: ${IMMICH_API_KEY}  # Supports env var substitution
download:
  delay: 2.0
  max_retries: 3
  batch_size: 50
processing:
  overlay_opacity: 1.3
  shadow_offset: 2
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `IMMICH_URL` | Immich API endpoint | None |
| `IMMICH_API_KEY` | Immich API key | None |
| `DELAY` | Seconds between downloads | 2.0 |

## 📊 Web Interface Features

### Dashboard
- Real-time progress bars
- Phase-by-phase status updates
- Live statistics display
- Import history

### Upload Page
- Drag & drop file upload
- Automatic validation
- File size preview
- Support for JSON and HTML formats

### Configuration
- Form-based settings
- API key masking
- Skip upload option
- Custom delay configuration

### Progress Tracking
- WebSocket-based live updates
- Detailed phase information
- Error notifications
- Completion statistics

## 🔧 How It Works

### 4-Phase Architecture

1. **Phase 1: Extract Metadata**
   - Parses JSON/HTML export
   - Extracts dates, GPS, URLs
   - Saves to standardized JSON

2. **Phase 2: Download Files**
   - Downloads from Snapchat servers
   - Retry logic with exponential backoff
   - Resume support via progress tracking

3. **Phase 3: Process Files**
   - Extracts .bin archives (ZIP files)
   - Applies overlay images/text
   - Embeds EXIF/GPS metadata

4. **Phase 4: Upload to Immich**
   - Uploads with correct timestamps
   - Duplicate detection
   - Batch processing

## 🐛 Troubleshooting

### Web Interface Issues

**"Port 8000 already in use"**
- Change port in docker-compose.yml: `- "8001:8000"`
- Or stop the conflicting service

**"Cannot connect to WebSocket"**
- Check browser console for errors
- Verify port 8000 is accessible
- Check firewall settings

**"Import stuck at X%"**
- Check docker logs: `docker compose logs snapchat-importer-web`
- Verify Immich is accessible from container
- Check network connectivity

### Common Issues

**"Videos are missing audio after processing"**
- Ensure ffmpeg is installed: `ffmpeg -version`
- Check logs for ffmpeg errors
- Some Snapchat videos may not have audio tracks

**"Uploads failed with Error 409"**
- File already exists in Immich (duplicate)
- This is normal - duplicates are skipped automatically

**"Connection failed" or "Upload timeout"**
- Verify Immich URL is correct (should end with `/api`)
- Check API key is valid
- For large videos, timeout is 120 seconds
- Verify network connection to Immich

**"GPS shows 0.0, 0.0"**
- Some Snapchat memories don't have GPS data
- This is expected - coordinates are skipped if invalid

**"No metadata found" during processing"**
- Check that `*_metadata.json` file exists
- Multiple fallback strategies are used
- File will still be processed without metadata

**"Download failed" errors**
- Snapchat may rate-limit - increase `--delay` (e.g., `--delay 5`)
- Some URLs may expire - re-request data from Snapchat
- Check internet connection

### Docker Issues

**"Cannot access Immich from container"**
```bash
# Verify network connectivity
docker compose exec snapchat-importer-web ping immich-server

# Check if using correct network
docker network ls
docker network inspect immich_default
```

**"Volume permissions error"**
```bash
# Fix permissions
sudo chown -R 1000:1000 ./snapchat-data ./snapchat-work
```

## 📜 API Documentation

The web interface exposes a REST API:

### Endpoints

**POST `/api/upload`**
- Upload Snapchat export file
- Returns: `{status, filename, size, path}`

**POST `/api/import/start`**
- Start import job
- Body: `{filename, config}`
- Returns: `{job_id, status}`

**GET `/api/import/status/{job_id}`**
- Get import job status
- Returns: Job details with progress

**GET `/api/import/list`**
- List all import jobs
- Returns: Array of job objects

**GET `/api/config`**
- Get current configuration
- Returns: Configuration object

**GET `/health`**
- Health check
- Returns: `{status, active_imports, connected_clients}`

**WebSocket `/ws`**
- Real-time progress updates
- Receives: `{type, job_id, progress, message, stats}`

## 🔐 Security Notes

- API keys are masked in config endpoint responses
- Use environment variables for sensitive data
- Web interface should run behind reverse proxy in production
- Consider using HTTPS for remote access

## 📈 Performance Tips

1. **Adjust Download Delay**: Lower for fast connections (1.0s), higher if rate-limited (5.0s)
2. **Batch Processing**: Process 50-100 files at a time for optimal performance
3. **Network**: Run on same network as Immich for faster uploads
4. **Storage**: Ensure sufficient disk space (2-3x export size)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

MIT License - Free to use and modify.

**Disclaimer**: This project is not affiliated with Snapchat or Immich. Use at your own risk. Always backup your `memories_history.json` before starting.

## 🙏 Acknowledgments

- Immich team for the excellent photo management system
- OpenCV, FFmpeg, and PIL/Pillow communities
- FastAPI for the excellent web framework

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/yourusername/immich-snapchat-importer/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/immich-snapchat-importer/discussions)

---

Made with ❤️ for the Immich community
