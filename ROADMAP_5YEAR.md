# 5-Year Research Program Blueprint

## From Current Project to Lasting Impact

---

## Phase 0: Foundation (Complete — 2026)
**Two verified untouched gaps filled. Complete infrastructure built.**

### Deliverables
- [x] 160 files, 31 commits, 73 tests
- [x] 9 papers (LaTeX + Markdown)
- [x] Complete experimental pipelines
- [x] Docker + FastAPI + CI/CD
- [x] ISEF materials
- [x] Theoretical framework (4 original theorems)

---

## Phase 1: Execution (3-5 weeks — 2026)
**Run real experiments, publish results.**

### Tasks
| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Add API keys, run pilots | Verified pipeline |
| 2 | Run all 5 judges | 48,000 real judgments |
| 3 | Analysis + figures | Real interaction ratios |
| 4 | Write final paper | arXiv submission |
| 5 | Submit to ISEF + NeurIPS HS | Applications |

### Resources Needed
- API keys: Claude, GPT-4o, Gemini, DeepSeek, Llama
- Budget: $26-50
- Time: 3-5 weeks

---

## Phase 2: Extension (6-12 months — 2026-2027)
**Expand to more models, bias types, and domains.**

### Research Questions
1. Do bias interactions extend to authority bias, bandwagon bias, self-preference bias?
2. Do interaction patterns hold across different prompt templates?
3. How do interaction ratios change with model scale (7B → 70B → 405B)?
4. Do cross-cultural biases show the same interaction patterns?

### Models to Add
- Qwen 2.5 (7B, 32B, 72B)
- DeepSeek V2
- OLMo
- Command R+
- GPT-4.1, Claude 4

### Budget: $100-500

---

## Phase 3: Mechanistic Understanding (1-2 years — 2027-2028)
**Open the black box — identify the neural circuits responsible for bias interactions.**

### Approach
1. Use activation patching to identify attention heads responsible for position bias
2. Use causal tracing to find where verbosity bias enters the computation
3. Use SVD decomposition of attention patterns to measure $\rho_{ij}$
4. Design minimal interventions that reduce $\rho_{ij}$ without affecting instruction-following

### Tools
- TransformerLens
- Activation patching
- Logit lens
- Sparse autoencoders

### Budget: $1,000-5,000 (compute)

### Target Publication
- ICML 2027
- NeurIPS 2027

---

## Phase 4: Mitigation Development (2-3 years — 2028-2029)
**Build practical tools that reduce bias in production LLM judges.**

### Products
1. **Bias-Aware Evaluator (BAE)**: An LLM judge that is explicitly trained to be bias-robust
2. **Bias Audit Service**: API that evaluates any LLM judge for all 35+ bias types and interaction effects
3. **Bias Compensator**: Post-hoc correction tool that adjusts biased scores
4. **FairBench**: Standardized benchmark for evaluating bias in LLM judges

### Methods to Explore
- Contrastive training on biased vs unbiased prompts
- Attention regularization to reduce $\rho_{ij}$
- Multi-objective optimization for instruction-following × bias robustness
- Meta-learning for bias-aware evaluation

### Target Publication
- ACL 2028
- EMNLP 2028

---

## Phase 5: Deployment (3-5 years — 2029-2031)
**Make bias-aware evaluation the industry standard.**

### Goals
1. Deploy Bias Audit Service as a public API
2. Integrate with major evaluation platforms (Chatbot Arena, AlpacaEval, MT-Bench)
3. Establish standards for bias reporting in AI evaluations
4. Publish comprehensive bias reports for all major LLM judges
5. Advocate for bias-aware evaluation practices

### Impact Metrics
- Number of evaluations using bias-aware methods
- Reduction in reported bias incidents
- Adoption by major AI labs
- Citations of our unified theory

### Funding Sources
- Academic grants (NSF, NIH)
- Industry partnerships (Anthropic, OpenAI, Google, Meta)
- Open source donations

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|------------|
| Scooped on interaction effects | Low | High | Submit to arXiv immediately |
| API costs increase | Medium | Medium | Use free tiers + synthetic data |
| Model availability changes | Low | Medium | Pin model versions in code |
| ISEF not accepted | Medium | Medium | Multiple backup venues |
| Research shows bias worse than expected | Low | High | Transparency is the goal — worse bias means more impact |

---

## Key Milestones

| Year | Milestone | Deliverable |
|------|-----------|-------------|
| 2026 | Foundation | Current repository (160 files) |
| 2026 | Publication | arXiv paper + ISEF submission |
| 2027 | Extension | More models, bias types, domains |
| 2028 | Mechanism | Neural circuit identification |
| 2029 | Mitigation | Bias-aware evaluator tools |
| 2030 | Standards | Industry adoption |
| 2031 | Impact | Bias-aware evaluation as standard practice |
