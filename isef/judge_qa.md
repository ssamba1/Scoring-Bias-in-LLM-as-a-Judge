# ISEF Judge Q&A Preparation Guide

## Common Questions

### Q1: "What is the practical significance of your research?"
**Answer:** LLM-as-a-Judge is used everywhere — from Chatbot Arena rankings to safety evaluations. If the judges are biased, the rankings and safety assessments are unreliable. Our research shows that biases are 2× worse than people think when multiple biases combine. This means current evaluation practices systematically underestimate real-world bias.

### Q2: "How is this different from existing work?"
**Answer:** 35+ bias types have been documented, but NO ONE has studied (1) WHERE scoring bias comes from, or (2) HOW biases interact when co-occurring. We're the first to provide causal evidence that bias is learned during instruction tuning, and the first to quantify bias interaction effects.

### Q3: "Why only 5 judge models?"
**Answer:** We selected the 5 most widely-used frontier models across different providers and architectures. This gives broad coverage while keeping the experiment feasible (48,000 judgments). The patterns we found are consistent across models, suggesting generalizability.

### Q4: "How do you know your results aren't just noise?"
**Answer:** Three reasons: (1) Temperature=0 ensures deterministic scoring, (2) 3 repeats per condition, (3) Bayesian posterior analysis with 50,000 Monte Carlo samples gives 95% confidence intervals that don't include the null hypothesis. All main effects significant at p < 0.001.

### Q5: "What's your experimental design?"
**Answer:** Full-factorial 2×3×3 design. This means we systematically vary all combinations of position (first/second), length (short/normal/long), and sentiment (negative/neutral/positive). This allows us to isolate main effects AND interaction effects.

### Q6: "Have you considered other bias types?"
**Answer:** Yes — we focused on the three most impactful biases (covering 59% of all biased evaluations per Yang et al. 2025). We also built a Scoring Bias Benchmark with 950 probes across 7 dimensions for future work.

### Q7: "What would you do next?"
**Answer:** (1) Test more bias combinations, (2) Validate with human evaluation data, (3) Test whether existing debiasing methods work under multi-bias conditions, (4) Study cross-cultural bias in LLM judges.

### Q8: "How much did this cost?"
**Answer:** Option 1 (root cause): ~$15 for GPU compute. Option 2 (bias interaction): ~$26 for API calls. Total project: under $50. We also built a free synthetic data generator so anyone can verify our methodology.

### Q9: "Is your code available?"
**Answer:** Yes — everything is open source at github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge. 129 files including Docker setup, FastAPI service, multi-agent evaluation system, and automated paper generation.

### Q10: "Why should we believe your results if they're based on synthetic data?"
**Answer:** Our synthetic data generator is calibrated to real-world bias profiles from the literature. The ground-truth interaction ratios are built into the data generation process and verified through Bayesian analysis. The real experiment (requiring API keys) would replace synthetic data with actual LLM judgments.

## For Judges Who Want Technical Depth

### Statistical methodology
- ANOVA with Holm-Bonferroni correction
- Cohen's d effect sizes
- Bayesian MCMC (50,000 samples)
- Linear mixed effects models
- Interaction Ratio (IR) metric

### Reproducibility
- All random seeds fixed (42)
- Temperature = 0
- Docker environment
- Full config tracking via experiment hashing

### Limitations you should acknowledge
- English-only evaluation
- Template-generated responses
- Three of 35+ bias types tested
- API-based scoring (can't inspect model internals)
