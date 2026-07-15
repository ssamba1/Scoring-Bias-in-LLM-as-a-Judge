# Blog Post

## Where Does AI Judge Bias Really Come From? A 31-Model Study Has the Answer

**By Sricharan Samba** | July 14, 2026

*When an AI judges another AI, can we trust the score? The answer reveals something surprising about how instruction-tuning changes model behavior.*

---

### The Problem We Can't Ignore

AI is now judging AI. This isn't science fiction — right now, large language models are scoring answers on benchmark tests, ranking chatbot responses in leaderboards, and serving as reward models for training other AI systems. It's called "LLM-as-a-Judge," and it's become central to how we evaluate progress in AI.

But there's a catch: these AI judges have biases.

Over 35 distinct types of bias have been identified. Show an AI judge the same answer with a different scoring rubric, and you get a different score. Change the score labels from numbers to letters — different score. Show a good example before asking for a score — the score drifts one way. Show a bad example — it drifts the other.

Prior work documented these biases in detail. A key paper by Li et al. (DASFAA 2026) defined three specific types of "scoring bias" and tested them across five frontier models. But they left a fundamental question open: **where does this scoring bias actually come from?** Is it baked into pre-trained language models from the start, or does it emerge when models are fine-tuned to follow instructions?

As a high school researcher interested in AI safety, I decided to find out.

### The Experiment: 31 Models, 54,000 Judgments

The core idea is simple. If scoring bias comes from pre-training, then both the "base" version of a model (raw pre-trained output) and its "instruct" version (fine-tuned to follow instructions) should show similar bias. If it comes from instruction tuning, the two versions should differ.

So I collected 9 model families where both base and instruct variants are publicly available — Llama 3.1, Llama 3.2, Mistral 7B, Qwen2.5, Gemma 2, StableLM 2, and others — spanning from 0.5 billion parameters to 671 billion parameters. For each family, I ran both versions through three scoring bias tests:

1. **Rubric Order:** Score on a normal scale (1=worst, 5=best), then a reversed scale (1=best, 5=worst). Does the model notice?
2. **Score ID:** Use numbers (1–5), letters (A–E), then descriptive words (Poor–Excellent). Do the scores change?
3. **Reference Answer:** No example, a good example, then a poor example shown before scoring. Does priming affect the score?

I added 22 additional instruct-only models for breadth — DeepSeek-V3, Gemini-2.5-Flash, Phi-4, Qwen3, and many more.

Total: **31 model variants, 54,000 judgments, less than $3 in total API costs, fully reproducible on free Kaggle GPUs.**

### The Main Finding: A Split Personality

Here's what I found, and it's not a simple story.

**Format bias goes down.** Across almost every model family, instruction-tuned models are significantly better at understanding scoring formats. Rubric order bias drops by 44% on average. Score ID bias drops by 77%. This makes intuitive sense: instruction tuning teaches models to follow instructions more carefully, so they pay better attention to how the scoring scale works.

**Content bias goes up — but only in the right conditions.** This is the finding that surprised me. When you show a model a poor example answer before asking it to score, larger instruction-tuned models become more biased — not less. In the most dramatic case, Llama-3.1-8B showed a 1.58-point shift on a 5-point scale after instruction tuning. Before instruction tuning, the base model barely budged.

But here's the nuance: this only happens in larger models (3 billion+ parameters) trained with a specific method called RLHF (Reinforcement Learning from Human Feedback). In smaller models (1.5 billion parameters and under), content bias actually decreases after instruction tuning. And models trained with different methods — like Mistral 7B, which uses SFT+DPO — show a completely different pattern.

This "scale-dependent differential effect" is the paper's central finding. Instruction tuning improves one thing (format understanding) while potentially worsening another (content susceptibility), but only when the model is big enough and trained the right way.

### Why Does This Happen? The Format Efficiency Hypothesis

I wanted to understand the mechanism, not just document the pattern. So I dug into the models' attention weights — the internal "focus" of the transformer architecture.

The leading hypothesis was that instruction tuning broadly increases attention to everything in the prompt, which would explain both the format improvement (more attention to format tokens) and the content increase (more attention to exemplar content).

The data didn't support this. Instead, I found something more interesting: **format token attention actually decreases** after instruction tuning, from 23.7% to 20.8%. The models become *more efficient* at parsing formats, using less attention to get the same (or better) format understanding. Meanwhile, content attention stays essentially flat.

I call this the **Format Efficiency Hypothesis**: instruction tuning makes models better at understanding scoring formats by making format parsing more efficient, not by allocating more attention to it. This explains why format bias consistently decreases. The content bias increase in larger models likely comes from a different mechanism — possibly increased "helpfulness" making models more susceptible to exemplar priming — rather than attention redistribution.

The hypothesis makes five specific, testable predictions that future work can confirm or refute.

### What This Means in Practice

The finding that scoring bias is modulated by instruction tuning — not inherent to pre-training — is actually good news. It means we don't need to redesign language models from scratch to fix scoring bias. We just need to improve how we fine-tune them.

**For anyone using AI judges right now:**

1. **Use numeric labels.** Across all models tested, numeric scales (1–5) produced the most consistent scores. Letter grades and descriptive labels introduced more variability.
2. **Test multiple formats.** Don't trust a single scoring format. Test at least two different formats to see if scores shift.
3. **Be careful with examples.** If you include example answers in your evaluation prompts, include both good and poor examples to counterbalance the priming effect.
4. **Report bias separately.** Format bias and content bias move in opposite directions. A single aggregate bias score hides the real story.

**For AI developers:**

The key insight is that bias mitigation should target the instruction-tuning stage, not the base model. The Format Efficiency Hypothesis suggests it's possible to improve format robustness without increasing content sensitivity — the two channels can be decoupled with the right training data and methods.

**For the research community:**

We need standardized bias evaluation for LLM-as-a-Judge systems. Every model deployed as a judge should report its bias profile alongside its accuracy. And we need to understand why RLHF specifically produces the differential effect — a question I hope future work will answer.

### Why This Matters for AI Safety

This isn't just an academic curiosity. If AI judges are systematically biased, then every evaluation that relies on them inherits that bias:

- AI safety assessments of new models may be unreliable
- Benchmark rankings may contain systematic errors
- RLHF training pipelines may inadvertently amplify biases
- Automated evaluation in production systems may produce misleading results

By understanding where scoring bias comes from — and showing that it emerges during instruction tuning rather than being baked into pre-training — we open a clear path toward mitigation. The problem is real, but it's solvable.

### Open Science

Every part of this project is open source:

- **Code:** github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
- **Data:** All 54,000 judgments, fully documented
- **Paper:** Full LaTeX source including all appendices
- **Interactive dashboard:** Bias explorer, model ranking, family comparisons
- **Archived:** zenodo.org/10.5281/zenodo.21361920

The entire experiment can be reproduced for free using Kaggle GPUs. I hope this encourages more researchers — especially students — to dig into AI safety questions that don't require massive budgets, just clear questions and rigorous methodology.

### What's Next

Five things I'd love to see the community take on:

1. **Replication on commercial models** (GPT-4, Claude, Gemini Pro)
2. **Testing on larger open-weight models** (70B+ families with base-instruct pairs)
3. **Testing the five Format Efficiency Hypothesis predictions**
4. **Developing training methods that reduce content sensitivity without sacrificing format robustness**
5. **Creating a standardized bias benchmark for LLM-as-a-Judge systems**

The data is open, the code is free, and the question matters. I hope you'll take a look — and maybe help answer the next question.

---

*Sricharan Samba is a high school researcher at South Forsyth High School studying AI alignment and evaluation. Contact: srisamba09@gmail.com*

📄 **Read the paper:** github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
💾 **Cite:** doi.org/10.5281/zenodo.21361920
🐦 **Follow for updates:** [@srisamba09](https://twitter.com)
