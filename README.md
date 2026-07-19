<h1 align="center">Where Does Scoring Bias Come From?</h1>
<p align="center"><b>A base-vs-instruct study of three scoring biases in small open-weight LLM judges</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_4.0-1a1a2e?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Families-7_(base%2Binstruct)-4a5568?style=flat-square" alt="Families">
  <img src="https://img.shields.io/badge/Analysis-family--level_n%3D7-2b6cb0?style=flat-square" alt="n=7">
</p>

---

> ### ⚠️ Correction notice (2026-07)
> **Earlier versions of this repository and paper reported a 22-model / 31-variant / 40,500-judgment
> "landscape" and a "content bias increases after instruction tuning" finding. Those claims were not
> supported by real data.** An independent audit found that the 22-model results, the domain
> breakdown, the flip-rate comparison, and the attention/"IIAR" evidence were synthetic, placeholder,
> or fabricated. Those artifacts have been moved to [`RETRACTED/`](RETRACTED/) and must not be cited.
> The only provenance-verified data is the 7-family Kaggle T4 run (`results_rootcause/t4fam_results.json`).
> See [`DATA_INTEGRITY_AUDIT.md`](DATA_INTEGRITY_AUDIT.md) and [`paper/PROVENANCE_AUDIT.md`](paper/PROVENANCE_AUDIT.md).

---

## What this repository now contains

A small, honest, fully reproducible study of the open question raised by
Li et al. (2026, DASFAA), *"Evaluating Scoring Bias in LLM-as-a-Judge"*: **do scoring biases originate
in pre-training, or are they shaped by instruction tuning?**

We compare the **base** and **instruct** checkpoints of **seven open-weight families ≤7B** under the
three perturbation probes of Li et al. (rubric order, score ID, reference answer), on a free Kaggle T4
GPU. Because only per-variant **mean** scores were retained (not per-item scores), the unit of analysis
is the model **family** (n = 7 paired observations).

### Finding

**Instruction tuning *reduces* all three scoring biases in this regime.** The reduction is large and
robust for two of the three probes:

| Probe | Base Δ | Instruct Δ | Change | Effect size | Robustness |
|---|---|---|---|---|---|
| Score ID | 2.41 | 1.44 | −0.97 (−40%) | dz = −1.08 | **robust** — 6/7 families, 95% CI [−1.54, −0.33] |
| Reference answer | 2.76 | 1.93 | −0.83 (−30%) | dz = −1.18 | **robust** — 6/7 families, 95% CI [−1.27, −0.31] |
| Rubric order | 0.69 | 0.29 | −0.40 | dz = −0.38 | inconclusive — CI crosses 0, outlier-driven |

Δ = max inter-variant spread in mean score (Li et al.'s metric); lower = less biased. This is
*directional* evidence that these biases are shaped during instruction tuning rather than fixed at
pre-training, at least for small models. We do **not** reproduce a "content bias increases" pattern.
Full scope and limitations are in the paper.

## Paper

- **[`paper/honest/scoring_bias_honest.pdf`](paper/honest/scoring_bias_honest.pdf)** — the current, honest paper.
- Source: `paper/honest/scoring_bias_honest.tex` + `paper/honest/honest.bib`.

## Reproduce (zero cost, seconds)

```bash
cd paper/honest
python repro/analyze.py       # reads results_rootcause/t4fam_results.json -> results.json + LaTeX tables
python repro/make_figures.py  # -> figures/fig1..3 (pdf + png)
# build the PDF:
pdflatex scoring_bias_honest && bibtex scoring_bias_honest && pdflatex scoring_bias_honest && pdflatex scoring_bias_honest
```

Independent check of what is real vs not:

```bash
python _verify_claims.py      # recomputes every Δ and prints real-vs-claimed
```

Everything derives from the single file `results_rootcause/t4fam_results.json` (seed 42).
**No synthetic or simulated data is used.**

## Data

- ✅ `results_rootcause/t4fam_results.json` — **real.** 7 families ≤7B, base+instruct, per-variant means (Kaggle T4, greedy decode).
- ✅ `results_rootcause/rootcause_results.json` — real 3-family, 8-item pilot (raw per-item scores).
- 🗄️ `RETRACTED/` — synthetic / placeholder / fabricated artifacts kept for transparency; **not for use or citation**.
- Other files under `results_rootcause/` are derived analyses that depended on retracted inputs and are **not** relied on by the current paper.

## How to cite

Please cite only the honest paper (see `CITATION.cff`). Do not cite the retracted 22-model claims.

## License

Code MIT; paper and figures CC-BY-4.0.
