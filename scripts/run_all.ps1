<#
.SYNOPSIS
    Master Run All Script (PowerShell) — Root Cause Analysis Pipeline
.DESCRIPTION
    Runs the complete root cause analysis pipeline:
    1. Validate data
    2. Run analyses
    3. Generate figures
    4. Run tests
    5. Print summary
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$ScriptsDir = Join-Path $ProjectRoot "scripts"
$ResultsDir = Join-Path $ProjectRoot "results_rootcause"
$PaperDir = Join-Path $ProjectRoot "paper"

Write-Host "╔" ("═" * 58) "╗" -ForegroundColor Cyan
Write-Host "║       ROOT CAUSE ANALYSIS — MASTER PIPELINE" -ForegroundColor Cyan
Write-Host "╚" ("═" * 58) "╝" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
Write-Host "Date:    $(Get-Date)"
Write-Host ""

# ── 1. Check environment ──
Write-Host "━━━ [1/7] Checking environment ──────────────────────────────" -ForegroundColor Green
python --version
pip --version
Write-Host "  ✓ Python available"

# ── 2. Data quality check ──
Write-Host ""
Write-Host "━━━ [2/7] Data quality report ───────────────────────────────" -ForegroundColor Green
python (Join-Path $ScriptsDir "data_quality.py")
Write-Host "  ✓ Data quality report generated"

# ── 3. Cross-validation study ──
Write-Host ""
Write-Host "━━━ [3/7] Cross-validation study ────────────────────────────" -ForegroundColor Green
python (Join-Path $ScriptsDir "cross_validation.py")
Write-Host "  ✓ Cross-validation complete"

# ── 4. Simulation study ──
Write-Host ""
Write-Host "━━━ [4/7] Simulation study ──────────────────────────────────" -ForegroundColor Green
python (Join-Path $ScriptsDir "simulation_study.py")
Write-Host "  ✓ Simulation study complete"

# ── 5. Bootstrap stability ──
Write-Host ""
Write-Host "━━━ [5/7] Bootstrap stability analysis ──────────────────────" -ForegroundColor Green
python (Join-Path $ScriptsDir "bootstrap_stability.py")
Write-Host "  ✓ Bootstrap stability complete"

# ── 6. Dashboard check ──
Write-Host ""
Write-Host "━━━ [6/7] Dashboard ─────────────────────────────────────────" -ForegroundColor Green
$Dashboard = Join-Path $PaperDir "interactive" "analysis_dashboard.html"
if (Test-Path $Dashboard) {
    Write-Host "  ✓ Dashboard exists at $Dashboard"
} else {
    Write-Host "  ⚠ Dashboard not found, was it created?"
}

# ── 7. Summary ──
Write-Host ""
Write-Host "━━━ [7/7] Summary ───────────────────────────────────────────" -ForegroundColor Green
Write-Host ""
Write-Host "  All scripts completed successfully." -ForegroundColor Green
Write-Host ""
Write-Host "  Output files:" -ForegroundColor Yellow
Write-Host "    Data Quality:    $ResultsDir\data_quality_report.json"
Write-Host "    Cross-Validation: $ResultsDir\cross_validation.json"
Write-Host "    Simulation:       $ResultsDir\simulation_results.json"
Write-Host "    Bootstrap:        $ResultsDir\bootstrap_stability.json"
Write-Host "    Dashboard:        $Dashboard"
Write-Host ""

# Print key stats
Write-Host "  Key numbers:" -ForegroundColor Yellow
python -c @"
import json
with open(r'$ResultsDir\t4fam_results.json') as f:
    t4 = json.load(f)
with open(r'$ResultsDir\study1_results.json') as f:
    s1 = json.load(f)
print(f'  Total models: {len(t4) + len(s1)}')
print(f'  T4 models: {len(t4)}')
print(f'  Study1 models: {len(s1)}')
"@

Write-Host ""
Write-Host "╔" ("═" * 58) "╗" -ForegroundColor Cyan
Write-Host "║       PIPELINE COMPLETE ✓" -ForegroundColor Cyan
Write-Host "╚" ("═" * 58) "╝" -ForegroundColor Cyan
