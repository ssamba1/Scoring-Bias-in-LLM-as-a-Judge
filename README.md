<p align="center">
  <img src="paper/figures_png/graphical_abstract.svg" width="600" alt="Graphical Abstract">
</p>

<h1 align="center">Where Does Scoring Bias Come From?</h1>
<p align="center"><b>A Base vs Instruct Comparison of LLM-as-a-Judge</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_4.0-1a1a2e?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-2b6cb0?style=flat-square" alt="Python"></a>
  <a href="https://arxiv.org"><img src="https://img.shields.io/badge/arXiv-2607.xxxxx-b31b1b?style=flat-square" alt="arXiv"></a>
  <a href="tests/test_all.py"><img src="https://img.shields.io/badge/Tests-11_passing-38a169?style=flat-square" alt="Tests"></a>
  <a href="https://zenodo.org"><img src="https://img.shields.io/badge/DOI-10.5281/zenodo.XXXXX-1867db?style=flat-square" alt="DOI"></a>
  <img src="https://img.shields.io/badge/Models-30_variants-4a5568?style=flat-square" alt="Models">
  <img src="https://img.shields.io/badge/Cost-\$0_total-276749?style=flat-square" alt="Cost">
</p>

---

**LLMs deployed as automated judges exhibit systematic scoring biases — but do these biases come from pre-training or instruction tuning?**

We compare base and instruct variants of **30 models across 15 families** using 3 scoring bias probes (40,500 judgments). The answer: **instruction tuning has opposite effects depending on bias type.**

| Bias Type | Δ Before | Δ After | Change |
|-----------|----------|---------|--------|
| 🔢 Rubric Order | 2.85 | 1.59 | **−44%** |
| 🏷️ Score ID | 0.67 | 0.15 | **−77%** |
| 📋 Reference Answer | 0.88 | 1.19 | **+35%** |

## Links

| What | Where |
|------|-------|
| 📄 **Full paper** | [`paper/camera_ready_full.tex`](paper/camera_ready_full.tex) |
| ✨ **Interactive article** | [`dashboard/interactive_paper.html`](dashboard/interactive_paper.html) |
| 🏆 **Model leaderboard** | [`dashboard/leaderboard.html`](dashboard/leaderboard.html) |
| 📊 **Figure gallery** | [`paper/figures_png/figure_gallery.html`](paper/figures_png/figure_gallery.html) |
| 🐳 **Docker image** | [`Dockerfile`](Dockerfile) |
| 📦 **arXiv package** | [`paper/arxiv_submission/`](paper/arxiv_submission/) |

## Quick Start

```bash
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
cd Scoring-Bias-in-LLM-as-a-Judge
pip install -r requirements.txt
python3 tests/test_all.py
```

## Key Findings

1. **Format biases decrease** after instruction tuning (rubric order −44%, score ID −77%)
2. **Content bias increases** after instruction tuning (reference answer +35%)
3. **RLHF models** show the effect consistently (8/8 families); **SFT+DPO** models do not
4. **Larger models** are less biased (Spearman ρ = −0.75)
5. **Ensemble mitigation** reduces bias by 38–52%

## Citation

```bibtex
@article{samba2026scoring,
  title={Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge},
  author={Samba, Sricharan},
  journal={arXiv preprint},
  year={2026},
  doi={10.5281/zenodo.XXXXX}
}
```

## License

CC-BY 4.0. See [`LICENSE`](LICENSE).
