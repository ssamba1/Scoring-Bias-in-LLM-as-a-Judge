# Frequently Asked Questions (FAQ)

> **20+ questions answered about the research, methodology, results, code, and more.**

---

## Research Questions

### Q1: What is this research about?

**A:** We investigate **scoring bias in LLM-as-a-Judge models** — when AI models used as judges systematically change their scores because of superficial prompt features rather than response quality. Specifically, we compare base (pre-trained only) and instruct (instruction-tuned) variants to understand **where these biases come from**.

### Q2: What is an "LLM-as-a-Judge"?

**A:** An LLM-as-a-Judge is a large language model (like GPT-4, Claude, or Llama) used to evaluate the quality of another AI system's output. Instead of having humans manually grade every response, researchers use LLMs as automated judges. This is common in benchmarks like MT-Bench, AlpacaEval, and Chatbot Arena.

### Q3: What are the three types of scoring bias you studied?

**A:** We studied three probes:
1. **Rubric Order Bias** — Does reversing the scale (1=best vs 1=worst) change scores?
2. **Score ID Bias** — Do different labeling systems (numbers vs letters vs words) change scores?
3. **Reference Answer Bias** — Does showing a sample answer before scoring change scores?

### Q4: Why does this matter? Who cares if AI judges are biased?

**A:** If AI judges are biased, then:
- **Model rankings are unreliable** — A model might rank higher simply because the judge's scoring bias favors it
- **Research conclusions could be wrong** — Papers that use AI judges might draw incorrect conclusions
- **Real-world applications suffer** — AI judges are used in content moderation, education, and healthcare evaluation
- **Progress is harder to measure** — We can't tell if AI systems are actually improving if our measurement tools are broken

### Q5: What's the most important finding?

**A:** The **differential effect**: instruction tuning has opposite effects depending on the bias type.
- **Format biases decrease**: Rubric order bias drops 44%, Score ID bias drops 77%
- **Content bias increases**: Reference answer bias increases 35%

In other words: training models to follow instructions makes them less vulnerable to format-related tricks but more vulnerable to content-related anchors.

### Q6: How many models did you test?

**A:** We tested **31 model variants** across **16 model families** (both open-weight and API-accessible models). This includes 7 model families where we tested both base and instruct variants side by side.

### Q7: How many judgments did you collect?

**A:** We collected **40,500+ individual judgments** — each model scored 80 items across 3 probes with multiple conditions.

### Q8: How much did this cost?

**A:** **Less than $3 USD total.** We used:
- Kaggle's free GPU tier (T4) for running local models
- Free API tiers for cloud models (where available)
- Clever experiment design to minimize API calls
- Efficient inference pipeline with batch processing

---

## Methodology Questions

### Q9: What is Δ (delta)?

**A:** Δ (delta) is our primary measure of bias. It's the difference between the mean score under the treatment (biased) condition and the mean score under the control (normal) condition:

```
Δ = mean(treatment scores) − mean(control scores)
```

- **Δ > 0**: Treatment increases scores (leniency bias)
- **Δ ≈ 0**: No bias detected
- **Δ < 0**: Treatment decreases scores (strictness bias)

### Q10: What is a "bootstrap confidence interval"?

**A:** A bootstrap CI estimates the uncertainty around Δ without making assumptions about the data distribution. We repeatedly resample the data with replacement (10,000 times), compute Δ each time, and find the range that contains 95% of the resampled values. If the CI doesn't contain zero, the bias is statistically significant at the 95% level.

### Q11: What is "flip rate"?

**A:** Flip rate measures how often individual items change score between conditions. For example, if item #1 gets a 3 under normal conditions and a 4 under the treatment, that's a "flip." The flip rate is the fraction of items that flip.

A high flip rate means the bias affects many individual judgments, not just the average.

### Q12: What is Cohen's d?

**A:** Cohen's d is a **standardized effect size** — it measures the magnitude of bias in standard deviation units. This lets us compare bias across different scales and models:
- |d| < 0.2: negligible
- |d| = 0.2–0.5: small
- |d| = 0.5–0.8: medium
- |d| > 0.8: large

### Q13: What is the "delta-of-deltas"?

**A:** The delta-of-deltas (Δ-of-Δ) compares base and instruct model variants:

```
Δ-of-Δ = |Δ_base| − |Δ_instruct|
```

- **Positive Δ-of-Δ**: Instruction tuning reduced bias (base was more biased)
- **Negative Δ-of-Δ**: Instruction tuning increased bias (instruct is more biased)

### Q14: What is the IIAR hypothesis?

**A:** The **Instruction-Induced Attention Redistribution (IIAR)** hypothesis is our proposed explanation for the differential effect. It states:
- Instruction tuning teaches models to focus on **task-relevant** features (content) over **task-irrelevant** features (format), reducing format biases.
- But it also teaches models to **use all available context**, including sample answers, which increases content biases.

### Q15: What statistical tests did you use?

**A:** We used multiple complementary approaches:
1. **Bootstrap confidence intervals** (non-parametric uncertainty estimation)
2. **Cohen's d** (standardized effect size)
3. **Wilcoxon signed-rank test** (non-parametric paired comparison)
4. **Cohen's d_z** (within-subject effect size)
5. **Bayesian analysis** (posterior probability distributions)
6. **Power analysis** (to determine if sample size is adequate)

---

## Results Questions

### Q16: Which model was the most biased?

**A:** Among instruct models, **Score ID bias** has the largest average effect (Δ = 0.68 across 22 models). Individual models show much higher values — for example, Llama 3.1 70B has Score ID bias of Δ = 1.80, meaning scores change by almost 2 points out of 5 just because of how scores are labeled!

### Q17: Which model was the least biased?

**A:** Generally, larger models are less biased, but size alone doesn't guarantee low bias. The models with the lowest overall bias tend to be the larger models (70B+) and models with extensive RLHF training. However, patterns vary by probe — a model might have very low rubric order bias but high reference answer bias.

### Q18: Is bigger always better?

**A:** No. While larger models are **generally** less biased, we found counterexamples. For instance, Hy3-295B (a 295-billion parameter model) has a mean Δ of 0.93 — quite biased. Size helps but doesn't guarantee fairness.

### Q19: Do RLHF and DPO have different effects?

**A:** Yes. Models trained with **RLHF** (Reinforcement Learning from Human Feedback) show the differential effect most strongly: format biases ↓, content biases ↑. Models trained with **DPO** (Direct Preference Optimization), like the Mistral 7B family, show a different pattern, suggesting that the training algorithm itself influences bias development.

### Q20: Are the results statistically significant?

**A:** Yes. For Score ID bias, the reduction after instruction tuning is statistically significant:
- **Wilcoxon signed-rank test**: p = 0.047
- **Cohen's d_z**: 1.08 (large effect)

For Rubric Order bias, the reduction is not statistically significant at current N (7 paired comparisons) — we need more model families to increase power.

### Q21: Could the biases come from the evaluation items rather than the models?

**A:** We controlled for this by using the same 80 items across all models and conditions. The items were drawn from diverse domains (math, coding, creative writing, reasoning, etc.) to ensure results aren't domain-specific. Our domain analysis shows the differential effect holds across domains.

---

## Code and Reproducibility Questions

### Q22: How do I install the package?

**A:** The easiest way:
```bash
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge
pip install -r requirements.txt
pip install -e .
python tests/test_all.py
```

### Q23: How do I reproduce the paper's results?

**A:** Use the pre-computed results in `results_rootcause/`:
```bash
python results_rootcause/run_all_analyses.py
```
Or use the Makefile:
```bash
make reproduce-all
```

### Q24: What Python version is required?

**A:** Python 3.11 or higher. The package uses modern Python features including `from __future__ import annotations` for PEP 604 type hints.

### Q25: I don't have a GPU. Can I still run this?

**A:** Yes. The analysis code is purely CPU-based. Only the model inference step requires a GPU. You can:
1. **Use the synthetic data** at `data/raw/` for testing
2. **Use the pre-computed results** at `results_rootcause/`
3. **Run on Kaggle/Colab** for free GPU access
4. **Use API-based models** instead of local models

### Q26: How do I add a new model?

**A:** See the [Contributors Guide](contributors.md) for detailed instructions. The basic steps:
1. Add inference code to `results_rootcause/`
2. Run all 3 probes × 3 conditions × 50 items
3. Save as structured JSON
4. Update model cards in `data/model_cards/`

### Q27: What are the main Python scripts?

**A:** The key entry points are:
- `cli.py` — Command-line interface for the analysis pipeline
- `scoring_bias/analysis.py` — Core analysis functions
- `scoring_bias/visualization.py` — Figure generation
- `scoring_bias/models.py` — Data structures
- `scoring_bias/metrics.py` — Statistical metrics
- `dashboard.py` — Interactive dashboard
- `api.py` — FastAPI backend

### Q28: How do I run the tests?

**A:**
```bash
# Run all tests
python tests/test_all.py

# Or with pytest
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Q29: What if I get import errors for `scoring_bias`?

**A:** Run `pip install -e .` from the project root. This installs the package in development mode, making `from scoring_bias import ...` work.

### Q30: Can I use this for my own research?

**A:** Absolutely! The code is MIT licensed, and the data is CC-BY 4.0. We encourage reuse. Please cite our paper if you build on this work (see [Citation Guide](citation_guide.md)).

---

## General Questions

### Q31: Will you release the paper on arXiv?

**A:** Yes, an arXiv preprint is planned. Stay tuned for the link.

### Q32: Is the data publicly available?

**A:** Yes. All evaluation items, model cards, and results are included in the repository. A Zenodo archive is also available at [10.5281/zenodo.21361920](https://doi.org/10.5281/zenodo.21361920).

### Q33: Can I contribute to this project?

**A:** Yes! We welcome contributions. See the [Contributors Guide](contributors.md) for details.

### Q34: What are the limitations of this study?

**A:** Key limitations include:
1. **Limited probe types**: We tested only 3 of many possible scoring bias types
2. **Single language**: All items are in English
3. **Limited model access**: Some models (GPT-4, Claude) are only accessible via API
4. **Power constraints**: Only 7 families had both base and instruct variants
5. **Score range**: We used 1–5 scales; results may not generalize to other scales

### Q35: What's next for this research?

**A:** Planned future work includes:
1. Testing 12 bias probes instead of 3
2. Adding 5 languages
3. Developing targeted mitigation strategies (calibration, ensembling, anti-bias prompting)
4. Human baseline studies
5. Cross-lingual evaluations

### Q36: Where can I learn more?

**A:** Check out:
- [User Guide](user_guide.md) — Complete guide to the codebase
- [Educational Explainer](educational_explainer.md) — Accessible explanation for students
- [Methodology Tutorial](methodology_tutorial.md) — Step-by-step walkthrough
- [Paper](paper/camera_ready_full.tex) — Full academic paper
- [Interactive Dashboard](dashboard/interactive_paper.html) — Explore results visually
