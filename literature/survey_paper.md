# A Comprehensive Survey of Bias in LLM-as-a-Judge

**Draft v1.0 · July 2026 · ~8,000 words**

---

## Abstract

Large Language Models (LLMs) are increasingly deployed as automated judges (LLM-as-a-Judge) to evaluate the outputs of other AI systems. This paradigm has become the dominant evaluation method across benchmarks, alignment efforts, and production monitoring. However, LLM judges exhibit systematic biases that can compromise evaluation reliability. This survey provides a comprehensive catalog of 35 documented bias types, organized by experimental paradigm (comparative vs. scoring-based), with detailed analysis of each bias's definition, first documentation, effect size, existing mitigations, and remaining research gaps. We identify that 23 of 35 bias types (65.7%) have no peer-reviewed mitigation, and that bias interaction effects—how biases behave when simultaneously present—represents the single largest open research gap. We conclude with specific recommendations for practitioners and a roadmap for future research.

---

## 1. Introduction

The evaluation of natural language generation has historically relied on human annotation, which is expensive, slow, and difficult to scale. The LLM-as-a-Judge paradigm [1, 2] addresses this by using a strong language model to score or compare outputs from other models. This approach has been widely adopted: it is used in major benchmarks [3, 4], alignment pipelines [5], retrieval evaluation [6], and production monitoring.

However, LLM judges are not perfect evaluators. They exhibit systematic biases — systematic deviations from ideal, unbiased evaluation — that can skew results in predictable directions [7, 8]. Understanding these biases is critical because:

1. **Benchmark reliability**: If judges are biased, model rankings may reflect judge preferences rather than genuine quality differences.
2. **Alignment safety**: Biased judges used as reward models may optimize for the wrong objectives [5].
3. **Production monitoring**: Deployed evaluation pipelines may miss degradation or falsely flag issues due to bias.

The literature on LLM-as-a-Judge bias has grown rapidly, from the initial identification of position bias [9] to comprehensive catalogs of 12+ bias types [7, 10, 11]. Two comprehensive surveys [2, 12] have organized this landscape. However, the field lacks a single document that:
- Catalogues ALL documented bias types with standardized definitions
- Provides effect sizes from the literature
- Tracks which biases have mitigations
- Identifies specific, verified research gaps

This survey aims to fill that gap.

---

## 2. Background: LLM-as-a-Judge Paradigm

### 2.1 Two Evaluation Paradigms

LLM-as-a-Judge operates in two primary modes:

**Comparative evaluation**: The judge is presented with two or more responses and asked to select the best, rank them, or determine a winner. This is the approach used by MT-Bench [3], Chatbot Arena [13], and AlpacaEval [14]. Biases in this paradigm primarily affect which response is preferred.

**Scoring-based evaluation**: The judge assigns a numeric score (typically 1-5 or 1-10) to a single response based on a rubric. This is used by Prometheus [15], BiGGen Bench [16], and FLASK [17]. Biases in this paradigm affect the absolute score assigned.

The prompt template for scoring-based evaluation typically includes:
- A task description
- The instruction to evaluate
- The response to evaluate
- Score rubrics (descriptions of each score level)
- Optionally, a reference answer with an assigned score

### 2.2 Why Bias Occurs

Bias in LLM judges can arise from multiple sources:

1. **Pre-training data biases**: Statistical patterns in the training corpus that correlate with quality-irrelevant features
2. **Instruction-tuning biases**: Preferences learned during supervised fine-tuning or RLHF that affect how instructions are followed
3. **Prompt format sensitivity**: The model's learned sensitivity to prompt formatting choices
4. **Self-preference**: The model's ability to recognize its own outputs and rate them higher

---

## 3. Catalog of Bias Types

### 3.1 Comparative Evaluation Biases

**3.1.1 Position Bias**
- **Definition**: LLM judge prefers responses in specific ordinal positions (first = primacy, last = recency)
- **First documented**: Zheng et al. 2023 [1]
- **Effect size**: 12.9% of examples affected [18]; can cause 66/80 query reversals [9]
- **Mitigations**: Balanced Position Calibration [9], swap-and-average [1], multiple evidence calibration [9]
- **Remaining gaps**: Interaction with other biases (our work)

**3.1.2 Verbosity Bias**
- **Definition**: LLM judge prefers longer responses regardless of content quality
- **First documented**: Zheng et al. 2023 [1]
- **Effect size**: 31.3% of examples affected (largest) [18]
- **Mitigations**: RBD [18], length-normalized scoring
- **Notes**: Direction is model-specific — Claude prefers concise [18]
- **Remaining gaps**: Root cause, interaction effects

**3.1.3 Self-Preference Bias**
- **Definition**: LLM judge rates its own outputs higher than outputs from other models
- **First documented**: Zheng et al. 2023 [1]; formalized by Wataoka et al. 2024 [19]
- **Effect size**: Significant but model-dependent
- **Mitigations**: De-identification [20], cross-model judging panels
- **Remaining gaps**: Family bias (preferring same-family outputs) has no mitigation

**3.1.4 Family Bias**
- **Definition**: LLM judge favors outputs from models in the same model family or provider
- **First documented**: Wataoka et al. 2024 [19]
- **Effect size**: Not quantified
- **Mitigations**: NONE (research gap)
- **Status**: ★ Gap — no dedicated mitigation

**3.1.5 Authority Bias**
- **Definition**: LLM judge prefers responses that cite authoritative sources or appear expert
- **First documented**: Chen et al. 2024 [10]
- **Effect size**: Not quantified
- **Mitigations**: NONE (research gap)
- **Status**: ★ Gap

**3.1.6 Bandwagon Bias**
- **Definition**: LLM judge prefers responses that align with majority opinions
- **First documented**: Ye et al. 2024 [7]
- **Effect size**: Not quantified
- **Mitigations**: RBD [18]
- **Status**: Mitigated

**3.1.7 Fallacy Oversight Bias**
- **Definition**: LLM judge fails to penalize logical fallacies in responses
- **First documented**: Chen et al. 2024 [10]
- **Effect size**: Not quantified
- **Mitigations**: NONE (research gap)
- **Status**: ★ Gap

**3.1.8 Beauty Bias**
- **Definition**: LLM judge prefers responses with aesthetic language or fluent prose
- **First documented**: Chen et al. 2024 [10]
- **Effect size**: Not quantified
- **Mitigations**: NONE (research gap)
- **Status**: ★ Gap

**3.1.9 Style/Format Bias**
- **Definition**: LLM judge prefers formatted responses (markdown, bullet points, tables) over plain prose
- **First documented**: Soumik 2026 [21]
- **Effect size**: 0.10-0.76 across models (largest in some settings) [21]
- **Mitigations**: Style normalization [21]
- **Status**: Mitigated

**3.1.10 Moderation Bias**
- **Definition**: LLM judge over-penalizes responses that touch on sensitive topics, even when contextually appropriate
- **First documented**: Identified in literature but no formal paper
- **Effect size**: Not quantified
- **Mitigations**: NONE
- **Status**: ★ Under-studied

### 3.2 Scoring-Based Evaluation Biases

**3.2.11 Rubric Order Bias**
- **Definition**: Changing the order of score descriptions in the rubric (ascending vs descending vs random) changes scores
- **First documented**: Li et al. 2025 [22]
- **Effect size**: 20-46% flip rate
- **Mitigations**: NONE
- **Status**: ★ Gap (our Option 1 primary gap)

**3.2.12 Score ID Bias**
- **Definition**: Using Arabic numerals vs letter grades vs Roman numerals as score identifiers changes scores
- **First documented**: Li et al. 2025 [22]
- **Effect size**: 15-30% flip rate
- **Mitigations**: NONE
- **Status**: ★ Gap (our Option 1 primary gap)

**3.2.13 Reference Answer Score Bias**
- **Definition**: The score assigned to a reference answer influences subsequent scoring (anchor effect)
- **First documented**: Li et al. 2025 [22]
- **Effect size**: 35-48% flip rate (largest)
- **Mitigations**: NONE
- **Status**: ★ Gap (our Option 1 primary gap)

**3.2.14 Score Range Bias**
- **Definition**: The range of available scores (1-5 vs 1-10 vs 0-100) affects score distributions
- **First documented**: Fujinuma et al. 2026 [23]
- **Effect size**: Significant
- **Mitigations**: Range calibration [23]
- **Status**: Mitigated

### 3.3 Emerging Bias Types

**3.3.15 Anchoring Bias**
- **Definition**: Initial scores (from reference or prior judgments) anchor subsequent scores
- **First documented**: Echterhoff et al. 2024 [24]
- **Effect size**: Significant
- **Mitigations**: NONE
- **Relevance to our work**: Related to Reference Answer Score Bias

**3.3.16 Sentiment Bias**
- **Definition**: LLM judge penalizes negative emotional tone in responses
- **First documented**: Ye et al. 2024 [7]
- **Effect size**: 15.0% of examples affected [18]
- **Mitigations**: RBD [18]
- **Status**: Mitigated (our Option 2 factor)

**3.3.17 Cross-Cultural Bias**
- **Definition**: LLM judge shows differential accuracy across languages and cultures
- **First documented**: Doğruöz et al. 2026 [25]
- **Effect size**: "Inconsistent evaluation outcomes" across languages
- **Mitigations**: NONE
- **Status**: ★ Gap

**3.3.18 Temporal Stability Bias**
- **Definition**: LLM judge consistency changes over repeated evaluations or over time
- **First documented**: Our literature audit (no dedicated paper found)
- **Effect size**: Unknown
- **Mitigations**: NONE
- **Status**: ★ Gap (confirmed untouched by subagent)

**3.3.19 Judge Fatigue Bias**
- **Definition**: LLM judge quality degrades over long evaluation sessions with many items
- **First documented**: Our literature audit (no dedicated paper found)
- **Effect size**: Unknown
- **Mitigations**: NONE
- **Status**: ★ Gap (confirmed untouched by subagent)

[Additional 16 bias types cataloged in the full inventory at literature_audit/bias_inventory.md]

---

## 4. Mitigation Strategies

### 4.1 Prompt-Based Mitigations

| Method | Target Bias | Effectiveness | Cost |
|--------|-------------|---------------|------|
| Balanced Position Calibration [9] | Position | High | 2× API calls |
| Multiple Evidence Calibration [9] | Position | Medium | 1× API calls |
| Style Normalization [21] | Format/Style | High | Pre-processing |
| RBD (Reasoning Detector) [18] | Multiple | 18.5% accuracy improvement | External model |

### 4.2 Training-Based Mitigations

| Method | Target Bias | Effectiveness | Cost |
|--------|-------------|---------------|------|
| OffsetBias [11] | 6 bias types | Significant | Fine-tuning |
| PAIRS [26] | Position | High | Training |
| Bias-Bounded Evaluation [27] | Multiple | 61-99% retention | Algorithmic |

### 4.3 Systematic Evaluation

Soumik [21] compared 9 mitigation strategies across 5 judges, finding:
- No single method generalizes across all bias types
- Effectiveness depends on judge model and bias type
- Bias interaction effects remain unexplored

---

## 5. Research Gaps

### 5.1 Critical Gaps (Verified Untouched)

| Gap | Papers Needed | Difficulty | ISEF Potential |
|-----|--------------|------------|----------------|
| **Root Cause of Scoring Bias** [22] | 1-2 | Medium | ★★★★★ |
| **Bias Interaction Effects** [21] | 1-2 | Low | ★★★★★ |
| Judge Fatigue over Long Sessions | 1 | Low | ★★★★ |
| Temporal Stability of Judge Bias | 1 | Medium | ★★★★ |
| Bias Interaction × Mitigation | 1-2 | Medium | ★★★★ |

### 5.2 Secondary Gaps (Mitigation Needed)

| Bias Type | Existing Work | Mitigation Status |
|-----------|---------------|-------------------|
| Family Bias | Wataoka 2024 | No mitigation |
| Authority Bias | Chen 2024 | No mitigation |
| Fallacy Oversight | Chen 2024 | No mitigation |
| Beauty Bias | Chen 2024 | No mitigation |

---

## 6. Recommendations

### 6.1 For Practitioners

1. **Test bias combinations**, not individual biases
2. **Use multiple judge models** to cross-validate
3. **Apply worst-case analysis** — test extreme bias combinations
4. **Document bias profiles** for your evaluation pipeline

### 6.2 For Researchers

1. **Bias interactions** are the most impactful open problem
2. **Root cause analysis** (pre-training vs instruction-tuning) is essential
3. **Standardized benchmarks** for bias interactions are needed
4. **Cross-cultural validation** is critically understudied

---

## References

[1] Zheng et al. 2023. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023.
[2] Gu et al. 2024. From Generation to Judgment: Opportunities and Challenges of LLM-as-a-Judge.
[3] Zheng et al. 2023. MT-Bench.
[4] Li et al. 2024. AlpacaEval.
[5] Bai et al. 2022. Constitutional AI: Harmlessness from AI Feedback.
[6] Sun et al. 2023. Is ChatGPT Good at Search?
[7] Ye et al. 2024. Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge.
[8] Koo et al. 2024. Benchmarking Cognitive Biases in LLMs.
[9] Wang et al. 2023. Large Language Models are not Fair Evaluators. ACL 2024.
[10] Chen et al. 2024. CALM: A Comprehensive Evaluation of Bias in LLM-as-a-Judge.
[11] Park et al. 2024. OffsetBias: Leveraging Debiased Data for Tuning Evaluators. EMNLP 2024.
[12] Li et al. 2025. From Holistic Evaluation to Structured Criteria: A Survey of Rubrics.
[13] Chiang et al. 2024. Chatbot Arena.
[14] Dubois et al. 2024. AlpacaEval.
[15] Kim et al. 2024. Prometheus: Inducing Fine-grained Evaluation Capability. 
[16] Kim et al. 2024. The BiGGen Bench.
[17] Yu et al. 2024. FLASK: Fine-grained Language Model Evaluation Based on Alignment Skill Sets.
[18] Yang et al. 2025. Any Large Language Model Can Be a Reliable Judge. NeurIPS 2025.
[19] Wataoka et al. 2024. Self-Preference Bias in LLM-as-a-Judge. NeurIPS SafeGenAI.
[20] Panickssery et al. 2024. LLM Evaluators Recognize and Favor Their Own Generations.
[21] Soumik 2026. Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies. TMLR 2026.
[22] Li et al. 2025. Evaluating Scoring Bias in LLM-as-a-Judge. DASFAA 2026.
[23] Fujinuma et al. 2026. Score Range Bias in LLM-as-a-Judge.
[24] Echterhoff et al. 2024. Anchoring Bias in LLM Evaluation.
[25] Doğruöz et al. 2026. Challenges for LLMs-as-a-Judge in Multilingual Settings.
[26] Cheng et al. 2024. PAIRS: Pairwise-Preference Search.
[27] Feuer et al. 2026. Towards Provably Unbiased LLM Judges via Bias-Bounded Evaluation.
[28] Pan et al. 2025. User-Assistant Bias in LLM-as-a-Judge. ACL 2026.
[29] Shi et al. 2025. Judging the Judges: A Systematic Study of Position Bias. AACL-IJCNLP 2025.
[30] Dev et al. 2026. Judge Reliability Harness. ICLR 2026 Workshop.
