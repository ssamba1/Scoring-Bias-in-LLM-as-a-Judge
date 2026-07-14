# Launch Announcement Package

## Timing Strategy

```
Day 1: arXiv preprint goes live
Hour 0:  Twitter/X thread
Hour 1:  LinkedIn article
Hour 2:  Reddit r/MachineLearning
Hour 6:  Hacker News
Hour 12: Newsletter blurb
Day 2:  Conference abstract submission
Week 1: Email list of 10 interested researchers
```

---

## Twitter/X Thread (8 posts)

```
1/8 New paper: "Where Does Scoring Bias Come From?"
We answer the open question from Li et al. (DASFAA 2026):
Is scoring bias inherent to LLMs, or does instruction tuning cause it?

2/8 TL;DR: Instruction tuning has opposite effects depending on bias type.
Format biases (rubric order, score ID) → ↓ 44-77%
Content bias (reference answer) → ↑ 35%
This holds across 30 model variants, 15 families.

3/8 Why this matters:
Every benchmark using LLM-as-a-Judge (MT-Bench, Chatbot Arena) 
has biased judges. We show WHERE the bias comes from,
so you know WHERE to mitigate it.

4/8 The IIAR hypothesis: Instruction tuning increases attention
to ALL prompt features. Good for format parsing, bad for
exemplar susceptibility. 5 testable predictions in the paper.

5/8 We ruled out 4 alternative explanations:
- Not a global scoring shift
- Not driven by one model family
- Not a probe ordering artifact
- Not a parser failure
The differential effect is real.

6/8 Best unbiased models? 
🥇 Gemma-4-31B (avg bias Δ=0.33)
🥈 Nemotron-Nano-30B (0.47)
🥉 Qwen3-14B (0.43)
Full leaderboard: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

7/8 We tested 4 training methods:
RLHF → strong differential effect (100% consistency)
SFT+DPO → weaker, sometimes reversed
DPO → higher overall bias
SFT → moderate effects
Training method matters for bias!

8/8 Read the paper: [arXiv link]
Code & data: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
Interactive: [project page]
#LLM #AI #Bias #LLMasJudge #Research
```

---

## LinkedIn Post

**Headline:** We Found Where LLM Scoring Bias Comes From

Every major LLM benchmark uses models to judge other models. And every judge is biased. But until now, nobody knew WHERE the bias came from.

We tested 30 model variants across 15 families — comparing base (pre-trained) against instruct (SFT + RLHF) versions of the same architecture.

Key finding: Format biases decrease (good!), content biases increase (bad!). Instruction tuning is a double-edged sword for bias.

For practitioners:
✅ Use RLHF models — they show the cleanest pattern
✅ Ensemble multiple judges — reduces bias by 52%
⚠️ Watch out for exemplar sensitivity in instruct models

Full paper, code, interactive article, and leaderboard at github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

---

## Reddit r/MachineLearning Post

**Title:** We tested 30 LLMs and found: instruction tuning reduces format bias by 44-77% but INCREASES content bias by 35%

**Text:**
We did the first systematic comparison of base vs instruct models for scoring bias. We already know LLM judges are biased. What nobody tested: does the bias come from pre-training or from instruction tuning?

30 model variants, 15 families, 40,500 judgments across 3 bias probes.

TL;DR: It depends on the bias type. Format biases get better (models learn to parse rubrics). Content biases get worse (models become more suggestible to exemplars).

We also found:
- RLHF vs SFT+DPO produce DIFFERENT bias profiles (Mistral is an outlier)
- Ensembling 3+ judges reduces bias by 52%
- Model size correlates negatively with bias (ρ=-0.75)

Paper + code + interactive leaderboard:
github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

Happy to answer questions!

---

## Newsletter Blurb (for The Batch, TLDR AI, etc.)

**Scoring Bias: Where Does It Come From?**

A new study by [Author] provides the first systematic answer to an open question: does LLM scoring bias come from pre-training or instruction tuning? Testing 30 model variants across 15 families, they found instruction tuning has *opposite effects* depending on the bias type — format biases decrease by 44-77%, but content biases increase by 35%. The IIAR hypothesis explains this through increased attention to all prompt features. 
[Link]

---

## Conference Talk Abstract (5 minutes)

**Title:** Where Does Scoring Bias Come From? A Base vs Instruct Comparison

We present the first systematic investigation of whether scoring bias in LLM-as-a-Judge originates from pre-training or instruction tuning. Testing 30 model variants from 15 families across 3 scoring probes (40,500 judgments), we find instruction tuning has differential effects: format-related biases decrease by 44-77%, but content-related bias increases by 35%. The pattern survives Bonferroni correction for format probes and holds across all RLHF families. We propose the IIAR hypothesis, rule out four alternative explanations, and demonstrate mitigation strategies. All code and data are open source.
