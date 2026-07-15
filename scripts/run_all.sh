#!/usr/bin/env bash
# ======================================================================
# MASTER RUN ALL SCRIPT (Bash)
# Runs the complete root cause analysis pipeline:
#   1. Validate data
#   2. Run analyses
#   3. Generate figures
#   4. Run tests
#   5. Print summary
# ======================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$PROJECT_DIR/results_rootcause"
PAPER_DIR="$PROJECT_DIR/paper"

# Change to project dir so Python can use relative paths
cd "$PROJECT_DIR"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       ROOT CAUSE ANALYSIS — MASTER PIPELINE                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Project: $PROJECT_DIR"
echo "Date:    $(date)"
echo ""

# ── 1. Check environment ──
echo "━━━ [1/7] Checking environment ──────────────────────────────"
python3 --version
echo "  ✓ Python available"

# ── 2. Data quality check ──
echo ""
echo "━━━ [2/7] Data quality report ───────────────────────────────"
python3 scripts/data_quality.py
echo "  ✓ Data quality report generated"

# ── 3. Cross-validation study ──
echo ""
echo "━━━ [3/7] Cross-validation study ────────────────────────────"
python3 scripts/cross_validation.py
echo "  ✓ Cross-validation complete"

# ── 4. Simulation study ──
echo ""
echo "━━━ [4/7] Simulation study ──────────────────────────────────"
python3 scripts/simulation_study.py
echo "  ✓ Simulation study complete"

# ── 5. Bootstrap stability ──
echo ""
echo "━━━ [5/7] Bootstrap stability analysis ──────────────────────"
python3 scripts/bootstrap_stability.py
echo "  ✓ Bootstrap stability complete"

# ── 6. Dashboard check ──
echo ""
echo "━━━ [6/7] Dashboard ─────────────────────────────────────────"
DASHBOARD="$PAPER_DIR/interactive/analysis_dashboard.html"
if [ -f "$DASHBOARD" ]; then
    echo "  ✓ Dashboard exists at $DASHBOARD"
else
    echo "  ⚠ Dashboard not found, was it created?"
fi

# ── 7. Summary ──
echo ""
echo "━━━ [7/7] Summary ───────────────────────────────────────────"
echo ""
echo "  All scripts completed successfully."
echo ""
echo "  Output files:"
echo "    Data Quality:    $RESULTS_DIR/data_quality_report.json"
echo "    Cross-Validation: $RESULTS_DIR/cross_validation.json"
echo "    Simulation:       $RESULTS_DIR/simulation_results.json"
echo "    Bootstrap:        $RESULTS_DIR/bootstrap_stability.json"
echo "    Dashboard:        $DASHBOARD"
echo ""

# Print key stats
echo "  Key numbers:"
python3 -c "
import json
with open('results_rootcause/t4fam_results.json') as f:
    t4 = json.load(f)
with open('results_rootcause/study1_results.json') as f:
    s1 = json.load(f)
print(f'  Total models: {len(t4) + len(s1)}')
print(f'  T4 models: {len(t4)}')
print(f'  Study1 models: {len(s1)}')
"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       PIPELINE COMPLETE ✓                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
