# RETRACTED artifacts — do not use or cite

These files were part of earlier versions of this project. An audit (2026-07) found they are
**synthetic, placeholder, or fabricated**, or are manuscripts/pages built on such data. They are kept
here for transparency and accountability, not for reuse. See [`../DATA_INTEGRITY_AUDIT.md`](../DATA_INTEGRITY_AUDIT.md)
and [`../paper/PROVENANCE_AUDIT.md`](../paper/PROVENANCE_AUDIT.md) for the full evidence.

## Second sweep (2026-08-02) — artefacts the first retraction missed

The 2026-07 retraction moved the manuscripts and the fabricated data files. It did not move the
things *built* from them, which stayed in the live tree where a reader would reasonably take them
for current results. A signature sweep over every tracked file outside this directory — searching
for the fabricated per-domain values, the non-existent model names the audit identified
(`DeepSeek-V4-Flash`, `GLM-4.7`, `Qwen3-*`, `Llama-4*`), and the retracted scale claims
("22-model landscape", "40,500 judgments", "31 variants") — found **44** such files. All are now
here, at their original paths.

| Group | Files | What they were |
|---|---|---|
| `paper/tables/` | `tab_domain.tex`, `tab_models.tex`, `tab_per_model.tex` | The fabricated per-domain table and the model tables listing models that do not exist. |
| `paper/figures/`, `paper/figures_advanced/` | 5 files incl. `study1/all_tables.tex`, `study1/tab6_domain.tex`, `infographic.svg`, the figure generators | Figure sources and generators over the retracted landscape. |
| `paper/interactive/` | `bias_explorer.html`, `model_comparison.html`, `ranking_table.html` | Public dashboards. `ranking_table.html` ranked `Qwen3-14B` — a model that does not exist — with precise scores. |
| `paper/archive/`, `paper/` | `camera_ready.tex`, `theoretical_monograph.tex`, `quantified_limitations.tex`, `supplementary_standalone.tex`, `apply_remaining.py` | Superseded manuscripts and a script that rewrites them. |
| `results_rootcause/` | 26 files: `analysis_output/`, `validation/`, `archive/`, and the top-level analysis scripts and JSON | Every analysis computed over the fabricated 22-model data, including cross-validation, model rankings and "peer review defence" outputs. |

Two files that match the same signatures are deliberately **not** here: `DATA_INTEGRITY_AUDIT.md` and
`paper/PROVENANCE_AUDIT.md`. Naming this material is their purpose.

`paper/interactive/index.html` stays live, rewritten: it now carries a retraction notice, links only
to the dashboard built on verified data, and no longer advertises "36 models" or "22 instruct models
ranked". `paper/interactive/base_vs_instruct.html` also stays — it names only real, measured models.

### Third sweep (2026-08-11) -- placeholder-authored drafts

Extending the sweep with the retracted submission's placeholder author names found five more
drafts of the fabricated bias-interaction study still live: `paper/auto_generated/auto_paper.tex`
(its own header records "16000 judgments, 5 judges, 400 items" -- the synthetic record set),
`paper/archive/formal_framework.tex`, `paper/archive/theoretical_appendix.tex`,
`paper/monograph.md` and `paper/unified_theory.md`. None carried the fabricated model names, which
is why the earlier sweeps missed them; all describe the study the audit retracted, under authorship
that was never filled in.

## `data/` — fabricated or unusable result files

| File | Why retracted |
|---|---|
| `synthetic_results.csv`, `synthetic_metadata.json`, `synthetic_summary.json`, `synthetic_v2_metadata.json` | Explicitly synthetic. `synthetic_metadata.json` states: *"Canonical synthetic dataset — matches paper values."* 16,000 generated records. |
| `simulation_results.json` | Simulated, not measured. |
| `bayesian_analysis_synthetic.json` | Bayesian stats over the synthetic bias-interaction data (n=9,600 fabricated). |
| `study1_results.json`, `study1_complete.json`, `study1_max_scale.json` | The "22-model landscape." Contains models that do not exist (e.g. `DeepSeek-V4-Flash`, `GLM-4.7`) and rows uniform at ~3.0; no API/run log exists. |
| `rootcause_analysis.json` | Three different families report byte-identical bias summaries (0.467 / 0.367 / −0.167). Degenerate/placeholder. |
| `full_metrics.json` | Source of the flip-rate and Cohen's-d tables; self-labels as the 3-family / 8-item / 8,100-judgment pilot, but was presented as the full study. |
| `new_families_results.json`, `all_results_merged.json` | Mixed/partial results depending on the above. |

## `paper/` — manuscripts built on the fabricated data

`camera_ready_full.tex`, `arxiv.tex`, `neurips_hs.tex`, `acl_srw.tex`, `camera_ready.html`,
`camera_ready_publishable.html`, `paper_biasinteraction_compiled.html`, `scoring_bias.pdf`.

These encode the retracted "22-model landscape", the fabricated per-domain table, the mislabeled
flip-rate comparison, the hardcoded "IIAR"/attention numbers, and internally inconsistent
model/judgment counts (47 vs 31 vs 22; 72,900 vs 54,000 judgments).

## `pages/` — public claim pages

`index.html`, `presentation.html`, `research_hub.html`, `results_package.html` — landing/summary
pages that advertised the retracted numbers.

---

**The replacement, honest study lives in [`../paper/honest/`](../paper/honest/)** and uses only the
provenance-verified `results_rootcause/t4fam_results.json`.

## legacy/ (added 2026-07-20)

`legacy/` holds the remaining scaffolding of the retracted-era project (docs,
citation guide, blog draft, dashboards, pipelines, synthetic-data generators,
tests, extensions). Quarantined wholesale when the deleted Zenodo record was
replaced: several files instructed readers to cite the removed DOI
(10.5281/zenodo.21361920) or described fabricated results. Nothing in `legacy/`
is part of the paper of record. The retracted-era `data/`, `docs/`,
`appendices/`, and `outreach/` trees moved here likewise.
