# Paper Notes — Batch 2 (Extended Reading)

## Paper 13: Wang et al. 2023 — "Large Language Models are not Fair Evaluators"
**arXiv:2305.17926 · ACL 2024 · cited 1039+**

### Key Details
- **First to systematically demonstrate position bias** in LLM-as-a-Judge
- Vicuna-13B beat ChatGPT on 66/80 queries just by manipulating response order
- Proposed 3 calibration strategies:
  1. **Multiple Evidence Calibration (MEC):** Generate evaluation evidence before scoring
  2. **Balanced Position Calibration (BPC):** Aggregate scores across all position orders
  3. **Human-in-the-Loop Calibration (HLC):** Use entropy to detect hard cases, defer to humans
- Released FairEval code and human annotations
- **Key quote:** "The quality ranking of candidate responses can be easily hacked by simply altering their order of appearance"

### Relevance
- Foundational position bias paper
- BPC is the standard mitigation (swap-and-average)
- Does NOT address scoring bias or bias interactions

## Paper 14: Shi et al. 2025 — "Judging the Judges: A Systematic Study of Position Bias"
**arXiv:2406.07791 · AACL-IJCNLP 2025 · cited 273**

### Key Details
- **15 judges × ~150,000 evaluation instances** — largest position bias study
- 3 metrics: repetition stability (RS), position consistency (PC), preference fairness (PF)
- Factors: Judge-Level, Candidate-Level, Task-Level
- **Key findings:**
  - Position bias is NOT random chance
  - Varies significantly across judges and tasks
  - Weakly influenced by prompt length
  - Strongly affected by quality gap between solutions
- **Agreement analysis:** Shows distribution of judging difficulty

### Relevance
- Most comprehensive position bias study
- Provides effect sizes and methodology we can reference
- Does NOT study bias interactions

## Paper 15: Park et al. 2024 — "OffsetBias: Leveraging Debiased Data for Tuning Evaluators"
**Findings of EMNLP 2024**

### Key Details
- Identified 6 bias types: length bias, concreteness bias, empty reference bias, etc.
- Proposed OFFSETBIAS: training data that improves judge robustness
- **Key finding:** Fine-tuning on debiased data reduces multiple biases simultaneously
- Released EVALBIASBENCH benchmark

### Relevance
- Mitigation approach (training-based rather than prompt-based)
- Does NOT address scoring bias or bias interactions
- Shows that multi-bias mitigation is possible through training

## Paper 16: Wataoka et al. 2024 — "Self-Preference Bias in LLM-as-a-Judge"
**NeurIPS SafeGenAI Workshop 2024**

### Key Details
- Formalized self-preference bias metric
- Found GPT-4 exhibits measurable self-preference
- Also identified **family bias** (preferring same-model-family outputs)
- **Family bias has NO dedicated mitigation** (gap)

### Relevance
- Source for family bias gap (23 of 35 bias types have no mitigation)
- Self-preference is well-studied; family bias is untouched

## Paper 17: Panickssery et al. 2024 — "LLM Evaluators Recognize and Favor Their Own Generations"
**NeurIPS 2024**

### Key Details
- Causal study: LLM judges recognize their own outputs and rate them higher
- De-identification (hiding model identity) partially mitigates
- **Key finding:** Self-recognition → self-preference causal link
- Judges can identify their own outputs at above-chance rates

### Relevance
- Shows bias can be causally traced (methodology applicable to scoring bias)
- Proves de-identification as a mitigation strategy
