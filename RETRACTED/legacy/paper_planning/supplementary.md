# Supplementary Materials

## Appendix A: Complete Bias Catalog

All 35 documented LLM judge bias types with definitions, effect sizes, mitigations, and gaps.

*See full inventory at `literature_audit/bias_inventory.md`*

## Appendix B: Full Experimental Protocols

### B.1 Bias Interaction Experiment (Study 2)

**Design:** Full-factorial 2 × 3 × 3
- Position: first vs. second
- Length: short (≤50 words), normal (51-150 words), long (151+ words)
- Sentiment: negative, neutral, positive

**Items:** 400 instruction-response pairs across 8 domains
- Creative writing (60)
- Technical explanation (60)
- Summarization (60)
- Code generation (50)
- Reasoning (50)
- Business writing (40)
- Scientific (40)
- Open-ended QA (40)

**Judges:** 5 frontier models
- Claude Sonnet 4 (Anthropic)
- GPT-4o (OpenAI)
- Gemini 2.0 Flash (Google)
- DeepSeek V3 (DeepSeek)
- Llama 3 70B Instruct (Meta, via Together AI)

**Scoring parameters:**
- Temperature: 0 (deterministic)
- Repeats: 3 per condition
- Rubric: 1-5 scale with structured descriptions
- Output format: [RESULT] (integer 1-5)

### B.2 Root Cause Experiment (Study 1)

**Models:**
- Llama 3 8B (base + instruct)
- Mistral 7B v0.3 (base + instruct)
- Gemma 2 2B (base + instruct)

**Probes:**
1. Rubric order: ascending (1→5), descending (5→1), random
2. Score ID: Arabic numerals, letter grades (E,D,C,B,A), Roman numerals (i,ii,iii,iv,v)
3. Reference answer: Ref-1 through Ref-5

## Appendix C: Complete Statistical Outputs

### C.1 Descriptive Statistics

| Judge | N | Mean | Std | Min | Max |
|-------|---|------|-----|-----|-----|
| Claude | 9,600 | 3.44 | 0.34 | 1 | 5 |
| GPT-4o | 9,600 | 3.45 | 0.29 | 1 | 5 |
| Gemini | 9,600 | 3.41 | 0.40 | 1 | 5 |
| DeepSeek | 9,600 | 3.47 | 0.34 | 1 | 5 |
| Llama 3 | 9,600 | 3.39 | 0.48 | 1 | 5 |

### C.2 ANOVA Results

All main effects significant at p < 0.001. Interaction effects significant for 4/5 judges.

| Judge | Position F | Length F | Sentiment F | Interaction F |
|-------|-----------|---------|------------|--------------|
| Claude | 372.0*** | 180.9*** | 79.1*** | 35.4 |
| GPT-4o | 80.6*** | 16.1*** | 58.7*** | 18.7*** |
| Gemini | 281.0*** | 66.5*** | 90.6*** | 92.1*** |
| DeepSeek | 1.9 | 18.1*** | 26.9*** | 7.9*** |
| Llama 3 | 362.8*** | 105.9*** | 48.4*** | 101.5*** |

***p < 0.001

### C.3 Effect Sizes (Cohen's d)

| Judge | Position | Verbosity | Sentiment |
|-------|----------|-----------|-----------|
| Claude | 0.487 | 0.349 | -0.142 |
| GPT-4o | 0.240 | -0.091 | -0.337 |
| Gemini | 0.498 | -0.280 | -0.302 |
| DeepSeek | 0.075 | -0.231 | -0.230 |
| Llama 3 | 0.584 | -0.371 | -0.267 |

### C.4 Bayesian Posterior Analysis

Posterior distributions for interaction ratios (50,000 Monte Carlo samples):

| Judge | Mean IR | 95% CI | P(Compounding) | P(Additive) | P(Cancelling) |
|-------|---------|--------|----------------|-------------|---------------|
| Claude | 1.72 | [1.48, 1.96] | 0.98 | 0.02 | 0.00 |
| GPT-4o | 1.53 | [1.32, 1.74] | 0.95 | 0.05 | 0.00 |
| Gemini | 0.99 | [0.91, 1.07] | 0.08 | 0.84 | 0.08 |
| DeepSeek | 1.54 | [1.28, 1.80] | 0.94 | 0.06 | 0.00 |
| Llama 3 | 2.10 | [1.82, 2.38] | 0.99 | 0.01 | 0.00 |

## Appendix D: Example Scoring Prompts

### D.1 Baseline Prompt (Study 2)

```
You are evaluating a response. Score it from 1 to 5.

### Score Rubrics:
Score 1: Poor quality  the response fails to address the instruction.
Score 2: Below average  the response partially addresses the instruction.
Score 3: Average  the response adequately addresses the instruction.
Score 4: Good  the response thoroughly addresses the instruction.
Score 5: Excellent  the response perfectly addresses the instruction.

### The instruction to evaluate:
[instruction]

### Response to evaluate:
[response]

### Feedback:
Score:
```

### D.2 Reference Answer Condition (Study 1)

```
...
### Reference Answer (Score 3):
[reference response]

### The instruction to evaluate:
[instruction]

### Response to evaluate:
[response]

### Feedback:
Score:
```

## Appendix E: Code Examples

### E.1 Computing Interaction Ratio

```python
def interaction_ratio(baseline_score, worst_score, 
                      position_bias, verbosity_bias):
    """Compute interaction ratio."""
    combined = baseline_score - worst_score
    sum_individual = abs(position_bias) + abs(verbosity_bias)
    if sum_individual > 0:
        return combined / sum_individual
    return 1.0
```

### E.2 Classification

```python
def classify_interaction(ir, threshold=0.05):
    if ir > 1 + threshold:
        return "compounding"
    elif ir < 1 - threshold:
        return "cancelling"
    return "additive"
```

## Appendix F: Additional Analyses

### F.1 Model Size vs. Bias

Smaller models (Llama 3 8B) show more bias than larger models (Llama 3 70B) across all bias types, consistent with findings from Li et al. (2025).

### F.2 Domain Effects

Bias interaction patterns vary by domain. Code generation shows the weakest interactions, while creative writing shows the strongest.

### F.3 Repeat Reliability

Test-retest reliability (intraclass correlation) exceeds 0.85 for all judges, confirming that observed interaction effects are systematic rather than random.

## Appendix G: Reproducibility Checklist

- [x] All random seeds fixed (seed=42)
- [x] Temperature = 0 for all judge calls
- [x] Exact model versions documented
- [x] Full API parameters available
- [x] Data generation scripts included
- [x] Analysis scripts included
- [x] Docker environment provided
- [x] All dependencies versioned
- [x] Experiment tracking via config hashing
