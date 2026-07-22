# Glossary

> **50+ terms defined in plain language.**
>
> Technical terms from the paper, methodology, and codebase, with cross-references.

---

## A

### Attention Redistribution
The hypothesized mechanism by which instruction tuning changes how models allocate attention across prompt features. See also: [IIAR hypothesis](#iiar-hypothesis).

### Average Delta
The mean bias delta (Δ) across all probes for a single model. A model's overall bias score. See also: [Δ (Delta)](#δ-delta).

---

## B

### Base Model
A language model that has undergone only pre-training (next-token prediction on large text corpora) without instruction tuning. Base models can generate text but don't follow instructions well. See also: [Instruct Model](#instruct-model), [Pre-training](#pre-training).

### Bayesian Analysis
A statistical approach that treats parameters as random variables with probability distributions. In our paper, Bayesian analysis provides the probability that one group is more biased than another. See also: [Frequentist Statistics](#frequentist-statistics).

### Bias
A systematic error or deviation from a fair, accurate judgment. In our context, scoring bias means the model's scores are influenced by factors unrelated to response quality. See also: [Scoring Bias](#scoring-bias).

### Bias Landscape
A visualization showing all tested models sorted by their bias magnitude, with individual probe deltas shown as grouped bars. See `plot_bias_landscape()`.

### Bootstrap Confidence Interval
A non-parametric method for estimating uncertainty by repeatedly resampling data with replacement. We use 10,000 resamples to compute 95% CIs for delta. See also: [Confidence Interval](#confidence-interval).

---

## C

### Chatbot Arena
A platform where users compare chatbot responses side-by-side and vote for the better one. Uses human evaluation rather than LLM-as-a-Judge.

### Cohen's d
A standardized measure of effect size. It expresses the difference between two groups in standard deviation units. Interpretation: |d|<0.2 negligible, 0.2–0.5 small, 0.5–0.8 medium, >0.8 large. See `cohens_d()`.

### Cohen's d_z
A variant of Cohen's d for within-subject (paired) designs. Used in our analysis of base vs instruct comparisons.

### Condition
One variant of a probe. For example, the Rubric Order probe has "normal" and "reversed" conditions. Each model scores each item under each condition.

### Confidence Interval (CI)
A range of values that likely contains the true population parameter. A 95% CI means that if we repeated the experiment many times, 95% of CIs would contain the true value. See also: [Bootstrap Confidence Interval](#bootstrap-confidence-interval).

### Content Bias
Bias related to the content of prompts  what information is included. Reference answer bias is a content bias because it involves showing an example answer. See also: [Format Bias](#format-bias), [Reference Answer Bias](#reference-answer-bias).

---

## D

### Δ (Delta)
Our primary measure of bias. Computed as `mean(treatment scores) − mean(control scores)`. Positive Δ means leniency bias (scores increase), negative Δ means strictness bias (scores decrease). See `compute_delta()`.

### Δ-of-Δ (Delta of Deltas)
The difference between base and instruct absolute deltas: `|Δ_base| − |Δ_instruct|`. Positive means instruction tuning reduced bias. See `compute_base_instruct_comparison()`.

### Differential Effect
Our main finding: instruction tuning has opposite effects on different types of bias. Format biases (rubric order, score ID) decrease, while content biases (reference answer) increase.

### DPO (Direct Preference Optimization)
An alternative to RLHF for aligning language models. Uses direct optimization on preference pairs rather than training a separate reward model. See also: [RLHF](#rlhf).

---

## E

### Effect Size
A quantitative measure of the magnitude of a phenomenon. Unlike p-values, effect sizes are independent of sample size. See also: [Cohen's d](#cohens-d).

### Evaluation Item
A single query-response pair that the LLM judge scores. We used 80 items across diverse domains.

---

## F

### Family
A group of models sharing the same underlying architecture and training approach. Examples: Llama, Gemma, Qwen, Mistral, DeepSeek. See `family_from_model()`.

### Flip Rate
The fraction of items where the score changes between conditions by at least a threshold (default: 0.5). A high flip rate means bias affects many individual judgments. See `compute_flip_rate()`.

### Format Bias
Bias related to how information is presented rather than what information is included. Rubric order bias and score ID bias are format biases. See also: [Content Bias](#content-bias).

### Frequentist Statistics
The traditional approach to statistical inference where parameters are fixed unknown values and probability refers to long-run frequencies. Our bootstrap CIs and Wilcoxon tests are frequentist. See also: [Bayesian Analysis](#bayesian-analysis).

---

## G

### GPU (Graphics Processing Unit)
Specialized hardware originally designed for graphics, now widely used for AI/ML computations because of their parallel processing capabilities. We used T4 GPUs on Kaggle.

---

## H

### HuggingFace
A platform and library for sharing and using pre-trained machine learning models. We use it to download model weights for local inference.

---

## I

### IIAR Hypothesis
**Instruction-Induced Attention Redistribution hypothesis**: our proposed explanation for the differential effect. Instruction tuning changes how models distribute attention  focusing more on task-relevant features (reducing format bias) but also more on all contextual information (increasing content bias).

### Inference (in ML)
The process of using a trained model to make predictions. In our context, inference means asking an LLM to produce a score for a given item.

### Inference Executor
A module (`inference_executor.py`) that handles running model inference for experiments, managing API calls, retries, and result collection.

### Instruct Model
A base model that has undergone instruction tuning (SFT + RLHF or DPO), making it capable of following human instructions effectively. See also: [Base Model](#base-model), [Instruction Tuning](#instruction-tuning).

### Instruction Tuning
The process of further training a pre-trained language model to follow instructions. Typically involves SFT followed by RLHF or DPO. See also: [SFT](#sft), [RLHF](#rlhf).

---

## J

### Judgment
A single score produced by one model for one item under one condition. Our study collected 40,500+ judgments.

---

## K

### Kaggle
A platform for data science competitions that also provides free GPU resources. We used Kaggle's T4 GPUs for running local model inference.

---

## L

### LLM (Large Language Model)
A neural network model trained on vast amounts of text data to understand and generate human-like text. Examples: GPT-4, Llama 3, Gemini, Claude.

### LLM-as-a-Judge
The practice of using a language model to evaluate the quality of text outputs, typically from other AI systems. Used in benchmarks like MT-Bench and AlpacaEval.

### Landscape Plot
See [Bias Landscape](#bias-landscape).

### Leniency Bias
A bias that causes scores to be higher than they should be (positive Δ). See also: [Strictness Bias](#strictness-bias).

---

## M

### MAD (Mean Absolute Deviation)
The average absolute deviation of scores from a central point (typically the mean). Measures the spread or variability of scores. See `mean_absolute_deviation()`.

### Matplotlib
The Python plotting library used for all figures in this project. We use the "Agg" backend for non-interactive, server-side rendering.

### Mean
The arithmetic average of a set of values. Computed as `sum(values) / len(values)`.

### Model Card
A standardized document describing a model's intended use, limitations, and evaluation results. Our model cards are in `data/model_cards/all_models.md`.

### Model Profile
A data structure (`ModelProfile`) that holds all bias analysis results for a single model. Contains probe results, family, size, and aggregate statistics.

### Multi-Stage Build
A Docker optimization technique that uses multiple FROM statements to separate build dependencies from runtime dependencies, resulting in smaller final images.

---

## N

### Normal Condition
The baseline (control) condition for a probe. For example, the normal rubric order condition uses a standard 1-5 scale where 1=worst, 5=best.

---

## O

### OpenRouter
A service that provides API access to many different language models through a single interface. We used OpenRouter to access 22 instruct models.

### Open-Weight Model
A model whose weights are publicly released, allowing local inference. Examples: Llama 3, Gemma 2, Qwen 2.5, Mistral.

---

## P

### Paired Deltas
Per-item differences between treatment and control scores. Used as input to bootstrap resampling.

### Percentile CI
A confidence interval computed by taking the α/2 and 1−α/2 percentiles of the bootstrap distribution. For a 95% CI, these are the 2.5th and 97.5th percentiles.

### Perturbation Framework
Our methodology: make small, controlled changes to prompts (perturbations) and measure the effect on scores. If a change that shouldn't matter does affect scores, that's evidence of bias.

### Pooled Standard Deviation
A weighted average of the standard deviations of two groups, used in computing Cohen's d. See `pooled_std()`.

### Pre-training
The first stage of LLM training: learning to predict the next token on a large corpus of text. This is where base models come from.

### Probe
A specific test for a type of scoring bias. Each probe has a normal condition and one or more perturbed conditions. Our three probes: rubric order, score ID, reference answer.

### Probe Breakdown
A visualization showing score distributions for each condition within a probe, typically as box plots. See `plot_probe_breakdown()`.

### ProbeResult
A data structure holding the results of one probe for one model, including delta, CI, flip rate, and condition scores.

---

## R

### Reference Answer Bias
A content bias where the model's score is influenced by whether a sample answer is shown before scoring. Our third probe type.

### RLHF (Reinforcement Learning from Human Feedback)
A training method where a model is fine-tuned using a reward model trained on human preferences. Used after SFT to align models with human values. See also: [SFT](#sft), [DPO](#dpo), [Instruction Tuning](#instruction-tuning).

### Rubric Order Bias
A format bias where changing the direction of the scoring scale (1=best vs 1=worst) affects scores. Our first probe type.

---

## S

### Score
A numerical rating assigned by a model to an evaluation item. On our 1-5 scale: 1=worst, 5=best.

### Score ID Bias
A format bias where changing the labeling system (numbers vs letters vs words) affects scores. Our second probe type.

### ScoreRecord
A data structure representing a single score from one model on one item under one condition.

### Scoring Bias
A systematic tendency for an LLM judge to assign scores that are influenced by factors unrelated to the quality of the response being evaluated.

### SFT (Supervised Fine-Tuning)
Training a model on human-written examples of following instructions. The first stage of instruction tuning, typically followed by RLHF or DPO.

### Size (of Model)
The number of parameters in a model, typically expressed in billions (B). Examples: 7B, 8B, 27B, 32B, 70B, 295B.

### Statistical Power
The probability that a test will detect an effect when one exists. Our power analysis showed we need more base-instruct pairs (N > 11) for some comparisons.

### Strictness Bias
A bias that causes scores to be lower than they should be (negative Δ). See also: [Leniency Bias](#leniency-bias).

---

## T

### T4 GPU
An NVIDIA GPU with 16GB VRAM, commonly available on free tiers of cloud services like Kaggle and Colab.

### Treatment Condition
The perturbed condition for a probe. For example, the "reversed" condition for rubric order bias. Scores from the treatment condition are compared to the control (normal) condition.

---

## W

### Wilcoxon Signed-Rank Test
A non-parametric statistical test for comparing two paired groups. Used in our analysis to test whether instruction tuning significantly changes bias. See also: [Frequentist Statistics](#frequentist-statistics).

---

## Z

### Zenodo
A general-purpose open-access repository for research outputs. We use it to archive our code and data with a persistent DOI: 10.5281/zenodo.21361920.

---

## Quick Reference

| Abbreviation | Full Form |
|-------------|-----------|
| **CI** | Confidence Interval |
| **Δ** | Delta (bias measure) |
| **DPO** | Direct Preference Optimization |
| **GPU** | Graphics Processing Unit |
| **IIAR** | Instruction-Induced Attention Redistribution |
| **LLM** | Large Language Model |
| **MAD** | Mean Absolute Deviation |
| **RLHF** | Reinforcement Learning from Human Feedback |
| **SFT** | Supervised Fine-Tuning |
| **SGD** | Stochastic Gradient Descent |
| **ML** | Machine Learning |
| **NLP** | Natural Language Processing |
| **API** | Application Programming Interface |
| **CSV** | Comma-Separated Values |
| **JSON** | JavaScript Object Notation |
| **DOI** | Digital Object Identifier |
| **arXiv** | Preprint repository for scientific papers |
| **ISEF** | International Science and Engineering Fair |
| **PDF** | Portable Document Format |
| **PNG** | Portable Network Graphics |
| **SVG** | Scalable Vector Graphics |

---

## Cross-References

> Terms marked with → have their own entry in this glossary.

| Related Terms | See Also |
|--------------|----------|
| Base → Instruct → Pre-training → SFT → RLHF → DPO | [Instruction Tuning](#instruction-tuning) |
| Delta → Flip Rate → Cohen's d → CI | [Scoring Bias](#scoring-bias) |
| Rubric Order → Score ID → Reference Answer | [Probe](#probe) |
| Format Bias → Content Bias | [Differential Effect](#differential-effect) |
| Bootstrap CI → Percentile CI | [Confidence Interval](#confidence-interval) |
| Bias Landscape → Probe Breakdown | [Visualization](#bias-landscape) |
| Leniency → Strictness | [Δ (Delta)](#δ-delta) |
| Model Profile → ProbeResult → ScoreRecord | [Data Structures](#model-profile) |
