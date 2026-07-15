# LinkedIn Article

## Can We Trust AI to Judge AI? A High School Researcher's Answer

**By Sricharan Samba** | July 2026

---

Imagine you're grading a student's biology exam. You have a rubric: 1 is worst, 5 is best. The student gives a perfect answer. You give them a 5. Fair enough.

Now imagine someone hands you the same exam but says "1 is best, 5 is worst." If you're a careful human grader, you notice the switch and adjust. But what if you're an AI? What if you don't notice?

This isn't hypothetical. Large language models (LLMs) are increasingly deployed as automated judges — scoring everything from chatbot responses to essay submissions, powering benchmarks like MT-Bench and Chatbot Arena, and even serving as reward models in reinforcement learning pipelines. Yet a growing body of research documents over 35 distinct types of bias in these AI judges.

The fundamental question — **where does scoring bias come from?** — remained unanswered. Until now.

### The Study

In my recent paper, "Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison," I investigate whether scoring bias originates from pre-training (baked into the model from the start) or emerges during instruction tuning (when models are fine-tuned to follow instructions).

The experimental setup: I tested 31 model variants across 16 families — including Llama, Mistral, Qwen, Gemma, DeepSeek, and others — collecting 54,000 scoring judgments. Critically, I compared 9 pairs of models where each pair consists of a "base" version (raw pre-trained model) and an "instruct" version (same architecture, fine-tuned to follow instructions). This base-instruct comparison is the key that unlocks the origin question.

Three bias types were measured using established perturbation probes:
1. **Rubric Order:** Reversing the scoring scale (1=best instead of 1=worst)
2. **Score ID:** Changing labels from numbers (1–5) to letters (A–E) to descriptive words (Poor–Excellent)
3. **Reference Answer:** Showing a good or poor example before asking for a score

### The Key Findings

**1. Format bias decreases after instruction tuning — a consistent improvement.**
Across 9 model families, instruction tuning made models better at understanding scoring formats. Rubric order bias dropped by 44% on average; score ID bias dropped by 77%. This was consistent across architectures from 1.6B to 671B parameters.

**2. Content bias increases — but only in larger RLHF-trained models.**
When shown a poor example answer before scoring, larger instruction-tuned models (3B+ parameters, trained with RLHF) became more biased. The most dramatic case: Llama-3.1-8B showed a 1.58-point shift on a 5-point scale after instruction tuning — where the base model showed almost none.

**3. The training method matters.**
The seven RLHF-trained families showed the differential effect (format decreases, content increases). The SFT+DPO family (Mistral 7B) and the SFT-only family (StableLM 2) showed different patterns, suggesting that the alignment method modulates the bias profile.

**4. Score ID bias is the most common problem overall.**
Across all 22 instruct models tested, Score ID bias had the largest average effect (0.68 points on a 5-point scale), ranging from 0.00 (Qwen3-14B) to 1.80 (Hermes-3-70B).

**5. Bayesian evidence is overwhelming.**
Bayes factors exceeding 10,000 confirm that scoring bias exists across instruct-tuned models with near-certainty.

### Why This Matters

These findings have direct, actionable implications:

**For practitioners using LLM-as-a-Judge:**
- Always test multiple scoring formats to detect bias
- Use numeric labels (not letters or descriptive words) — they show the lowest bias
- When using reference examples in prompts, include both good AND poor exemplars
- Report format bias and content bias separately — they move in opposite directions

**For model developers:**
- Bias mitigation must target the alignment stage, not the base model
- The Format Efficiency Hypothesis suggests that improving format parsing is achievable without increasing content susceptibility

**For benchmark designers:**
- Scoring rubrics should use numeric labels by default
- Avoid letter-grade or descriptive labels where possible

### The Bigger Picture

The finding that scoring bias is modulated by instruction tuning — not inherent to pre-training — is actually good news. It means we can address the problem by improving how we fine-tune models, rather than redesigning them from scratch. But the solution requires nuance: improving format understanding can inadvertently make models more sensitive to content-based priming.

As a high school researcher working with a budget of under $3 in API costs, I hope this work demonstrates that impactful AI safety research doesn't require massive resources — just clear questions, rigorous methodology, and open science.

### Read the Full Paper

All code, data, and analysis are publicly available:
- **GitHub:** github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
- **Zenodo:** doi.org/10.5281/zenodo.21361920
- **arXiv:** Coming soon

*I welcome feedback, collaboration, and replication efforts. If you're working on LLM evaluation, bias mitigation, or AI safety — let's connect.*

---

*Sricharan Samba is a high school researcher at South Forsyth High School studying AI alignment and evaluation. Contact: srisamba09@gmail.com*
