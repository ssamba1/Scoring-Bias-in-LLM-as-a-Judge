# Anticipated objections and where the paper answers them

Prepared for submission/defense. Each objection maps to evidence already in the paper.

**"Expected-value scoring is not novel — G-Eval did it in 2023."**
Agreed and stated (§3.2, Related Work). The readout is attributed to Liu et al. 2023,
Wang et al. 2025, TrustJudge. Our claims attach to (i) the parse-failure *confound*
documentation and (ii) using the distribution as the measured object of the theory.

**"The theory is elementary."**
It is (softmax Jacobian + Cauchy–Schwarz + CGF tilt), and the paper never claims
otherwise. Its value is the *decomposition framing* and that both terms are measured
independently and confirmed at their predicted levels (§5.3–5.4). The per-cell test
(74% sign accuracy) makes it predictive, not decorative.

**"The entropy–bias correlation is a capability/size confound."**
Partial correlation given log-size: −0.38 (p<10⁻⁴), and size correlates *positively*
with bias — the opposite direction the confound requires (§5.3). Also holds within
base-only and within instruct-only judges.

**"Pooled correlations double-count checkpoints."**
Every pooled correlation has a cluster-respecting counterpart: family-random-intercept
regression (−0.46, p<10⁻⁵), within-checkpoint analyses, family-clustered bootstrap,
exact sign-flip permutation over all 2¹³ patterns (p=0.00098) (§3.3, §5.2).

**"No probe is individually significant."**
Correct, and §5.1 says so: the registered per-probe test — paired Wilcoxon,
Holm-corrected across the five probes — is null for *every* probe, the smallest
being p_Holm=0.13 (score ID and authority). Three of the five bootstrap CIs
exclude zero and are seed-stable, which is weaker evidence than significance and
is not offered as a substitute. With n=13 paired families per probe that test
has little power. The aggregate rests on the pooled per-item model
(instruct coefficient +0.16; p=4×10⁻⁶ from a family-clustered OLS, not from the
mixed-effects fit, whose family variance component is exactly zero and whose
standard errors are not all finite — the coefficient is identical under both),
the exact sign-flip permutation test, and
the twelve-specification sweep — not on any single probe.

**"The predictor R²=0.27 won't replicate."**
The paper itself downgrades it: the clustered bootstrap CI on R² spans zero and the
claim is scoped to the rank signal (ρ=0.58) with the inverted sign (§5.12). The
practical recommendation is a red flag, not a measurement.

**"Discrete-score users won't see this."**
Correct, and reported as a limitation: argmax quantization hides the increase except
for content probes; it simultaneously inflates the *level* of bias (§7, Limitations). The claim
attaches to the continuous readout the paper recommends.

**"Items are author-written."**
Replicated on public Dolly-15k items: 7/8 families, ρ=−0.44 (§5.17). Item-level
analysis also shows items carry no stable bias signal at all (mean cross-judge
item-profile ρ=0.01).

**"One prompt template."**
Three templates in the main battery (§5.15), ten more on small models preregistered
as P15, all English templates disclosed in the appendix; Chinese replication
preregistered as P11.

**"'Instruction tuning' is a black box — which stage?"**
The preregistered stage ablation answers this: SFT installs the responsiveness
(87–94% of the rise, 10/10 cells), preference tuning installs the confidence (§5.16).
Predictions are timestamped in git before the data existed.

**"Correlational mechanism."**
Two interventions: activation patching (layer-localized transfer, §5.5) and the
alignment-stage ablation; a third (nuisance-span patching, P13) is preregistered.
The attention account is an honest *null* (§5.6), explicitly contrasted with the
fabricated mechanism of the retracted prior version.

**"Xu et al. (2026) already give a mechanism for judge bias."**
They give a different one, and the two do not overlap. They intervene *within* a
fixed judge, steering hidden states along a bias subspace to show it is causally
load-bearing. We patch *between* a base and an instruct checkpoint of the same
model (§5.5, §5.7), which is the only way to attribute a change to what tuning
did — their design has no base checkpoint to compare against. Neither subsumes
the other, and the obvious joint question, whether their subspace and our
responsiveness term are the same object seen two ways, is one neither paper can
answer alone. The positioning table credits them the mechanism and causal
columns rather than claiming those cells.

**"Zahraei et al. (2026) already ran the stage ablation."**
On the same Tülu-3 ladder, for a different bias family, and they report the
curve rather than decomposing it — their design measures no responsiveness term.
What ours adds is both terms measured at each checkpoint. The Discussion (§6)
shows their curve turns at both transitions where our two terms say a curve
should turn, and says plainly that this is a retrodiction, not a forecast, and
not an attribution to either term: at DPO responsiveness and bias both rise 11%,
so responsiveness alone accounts for the movement.

**"Anchoring is null here, but Kapetanovic et al. (2026) measure a large
anchoring effect."**
Different manipulations. Ours is a population base rate ("most responses of this
kind receive a score of 5"); theirs is a prior score attached to the very text
being judged, carried as revision metadata. §5.9 already argues that tuning
inflates responsiveness to social and content framing rather than to every
injected signal, and a verdict attributed to an earlier evaluator is social
framing where a base rate is not. We state that as the reconciliation we believe
correct, not one we have tested — running both anchor variants on this panel is
the direct test and needs no new models. Note also that their token-level probe
independently reproduces the shape our preregistered dose–response prediction
failed into (§5.10): the anchor acts on presence, not magnitude.

**"No frontier models."**
Now tested (preregistered P20, §5.22): GPT-4o-mini, GPT-4o, and Llama-3.1-70B
via API logprobs are biased on 5/5 probes each — the largest biases in the study
(rubric-order Δ up to 2.02) — and pooling them *strengthens* the confidence–bias
law to ρ=−0.45 (n=145). Two clauses failed and are reported: deployed judges are
*more* biased than small open models, and the within-trio direction at n=3 is
positive. The honest residual: no causal base-vs-instruct contrast is possible at
the frontier in principle (no public base checkpoints), and Claude/Gemini expose
no logprobs.

**"n=13 families is small."**
The inferential unit is honest (families, not items), effects are reported with
exact tests and CIs, the estimator's split-half reliability is 0.99, and the
sensitivity analysis shows no single family or vendor drives the result. Power is
disclosed as sized for large effects.

**"Why should we trust this project given the fabrication?"**
The fabrication is self-reported, audited (`DATA_INTEGRITY_AUDIT.md`), quarantined,
and the honest version is CI-enforced: a GitHub Action rerun of every analyzer must
reproduce every committed number byte-for-byte. Twenty predictions were preregistered
with git timestamps before their data existed, and each is reported with its clauses,
including the ones that failed. This paper is *more*
auditable than the field's norm, precisely because of its history.

**"Does bias scale with how strong the nuisance is?"**
No — and we preregistered the opposite and report the failure (§5.10, dose–response):
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
