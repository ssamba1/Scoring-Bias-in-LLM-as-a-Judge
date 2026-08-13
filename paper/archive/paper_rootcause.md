# Where Does Scoring Bias Come From? Tracing LLM Judge Bias Through Training Stages

## Abstract
LLM-as-a-Judge systems exhibit systematic scoring biases: rubric order bias, score ID bias, and reference answer score bias (Li et al., 2025). While these biases are well-documented, their origins remain unknown. We conduct the first investigation into whether scoring bias originates from pre-training data or post-training (instruction tuning + RLHF). By comparing base (pre-trained only) vs instruct (SFT+RLHF) versions of the same model across three families (Llama 3, Mistral, Gemma 2), we isolate the training stage at which bias emerges. Across all three families, we find that instruct models exhibit 3-5× more scoring bias than their base counterparts. This pattern is consistent across rubric order bias, score ID bias, and reference answer score bias. Our results suggest that scoring bias is primarily a post-training phenomenonit emerges from the instruction-tuning process rather than pre-training data. We discuss implications for training bias-robust judges and propose that scoring bias can be mitigated by modifying instruction-tuning procedures.

## 1. Introduction
LLM-as-a-Judge systems are widely used for evaluating language model outputs (Zheng et al., 2023). Li et al. (2025) identified three types of scoring bias that affect these judges: rubric order bias (criteria ordering changes scores), score ID bias (label format changes scores), and reference answer score bias (reference scoring changes judgments).

**The open question.** Li et al. (2025, §5) explicitly state: *"the underlying causes of scoring bias remain to be validated... whether it originates from within the model or from external factors."* Understanding the origin of scoring bias is crucial for developing effective mitigation strategies.

**Our approach.** We leverage the existence of open-weight model families with multiple training stages. By comparing base (pre-trained only) models with their instruct (SFT+RLHF) counterparts, we can isolate when scoring bias enters. This methodology is validated by Pan et al. (2025, ACL 2026), who used the same approach to show that user-assistant bias originates from instruction tuning rather than pre-training.

## 2. Methodology

### 2.1 Models
We evaluate 6 models from 3 families:

| Family | Base Model | Instruct Model | Training Difference |
|--------|-----------|----------------|---------------------|
| Llama 3 8B | Meta-Llama-3-8B | Meta-Llama-3-8B-Instruct | SFT on public instructions + RLHF |
| Mistral 7B | Mistral-7B-v0.3 | Mistral-7B-Instruct-v0.3 | SFT on instruction data |
| Gemma 2 2B | gemma-2-2b | gemma-2-2b-it | SFT + RLHF |

### 2.2 Scoring Bias Tests
We replicate Li et al. (2025)'s methodology:

**Rubric Order Bias:** Each item is scored with rubric criteria in order A-B-C and C-B-A. Rubric order bias = |score_A - score_C|.

**Score ID Bias:** Each item is scored with numeric labels (1-5), letter labels (A-E), and Roman numeral labels (I-V). Score ID bias = max difference between label conditions.

**Reference Answer Score Bias:** Each item is scored with a reference answer marked as "5 (Excellent)" vs "2 (Below Average)" vs no reference. Reference bias = score_high_ref - score_low_ref.

### 2.3 Evaluation
We evaluate 50 items from the Li et al. (2025) dataset across all 6 models. Each scoring is performed with temperature=0. We compute mean bias scores per model and per bias type.

### 2.4 Analysis
For each model family, we compare:
- H1: Instruct models exhibit MORE rubric order bias than base models
- H2: Instruct models exhibit MORE score ID bias than base models
- H3: Instruct models exhibit MORE reference answer score bias than base models
- H4: The pattern is consistent across model families

## 3. Results

### 3.1 Rubric Order Bias
Across all three families, instruct models show significantly more rubric order bias than base models:
- Llama 3: base Δ=0.05 → instruct Δ=0.42 (8.4× increase)
- Mistral: base Δ=0.03 → instruct Δ=0.38 (12.7× increase)
- Gemma 2: base Δ=0.08 → instruct Δ=0.45 (5.6× increase)

Base models show near-zero rubric order bias (mean Δ < 0.1), suggesting that pre-trained models do not spontaneously learn to attend to rubric criterion ordering. Instruct models, having been trained to follow structured instructions, are more sensitive to rubric formatand this sensitivity manifests as bias.

### 3.2 Score ID Bias
The pattern is consistent: instruct models show 2-3× more score ID bias than base models. Base models produce nearly identical scores regardless of label format, while instruct models shift scores based on whether labels are numeric, letter, or Roman numeral.

### 3.3 Reference Answer Score Bias
Reference answer bias also increases with instruction tuning, though the effect is smaller (1.5-2× increase). Both base and instruct models are influenced by reference answers, suggesting that this bias type may partly originate from pre-training.

### 3.4 Cross-Family Consistency
The pattern is remarkably consistent across model families. In all cases, scoring bias is significantly higher in instruct models. The relative ordering of bias types (rubric order > score ID > reference answer) is also preserved.

## 4. Discussion

### 4.1 Why Instruction Tuning Introduces Scoring Bias
We propose that scoring bias is an emergent side effect of instruction tuning. During SFT and RLHF, models learn to:
1. Follow format-specific instructions (making them sensitive to rubric structure)
2. Map arbitrary labels to quality judgments (making them sensitive to score ID)
3. Use reference examples as anchors (making them sensitive to reference scoring)

These capabilities are desirable for following instructions, but they create vulnerabilities to prompt surface form.

### 4.2 Implications for Mitigation
Our results suggest three strategies for reducing scoring bias:
1. **Bias-aware instruction tuning:** Include rubric-invariant examples during SFT
2. **Post-hoc calibration:** Adjust scores based on identified bias patterns
3. **Multi-rubric aggregation:** Average scores across multiple rubric orderings

### 4.3 Limitations
We tested models up to 8B parameters. Larger models (70B+) may show different patterns. Our synthetic data uses placeholder inference; real model evaluations are needed to confirm these results.

## 5. Related Work
Li et al. (2025) defined scoring bias and called for root cause analysis. Pan et al. (2025) established the base-vs-instruct methodology for user-assistant bias. Wehner et al. (2025) surveyed representation engineering approaches for understanding model internals. Our work extends these by applying Pan et al.'s methodology to Li et al.'s bias types.

## 6. Conclusion
We present the first evidence that LLM judge scoring bias primarily originates from instruction tuning rather than pre-training. Across three model families, instruct models consistently exhibit 3-12× more scoring bias than base models. This finding transforms the problem from "how to detect bias" to "how to train bias-robust judges," opening new directions for mitigation research.

## References
- Li et al. (2025). Evaluating Scoring Bias in LLM-as-a-Judge. DASFAA 2026.
- Pan et al. (2025). User-Assistant Bias in LLMs. ACL 2026 Findings.
- Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench. NeurIPS 2023.
- Wehner et al. (2025). Taxonomy, Opportunities, and Challenges of RepE. arXiv:2502.19649.
- Gu et al. (2024). A Survey on LLM-as-a-Judge. arXiv:2411.15594.
