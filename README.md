<p align="center">
  <img src="paper/figures_png/graphical_abstract.svg" width="600" alt="Graphical Abstract">
</p>

<h1 align="center">Scoring Bias in LLM-as-a-Judge Models</h1>
<p align="center"><b>A 22-Model Landscape with Base-Instruct Comparison</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_4.0-1a1a2e?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-2b6cb0?style=flat-square" alt="Python"></a>
  <a href="https://arxiv.org"><img src="https://img.shields.io/badge/arXiv-2607.xxxxx-b31b1b?style=flat-square" alt="arXiv"></a>
  <a href="tests/test_all.py"><img src="https://img.shields.io/badge/Tests-11_passing-38a169?style=flat-square" alt="Tests"></a>
  <a href="https://zenodo.org"><img src="https://img.shields.io/badge/DOI-10.5281/zenodo.21361920-1867db?style=flat-square" alt="DOI"></a>
  <img src="https://img.shields.io/badge/Models-31_variants-4a5568?style=flat-square" alt="Models">
  <img src="https://img.shields.io/badge/Judgments-40%2C500+-blueviolet?style=flat-square" alt="Judgments">
  <img src="https://img.shields.io/badge/Cost-%3C%243_USD-276749?style=flat-square" alt="Cost">
  <img src="https://img.shields.io/badge/Status-Preprint-yellow?style=flat-square" alt="Status">
</p>

---

**LLMs deployed as automated judges exhibit systematic scoring biases — but do these biases come from pre-training or instruction tuning?** We compare base and instruct variants of **31 model variants across 16 families** using 3 scoring bias probes (40,500+ judgments, <$3 total API cost). The answer: **instruction tuning has opposite effects depending on bias type.**

| Bias Type | Δ Before | Δ After | Change |
|-----------|----------|---------|--------|
| 🔢 Rubric Order | 2.85 | 1.59 | **−44%** |
| 🏷️ Score ID | 0.67 | 0.15 | **−77%** |
| 📋 Reference Answer | 0.88 | 1.19 | **+35%** |

## Key Results

1. **Format biases decrease** after instruction tuning: rubric order bias drops −44% on average across 9 families; score ID bias drops −77%
2. **Content bias increases** after instruction tuning in larger (3B+) RLHF-trained models: reference answer bias increases +35%
3. **Score ID bias has the largest average effect** across 22 instruct models (Δ=0.68), with range 0.00–1.80
4. **RLHF models show the differential effect** consistently (format ↓, content ↑); the SFT+DPO family (Mistral 7B) shows a different pattern
5. **Larger models are generally less biased** but size alone does not guarantee low bias (e.g., Hy3-295B has mean Δ=0.93)
6. **Instruction tuning reduces score ID bias significantly** (Wilcoxon p=0.047, Cohen's d_z=1.08) but rubric order reduction is not significant at current N
7. **We propose the Format Efficiency Hypothesis** as a mechanistic explanation, supported by attention-weight evidence

## Project Structure

```
Scoring-Bias-in-LLM-as-a-Judge/
├── paper/
│   ├── camera_ready_full.tex      # Full paper (LaTeX)
│   ├── references.bib             # 22 references with DOIs/URLs
│   ├── generate_figures.py        # Figure generation script
│   ├── figures/                   # Generated figures (10 total)
│   ├── appendices/                # Supplementary materials
│   │   ├── appendix_a_model_details.tex
│   │   ├── appendix_b_full_results.tex
│   │   ├── appendix_c_domain_breakdown.tex
│   │   ├── appendix_d_statistical_tests.tex
│   │   ├── appendix_e_excluded_models.tex
│   │   ├── appendix_f_reproducibility.tex
│   │   ├── appendix_g_prompt_templates.tex
│   │   └── literature_table.tex
│   └── arxiv_submission/          # Camera-ready package
├── data/
│   ├── combined_80_items.json      # 80 evaluation items
│   ├── dataset_card.md             # Dataset documentation
│   └── model_cards/
│       └── all_models.md           # Cards for all 31 variants
├── results_rootcause/
│   ├── t4fam_results.json          # 7 base-instruct families (T4)
│   ├── study1_results.json         # 22 instruct models (OpenRouter)
│   ├── rootcause_analysis.json     # 3 original families (Kaggle)
│   └── analysis_output/            # Statistical analysis results
│       ├── t4fam_deltas.json
│       ├── bootstrapped_cis.json
│       ├── wilcoxon_results.json
│       ├── cohens_d.json
│       ├── bayesian_results.json
│       ├── power_analysis.json
│       ├── domain_analysis.json
│       └── ...
├── dashboard/                      # Interactive visualizations
├── infrastructure/                 # Docker, CI, environment config
├── tests/                          # Test suite
├── README.md                       # This file
├── CONTRIBUTING.md                 # Contribution guidelines
├── CITATION.cff                    # Citation metadata
└── requirements.txt               # Python dependencies
```

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
cd Scoring-Bias-in-LLM-as-a-Judge
pip install -r requirements.txt

# 2. Verify setup
python tests/test_all.py

# 3. Reproduce analyses
python results_rootcause/run_all_analyses.py
```

## Links

| What | Where |
|------|-------|
| 📄 **Full paper** | [`paper/camera_ready_full.tex`](paper/camera_ready_full.tex) |
| 🌐 **arXiv** | _Coming soon_ |
| 🏗️ **Interactive dashboard** | [`dashboard/interactive_paper.html`](dashboard/interactive_paper.html) |
| 🏆 **Model leaderboard** | [`dashboard/leaderboard.html`](dashboard/leaderboard.html) |
| 📊 **Figure gallery** | [`paper/figures_png/figure_gallery.html`](paper/figures_png/figure_gallery.html) |
| 📋 **Model cards** | [`data/model_cards/all_models.md`](data/model_cards/all_models.md) |
| 💾 **Dataset card** | [`data/dataset_card.md`](data/dataset_card.md) |
| 📦 **Supplementary appendices** | [`paper/appendices/`](paper/appendices/) |
| 🐳 **Docker** | [`Dockerfile`](infrastructure/Dockerfile) |
| 💾 **Zenodo archive** | [10.5281/zenodo.21361920](https://doi.org/10.5281/zenodo.21361920) |

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

## License

CC-BY 4.0. See [`LICENSE`](LICENSE).

## Contact

Sricharan Samba — srisamba09@gmail.com
