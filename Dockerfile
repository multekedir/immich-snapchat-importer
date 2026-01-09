# Use a slim python image to keep size down
FROM python:3.10-slim

# 1. Install System Dependencies
# ffmpeg: for video processing
# libgl1/libglib: required by opencv-python
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Working Directory
WORKDIR /app

# 3. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Your Code
COPY process_memories.py .
COPY README.md .

# 5. Define the Entrypoint
# We use a shell script entrypoint to handle arguments or defaults
ENTRYPOINT ["python", "process_memories.py"]
