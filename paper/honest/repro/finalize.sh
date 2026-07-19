#!/usr/bin/env bash
# One-shot finalize: pull Kaggle outputs, run all analyses, regenerate figures.
# Usage: bash finalize.sh   (run from paper/honest/repro/)
set -e
export PATH="$PATH:$HOME/.local/bin"
SCALED_OUT="${SCALED_OUT:-/tmp/kag_scaled}"
PATCH_OUT="${PATCH_OUT:-/tmp/kag_patch}"
mkdir -p "$SCALED_OUT" "$PATCH_OUT"

echo "== pulling scaled =="
kaggle kernels output srisamba/scoring-bias-scaled -p "$SCALED_OUT" || true
echo "== pulling patch =="
kaggle kernels output srisamba/scoring-bias-patch -p "$PATCH_OUT" || true

# copy raw into repo (canonical inputs)
[ -f "$SCALED_OUT/results_scaled.json" ] && cp "$SCALED_OUT/results_scaled.json" ./results_scaled.json
[ -f "$PATCH_OUT/patch_results.json" ]   && cp "$PATCH_OUT/patch_results.json" ./patch_results.json

echo "== analyses =="
python analyze_peritem.py   ./results_scaled.json
python analyze_mechanism.py ./results_scaled.json

echo "== figures =="
python make_mech_figures.py             # fig1 (scaled), mechanism, patch -- all from real data

echo "DONE. Inspect results_peritem.json, results_mechanism.json, figures/."
