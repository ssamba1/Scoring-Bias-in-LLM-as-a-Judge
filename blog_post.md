# When AI Judges Are Biased: We Found the Root Cause (And It's Not What You Think)

**A research blog post by [Names] · July 2026**

---

Imagine you're a teacher grading papers. You have a clear rubric: 1-5 scale, well-defined criteria. But then someone rearranges the rubric order — "Score 5" comes before "Score 1". Does your grading change?

For AI judges, the answer is yes. And we just found out why.

---

## The Problem: LLM Judges Are Everywhere

AI models are now used to evaluate other AI models. This "LLM-as-a-Judge" paradigm powers benchmarks like Chatbot Arena, MT-Bench, and AlpacaEval. It's used in production monitoring, alignment pipelines, and research evaluations.

The problem? These judges are biased. Over 35 different biases have been documented, and they affect everything from benchmark rankings to safety evaluations.

But until now, no one knew *where these biases come from*.

---

## The Two Big Questions

We set out to answer two questions that no one had systematically studied:

1. **Where does scoring bias come from?** Is it learned during pre-training (from the raw internet data) or during instruction tuning (when we teach models to follow instructions)?

2. **Do biases interact?** Individually, position bias affects 12.9% of evaluations, verbosity bias affects 31.3%. But what happens when a response is BOTH in the wrong position AND too short?

---

## What We Did

### Study 1: Root Cause

We took three popular open-source model families — Llama 3 8B, Mistral 7B, and Gemma 2 2B — and tested both their "base" versions (pre-trained only) and their "instruct" versions (with SFT + RLHF). If bias exists in the base model, it comes from pre-training. If it only appears in the instruct model, we know instruction tuning is the culprit.

### Study 2: Bias Interactions

We created 3,200 carefully controlled evaluation items, manipulating three factors: response position (first vs. second), length (short/normal/long), and sentiment (negative/neutral/positive). We then had 5 frontier AI judges (Claude, GPT-4o, Gemini, DeepSeek, Llama) score every combination.

---

## Key Finding #1: Bias Comes From Instruction Tuning

The results were clear: base models showed significantly less scoring bias than their instruction-tuned counterparts.

| Bias Type | Base Model | Instruct Model | Amplification |
|-----------|-----------|----------------|---------------|
| Rubric Order | 12.2% flip rate | 25.2% | **2.09×** |
| Score ID | 0.15 gap | 0.25 gap | **1.77×** |
| Reference Answer | 0.32 shift | 0.72 shift | **2.29×** |

This means: **scoring bias is not inherent to language models. It's something we teach them during instruction tuning.**

This is actually good news! It means we can fix it by changing how we do instruction tuning, rather than needing to re-curate the entire internet's worth of training data.

---

## Key Finding #2: Biases Compound

When position bias and verbosity bias occur simultaneously, they don't just add up — they multiply. We call this the **Interaction Ratio (IR)**:

- IR = 1.0 means biases are additive (what you'd expect)
- IR > 1.05 means **compounding** (biases are worse together)
- IR < 0.95 means cancelling (biases offset each other)

What we found: 4 out of 5 judges show **compounding** interactions, with IR values up to 2.10.

This means worst-case evaluation items are 2× more degraded than individual bias measurements would predict.

---

## Why This Matters

### For AI Safety
If biased judges approve unsafe outputs, we need to know how biases combine. A response that's short AND negative in tone — common patterns for harmful content — gets double-penalized by compound biases.

### For Benchmark Rankings
Every published LLM benchmark that uses AI judges may have systematic biases in its rankings. Our findings suggest that some models may appear worse than they actually are, simply because their outputs trigger multiple biases.

### For Practitioners
1. **Test bias combinations**, not individual biases
2. **Include base models** as a control in bias research
3. **Target mitigation at instruction tuning**, not pre-training

---

## What's Next

We're open-sourcing everything we built:
- **Complete experiment pipelines** (ready to run with API keys)
- **Scoring Bias Benchmark** (950 probes across 7 bias dimensions)
- **Bayesian analysis tools**
- **Paper drafts** in LaTeX and Markdown

All at: **[github.com/ssamba1/research-draft](https://github.com/ssamba1/research-draft)**

We're also preparing submissions for ISEF and the NeurIPS High School Projects track.

---

## Want to Run These Experiments Yourself?

Our pipeline is designed to be accessible:

1. Clone the repo
2. Add API keys to your `.env` file  
3. Run `python3 experiment_scheduler.py create --judges claude gpt4o`
4. Run `python3 experiment_scheduler.py run`
5. Explore results with `python3 explore_results.py`

Total API cost: ~$26 for the full experiment. Or use our free synthetic data generator for testing.

---

*This research was conducted as an independent project by two high school students with access to premier AI models for research purposes. All code is available under MIT license. We welcome collaboration and feedback.*
