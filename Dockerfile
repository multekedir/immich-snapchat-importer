# Multi-stage build for smaller image
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim

# Install System Dependencies
# ffmpeg: for video processing
# libgl1/libglib: required by opencv-python
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Setup Working Directory
WORKDIR /app

# Copy application code
COPY process_memories.py .
COPY README.md .

# Health check to verify Python environment
HEALTHCHECK CMD python -c "import sys; sys.exit(0)"

# Define the Entrypoint
ENTRYPOINT ["python", "process_memories.py"]
