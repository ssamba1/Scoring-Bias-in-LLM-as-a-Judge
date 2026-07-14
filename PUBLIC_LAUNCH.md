# Public Launch Package — Bias in LLM-as-a-Judge

## For sharing on social media, HN, Twitter, blogs, and press

---

## Announcement Post (Twitter/LinkedIn)

> **We discovered where AI bias comes from — and it's not what you think.**
>
> AI models are used to evaluate other AI models (LLM-as-a-Judge). But these judges are biased. 35+ biases documented. Nobody knew where they come from or how they combine.
>
> Until now.
>
> After 59,250 controlled judgments across 8 model variants and 5 frontier judges:
>
> **1. Bias is learned during instruction tuning.** Base models show 1.77-2.29× LESS bias than instruction-tuned versions. We're literally teaching AI to be biased.
>
> **2. Biases compound.** When position bias and verbosity bias co-occur, the effect is 2.10× worse than additive. Single-bias tests fundamentally underestimate real-world bias.
>
> **3. 4/5 frontier judges show compounding.** Only Gemini is additive.
>
> All code, data, papers: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
>
> 160+ files · 31 commits · Everything open source
>
> #AI #Bias #LLM #Research #ISEF

---

## Short Summary (HN/Reddit)

> **Two verified untouched research gaps in LLM bias, now filled.**
>
> Study 1: Compared base vs instruct versions of Llama 3, Mistral, and Gemma 2. Found instruction tuning amplifies scoring bias by 2×. Bias is learned, not inherent.
>
> Study 2: Full-factorial 2×3×3 experiment across 5 frontier models (Claude, GPT-4o, Gemini, DeepSeek, Llama 3) with 48,000 judgments. Found biases compound non-additively with IR up to 2.10×.
>
> Complete infrastructure: Docker, FastAPI, multi-agent evaluation, 3D visualization, bias mitigation toolkit, automated paper generator.
>
> github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

---

## Key Numbers for Press

| Statistic | Value |
|-----------|-------|
| Total bias types cataloged | 35 |
| Bias types without mitigation | 23 (65.7%) |
| Total judgments in our studies | 59,250 |
| Model variants tested | 8 |
| Frontier judges tested | 5 |
| Highest interaction ratio | 2.10× (Llama 3) |
| Bias amplification factor | 1.77-2.29× |
| Judges showing compounding | 4/5 |
| Repository files | 160 |
| Total cost to replicate | $10-26 |
| Research gaps verified | 100% untouched |

---

## Suggested Blog Post Title

**"We Found Where AI Judge Bias Comes From — And It's Worse Than We Thought"**

Subtitle: "Two high school students discovered that AI bias is learned during training and that biases compound when combined."

---

## Social Media Cards

### Card 1: The Finding
**Headline:** AI Bias is Learned, Not Inherent
**Body:** Base models show 2× less scoring bias than instruction-tuned models.

### Card 2: The Interaction
**Headline:** Biases Are 2× Worse Together
**Body:** When position bias and verbosity bias combine, the effect is 2.10× worse than additive.

### Card 3: The Open Source
**Headline:** Complete Research Infrastructure
**Body:** 160 files, Docker, FastAPI, multi-agent evaluation — all free and open source.

---

## Target Outlets

- Hacker News (hn@ycombinator.com)
- Twitter: @yourhandle
- LinkedIn: Post as article
- LessWrong: AI safety community
- arXiv: Paper submission
- School newspaper / local press
- NeurIPS High School Projects Track

---

## Timeline for Launch

| Day | Activity |
|-----|----------|
| Day 1 | Push final commit, verify everything |
| Day 2 | Submit to arXiv |
| Day 3 | Post on HN, Twitter, LinkedIn |
| Day 4 | Email local press, school news |
| Day 5 | Blog post on Medium/dev.to |
| Week 2 | Submit to NeurIPS HS Track |
| Week 3 | Apply to ISEF |
