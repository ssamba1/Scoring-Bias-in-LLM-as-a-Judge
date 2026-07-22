# Nightly Analysis — 2026-07-16 (LATEST)

## Simulation Recovery
- **Best:** Δ=1.0 at N=20 (error: +3.83%)
- **Worst:** Δ=0.1 at N=15 (error: +382.2%)
- **Trend:** Larger Δ → much better recovery; N has weak/inconsistent effect. Δ≥0.5 recovers within 20%.

## Cross-Validation
- **Most stable probe:** reference_answer (mean|%Δ|=4.16%)
- **Most variable probe:** rubric_order (mean|%Δ|=16.32%)
- **Key insight:** Content bias estimates are family-independent; format bias depends on which families are included.

## Data Quality
- **Status:** PASS
- study1 == max_scale: 0 discrepancies
- 49 outliers + 9 "impossible" flagged — all false positives (expected scale-boundary values, legitimate %/negative deltas)

## Cross-Probe Correlations
- IIAR bound holds for all 3 tested families. Format-content differential effect in 2/3 families. Limited by hardcoded N=3.

## Tests
- **80/80 passed**

## Overnight Summary
Data pipeline healthy. Small-effect recovery noise-dominated (Δ≤0.3), Δ≥0.5 reliable. Reference answer bias most robust finding. All tests pass.
