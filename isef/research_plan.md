# ISEF Research Plan — Scoring Bias in LLM-as-a-Judge

## 1. Abstract

Large language models (LLMs) deployed as automated judges (LLM-as-a-Judge) exhibit systematic scoring biases. Prior work documented over 35 bias types but left a fundamental question unanswered: does scoring bias originate from pre-training or instruction tuning? This study compares base (pre-trained only) and instruct (fine-tuned) variants across 9 model families using three scoring bias probes — rubric order, score ID, and reference answer — totaling 54,000 judgments across 31 model variants. We find that instruction tuning decreases format-related bias (rubric order: −0.42; score ID: −0.72) but increases content-related bias in larger RLHF-trained models (e.g., Llama-3.1-8B: +1.58). The 22-model landscape shows Score ID bias has the largest average effect (Δ = 0.68). These findings demonstrate that scoring bias is modulated by instruction tuning, not inherent to pre-training.

## 2. Research Question / Hypothesis

**Primary Research Question:** Does instruction tuning change scoring bias magnitude in LLM-as-A-Judge models, and in which direction?

**Sub-Questions:**
- RQ1: Is the direction of change consistent across bias types (format vs. content)?
- RQ2: Is the direction consistent across model families and architectures?
- RQ3: Do training methods (SFT, DPO, RLHF) modulate the effect?

**Hypotheses (specified before data analysis):**
- H1: Instruction tuning changes scoring bias magnitude; format-related bias decreases while content-related bias increases.
- H2: The direction of change differs between format (decrease) and content (increase) bias types.
- H3: This differential effect is consistent across model families and architectures.
- H4: RLHF-trained families show a stronger differential effect than SFT-only or SFT+DPO families.

## 3. Methodology

### 3.1 Model Selection

**Primary analysis** — 9 model families with both base and instruct variants:
| Family | Sizes | Training |
|--------|-------|----------|
| Meta Llama 3.1 | 8B | RLHF |
| Meta Llama 3.2 | 1B, 3B | RLHF |
| Meta Llama 2 | 7B | RLHF |
| Mistral 7B v0.3 | 7B | SFT+DPO |
| Qwen 2.5 | 0.5B, 1.5B, 7B | RLHF |
| Google Gemma 2 | 2B, 9B | RLHF |
| StableLM 2 | 1.6B | SFT |

**Breadth analysis** — 22 additional instruct-tuned models including DeepSeek V3/V4, Google Gemma 3, Microsoft Phi-4, Mistral Nemo, Cohere Command-R, Tencent Hy3, and others (see paper Table 3).

### 3.2 Evaluation Items

50 instruction-response pairs spanning 5 domains:
- Science (10 items)
- Technology (10 items)
- Humanities (10 items)
- Daily Life (10 items)
- Mathematics (10 items)

Items were sampled from public instruction-following evaluation sets and rewritten to be factual, mid-quality responses (approximately 3–4 out of 5) to allow bias detection in either direction.

### 3.3 Scoring Bias Probes

Following the perturbation framework of Li et al. (DASFAA 2026), we measure three bias types:

1. **Rubric Order:** Control (1=worst, 5=best), reversed (1=best, 5=worst), random label mapping.
2. **Score ID:** Numeric (1–5), letter grades (A–E), descriptive labels (Poor–Excellent).
3. **Reference Answer:** No exemplar, good exemplar, poor exemplar shown before scoring.

### 3.4 Inference Setup

- Local models: greedy decoding (temperature 0), token-by-token generation
- API models (OpenRouter): chat completions, temperature 0, max 5 tokens, 15-second timeout
- Total judgment count: 24,300 (base-instruct pairs) + 29,700 (instruct-only) = 54,000
- Platform: Kaggle T4 GPU (primary), OpenRouter API (supplementary)
- Total compute cost: under $3 USD

### 3.5 Metrics

- **Max Delta (Δ):** maximum absolute difference between control and biased variant means
- **Flip Rate (FR):** proportion of items where biased score differs from control
- **Cohen's d:** standardized effect size
- **Mean Absolute Deviation (MAD):** average absolute deviation across variants

### 3.6 Alternative Explanations Tested

Four competing hypotheses are examined and found inconsistent with the data:
1. Global scoring shift (all probes would move same direction; they do not)
2. Single-family dominance (pattern persists when any family is removed)
3. Probe ordering artifacts (control and biased differ only in bias manipulation)
4. Parser artifacts (numeric and letter variants independently confirm the pattern)

## 4. Bibliography

1. Li, S., et al. (2026). Scoring Bias in LLM-as-a-Judge. *Proceedings of DASFAA 2026*. — Introduced scoring bias definition and measurement framework; called for root cause analysis.

2. Pan, R., et al. (2026). User Bias in Instruction-Tuned LLMs. *ACL 2026 Findings*. — Validated the base-versus-instruct methodology for studying bias; found instruction-tuned models exhibit strong user bias while base models remain neutral.

3. Zheng, L., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *arXiv:2306.05685*. — Systematized LLM-as-a-Judge evaluation; documented length and position biases.

4. Wang, P., et al. (2024). Large Language Models are Not Fair Evaluators. *ACL 2024*. — Documented position bias in pairwise evaluation; reported 46.3% conflict rate for GPT-4.

5. Ye, J., et al. (2024). A Comprehensive Study of LLM Evaluation Bias. *NeurIPS Workshop 2024*. — Cataloged 12 bias types across 6 LLMs; proposed CALM framework.

6. Thakur, S., et al. (2024). Judging the Judges: Examining LLM Judge Bias. *arXiv:2410.02834*. — Found base and instruct versions show different alignment with human judges.

7. Park, J., et al. (2024). OffsetBias: Mitigating LLM Judge Bias. *EMNLP 2024*. — Identified six bias types; proposed debiased training data for judges.

8. Chen, G., et al. (2024). Humans and LLMs: How Biases Are Similar. *arXiv:2411.02767*. — Compared human and LLM judgment biases; found both exhibit similar susceptibility to irrelevant factors.

## 5. Timeline

| Phase | Duration | Period | Activities |
|-------|----------|--------|------------|
| Literature Review | 4 weeks | Jan–Feb 2026 | Read 60+ papers on LLM bias and evaluation; identified open problem |
| Experimental Design | 2 weeks | Feb 2026 | Designed perturbation framework; specified hypotheses RQ1–RQ4 |
| Data Collection (Phase 1) | 2 weeks | Mar 2026 | Ran base-instruct comparisons on Kaggle T4 GPU (24,300 judgments) |
| Data Collection (Phase 2) | 1 week | Mar 2026 | Ran instruct-only models via OpenRouter API (29,700 judgments) |
| Analysis | 2 weeks | Apr 2026 | Statistical analysis, attention weight extraction, alternative explanation tests |
| Paper Writing | 2 weeks | Apr–May 2026 | Wrote camera-ready paper; created figures and tables |
| Revisions | 1 week | May 2026 | Peer feedback; accuracy checks; reproducibility verification |
| **Current** | — | **Jul 2026** | **Preparing ISEF competition materials** |

Total timeline: Approximately 6 months from start to ISEF-ready materials.

## 6. Approvals

**No approvals required.** This project involves:
- No human subjects
- No vertebrate animals
- No hazardous chemicals or biological materials
- No recombinant DNA
- No human/animal tissue
- All computational research using publicly available open-weight AI models
- All code and data are publicly available and fully reproducible
