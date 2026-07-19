<h1 align="center">Confidence Is Not Robustness</h1>
<p align="center"><b>Instruction tuning makes LLM-as-a-judge sharper <i>and</i> more biased</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_4.0-1a1a2e?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Families-9_(base%2Binstruct)-4a5568?style=flat-square" alt="Families">
  <img src="https://img.shields.io/badge/Bias_types-5-2b6cb0?style=flat-square" alt="5 bias types">
  <img src="https://img.shields.io/badge/data-real_only-38a169?style=flat-square" alt="real data">
</p>

---

> ### ⚠️ Correction notice (2026-07)
> **Earlier versions of this project reported a 22-model / 40,500-judgment "landscape", a
> "content bias increases" finding, and an "IIAR" attention mechanism. Those were synthetic,
> placeholder, or fabricated** — see the full audit in [`DATA_INTEGRITY_AUDIT.md`](DATA_INTEGRITY_AUDIT.md)
> and [`paper/PROVENANCE_AUDIT.md`](paper/PROVENANCE_AUDIT.md). Those artifacts are quarantined in
> [`RETRACTED/`](RETRACTED/) and must not be cited. The Zenodo DOI `10.5281/zenodo.21361920`
> archives that retracted version.
>
> An intermediate honest paper (`superseded/scoring_bias_honest.*`, 7 tiny models) used
> **parse-based** scoring, which we later show is a measurement confound (it silently drops items on
> weak judges — Appendix A of the current paper). It is superseded and should not be cited.

---

## The paper

**[`paper/honest/scoring_bias_v2.pdf`](paper/honest/scoring_bias_v2.pdf)** — *Confidence Is Not
Robustness.* Source: `paper/honest/scoring_bias_v2.tex` (+ `macros.tex`, `honest.bib`).

We study whether a stronger, more instruction-tuned LLM judge is a fairer one. It is not.

## Finding

Across **13 open-weight families (0.1–8B)** and **five bias types** (rubric order, score ID,
reference answer, plus **authority** and **verbosity** from outside the scoring-bias literature),
scored by the **expected value of the answer-token distribution** (which fixes the parse-failure
confound):

- Instruction tuning **sharpens** the score distribution (entropy 2.04 → 1.45 bits, 11/13 families)…
- …yet **increases** bias across **all 5** types (linear mixed-effects instruct coef **+0.16, p<10⁻³**).
- So decisiveness correlates **negatively** with bias (ρ = −0.41, p<10⁻³; the exact √Var term ρ = −0.25).
- Decisiveness even **predicts** bias out-of-sample (leave-one-family-out R² = 0.27) — but **inverted**: the more confident judge is the more biased one.
- **Theory:** bias = *decisiveness* × *responsiveness* (Prop 1 + Corollary 1); tuning inflates
  responsiveness faster than it trims decisiveness, so the sign flips.
- **Causal:** activation-patching the instruct representation into the base model transfers the shift
  in a single mid-network layer band (Qwen2.5-1.5B, n=35 items).
- **Ground truth:** nuisances wreck real good-vs-bad discrimination (rubric reversal: accuracy 0.98→0);
  tuning does not protect it.
- **Mitigation:** marginalizing over nuisance formats cuts bias **60%**, where a more confident
  readout makes it worse.

**Confidence is not robustness.**

## Reproduce (from the committed raw data, seconds)

```bash
cd paper/honest/repro
python analyze_peritem.py   results_scaled.json    # deltas, flip rates, domain, mixed-effects, tables
python analyze_mechanism.py results_scaled.json    # entropy↔bias, generality, predictor, mitigation
python analyze_gold.py      gold_results.json       # ground-truth discrimination
python make_mech_figures.py                         # all figures from real data
cd .. && pdflatex scoring_bias_v2 && bibtex scoring_bias_v2 && pdflatex scoring_bias_v2 && pdflatex scoring_bias_v2
```

Every number and figure regenerates from the committed raw files
(`repro/results_scaled.json`, `repro/gold_results.json`, `repro/patch_results.json`), seed 42.
**No synthetic or simulated data is used.**

## Real data of record

- ✅ `paper/honest/repro/results_scaled.json` — 9 families × 5 bias types, per-item scores + entropy (logit scoring).
- ✅ `paper/honest/repro/gold_results.json` — 12 gold good/bad pairs × 5 families.
- ✅ `paper/honest/repro/patch_results.json` — causal activation-patching (Qwen2.5-1.5B, per layer).
- 🗄️ `RETRACTED/` — fabricated / synthetic artifacts from prior versions; **not for use or citation**.
- Data-collection harnesses that produced these: `paper/honest/repro/{scaled_harness,gold_harness,patch_harness}.py` (Kaggle).

## How to cite

Cite only `scoring_bias_v2` (see `CITATION.cff`). Do **not** cite the retracted 22-model claims or
the superseded 7-model paper.

## License

Code MIT; paper and figures CC-BY-4.0.
