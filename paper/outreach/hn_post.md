# Hacker News Post

---

## Title Options (punchy, practical)

**Option A (recommended):**
> Scoring bias in LLM-as-a-Judge: I tested 31 models (54K judgments) and found instruction tuning has opposite effects depending on bias type

**Option B (more clickable):**
> A high school researcher discovered that instruct-tuning fixes one kind of AI judge bias but creates another

**Option C (straightforward):**
> Scoring Bias in LLM-as-a-Judge: 31 models tested, format bias ↓ content bias ↑ in larger RLHF models

---

## Post Description

Key findings from a new paper on scoring bias in LLM-as-a-Judge:

- **Format bias decreases** after instruction tuning: rubric order bias −44%, score ID bias −77% across 9 model families
- **Content bias increases** in larger (3B+) RLHF-trained models: reference answer priming shifts scores by up to 1.58 points on a 5-point scale
- The SFT+DPO family (Mistral 7B) shows a different pattern — suggesting the training method modulates bias
- Bayes factors > 10,000 confirm bias exists across 22 instruct models
- **Format Efficiency Hypothesis**: attention analysis shows format token attention drops 23.7% → 20.8% after instruction tuning, making models more efficient parsers

**Practical takeaways:**
1. Use numeric labels (1-5) for scoring — lowest bias across all tests
2. Test multiple scoring formats before trusting any single result
3. If using reference examples, include both good AND poor exemplars
4. Report format bias and content bias as separate metrics

All code, data, and paper are open-source:
- Interactive demo: https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge (dashboard included)
- Paper + analysis: same repo
- Archived data: https://doi.org/10.5281/zenodo.21361920

The entire study cost less than $3 in API fees and runs on Kaggle T4 GPUs — fully reproducible.
