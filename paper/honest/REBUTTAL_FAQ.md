# Anticipated objections and where the paper answers them

Prepared for submission/defense. Each objection maps to evidence already in the paper.

**"Expected-value scoring is not novel — G-Eval did it in 2023."**
Agreed and stated (§3.2, Related Work). The readout is attributed to Liu et al. 2023,
Wang et al. 2025, TrustJudge. Our claims attach to (i) the parse-failure *confound*
documentation and (ii) using the distribution as the measured object of the theory.

**"The theory is elementary."**
It is (softmax Jacobian + Cauchy–Schwarz + CGF tilt), and the paper never claims
otherwise. Its value is the *decomposition framing* and that both terms are measured
independently and confirmed at their predicted levels (§5.2–5.4). The per-cell test
(75% sign accuracy) makes it predictive, not decorative.

**"The entropy–bias correlation is a capability/size confound."**
Partial correlation given log-size: −0.38 (p<10⁻⁴), and size correlates *positively*
with bias — the opposite direction the confound requires (§5.3). Also holds within
base-only and within instruct-only judges.

**"Pooled correlations double-count checkpoints."**
Every pooled correlation has a cluster-respecting counterpart: family-random-intercept
regression (−0.46, p<10⁻⁵), within-checkpoint analyses, family-clustered bootstrap,
exact sign-flip permutation over all 2¹³ patterns (p=0.00098) (§3.3, §5.2).

**"Only 3/5 probes individually significant."**
Stated verbatim in §5.1; the aggregate rests on the pooled mixed-effects model,
the exact permutation test, and the 12-specification sweep, not on any single probe.

**"The predictor R²=0.27 won't replicate."**
The paper itself downgrades it: the clustered bootstrap CI on R² spans zero and the
claim is scoped to the rank signal (ρ=0.58) with the inverted sign (§5.6). The
practical recommendation is a red flag, not a measurement.

**"Discrete-score users won't see this."**
Correct, and reported as a limitation: argmax quantization hides the increase except
for content probes; it simultaneously inflates the *level* of bias (§5.2). The claim
attaches to the continuous readout the paper recommends.

**"Items are author-written."**
Replicated on public Dolly-15k items: 7/8 families, ρ=−0.44 (§5.10). Item-level
analysis also shows items carry no stable bias signal at all (mean cross-judge
item-profile ρ=0.01).

**"One prompt template."**
Three templates in the main battery (§5.9), ten more on small models preregistered
as P15, all English templates disclosed in the appendix; Chinese replication
preregistered as P11.

**"'Instruction tuning' is a black box — which stage?"**
The preregistered stage ablation answers this: SFT installs the responsiveness
(84–99% of the rise, 10/10 cells), preference tuning installs the confidence (§5.8).
Predictions are timestamped in git before the data existed.

**"Correlational mechanism."**
Two interventions: activation patching (layer-localized transfer, §5.4) and the
alignment-stage ablation; a third (nuisance-span patching, P13) is preregistered.
The attention account is an honest *null* (§5.5), explicitly contrasted with the
fabricated mechanism of the retracted prior version.

**"No frontier models."**
True and stated first in Limitations. Requires paid API access; the harness
(`closed_harness.py`) is committed and ready. The studied regime (0.1–14B open
weights) is the regime where base/instruct pairs exist, which the causal comparison
requires — frontier judges have no public base checkpoint, so the *within-family
causal contrast* is impossible there in principle; only the correlational
entropy–bias screen can be tested on frontier models.

**"n=13 families is small."**
The inferential unit is honest (families, not items), effects are reported with
exact tests and CIs, the estimator's split-half reliability is 0.99, and the
sensitivity analysis shows no single family or vendor drives the result. Power is
disclosed as sized for large effects.

**"Why should we trust this project given the fabrication?"**
The fabrication is self-reported, audited (`DATA_INTEGRITY_AUDIT.md`), quarantined,
and the honest version is CI-enforced: a GitHub Action rerun of every analyzer must
reproduce every committed number byte-for-byte. Ten of the sixteen predictions were
preregistered with git timestamps before their data existed. This paper is *more*
auditable than the field's norm, precisely because of its history.

**"Does bias scale with how strong the nuisance is?"**
No — and we preregistered the opposite and report the failure (§5, dose–response):
the shift is a step function of the nuisance's presence. This constrains mechanism
stories: the nuisance is a categorical feature, consistent with the span-encoding
result.

**"Instruct models are out-of-distribution in your raw completion format."**
Preregistered P19 tests exactly this: instruct checkpoints scored under their own
chat template vs raw format, with base-raw as the effect baseline.

**"The renormalized readout ignores most of the digit probability mass."**
Closed by preregistered P18 (confirmed): a vocab scan shows the bare digits are the
*complete* digit-token set at the score position (no space-digit tokens exist); the
mass (0.91–0.96) sits one position later, and scoring at that high-mass position
agrees with the bare readout per cell (ρ=0.79 ≥ the preregistered 0.7 bar), with
the effect 4/4 families under the union. Honest residual: at the high-mass
position the effect is +0.06 but 2/4 of the smallest families. (The v1 variant was
degenerate — a tokenization bug we caught via an impossible mass value and
disclosed as invalid, not unfavorable.)

**"Does the increase survive at larger scale?"**
Partially: 14B (4-bit) is nominally positive (+0.06) but strongly attenuated vs the
≤8B panel (+0.26), consistent with the >3B flattening of the entropy–bias relation.
The paper scopes the headline to the studied regime and says the attenuation out
loud.

**"Is the entropy–bias relation universal?"**
No, and the paper scopes it three ways: absent within checkpoints, absent across
the 11 stage-ladder checkpoints, flat in the >3B band. It is a between-family
regularity of the full panel — stated, not hidden.
