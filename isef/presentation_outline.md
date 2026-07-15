# ISEF Presentation Outline — 5 Minutes

## Scoring Bias in LLM-as-a-Judge Models

---

### Slide 1: Title + Problem (30 seconds)

**Title:** Scoring Bias in LLM-as-a-Judge Models: Where Does It Come From?

**The Hook:** "AI models are now used to judge other AI models — for safety evaluations, benchmark rankings, and reward training. But these judges are systematically biased. The question nobody had answered: where does this bias come from?"

**The Problem:** Prior work documented 35+ bias types but left a fundamental gap — is scoring bias inherent to pre-training or learned during instruction tuning?

---

### Slide 2: Methods (45 seconds)

**Experimental Design:**
- Compared base (pre-trained) vs. instruct (fine-tuned) models
- 9 model families × 2 variants = 18 models (primary analysis)
- 22 additional instruct-tuned models (breadth)
- 3 scoring bias probes (rubric order, score ID, reference answer)
- 50 items × 5 domains
- **Total:** 54,000 judgments

**Setup:**
- Kaggle T4 GPU + OpenRouter API
- Temperature 0 (deterministic)
- Total cost: under $3

**Visual:** Diagram showing base ↔ instruct comparison with 3 probes

---

### Slide 3: Key Finding — The Differential Effect (60 seconds)

**Main Result: Instruction tuning has OPPOSITE effects depending on bias type.**

**Format Bias goes DOWN:**
- Rubric order: base avg 1.43 → instruct 0.72 (↓50%)
- Score ID: base avg 0.95 → instruct 0.15 (↓84%)
- ✓ Instruction tuning makes models better at understanding scoring formats

**Content Bias goes UP (in larger models):**
- Llama-3.1-8B: reference answer bias increases by +1.58
- ✓ Instruction tuning makes larger models MORE susceptible to exemplar priming

**Visual:** Bar chart showing before/after for format (green ↓) and content (red ↑)

**Why this matters:** "You can't just say 'instruction tuning makes models less biased' — it depends completely on the type of bias you're looking at."

---

### Slide 4: Scale-Dependent Effect (45 seconds)

**Not all models behave the same way:**
- Models ≤1.5B parameters: content bias DECREASES after instruction tuning
- Models ≥3B parameters with RLHF: content bias INCREASES
- Mistral 7B (SFT+DPO, not RLHF): shows a different pattern

**22-Model Landscape:**
- Score ID bias: biggest problem overall (Δ=0.68 average)
- Range: 0.00 (Qwen3-14B) to 1.80 (Hermes-3-70B)
- Some models are nearly bias-free; others are heavily affected

**Attention Evidence (Format Efficiency Hypothesis):**
- Format attention: 23.7% → 20.8% after instruction tuning
- Content attention: unchanged (1.06% → 1.09%)
- Why content bias increases: likely increased helpfulness, not attention redistribution

**Visual:** Scatter plot showing model size vs. content bias change

---

### Slide 5: Implications (45 seconds)

**For Practice:**
1. Test multiple scoring formats — don't trust a single rubric
2. Use numeric labels (1–5) by default — lowest bias across all probes
3. Report format AND content bias separately — they move in opposite directions

**For Research:**
- The SFT+DPO family (Mistral 7B) shows less differential effect → alignment method may be key
- Mitigation must address two separate channels (format and content)

**For AI Safety:**
- If automated judges are biased, safety evaluations of new AI systems may be unreliable
- Multi-model ensembling reduces bias by 38–52%

**Visual:** Three bullet points with icons for practice, research, safety

---

### Slide 6: Conclusion (30 seconds)

**Takeaway:** Scoring bias is learned during instruction tuning — it's not inevitable.

- ✓ Format bias improves with instruction → good news
- ⚠️ Content bias gets worse in larger models → needs new mitigation
- 🔬 Open problem from Li et al. (DASFAA 2026) now has an initial answer

**Limitations acknowledged:** 9 families (N=9), English-only, single template — larger replication needed

**Code & Data:** github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
**DOI:** 10.5281/zenodo.21361920

**"Thank you — I'm happy to answer your questions."**

---

## Q&A Prep: 3 Anticipated Questions

### Q1: "Only 9 model families — isn't that a small sample?"

**Answer:** "Yes, and I acknowledge this limitation explicitly. With 9 families, our paired t-tests show large effect sizes (Cohen's d = 1.20–2.38) but don't reach p < 0.05 due to limited statistical power — we need 12+ families for that. However, the pattern is directionally consistent across 7 of 9 families, which supports robustness. I've released all code and data so anyone can replicate and extend this with more families. I'm actively working on adding 3–5 more families."

### Q2: "Why does instruction tuning make content bias worse? That seems counterintuitive."

**Answer:** "It's counterintuitive but makes sense through the Format Efficiency Hypothesis. Instruction tuning makes models better at parsing instructions — format attention becomes more efficient (23.7% → 20.8%). But this improved attention to the prompt can also make them more susceptible to content-based priming, like a poor example answer. Think of it as a side effect: the same mechanism that helps models understand the rubric also makes them more influenced by example answers. This is supported by our attention-weight analysis."

### Q3: "How is this different from existing research?"

**Answer:** "The key difference is in the question. Over 35 bias types had been documented, and Li et al. (DASFAA 2026) explicitly called for root cause analysis — asking whether bias comes from pre-training or instruction tuning. We're the first to provide experimental evidence for an answer. Prior work also studied only 2–6 models; our 22-model landscape is the largest scoring bias comparison to date. Additionally, we examined and ruled out four alternative explanations that no prior study tested."
