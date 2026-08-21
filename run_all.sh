#!/usr/bin/env bash
# Complete end-to-end reproduction of the paper of record.
#
# Until 2026-08-11 this script reproduced the *retracted* version: it built
# camera_ready_full.tex, regenerated the fabricated-era figures, and ran the
# analyses over the suspect 22-model set. A reader running it to check the paper
# would have reproduced the wrong paper, and every step would have succeeded.
#
# The paper of record is paper/honest/scoring_bias_v2.tex. Everything the
# retracted version left behind is under RETRACTED/ and is not run here.
#
# Usage: bash run_all.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Scoring Bias: Full Reproduction Pipeline ==="
echo "Started: $(date)"
echo ""

echo "[1/7] Installing dependencies..."
pip install -r paper/honest/repro/requirements-repro.txt -q
pip install pytest -q
echo "  Done."

echo "[2/7] Integrity: nothing fabricated live, guards can fail, no credentials..."
python3 -m pytest tests/ -q
python3 mutation_check.py
python3 scan_secrets.py
echo "  Done."

echo "[3/7] Regenerating every derived result from the committed raw data..."
cd paper/honest/repro
for f in analyze_peritem.py analyze_mechanism.py analyze_gold.py \
         analyze_robustness.py analyze_stages.py analyze_spanpatch.py \
         analyze_dose.py analyze_gran.py analyze_chat.py analyze_sampled.py \
         analyze_t10.py analyze_tokvar.py analyze_closed.py analyze_nulls.py analyze_bands.py analyze_readout.py analyze_quantization.py analyze_speccurve.py; do
    python3 "$f" > /dev/null
done
for raw in results_probes2.json results_zh.json results_14b.json; do
    python3 analyze_newprobes.py "$raw" > /dev/null
done
cd ../../..
echo "  Done."

echo "[4/7] Checking the derived results match what is committed..."
git diff --exit-code -- paper/honest/repro/ paper/honest/tables/ \
    || { echo "  MISMATCH: regenerated results differ from the committed ones."; exit 1; }
echo "  Done."

echo "[5/7] Checking the prose and figures against the data..."
cd paper/honest/repro
python3 check_prose.py
python3 check_figures.py
cd ../../..
echo "  Done."

echo "[6/7] Compiling the paper..."
if command -v pdflatex &> /dev/null; then
    cd paper/honest
    pdflatex -interaction=nonstopmode scoring_bias_v2.tex 2>&1 | tail -1
    bibtex scoring_bias_v2 2>&1 | tail -1
    pdflatex -interaction=nonstopmode scoring_bias_v2.tex 2>&1 | tail -1
    pdflatex -interaction=nonstopmode scoring_bias_v2.tex 2>&1 | tail -1
    cd ../..
    echo "  Done."
else
    echo "  Skipped (pdflatex not installed)."
fi

echo "[7/7] Building and verifying the arXiv submission package..."
python3 paper/honest/arxiv_package.py 2>&1 | tail -4
echo "  Done."

echo ""
echo "=== Pipeline complete. ==="
echo "Results: paper/honest/repro/*.json"
echo "Figures: paper/honest/figures/*.pdf"
echo "Paper:   paper/honest/scoring_bias_v2.pdf"
echo "Archive: paper/honest/arxiv_submission.tar.gz"
echo "Finished: $(date)"
