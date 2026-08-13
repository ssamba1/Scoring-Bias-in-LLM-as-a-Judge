# Preregistration Draft  OSF-Style

## Study 1: Root Cause of Scoring Bias

---

### 1. Title
Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge

### 2. Authors
Author Name, Author Name

### 3. Research Question
Does scoring bias in LLM-as-a-Judge originate from pre-training (present in base models) or emerge during instruction tuning (only present in instruct models)?

### 4. Hypothesis
We hypothesize that instruction tuning changes scoring behavior across all three bias probes (rubric order, score ID, reference answer). If bias increases after instruction tuning, it emerges from the alignment process. If bias decreases, it originates from the base pre-training. Null hypothesis: base and instruct models show no systematic difference in scoring bias.

Prediction: Given prior work by Pan et al. (ACL 2026) showing instruction tuning amplifies user bias, we predict instruction tuning will amplify all scoring biases (uniform increase).

### 5. Design
Controlled experiment: 3 (bias probes) × 3 (variants per probe) × 44 (model families) × 2 (base + instruct) × 50 (items) × 3 (repeats) = 118,800 total observations.

Independent variables: Model training type (base vs instruct, within-family), bias probe type (rubric order, score ID, reference answer), variant (control vs biased).
Dependent variable: Score (1-5 scale).

### 6. Sample
44 model families with publicly available base and instruct variants on HuggingFace. All families tested on T4 GPU (16GB). Exclusion criteria: any model that fails to load or produces invalid outputs (score outside 1-5).

### 7. Materials
50 instruction-response pairs across 5 domains (science, tech, humanities, daily life, math). Three bias probes with three variants each, adapted from Li et al. (DASFAA 2026).

### 8. Procedure
1. Load base model variant
2. For each of 50 items × 3 probes × 3 variants × 3 repeats: generate score at temperature 0
3. Save results, unload model, clear GPU memory
4. Load instruct model variant
5. Repeat steps 2-3
6. Move to next family
7. Compute Δ, flip rate, Cohen's d, Spearman's ρ

### 9. Analysis Plan
Primary analysis: Paired t-test (base vs instruct) across families, per probe.
Secondary: Effect sizes (Cohen's d), flip rates, MAD, Spearman's ρ.
Mixed-effects model: score ~ training_type + probe + (1|family).
Power analysis: N=44 provides >99% power for rubric order, >95% for reference answer, >80% for score ID.

### 10. Deviations
If the data contradicts the prediction (uniform increase), we will report the pattern honestly and explore post-hoc explanations.
