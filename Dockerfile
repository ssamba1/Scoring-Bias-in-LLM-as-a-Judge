FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge"
LABEL org.opencontainers.image.description="LLM-as-a-Judge Bias Research Environment"
LABEL org.opencontainers.image.version="1.0.0"

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
pip install --no-cache-dir \
    -r requirements.txt \
    torch --extra-index-url https://download.pytorch.org/whl/cpu

# Make scripts executable
RUN chmod +x *.sh

# Create directories
RUN mkdir -p results results_rootcause cache benchmark

# Default command
CMD ["python3", "dashboard.py"]
