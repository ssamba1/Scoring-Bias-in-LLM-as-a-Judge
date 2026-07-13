#!/bin/bash
# Automated Experiment Pipeline — One-click full run
# Usage: bash auto_pipeline.sh
# Requires: API keys in .env (for Option 2), Kaggle API (for Option 1)
set -e

START=$(date +%s)

echo "============================================"
echo "  Automated Experiment Pipeline"
echo "  $(date)"
echo "============================================"

# Step 0: Check environment
echo ""
echo "[0] Checking environment..."
python3 -c "import torch; print(f'  PyTorch {torch.__version__}')" 2>/dev/null || echo "  PyTorch not found"
python3 -c "import transformers; print(f'  Transformers {transformers.__version__}')" 2>/dev/null || echo "  Transformers not found"

# Step 1: Generate canonical synthetic data
echo ""
echo "[1/7] Generating canonical synthetic data..."
python3 data/generate_data.py 2>&1 | tail -3

# Step 2: Run statistical analysis
echo ""
echo "[2/7] Running statistical analysis..."
python3 pipeline_biasinteraction/statistical_analysis.py \
  --data results/bias_interaction_synthetic.csv 2>&1 | tail -5

# Step 3: Compute full metrics
echo ""
echo "[3/7] Computing full metrics..."
python3 results_rootcause/compute_metrics.py 2>&1 | tail -5

# Step 4: Run bias audit
echo ""
echo "[4/7] Running bias audit..."
python3 bias_audit.py --input results/bias_interaction_synthetic.csv 2>&1 | head -5

# Step 5: Generate auto-paper
echo ""
echo "[5/7] Generating auto-paper..."
python3 auto_writer.py --data results/bias_interaction_synthetic.csv --format all 2>&1 | tail -3

# Step 6: Generate publication figures
echo ""
echo "[6/7] Generating publication figures..."
python3 paper/figures/generate_all_figures.py 2>&1 | tail -3

# Step 7: Run tests
echo ""
echo "[7/7] Running tests..."
python3 tests/run_all.py 2>&1 | tail -5
python3 tests/run_tests.py 2>&1 | tail -3

# Summary
DURATION=$(( $(date +%s) - START ))
echo ""
echo "============================================"
echo "  PIPELINE COMPLETE"
echo "  Duration: ${DURATION}s"
echo "============================================"
echo ""
echo "Outputs:"
echo "  Canonical data:  results/bias_interaction_synthetic.csv"
echo "  Metrics:         results_rootcause/full_metrics.json"
echo "  Auto-paper:      paper/auto_generated/auto_paper.tex (and .md)"
echo "  Figures:         paper/figures/study1/fig1-8*.html"
echo "  Tables:          paper/figures/study1/tab1-6*.tex"
echo ""
echo "To run real API experiments:"
echo "  cp .env.template .env  (add API keys)"
echo "  python3 inference_executor.py --judge all"
echo ""
echo "To run on Kaggle (free GPU):"
echo "  Upload pipeline_rootcause/study1_full.kaggle.ipynb"
echo "  Set GPU: P100 or T4"
echo "  Run cells 1-7"
