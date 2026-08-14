#!/bin/bash
# One-command setup for the research project
# Usage: bash setup.sh

set -e

echo "========================================"
echo "  Research Project Setup"
echo "========================================"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PY=python3
elif command -v python &> /dev/null; then
    PY=python
else
    echo "ERROR: Python not found. Install Python 3.9+"
    exit 1
fi

echo "[1/4] Python version: $($PY --version)"

# Clone if not already
if [ ! -f "README.md" ]; then
    echo "[2/4] Cloning repository..."
    git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
    cd research-draft
else
    echo "[2/4] Already in repository"
fi

# Install dependencies
echo "[3/4] Installing dependencies..."

# Option 2 dependencies
echo "  Installing API-based pipeline dependencies..."
$PY -m pip install --quiet openai anthropic google-generativeai pandas numpy scipy matplotlib seaborn statsmodels pyyaml 2>/dev/null || echo "  (Some packages may have failed  install manually if needed)"

# Option 1 dependencies
echo "  Installing GPU pipeline dependencies..."
$PY -m pip install --quiet transformers torch accelerate huggingface_hub 2>/dev/null || echo "  (Some packages may have failed  install manually if needed)"

# Run tests. Until 2026-08-13 this invoked a runner script under tests/ that has
# not existed since the rewrite, so the last step of setup always failed. The
# path is not repeated here: a guard reads this file for paths that do not
# resolve, and naming it would trip the check that caught it.
echo "[4/4] Running tests..."
$PY -m pytest tests/ -q

echo ""
echo "========================================"
echo "  SETUP COMPLETE"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Read the paper of record: paper/honest/scoring_bias_v2.tex"
echo "  2. Reproduce every number:   bash run_all.sh"
echo "  3. Check it like CI does:    python3 verify_like_ci.py"
echo ""
echo "Quick links:"
echo "  Test suite:       python3 -m pytest tests/ -q"
echo "  Guard mutations:  python3 mutation_check.py"
echo "  Prose gate:       cd paper/honest/repro && python3 check_prose.py"
echo "  Preregistration:  paper/honest/PREREGISTRATION.md"
