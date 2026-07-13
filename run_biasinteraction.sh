#!/bin/bash
# Run the full bias interaction pipeline
# Usage: bash run_biasinteraction.sh

echo "=== Bias Interaction Effects Pipeline ==="
echo ""

# Step 1: Install dependencies
echo "[1/4] Installing dependencies..."
pip install -r pipeline_biasinteraction/requirements.txt

# Step 2: Generate synthetic data and analysis
echo "[2/4] Running synthetic pilot..."
python3 pipeline_biasinteraction/generate_synthetic_pilot.py

# Step 3: Run analysis
echo "[3/4] Running analysis..."
python3 pipeline_biasinteraction/analysis.py

# Step 4: Generate report
echo "[4/4] Done! Results in results/ directory"
echo ""
echo "To run with real API calls:"
echo "  1. Add API keys to pipeline_biasinteraction/scoring_pipeline.py"
echo "  2. Run: python3 pipeline_biasinteraction/scoring_pipeline.py --judge claude"
echo "  3. Repeat for each judge model"
echo "  4. Run analysis on real data: python3 pipeline_biasinteraction/analysis.py"
