# ISEF Presentation — Bias Interaction Effects
## Slide-by-Slide Outline

---

## Slide 1: Title
**Bias Interaction Effects in LLM-as-A Judge: A Full-Factorial Study**
Student A, Student B — High School Name
ISEF 2027 — Systems Software Category

---

## Slide 2: The Problem
**LLM-as-A-Judge is everywhere**
- Used to evaluate ChatGPT, Claude, Gemini outputs
- But judges have KNOWN biases: favor first answers, longer answers, positive tone
- **Problem:** These biases have only been studied ONE AT A TIME
- In reality, ALL biases are present simultaneously

**Key question:** When biases co-occur, do they compound or cancel?

---

## Slide 3: The Gap
**What we found after reading 60+ papers:**
- 35 bias types documented
- 12 have mitigations
- **23 have NO mitigation**
- **ZERO papers study bias interactions**

This is a completely untouched research area.

---

## Slide 4: Experimental Design
**Full-factorial 2 × 3 × 3 design:**

| Factor | Levels |
|--------|--------|
| Position | First, Second |
| Length | Short, Normal, Long |
| Sentiment | Negative, Neutral, Positive |

**= 18 unique conditions per item**
**400 items × 8 key conditions × 5 judges**

---

## Slide 5: How We Built It
**400 evaluation items** across 8 domains (creative, technical, code, reasoning, etc.)
**Each item has 8 versions** varying length and sentiment
**5 judge models:** Claude, GPT-4o, Gemini, DeepSeek, Llama
**Statistical model:** Linear mixed effects with interaction terms

---

## Slide 6: Results — Main Effects
**Position bias:** First position scores 0.08–0.20 higher (confirmed known result)
**Verbosity bias:** Long responses score 0.15–0.32 higher (largest effect)
**Sentiment bias:** Positive tone scores 0.05–0.15 higher

---

## Slide 7: Results — Interaction Effects (NOVEL)
**Key metric:** Interaction Ratio (IR)
- IR > 1.05 = biases compound (worse together)
- IR = 1.0 = additive (no interaction)
- IR < 0.95 = biases cancel

**Position × Verbosity:**
- Claude: IR = 2.72 (compounding!)
- GPT-4o: IR = 2.53 (compounding!)
- Gemini: IR = 0.99 (additive)
- DeepSeek: IR = 1.54 (mild compounding)
- Llama: IR = 2.10 (compounding!)

---

## Slide 8: Results — Worst Case Analysis
**Worst case** (second position + short + negative tone):
- Baseline score: ~3.5/5
- Worst case: ~2.8–3.2/5
- **Degradation is 1.5–3× worse than individual biases would predict**

**Conclusion:** Biases don't just add up — they gang up.

---

## Slide 9: Implications
1. **Test combinations, not individuals** — Single-bias tests underestimate real bias
2. **Validate mitigations jointly** — A fix for position bias alone might fail with other biases present
3. **Model selection matters** — Some models compound biases more than others
4. **Worst-case analysis should be standard** — Like stress testing in engineering

---

## Slide 10: Why This Is Novel
- **First systematic study** of bias interaction effects
- **Full-factorial design** (textbook good science)
- **5 models from different providers** (not just one)
- **400 items across 8 domains** (not just chat)
- **Statistical rigor** (mixed effects models, interaction ratios)

---

## Slide 11: Limitations & Future Work
**Limitations:**
- Only 3 of 12+ bias types tested
- Synthetic responses, not real user data
- API-based scoring adds noise

**Future work:**
- Test more bias combinations (authority × verbosity, etc.)
- Open-source fine-tuned judge with controlled bias interactions
- Real-world validation: do interaction effects matter in production?

---

## Slide 12: Thank You
**Key takeaway:** When you test LLM judges, don't test biases one at a time — they interact.

Research repository: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
Questions?
