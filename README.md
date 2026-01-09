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
- **Duplicate Detection**: Skips files that have already been imported.
- **Memory Efficient**: Downloads, processes, and uploads files in batches.
- **Resume Support**: If the script crashes, it picks up exactly where it left off.

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

The container will start, process your memories, upload them, and then stop automatically when finished.

## 🛠️ Manual / Standalone Usage

If you prefer to run it on your laptop (Mac/Windows/Linux) without Docker:

### Prerequisites

- Python 3.10+
- ffmpeg (Installed and in your system PATH)

### Installation

```bash
git clone https://github.com/yourusername/immich-snapchat-importer.git
cd immich-snapchat-importer
pip install -r requirements.txt
```

### Usage

```bash
# 1. Dry Run (Check metadata without downloading)
python process_memories.py memories_history.json --dry-run

# 2. Full Import (Download + Process + Upload)
python process_memories.py memories_history.json \
  --immich-url "http://192.168.1.100:2283/api" \
  --api-key "your_key_here"
```

## ⚙️ Configuration Options

| Environment Variable | CLI Argument | Description | Default |
|---------------------|--------------|-------------|---------|
| `IMMICH_URL` | `--immich-url` | Your Immich Server API URL | None |
| `IMMICH_API_KEY` | `--api-key` | Your API Key (Create in Account Settings) | None |
| `DELAY` | `--delay` | Seconds to wait between downloads (avoids ban) | 2.0 |
| `OVERWRITE` | `--overwrite` | Reprocess files even if they exist locally | False |

## 🐛 Troubleshooting

**"Videos are missing audio after processing"**
- Ensure ffmpeg is installed correctly. The tool uses a complex ffmpeg filter to merge audio from the original file while burning the visual overlay.

**"Uploads failed with Error 409"**
- This means the file already exists in Immich. The tool automatically skips these to prevent duplicates.

**"GPS shows 0.0, 0.0"**
- If Snapchat didn't record a valid GPS location for a memory, the tool preserves the timestamp but leaves the location blank (rather than placing you in the middle of the Atlantic Ocean).

## 📜 License

MIT License - Free to use and modify.

**Disclaimer**: This project is not affiliated with Snapchat or Immich. Use at your own risk. Always backup your `memories_history.json` before starting.
