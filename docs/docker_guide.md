# Docker Guide

> **Using Docker for reproducible research environments.**

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Dockerfile Explained](#dockerfile-explained)
4. [Building the Image](#building-the-image)
5. [Running Containers](#running-containers)
6. [Docker Compose](#docker-compose)
7. [Volume Mounting](#volume-mounting)
8. [GPU Support](#gpu-support)
9. [Running Tests](#running-tests)
10. [Running Jupyter](#running-jupyter)
11. [Running the Dashboard](#running-the-dashboard)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Overview

Docker containers provide a **completely reproducible environment** for running the scoring-bias analysis. Our Docker setup:

- Pins Python 3.11 with exact dependency versions
- Uses multi-stage builds for smaller images (~300 MB runtime)
- Supports CPU and GPU usage
- Provides services for testing, Jupyter, and dashboard

---

## Prerequisites

- **Docker Engine 24+** ([install guide](https://docs.docker.com/engine/install/))
- **Docker Compose v2+** (for multi-service setup)
- Optional: **NVIDIA Container Toolkit** (for GPU support)

### Verify Installation

```bash
docker --version
# Docker version 24.0.7, build afdd53b

docker compose version
# Docker Compose version v2.24.1

# Optional: Check GPU support
docker run --rm --gpus all nvidia/cuda:12.2.0-base nvidia-smi
```

---

## Dockerfile Explained

Our `Dockerfile` uses a **multi-stage build** for efficiency:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

LABEL org.opencontainers.image.source="https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge"
LABEL org.opencontainers.image.description="LLM-as-a-Judge Bias Research Environment"
LABEL org.opencontainers.image.version="1.0.0"

WORKDIR /app

# System dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image (slim)
FROM python:3.11-slim

WORKDIR /app

# Only copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project source
COPY . .

# Make scripts executable
RUN chmod +x *.sh 2>/dev/null || true

# Create working directories
RUN mkdir -p results results_rootcause cache benchmark

# Default command
CMD ["python3", "dashboard.py"]
```

### Multi-Stage Benefits

- **Stage 1 (builder)**: Installs build dependencies (gcc, git) and compiles packages
- **Stage 2 (runtime)**: Copies only the compiled packages and source code
- **Result**: Final image is ~300 MB instead of 1 GB+

---

## Building the Image

### Standard Build

```bash
# Build the image
docker build -t scoring-bias .

# Verify it built
docker images | grep scoring-bias
```

### Build with Different Tag

```bash
docker build -t scoring-bias:latest .
docker build -t scoring-bias:v1.0.0 .
```

### Build with No Cache

```bash
# Force fresh build (useful when dependencies change)
docker build --no-cache -t scoring-bias .
```

---

## Running Containers

### Basic Run

```bash
# Run the default command (dashboard)
docker run --rm scoring-bias

# Run with interactive shell
docker run --rm -it scoring-bias /bin/bash
```

### Run Analysis Commands

```bash
# Run tests
docker run --rm scoring-bias python -m pytest tests/ -v

# Run CLI
docker run --rm scoring-bias scoring-bias run-all

# Run a specific script
docker run --rm scoring-bias python results_rootcause/run_all_analyses.py
```

### Run with Volume Mounting

```bash
# Mount results directory to host
docker run --rm \
    -v "$(pwd)/results:/app/results" \
    scoring-bias scoring-bias run-all --output results/
```

### Run with Environment Variables

```bash
# Pass API keys
docker run --rm \
    --env-file .env \
    scoring-bias python inference_executor.py --judge all
```

---

## Docker Compose

Our `docker-compose.yml` defines three services:

```yaml
version: '3.8'

services:
  # Main test/runtime service
  test:
    build: .
    container_name: bias-test
    command: ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]

  # Jupyter notebook service for interactive analysis
  jupyter:
    build: .
    container_name: bias-jupyter
    ports:
      - "8888:8888"
    volumes:
      - ./results:/app/results
      - ./notebooks:/app/notebooks
      - ./data:/app/data
    command: ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888",
              "--no-browser", "--allow-root"]
    restart: unless-stopped

  # Dashboard service
  dashboard:
    image: nginx:alpine
    container_name: bias-dashboard
    ports:
      - "8080:80"
    volumes:
      - ./dashboard:/usr/share/nginx/html:ro
    restart: unless-stopped
```

### Using Docker Compose

```bash
# Build all services
docker compose build

# Run tests
docker compose run test

# Start Jupyter in background
docker compose up -d jupyter
# Access at http://localhost:8888

# Start dashboard
docker compose up -d dashboard
# Access at http://localhost:8080

# Run all services
docker compose up

# Stop all services
docker compose down

# Rebuild and run
docker compose up --build
```

---

## Volume Mounting

Volumes let you persist data between container runs.

### Mounting Results

```bash
# Linux/macOS
docker run --rm \
    -v "$(pwd)/results:/app/results" \
    scoring-bias scoring-bias run-all --output results/

# Windows (PowerShell)
docker run --rm `
    -v "${PWD}/results:/app/results" `
    scoring-bias scoring-bias run-all --output results/

# Windows (cmd)
docker run --rm ^
    -v "%cd%/results:/app/results" ^
    scoring-bias scoring-bias run-all --output results/
```

### Mounting Data

```bash
docker run --rm \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/results:/app/results" \
    scoring-bias scoring-bias run-all --input data/custom_scores.csv
```

### Mounting Environment File

```bash
docker run --rm \
    --env-file .env \
    -v "$(pwd)/.env:/app/.env" \
    scoring-bias python inference_executor.py
```

---

## GPU Support

### Prerequisites

Install the **NVIDIA Container Toolkit**:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Run with GPU

```bash
# Run with all GPUs
docker run --rm --gpus all scoring-bias python run_rootcause.sh

# Run with specific GPU
docker run --rm --gpus '"device=0"' scoring-bias python run_rootcause.sh

# Run with GPU + volume mounts
docker run --rm --gpus all \
    -v "$(pwd)/results:/app/results" \
    scoring-bias python run_rootcause.sh
```

### GPU with Docker Compose

```yaml
# Add to docker-compose.yml
services:
  gpu-experiment:
    build: .
    container_name: bias-gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./results:/app/results
    command: ["python", "run_rootcause.sh"]
```

---

## Running Tests

```bash
# Using Docker directly
docker run --rm scoring-bias python -m pytest tests/ -v --tb=short

# Using Docker Compose
docker compose run test

# With coverage
docker run --rm scoring-bias \
    python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Keep container after run for investigation
docker run --name bias-test scoring-bias python -m pytest tests/
docker cp bias-test:/app/results ./results
docker rm bias-test
```

---

## Running Jupyter

```bash
# Start Jupyter
docker compose up -d jupyter

# Check logs for token
docker compose logs jupyter

# Access at http://localhost:8888
# Look for: http://127.0.0.1:8888/tree?token=...
```

### Jupyter with Custom Password

```bash
docker run --rm -p 8888:8888 \
    -v "$(pwd)/notebooks:/app/notebooks" \
    scoring-bias \
    jupyter notebook --ip=0.0.0.0 --port=8888 \
    --no-browser --allow-root \
    --NotebookApp.password='sha1:...'  # Or use token
```

---

## Running the Dashboard

```bash
# Using Docker Compose
docker compose up -d dashboard
# Access at http://localhost:8080

# Or using Docker directly with Python
docker run --rm -p 8501:8501 scoring-bias streamlit run dashboard.py
```

---

## Best Practices

### Image Size Optimization

- Use `python:3.11-slim` instead of `python:3.11` (saves ~500 MB)
- Use multi-stage builds to separate build and runtime
- Clean apt cache: `rm -rf /var/lib/apt/lists/*`
- Use `--no-cache-dir` with pip

### Security

- Don't hardcode API keys in Dockerfiles
- Use `--env-file` for secrets
- Don't run as root in production (add `USER appuser`)
- Use `.dockerignore` to exclude sensitive files

### `.dockerignore`

```
.git/
__pycache__/
*.pyc
.venv/
venv/
.env
results/
*.egg-info/
.gitignore
README.md
```

### Reproducibility

- Pin exact versions in `requirements.txt`
- Use `--no-cache` for critical builds
- Tag images with version numbers
- Keep Dockerfile in version control

---

## Troubleshooting

### Build Issues

| Problem | Solution |
|---------|----------|
| `gcc: command not found` | Install build-essential or use `python:3.11-slim` with apt-get |
| `pip install fails` | Check `requirements.txt` for pinned version conflicts |
| Disk space | Remove dangling images: `docker image prune` |
| Network timeout | Use `--network=host` or configure Docker DNS |

### Runtime Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Package not installed in image—rebuild |
| Permission denied | Use `chmod` in Dockerfile or run as root |
| Port already in use | Change host port: `-p 8889:8888` |
| Container exits immediately | Check command syntax in `CMD` or `command` |
| GPU not available | Install NVIDIA Container Toolkit |

### Common Commands

```bash
# List images
docker images

# List running containers
docker ps

# Stop all containers
docker stop $(docker ps -aq)

# Clean up unused resources
docker system prune -a

# Check image size
docker image inspect scoring-bias --format='{{.Size}}' | numfmt --to=iec

# View container logs
docker logs bias-test

# Enter running container
docker exec -it bias-test /bin/bash
```

---

## Quick Reference

```bash
# Build
docker build -t scoring-bias .

# Tests
docker compose run test
# OR: docker run --rm scoring-bias python -m pytest tests/ -v

# Analysis
docker run --rm -v "$(pwd)/output:/app/output" scoring-bias scoring-bias run-all

# Jupyter
docker compose up -d jupyter
# Open http://localhost:8888

# Dashboard
docker compose up -d dashboard
# Open http://localhost:8080

# Interactive shell
docker run --rm -it scoring-bias /bin/bash

# GPU
docker run --rm --gpus all scoring-bias python run_rootcause.sh

# Cleanup
docker compose down
docker system prune -a
```
