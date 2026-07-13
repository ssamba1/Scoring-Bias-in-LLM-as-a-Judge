# Everything Remaining — Complete Project Inventory

## Phase A: Buildable NOW (no GPU results needed)

| # | Task | File | Effort | Why |
|---|------|------|--------|-----|
| 1 | Multi-language items (EN, ZH, ES, AR, HI) | `data/multilingual/` | 1 hr | Tests cross-lingual generalizability |
| 2 | Additional probe code (9 probes) | `pipeline_rootcause/additional_probes.py` | 3 hrs | Ready for deep-dive GPU run |
| 3 | Mixed-effects statistical model | `results_rootcause/mixed_effects.py` | 2 hrs | Professional-grade stats |
| 4 | Bayesian hierarchical analysis | `results_rootcause/bayesian_analysis.py` | 2 hrs | Posterior distributions |
| 5 | Bias profile clustering (PCA/t-SNE) | `results_rootcause/bias_clustering.py` | 1 hr | Model archetypes |
| 6 | Real benchmark item formatting (MT-Bench, FLASK) | `data/benchmark/` | 1 hr | External validity |
| 7 | IRT item analysis | `results_rootcause/item_response.py` | 2 hrs | Item quality metrics |
| 8 | Updated paper framing 44-family story | `paper/camera_ready.tex` | 2 hrs | Ready for submission |
| 9 | Configurable figure generation | `paper/figures/generate_all_figures.py` | 1 hr | Any data source |
| 10 | Interactive model browser (44 families) | `dashboard/model_browser.html` | 2 hrs | Explore all results |

## Phase B: Needs GPU Data (but code can be templated now)

| # | Task | Depends On | Effort |
|---|------|-----------|--------|
| 11 | Run post-processing on real data | study1_max_scale.json | 5 min |
| 12 | Human baseline scoring | 5 raters × 50 items | 2 hrs |
| 13 | Cross-lingual comparison | Multi-language items + GPU run | 1 hr |
| 14 | 12-probe deep dive analysis | Additional probe GPU run | 1 hr |
| 15 | Bias-date correlation | Output data | 30 min |
| 16 | Model size vs bias plot | Output data | 30 min |

## Phase C: Needs All Data

| # | Task | Depends On | Effort |
|---|------|-----------|--------|
| 17 | Final paper with all results | Everything above | 4 hrs |
| 18 | ISEF final package | Final paper | 2 hrs |
| 19 | NeurIPS submission | Final paper | 1 hr |
| 20 | arXiv submission | Final paper | 30 min |

---

## What I'm Building Right Now

The 5 highest-impact items from Phase A that don't need GPU results.
