# 🚀 Quick Start Guide

## Web Interface (5 minutes)

### 1. Download and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/immich-snapchat-importer.git
cd immich-snapchat-importer

# Create config
cp .env.example .env
nano .env  # Add your Immich URL and API key
```

### 2. Start Web Interface

```bash
# Using Docker Compose (choose one method)

# Method 1: If your Docker Compose supports profiles (v1.28+)
docker compose --profile web up -d

# Method 2: Using separate compose file (works with older versions)
docker-compose -f docker-compose.web.yml up -d
# or
docker compose -f docker-compose.web.yml up -d

# Or standalone Docker
docker run -d \
  --name snapchat-importer \
  -p 8000:8000 \
  -v $(pwd)/snapchat-data:/app/uploads \
  -v $(pwd)/snapchat-work:/app/work \
  -e IMMICH_URL=http://your-immich:2283/api \
  -e IMMICH_API_KEY=your_key \
  yourusername/immich-snapchat-importer:web
```

### 3. Access Web UI

Open your browser and navigate to:
```
http://localhost:8000
```

### 4. Import Your Memories

- **Upload File**: Drag & drop your `memories_history.json` or `.html` file
- **Configure**: Enter Immich URL and API key (or pre-configured from .env)
- **Start Import**: Click "Start Import" and watch the progress
- **View Statistics**: See import stats when complete

## CLI Mode (Advanced)

### One-Command Import

```bash
# Place your file in snapchat-data/memories_history.json
mkdir -p snapchat-data
mv memories_history.json snapchat-data/

# Run import (choose one method)

# Method 1: If your Docker Compose supports profiles (v1.28+)
docker compose --profile cli up

# Method 2: Using separate compose file (works with older versions)
docker-compose -f docker-compose.cli.yml up
# or
docker compose -f docker-compose.cli.yml up
```

### Custom Configuration

```bash
# Edit docker-compose.yml or use environment variables
IMMICH_URL=http://immich:2283/api \
IMMICH_API_KEY=your_key \
DELAY=3.0 \
docker compose --profile cli up
```

## Without Docker (Python)

### Install

```bash
# Install dependencies
pip install -r requirements.txt

# Install ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from ffmpeg.org
```

### Run Web Interface

```bash
python webapp.py
# Access at http://localhost:8000
```

### Run CLI

```bash
python process_memories.py memories_history.json \
  --immich-url http://localhost:2283/api \
  --api-key your_key_here
```

## Next Steps

- **Customize Settings**: Edit `config.yaml` for advanced options
- **Check Logs**: `docker compose logs -f`
- **View Statistics**: Check import report in web UI
- **Troubleshooting**: See README.md for common issues

## Getting Your Files

### Snapchat Export

1. Snapchat → Settings → My Data
2. Submit Request
3. Wait for email (24-48h)
4. Download and extract ZIP
5. Find `json/memories_history.json`

### Immich API Key

1. Immich → Account Settings → API Keys
2. Create API Key
3. Copy key (shown once)
4. Add to `.env` or web UI

## Tips

- **First Time**: Start with a small test (use `--dry-run` in CLI)
- **Large Imports**: Increase `DELAY` to avoid rate limiting
- **Monitor Progress**: Web UI shows real-time updates
- **Resume Support**: If interrupted, restart - it will resume automatically
- **Check Space**: Ensure 2-3x export size available

## Help & Support

- **Documentation**: See README.md
- **Issues**: [GitHub Issues page](https://github.com/yourusername/immich-snapchat-importer/issues)
- **Discussions**: [GitHub Discussions page](https://github.com/yourusername/immich-snapchat-importer/discussions)

---

Happy importing! 📸
