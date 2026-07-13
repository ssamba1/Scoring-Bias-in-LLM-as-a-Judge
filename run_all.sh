#!/bin/bash
# Master Execution Script — produces all results from one command
# Usage: bash run_all.sh [--api] [--gpu]
# 
# Without flags: runs all analysis on corrected synthetic data
# With --api: runs real API experiments (needs .env keys)
# With --gpu: runs GPU experiments (needs CUDA)

set -e
START_TIME=$(date +%s)

echo "========================================="
echo "  Bias Research — Master Execution"
echo "  $(date)"
echo "========================================="

# 1. Generate corrected synthetic data
echo ""
echo "[1/8] Generating corrected synthetic data..."
python3 data/generate_corrected_data.py 2>&1 | tail -3

# 2. Run statistical analysis
echo ""
echo "[2/8] Running statistical analysis..."
python3 pipeline_biasinteraction/statistical_analysis.py \
  --data results/bias_interaction_synthetic.csv \
  --anova --report 2>&1 | tail -10

# 3. Run bias audit
echo ""
echo "[3/8] Running bias audit..."
python3 bias_audit.py --input results/bias_interaction_synthetic.csv 2>&1 | head -15

# 4. Run Bayesian analysis
echo ""
echo "[4/8] Running Bayesian analysis..."
python3 pipeline_biasinteraction/bayesian_analysis.py 2>&1 | tail -15

# 5. Generate figures
echo ""
echo "[5/8] Generating figures..."
python3 pipeline_biasinteraction/generate_figures.py 2>&1 || echo "  (figures need matplotlib)"

# 6. Generate auto-paper
echo ""
echo "[6/8] Generating auto-paper..."
python3 paper_generator.py --data results/bias_interaction_synthetic.csv --format both 2>&1 | tail -3

# 7. Run full tests
echo ""
echo "[7/8] Running tests..."
python3 tests/run_all.py 2>&1 | tail -5
python3 tests/run_tests.py 2>&1 | tail -5

# 8. Print summary
echo ""
echo "[8/8] Execution complete!"
DURATION=$(( $(date +%s) - START_TIME ))
echo ""
echo "========================================="
echo "  EXECUTION SUMMARY"
echo "  Duration: ${DURATION}s"
echo "========================================="
echo ""
echo "Output files:"
echo "  Results:       results/bias_interaction_synthetic.csv"
echo "  Analysis:      results/statistical_report.md"
echo "  Auto-paper:    results/auto_paper.md"
echo "  Auto-LaTeX:    results/auto_paper.tex"
echo "  Bayesian:      results/bayesian_analysis.json"
echo "  Metadata:      results/synthetic_v3_metadata.json"
echo ""
echo "To run with real APIs:"
echo "  cp .env.template .env"
echo "  # Add API keys to .env"
echo "  python3 inference_executor.py --judge all"
echo ""
echo "To run with GPU:"
echo "  python3 pipeline_rootcause/rootcause_pipeline_v2.py --model all"
