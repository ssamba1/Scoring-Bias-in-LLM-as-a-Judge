<h1 align="center">Confidence Is Not Robustness</h1>
<p align="center"><b>Instruction tuning makes LLM-as-a-judge sharper <i>and</i> more biased</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC_BY_4.0-1a1a2e?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Families-13_(base%2Binstruct)-4a5568?style=flat-square" alt="Families">
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

Across **13 open-weight families (0.1-8B; 26 checkpoints; 13,000 per-item scores)** and
**5 bias types** (rubric order, score ID, reference answer + authority, verbosity):

- Instruction tuning **sharpens** the score distribution (entropy 2.04 -> 1.45 bits, 11/13 families)...
- ...yet **increases** bias (mixed-effects instruct coef **+0.16, p<1e-3**; exact sign-flip
  permutation over all 2^13 family patterns **p=0.00098**; stable under leave-one-family,
  leave-one-vendor, and >=1B-only sensitivity checks, and under all six expected-value
  analysis specifications).
- Decisiveness correlates **negatively** with bias (rho=-0.41 pooled; -0.38 partialling out
  model size; holds within base-only and within instruct-only judges) - the confident judge
  is the more biased one. Within a single judge, **responsiveness** - not confidence - ranks
  which nuisances hurt (mean within-judge rho=+0.64, 24/26 judges).
- **Theory:** bias = *decisiveness* x *responsiveness* (Prop 1 + corollaries + a TV->logit
  lemma). Measured directly, tuning trims decisiveness a little and inflates responsiveness a
  lot (TV 0.15->0.26, d_z=1.44); the first-order product predicts the per-cell direction of
  bias change in 75% of 65 cells.
- **Causal (2 ways):** activation patching transfers the shift in a mid-network layer band;
  a **preregistered stage ablation** (OLMo-2 1B/7B, Tulu-3-8B ladders) shows **SFT installs
  the responsiveness (84-99% of the rise); DPO/RLVR install the confidence**.
- **Replications:** public Dolly-15k items (7/8 families, rho=-0.44); three prompt templates;
  more in flight (new bias types, Chinese, 14B - preregistered P10-P13).
- **Ground truth:** nuisances wreck real good-vs-bad discrimination (rubric reversal:
  accuracy 0.98->0); tuning does not protect it.
- **Mitigations:** marginalizing over score formats cuts bias **59%**; template ensembling
  cuts **22%**; a *more decisive* readout (argmax) makes it **worse** (1.09 -> 1.88).
- **Honest boundaries** (reported, not hidden): the out-of-sample predictor is a rank signal
  (rho=0.58) whose R^2 CI spans zero at n=13; the increase attaches to the continuous
  expected-value readout (argmax quantization hides it except for content probes); the
  entropy-bias relation is flat in the small >3B subsample; attention to nuisance tokens is
  an explicit null (refutes the fabricated "IIAR" mechanism of the retracted version).

**Confidence is not robustness.**

## Reproduce (from the committed raw data, seconds)

```bash
cd paper/honest/repro
pip install -r requirements-repro.txt
python analyze_peritem.py       # deltas, flip rates, domain, mixed-effects, tables
python analyze_mechanism.py     # entropy<->bias, generality, predictor, mitigation, size control
python analyze_gold.py          # ground-truth discrimination
python analyze_robustness.py    # clustered stats, spec curve, permutation, forest, anatomy
python analyze_stages.py        # preregistered stage ablation (P7-P9)
python make_mech_figures.py && python make_concept_figure.py && python make_forest_figure.py
python make_stage_figure.py && python make_exact_figure.py
cd .. && pdflatex scoring_bias_v2 && bibtex scoring_bias_v2 && pdflatex scoring_bias_v2 && pdflatex scoring_bias_v2
```

**CI-enforced:** `.github/workflows/repro.yml` reruns every analyzer on the committed raw
files and fails on any numerical drift. **No synthetic or simulated data is used.**

## Real data of record

| Raw file (committed) | Experiment | Harness |
|---|---|---|
| `repro/results_scaled.json` | 13 families x 5 bias types, per-item + distributions | `scaled_harness.py` |
| `repro/gold_results.json` | 20 gold good/bad pairs | `gold_harness.py` |
| `repro/patch_results.json` | activation patching (per layer) | `patch_harness.py` |
| `repro/results_multitemplate.json` | 3 prompt templates x 3 families | `multitemplate_harness.py` |
| `repro/attn_results.json` | attention-to-nuisance null | `attention_harness.py` |
| `repro/results_dolly.json.gz` | public-items replication (Dolly-15k) | `dolly_harness.py` |
| `repro/results_stages.json.gz` | alignment-stage ablation (preregistered) | `stage_harness.py` |

Preregistrations (predictions committed before data): `paper/honest/PREREGISTRATION.md`
(P1-P6 main, P7-P9 stages, P10-P13 in-flight). Prior fabricated artifacts:
quarantined in `RETRACTED/`, audited in `DATA_INTEGRITY_AUDIT.md`.

## How to cite

Cite only `scoring_bias_v2` (see `CITATION.cff`). Do **not** cite the retracted 22-model claims or
the superseded 7-model paper.

## License

Code MIT; paper and figures CC-BY-4.0.
