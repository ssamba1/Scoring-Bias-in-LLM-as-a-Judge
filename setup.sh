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
$PY -m pip install --quiet openai anthropic google-generativeai pandas numpy scipy matplotlib seaborn statsmodels pyyaml 2>/dev/null || echo "  (Some packages may have failed — install manually if needed)"

# Option 1 dependencies
echo "  Installing GPU pipeline dependencies..."
$PY -m pip install --quiet transformers torch accelerate huggingface_hub 2>/dev/null || echo "  (Some packages may have failed — install manually if needed)"

# Run tests
echo "[4/4] Running tests..."
$PY tests/run_tests.py

echo ""
echo "========================================"
echo "  SETUP COMPLETE"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Read the proposals: less proposals/01_rootcause_scoring_bias.md"
echo "  2. Set up API keys: cp .env.template .env"
echo "  3. Run synthetic pilot: python3 pipeline_biasinteraction/generate_synthetic_pilot.py"
echo "  4. Explore: python3 explore_results.py"
echo ""
echo "Quick links:"
echo "  FAQ:              python3 FAQ.py"
echo "  Dashboard:        python3 dashboard.py"
echo "  Bias Explorer:    python3 bias_explorer.py --stats"
echo "  Run tests:        python3 tests/run_tests.py"
