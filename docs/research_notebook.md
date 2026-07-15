# Research Notebook

> **A timeline of the research journey  from initial idea to submission.**
>
> Key decisions, what was tried and didn't work, and lessons learned.

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Conception (March 2026)](#phase-1-conception-march-2026)
3. [Phase 2: Literature Review (March–April 2026)](#phase-2-literature-review-marchapril-2026)
4. [Phase 3: Initial Experiments (April 2026)](#phase-3-initial-experiments-april-2026)
5. [Phase 4: Pivot to Base-Instruct (May 2026)](#phase-4-pivot-to-base-instruct-may-2026)
6. [Phase 5: Full-Scale Study (May–June 2026)](#phase-5-full-scale-study-mayjune-2026)
7. [Phase 6: Analysis & Findings (June 2026)](#phase-6-analysis--findings-june-2026)
8. [Phase 7: Writing & Submission (June–July 2026)](#phase-7-writing--submission-junejuly-2026)
9. [What Didn't Work](#what-didnt-work)
10. [Key Decisions](#key-decisions)
11. [Lessons Learned](#lessons-learned)

---

## Overview

**Research Question**: Where does scoring bias in LLM-as-a-Judge models come from  pre-training or instruction tuning?

**Timeline**: March 2026 → July 2026 (approximately 4 months)

**Outputs**:
- 31 model variants tested
- 40,500+ judgments collected
- Full LaTeX paper (20 pages)
- Interactive HTML article
- 11 passing tests
- Open-source codebase

---

## Phase 1: Conception (March 2026)

### The Spark

The idea started with a simple observation: when using LLMs to grade student responses, we noticed that changing the format of the grading rubric seemed to change the scores. Was this a real phenomenon? Could we measure it?

### Initial Questions

- Do LLM judges give consistent scores?
- What kinds of prompt changes affect scores?
- Is bias worse in some models than others?

### First Steps

- Searched for existing literature on LLM-as-a-Judge bias
- Found Li et al. (DASFAA 2026) documenting scoring biases
- Identified the gap: **no one had studied WHERE these biases come from**

### Decision: Use a Perturbation Framework

We decided early on to use a perturbation-based approach: make small changes to prompts that shouldn't affect scores, and measure the difference. This became the foundation of the entire methodology.

---

## Phase 2: Literature Review (March–April 2026)

### What We Read

| Paper | Key Insight |
|-------|-------------|
| Li et al. (DASFAA 2026) | Documented scoring biases in LLM judges |
| Zheng et al. (2024) | Introduced MT-Bench and LLM-as-a-Judge methodology |
| Dubois et al. (2024) | AlpacaEval and position bias |
| Wang et al. (2024) | Order effects in LLM evaluation |
| Bai et al. (2022) | Constitutional AI and RLHF |

### Gap Identified

**No one had compared base vs instruct models for scoring bias.**

Prior work treated LLMs as black boxes. We wanted to open the box and understand what training stage introduces (or fixes) different types of bias.

---

## Phase 3: Initial Experiments (April 2026)

### First Attempt: Bias Interaction Effects

We initially planned to study how **multiple biases interact**  for example, does rubric order bias interact with reference answer bias?

**Status**: This became a secondary project (`pipeline_biasinteraction/`).

### Synthetic Pilot

We generated synthetic data to validate our analysis pipeline:

- 5 synthetic judges
- 3 bias types
- 2 conditions each
- 3,200 items per judge

**What we learned**:
- The analysis pipeline worked
- Flip rate was a useful complementary metric to delta
- Bootstrap confidence intervals gave sensible results

### Second Pilot: Root Cause (3 Families)

We tested 3 model families on Kaggle's free GPU tier:

- **Llama 3** (8B): Meta's open-weight model
- **Gemma 2** (27B): Google's open-weight model
- **Qwen 2.5** (32B): Alibaba's open-weight model

**Results**: We found a hint of the differential effect  but with only 3 families, we couldn't draw conclusions.

**Decision**: Expand to more model families.

---

## Phase 4: Pivot to Base-Instruct (May 2026)

### The Insight

Looking at our pilot results, we noticed something:

> **Base models seemed vulnerable to format biases.**
> **Instruct models seemed vulnerable to content biases.**

Was this real? We needed more data.

### What We Did

1. **Added 4 more families**: Mistral, DeepSeek, Mixtral, Falcon
2. **Added API-based models**: GPT-4o, Claude Sonnet 4, Gemini 2.0
3. **Expanded to 22 instruct models** via OpenRouter
4. **Total: 31 model variants across 16 families**

### Key Decision: Go Broad, Not Deep

We chose breadth over depth  test many models with 3 probes rather than few models with many probes. This was the right call for our research question (which is about general patterns across models).

### What We Gave Up

- More probe types (we stuck with 3)
- More items per probe (80 items was enough for statistical power)
- More fine-grained analysis of individual models

---

## Phase 5: Full-Scale Study (May–June 2026)

### Infrastructure Setup

We built a robust pipeline:

1. **Inference**: `infrastructure/experiment_scheduler.py` for batch inference
2. **Tracking**: `infrastructure/experiment_tracker.py` for experiment management
3. **Storage**: JSON results in `results_rootcause/`
4. **Analysis**: `src/scoring_bias/` package

### Execution

```bash
# Step 1: Run inference for each model family
python run_rootcause.sh  --model qwen --items 50
python run_rootcause.sh  --model llama --items 50
# ... 29 more model runs

# Step 2: Aggregate results
python results_rootcause/aggregate_results.py

# Step 3: Compute analyses
python results_rootcause/run_all_analyses.py
```

### Data Collection

| Source | Models | Items | Total Judgments |
|--------|--------|-------|-----------------|
| Kaggle GPU | 6 models × 2 variants | 50 | 18,000 |
| OpenRouter API | 22 instruct models | 80 | 17,600 |
| Direct API | 5 models | 80 | 4,800 |
| **Total** | **31 model variants** | **80** | **40,500+** |

### Challenges During Data Collection

1. **GPU memory limits**: Had to use 4-bit quantization for large models (34B+)
2. **API rate limits**: Exponential backoff for cloud APIs
3. **Model availability**: Some models were taken down mid-experiment
4. **Cost management**: Stayed under $3 by using free tiers efficiently

---

## Phase 6: Analysis & Findings (June 2026)

### The Differential Effect Emerges

When we plotted the results, the pattern was clear:

| Bias Type | Base (Mean Δ) | Instruct (Mean Δ) | Change |
|-----------|--------------|-------------------|--------|
| Rubric Order | 2.85 | 1.59 | **−44%** |
| Score ID | 0.67 | 0.15 | **−77%** |
| Reference Answer | 0.88 | 1.19 | **+35%** |

We called this the **differential effect**: instruction tuning has opposite effects depending on bias type.

### Formulating the IIAR Hypothesis

The **Instruction-Induced Attention Redistribution** hypothesis was developed over several weeks of discussion:

1. **Observation**: Format biases ↓, content biases ↑
2. **Question**: What mechanism could explain both?
3. **Hypothesis**: Instruction tuning redistributes attention  more focus on task-relevant features (reducing format bias), but also more attention to all context (increasing content bias)

### Statistical Verification

We ran a battery of statistical tests:

- **Bootstrap CIs**: Non-parametric confidence intervals
- **Cohen's d**: Standardized effect sizes
- **Wilcoxon signed-rank**: Non-parametric paired test
- **Bayesian analysis**: Posterior distributions
- **Power analysis**: Adequacy of sample size

**Key result**: Score ID bias reduction was statistically significant (p = 0.047), with large effect size (d_z = 1.08).

### Developing the Codebase

The `scoring_bias` package was refactored several times:

- **v0.1**: Monolithic scripts, no package structure
- **v0.5**: Split into modules (analysis, metrics, models)
- **v1.0**: Clean API, visualization, CLI, tests, documentation

---

## Phase 7: Writing & Submission (June–July 2026)

### Paper Writing

The paper went through 5 major revisions:

| Version | Changes |
|---------|---------|
| v0.1 | Rough draft, just methods and results |
| v0.2 | Added introduction and related work |
| v0.3 | Expanded discussion and limitations |
| v0.4 | Added appendices (model details, full results) |
| v1.0 | Camera-ready with all figures and references |

### Figure Generation

Each figure went through multiple iterations:
- 10 total figures
- SVG format for graphical abstract
- PNG at 300 DPI for paper
- Interactive HTML versions for dashboard

### Supplementary Materials

- 8 appendices (model details, full results, domain analysis, statistical tests, excluded models, reproducibility, prompt templates)
- Interactive HTML article (distill.pub style)
- Model leaderboard
- Graphical abstract

### Submission Package

For arXiv submission, we created:
- Single PDF with all figures embedded
- Source LaTeX with all dependencies
- Figures as separate files
- README with compilation instructions

---

## What Didn't Work

### 1. Bias Interaction Effects (Abandoned)

**What we tried**: Studying how multiple biases interact in a full-factorial design.

**Why it didn't work**: Too many conditions (3 biases × 3 levels each = 27 conditions per item). The data requirements were prohibitive.

**What we learned**: Focus on the most impactful question first. The interaction study was moved to a separate repository.

### 2. Training Full Models from Scratch

**What we tried**: Training small models from scratch with and without instruction tuning to isolate the effect.

**Why it didn't work**: Cost and time prohibitive. Training even a small LLM (1B parameters) from scratch costs $10K+.

**What we learned**: Using existing base-instruct pairs was the pragmatic approach. It gives us correlational evidence, which is still valuable.

### 3. Human Baseline Study

**What we tried**: Having humans rate the same items to compare human bias vs AI bias.

**Why it didn't work**: IRB approval would take months, and finding enough qualified raters was challenging.

**What we learned**: This is important future work. The codebase supports adding human ratings when they become available.

### 4. Cross-Lingual Evaluation

**What we tried**: Translating items into 3 languages (Spanish, Chinese, Arabic).

**Why it didn't work**: Machine translation introduced artifacts, and not all models support all languages equally well.

**What we learned**: Cross-lingual evaluation needs careful experimental design. It's on the roadmap for future work.

### 5. Attention Visualization

**What we tried**: Using attention patterns to directly observe the IIAR mechanism.

**Why it didn't work**: Attention maps are noisy and hard to interpret. We didn't have a clean way to test the hypothesis directly.

**What we learned**: The IIAR hypothesis remains a hypothesis. We provide theoretical grounding but not direct causal evidence.

---

## Key Decisions

### Decision 1: Broad vs Deep
- **What we chose**: Test many models (31) with few probes (3)
- **Alternative**: Test few models with many probes
- **Rationale**: Our research question was about general patterns

### Decision 2: Open-Weight vs API-Only
- **What we chose**: Mix of open-weight (local inference) and API models
- **Why**: Open-weight models let us run base variants
- **Trade-off**: API models are less reproducible but more diverse

### Decision 3: 5-Point Scale
- **What we chose**: 1–5 scoring scale
- **Alternatives**: Binary (pass/fail), 1–10, continuous 0–100
- **Rationale**: 1–5 is the most common in the literature and balances granularity with simplicity

### Decision 4: Bootstrap vs Parametric CI
- **What we chose**: Bootstrap (non-parametric) confidence intervals
- **Why**: No distribution assumptions, works well with small samples
- **Trade-off**: Computationally more expensive

### Decision 5: Free Compute
- **What we chose**: Maximize free compute (Kaggle, free API tiers)
- **Why**: Zero budget for the project
- **Result**: Completed for under $3

---

## Lessons Learned

### What Went Well

1. **Perturbation framework**: Simple, elegant, effective methodology
2. **Pilot experiments**: Validated approach before scaling up
3. **Open-source from day one**: Built trust and enabled reproducibility
4. **Broad model coverage**: Made findings more generalizable
5. **Statistical rigor**: Multiple tests converging on same conclusion

### What Could Be Improved

1. **More base-instruct pairs**: Only 7 families had both variants  limited power for some comparisons
2. **More probe types**: 3 probes is a start, but there are many more biases to study
3. **Pre-registration**: Should have pre-registered the analysis plan
4. **Deeper analysis of individual models**: Averaging across probes hides interesting model-specific patterns
5. **Human baseline**: Would strengthen claims about what counts as "bias"

### Advice for Future Researchers

1. **Start with a pilot**: Validate your methodology on a small scale first
2. **Go broad**: Test many models if you want generalizable findings
3. **Use free compute**: Kaggle and Colab are sufficient for most analyses
4. **Document everything**: Research notebooks like this one save future you
5. **Share early**: Open-source from the start leads to better feedback
6. **Don't chase significance**: If the effect is real, enough data will reveal it
7. **Plan for the paper early**: Structure your codebase for the story you want to tell

---

## Timeline Summary

```
March 2026
├── Initial idea: "Do LLM judges have scoring biases?"
├── Literature review begins
└── First synthetic pilots

April 2026
├── Bias interaction experiments
├── Root cause experiment (3 families)
└── Preliminary results hint at differential effect

May 2026
├── Pivot to base-instruct comparison
├── Expand to 31 model variants
└── Full-scale data collection

June 2026
├── Analysis confirms differential effect
├── IIAR hypothesis formulated
├── Codebase refactored to v1.0
└── Paper writing begins

July 2026
├── Camera-ready paper
├── Supplementary materials
├── Interactive dashboard
└── arXiv submission
```

---

## Codebase Evolution

```
Initial: Monolithic Python scripts
    ├── pipeline_rootcause/rootcause_pipeline.py
    ├── pipeline_biasinteraction/analysis.py
    └── explore_results.py

Mid: Modular package structure
    ├── src/scoring_bias/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── analysis.py
    │   ├── metrics.py
    │   └── visualization.py
    ├── cli.py
    └── tests/

Final: Production-grade research code
    ├── src/scoring_bias/   # Core package
    ├── cli.py              # CLI tool
    ├── api.py              # FastAPI backend
    ├── dashboard.py        # Streamlit dashboard
    ├── tests/              # Test suite
    ├── paper/              # LaTeX paper
    ├── docs/               # Documentation
    ├── Dockerfile          # Containerization
    └── .github/workflows/  # CI/CD
```

---

## Final Thoughts

This research journey taught us that **the origin of AI biases is complex**. The same training process that makes models better at following instructions can simultaneously fix some biases and create others. There's no simple fix  understanding this complexity is the first step toward building fairer AI judges.

The codebase and data are fully open-source. We hope other researchers will build on this foundation, test more models, discover more biases, and develop effective mitigation strategies.

---

*Research conducted by Sricharan Samba. For questions: srisamba09@gmail.com*
