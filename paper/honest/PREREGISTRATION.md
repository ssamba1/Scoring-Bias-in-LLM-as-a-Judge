# Preregistration — Decisiveness Governs Judge Bias

Registered **before** analyzing the scaled run. Predictions derive from
Proposition 1 (score-distribution variance bounds nuisance-sensitivity). Analysis
code (`repro/analyze_peritem.py`, `repro/analyze_mechanism.py`, `repro/analyze_gold.py`)
and the metric definitions were fixed in advance; only the raw scores were pending.

## Design
- **Unit:** model family (base vs instruct), n = up to 13 open-weight families (0.1–8B).
- **Bias families (5):** rubric order, score ID, reference answer (Li et al. 2025);
  authority, verbosity (generality test).
- **Metric:** bias `Δ` = max inter-variant spread in mean expected-value score;
  scoring by expected value over answer tokens (fixes the parse-failure confound).
- **Seed:** 42. Bootstrap: 10^4 resamples.

## Confirmatory predictions
- **H0 (origin).** Instruction tuning changes bias magnitude (paired Wilcoxon per
  probe, Holm-corrected across probes; bootstrap 95% CI of mean change).
- **P1 (sharpening).** Instruction tuning lowers score-distribution entropy
  (paired, base > instruct).
- **P2 (link).** Across families and probes, entropy correlates positively with `Δ`
  (Spearman > 0). *This is the core mechanism claim.*
- **P3 (causal).** Patching the instruct residual into the base model at the score
  position moves the base score toward the instruct score in > 50% of items, and this
  fraction rises with layer depth.
- **P4 (generality).** P2 holds within the content-perturbation group
  (authority, verbosity), not only the format group.
- **P5 (predictive).** A model's mean bias is predictable out-of-sample
  (leave-one-family-out) from its control-condition entropy alone (LOO R² > 0).
- **P6 (validity).** Nuisance perturbations reduce ground-truth good-vs-bad
  discrimination (accuracy and margin), and instruction tuning reduces this loss.

## Reporting rules
- Report all five bias families and all families run, including failures.
- Report effect sizes and CIs as primary evidence; treat any single p-value as
  secondary and Holm-correct across probes.
- Any prediction that fails is reported as a failure, not omitted.
- Exploratory analyses (e.g. per-domain, per-recipe) are labeled exploratory.
