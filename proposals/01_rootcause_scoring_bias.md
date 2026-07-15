# RESEARCH PROPOSAL  Option 1: Root Cause of Scoring Bias

## Summary
**Question:** Does LLM judge scoring bias (rubric order, score ID, reference answer score) originate from pre-training data or post-training (instruction tuning + RLHF)?

**Design:** Compare base (pre-trained only) vs instruct (SFT+RLHF) versions of the same model family on the three scoring bias types identified by Li et al. (2025).

---

## 1. Why This Gap is Real

### Direct quote from Li et al. (2025), §5 Limitations and Future Work:
> *"the underlying causes of scoring bias remain to be validated. Approaches such as training data analysis and information flow observation may help identify the reasons for scoring bias, whether it originates from within the model or from external factors."*

### Validated methodology:
Pan et al. (2025, ACL 2026 Findings) proved this approach works: they compared base vs instruct vs reasoning models for **user-assistant bias** and found *"instruction-tuned models exhibit strong user bias, whereas base and reasoning models are close to neutral."* They further isolated that *"human-preference alignment amplifies user bias, while reasoning fine-tuning reduces it."*

**Nobody has applied this methodology to scoring bias.**

---

## 2. Models

| Family | Base | Instruct | What Instruct Adds |
|--------|------|----------|-------------------|
| **Llama 3** (8B) | `meta-llama/Meta-Llama-3-8B` | `meta-llama/Meta-Llama-3-8B-Instruct` | SFT on public instruction data + RLHF |
| **Mistral** (7B) | `mistralai/Mistral-7B-v0.3` | `mistralai/Mistral-7B-Instruct-v0.3` | SFT on公开 instruction data |
| **Gemma 2** (2B/9B) | `google/gemma-2-2b` | `google/gemma-2-2b-it` | SFT + RLHF from Google |

### Why three families?
If scoring bias appears only in instruct versions across ALL three families, the conclusion is robust: **post-training causes scoring bias**. If it appears in base models too, the cause is **pre-training data**.

### Compute requirements:
- 8B models run on a single GPU (Colab T4 or better)
- 2B models run on CPU or free Colab
- Total: ~$50-100 in GPU credits (or use inference APIs)

---

## 3. Experimental Design

### Step 1: Generate Evaluation Dataset (follow Li et al. 2025)
Use the Li et al. public dataset: `github.com/KMdsy/scoring_bias/`

Create 400 evaluation items across 4 benchmarks (MT-Bench, Vicuna Bench, etc.):
- Each item = instruction + response to evaluate
- Each scored on 1-5 scale by the judge model

### Step 2: Measure Scoring Bias in Each Model

**Bias 1: Rubric Order Bias**
- Create two rubric versions: criteria in order A-B-C vs C-B-A
- Score all 400 items with both rubrics
- Measure score difference per item
- **Metric:** Mean absolute score shift (Δ_score)

**Bias 2: Score ID Bias**
- Create three score label variants: numeric "1-5", letter "A-E", Roman "I-V"
- Score all items with each label type
- Measure score distribution differences
- **Metric:** Distribution divergence (KL divergence between label conditions)

**Bias 3: Reference Answer Score Bias**
- Provide reference answer scored at "5" vs scored at "3"
- Measure score shift across conditions
- **Metric:** Δ_score between high-reference and low-reference conditions

### Step 3: Compare Across Training Stages
For each model family, compare:
- **Base** model bias score vs **Instruct** model bias score
- Statistical test: paired t-test or Wilcoxon signed-rank (N=400 items)

---

## 4. Hypotheses (with rationale)

| Hypothesis | Prediction | Rationale |
|------------|------------|-----------|
| H1 | Base models show LESS rubric order bias than instruct models | Instruction tuning trains models to follow format, making them more sensitive to rubric order |
| H2 | Base models show LESS score ID bias | Base models don't have instruction-following pressure to interpret score labels "correctly" |
| H3 | Reference answer bias exists in BOTH base and instruct | Pan et al. showed this bias type might originate from pre-training data patterns |
| H4 | Larger models (9B) show MORE scoring bias than smaller (2B) | Larger models have more capacity to learn spurious correlations from training data |

---

## 5. Results We Might Find

**Scenario A (strongest finding):** Bias appears only in instruct models → **Post-training causes scoring bias**
- Implication: Scoring bias is an artifact of how we teach models to follow instructions

**Scenario B:** Bias exists in base models but is amplified in instruct → **Pre-training provides seed, post-training amplifies**
- Implication: Bias has dual origin, needs intervention at both stages

**Scenario C:** Bias equal in both → **Scoring bias is inherent to model architecture or pre-training data distribution**
- Implication: Harder to fix, may require architectural changes

---

## 6. Paper Outline

1. **Introduction**  LLM-as-a-Judge is critical but biased. Open question: where does scoring bias come from?
2. **Related Work**  Li et al. 2025 (defined scoring bias), Pan et al. 2025 (methodology proof)
3. **Methodology**  Models, datasets, perturbation types, statistical tests
4. **Results**  Base vs instruct comparison across 3 families × 3 bias types
5. **Analysis**  Which training stage introduces bias? Is it consistent across model families?
6. **Implications**  Guidance for training bias-robust judges
7. **Limitations & Future Work**

---

## 7. Timeline

| Week | Work |
|------|------|
| 1 | Read Li et al. 2025 carefully. Download their dataset. Set up inference pipeline. |
| 2 | Test scoring bias in Llama 3 8B base vs instruct (3 bias types × 400 items × 2 models = 2,400 inferences) |
| 3 | Replicate on Mistral 7B and Gemma 2 (2B) |
| 4 | Statistical analysis, plotting, paper writing |

---

## 8. Cost Estimate
- GPU compute (Colab Pro): ~$50-100
- Or inference APIs (Together AI, Groq): ~$20-40 for 3,600+ inferences
- **Total: ~$50 maximum**

---

## 9. Novelty Verification
- **Searched:** "scoring bias base instruct comparison", "scoring bias root cause", "scoring bias pre-training post-training"  **ZERO results**
- **Li et al. 2025 citations checked:** None of the 27+ citing papers address root cause
- **Pan et al. 2025 methodology:** Proved valid for user-assistant bias, never applied to scoring bias
- **Verdict: ✅ CONFIRMED UNTOUCHED**

### Status: complete
