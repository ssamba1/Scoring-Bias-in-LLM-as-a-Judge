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
