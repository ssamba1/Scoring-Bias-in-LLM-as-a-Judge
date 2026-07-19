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

## Addendum (registered 2026-07-19, before stage-ablation data arrived)

The alignment-stage ablation (`repro/stage_harness.py`: OLMo-2 1B and 7B
base → SFT → DPO → RLVR; Tülu-3-8B SFT → DPO → RLVR) was launched on
2026-07-19; these predictions were written while the run was in progress and
before any of its results were read. Analysis code (`repro/analyze_stages.py`)
was committed before results arrived.

- **P7 (stage of onset).** The responsiveness rise (mean TV shift of the answer
  distribution under nuisance) appears at the **SFT** stage: SFT responsiveness >
  base responsiveness in a majority of family×probe cells, and SFT accounts for
  more than half of the total base→final responsiveness rise.
- **P8 (preference stages).** DPO/RLVR further sharpen the distribution (entropy
  drops at each stage) but add less responsiveness than SFT did.
- **P9 (bias follows).** Measured bias Δ increases at whichever stage
  responsiveness increases (per-stage sign agreement above chance), consistent
  with the per-cell decomposition test (§5.3 of the paper).

Failure of any of P7–P9 is reported as a failure.

**Outcomes (recorded 2026-07-19 after the run completed; commit history shows
the predictions and analyzer predate the data):**
- P7 **confirmed**: SFT raises responsiveness in 10/10 family×probe cells; the
  SFT step accounts for 84% (OLMo-2-1B) and 99% (OLMo-2-7B) of the total
  base→RLVR responsiveness rise.
- P8 **confirmed**: entropy falls at every stage (preference stages most);
  DPO/RLVR add far less responsiveness than SFT (OLMo-7B: −0.01/+0.01 vs +0.06).
- P9 **7/8 transitions** sign-agree (binomial p = 0.07; marginal at n = 8,
  reported as such).

## Addendum 2 (registered 2026-07-19, before any of these runs completed)

Four further experiments launched 2026-07-19 (`repro/probes2_harness.py`,
`repro/zh_harness.py`, `repro/q14b_harness.py`, `repro/spanpatch_harness.py`);
predictions written before any results were read.

- **P10 (new bias types).** Two content perturbations not in the original suite —
  sycophancy (user states an opinion before scoring) and anchoring (a numeric
  anchor is stated) — show the same pattern: instruct Δ > base Δ in a majority
  of the 13 families, for both probes.
- **P11 (language generality).** On a fully Chinese version of the 5-probe suite
  (Qwen2.5 0.5–7B), (a) instruct Δ > base Δ on average, and (b) the pooled
  entropy–bias correlation is negative.
- **P12 (scale).** Qwen2.5-14B (NF4 4-bit) continues the pattern: instruct mean
  Δ > base mean Δ.
- **P13 (locus of responsiveness).** Overwriting the instruct model's residual
  stream at the nuisance-span positions with the base model's activations
  (Qwen2.5-1.5B; expert-authority and good-exemplar probes) reduces the
  instruct bias toward the base level by more than 50% in at least one layer
  band; i.e., the instruct encoding of the nuisance span causally carries the
  extra responsiveness.

Failure of any of P10–P13 is reported as a failure.

**P11 outcome (recorded 2026-07-19 after the run):** CONFIRMED.
Fully-Chinese 5-probe suite, Qwen2.5 0.5/1.5/3/7B, zero errors: (a) instruct Δ >
base Δ in 4/4 families (mean +0.43; positive point estimate for all five probes);
(b) pooled entropy–bias Spearman ρ = −0.36 (p = 0.024, n = 40).

**P10 outcome (recorded 2026-07-19 after the run):** SPLIT.
- Sycophancy: **confirmed** — instruct Δ > base Δ in 11/13 families, mean change
  +0.46 (Wilcoxon p = 0.027); the instruct-side bias (1.37) is the largest of any
  probe measured in this project.
- Anchoring: **not supported** — 9/13 families positive (nominal majority) but the
  mean change is +0.015 (p = 0.54), i.e., null in magnitude. Reported as a failure
  of the "both probes" clause.

## Addendum 3 (registered 2026-07-19, before these CPU runs launched)

Two further experiments on Kaggle CPU (`repro/dose_harness.py`,
`repro/template10_harness.py`); predictions written before launch.

- **P14 (dose–response).** Bias increases monotonically with nuisance magnitude
  (verbosity: 0/1/2/4/8 filler units; authority: 5 graded framing strengths), and
  the instruct checkpoint's dose–response slope exceeds the base checkpoint's in
  a majority of family×probe cells — the dose-level form of the responsiveness
  claim.
- **P15 (template breadth).** Across ten surface-distinct prompt templates
  (SmolLM2-135M/360M, Qwen2.5-0.5B), the pooled entropy–bias correlation remains
  negative, and instruct Δ > base Δ on average in each template.

Failure of either is reported as a failure.

## Reporting rules
- Report all five bias families and all families run, including failures.
- Report effect sizes and CIs as primary evidence; treat any single p-value as
  secondary and Holm-correct across probes.
- Any prediction that fails is reported as a failure, not omitted.
- Exploratory analyses (e.g. per-domain, per-recipe) are labeled exploratory.
