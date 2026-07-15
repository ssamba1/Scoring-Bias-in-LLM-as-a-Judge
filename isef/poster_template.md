# ISEF Poster Template — 36×48 inches

## Three-Panel Layout

---

### TOP BANNER (Full Width, ~12 inches tall)

**Title: Scoring Bias in LLM-as-a-Judge Models — A 22-Model Landscape with Base-Instruct Comparison**

**Researcher:** Sricharan Samba, South Forsyth High School

**Category:** Systems Software

**[QR Code]** → github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

---

### LEFT PANEL (~12 inches wide)

#### Introduction

Large language models (LLMs) are increasingly used as automated judges to evaluate AI systems — powering benchmarks like MT-Bench, serving as reward models in RLHF, and automating evaluation in production pipelines. However, these judges exhibit over 35 documented bias types.

**The Open Problem:** Do these biases come from pre-training or instruction tuning?

#### Research Questions

1. Does instruction tuning change scoring bias magnitude?
2. Is the direction consistent across bias types (format vs. content)?
3. Is the direction consistent across model families?
4. Do training methods (SFT, DPO, RLHF) modulate the effect?

#### Hypotheses

- **H1:** Format bias decreases; content bias increases
- **H2:** Differential effect consistent across families
- **H3:** RLHF > SFT+DPO in differential effect magnitude

---

### MIDDLE PANEL (~24 inches wide)

#### Methods

**Model Landscape:** 31 model variants tested across 15 families
- 9 families with base+instruct pairs (primary analysis)
- 22 instruct-only models (breadth)

**Three Scoring Bias Probes** (Li et al. framework):
| Probe | Control | Biased Variants |
|-------|---------|-----------------|
| Rubric Order | 1=worst, 5=best | 1=best, 5=worst; random labels |
| Score ID | Numeric (1–5) | Letter (A–E); Descriptive (Poor–Excellent) |
| Reference Answer | No exemplar | Good exemplar; Poor exemplar |

**Scale:** 50 items × 5 domains × 3 probes × 3 variants × 3 repeats = **54,000 judgments**

#### Key Results

**Figure 1: Format Bias Decreases After Instruction Tuning**
```
Bias Type      Base Avg    Instruct Avg    Change
Rubric Order    1.43          0.72         −50% 📉
Score ID        0.95          0.15         −84% 📉
```

**Figure 2: Content Bias Increases in Larger RLHF Models**
```
Model              Base Δ    Instruct Δ    Change
Llama-3.1-8B        0.12       1.70       +1.58 🚨
Llama-3.2-3B        0.50       0.70       +0.20
Qwen2.5-0.5B        1.40       0.80       −0.60
StableLM-2-1.6B     1.60       0.80       −0.80
```

**Figure 3: 22-Model Bias Landscape**
```
Bias Probe       Mean Δ    Range        Most Biased        Least Biased
Score ID          0.68     0.00–1.80   Hermes-3-70B (1.80)  Qwen3-14B (0.00)
Rubric Order      0.56     0.10–1.50   MythoMax-13B (1.50) GLM-4.7 (0.10)
Ref Answer        0.41     0.00–1.00   Lunaris-8B (1.00)   Qwen3-8B (0.00)
```

**Figure 4: Attention Evidence — Format Efficiency Hypothesis**
- Format token attention: 23.7% → 20.8% after instruction tuning
- Content token attention: 1.06% → 1.09% (unchanged)
- Supports: format parsing becomes more efficient, not that attention redistributes to content

---

### RIGHT PANEL (~12 inches wide)

#### Conclusions

1. **Scoring bias is modulated by instruction tuning** — not inherent to pre-training ✓
2. **Format robustness improves** naturally through instruction tuning (7/9 families)
3. **Content sensitivity increases** in larger (3B+) RLHF-trained models
4. **Training method matters** — SFT+DPO (Mistral 7B) shows a different pattern
5. **Score ID bias** is the most problematic overall (Δ = 0.68 average)

#### Practical Implications

- **For AI Practitioners:** Always test multiple scoring formats; use numeric labels by default
- **For Benchmark Designers:** Report separate format and content bias scores, not a single metric
- **For Model Developers:** Format robustness can be improved without increasing content sensitivity
- **For Safety Evaluation:** Worst-case bias may be systematically underestimated

#### Alternative Explanations Examined

| Hypothesis | Evidence |
|------------|----------|
| Global scoring shift? | ❌ Biases don't move same direction |
| Single-family dominance? | ❌ Pattern persists without any single family |
| Parser artifacts? | ❌ Numeric/letter variants confirm independently |

#### Future Work

- Replicate with N ≥ 12 model families for statistical significance
- Test IIAR predictions: monotonicity, prompt length independence
- Develop mitigation: multi-model ensembling and calibration
- Cross-lingual evaluation (currently English-only)

#### Acknowledgments

Research mentor guidance. AI tools assisted in code generation and drafting. All experimental design, analysis, and interpretation by the author.

---

### QR CODE / DATA ACCESS

**Scan for:**
- Full paper (PDF)
- Code repository
- Interactive data explorer
- Docker reproduction
- DOI: 10.5281/zenodo.21361920

**GitHub:** github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
