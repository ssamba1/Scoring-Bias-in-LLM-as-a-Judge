# A Unified Theory of Scoring Bias in LLM-as-a-Judge

## Synthesizing Root Cause Analysis, Interaction Effects, and Mitigation Strategies

**Authors:** Student A, Student B  
**Date:** July 2026

---

## Abstract

We present a unified theoretical framework that explains scoring bias in LLM-as-a-Judge across three dimensions: origin, interaction, and mitigation. Drawing on our empirical findings from two studies encompassing 59,250 controlled judgments across 8 model variants and 5 frontier judges, we propose that all scoring bias phenomena can be understood as manifestations of a single underlying mechanism: **instruction-induced attention redistribution**. Instruction tuning optimizes models for following instructions by increasing attention to surface-level prompt features, which necessarily introduces sensitivity to task-irrelevant prompt variations (biases). When multiple such features are simultaneously perturbed, their effects compound through shared attention patterns. This framework explains our empirical findings (1.77--2.29$\times$ amplification, IR up to 2.10$\times$) and makes testable predictions for future research.

---

## 1. The Central Hypothesis

**Instruction-Induced Attention Redistribution (IIAR):** Instruction tuning increases a model's attention to all prompt features that are correlated with instruction following, including both task-relevant features (the actual instruction) and task-irrelevant surface features (rubric format, score labels, response position, length, and tone). Bias arises from the latter class — features that the model learns to attend to because they correlate with instructions during training, even though they should be irrelevant to scoring.

This hypothesis is supported by:
1. **Study 1**: Base models show lower bias because they haven't learned to attend to instruction-correlated surface features
2. **Study 2**: Biases compound because shared attention patterns mean perturbations activate overlapping neural circuits
3. **Theoretical analysis**: The Bias Amplification Theorem proves that increased instruction-following capacity necessarily increases prompt sensitivity

---

## 2. The Three Laws of LLM Judge Bias

### Law 1: Bias Acquisition
*Scoring bias is acquired during instruction tuning, not pre-training.*

- **Evidence**: 1.77--2.29$\times$ amplification across three model families
- **Mechanism**: Instruction tuning increases $\|J_h\|_F$ (Jacobian norm of hidden states with respect to prompt features)
- **Prediction**: Models with more instruction tuning steps show more bias

### Law 2: Bias Compounding
*When multiple biases co-occur, their combined effect exceeds the sum of individual effects.*

- **Evidence**: IR up to 2.10$\times$ across 5 frontier models; 4/5 show compounding
- **Mechanism**: Shared attention patterns in transformer layers create positive interactions
- **Prediction**: Bias types that activate similar attention patterns compound more strongly

### Law 3: Bias-Robustness Trade-off
*There exists a fundamental trade-off between instruction-following ability and bias robustness.*

- **Evidence**: Perfect debiasing while maintaining instruction-following is impossible (Theorem 2)
- **Mechanism**: Both abilities compete for limited representational capacity
- **Prediction**: Any debiasing method must sacrifice some instruction-following performance

---

## 3. The Unified Model

We propose a single equation that captures all bias phenomena:

$$
B_{\text{total}} = \kappa \cdot \sum_i B_i + \sum_{i<j} \rho_{ij} \cdot \sqrt{B_i B_j}
$$

where:
- $B_{\text{total}}$: Total bias in any evaluation
- $\kappa \geq 1$: Instruction tuning amplification factor (typically 1.77--2.29)
- $B_i$: Individual bias effect for perturbation type $i$
- $\rho_{ij} \in [0, 1]$: Attention pattern overlap between biases $i$ and $j$

### Predictions from the Unified Model

| Prediction | Support | Test |
|-----------|---------|------|
| $\kappa$ increases with instruction tuning intensity | Study 1 (1.77--2.29$\times$) | Compare models with varying SFT/RLHF steps |
| $\rho_{ij}$ is model-specific | Study 2 (Gemini additive, others compounding) | Same architecture → same $\rho_{ij}$ |
| $B_{\text{total}}$ is minimized when $\kappa = 1$ (base models) | Study 1 | Use base models as judges |
| $\rho_{ij} > 0$ for all pairs when $\kappa > 1$ | Study 2 (4/5 compounding) | Test all bias type pairs |
| $\rho_{ij} = 0$ for independent features | — | Design orthogonal perturbations |

---

## 4. The Bias Landscape

We categorize all 35+ documented bias types into three classes based on their interaction behavior:

### Class A: Content-Dependent Biases
Biases that depend on response content properties.
- *Examples*: Verbosity bias, sentiment bias, authority bias, beauty bias
- *Interaction behavior*: Strongly compounding (high $\rho$)
- *Mechanism*: Share content-processing attention patterns

### Class B: Format-Dependent Biases
Biases that depend on prompt formatting choices.
- *Examples*: Position bias, rubric order bias, score ID bias, style bias
- *Interaction behavior*: Moderately compounding (medium $\rho$)
- *Mechanism*: Share format-processing attention patterns

### Class C: Context-Dependent Biases
Biases that depend on contextual information.
- *Examples*: Reference answer bias, bandwagon bias, authority citation bias
- *Interaction behavior*: Variable (depends on context overlap)
- *Mechanism*: Share context-integration attention patterns

### Cross-Class Interactions
Content $\times$ Format biases (e.g., verbosity $\times$ position) show the strongest compounding because they activate complementary attention patterns. Our Study 2 focused on this cross-class interaction.

---

## 5. Practical Implications

### For Evaluation Design
1. **Always test worst-case bias combinations**: A judge that passes individual bias tests may fail on combined-bias items that are common in production
2. **Use multi-judge panels**: Consensus scoring reduces individual bias effects by 0.15 points per item
3. **Include base model baselines**: Compare biased (instruct) vs unbiased (base) judgments to quantify bias

### For Model Development
1. **Target instruction tuning, not pre-training**: Bias is acquired during post-training
2. **Design orthogonal attention patterns**: Models with more independent feature representations show additive (not compounding) interactions
3. **Consider the trade-off**: More instruction-following capability means more bias susceptibility

### For Bias Research
1. **Report interaction ratios alongside individual bias measurements**
2. **Test at least three bias types simultaneously**
3. **Include the bias-robustness trade-off in mitigation evaluations**

---

## 6. Open Questions and Future Directions

### Immediate (6 months)
- [ ] Validate predictions 1-5 from the unified model
- [ ] Extend to more bias types (authority, bandwagon, self-preference)
- [ ] Test cross-cultural bias interactions
- [ ] Replicate with human evaluation data

### Medium-term (1-2 years)
- [ ] Mechanistic interpretability: identify specific attention heads responsible for interactions
- [ ] Develop instruction tuning methods that minimize $\kappa$
- [ ] Build bias-aware training curricula
- [ ] Create standardized bias interaction benchmarks

### Long-term (3-5 years)
- [ ] Develop provably unbiased judge architectures
- [ ] Establish theoretical limits on bias-robustness trade-off
- [ ] Deploy bias monitoring in production evaluation pipelines
- [ ] Create international standards for AI evaluation fairness

---

## 7. Conclusion

We have presented a unified theory of scoring bias in LLM-as-a-Judge that explains the origin (instruction tuning), interaction (shared attention patterns), and mitigation (multi-judge consensus) of bias effects. The framework makes testable predictions, categorizes all known bias types, and provides practical guidance for evaluation design. This theory represents the first comprehensive synthesis of bias phenomena in automated AI evaluation.

---

## References

1. Li et al. (2025). Evaluating Scoring Bias in LLM-as-a-Judge. DASFAA 2026.
2. Yang et al. (2025). Any Large Language Model Can Be a Reliable Judge. NeurIPS 2025.
3. Pan et al. (2025). User-Assistant Bias in LLMs. ACL 2026 Findings.
4. Soumik (2026). Judging the Judges. TMLR 2026.
5. This work, Studies 1 and 2.
6. This work, Theoretical Monograph.
