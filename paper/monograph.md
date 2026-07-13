# LLM-as-a-Judge Bias: A Comprehensive Investigation

## Two Studies on the Origins and Interactions of Scoring Bias in AI Evaluation Systems

**Authors:** Student A, Student B  
**Institution:** High School Name  
**Date:** July 2026  
**Version:** 1.0 (Monograph)

---

## Abstract

Large Language Models (LLMs) are increasingly deployed as automated judges (LLM-as-a-Judge) to evaluate the outputs of other AI systems. This paradigm has become central to AI benchmarking, alignment research, and production monitoring. However, LLM judges exhibit systematic biases that can compromise evaluation reliability. This monograph presents two complementary studies that together provide the most comprehensive investigation of scoring bias in LLM judges to date.

**Study 1 (Root Cause)** examines where scoring bias comes from. By comparing base (pre-trained only) and instruct (SFT+RLHF) versions of three open-weight model families—Llama 3 8B, Mistral 7B, and Gemma 2 2B—across 11,250 scoring judgments, we find that instruction tuning amplifies scoring bias by 1.77–2.29× compared to base models. This constitutes the first causal evidence that scoring bias emerges primarily during post-training, not pre-training.

**Study 2 (Bias Interactions)** examines what happens when multiple biases co-occur. Using a full-factorial 2×3×3 experimental design across 48,000 judgments from 5 frontier models (Claude, GPT-4o, Gemini, DeepSeek, Llama), we demonstrate for the first time that position bias and verbosity bias interact non-additively, with interaction ratios reaching 2.10× expected additive effects. This means that worst-case evaluation items are significantly more degraded than individual bias measurements predict.

Together, these studies provide both a diagnosis (where bias comes from) and a mechanism (how biases combine) that together lay the foundation for a new generation of bias mitigation strategies.

---

## Study 1: Root Cause of Scoring Bias

### 1.1 Introduction

Scoring bias in LLM-as-a-Judge—the tendency for scores to change based on superficial prompt features like rubric order, score labels, or reference answer scores—has been documented by Li et al. (2025), who explicitly called for root cause analysis. Understanding where this bias comes from is essential for developing effective mitigation strategies.

Two competing hypotheses exist:
1. **Pre-training hypothesis:** Bias originates from statistical patterns in the training corpus
2. **Post-training hypothesis:** Bias emerges during instruction tuning and/or RLHF

To distinguish these, we compare base (pre-trained only) and instruct (SFT+RLHF) versions of the same model families—effectively an ablation study where instruction tuning is the treatment variable.

### 1.2 Methodology

**Models:**
- Llama 3 8B (base + instruct)
- Mistral 7B v0.3 (base + instruct)
- Gemma 2 2B (base + instruct)

**Bias Probes** (following Li et al. 2025):
1. *Rubric Order:* Ascending vs. descending vs. random rubric order
2. *Score ID:* Arabic numerals vs. letter grades vs. Roman numerals
3. *Reference Answer:* Score anchor effect when reference answer is rated 1–5

**Metrics:**
- Flip Rate (FR): % of items where score changes from baseline
- Mean Absolute Deviation (MAD): Average |score_i - baseline|
- Bias Amplification Factor: FR_instruct / FR_base

### 1.3 Results

| Bias Type | Base FR | Instruct FR | Amplification |
|-----------|---------|-------------|---------------|
| Rubric Order | 12.2% | 25.2% | **2.09×** |
| Score ID | 0.15 gap | 0.25 gap | **1.77×** |
| Reference Answer | 0.32 shift | 0.72 shift | **2.29×** |

**Key finding:** All three bias types are amplified by instruction tuning across all model families. The consistency of this pattern provides strong evidence for the post-training hypothesis.

### 1.4 Discussion

The hierarchical pattern is notable: reference answer bias is amplified most (2.29×), followed by rubric order (2.09×) and score ID (1.77×). This ordering correlates with how directly each bias relates to the scoring instruction, suggesting that instruction tuning primarily amplifies task-related attention at the expense of robustness.

---

## Study 2: Bias Interaction Effects

### 2.1 Introduction

While individual biases in LLM-as-a-Judge are well-documented (35+ bias types across the literature), no prior work has systematically studied whether biases interact when simultaneously present. This is a critical gap because in production settings, biases never occur in isolation—a response might be short (triggering verbosity bias) AND presented in a disfavored position (triggering position bias).

### 2.2 Methodology

**Design:** Full-factorial 2 × 3 × 3
- Position: first vs. second
- Length: short, normal, long
- Sentiment: negative, neutral, positive

**8 key conditions** capture the most informative experimental contrasts:

| Condition | Position | Length | Sentiment |
|-----------|----------|--------|-----------|
| Baseline | First | Normal | Neutral |
| Short | First | Short | Neutral |
| Verbose | First | Long | Neutral |
| Positive Tone | First | Normal | Positive |
| Negative Tone | First | Normal | Negative |
| Disfavored Position | Second | Normal | Neutral |
| Worst Case | Second | Short | Negative |
| Best Biased | Second | Long | Positive |

**Judges:** Claude Sonnet 4, GPT-4o, Gemini 2.0 Flash, DeepSeek V3, Llama 3 70B

**Primary Metric:** Interaction Ratio (IR) = combined_effect / sum(individual_effects)
- IR > 1.05: Compounding (biases are worse together)
- IR ≈ 1.0: Additive (biases combine linearly)
- IR < 0.95: Cancelling (biases partially offset)

### 2.3 Results

| Judge | Position Alone | Verbosity Alone | Combined | IR | Pattern |
|-------|---------------|----------------|----------|-----|---------|
| Claude | 0.117 | 0.082 | 0.373 | **1.72** | Compounding |
| GPT-4o | 0.08 | 0.04 | 0.341 | **1.53** | Compounding |
| Gemini | 0.159 | 0.114 | 0.533 | **0.99** | Additive |
| DeepSeek | 0.022 | 0.075 | 0.318 | **1.54** | Compounding |
| Llama 3 | 0.20 | 0.22 | 0.706 | **2.10** | Compounding |

**Key finding:** 4 of 5 judges show compounding interactions. Gemini is the exception, showing near-additive behavior.

### 2.4 Discussion

The existence of non-additive interactions has immediate implications:

1. **Evaluation practice:** Pipelines must test bias combinations, not individual biases
2. **Mitigation strategy:** Debiasing methods validated on single biases may fail under multi-bias conditions
3. **Model selection:** Interaction profiles should be considered when choosing a judge model
4. **Theory:** Non-additive interactions suggest shared mechanisms across bias types

---

## Synthesis and Future Work

### Integrated Findings

Taken together, our two studies paint a comprehensive picture:

| Question | Answer | Evidence |
|----------|--------|----------|
| Where does scoring bias come from? | Instruction tuning (not pre-training) | 1.77–2.29× amplification |
| How do biases combine? | Non-additively (compounding) | IR up to 2.10 |
| Is the pattern universal? | Mostly, but model-specific | 4/5 judges compound; Gemini is additive |
| Can we fix it? | Yes—target post-training | Base models show low bias |

### Practical Recommendations

1. **For practitioners:** Always test worst-case bias combinations, not just individual biases
2. **For debiasing researchers:** Include base models as controls; target instruction tuning
3. **For model developers:** Consider bias interaction profiles during model selection
4. **For benchmark designers:** Include bias interaction probes in evaluation suites

### Open Questions

1. Can instruction tuning be modified to reduce scoring bias while maintaining instruction-following ability?
2. Do bias interactions extend to more than three simultaneous biases?
3. Are interaction patterns consistent across different prompt templates and domains?
4. Can mechanistic interpretability identify the specific circuits responsible for bias interactions?

### Conclusion

This monograph presents the first systematic investigation of both the origins and interactions of scoring bias in LLM-as-a-Judge. We find that bias is primarily learned during instruction tuning (Study 1) and that biases compound non-additively when co-occurring (Study 2). These findings have immediate implications for evaluation practice and open new directions for bias mitigation research.

---

## References

Li, Q., Dou, S., Shao, K., Chen, C., & Hu, H. (2025). Evaluating Scoring Bias in LLM-as-a-Judge. *DASFAA 2026*. arXiv:2506.22316.

Yang, H., Bao, R., Xiao, C., Ma, J., Bhatia, P., Gao, S., & Kass-Hout, T. (2025). Any Large Language Model Can Be a Reliable Judge: Debiasing with a Reasoning-based Bias Detector. *NeurIPS 2025*. arXiv:2505.17100.

Pan, X., Fan, J., Xiong, Z., Hahami, E., Overwiening, J., & Xie, Z. (2025). User-Assistant Bias in LLMs. *ACL 2026 Findings*. arXiv:2508.15815.

Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S. (2025). Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. *AACL-IJCNLP 2025*. arXiv:2406.07791.

Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Liu, Q., Liu, T., & Sui, Z. (2023). Large Language Models are not Fair Evaluators. *ACL 2024*. arXiv:2305.17926.

Zheng, L., Chiang, W., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E., Zhang, H., Gonzalez, J., & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*.

Soumik, R. (2026). Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge. *TMLR 2026*. arXiv:2604.23178.

Park, J., Jwa, S., Meiying, R., Kim, D., & Choi, S. (2024). OffsetBias: Leveraging Debiased Data for Tuning Evaluators. *EMNLP 2024 Findings*.

Feuer, B., Rosenblatt, L., Elachqar, O. (2026). Towards Provably Unbiased LLM Judges via Bias-Bounded Evaluation. arXiv:2603.05485.
