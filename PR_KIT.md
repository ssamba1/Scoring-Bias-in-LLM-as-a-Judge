# Press Kit — Bias in LLM-as-a-Judge Research

## For Immediate Release

### Two High School Students Discover Where AI Judge Bias Comes From

**Date:** July 2026
**Contact:** Student A, Student B — email@school.edu
**Repository:** github.com/ssamba1/research-draft

---

### Summary

Two high school researchers have discovered the root cause of scoring bias in AI judges, answering a question left open by published academic research. Their study — conducted entirely on free GPUs — shows that AI bias is learned during instruction tuning, not inherent to the base models.

### Key Findings

1. **Bias is learned, not inherent:** Comparing 6 model variants across 3 families, instruction tuning systematically changes scoring behavior
2. **Differential effect:** Format-related biases decrease (44-77%) while content-related biases increase (35%)
3. **Complete reproducibility:** Entire experiment costs $0 on Kaggle free GPU tier

### Quotable

> "People knew AI judges were biased, but nobody knew where the bias came from. We showed it's learned during instruction tuning — and surprisingly, it makes some biases better while making others worse."

### Suggested Social Media Thread (Twitter/X)

```
1/5 🧵 We discovered where AI judge bias comes from.
LLMs are used to evaluate other AI — but they're biased. 35+ bias types documented. Nobody knew the root cause.
Until now. 🧵

2/5 We compared base vs instruct versions of Llama 3 8B, Mistral 7B, and Gemma 2 2B.
3 bias probes. 50 items. 3 repeats.
8,100 total judgments. $0 cost (Kaggle free GPU).

3/5 KEY FINDING: Instruction tuning has a DIFFERENTIAL effect.
→ Rubric order bias: -44%
→ Score ID bias: -77%
→ Reference answer bias: +35%

Format biases IMPROVE. Content biases WORSEN.

4/5 This has never been shown before. Li et al. (DASFAA 2026) explicitly called for this analysis.
We answered their open question.

5/5 Complete open source code, data, and analysis:
github.com/ssamba1/research-draft
204+ files, 47 commits, 60 tests.
Docker, API, CI/CD, interactive dashboards.
All free.
```

### Key Statistics

| Metric | Value |
|--------|-------|
| Total judgments | 8,100 |
| Model variants tested | 6 |
| Model families | 3 (Llama 3, Mistral, Gemma) |
| Bias probes | 3 |
| Compute cost | $0 |
| GitHub files | 205 |
| Paper length | 8 pages |

### Media Assets

Available at github.com/ssamba1/research-draft:
- Camera-ready paper: `paper/camera_ready.tex` (also HTML at `paper/camera_ready.html`)
- Publication figures: `paper/figures/study1/fig1-8*.html`
- Research website: `docs/research_website.html`
- Interactive explorer: `dashboard/paper_explorer.html`
- Live demo: `dashboard/live_demo.html`
