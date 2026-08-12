#!/bin/bash
# Run the root cause pipeline
# Usage: bash run_rootcause.sh

echo "=== Root Cause of Scoring Bias Pipeline ==="
echo ""

echo "[1/4] Installing dependencies..."
pip install -r pipeline_rootcause/requirements.txt

echo "[2/4] Running pipeline..."
python3 pipeline_rootcause/rootcause_pipeline.py

echo "[3/4] Done! Results in results_rootcause/ directory"
echo ""
echo "NOTE: To run with real HuggingFace models,"
echo "implement score_with_hf_model() in pipeline_rootcause/rootcause_pipeline.py"
echo "Then run: python3 pipeline_rootcause/rootcause_pipeline.py"
