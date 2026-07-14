# Scoring Bias in LLM-as-a-Judge

**Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![arXiv](https://img.shields.io/badge/arXiv-2607.xxxxx-b31b1b.svg)](https://arxiv.org)
[![Tests](https://img.shields.io/badge/Tests-11%20passing-brightgreen)](tests/test_all.py)
[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

## Overview

This repository contains the first systematic investigation of whether scoring bias in LLM-as-a-Judge originates from pre-training or emerges during instruction tuning.

**Key finding:** Instruction tuning has *differential effects* on scoring bias. Format-related biases (rubric order, score ID) decrease by 44–77%, while content-related bias (reference answer) increases by 35%.

## Paper

- **[Complete paper (LaTeX)](paper/camera_ready_full.tex)** — 20-page camera-ready manuscript
- **[Supplementary](paper/supplementary_formal.tex)** — 4 theorems with proofs
- **[Interactive article](dashboard/interactive_paper.html)** — distill.pub style scrolling HTML
- **[Graphical abstract](paper/figures_png/graphical_abstract.svg)** — Single-image summary

## Quick Start

```bash
# Clone
git clone https://github.com/ssamba1/research-draft
cd research-draft

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 tests/test_all.py

# Generate figures (requires matplotlib)
python3 paper/generate_png_figures.py
```

## Project Structure

```
paper/          — LaTeX source, figures, arXiv package, supplementary
dashboard/      — Interactive paper, leaderboard, model browser, 3D surface
pipeline/       — Experiment notebooks, analysis scripts, probes
results/        — Statistical analysis, depth findings, quantified limitations
data/           — Evaluation items, model cards, human baseline sheet
docs/           — GitHub Pages site, glossary, FAQ
isef/           — Competition materials
tests/          — Unit tests (11 passing)
```

## Results Summary

| Probe | Base Δ | Instruct Δ | Change |
|-------|--------|-----------|--------|
| Rubric Order | 2.85 | 1.59 | **−44%** |
| Score ID | 0.67 | 0.15 | **−77%** |
| Reference Answer | 0.88 | 1.19 | **+35%** |

## Citation

```bibtex
@article{author2026scoring,
  title={Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge},
  author={Author Name},
  journal={arXiv preprint},
  year={2026}
}
```

## License

CC-BY 4.0. All models used are publicly available under their respective licenses.
