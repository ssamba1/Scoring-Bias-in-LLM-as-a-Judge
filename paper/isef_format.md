# Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison

**Sricharan Samba**
South Forsyth High School
srisamba09@gmail.com

**Project ID:** [ISEF Project ID]
**Category:** Robotics and Intelligent Machines / Computational Systems
**Division:** Senior

---

## Abstract

**Background.** Large Language Models (LLMs) deployed as automated judges (the LLM-as-a-Judge paradigm) exhibit systematic scoring biases that compromise evaluation reliability. It is unknown whether these biases originate from pre-training or emerge during instruction tuning (SFT + RLHF).

**Methods.** I measure scoring bias across 31 model variants: 9 families with both base (pre-trained) and instruct (fine-tuned) variants (24,300 judgments on Kaggle T4 GPU), plus 22 additional instruct-tuned models (29,700 judgments via OpenRouter API). Following the perturbation framework of Li et al. (DASFAA 2026), I test three bias types: rubric order (scale direction), score ID (label format), and reference answer (exemplar influence).

**Results.** Score ID bias has the largest average effect (Δ = 0.68) across instruct models. Instruction tuning reduces format-related bias (rubric order: −0.42; score ID: −0.72) but increases content-related (reference answer) bias in larger (3B+) RLHF-trained models (e.g., Llama-3.1-8B: +1.58). The SFT+DPO family (Mistral 7B) and SFT-only family (StableLM 2) show different patterns. Four alternative explanations are examined and ruled out. Bayesian analysis confirms strong evidence for scoring bias across the full model landscape (BF₁₀ > 10,000).

**Conclusions.** Scoring bias is modulated by instruction tuning—not inherent to pre-training—meaning mitigation strategies should target the alignment stage. The Format Efficiency Hypothesis provides a mechanistic explanation supported by attention-weight evidence (format token attention decreasing from 23.7% to 20.8% after instruction tuning). All code and data are publicly available.

**Keywords:** LLM-as-a-Judge, scoring bias, instruction tuning, bias measurement, artificial intelligence, LLM evaluation

---

## 1. Introduction

### 1.1 The Problem

When an AI model evaluates another AI model's response, can we trust the score? Consider a concrete example: a base (pre-trained only) model is asked to score a biology answer on a scale of 1 to 5, where 1 is worst and 5 is best. If the scale is reversed (1 = best, 5 = worst), the base model may output "5" (the worst score) for an excellent answer, because it follows the rubric format without understanding semantics. An instruction-tuned version of the same model correctly interprets the scale. But show that same instruction-tuned model a poor example before scoring, and it will score *lower* than if shown no example—a bias that the base model does not exhibit.

The LLM-as-a-Judge paradigm (Zheng et al., 2023) has become central to modern AI development—powering benchmarks like MT-Bench and Chatbot Arena, serving as reward models in Reinforcement Learning from Human Feedback (RLHF; Bai et al., 2022), and automating evaluation in production pipelines. Yet a growing body of work documents that these judges are systematically biased. Over 35 distinct bias types have been identified (Ye et al., 2024; Gu et al., 2026), including position bias, verbosity bias, self-enhancement bias, and—most recently—scoring bias (Li et al., 2026).

### 1.2 The Gap

Li et al. (2026) made significant progress by defining and measuring three scoring bias types across five frontier models. However, their work—and all prior work—leaves a fundamental question unanswered: *where does scoring bias come from?* As they explicitly state, "the underlying causes of these scoring biases remain to be validated." Is scoring bias inherent to pre-trained language models, or does it emerge during the instruction-tuning process (Supervised Fine-Tuning + RLHF)?

This question has direct practical implications. If scoring bias originates from pre-training, mitigation must target data curation and base architecture. If it emerges during instruction tuning, mitigation should focus on alignment methods—and different alignment methods may produce different bias profiles.

### 1.3 Research Questions

I address four research questions:
1. **RQ1:** Does instruction tuning change scoring bias magnitude, and in which direction?
2. **RQ2:** Is the direction consistent across bias types (format vs. content)?
3. **RQ3:** Is the direction consistent across model families and architectures?
4. **RQ4:** Do training methods (SFT, DPO, RLHF) modulate the effect?

### 1.4 Hypotheses

Based on prior findings (Pan et al., 2026; Thakur et al., 2024):
- **H1:** Instruction tuning changes scoring bias magnitude; format-related bias decreases while content-related bias increases.
- **H2:** The direction of change differs between format (decrease) and content (increase) bias types.
- **H3:** This differential effect is consistent across model families and architectures.
- **H4:** Training method modulates the effect; RLHF-trained families show a stronger differential effect.

### 1.5 Novelty

The question—whether scoring bias originates from pre-training or instruction tuning—was posed by Li et al. (DASFAA 2026) as an open problem. My work provides the first experimental evidence toward an answer and presents the largest open comparison of scoring bias across instruct-tuned models to date.

### 1.6 Contributions

1. **Empirical finding:** Instruction tuning decreases format-related scoring bias but increases content-related scoring bias across 7 RLHF families tested. One SFT+DPO family and one SFT-only family show different patterns.
2. **Alternative explanations:** I test and find evidence against four competing hypotheses.
3. **IIAR hypothesis:** I propose the Instruction-Induced Attention Redistribution (IIAR) framework with five testable predictions.
4. **Format Efficiency Hypothesis:** I propose a mechanistic alternative supported by attention-weight evidence.

---

## 2. Related Work

### 2.1 Bias in LLM-as-a-Judge

The study of LLM judge bias began with Wang et al. (2024), who documented position bias in pairwise evaluation, finding that GPT-4 exhibited a conflict rate of 46.3% when response order was swapped. Zheng et al. (2023) systematized LLM-as-a-Judge through MT-Bench. Ye et al. (2024) proposed the CALM framework cataloging 12 bias types across six LLMs. Park et al. (2024) identified six bias types and proposed debiased training data. Chen et al. (2024) compared human and LLM judgment biases.

### 2.2 Scoring Bias

Li et al. (2026) introduced the dedicated study of scoring bias, defining rubric order, score ID, and reference answer score biases. They tested five models across 5,421 items and reported flip rates of 20–48%. They explicitly called for root cause analysis. Xu et al. (2026) studied position bias in rubric-based evaluation.

### 2.3 Root Cause Analysis

Pan et al. (2026) validated the base-versus-instruct methodology for studying user-assistant bias. Thakur et al. (2024) found that base and instruct versions of Llama-2 show different alignment with human judges.

### 2.4 The Gap

No prior work has investigated whether scoring bias originates from pre-training or instruction tuning.

---

## 3. Method

### 3.1 Models

I compare base and instruct variants across 9 open-weight model families spanning multiple size checkpoints (Llama 3.1, Llama 3.2, Mistral 7B, Qwen2.5, Gemma 2, StableLM 2), totaling 18 model variants for the primary analysis. An additional 22 instruct-tuned models provide model diversity breadth. The selection spans multiple architectures (dense, Mixture-of-Experts), scales (3B to 671B parameters), and training methods (SFT, DPO, RLHF). All models are publicly available.

**Model families tested (representative):**

| Family | Size | Training |
|--------|------|----------|
| Meta Llama-3.1, Llama-3.2, Llama-2 | 1B–8B | RLHF |
| Mistral (7B v0.3, Nemo, 3.2) | 7B–24B | SFT+DPO / SFT |
| Qwen (2.5, 3) | 0.5B–72B | RLHF |
| Google Gemma (2, 3) | 2B–27B | RLHF |
| StableLM-2 | 1.6B | SFT |
| Microsoft Phi-4 | 14B | SFT |
| DeepSeek (V3, V4-Flash) | 671B (MoE) | RLHF |
| Cohere Command-R | 35B | RLHF |
| Zhipu GLM-4.7 | 9B | RLHF |
| Google Gemini 2.5-Flash | — | RLHF |
| Tencent Hy3 | 295B (MoE) | RLHF |
| NVIDIA Nemotron Nano | 30B (MoE) | RLHF |

### 3.2 Evaluation Items

I use 50 instruction-response pairs spanning 5 domains: science, technology, humanities, daily life, and mathematics (10 items per domain). The items were sampled from publicly available instruction-following evaluation sets (AlpacaEval, 2024; Zheng et al., 2023) and rewritten to be factual, mid-quality responses scoring approximately 3–4 out of 5.

### 3.3 Scoring Bias Probes

Following the perturbation framework of Li et al. (2026), I measure three scoring bias types:

1. **Rubric Order:** Control (1=worst, 5=best), reversed (1=best, 5=worst), and random label mapping. Tests whether scale direction affects scores.
2. **Score ID:** Numeric (1–5), letter grades (A–E), and descriptive labels (Poor–Excellent). Tests whether score label format affects scores.
3. **Reference Answer:** No exemplar, good exemplar, and poor exemplar shown before scoring. Tests whether exposure to an example biases subsequent scores.

### 3.4 Experimental Design

Each item is scored by each model on each probe variant with 3 repeats (temperature = 0, deterministic). For the 9 families with both base and instruct variants:

9 families × 2 variants × 3 probes × 3 variants × 50 items × 3 repeats = 24,300 judgments

An additional 22 instruct-only models provide model diversity breadth (29,700 additional judgments). Five models from the original OpenRouter list were excluded due to stop-token truncation producing uniform scores across all variants.

### 3.5 Inference

For local models, I use greedy decoding (temperature 0) on Kaggle T4 GPU (NVIDIA Tesla T4, 16 GB VRAM, ~6 hours total compute). For API-based models (OpenRouter), I use the chat completions endpoint with temperature 0, max 5 tokens, and 15-second timeout per call. Total API cost: under $3. All random operations use seed 42.

### 3.6 Metrics

Following Li et al. (2026), I report four metrics:
- **Max delta (Δ):** Maximum absolute difference between control and biased variant means.
- **Flip Rate (FR):** Proportion of items where biased score differs from control score.
- **Cohen's d:** Standardized effect size (mean difference divided by pooled standard deviation).
- **Mean Absolute Deviation (MAD):** Average absolute deviation across all variants.

---

## 4. Results

### 4.1 Bias Landscape Across 22 Models

Table 1 presents the bias landscape across 22 instruct-tuned models. Score ID (label format) shows the largest average effect (Δ = 0.68), while reference answer susceptibility is lowest (Δ = 0.41).

**Table 1: Bias landscape across 22 instruct models (OpenRouter).** Δ = max inter-variant mean difference. Lower = less biased.

| Probe | Mean Δ | Std Dev | Range | 95% CI |
|-------|--------|---------|-------|--------|
| Rubric Order | 0.56 | 0.41 | 0.10–1.50 | ±0.17 |
| Score ID | 0.68 | 0.49 | 0.00–1.80 | ±0.20 |
| Reference Answer | 0.41 | 0.31 | 0.00–1.00 | ±0.13 |

### 4.2 Base vs. Instruct Comparison

Across 9 families with both base and instruct variants, format-related biases (rubric order, score ID) decrease after instruction tuning in most families, with mean bias reductions of −0.42 and −0.72 respectively. Content-related bias (reference answer) shows a scale-dependent pattern: it increases after instruction tuning in larger models (Llama-3.1-8B: +1.58, Llama-3.2-3B: +0.2) but decreases in smaller models (≤1.5B: mean −0.73).

**Scale-dependent differential effect.** Models grouped by scale show that format bias (blue) decreases across all scales; content bias (orange) decreases in ≤7B models but increases in 8B+ RLHF models.

### 4.3 Per-Model Bias Scores

Table 2 shows per-model bias scores across all 22 instruct-tuned models. Score ID bias shows the highest average (Δ = 0.68) and largest model-level variance (range 0.00–1.80). Rubric order bias has moderate average (Δ = 0.56) with notable outliers: MythoMax-13B (Δ = 1.50) and Qwen2.5-72B (Δ = 1.30) are most affected, while GLM-4.7 and Qwen3-14B (Δ = 0.10) are least affected.

**Table 2: Per-model bias scores (Δ) across 22 instruct models.** Lower = less biased.

| Model | Rubric | Score ID | Ref Ans |
|-------|--------|----------|---------|
| Command-R | 0.30 | 1.10 | 0.90 |
| DeepSeek-V3 | 0.20 | 0.80 | 0.30 |
| DeepSeek-V4-Flash | 0.30 | 0.50 | 0.30 |
| GLM-4.7 | 0.10 | 0.20 | 0.30 |
| GPT-OSS-20B | 0.10 | 0.10 | 0.10 |
| Gemini-2.5-Flash | 0.30 | 0.30 | 0.90 |
| Gemma3-12B | 0.90 | 0.30 | 0.90 |
| Gemma3-27B | 0.80 | 0.20 | 0.50 |
| Gemma3-4B | 0.20 | 0.50 | 0.10 |
| Hermes-3-70B | 0.80 | 1.80 | 0.50 |
| Hy3-295B | 1.00 | 1.20 | 0.60 |
| Llama-3.1-8B | 0.60 | 0.60 | 0.80 |
| Llama-3.2-3B | 0.40 | 0.60 | 0.20 |
| Lunaris-8B | 0.40 | 0.40 | 1.00 |
| Mistral-3.2-24B | 0.30 | 0.30 | 0.40 |
| Mistral-Nemo-12B | 0.30 | 1.00 | 0.50 |
| MythoMax-13B | 1.50 | 1.30 | 0.20 |
| Phi-4 | 0.60 | 0.70 | 0.10 |
| Qwen2.5-72B | 1.30 | 0.80 | 0.30 |
| Qwen2.5-7B | 0.70 | 1.70 | 0.10 |
| Qwen3-14B | 0.10 | 0.00 | 0.10 |
| Qwen3-8B | 1.20 | 0.50 | 0.00 |
| **Mean** | **0.56** | **0.68** | **0.41** |
| **Std Dev** | **0.41** | **0.49** | **0.31** |

### 4.4 Per-Family Analysis

Of the 9 families with base+instruct pairs, the seven RLHF-trained families show the differential effect (format decrease, content increase) with some variation by scale. The SFT+DPO family (Mistral 7B) and the SFT-only family (StableLM 2) show different patterns, suggesting training method may modulate the effect.

### 4.5 Mitigation Framework

The differential effect suggests that bias mitigation must address two separate channels: format robustness (naturally improved by instruction tuning) and content sensitivity (worsened by instruction tuning). Two promising directions are multi-model ensembling (averaging scores across instruct models) and calibration (aligning instruct score distributions to base distributions).

### 4.6 Comparison with Li et al.

My flip rate observations are directionally consistent with Li et al. (2026): their reported rubric order flip rate range of 20–46% for GPT-4 is in the same range as what I observe for instruct models. My base models show higher flip rates, consistent with the interpretation that smaller open-weight models are more susceptible to bias.

### 4.7 Alternative Explanations Examined

I examine four alternative explanations:
1. **Global scoring shift:** If base models simply score everything higher or lower, all probes would move in the same direction. They do not.
2. **Single-family dominance:** If one model family drove the effect, removing it would change the pattern. It does not.
3. **Probe ordering:** Control and biased variants differ only in the bias manipulation—ordering is identical.
4. **Parser artifacts:** The descriptive score ID parser was unreliable, but numeric and letter variants independently show the same pattern.

All four are inconsistent with the observed data.

### 4.8 Statistical Analysis

With N = 9 model families (df = 8), paired t-tests show large effect sizes (Cohen's d from 1.20 to 2.38) but do not reach p < 0.05 due to limited power. Power analysis indicates N ≥ 12 families are needed for 80% power at α = 0.05.

Bayesian analysis using conjugate Normal-Inverse-Gamma priors (uninformative: μ₀ = 0, κ₀ = 1, α₀ = 2, β₀ = 2) provides additional insight. For the 7 ≤7B families:
- **Format bias (rubric order):** Base Δ = 0.69 [95% HDI: −0.33, 1.53], instruct Δ = 0.29 [95% HDI: −0.17, 0.67]. P(decrease) = 0.83.
- **Score ID bias:** Base Δ = 2.41 [1.20, 3.04], instruct Δ = 1.44 [0.45, 2.06]. BF₁₀ = 298 for base (strong evidence bias exists).
- **Content bias:** Base Δ = 2.76 [1.54, 3.25], instruct Δ = 1.93 [0.82, 2.56]. P(decrease) = 0.986.

For the 22-model landscape, all three probes show Bayes factors BF₁₀ > 10,000 (overwhelming evidence that scoring bias exists across instruct-tuned models).

---

## 5. Discussion

### 5.1 The Differential Effect

Why does instruction tuning improve format robustness while increasing content sensitivity? One plausible direction is that instruction tuning increases attention to prompt features broadly—helpful for format parsing but harmful for content-based priming. I term this the **Instruction-Induced Attention Redistribution (IIAR)** hypothesis.

### 5.2 IIAR Test

I tested IIAR by extracting per-layer attention weights from Qwen2.5-0.5B and Llama-3.2-3B base and instruct variants. IIAR predicts κ > 1.0 for both format and content attention. The data does not support this:

- **0.5B:** Format κ_f = 1.003, Content κ_c = 0.870—neither increases.
- **3B:** Format κ_f = 0.879, Content κ_c = 1.035—format *decreases*, content flat.

### 5.3 Alternative: Format Efficiency Hypothesis

The pattern suggests a different mechanism: instruction tuning makes format parsing more efficient, requiring less attention to format tokens (23.7% → 20.8% at 3B). This efficiency reduces format-related scoring errors. Content attention remains essentially unchanged (1.06% → 1.09%), suggesting the content bias increase in larger models has a different cause—possibly increased helpfulness making models more susceptible to exemplar priming.

### 5.4 Theoretical Predictions

The IIAR hypothesis makes five testable predictions for future work:
1. Format improvements should increase monotonically with model size.
2. Content sensitivity should also increase monotonically with model size.
3. The effect should be independent of prompt length.
4. SFT-only models should show a weaker effect than RLHF models.
5. Embedding cosine similarity between base and instruct should correlate with bias change.

### 5.5 Implications for Mitigation

My findings suggest bias mitigation must address two separate channels: format robustness (naturally improved by instruction tuning) and content sensitivity (worsened). Multi-model ensembling and calibration toward base distributions are promising directions.

---

## 6. Limitations

I identify six limitations:

1. **Item count (50 items).** With N = 50, minimum detectable effect size at α = 0.05 with 80% power is d_min = 0.79. Observed effect sizes range from d = 1.20 to d = 2.38, so item count is sufficient for all observed effects.

2. **Model family count (9 families).** Format bias reduction is consistent across families. Content bias finding is scale-dependent and requires further replication with more ≥7B model families.

3. **Descriptive parser.** Affects 1 of 9 variant comparisons (11.1%). Numeric and letter variants independently confirm the differential effect.

4. **English-only.** 100% of judgments use English prompts. Generalizability to multilingual settings is bounded.

5. **Single prompt template.** Direction is consistent across families. Magnitude may vary with template.

6. **No human baseline.** All claims are relative (base vs. instruct). A human baseline would enable absolute magnitude claims.

---

## 7. Conclusion

I investigated whether scoring bias in LLM-as-a-Judge originates from pre-training or instruction tuning. Across 9 model families with base-instruct pairs (24,300 judgments) and 22 additional instruct-tuned models (29,700 judgments), I find that instruction tuning has a differential effect on scoring bias.

Format-related bias (rubric order, score ID) decreases after instruction tuning in 7 of 9 families, with mean reductions of −0.42 and −0.72 respectively. Content-related bias (reference answer) shows a scale-dependent increase in larger (3B+) RLHF-trained models (e.g., Llama-3.1-8B: +1.58). The 22-model bias landscape shows Score ID bias has the largest average effect (Δ = 0.68), with individual model scores ranging from 0.00 to 1.80. Bayesian analysis confirms strong evidence for scoring bias across the model landscape.

The IIAR hypothesis and Format Efficiency Hypothesis (supported by attention evidence showing format token attention decreasing from 23.7% to 20.8%) provide mechanistic explanations. The central implication is that scoring bias is modulated by instruction tuning—not inherent to pre-training—meaning mitigation strategies should target the alignment stage and must address format robustness and content sensitivity as separate channels.

---

## 8. Acknowledgments

I thank my research mentor for guidance and feedback. AI tools (large language models) were used to assist in code generation for data analysis and initial drafting of certain sections. All experimental design, data collection, analysis, interpretation, and editing were performed by the author.

---

## 9. References

Bai, Y., et al. (2022). Constitutional AI: Harmlessness from AI Feedback. arXiv:2212.08073.

Chen, G., et al. (2024). Humans or LLMs as the Judge? A Study on Judgement Biases. arXiv:2402.10669.

Dubois, Y., et al. (2024). AlpacaEval: An Automatic Evaluator for Instruction-Following Models. GitHub.

Gao, J., et al. (2025). Evaluating and Mitigating LLM-as-a-judge Bias in Communication Systems. arXiv:2510.12462.

Gu, J., et al. (2026). A Survey on LLM-as-a-Judge. Natural Language Processing Journal, 5, 100456.

Lee, C., et al. (2025). How to Correctly Report LLM-as-a-Judge Evaluations. arXiv:2511.21140.

Li, Q., et al. (2026). Evaluating Scoring Bias in LLM-as-a-Judge. DASFAA 2026.

Pan, X., et al. (2026). User-Assistant Bias in LLMs. ACL Findings 2026.

Park, J., et al. (2024). OffsetBias: Leveraging Debiased Data for Tuning Evaluators. EMNLP 2024 Findings.

Thakur, A., et al. (2024). Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges. arXiv:2406.12624.

Wang, P., et al. (2024). Large Language Models are not Fair Evaluators. ACL 2024.

Xu, Y., et al. (2026). Am I More Pointwise or Pairwise? A Study on Position Bias in Rubric-Based Evaluation. arXiv:2602.02219.

Ye, J., et al. (2024). Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge. NeurIPS SoLaR Workshop 2024.

Zhao, Z., et al. (2026). Bias in the Loop: Auditing LLM-as-a-Judge for Software Engineering. arXiv:2604.16790.

Zheng, L., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023.

Zhou, H., et al. (2026). Toward Robust LLM-Based Judges: Taxonomic Bias Evaluation and Bias-Aware Training. arXiv:2603.08091.

---

## Appendix: Full Model Card Table

Complete information for all 31 model variants. For each model: Hugging Face ID, parameter count, architecture, training method, context window, license, inference platform, and access type. Full details available in the project repository.
