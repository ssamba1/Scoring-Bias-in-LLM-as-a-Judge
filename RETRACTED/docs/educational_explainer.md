# Educational Explainer  Scoring Bias in LLM-as-a-Judge

> **An accessible explanation of scoring bias in AI judges, written for high school students (ISEF audience).**
>
> *No PhD required. Just curiosity.*

---

## What Is an LLM-as-a-Judge?

Imagine you're a teacher grading a hundred essays. You read each one, think about it, and give a score from 1 to 5. Now imagine that instead of you, a robot teacher does the grading  but this robot learned how to grade by reading billions of examples from the internet.

That's an **LLM-as-a-Judge**.

**LLM** stands for "Large Language Model"  a type of AI that's really good at understanding and generating text. Companies like OpenAI (GPT-4), Google (Gemini), Meta (Llama), and Anthropic (Claude) build these models. People use them as judges to automatically evaluate the quality of other AI systems.

Here's the problem: **these robot judges have biases**. They don't always grade fairly. Sometimes they're influenced by things that have nothing to do with the quality of the answer they're supposed to evaluate.

---

## What Is Scoring Bias?

**Scoring bias** is when a judge (human or AI) gives a different score because of something that shouldn't matter.

### Real-World Examples

**Human judges have biases too:**

- A teacher grades an essay higher if it uses fancy vocabulary  even if the content is weak.
- A judge at a science fair favors projects with expensive equipment over simpler ones.
- A music contest judge gives higher scores to performers who go first or last.

**AI judges have their own biases:**

- An AI judge gives different scores depending on whether 1 = best or 1 = worst (*rubric order bias*).
- An AI judge scores differently if the labels are numbers (1–5) vs letters (A–E) vs words (excellent–terrible) (*score ID bias*).
- An AI judge changes its score depending on whether a sample answer is shown first (*reference answer bias*).

These are not bugs in the traditional sense  **they are learned behaviors**. The AI picked them up during training, just like humans pick up biases from their environment.

---

## Why Does It Matter?

AI judges are used everywhere:

- **Chatbot Arena**  People vote on which chatbot gives better answers
- **MT-Bench**  A benchmark that uses AI to evaluate other AI
- **AlpacaEval**  Automated evaluation of instruction-following models
- **Research papers**  Many papers use AI judges to compare their models against competitors

If the judges are biased, then **model rankings are unreliable**. A model might appear better or worse than it actually is  just because the judge has a scoring bias.

Think about it like this: if you're trying to figure out who's the best basketball player, but the referee has a grudge against tall players, the results won't be fair. The same thing happens with AI judges.

This is especially important as AI systems become more powerful and widespread. We need reliable ways to measure how good they are.

---

## How Do We Measure Scoring Bias?

Our research uses a **perturbation framework**. Here's how it works:

### Step 1: Create a Normal Setup

Ask the AI judge to evaluate a response using a standard grading rubric:

> **Prompt**: "Score this response from 1–5, where 1 = worst and 5 = best."

### Step 2: Create a Perturbed Setup

Ask the same question, but change just one thing about the prompt that **shouldn't matter**:

> **Perturbed Prompt**: "Score this response from 1–5, where 5 = worst and 1 = best."

Wait  that seems like it should matter, right? Actually, the quality of the response hasn't changed. Only the direction of the scale has changed. A fair judge should figure this out and adjust accordingly.

### Step 3: Compare the Scores

If the judge gives scores that are systematically different between the two setups, that's **scoring bias**.

We measure this with a number called **Δ (delta)**:

```
Δ = average score under perturbed condition − average score under normal condition
```

- **Δ = 0** → No bias (perfectly fair)
- **Δ > 0** → Scores went up when we changed the prompt (leniency bias)
- **Δ < 0** → Scores went down (strictness bias)

### The Three Biases We Tested

| Bias Probe | Normal Condition | Perturbed Condition | What We're Testing |
|------------|-----------------|---------------------|-------------------|
| 🔢 **Rubric Order** | 1 = worst, 5 = best | 1 = best, 5 = worst | Does the direction of the scale matter? |
| 🏷️ **Score ID** | Numbers (1–5) | Letters (A–E) or Words | Does the format of scores matter? |
| 📋 **Reference Answer** | No example shown | Example answer shown first | Does showing a sample change the scoring? |

---

## How Base vs Instruct Comparison Works

Here's the really interesting part of our research.

Large language models go through two main stages of training:

### Stage 1: Pre-training (Base Models)

The AI reads billions of texts from the internet  books, articles, Wikipedia, Reddit, code repositories. It learns patterns of language, facts about the world, and how to complete sentences.

At this stage, the model is called a **base model**. It can generate text, but it doesn't follow instructions very well. If you ask it a question, it might answer or it might just continue writing whatever it was "thinking."

**Examples**: Llama 3.1 8B (base), Gemma 2 27B (base), Qwen 2.5 32B (base)

### Stage 2: Instruction Tuning (Instruct Models)

The base model undergoes additional training:

1. **SFT (Supervised Fine-Tuning)**  Trained on thousands of examples of humans giving instructions and providing good responses.
2. **RLHF (Reinforcement Learning from Human Feedback)**  Trained using feedback from humans about which responses are better.

The result is an **instruct model** that follows instructions well, is helpful, and (ideally) is aligned with human values.

**Examples**: Llama 3.1 8B Instruct, Gemma 2 27B IT, Qwen 2.5 32B Instruct

### The Key Question

**Do scoring biases come from pre-training (Stage 1) or instruction tuning (Stage 2)?**

If a bias is present in the base model, it was learned during pre-training.
If a bias appears only after instruction tuning, it was learned during that process.
If a bias changes (increases or decreases) after instruction tuning, the process affects it.

This question has never been systematically studied before our work.

---

## What We Found: The Differential Effect

Our main discovery is something we call the **differential effect**:

> **Instruction tuning reduces format biases but increases content biases.**

### Format Biases Decrease

| Bias Type | Base Models (Before) | Instruct Models (After) | Change |
|-----------|---------------------|----------------------|--------|
| Rubric Order | Δ = 2.85 | Δ = 1.59 | **−44%** |
| Score ID | Δ = 0.67 | Δ = 0.15 | **−77%** |

This makes sense! Instruction tuning teaches models to pay attention to the format of prompts and follow instructions carefully. So models learn not to be fooled by reversed scales or different labeling systems.

### Content Biases Increase

| Bias Type | Base Models (Before) | Instruct Models (After) | Change |
|-----------|---------------------|----------------------|--------|
| Reference Answer | Δ = 0.88 | Δ = 1.19 | **+35%** |

Wait  why would instruction tuning make this worse?

Our hypothesis: instruction tuning teaches models to be more helpful and to use context. When you show a model a sample answer ("here's what a good answer looks like"), the model wants to be helpful by basing its score on that example. But this actually introduces bias  the model becomes too influenced by the example.

### Summary

```
              Format Biases          Content Biases
              (Rubric, Score ID)     (Reference Answer)
                 ↓                         ↑

Before (Base)    HIGH                     MODERATE
After (Instruct) LOW                      HIGHER

         Instruction tuning has OPPOSITE effects
         depending on the type of bias!
```

---

## Our Hypothesis: The IIAR (Instruction-Induced Attention Redistribution)

Why does this differential effect happen? We propose the **Instruction-Induced Attention Redistribution (IIAR)** hypothesis:

1. **Format biases** decrease because instruction tuning teaches models to focus on **task-relevant features** (the actual content to evaluate) rather than **task-irrelevant features** (how the rubric is formatted).

2. **Content biases** increase because instruction tuning teaches models to **use all available context**  including sample answers. This is usually helpful, but when the sample answer creates an anchor, the model over-relies on it.

Think of it like this: instruction tuning makes the model a "better" instruction-follower. But being a better instruction-follower means paying more attention to everything in the prompt  including things that might bias the evaluation.

---

## How We Ran the Experiment

### The Setup

- **31 model variants** from **16 families** (Llama, Gemma, Qwen, Mistral, DeepSeek, etc.)
- **80 evaluation items** across diverse domains
- **3 probes** × **multiple conditions** per item
- **40,500+ judgments** total

### The Cost

**Less than $3 USD total.**

We achieved this by using student-friendly platforms:
- **Kaggle's free GPU tier** for running local models (T4 GPU)
- **Free API tiers** for cloud models
- **Clever experiment design** to minimize the number of API calls needed

### The Analysis

For each model-probe pair, we computed:
1. **Δ (delta)**  the mean bias
2. **95% CI**  bootstrap confidence intervals
3. **Flip Rate**  fraction of items where scores changed
4. **Cohen's d**  standardized effect size
5. **Wilcoxon signed-rank test**  statistical significance
6. **Bayesian analysis**  probability that one group is more biased

---

## Key Findings in Plain Language

### Finding 1: Format Biases Drop After Training
Score ID bias drops 77% after instruction tuning. Models learn that "A" and "5" and "Excellent" should mean roughly the same thing.

### Finding 2: Content Bias Gets Worse
Reference answer bias increases 35% in larger RLHF-trained models. Showing a sample answer has a bigger effect on instructed models than on base models.

### Finding 3: Score ID Bias Is the Biggest Problem
Across all 22 instruct models tested, Score ID bias has an average effect of Δ = 0.68. For Llama 3.1 70B, it's as high as Δ = 1.80  meaning scores change by almost 2 points out of 5 just because of how the scores are labeled!

### Finding 4: RLHF Models Show the Pattern Most Strongly
Models trained with RLHF (Reinforcement Learning from Human Feedback) show the clearest differential effect: format biases go way down, content biases go way up. Models trained with DPO (Direct Preference Optimization) show a different pattern.

### Finding 5: Bigger Is Not Always Better
Larger models are generally less biased, but size alone doesn't guarantee low bias. For example, a very large 295B model (Hy3-295B) has a mean Δ of 0.93  quite biased.

### Finding 6: The Effect Is Statistically Significant
For Score ID bias, the reduction is statistically significant (Wilcoxon p = 0.047, Cohen's d_z = 1.08  that's a **large** effect).

---

## Why This Matters for Society

As AI systems become more integrated into our lives, we need reliable ways to evaluate them:

- **Education**: AI tutors that grade student work must be fair
- **Healthcare**: AI diagnostic tools must be evaluated without bias
- **Content moderation**: AI systems that flag harmful content must judge consistently
- **Scientific research**: AI judges used in papers must give reliable results

Understanding where scoring biases come from is the first step to fixing them. Our research shows that the solution isn't simple  the same training process that fixes some biases can make others worse. But knowing this, we can develop targeted mitigation strategies.

---

## Glossary for Students

| Term | Simple Definition |
|------|------------------|
| **LLM** | A large language model  AI trained on lots of text |
| **Base model** | An AI before it's trained to follow instructions |
| **Instruct model** | An AI that's been trained to follow instructions well |
| **Bias** | A systematic error  consistently favoring one thing over another |
| **Delta (Δ)** | A number that measures how much bias there is |
| **Perturbation** | A small change made on purpose |
| **SFT** | Supervised Fine-Tuning  training on examples |
| **RLHF** | Training using feedback from humans |
| **Cohen's d** | A measure of how big an effect is |
| **Statistical significance** | A mathematical way to check if a result is real or just random |

---

## Want to Learn More?

- Read our full paper: [`paper/camera_ready_full.tex`](../paper/camera_ready_full.tex)
- Try the interactive dashboard: [`dashboard/interactive_paper.html`](../dashboard/interactive_paper.html)
- Explore the code: [`src/scoring_bias/`](../src/scoring_bias/)
- Run the experiments yourself: See [Setup Guide](setup_guide.md)

---

*This explainer was written for the ISEF (International Science and Engineering Fair) audience  students in grades 9–12 who want to understand cutting-edge AI research without a computer science degree.*
