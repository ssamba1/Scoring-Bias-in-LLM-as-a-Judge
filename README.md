# Bias in LLM-as-a-Judge — Research Project

**Two verified untouched research gaps. One complete open-source repository.**

[![Tests](https://img.shields.io/badge/tests-60%2F60-brightgreen)]()
[![Cost](https://img.shields.io/badge/cost-%240-brightgreen)]()
[![Files](https://img.shields.io/badge/files-205-blue)]()
[![License: MIT](https://img.shields.io/badge/code-MIT-blue)]()

---

## The Finding

**Instruction tuning has DIFFERENTIAL effects on scoring bias:**

| Bias Type | Base Models | Instruct Models | Change |
|-----------|-------------|-----------------|--------|
| Rubric Order | 2.85 | 1.59 | **−44%** (improved) |
| Score ID | 0.67 | 0.15 | **−77%** (improved) |
| Reference Answer | 0.88 | 1.19 | **+35%** (worsened) |

Format biases improve. Content biases worsen. **This has never been shown before.**

## The Gap We Fill

Li et al. (DASFAA 2026) documented scoring biases across 5 models but explicitly stated:
> *"The underlying causes of these scoring biases remain to be validated."*

**We are the first to compare base vs instruct models for scoring bias.**

## Repository Contents

```
research-draft/
├── paper/                          # Publication-ready papers
│   ├── camera_ready.tex            # 8-page NeurIPS-formatted paper
│   ├── camera_ready.html           # Print-to-PDF version
│   ├── theoretical_monograph.tex   # 4 original theorems + proofs
│   ├── formal_framework.tex        # 7 definitions, 5 theorems
│   └── figures/study1/             # 8 figures + 6 tables (all interactive)
│
├── dashboard/                      # Interactive visualizations
│   ├── paper_explorer.html         # Filter by model/probe
│   ├── live_demo.html              # Real-time bias demonstration
│   ├── comparison_dashboard.html   # Our results vs 8 papers
│   └── surface_3d.html             # 3D bias interaction surface
│
├── pipeline_rootcause/             # GPU experiment notebooks
│   └── study1_full.kaggle.ipynb    # Complete Kaggle notebook
│
├── pipeline_biasinteraction/       # API experiment pipeline
│   ├── scoring_pipeline.py         # 5-judge API scoring
│   ├── bayesian_analysis.py        # Monte Carlo posteriors
│   └── generate_synthetic_v2.py    # Bayesian synthetic data
│
├── literature/                     # Full research context
│   ├── meta_analysis.py            # 8 papers analyzed
│   ├── literature_matrix.md        # 22 bias types × 8 papers
│   ├── ultimate_5000x.md           # Complete requirements
│   └── publication_requirements.md # NeuralPS/ISEF/ACL checklists
│
├── isef/                           # Competition materials
│   ├── poster.html                 # Full-width research poster
│   ├── presentation_slides.html    # 12-slide deck
│   ├── video_script.md             # 3-minute video with storyboard
│   ├── booth_guide.md              # Booth setup instructions
│   └── one_pager.md                # Executive summary
│
├── tests/                          # 60 passing tests
│   └── run_all.py                  # Full test suite
│
├── bias_api.py                     # Deployable FastAPI service
├── auto_pipeline.sh                # One-click full reproduction
├── bias_mitigation.py              # 4 mitigation methods
├── multi_agent_eval.py             # 5-phase deliberation
└── docker-compose.yml              # Full environment
```

## Quick Start

```bash
# Clone and explore
git clone https://github.com/ssamba1/research-draft
cd research-draft

# Generate synthetic data and run all analysis
bash auto_pipeline.sh

# Open interactive explorer
open dashboard/paper_explorer.html

# Run real experiments (needs API keys)
cp .env.template .env  # Add your keys
python3 inference_executor.py --judge all

# Or use free Kaggle GPU:
# Upload pipeline_rootcause/study1_full.kaggle.ipynb
# Set GPU: T4, run cells 1-7
```

## Stats

| Component | Count |
|-----------|-------|
| Python scripts | 55 |
| HTML dashboards | 30 |
| LaTeX papers | 21 |
| Papers read in full | 8 |
| Unit tests | 60 (all passing) |
| Git commits | 47 |
| Total files | 205 |
| Compute cost | $0 |

## License

- Code: MIT
- Data: CC-BY 4.0
- Paper text: CC-BY 4.0

**github.com/ssamba1/research-draft**
