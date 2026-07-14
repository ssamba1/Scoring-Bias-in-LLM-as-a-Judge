#!/usr/bin/env bash
# Complete end-to-end reproduction pipeline
# Usage: bash run_all.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Scoring Bias: Full Reproduction Pipeline ==="
echo "Started: $(date)"
echo ""

# 1. Install dependencies
echo "[1/6] Installing dependencies..."
pip install -r requirements.txt -q
echo "  Done."

# 2. Run tests
echo "[2/6] Running unit tests..."
python3 tests/test_all.py
echo "  Done."

# 3. Generate figures (requires matplotlib)
echo "[3/6] Generating figures..."
if python3 -c "import matplotlib" 2>/dev/null; then
    python3 paper/generate_png_figures.py
    python3 paper/figures_advanced/generate_advanced_figures.py
    echo "  Done."
else
    echo "  Skipped (matplotlib not installed). Run: pip install matplotlib"
fi

# 4. Run all analyses
echo "[4/6] Running analysis pipeline..."
echo "  Depth analysis..."
python3 results_rootcause/depth_analysis.py 2>&1 | tail -3
echo "  Cross-probe analysis..."
python3 results_rootcause/cross_probe_analysis.py 2>&1 | tail -3
echo "  Peer review defense..."
python3 results_rootcause/peer_review_defense.py 2>&1 | tail -3
echo "  Model ranking..."
python3 results_rootcause/model_ranking_analysis.py 2>&1 | tail -3
echo "  Variance decomposition..."
python3 results_rootcause/variance_decomposition.py 2>&1 | tail -3
echo "  Done."

# 5. Compile paper if pdflatex available
echo "[5/6] Compiling paper..."
if command -v pdflatex &> /dev/null; then
    cd paper
    pdflatex camera_ready_full.tex -interaction=nonstopmode 2>&1 | tail -1
    pdflatex camera_ready_full.tex -interaction=nonstopmode 2>&1 | tail -1
    cd ..
    echo "  Done."
else
    echo "  Skipped (pdflatex not installed)."
fi

# 6. Build arXiv package
echo "[6/6] Building arXiv submission package..."
python3 paper/arxiv_package.py 2>&1 | tail -3
echo "  Done."

echo ""
echo "=== Pipeline complete. ==="
echo "Results: results_rootcause/*.json"
echo "Figures: paper/figures_png/*.png, paper/figures_advanced/*.png"
echo "Paper:   paper/camera_ready_full.pdf"
echo "Archive: arxiv_submission.tar.gz"
echo "Finished: $(date)"
