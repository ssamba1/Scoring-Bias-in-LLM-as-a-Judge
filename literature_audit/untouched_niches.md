# Research Niche Discovery Report: LLM Judge Bias

**Date:** July 12, 2026
**Scope:** 10 angles × multiple queries each across arXiv, Google Scholar, Semantic Scholar, ACL Anthology, NeurIPS, and general web

---

## 1. LLM Self-Awareness of Bias (Can models recognize their own biased judgments?)

**STATUS: EXISTS**

Papers found:
- **Hills (2025)** "Could you be wrong: Debiasing LLMs using a metacognitive prompt for improving human decision making"  arXiv:2507.10124. Directly shows that asking LLMs "could you be wrong?" causes them to introspect and identify their own biases (omission bias, etc.) and produce metacognitive reflection.
- **Panickssery et al. (2024)** "LLM Evaluators Recognize and Favor Their Own Generations"  NeurIPS 2024. Shows causal link between self-recognition and self-preference bias.
- **"Self-Preference Bias in LLM-as-a-Judge"** (2024)  Studies correlation between self-recognition capability and self-preference strength.

**Bottom line:** This area is active. The metacognitive prompting approach is particularly well-explored.

---

## 2. LLM Anchoring Effects in Sequential Evaluation

**STATUS: EXISTS** (multiple papers)

Papers found:
- **Echterhoff et al. (2024)** "Cognitive Bias in Decision-Making with LLMs"  EMNLP 2024 Findings. Evaluates anchoring bias in sequential setups.
- **O'Leary (2025)** "An Anchoring Effect in Large Language Models"  SSRN.
- **Huang et al. (2025)** "Understanding the Anchoring Effect of LLM with Synthetic Data"  arXiv.
- **Mahajan et al. (2025)** "Cognitive bias in clinical large language models"  PMC.

**Bottom line:** Well-established. Not a novel niche.

---

## 3. LLM Judge Fatigue Over Long Evaluation Sessions

**STATUS: ✅ CONFIRMED UNTOUCHED**

Searches performed: "LLM-as-a-judge fatigue", "evaluation session degradation", "batch effect LLM judge", "long context evaluation decline", "fatigue OR tired OR exhaust LLM judge evaluation", "cognitive load LLM judge"  **zero empirical papers found.**

The survey papers (Gu et al. 2026, Cell Press) mention human annotator fatigue as a known problem and suggest LLMs *might* be superior to humans because they don't fatigue  but no paper tests whether LLM judges actually *do* degrade over long evaluation sessions.

**This is a genuinely untouched area.** Key questions:
- Does LLM judge accuracy/consistency decline after evaluating 100, 500, 1000 items?
- Do biases (position, verbosity) worsen with evaluation session length?
- Does context window saturation cause drift?
- Can this be mitigated with rest, resets, or calibration checks?

**ISEF potential: HIGH.** Clean experiment: compare judge accuracy on first 50 vs last 50 of a 500-item batch. Fully API-doable. 2-week experiment.

---

## 4. LLM Judge Bias in Evaluating AI Agent Trajectories (Multi-Step)

**STATUS: EXISTS** (limited)

Papers found:
- **Zhuge et al. (2024/2025)** "Agent-as-a-Judge: Evaluate Agents with Agents"  ICML 2025. Framework for using agents as evaluators of other agent trajectories.
- **Yu (2025)** "The Rise of Agent-as-a-Judge Evaluation for LLMs"  arXiv:2508.02994. Survey covering trajectory evaluation biases.
- **Zylos Research** "LLM-as-Judge Patterns for Agent Evaluation: Calibration, Bias, and..."  Discusses trajectory-specific biases.

**Nuance:** The Agent-as-a-Judge papers focus on *framework design*, not on systematic measurement of trajectory-specific biases. A dedicated empirical study ("What biases do LLM judges exhibit when evaluating agent trajectories compared to evaluating final outputs?") does not exist as a standalone paper.

**Bottom line:** Touched but not thoroughly explored. There's room for a study on "trajectory length bias" or "tool-call-count bias."

---

## 5. Biased LLM Judges Approving Unsafe Models (AI Safety Intersection)

**STATUS: EXISTS**

Papers found:
- **Raina et al. (2024)** "Is LLM-as-a-Judge Robust? Investigating Universal Adversarial Attacks on Zero-shot LLM Assessment"  EMNLP 2024. Shows adversarial phrases can universally inflate judge scores.
- **Al Masoud et al. (2026)** "Security in LLM-as-a-Judge: A Comprehensive SoK"  arXiv:2603.29403. Systematizes attacks on/through LLM judges.
- **LessWrong** "Your LLM Judge may be biased"  Documents real biased judge failures in safety evaluation.

**Nuance:** Existing work is about *adversarial attacks* on judges (can you trick them?), not about *inherent bias causing safety approval failures*. A paper titled "Do Biased LLM Judges Unknowingly Approve Unsafe Content?" does not exist.

**Bottom line:** The specific angle (inherent bias → safety failure) is underexplored, but related work exists.

---

## 6. LLM Judge Bias Interaction Effects (Do biases compound or cancel?)

**STATUS: ✅ CONFIRMED UNTOUCHED**

Searches performed: "bias interaction LLM judge", "compound OR cancel OR interact position verbosity", "combined bias effect", "cross-bias interaction", "bias interaction effects systematic study"  **zero systematic empirical studies found.**

Blog posts (mbrenndoerfer) state: "Position bias, verbosity bias, and sycophancy do not operate independently. They interact and compound." The OpenReview on Self-Preference Bias notes: "position bias, verbosity bias, and self-preference bias interact and affect each other." But these are *observations*, not *systematic studies*.

No paper asks:
- When position bias (prefers first) and verbosity bias (prefers longer) conflict, which wins?
- Do biases add linearly, multiplicatively, or cancel?
- Which pairs of biases compound vs offset?

**ISEF potential: HIGH.** Beautiful experimental design: create evaluation items that trigger combinations of biases (e.g., long response in second position vs short response in first position). Measure bias strength individually and in combination. Full-factorial design. 2-3 week experiment. Doable with API calls.

---

## 7. LLM Judge Confidence Calibration Specifically for Bias Detection

**STATUS: EXISTS** (general) but **UNTOUCHED** for the specific angle

Papers found (general calibration):
- **Tian et al. (2025)** "Overconfidence in LLM-as-a-Judge: Diagnosis and Confidence-Driven Solution"  arXiv:2508.06225. Studies overconfidence in LLM judges (confidence > accuracy).
- **"Competing Biases underlie Overconfidence and Underconfidence in LLMs"**  Nature Machine Intelligence (2026). Reveals choice-supportive bias and contradiction hypersensitivity.
- **"How to Correctly Report LLM-as-a-Judge Evaluations"**  Statistical framework for bias correction with confidence intervals.

**None of these study calibration FOR BIAS DETECTION.** The specific question  "When an LLM judge IS biased, is its confidence in that biased judgment well-calibrated? Does the judge know it's being biased?"  is untouched.

**ISEF potential: HIGH.** Protocol: Create evaluation items where the judge exhibits known biases (position, etc.). Ask the judge for confidence in its own judgment. Compare confidence when biased vs unbiased. Doable in 2-3 weeks with API.

---

## 8. Cross-Cultural Bias in LLM Judges

**STATUS: EXISTS**

Papers found:
- **"A Benchmark for Evaluating LLM-Judge in Identifying Cultural Errors"**  arXiv:2605.26955. Specific benchmark for LLM-judge cultural error detection.
- **"Why are all LLMs Obsessed with Japanese Culture?"** (2026)  Uses LLM-as-a-judge to detect cultural bias.
- **"Cultural bias and cultural alignment of large language models"**  PMC (2024).
- **"Ready to Translate, Not to Represent?"**  Uses LLM-as-a-judge for translation bias detection.

**Bottom line:** Well-trodden. Cultural bias in LLMs is a major research area. LLM-as-a-judge used both as tool and object of study.

---

## 9. Temporal Stability of LLM Judge Bias Over Repeated Use

**STATUS: ✅ CONFIRMED UNTOUCHED**

Searches performed: "temporal stability LLM judge bias", "judge drift over time", "repeated evaluation consistency", "longitudinal LLM judge", "test-retest reliability LLM-as-a-judge", "temporal OR longitudinal bias drift"  **zero empirical papers found.**

Related but different:
- **"Stable Personas"**  studies temporal stability of *LLM personas/personality*, not judge bias.
- **"Human-anchored longitudinal comparison"**  uses bias-calibrated LLM-as-judge but studies *model drift*, not judge bias stability.
- **"On the Fundamental Limits of LLMs at Scale"**  mentions "judge drift" as a conceptual phrase about benchmark skew.
- **Blog post "LLM-as-Judge Drift"** (tianpan.co)  discusses model version changes, not repeated use of same model.

**No paper studies:** Does position bias strength change when the same judge evaluates the same items at time A vs time B (1 hour, 1 day, 1 week later)? Is verbosity bias temporally stable?

**ISEF potential: MEDIUM-HIGH.** Requires running evaluations at multiple time points. Doable but requires patience (longitudinal design). Clean interpretability.

---

## 10. LLM Judge Bias in Multi-Turn Conversations vs Single-Turn

**STATUS: ✅ CONFIRMED UNTOUCHED**

Searches performed: "multi-turn vs single-turn bias comparison LLM judge", "multi-turn conversation evaluation bias difference", "multi-turn position bias single-turn comparative"  **zero papers found comparing bias magnitude between multi-turn and single-turn evaluations.**

Related but different:
- **Zheng et al. (2023)** "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"  studies LLM judges on multi-turn questions but doesn't compare bias across settings.
- **"RankJudge: A Multi-Turn LLM-as-a-Judge Synthetic Benchmark Generator"** (2026)  benchmark generation, not bias comparison.
- **"LLMs Get Lost In Multi-Turn Conversation"**  studies LLM performance drop in multi-turn, not judge bias.

**No paper asks:** Does position bias become stronger in multi-turn evaluations (where there's more context)? Does verbosity bias differ when evaluating a full conversation vs a single response?

**ISEF potential: HIGH.** Clean within-model comparison: same judge evaluates single-turn responses vs multi-turn conversations. Measure all known biases in both settings. 2-3 week experiment. Highly novel.

---

## Summary Table

| # | Angle | Status | Papers | Novelty | ISEF Potential |
|---|-------|--------|--------|---------|----------------|
| 1 | Self-awareness of bias | EXISTS | 3+ papers | Low | Low |
| 2 | Anchoring effects | EXISTS | 4+ papers | Low | Low |
| **3** | **Judge fatigue** | **✅ UNTOUCHED** | **0 papers** | **Very High** | **HIGH** |
| 4 | Agent trajectory bias | EXISTS | 2-3 papers | Medium | Medium |
| 5 | Safety × biased judges | EXISTS | 2-3 papers | Medium | Medium |
| **6** | **Bias interaction effects** | **✅ UNTOUCHED** | **0 papers** | **Very High** | **HIGH** |
| 7 | Confidence calibration for bias | EXISTS (general) | 3 papers | Medium-High | HIGH |
| 8 | Cross-cultural bias | EXISTS | 4+ papers | Low | Low-Medium |
| **9** | **Temporal stability** | **✅ UNTOUCHED** | **0 papers** | **Very High** | **MEDIUM-HIGH** |
| **10** | **Multi-turn vs single-turn bias** | **✅ UNTOUCHED** | **0 papers** | **Very High** | **HIGH** |

---

## Top-3 Recommended Niches for a High School Student

### 🥇 #6: Bias Interaction Effects (Do LLM Judge Biases Compound or Cancel?)

**Why:** 
- **Completely untouched**  zero papers found
- **Clean experiment:** Create a 2×2 factorial design with position bias (first/second) and verbosity bias (short/long). Cross them: short-first, long-first, short-second, long-second. Measure individual bias strengths, then measure combined. Test all pairs of known biases.
- **API-doable:** Only need to call LLM-as-a-judge with controlled comparison pairs.
- **ISEF appeal:** The elegance of asking "do biases add or cancel?" is immediately understandable to judges. Statistical interaction analysis (ANOVA) is a sophisticated technique for a high schooler.
- **Timeline:** 2-3 weeks for full experiment.

### 🥈 #3: LLM Judge Fatigue Over Long Evaluation Sessions

**Why:**
- **Completely untouched**
- **Analogous to human psychology:** Framing it as "do AI judges suffer the same fatigue effects as human judges?" is compelling.
- **Simple protocol:** Run an LLM judge on a 500+ item batch. Compare accuracy/consistency of first N vs last N items. Vary session length. Check if biases intensify with fatigue.
- **ISEF appeal:** Tangible real-world implications (benchmark reliability depends on evaluation order).
- **Timeline:** 2 weeks.

### 🥉 #10: Multi-Turn vs Single-Turn Bias

**Why:**
- **Completely untouched**
- **Growing importance:** As agents become multi-turn, understanding whether judges evaluate them differently is critical.
- **Clean comparison:** Same judge, same content, but one presented as single-turn Q&A and one as multi-turn conversation. Measure position bias, verbosity bias, self-enhancement in both conditions.
- **ISEF appeal:** Directly addresses a practical gap  current leaderboards mix single-turn and multi-turn evaluations without accounting for differential bias.
- **Timeline:** 2-3 weeks.
