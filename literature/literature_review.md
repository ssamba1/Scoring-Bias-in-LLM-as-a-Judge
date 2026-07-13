# Comprehensive Literature Review — LLM-as-a-Judge Bias

## Overview
This review covers the key papers on LLM-as-a-Judge bias, organized by theme. Each entry includes a summary and relevance to our research.

---

## 1. Foundational Papers

### Zheng et al. (2023) — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"
**Venue:** NeurIPS 2023
**Summary:** Introduced MT-Bench and the LLM-as-a-Judge paradigm. First to document position bias and self-enhancement bias. Found GPT-4 agrees with humans 80% of the time.
**Relevance:** The paper that launched the field. All subsequent bias research builds on this.

### Li et al. (2025) — "Evaluating Scoring Bias in LLM-as-a-Judge"
**Venue:** DASFAA 2026 (arXiv June 2025)
**Summary:** First dedicated study of scoring bias. Identified rubric order bias, score ID bias, and reference answer score bias. Proposed evaluation framework. **Explicitly calls for root cause analysis.**
**Relevance:** Cornerstone paper for both research options. Citations checked: 100+ papers cite it, none address root cause.

---

## 2. Bias Taxonomy Papers

### Ye et al. (2024) — "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge"
**Venue:** NeurIPS SafeGenAI Workshop 2024
**Summary:** Proposed 12-bias taxonomy including position, verbosity, sentiment, authority, bandwagon, and fallacy oversight biases. Introduced CALM framework.
**Relevance:** Comprehensive taxonomy we reference for bias types.

### Park et al. (2024) — "OffsetBias: Leveraging Debiased Data for Tuning Evaluators"
**Venue:** EMNLP 2024 Findings
**Summary:** Introduced EVALBIASBENCH with 6 bias types. Proposed OFFSETBIAS training to improve robustness.
**Relevance:** Mitigation approach for format bias.

---

## 3. Position Bias

### Shi et al. (2025) — "A Systematic Study of Position Bias in LLM-as-a-Judge"
**Venue:** IJCNLP 2025
**Summary:** Studied position bias across 15 judges and 150,000 instances. Found bias varies by judge and task, not due to random chance. Introduced repetition stability metric.
**Relevance:** Key source for position bias effect sizes.

### Wang et al. (2024) — "Large Language Models are not Fair Evaluators"
**Venue:** ACL 2024
**Summary:** Proposed 3 calibration methods for position bias (multiple evidence, balanced position, human-in-the-loop).
**Relevance:** Position bias mitigation reference.

---

## 4. Self-Preference and Family Bias

### Wataoka et al. (2024) — "Self-Preference Bias in LLM-as-a-Judge"
**Venue:** NeurIPS SafeGenAI Workshop 2024
**Summary:** Formalized self-preference and family bias metrics. Found GPT-4 exhibits measurable self-preference.
**Relevance:** Family bias documented but no dedicated mitigation exists (gap).

### Panickssery et al. (2024) — "LLM Evaluators Recognize and Favor Their Own Generations"
**Venue:** NeurIPS 2024
**Summary:** Showed causal link between self-recognition and self-preference. De-identification partially mitigates.
**Relevance:** Proof that bias can be causally linked to model properties.

---

## 5. Bias Mitigation

### Soumik (2026) — "Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies"
**Venue:** TMLR 2026
**Summary:** Compared 9 debiasing strategies across 5 models. Found Gemini 2.5 Flash + Combined Budget reaches highest agreement. Style bias is dominant. **Mentions cross-bias interaction as future work.**
**Relevance:** Most comprehensive debiasing study. Explicitly leaves bias interactions for future work.

### Fujinuma et al. (2026) — "Contrastive Decoding Mitigates Score Range Bias"
**Venue:** ACL 2026 Findings
**Summary:** Identified score range bias (shifted scales produce different correlations). Proposed contrastive decoding mitigation.
**Relevance:** Addresses different bias type than our three scoring biases.

### Feuer et al. (2026) — "Towards Provably Unbiased LLM Judges via Bias-Bounded Evaluation"
**Venue:** arXiv March 2026
**Summary:** Proposed average bias-boundedness (A-BB) framework for mathematical bias guarantees.
**Relevance:** Theoretical framework, not specific to scoring bias.

---

## 6. Training Stage & Root Cause

### Pan et al. (2025) — "User-Assistant Bias in LLMs"
**Venue:** ACL 2026 Findings
**Summary:** Compared base vs instruct vs reasoning models for user-assistant bias. Found instruction tuning amplifies bias, reasoning fine-tuning reduces it. **Methodology directly applicable to scoring bias.**
**Relevance:** Proves the base-vs-instruct comparison methodology works.

---

## 7. Survey Papers

### Gu et al. (2024) — "A Survey on LLM-as-a-Judge"
**Venue:** arXiv (cited 1661+)
**Summary:** Comprehensive survey with formal definition, bias taxonomy, mitigation strategies, and future directions.
**Relevance:** Main survey reference.

### Li et al. (2024) — "LLMs-as-Judges: A Comprehensive Survey"
**Venue:** arXiv
**Summary:** 60-page survey covering functionality, methodology, applications, meta-evaluation, and limitations.
**Relevance:** Secondary survey reference.

---

## 8. Activation Steering (Why We Chose Not To)

### Wehner et al. (2025) — "Taxonomy, Opportunities, and Challenges of RepE"
**Venue:** arXiv (v5 Oct 2025)
**Summary:** Definitive survey on Representation Engineering. 12 challenges identified. 0 fully solved, 9 partially solved.
**Relevance:** We determined activation steering is too competitive and compute-intensive for a HS project.

---

## 9. Additional Relevant Work

### Xu et al. (2026) — "Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge"
**Venue:** arXiv Feb 2026
**Summary:** Shows rubric-based evaluation has position bias in score OPTIONS. Proposes random permutations. Does NOT address rubric ORDER bias (criteria ordering).
**Relevance:** Adjacent work — confirms our gap (rubric order bias) is distinct.

### Hong et al. (2026) — "RULERS: Locked Rubrics and Evidence-Anchored Scoring"
**Venue:** arXiv Jan 2026
**Summary:** Three-stage framework for reliable rubric scoring. Improves stability under rubric perturbations as side effect.
**Relevance:** Partially addresses rubric reliability but not a dedicated study.

### Doğruöz et al. (2026) — "Challenges and Recommendations for LLMs-as-a-Judge in Multilingual Settings"
**Venue:** arXiv Jul 2026
**Summary:** Shows only 33 of 650 LLM-as-a-Judge papers focus on multilingual/low-resource settings.
**Relevance:** Documents cross-cultural bias as under-explored.
