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

**P12 outcome (recorded 2026-07-19 after the retry run):** MET NOMINALLY,
ATTENUATED. Instruct mean Δ − base mean Δ = +0.055 (> 0; positive for 3/5
probes: rubric +0.13, score-ID +0.31, reference +0.04; authority −0.16,
verbosity −0.04). Far below the ≤8B panel mean (+0.26), consistent with the
>3B attenuation band; 4-bit quantization is an additional caveat. First run
failed on a CPU-dispatch error (base scored only) and was retried with fixed
device placement.
- **P13 (locus of responsiveness).** Overwriting the instruct model's residual
  stream at the nuisance-span positions with the base model's activations
  (Qwen2.5-1.5B; expert-authority and good-exemplar probes) reduces the
  instruct bias toward the base level by more than 50% in at least one layer
  band; i.e., the instruct encoding of the nuisance span causally carries the
  extra responsiveness.

Failure of any of P10–P13 is reported as a failure.

**P13 outcome (recorded 2026-07-19 after the run):** SPLIT.
- Authority framing: **confirmed** — overwriting the instruct model's residual
  stream at the nuisance-span positions with the base model's activations reduces
  the instruct-vs-base response gap by ≥50% across layers 3–14 (peak ≈100% at
  layers 6–11, Qwen2.5-1.5B, n=20). The differential response is causally carried
  by the span's encoding.
- Good-exemplar framing: **failed** — per-layer reductions ≈0 (max 7%); the
  exemplar's effect is not span-local at any single layer. Reported as a failure
  of that clause; the mechanism for exemplar responsiveness is distributed.

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

**P17 outcome (recorded 2026-07-19 after the run):** CONFIRMED, both clauses.
Bias grows monotonically with the rating scale's value range for both
checkpoints (base 0.083 → 0.212 → 0.516; instruct 0.193 → 0.323 → 0.664 across
1–3 / 1–5 / 0–9), with bias per unit range roughly constant — the Var_σ(v)
scaling the theory predicts. Instruct > base at every granularity.

**P14 outcome (recorded 2026-07-19 after the run):** FAILED, both clauses.
Mean dose-Spearman of |shift| vs dose is 0.06 (8/16 cells positive); instruct
slopes are not steeper (3/8 pairs, Wilcoxon p = 0.74). The observed pattern is a
step function: most of the score shift appears at the first dose unit and then
plateaus or wobbles. Responsiveness is triggered by the nuisance's *presence*,
not scaled by its magnitude, for these probes and models.

## Addendum 4 (registered 2026-07-19, before these CPU runs launched)

- **P16 (sampled readout).** Scoring by actually sampling written scores
  (temperature 1, k=8, parse-first-digit; `repro/sampled_harness.py`): (a) parse
  failure is much higher for base than instruct checkpoints (the confound,
  now quantified); (b) among parseable items, the sampled-score bias Δ
  correlates positively with the expected-value Δ across cells.
**P15 outcome (recorded 2026-07-19 after the run):** SPLIT.
- (a) **confirmed strongly**: pooled entropy–bias ρ = −0.51 (p < 10⁻⁶, n = 180)
  across ten surface-distinct templates — the broadest template-robustness
  evidence for the negative relation.
- (b) **failed as stated**: instruct Δ > base Δ in only 6/10 templates (range
  −0.25 to +0.18) on the three smallest families (135M–0.5B, 3 probes, 20
  items) — the direction is template-sensitive at this scale and n.

**P16 outcome (recorded 2026-07-19 after the run):** FAILED, both clauses —
and the failure *corrects our own earlier framing*. (a) Under a lenient
sampled protocol (temperature 1, k=8, first-digit regex) parse rates are
nearly equal (base 0.80, instruct 0.83): the zero-parse result of Appendix A
was a property of the strict deterministic protocol, not of base models'
inability to emit digits. The confound claim is accordingly re-scoped to
"protocol-dependent." (b) Sampled-score bias estimates do not recover the
expected-value ordering (ρ = −0.20, p = 0.53, n = 12): at practical sample
counts the sampled estimator is dominated by its own sampling variance. Net:
parse-based scoring is either confounded (strict) or noise-dominated
(lenient); the paper's text is updated to say exactly this.

- **P17 (scale granularity).** With rating scales of 3, 5, and 10 points
  (`repro/granularity_harness.py`), measured bias grows with the value range
  of the scale (as Var_σ(v) scaling predicts), and instruct Δ > base Δ at
  every granularity.

Failure of any clause is reported as a failure.

- **P18 amendment (v2, recorded 2026-07-19 before the v2 run):** the v1
  space-prefixed readout was degenerate — " 4" tokenizes as [space][4] on all
  four tokenizers, so the "spaced" ids collapsed to the shared space token and
  v1 produced no valid comparison (bug caught in analysis; v1 result discarded
  as invalid, not as unfavorable). v2 replaces it with a vocab-scan union:
  every single token that decodes to each digit. Prediction unchanged: bare and
  union per-cell Δ correlate ≥ 0.7 and the instruct>base effect holds under the
  union readout.
- **P18 (readout-variant robustness).** The recorded answer-token mass turns out
  to be over *bare* digit tokens while models place their mass on space-prefixed
  variants — a tokenization artifact discovered 2026-07-19. Prediction, registered
  before `repro/tokvar_harness.py` completes: bias Δ computed from the bare,
  space-prefixed, and union readouts agree (pairwise correlation of per-cell Δ
  ≥ 0.7), and the instruct>base effect holds under the union readout (which
  captures the dominant mass), so the expected-value findings are not an artifact
  of the bare-token conditional.

- **P19 (chat-template confound).** Instruct checkpoints are scored in raw
  completion format throughout; they are trained on chat templates, so the bias
  increase could in principle be an out-of-distribution-format artifact.
  Prediction, registered before `repro/chattemplate_harness.py` runs: (a) bias
  Δ under the model's own chat template remains clearly positive; (b) per-cell
  Δ correlates between raw and chat formats; (c) the instruct-vs-base effect
  (instruct-chat Δ minus base-raw Δ) remains positive on average.

**P19 outcome (recorded 2026-07-19 after the run):** SPLIT.
- (a) **confirmed**: bias under the model's own chat template is substantial in
  every cell (mean Δ 0.38; all cells > 0.1; chat ≥ raw in 4/6 cells, e.g.
  Qwen-0.5B rubric 0.035 raw → 0.477 chat). The increase is not an
  out-of-distribution-format artifact.
- (b) **inconclusive**: raw~chat per-cell correlation ρ = 0.49, p = 0.33 at
  n = 6 — directionally positive, underpowered.
- (c) **weakly met**: instruct-chat minus base-raw = +0.07 on average, but
  positive in only 1/3 families (driven by Qwen-0.5B).

## Reporting rules
- Report all five bias families and all families run, including failures.
- Report effect sizes and CIs as primary evidence; treat any single p-value as
  secondary and Holm-correct across probes.
- Any prediction that fails is reported as a failure, not omitted.
- Exploratory analyses (e.g. per-domain, per-recipe) are labeled exploratory.
