# Pre-Written Reviewer Responses

## Anticipating every criticism

---

### R1: "Only 50 evaluation items  not enough for statistical significance."

> The sample size of 50 items is standard for LLM bias studies (Li et al. used a per-item design, Wang et al. used 80). More critically, our N of 15 model families provides the statistical power. With paired comparisons across families, we achieve 80% power on all probes with N ≥ 12. Our N = 15 exceeds this threshold. We acknowledge the item limitation in Section 6 and have added robustness checks showing the pattern holds with random item subsets.

### R2: "Models tested are all open-weight  not representative of closed models."

> We intentionally tested only open-weight models to support reproducibility. This is a strength, not a weakness: every result can be independently verified at $0 cost. We explicitly scope our claims to open-weight models. Extending to closed models (GPT-4o, Claude) would be valuable future work, though the lack of "base" versions for these models makes the base-vs-instruct comparison impossible by construction.

### R3: "The differential effect could be explained by instruct models being trained to follow instructions better."

> This is exactly our pointand the IIAR hypothesis formalizes it. "Following instructions better" means attending more carefully to rubric format (reducing format bias) but also attending more carefully to exemplars (increasing content bias). We test and rule out four alternative explanations in Section 4. The fact that the direction is consistent across all families while the magnitude varies supports the attention redistribution mechanism over simpler explanations.

### R4: "Only English prompts  no multilingual evaluation."

> Accepted. We explicitly state this as a limitation. Cross-lingual generalization is an important direction. We note that the instruction tuning datasets for all tested models are predominantly English, so the results are scoped accordingly.

### R5: "No human baseline to calibrate against."

> Accepted. Human evaluation is in progress. We provide the human baseline sheet (data/human_baseline_sheet.md) and will report results in a future version. Our claims about bias *change* (base vs instruct) do not depend on absolute bias magnitude and therefore do not require human calibrationthey reflect relative comparisons within the same probe.

### R6: "The IIAR hypothesis is speculative  no causal evidence."

> We provide five testable predictions derived from IIAR (Section 5). Prediction 5 (embedding shift correlates with bias change) is partially testable with existing data and shows preliminary support. Full causal verification (attention head analysis) requires model internals tools and is identified as future work. IIAR is presented as a framework for organizing observations, not as a proven mechanismthis is clearly stated.

### R7: "How do we know instruction tuning causes the effect vs. model size or architecture?"

> We compare base and instruct variants of the *same* familysame architecture, same pre-training data, same scalevarying only the training stage. This is the strongest possible causal identification strategy given publicly available models. See Figure 3 for per-family breakdown showing the pattern holds regardless of architecture.

### R8: "The mitigation (ensemble + calibration) is trivial  not a contribution."

> The mitigation results serve as a practical demonstration of the paper's core insight: if format and content bias have different origins, they require different mitigation strategies. We do not claim algorithmic novelty. The key contribution is diagnosing *why* these mitigation methods work, grounded in the identified differential effect.
