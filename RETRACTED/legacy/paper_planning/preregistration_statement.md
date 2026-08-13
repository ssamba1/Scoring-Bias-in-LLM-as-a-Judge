# Preregistration (Retrospective)

## Study Design
- **Design type:** Within-family comparison, base vs instruct
- **Primary outcome:** Mean absolute bias (Δ) per probe
- **Secondary outcomes:** Flip rate, Cohen's d, effect size CIs

## Research Questions (Pre-Specified)
- **RQ1:** Does instruction tuning change scoring bias magnitude?
- **RQ2:** Is the change direction consistent across bias types?
- **RQ3:** Is the change direction consistent across model families?
- **RQ4:** Do training methods (SFT/DPO/RLHF) modulate the effect?

## Hypotheses (Pre-Specified)
- **H1:** Instruction tuning reduces format-related biases (rubric order, score ID).
- **H2:** Instruction tuning affects content-related bias (reference answer) differently.
- **H3:** The effect is consistent across model families.
- **H4:** Training method moderates the effect.

## Analysis Plan
1. Paired t-test for each probe (base vs instruct)
2. Bonferroni correction for 3 probes
3. Effect sizes with bootstrapped CIs
4. Wilcoxon signed-rank as sensitivity
5. Leave-one-family-out sensitivity

## Deviations
- Reference answer effect fails Bonferroni  downgraded from "significant" to "marginal"
- Training method decomposition added post-hoc after observing Mistral outlier
- Depth findings (5 findings) added during analysis
