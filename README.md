<p align="center">
  <img src="paper/figures_png/graphical_abstract.svg" width="700" alt="Graphical Abstract — Scoring Bias in LLM-as-a-Judge Models">
</p>

<h1 align="center">Scoring Bias in LLM-as-a-Judge Models</h1>
<p align="center"><b>A 22-Model Landscape with Base-Instruct Comparison — ISEF 2026 Finalist</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_4.0-1a1a2e?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-2b6cb0?style=flat-square" alt="Python 3.11+"></a>
  <a href="https://arxiv.org/abs/XXXX.XXXXX"><img src="https://img.shields.io/badge/arXiv-2607.xxxxx-b31b1b?style=flat-square" alt="arXiv"></a>
  <a href="https://doi.org/10.5281/zenodo.21361920"><img src="https://img.shields.io/badge/DOI-10.5281/zenodo.21361920-1867db?style=flat-square" alt="DOI"></a>
  <a href="tests/test_all.py"><img src="https://img.shields.io/badge/Tests-11_passing-38a169?style=flat-square" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Models-31_variants-4a5568?style=flat-square" alt="Models">
  <img src="https://img.shields.io/badge/Judgments-40,500+-blueviolet?style=flat-square" alt="Judgments">
  <img src="https://img.shields.io/badge/Cost-%3C%243_USD-276749?style=flat-square" alt="Cost">
  <img src="https://img.shields.io/badge/Status-Published-805ad5?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/ISEF-2026_Finalist-ff6b35?style=flat-square" alt="ISEF 2026">
</p>

---

**LLMs deployed as automated judges exhibit systematic scoring biases — but do these biases originate from pre-training or from instruction tuning?** We systematically compare base (pre-trained) and instruct (fine-tuned) variants across **31 model variants from 16 families** using three perturbation-based scoring bias probes. With **40,500+ judgments** generated for under **$3 USD** in total API cost, we find that instruction tuning has **opposite effects depending on bias type**: format-related biases decrease, while content-related biases increase in larger RLHF-trained models.

### Key Findings

> **1. Instruction tuning reduces format biases by up to 77%.** Rubric order bias drops from Δ=2.85 to 1.59 (−44%); score ID bias drops from Δ=0.67 to 0.15 (−77%) across 7 T4-evaluated families.

> **2. Content bias increases after instruction tuning in larger (3B+) RLHF-trained models.** Reference answer bias increases +35% on average, creating a **differential effect** where format and content biases move in opposite directions.

> **3. Score ID bias is the largest and most variable.** Across 22 instruct-tuned models, mean Δ=0.68 (range: 0.00–1.80), with Hermes-3-70B most affected (Δ=1.80) and Qwen3-14B least affected (Δ=0.00).

---

## Graphical Abstract

<p align="center">
  <img src="paper/figures/infographic.svg" width="800" alt="Study Overview">
</p>

| Bias Type | Δ Before | Δ After | Change |
|-----------|----------|---------|--------|
| 🔢 Rubric Order | 2.85 | 1.59 | **−44%** |
| 🏷️ Score ID | 0.67 | 0.15 | **−77%** |
| 📋 Reference Answer | 0.88 | 1.19 | **+35%** |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
cd Scoring-Bias-in-LLM-as-a-Judge
pip install -r requirements.txt

# 2. Verify setup (11 tests)
python -m pytest tests/test_all.py -v

# 3. Reproduce all figures
python paper/figures/generate_all_figures.py
```

> **Zero-cost reproduction:** All data and analysis scripts are included. The inference pipeline uses Kaggle T4 GPUs (free tier) and OpenRouter API (< $3 total). See [`REPLICATION.md`](REPLICATION.md) for a step-by-step guide.

---

## Project Structure

```
Scoring-Bias-in-LLM-as-a-Judge/
├── paper/                           # Publication materials
│   ├── camera_ready_full.tex        # Full manuscript (LaTeX)
│   ├── references.bib               # 22 references with DOIs
│   ├── figures/                     # All 20 publication figures
│   │   ├── fig1_bias_landscape.png  #   Bias landscape (bar chart)
│   │   ├── fig2_format_content.png  #   Format vs content scatter
│   │   ├── fig3_scale_dependent.png #   Scale-dependent effects
│   │   ├── fig4_model_ranking.png   #   Model ranking heatmap
│   │   ├── fig5_bayesian.png        #   Bayesian posteriors
│   │   ├── fig6_domain_bias.png     #   Domain breakdown
│   │   ├── fig7_base_instruct.png   #   Base-instruct paired
│   │   ├── fig8_flip_rate.png       #   Flip rate comparison
│   │   ├── fig9_item_analysis.png   #   Item-level analysis
│   │   ├── fig10_dashboard.png      #   Comprehensive dashboard
│   │   ├── fig11_error_analysis.png #   Error analysis
│   │   ├── fig12_training_method.png#   Training method effects
│   │   ├── fig13_size_quantile.png  #   Size quantile trends
│   │   ├── fig14_correlations.png   #   Probe correlation matrix
│   │   ├── fig15_power_curve.png    #   Statistical power
│   │   ├── fig16_variance.png       #   Variance decomposition
│   │   ├── fig17_discrimination.png #   Item discrimination
│   │   ├── fig18_base_vs_instruct.png#  Base vs instruct all
│   │   ├── fig19_bayes_factor.png   #   Bayes factor comparison
│   │   ├── fig20_summary.png        #   Comprehensive summary
│   │   ├── generate_all_figures.py  #   Single-script regeneration
│   │   └── figure_captions.tex      #   LaTeX captions for all figs
│   ├── tables/                      # Extracted LaTeX tables
│   │   ├── tab_main.tex             #   Main results table
│   │   ├── tab_per_model.tex        #   Per-model bias scores
│   │   ├── tab_related.tex          #   Related work comparison
│   │   ├── tab_models.tex           #   Model families table
│   │   ├── tab_bayesian.tex         #   Bayesian results
│   │   ├── tab_bootstrapped.tex     #   Bootstrapped CIs
│   │   ├── tab_domain.tex           #   Domain breakdown
│   │   └── tab_comparison.tex       #   Li et al. comparison
│   ├── appendices/                  # Supplementary materials
│   │   ├── appendix_a_model_details.tex
│   │   ├── appendix_b_full_results.tex
│   │   ├── appendix_c_domain_breakdown.tex
│   │   ├── appendix_d_statistical_tests.tex
│   │   ├── appendix_e_excluded_models.tex
│   │   ├── appendix_f_reproducibility.tex
│   │   ├── appendix_g_prompt_templates.tex
│   │   └── literature_table.tex
│   ├── interactive/                 # HTML-based interactive figures
│   └── outreach/                    # Blog posts, press materials
├── data/                            # Experimental data
│   ├── dataset.json                 # Unified structured dataset
│   ├── dataset_card.md              # Comprehensive dataset card
│   ├── data_dictionary.md           # Field-level documentation
│   ├── combined_80_items.json       # All 80 evaluation items
│   ├── model_cards/all_models.md    # Cards for all 31 variants
│   └── raw/                         # Raw CSV data
├── results_rootcause/               # Analysis outputs
│   ├── t4fam_results.json           # 7 base-instruct families (T4)
│   ├── study1_results.json          # 22 instruct models (OpenRouter)
│   ├── rootcause_analysis.json      # 3 original families (Kaggle)
│   ├── analysis_output/             # Statistical analysis results
│   │   ├── bayesian_results.json    #   Bayesian posteriors
│   │   ├── bootstrapped_cis.json    #   Bootstrapped confidence intervals
│   │   ├── wilcoxon_results.json    #   Wilcoxon signed-rank tests
│   │   ├── cohens_d.json            #   Effect size estimates
│   │   ├── model_ranking.json       #   Model bias rankings
│   │   ├── family_profiles.json     #   Per-family delta profiles
│   │   ├── domain_analysis.json     #   Domain-level breakdowns
│   │   ├── training_method_analysis.json  # RLHF / SFT / DPO
│   │   ├── probe_correlations.json  #   Cross-probe correlation
│   │   ├── variance_decomposition.json    # Between/within model
│   │   ├── power_curve.json         #   Statistical power analysis
│   │   ├── size_quantile_analysis.json    # Bias vs size bins
│   │   ├── item_analysis.json       #   Item difficulty/discrimination
│   │   ├── t4fam_deltas.json        #   Per-model base/instruct deltas
│   │   └── robustness_metrics.json  #   MAD, std, CV per model
│   └── validation/                  # Reproducibility validation
├── src/scoring_bias/                # Core library
│   ├── models.py                    # Data models (ProbeType, ScoreRecord, etc.)
│   ├── metrics.py                   # Bias metrics computation
│   ├── analysis.py                  # Statistical analysis
│   └── visualization.py             # Publication-quality plotting
├── dashboard/                       # Interactive visualizations
│   ├── interactive_paper.html       #   Full interactive paper
│   ├── leaderboard.html             #   Model bias leaderboard
│   ├── bias_monitor.html            #   Bias monitoring dashboard
│   └── comparison_dashboard.html    #   Side-by-side comparison
├── infrastructure/                  # Docker, CI, env config
├── tests/                           # Test suite (11 tests)
├── notebooks/                       # Jupyter notebooks (reproducibility)
├── isef/                            # ISEF competition materials
│   ├── abstract.md                  #   Project abstract
│   ├── poster_template.md           #   Poster presentation
│   ├── presentation_slides.md       #   Slide deck outline
│   └── judge_qa.md                  #   Judge Q&A preparation
├── README.md                        # This file
├── CONTRIBUTING.md                  # Contribution guidelines
├── CITATION.cff                     # Citation metadata
├── REPLICATION.md                   # Reproduction guide
├── requirements.txt                 # Python dependencies
└── LICENSE                          # CC-BY 4.0
```

---

## Results Summary

### Bias Landscape (22 Instruct-Tuned Models)

| Probe | Mean Δ | Std Dev | Range | 95% CI |
|-------|--------|---------|-------|--------|
| 🔢 Rubric Order | 0.56 | 0.41 | 0.10–1.50 | ±0.17 |
| 🏷️ Score ID | **0.68** | 0.49 | 0.00–1.80 | ±0.20 |
| 📋 Reference Answer | 0.41 | 0.31 | 0.00–1.00 | ±0.13 |

**Most robust model:** Qwen3-14B (mean Δ = 0.07)  
**Most biased model:** Hermes-3-70B (mean Δ = 1.03)

### Base vs Instruct Comparison (7 T4 Families)

- **Rubric order:** Δ decreases in 5/7 families (mean Δ change: −0.40)
- **Score ID:** Δ decreases in 6/7 families (mean Δ change: **−0.97**, Wilcoxon p = 0.047, Cohen's d_z = 1.08)
- **Reference answer:** Δ decreases in 5/7 families, but **increases in larger (3B+) RLHF models**

### Statistical Power

At current N=9 families:
- Score ID: **91% power** (sufficient)
- Reference answer: 45% power
- Rubric order: 8% power

Target N=30 families for 80% power on all probes.

---

## How to Cite

```bibtex
@article{samba2026scoring,
  title     = {Scoring Bias in {LLM-as-a-Judge} Models:
               A 22-Model Landscape with Base-Instruct Comparison},
  author    = {Samba, Sricharan},
  journal   = {arXiv preprint},
  year      = {2026},
  doi       = {10.5281/zenodo.21361920},
  url       = {https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge}
}
```

---

## Links

| What | Where |
|------|-------|
| 📄 **Full paper (PDF)** | [`paper/camera_ready_full.tex`](paper/camera_ready_full.tex) |
| 🌐 **arXiv** | _Coming soon_ |
| 🏗️ **Interactive paper** | [`dashboard/interactive_paper.html`](dashboard/interactive_paper.html) |
| 🏆 **Model leaderboard** | [`dashboard/leaderboard.html`](dashboard/leaderboard.html) |
| 📊 **Figure gallery** | [`paper/figures_png/figure_gallery.html`](paper/figures_png/figure_gallery.html) |
| 📋 **Model cards** | [`data/model_cards/all_models.md`](data/model_cards/all_models.md) |
| 💾 **Dataset card** | [`data/dataset_card.md`](data/dataset_card.md) |
| 📖 **Data dictionary** | [`data/data_dictionary.md`](data/data_dictionary.md) |
| 📦 **Supplementary appendices** | [`paper/appendices/`](paper/appendices/) |
| 🐳 **Docker image** | [`Dockerfile`](infrastructure/Dockerfile) |
| 💾 **Zenodo archive** | [10.5281/zenodo.21361920](https://doi.org/10.5281/zenodo.21361920) |
| 🔬 **Interactive explorer** | [`dashboard/bias_monitor.html`](dashboard/bias_monitor.html) |

---

## ISEF 2026 Competition

This project is a **Regeneron ISEF 2026 Finalist**. Competition materials are in [`isef/`](isef/):

- 📝 [Project Abstract](isef/abstract.md)
- 🖼️ [Poster Template](isef/poster_template.md)
- 📽️ [Presentation Outline](isef/presentation_outline.md)
- 📹 [Video Script](isef/video_script.md)
- ❓ [Judge Q&A Prep](isef/judge_qa.md)
- 📋 [Competition Checklist](isef/checklist.md)
- ⚖️ [Ethics Statement](isef/ethics_statement.md)

---

## Related Work

This work builds on the perturbation-based scoring bias framework introduced by **Li et al. (2025)** ["Scoring Bias in LLM-as-a-Judge"](https://doi.org/10.1007/978-981-96-0957-6_11), DASFAA 2026. While Li et al. studied 5 commercial models (GPT-4o, DeepSeek-V3, etc.), we extend the analysis to **31 open-weight variants** and provide the first systematic comparison of **base vs instruct** models to isolate the effect of instruction tuning on scoring bias.

---

## License

CC-BY 4.0. See [`LICENSE`](LICENSE).

---

## Contact

**Sricharan Samba** — [srisamba09@gmail.com](mailto:srisamba09@gmail.com)

South Forsyth High School · Cumming, GA · Regeneron ISEF 2026 Finalist
