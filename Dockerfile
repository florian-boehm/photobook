# Photobook Media Streaming Service Dockerfile
# Multi-stage build for production and development

# ============================================
# Base stage for dependencies
# ============================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# ============================================
# Development stage
# ============================================
FROM base as development

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --user -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create directories for media and data
RUN mkdir -p /media /data

# Set permissions
RUN chown -R appuser:appgroup /app /media /data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables for development
ENV PYTHONPATH=/app \
    MEDIA_ROOT_PATH=/media \
    MAPPING_FILE_PATH=/data/mapping.json

# Default command for development (with auto-reload)
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Production stage
# ============================================
FROM base as production

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies (without dev dependencies)
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create directories for media and data
RUN mkdir -p /media /data

# Set permissions
RUN chown -R appuser:appgroup /app /media /data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables for production
ENV PYTHONPATH=/app \
    MEDIA_ROOT_PATH=/media \
    MAPPING_FILE_PATH=/data/mapping.json \
    DEBUG=False

# Default command for production
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
