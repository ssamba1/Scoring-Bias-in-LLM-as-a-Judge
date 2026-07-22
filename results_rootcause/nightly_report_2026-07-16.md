# Nightly Analysis — 2026-07-16

## Simulation Recovery

| Effect Size | N=5     | N=10    | N=15    | N=20    | Trend |
|-------------|---------|---------|---------|---------|-------|
| Δ=0.1       | +300.0% | +290.0% | +382.2% | +351.7% | Noise floor — signal undetectable |
| Δ=0.3       | +93.3%  | +54.4%  | +70.4%  | +61.1%  | Still high but improving |
| Δ=0.5       | +10.7%  | +20.0%  | +8.9%   | +15.0%  | **Acceptable** (<20%) |
| Δ=0.8       | −13.3%  | +13.8%  | −5.6%   | +7.1%   | Good recovery |
| Δ=1.0       | −6.7%   | +5.7%   | +4.5%   | +3.8%   | **Best recovery** |

- **Best:** Δ=1.0 at N=20 (error: +3.83%) — near-perfect recovery
- **Worst:** Δ=0.1 at N=15 (error: +382.2%) — signal buried in noise
- **Trends:**
  - Effect size Δ dominates recovery quality; N (sample size) has weak, inconsistent impact
  - Small effects (Δ≤0.3) are systematically overestimated by 54–382%
  - Δ≥0.8 recovers within ±14% regardless of N
  - Counterintuitive: larger N doesn't help at very small Δ — the noise is structural (per-family random variance σ~0.3), not sampling noise

## Cross-Validation

| Probe              | Mean\|%Δ\| (LOO) | K-fold Stdev | Robustness Rank |
|--------------------|-----------------|--------------|-----------------|
| reference_answer   | 4.16%           | 0.451        | **1 (most robust)** |
| score_id           | 6.50%           | 0.770        | 2               |
| rubric_order       | 16.32%          | 0.606        | 3 (least robust) |

- **Most stable probe:** `reference_answer` — lowest variance across LOO folds and K-fold splits. Content bias estimates are robust to which families are included.
- **Most variable probe:** `rubric_order` — mean|%Δ| = 16.32%, driven by sensitivity to specific families. Removing Llama-3.2-3B causes the biggest swing.
- **Most influential family:** Llama-3.2-3B (mean|Δ|=0.189); Qwen2.5-7B least influential (mean|Δ|=0.050).
- **Key insight:** Format bias (rubric) estimates are family-dependent; content bias (reference answer) generalizes cleanly across families.

## Data Quality

- **Status: PASS** (with noted data characteristics, not quality defects)
- **study1 vs max_scale consistency:** 0 differences out of 22 models — identical datasets
- **Missing values:** 0 across all four data files
- **Impossible values:** 9 flagged in `rootcause_analysis.json` — all false positives:
  - 6 negative values in `reference_answer` deltas (legitimate — bias can go negative)
  - 3 pct_affected=43.3% flagged as "above_max_scale" (legitimate percentage, not a score)
  - These are scoring tool limitations, not data errors
- **Outliers:** 49 flagged in study1 datasets (20 each in study1_results + study1_max_scale, 9 in rootcause_analysis) — all are scale-boundary values (low 1.2–1.8, high 4.2–5.0), expected for scoring distributions
- **T4 models in rootcause_analysis:** 0/14 — expected mismatch (different naming conventions, different analysis scope)

No action required. Data integrity is solid.

## Cross-Probe Correlations

- **IIAR bound** (|Δ_rubric| + |Δ_score| ≥ |Δ_ref|): **Holds for all 3 families** — consistent with Format Efficiency Hypothesis
- **Format-format correlation:** Mixed — rubric and score ID deltas don't uniformly move together (rubric: [+3.20, −0.66, +1.26]; score: [−0.18, +0.84, +0.90])
- **Format-content direction:** Not consistently opposite — the differential effect (format↓, content↑) is observed in 2/3 families, not universal
- **Domain analysis:** DailyLife shows highest bias (2.3), Math lowest (1.2) — illustrative, not from full pipeline
- **Caveat:** This analysis is hardcoded to 3 families (Llama-3-8B, Mistral-7B, Gemma-2-2B) — not representative of the full 7 T4 families. Results are suggestive, not conclusive.

## Tests

- **Status: 80/80 passed** (1.35s)
- **4 test modules:** test_all.py (19), test_analysis.py (26), test_metrics.py (23), test_models.py (20)
- **No regressions** — first nightly run, no baseline to compare

## Overnight Summary

Data pipeline healthy. Small-effect recovery is noise-dominated (Δ≤0.3 unreliable), but Δ≥0.5 recovers within 20%. Reference answer bias is the most robust finding in cross-validation. Data files are consistent (study1 == max_scale). All 80 tests pass. Cross-probe analysis is limited by hardcoded N=3 families — should be updated to use full T4 dataset.
