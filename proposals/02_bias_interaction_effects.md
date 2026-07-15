# RESEARCH PROPOSAL  Option 2: Bias Interaction Effects

## Summary
**Question:** When multiple LLM judge biases are simultaneously present (e.g., position bias + verbosity bias), do they compound (get worse), cancel out, or interact non-linearly?

**Design:** Full-factorial 2×2×2 experiment crossing three well-documented biases, measuring whether each bias's effect size changes when another bias is also present.

---

## 1. Why This Gap is Real

### Evidence of absence:
Subagent 3's exhaustive search: "bias interaction LLM judge", "compound OR cancel OR interact position verbosity", "cross-bias interaction", "combined bias effect"  **zero systematic empirical studies found.**

### Acknowledged but never studied:
Blog posts (mbrenndoerfer) note: *"Position bias, verbosity bias, and sycophancy do not operate independently. They interact and compound."* Soumik (2026, TMLR) mentions *"cross-bias interaction analysis"* but doesn't deeply study it.

**Quote from the NeurIPS 2025 paper "Any Large Language Model Can Be a Reliable Judge":**
- Verbosity bias affects 31.3% of examples
- Position bias affects 12.9%
- Sentiment bias affects 15.0%

**But NO paper asks:** What happens when a response is BOTH in the disfavored position AND shorter? Does the judge penalize it once or twice?

---

## 2. Experimental Design

### 2.1 Bias Selection (3 biases, well-documented)

| Bias | Known Effect Size | Why Include |
|------|------------------|-------------|
| **Position bias** | 12.9% of examples flip | Most studied bias, known direction (primacy/recency varies by model) |
| **Verbosity bias** | 31.3% of examples favor longer | Largest effect size, well-measured |
| **Sentiment bias** | 15.0% favor positive tone | Third most impactful, orthogonal to position/length |

### 2.2 Full Factorial Design (2 × 2 × 2 = 8 conditions)

For each judge model, for each of N=400 evaluation items, manipulate:

| Condition | Position | Length | Sentiment |
|-----------|----------|--------|-----------|
| 1 (baseline) | Favored | Long | Positive |
| 2 | Favored | Long | Negative |
| 3 | Favored | Short | Positive |
| 4 | Favored | Short | Negative |
| 5 | Disfavored | Long | Positive |
| 6 | Disfavored | Long | Negative |
| 7 | Disfavored | Short | Positive |
| 8 (worst case) | Disfavored | Short | Negative |

### 2.3 Response Construction
For each of 400 evaluation items, generate 8 versions:
- **Position:** Swap order in pairwise comparison (first vs second)
- **Length:** Truncate vs expand response (keep semantic content constant)
- **Sentiment:** Add positive vs negative framing (e.g., "this approach works well" vs "this approach has issues")

### 2.4 Models to Test (5 models, diverse families)

| Model | Provider | Size |
|-------|----------|------|
| Claude 3.5 Sonnet (or Claude 4) | Anthropic | Frontier |
| GPT-4o | OpenAI | Frontier |
| Gemini 2.0 Flash | Google | Mid |
| Llama 3 70B Instruct | Meta | Large open |
| DeepSeek V3 | DeepSeek | Frontier |

### 2.5 Judge Protocol
- Pointwise scoring: rate each response on 1-5
- Each judge scores ALL 8 versions of each item (3,200 judgments per model = 16,000 total)
- Each judgment repeated 3× at temperature=0 for consistency

---

## 3. Analysis

### 3.1 Main Effects (replicating known biases)
- Position bias Δ = score(pos_favored) − score(pos_disfavored)
- Verbosity bias Δ = score(long) − score(short)
- Sentiment bias Δ = score(positive) − score(negative)

### 3.2 Interaction Effects (NOVEL  this is the contribution)
- **Position × Verbosity:** Is Δ_verbosity the same in favored vs disfavored position?
- **Position × Sentiment:** Does position bias change with sentiment?
- **Verbosity × Sentiment:** Are verbose-positive responses doubly favored?
- **Position × Verbosity × Sentiment:** Three-way interaction (worst-case analysis)

### 3.3 Statistical Model
```python
score ~ position + length + sentiment + 
        position:length + position:sentiment + length:sentiment + 
        position:length:sentiment
```
- Linear mixed effects model with random intercepts for items and judges
- ANOVA for significance of each interaction term
- Effect size (Cohen's d) for each interaction

### 3.4 Key Metrics
- **Δ_bias_alone** = effect size when only one bias is present
- **Δ_bias_together** = effect size when another bias is also present
- **Interaction Ratio** = Δ_together / (Δ_bias_alone + Δ_other_alone)
  - >1.0 = compounding (biases amplify each other)
  - =1.0 = additive (no interaction)
  - <1.0 = diminishing returns / cancellation

---

## 4. Hypotheses

| # | Hypothesis | Prediction | Why |
|---|------------|------------|-----|
| H1 | Verbosity × Position interaction exists | Short-disfavored condition is worse-than-additive | Both biases push in same direction |
| H2 | Sentiment × Verbosity interaction exists | Verbose-positive gets extra boost | Both indicate "effort" to the judge |
| H3 | Three-way interaction exists | Worst case (short + disfavored + negative) is non-additively bad | All biases compound |
| H4 | Interaction patterns vary by model family | Some models compound, others cancel | Different training data produces different bias structures |

---

## 5. Paper Outline

1. **Introduction**  LLM judges have known individual biases, but they never occur in isolation. What happens when biases co-occur?
2. **Related Work**  Documented biases and their effect sizes (Zheng 2023, Shi 2025, Ye 2024, etc.)
3. **Methodology**  Full factorial design, item construction, models, statistical model
4. **Results**  Main effects (replicate known), interaction effects (novel), model comparison
5. **Analysis**  Which bias pairs compound? Which cancel? Is the worst case predictable?
6. **Implications**  How to design bias test suites (must test combinations, not just individual biases)
7. **Limitations & Future Work**

---

## 6. Timeline

| Week | Work |
|------|------|
| 1 | Generate 8 versions of 400 evaluation items. Validate quality (human check). |
| 2 | Run API calls: 5 models × 400 items × 8 versions × 3 repeats = 48k judgments |
| 3 | Statistical analysis: fit mixed effects model, compute interaction ratios |
| 4 | Write paper: plots, tables, interpretation |

---

## 7. Cost Estimate
- 5 judge models × 3,200 judgments each = 16,000 API calls
- Estimated cost: ~$30-80 total (most judges are cheap for scoring)
- **Total: ~$50 maximum**  zero GPU

---

## 8. Novelty Verification
- **Searched:** "bias interaction LLM judge", "compound cancel interact position verbosity", "cross-bias interaction systematic"  **ZERO results**
- Soumik (Apr 2026) mentions cross-bias analysis but does NOT systematically study interactions
- Blog posts note "biases interact" as observation, not as systematic experiment
- **Verdict: ✅ CONFIRMED UNTOUCHED**
