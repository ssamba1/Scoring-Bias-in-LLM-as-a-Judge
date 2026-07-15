# LLM-as-a-Judge: Complete Bias Type Inventory

> **Exhaustive literature audit**  Every documented bias type in LLM-as-a-Judge research, with original paper, year, and mitigation status.
> Compiled: July 2026 | Target audience: High school AI/ML research students seeking untouched gaps.

---

## How to Read This Document

| Column | Meaning |
|--------|---------|
| **Bias** | Common name(s) of the bias |
| **Definition** | What the bias is |
| **First Paper** | The earliest paper that identified/defined it |
| **Year** | Publication year |
| **Venue** | Where it was published |
| **Mitigation Exists?** | ✅ = peer-reviewed mitigation published; ⬜ = none found |
| **Mitigation Paper(s)** | Which paper(s) proposed the fix |
| **Untouched Gap?** | ★ = no mitigation exists → potential research entry point |

---

## 1. Position Bias (Primacy / Recency)

**Definition:** LLM judge prefers the candidate response that appears in a particular ordinal position (first = primacy, last = recency), independent of content quality.

| Field | Value |
|-------|-------|
| **First Paper** | Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" |
| **Year** | 2023 |
| **Venue** | NeurIPS 2023 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | • Wang et al. (2024) ACL: "Large Language Models are not Fair Evaluators"  3 calibration methods (multiple evidence, balanced position, human-in-the-loop)<br>• Zheng et al. (2023): standard position-swap practice<br>• Zhou et al. (2024) CCL: "Mitigating the Bias of Large Language Model Evaluation"<br>• Soumik (2026) TMLR: systematic evaluation of 9 debiasing strategies |
| **Status** | Well-studied, multiple mitigations exist |

**Key follow-up works:**
- Shi et al. (2024/2025) "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge"  AACL/IJCNLP 2025
- Thakur et al. (2024) "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges"  GEM Workshop 2025

---

## 2. Verbosity Bias / Length Bias

**Definition:** LLM judge systematically favors longer responses, even when the extra length is padding, redundancy, or restating the same point.

| Field | Value |
|-------|-------|
| **First Paper** | Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" |
| **Year** | 2023 |
| **Venue** | NeurIPS 2023 |
| **Mitigation Exists?** | ✅ (partial) |
| **Mitigation Papers** | • Park et al. (2024) "OffsetBias"  OFFSETBIAS training dataset improves robustness<br>• Zhou et al. (2024) CCL  calibration-based method<br>• Post-hoc length control (Hu et al. 2024, "Explaining Length Bias") |
| **Status** | Mitigations exist but no silver bullet; still an active area |

---

## 3. Self-Preference Bias / Self-Enhancement Bias / Self-Bias

**Definition:** LLM judge rates its own outputs higher than outputs from other models, even when human evaluators consider them equal quality.

**Note:** "Self-enhancement" (Zheng 2023) and "self-preference" (Wataoka 2024) describe the same phenomenon.

| Field | Value |
|-------|-------|
| **First Paper** | Zheng et al. (self-enhancement bias)  NeurIPS 2023 |
| **Formal Metric** | Wataoka et al. (2024) "Self-Preference Bias in LLM-as-a-Judge"  NeurIPS SafeGenAI Workshop |
| **Causal Study** | Panickssery et al. (2024) "LLM Evaluators Recognize and Favor Their Own Generations"  NeurIPS 2024 |
| **Mitigation Exists?** | ✅ (partial) |
| **Mitigation Papers** | • Panickssery et al. (2024)  de-identification (hiding model identity)<br>• Yang et al. (2026) "Quantifying and Mitigating Self-Preference Bias of LLM Judges"  structured multi-dimensional evaluation strategy<br>• Multi-model juries / ensembles (industry practice) |
| **Status** | Active research; 2026 paper proposes first dedicated mitigation |

---

## 4. Family Bias

**Definition:** LLM judge favors outputs from models in the same model family (e.g., Claude judge favors Anthropic models), a broader form of self-preference.

| Field | Value |
|-------|-------|
| **First Paper** | Wataoka et al. (2024) "Self-Preference Bias in LLM-as-a-Judge" |
| **Year** | 2024 |
| **Venue** | NeurIPS SafeGenAI Workshop 2024 |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation** |
| **Status** | ★ **GAP: No peer-reviewed mitigation paper exists** |

---

## 5. Format Bias (Output Style / Presentation)

**Definition:** LLM judge prefers responses with markdown, bullet lists, numbering, or structured formatting even when the plain-text version contains better content.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) "OffsetBias"  identified as error case in EVALBIASBENCH |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Also studied by** | Ye et al. (2024) "Justice or Prejudice?" (as part of 12-bias taxonomy) |
| **Mitigation Exists?** | ✅ (partial) |
| **Mitigation Papers** | Park et al. (2024)  OFFSETBIAS training data partially addresses it |
| **Status** | Indirectly mitigated via debiased training data; no dedicated fix |

---

## 6. Scoring Bias  Score Rubric Order Bias

**Definition:** The order in which score rubric criteria are listed affects the judge's score.

| Field | Value |
|-------|-------|
| **First Paper** | Li et al. (2025) "Evaluating Scoring Bias in LLM-as-a-Judge" |
| **Year** | 2025 |
| **Venue** | arXiv 2025 (conf. proceedings TBD) |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 7. Scoring Bias  Score ID Bias

**Definition:** Whether candidates are labeled A/B vs. 1/2 vs. Alpha/Beta changes the judge's preference.

| Field | Value |
|-------|-------|
| **First Paper** | Li et al. (2025) "Evaluating Scoring Bias in LLM-as-a-Judge" |
| **Year** | 2025 |
| **Venue** | arXiv 2025 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 8. Scoring Bias  Reference Answer Score Bias

**Definition:** Providing a "golden" reference answer anchors the judge; varying the reference shifts scores.

| Field | Value |
|-------|-------|
| **First Paper** | Li et al. (2025) "Evaluating Scoring Bias in LLM-as-a-Judge" |
| **Year** | 2025 |
| **Venue** | arXiv 2025 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 9. Authority Bias / Citation Bias

**Definition:** Responses containing citations, expert quotes, or authoritative references get higher scores even when the citations are fabricated or irrelevant.

| Field | Value |
|-------|-------|
| **First Paper** | Chen et al. (2024) "Humans or LLMs as the Judge? A Study on Judgement Bias" |
| **Year** | 2024 |
| **Venue** | EMNLP 2024 |
| **Also studied by** | Ye et al. (2024) CALM framework |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation** |
| **Status** | ★ **GAP: No peer-reviewed mitigation paper exists** (reference-guided evaluation suggested but not formally proposed/tested) |

---

## 10. Fallacy Oversight Bias

**Definition:** LLM judge overlooks logical fallacies in arguments and accepts conclusions without critically evaluating supporting evidence.

| Field | Value |
|-------|-------|
| **First Paper** | Chen et al. (2024) "Humans or LLMs as the Judge? A Study on Judgement Bias" |
| **Year** | 2024 |
| **Venue** | EMNLP 2024 |
| **Also studied by** | Ye et al. (2024) CALM |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 11. Beauty Bias

**Definition:** The judge's evaluation is influenced by the aesthetic quality or surface fluency of writing rather than its substantive correctness.

| Field | Value |
|-------|-------|
| **First Paper** | Chen et al. (2024) "Humans or LLMs as the Judge? A Study on Judgement Bias" |
| **Year** | 2024 |
| **Venue** | EMNLP 2024 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 12. Sentiment Bias / Tone Bias

**Definition:** LLM judge prefers responses with a particular emotional tone (positive, cheerful, agreeable) over neutral or negative ones with the same factual content.

| Field | Value |
|-------|-------|
| **First Paper** | Ye et al. (2024) "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge" |
| **Year** | 2024 |
| **Venue** | NeurIPS SafeGenAI Workshop 2024 / ICLR 2025 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 13. Bandwagon Effect / Conformity Bias / Bandwagon-Effect Bias

**Definition:** LLM judge's scores shift toward a perceived majority opinion or consensus when social signals are present in the prompt.

| Field | Value |
|-------|-------|
| **First Paper** | Koo et al. (2024) "Benchmarking Cognitive Biases in Large Language Models as Evaluators" |
| **Year** | 2024 |
| **Venue** | Findings of ACL 2024 |
| **Also studied by** | Ye et al. (2024) CALM |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 14. Compassion Fade Bias (Source Identity Bias)

**Definition:** LLM judge evaluates identical content differently depending on the name/identity of the model or entity being judged.

| Field | Value |
|-------|-------|
| **First Paper** | Koo et al. (2024) "Benchmarking Cognitive Biases in LLMs as Evaluators" |
| **Year** | 2024 |
| **Venue** | Findings of ACL 2024 |
| **Also studied by** | Ye et al. (2024) CALM |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 15. Egocentric Bias

**Definition:** LLM judge penalizes response styles it would not itself produce, preferring answers that match its own generation patterns.

| Field | Value |
|-------|-------|
| **First Paper** | Koo et al. (2024) "Benchmarking Cognitive Biases in LLMs as Evaluators" |
| **Year** | 2024 |
| **Venue** | Findings of ACL 2024 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 16. Order Bias (Cognitive)

**Definition:** In multi-option evaluation, LLM judge prefers options based on their presentation order, distinct from position bias in pairwise comparison.

| Field | Value |
|-------|-------|
| **First Paper** | Koo et al. (2024) "Benchmarking Cognitive Biases in LLMs as Evaluators" |
| **Year** | 2024 |
| **Venue** | Findings of ACL 2024 |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation** |
| **Status** | ★ **GAP: No dedicated mitigation paper exists** |

---

## 17. Salience Bias / Attentional Bias

**Definition:** LLM judge focuses on salient or attention-grabbing features of a response rather than its overall quality.

| Field | Value |
|-------|-------|
| **First Paper** | Koo et al. (2024) "Benchmarking Cognitive Biases in LLMs as Evaluators" |
| **Year** | 2024 |
| **Venue** | Findings of ACL 2024 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 18. Distraction Bias

**Definition:** LLM judge is influenced by irrelevant or off-topic content inserted into a response, affecting the evaluation of an otherwise high-quality answer.

| Field | Value |
|-------|-------|
| **First Paper** | Ye et al. (2024) "Justice or Prejudice?" CALM framework |
| **Year** | 2024 |
| **Venue** | ICLR 2025 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 19. Diversity Bias

**Definition:** LLM judge's scoring is affected by identity-related attributes (gender, race, religion, etc.) mentioned in the response.

| Field | Value |
|-------|-------|
| **First Paper** | Ye et al. (2024) "Justice or Prejudice?" CALM framework |
| **Year** | 2024 |
| **Venue** | ICLR 2025 |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation for judge context** |
| **Status** | ★ **GAP: No mitigation paper specific to LLM-as-a-Judge exists** |

---

## 20. Refinement-Aware Bias

**Definition:** When LLM judges know a response has been refined (vs. original), their scoring shifts even when content quality is identical.

| Field | Value |
|-------|-------|
| **First Paper** | Ye et al. (2024) "Justice or Prejudice?" CALM framework |
| **Year** | 2024 |
| **Venue** | ICLR 2025 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 21. Concreteness Bias

**Definition:** LLM judge prefers responses with specific, concrete details or references even when those details are fabricated or irrelevant.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) "OffsetBias" |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | Park et al. (2024)  OFFSETBIAS training dataset |
| **Status** | Mitigation exists via debiased training data |

---

## 22. Empty Reference Bias

**Definition:** Judge prefers responses that reference generic, unverifiable advice over equally correct but less "reference-filled" alternatives.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) "OffsetBias" |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | Park et al. (2024)  OFFSETBIAS training dataset |
| **Status** | Mitigated via debiased data |

---

## 23. Content Continuation Bias

**Definition:** Judge prefers responses that continue or complete a partial thought in the prompt rather than providing accurate independent information.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) "OffsetBias" |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | Park et al. (2024)  OFFSETBIAS training dataset |
| **Status** | Mitigated via debiased data |

---

## 24. Nested Instruction Bias

**Definition:** Judge is confused by instructions embedded within response text, treating response content as evaluation criteria.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) "OffsetBias" |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | Park et al. (2024)  OFFSETBIAS training dataset |
| **Status** | Mitigated via debiased data |

---

## 25. Familiar Knowledge Bias

**Definition:** Judge prefers responses that align with common knowledge or widely accepted facts, penalizing correct but non-obvious answers.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) "OffsetBias" |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | Park et al. (2024)  OFFSETBIAS training dataset |
| **Status** | Mitigated via debiased data |

---

## 26. Teacher Preference Bias

**Definition:** LLM judges fine-tuned on a stronger teacher model's preferences inherit and amplify the teacher's biases, systematically favoring responses that the teacher would prefer.

| Field | Value |
|-------|-------|
| **First Paper** | Liu et al. (2025) "Assistant-Guided Mitigation of Teacher Preference Bias in LLM-as-a-Judge" |
| **Year** | 2025 |
| **Venue** | Findings of EMNLP 2025 |
| **Mitigation Exists?** | ✅ |
| **Mitigation Papers** | Liu et al. (2025)  AGDe-Judge (Assistant-Guided Debiasing) |
| **Status** | Dedicated mitigation exists |

---

## 27. Rich Content / Elaboration Bias

**Definition:** Judge favors responses that are more elaborate, descriptive, or "richer" in content, even if the extra detail is unnecessary (related to but distinct from verbosity bias).

| Field | Value |
|-------|-------|
| **First Paper** | Gao et al. (2026) "Evaluating and Mitigating LLM-as-a-judge Bias in Communication Systems" |
| **Year** | 2026 |
| **Venue** | arXiv 2026 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 28. Chain-of-Thought (CoT) Bias

**Definition:** Judge's scoring changes depending on whether the response uses explicit step-by-step reasoning vs. direct answer, regardless of correctness.

| Field | Value |
|-------|-------|
| **First Paper** | Gao et al. (2026) "Evaluating and Mitigating LLM-as-a-judge Bias in Communication Systems" |
| **Year** | 2026 |
| **Venue** | arXiv 2026 |
| **Mitigation Exists?** | ⬜ **NO mitigation** |
| **Status** | ★ **GAP: No mitigation paper exists** |

---

## 29. Gender Bias (in LLM-as-a-Judge)

**Definition:** LLM judge's scoring is affected by gendered language or stereotypes in the response text.

| Field | Value |
|-------|-------|
| **First Paper** | Gao et al. (2026) "Evaluating and Mitigating LLM-as-a-judge Bias in Communication Systems" |
| **Year** | 2026 |
| **Venue** | arXiv 2026 |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation for judge context** |
| **Status** | ★ **GAP: No mitigation paper exists specifically for LLM-as-a-Judge** |

---

## 30. Moderation Bias

**Definition:** LLM judge over-penalizes responses on sensitive topics, conflating content moderation with quality assessment.

| Field | Value |
|-------|-------|
| **First Paper** | Not formally defined in peer-reviewed literature; discussed in industry blogs (Sebastian Sigl 2025, FutureAGI 2026) |
| **Year** | 2025 |
| **Venue** | Non-academic |
| **Mitigation Exists?** | ⬜ **NO academic mitigation** |
| **Status** | ★ **GAP: Not formally studied in peer-reviewed research** |

---

## 31. Anchoring Bias (in LLM Judges)

**Definition:** LLM judge's score is anchored to a reference value (e.g., a provided example score, an initial impression) and insufficiently adjusted.

| Field | Value |
|-------|-------|
| **First Paper** | Not formally defined in LLM-judge literature; noted in "Anchoring and Contamination in Chained LLM Pipelines" (Zylos Research 2026) |
| **Year** | 2026 |
| **Venue** | Blog/research report |
| **Mitigation Exists?** | ⬜ **NO academic mitigation** |
| **Status** | ★ **GAP: Not formally studied in peer-reviewed LLM-as-a-Judge research** |

---

## 32. Label Bias / Selection Bias

**Definition:** Judge's preference shifts based on how options are labeled (e.g., option A vs. option 1) or the selection framing.

| Field | Value |
|-------|-------|
| **First Paper** | Reif & Schwartz (2024)  label bias in LLM evaluation |
| **Year** | 2024 |
| **Venue** | (identified in multiple papers) |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation** |
| **Status** | ★ **GAP: No dedicated mitigation paper exists** |

---

## 33. Leniency / Strictness Bias

**Definition:** Different LLMs (or the same LLM with different prompts) anchor on different baselines  some grade leniently, others strictly.

| Field | Value |
|-------|-------|
| **First Paper** | Discussed across surveys (Gu et al. 2024, Li et al. 2024) |
| **Year** | 2024 |
| **Venue** | Various |
| **Mitigation Exists?** | ⬜ **NO dedicated mitigation** |
| **Status** | ★ **GAP: No dedicated mitigation paper exists** |

---

## 34. Overlap Bias

**Definition:** Judge prefers responses with more token overlap with the instruction, confusing lexical similarity with quality.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) OffsetBias (error case analysis) |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ (partial) |
| **Mitigation Papers** | Park et al. (2024) OFFSETBIAS |
| **Status** | Mitigated via debiased data |

---

## 35. Kindness Bias

**Definition:** Judge prefers responses that are polite, agreeable, or express willingness to help, even when those responses contain factual errors.

| Field | Value |
|-------|-------|
| **First Paper** | Park et al. (2024) OffsetBias (error case analysis) |
| **Year** | 2024 |
| **Venue** | Findings of EMNLP 2024 |
| **Mitigation Exists?** | ✅ (partial) |
| **Mitigation Papers** | Park et al. (2024) OFFSETBIAS |
| **Status** | Mitigated via debiased data |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total bias types identified** | **35** |
| Bias types with at least one peer-reviewed mitigation | 12 |
| Bias types with **NO mitigation** | **23** |
| Bias types identified but never formally studied in peer review | 2 (moderation, anchoring) |
| Bias types identified, measured, but never mitigated | 19 (starred above) |

---

## 🎯 Top Research Gaps (Best Entry Points for High School Researchers)

These are biases that have been **identified in published research** but have **zero peer-reviewed mitigation papers**:

### Tier 1: Easy entry (well-defined, small scope)
1. **Family Bias** (Wataoka 2024)  → design a cross-family judge panel or family-aware calibration
2. **Score Rubric Order Bias** (Li 2025)  → propose rubric randomization or order-robust scoring
3. **Score ID Bias** (Li 2025)  → design label-agnostic evaluation
4. **Reference Answer Score Bias** (Li 2025)  → develop reference-robust scoring protocols

### Tier 2: Medium complexity (needs creative approach)
5. **Authority Bias** (Chen 2024)  → citation verification integration for LLM judges
6. **Fallacy Oversight Bias** (Chen 2024)  → fallacy-aware judge prompting
7. **Beauty Bias** (Chen 2024)  → content-vs-style disentanglement
8. **Sentiment Bias** (Ye 2024)  → sentiment-normalized scoring
9. **Bandwagon Effect** (Koo 2024)  → independence-preserving evaluation
10. **Egocentric Bias** (Koo 2024)  → cross-model style calibration
11. **Refinement-Aware Bias** (Ye 2024)  → blind refinement evaluation
12. **Distraction Bias** (Ye 2024)  → relevance-filtered judging

### Tier 3: Higher complexity (broader scope)
13–19. **Rich Content, CoT Bias, Gender Bias, Moderation Bias, Anchoring Bias, Label Bias, Leniency Bias**  these range from partially defined to entirely undefined in peer review.

> **Note:** For biases that also lack a formal accepted **definition** in peer-reviewed literature (moderation, anchoring), there is a double opportunity: define and then mitigate.

---

## Key Survey Papers Referenced

| Paper | Year | Venue | Coverage |
|-------|------|-------|----------|
| Zheng et al.  "Judging LLM-as-a-Judge with MT-Bench" | 2023 | **NeurIPS** | Position, verbosity, self-enhancement |
| Wang et al.  "LLMs are not Fair Evaluators" | 2024 | **ACL** | Position bias + calibration |
| Koo et al.  "Benchmarking Cognitive Biases in LLMs as Evaluators" | 2024 | **Findings of ACL** | 6 cognitive biases |
| Chen et al.  "Humans or LLMs as the Judge? A Study on Judgement Bias" | 2024 | **EMNLP** | Fallacy oversight, authority, beauty |
| Ye et al.  "Justice or Prejudice?" (CALM) | 2024 | **ICLR 2025** | **12 biases** (most comprehensive single taxonomy) |
| Park et al.  "OffsetBias" | 2024 | **Findings of EMNLP** | 6 biases + EVALBIASBENCH + OFFSETBIAS |
| Wataoka et al.  "Self-Preference Bias in LLM-as-a-Judge" | 2024 | **NeurIPS SafeGenAI** | Self-preference metric + family bias |
| Panickssery et al.  "LLM Evaluators Recognize and Favor Their Own Generations" | 2024 | **NeurIPS** | Self-precision + self-recognition |
| Li et al.  "LLMs-as-Judges: A Comprehensive Survey" | 2024 | arXiv | Survey |
| Gu et al.  "A Survey on LLM-as-a-Judge" | 2024 | arXiv / The Innovation | **Survey** |
| Shi et al.  "Judging the Judges: A Systematic Study of Position Bias" | 2025 | **AACL/IJCNLP** | Position bias (deep dive) |
| Li et al.  "Evaluating Scoring Bias in LLM-as-a-Judge" | 2025 | arXiv | 3 scoring biases |
| Liu et al.  "Assistant-Guided Mitigation of Teacher Preference Bias" | 2025 | **Findings of EMNLP** | Teacher preference bias |
| Gao et al.  "Evaluating and Mitigating LLM-as-a-judge Bias in Communication Systems" | 2026 | arXiv | 11 biases in pointwise setting |
| Yang et al.  "Quantifying and Mitigating Self-Preference Bias of LLM Judges" | 2026 | arXiv | Self-preference mitigation |
| Soumik  "A Systematic Evaluation of Bias Mitigation Strategies" | 2026 | **TMLR** | 9 debiasing strategies compared |
| Malberg et al.  "A Comprehensive Evaluation of Cognitive Biases in LLMs" | 2025 | NLP4DH | 30 cognitive biases (not all judge-specific) |

---

## Search Methodology

This inventory was compiled via iterative searches across:
- **arXiv** (cs.CL, cs.AI, cs.LG)
- **ACL Anthology** (ACL, EMNLP, Findings, AACL/IJCNLP, COLING)
- **Semantic Scholar**
- **NeurIPS proceedings** (2023, 2024, 2025)
- **ICLR proceedings** (2024, 2025)
- **Google Scholar** for cross-referencing

Search terms used:
- `"LLM-as-a-judge" bias` • `position bias LLM judge` • `verbosity bias LLM judge`
- `self-preference bias LLM judge` • `cognitive bias LLM evaluator`
- `"LLM judge" bias taxonomy` • `bias mitigation LLM-as-a-judge`
- `"Justice or Prejudice" LLM bias` • `OffsetBias` • `scoring bias LLM judge`
- `site:aclanthology.org "bias" "LLM-as-a-judge"`
- `site:arxiv.org "LLM-as-a-judge" bias mitigation`

---

*Generated as part of an exhaustive literature audit for high school AI/ML research students. Last updated: July 2026.*

Review cycle: July 2026
