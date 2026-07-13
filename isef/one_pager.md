# Project One-Pager — Bias in LLM-as-a-Judge

## Two Studies on the Origins and Interactions of Scoring Bias in AI Evaluation

### The Problem
AI models are used to evaluate other AI models (LLM-as-a-Judge). These judges have 35+ documented biases that affect up to 31% of evaluations. But nobody knew where these biases come from or what happens when multiple biases occur simultaneously.

### Our Research

**Study 1: Root Cause** — *Where does scoring bias come from?*
- Compared base (pre-trained) vs instruct (fine-tuned) models
- Found: bias emerges during **instruction tuning** (2.09× amplification)
- Implication: fix instruction tuning, not pre-training

**Study 2: Bias Interactions** — *Do biases compound or cancel?*
- Tested 5 frontier models × 3,200 items = 48,000 judgments
- Found: biases **compound non-additively** (IR up to 2.10×)
- Implication: single-bias tests underestimate real-world bias by ~2×

### Key Findings
1. ✓ Scoring bias is learned during instruction tuning (not pre-training)
2. ✓ Position + verbosity biases compound to 1.5-2.1× additive expectations
3. ✓ Model-specific interaction patterns (Gemini = additive; others = compounding)
4. ✓ Causal methodology validated (Pan et al. 2025 replication)

### Methods
- Full-factorial 2×3×3 experimental design
- 5 frontier judge models (Claude, GPT-4o, Gemini, DeepSeek, Llama 3)
- 3 model families for root cause (Llama 3, Mistral, Gemma 2)
- Bayesian MCMC, ANOVA, Cohen's d, Interaction Ratio
- All code: github.com/ssamba1/research-draft

### Impact
- **AI Safety**: Worst-case biases 2× worse than measured
- **Benchmarks**: Rankings may contain systematic bias
- **Practice**: Test combinations, not individuals
- **Research**: Two verified untouched gaps now filled

### Budget & Timeline
- Cost: $10-26 (GPU or API)
- Duration: 3-5 weeks
- Target: ISEF 2027, arXiv preprint, NeurIPS HS Track

### Contact
Student A, Student B · High School Name
github.com/ssamba1/research-draft
