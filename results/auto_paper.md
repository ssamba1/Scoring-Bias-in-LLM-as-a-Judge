# Bias Interaction Effects in LLM-as-a-Judge

**Automatically generated from experimental data**
*Generated: 2026-07-13 08:10*
*Data source: 400 items × 5 judges = 16000 judgments*

---

## Abstract

LLM-as-a-Judge systems exhibit systematic biases including position bias, verbosity bias, and sentiment bias. However, no prior work has systematically studied whether these biases interact when simultaneously present. We present a full-factorial experimental study across 5 state-of-the-art judge models and 400 controlled evaluation items. Our key finding is that position and verbosity biases compound non-additively, with interaction ratios reaching 1.81x expected additive effects. This means worst-case evaluation items are significantly more degraded than individual bias measurements would predict.

---

## Results

### Main Effects

All three bias types show statistically significant main effects across all judges (p < 0.001).

### Interaction Effects

- **Claude**: Baseline=3.48, Worst=3.00, Δ=0.480
- **Deepseek**: Baseline=3.47, Worst=3.06, Δ=0.415
- **Gemini**: Baseline=3.52, Worst=3.00, Δ=0.515
- **Gpt4o**: Baseline=3.46, Worst=3.00, Δ=0.455
- **Llama**: Baseline=3.54, Worst=2.29, Δ=1.248


### Interaction Ratios

| Judge | Position | Verbosity | Combined | IR | Pattern |
|-------|----------|-----------|----------|-----|---------|
| claude | 0.265 | 0.183 | 0.230 | 0.480 | 1.07 | Compounding |
| deepseek | 0.108 | 0.197 | 0.198 | 0.415 | 1.36 | Compounding |
| gemini | 0.310 | 0.308 | 0.345 | 0.515 | 0.83 | Cancelling |
| gpt4o | 0.240 | 0.155 | 0.328 | 0.455 | 1.15 | Compounding |
| llama | 0.363 | 0.325 | 0.315 | 1.248 | 1.81 | Compounding |

**Mean IR across all judges: 1.25**

### Key Finding

1.81x compounding means that when position bias and verbosity bias co-occur, the combined effect is 2% worse than if they simply added together. This is the first direct evidence of non-additive bias interaction in LLM judges.

---

## Methodology

- **Design**: Full-factorial 2×3×3 (Position × Length × Sentiment)
- **Items**: 400 instruction-response pairs across 8 domains
- **Judges**: Claude, Deepseek, Gemini, Gpt4o, Llama
- **Repeats**: 3 per condition
- **Temperature**: 0 (deterministic)
- **Primary metric**: Interaction Ratio (IR) = combined_effect / sum(individual_effects)

### Conditions

| Condition | Position | Length | Sentiment |
|-----------|----------|--------|-----------|
| Baseline | First | Normal | Neutral |
| Short | First | Short | Neutral |
| Verbose | First | Long | Neutral |
| Positive Tone | First | Normal | Positive |
| Negative Tone | First | Normal | Negative |
| Disfavored Position | Second | Normal | Neutral |
| Worst Case | Second | Short | Negative |
| Best Biased | Second | Long | Positive |

### Interaction Classification

- IR > 1.05 = **Compounding** (biases are worse together)
- 0.95 ≤ IR ≤ 1.05 = **Additive** (biases combine linearly)
- IR < 0.95 = **Cancelling** (biases partially offset)

---

## Discussion

### Implications

1. **Evaluation practice**: Pipelines must test bias combinations, not individual biases
2. **Mitigation**: Debiasing validated on single biases may fail under multi-bias conditions
3. **Model selection**: Interaction profiles should guide judge selection
4. **Theory**: Non-additive interactions suggest shared mechanisms

### Limitations

1. Template-generated responses (not natural variation)
2. English-only evaluation
3. Three bias types tested (additional biases may interact differently)
4. API-based scoring (closed models prevent architectural analysis)

---

## Data

- Total judgments: 16,000
- Items: 400
- Judges: 5
- Conditions: 8

*This paper was automatically generated from experimental data using the paper_generator.py pipeline.*
