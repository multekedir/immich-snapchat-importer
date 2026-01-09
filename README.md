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

## 🚀 Quick Start (Docker Compose)

The easiest way to run this is as a "sidecar" to your existing Immich installation.

### 1. Prepare your Data

1. Request your data from Snapchat (Settings -> My Data).
2. Download the ZIP file and extract it.
3. Locate `json/memories_history.json` inside the extracted folder.
4. Create a folder named `snapchat-data` on your server and move the `.json` file there.

### 2. Update Docker Compose

Add this service to your existing `docker-compose.yml` file:

```yaml
services:
  # ... your existing immich services ...

  snapchat-importer:
    image: yourusername/immich-snapchat-importer:latest
    container_name: immich_snapchat_importer
    restart: on-failure
    volumes:
      # Link to the folder where you put memories_history.json
      - ./snapchat-data:/data
    environment:
      - IMMICH_URL=http://immich-server:2283/api
      - IMMICH_API_KEY=your_immich_api_key_here
      - INPUT_FILE=/data/memories_history.json
```

### 3. Run It

```bash
docker compose up -d snapchat-importer
docker compose logs -f snapchat-importer
```

The container will start, process your memories, upload them to Immich, and then stop automatically when finished.

**Note**: The Docker image is not yet available. You'll need to build it yourself or wait for it to be published. For now, use the manual installation method below.

## 🛠️ Manual / Standalone Usage

If you prefer to run it on your laptop (Mac/Windows/Linux) without Docker:

### Prerequisites

- Python 3.10+
- ffmpeg (Installed and in your system PATH)

### Installation

```bash
git clone https://github.com/multekedir/immich-snapchat-importer.git
cd immich-snapchat-importer
pip install -r requirements.txt
```

**Note**: Make sure `ffmpeg` is installed on your system:
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Usage

The tool runs in 4 phases. You can run them all at once, or separately:

#### Phase 1: Extract Metadata (Dry Run)

```bash
# Extract metadata from JSON file (no download/processing)
python process_memories.py memories_history.json --dry-run

# Or from HTML file
python process_memories.py memories_history.html --dry-run
```

This creates a `*_metadata.json` file with all extracted metadata. Useful for previewing what will be imported.

#### Phase 2-4: Full Import (Download + Process + Upload)

```bash
# Full import with automatic upload to Immich
python process_memories.py memories_history.json \
  --immich-url "http://192.168.1.100:2283/api" \
  --api-key "your_key_here"

# Using environment variables (more secure)
export IMMICH_URL="http://localhost:2283/api"
export IMMICH_API_KEY="your_key_here"
python process_memories.py memories_history.json

# With custom download delay (slower, but safer)
python process_memories.py memories_history.json \
  --immich-url "http://localhost:2283/api" \
  --api-key "your_key_here" \
  --delay 3
```

#### Process-Only Mode (Skip Download)

If you've already downloaded files but want to reprocess or upload:

```bash
# Process existing downloads and upload to Immich
python process_memories.py --process-only memories_history.json \
  --immich-url "http://localhost:2283/api" \
  --api-key "your_key_here"
```

#### How It Works

1. **Phase 1: Extract** - Parses JSON/HTML and extracts metadata (dates, GPS, URLs)
2. **Phase 2: Download** - Downloads all media files from Snapchat servers
3. **Phase 3: Process** - Extracts .bin files, applies overlays, embeds EXIF/GPS metadata
4. **Phase 4: Upload** - Uploads processed files to Immich with correct dates

## ⚙️ Configuration Options

| Environment Variable | CLI Argument | Description | Default |
|---------------------|--------------|-------------|---------|
| `IMMICH_URL` | `--immich-url` | Your Immich Server API URL (e.g., `http://localhost:2283/api`) | None |
| `IMMICH_API_KEY` | `--api-key` | Your API Key (Create in Immich: Account Settings → API Keys) | None |
| `DELAY` | `--delay` | Seconds to wait between downloads (avoids rate limiting) | 2.0 |

**Note**: If Immich URL and API key are not provided, the tool will skip the upload phase and only process files locally.

### Getting Your Immich API Key

1. Open Immich in your browser
2. Go to **Account Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the key (you won't see it again!)
5. Use it with `--api-key` or set `IMMICH_API_KEY` environment variable

## 🐛 Troubleshooting

**"Videos are missing audio after processing"**
- Ensure ffmpeg is installed correctly: `ffmpeg -version`
- The tool uses a complex ffmpeg filter to merge audio from the original file while burning the visual overlay.
- If audio is still missing, check the original .bin file - some Snapchat videos may not have audio tracks.

**"Uploads failed with Error 409"**
- This means the file already exists in Immich. The tool automatically skips these to prevent duplicates.
- This is normal if you re-run the script - it won't re-upload existing files.

**"Connection failed" or "Upload timeout"**
- Check that your Immich URL is correct (should end with `/api`)
- Verify your API key is valid and not expired
- For large video files, uploads may take longer - the timeout is set to 120 seconds
- Check your network connection to the Immich server

**"GPS shows 0.0, 0.0"**
- If Snapchat didn't record a valid GPS location for a memory, the tool preserves the timestamp but leaves the location blank (rather than placing you in the middle of the Atlantic Ocean).
- This is expected behavior - not all Snapchat memories have GPS data.

**"No metadata found" during processing**
- The tool uses multiple fallback strategies to match files to metadata
- If you see this warning, the file will still be processed but without date/GPS metadata
- Check that your `*_metadata.json` file exists and contains the expected memory entries

**"Download failed" errors**
- Snapchat may rate-limit downloads. Increase the `--delay` value (e.g., `--delay 5`)
- Some URLs may expire. Re-request your data from Snapchat if many downloads fail
- Check your internet connection

## 📜 License

MIT License - Free to use and modify.

**Disclaimer**: This project is not affiliated with Snapchat or Immich. Use at your own risk. Always backup your `memories_history.json` before starting.
