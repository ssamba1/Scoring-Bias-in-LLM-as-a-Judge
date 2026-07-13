# The True Ceiling: What's Actually Missing

## 6 dimensions that top research labs explore — none of which we've touched

---

### Dimension 1: Causal / Mechanistic Analysis

**What top labs do:** They don't just measure a phenomenon — they explain WHY it happens at the mechanism level. Attention patterns, hidden state comparisons, circuit analysis.

**What we have:** The IIAR hypothesis (verbal explanation)
**What's missing:** Empirical evidence that attention redistribution actually occurs

**Buildable now:** 
- Embedding similarity analysis (compare hidden states across biased vs unbiased prompts)
- Attention head attribution (which heads change most between base and instruct)
- Prompt sensitivity heatmaps (which tokens drive the score change most)

### Dimension 2: Bias Mitigation

**What top labs do:** After finding a problem, they propose and test solutions.

**What we have:** "Format and content channels need separate mitigation" (conceptual)
**What's missing:** Actual mitigation methods with measured effectiveness

**Buildable now:**
- Code for 5 mitigation methods (calibration, ensembling, prompting, few-shot, adversarial)
- Evaluation framework to compare mitigation effectiveness

### Dimension 3: Bias Interaction Effects

**What top labs do:** Test how phenomena interact. Is the whole greater than the sum of parts?

**What we have:** 3 independent probe measurements
**What's missing:** What happens when you combine probes? (e.g., rubric order + reference answer simultaneously)

**Buildable now:**
- 2-way probe combination code (3 choose 2 = 3 combinations)
- 3-way probe combination code (all three together)
- Interaction effect analysis framework

### Dimension 4: Judge Consistency

**What top labs do:** Measure how reliable their measurements are. Test-retest reliability, split-half reliability.

**What we have:** 3 repeats at temperature 0 (deterministic)
**What's missing:** Consistency at temperature > 0, test-retest on different days, split-half reliability

**Buildable now:**
- Consistency analysis framework (ICC, Cohen's κ, test-retest)
- Confidence analysis (does the model's output probability correlate with bias?)

### Dimension 5: Bias Detection

**What top labs do:** Build tools that use their findings. The paper becomes a framework, not just a result.

**What we have:** A paper
**What's missing:** A tool that detects bias in any model, usable by anyone

**Buildable now:**
- Bias detection API (submit any HuggingFace model, get a bias report)
- Bias report card generator (PDF output)

### Dimension 6: Longitudinal Analysis

**What top labs do:** Show how phenomena change over time. Training dynamics, model evolution.

**What we have:** Snapshot at one point in training
**What's missing:** When during training does the differential effect emerge?

**Needs data:** Requires intermediate checkpoints (not available for most models)

---

## Building the 5 Buildable Dimensions NOW
