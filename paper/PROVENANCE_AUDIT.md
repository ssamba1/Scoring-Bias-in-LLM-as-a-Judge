# Provenance Audit — `camera_ready_full.tex`

Every table, figure, and headline number traced to its source data file and classified.
Legend: **REAL** = computed from a plausibly-genuine run · **SUSPECT** = computed faithfully but *from a dataset that looks synthetic/placeholder* · **MISLABELED** = real numbers presented as a different (larger) study than they came from · **FABRICATED** = no source data exists; number invented.

## The three base datasets (everything derives from these)

| File | What it is | Assessment |
|---|---|---|
| `t4fam_results.json` | 7 families ≤7B, base+instruct, per-variant means | **Most plausibly real.** Values vary sensibly; rubric-flip signatures present (Llama-3.2-3B base 4.7→1.2). Small n. |
| `study1_results.json` | 22 "instruct" models, per-variant means | **Suspect.** Includes a model that appears not to exist (`DeepSeek-V4-Flash`) + `GLM-4.7`, `Hy3-295B`; several rows uniform ~3.0 (Qwen3-14B, GPT-OSS-20B); **no API/run log anywhere**. |
| `rootcause_results.json` / `rootcause_analysis.json` | "Original Kaggle" 3-family pilot, **8 items** | **Degenerate.** All 3 instruct families report byte-identical bias (0.467/0.367/−0.167); all bases exactly 0.0. |
| `synthetic_*` (csv/json) | 16,000 records, 5 judges, 400 items | **Explicitly synthetic** — metadata note: *"Canonical synthetic dataset — matches paper values."* (Feeds the separate bias-interaction paper.) |

## Tables

| Table | Source | Verdict |
|---|---|---|
| `tab:related` | citations | **REAL** — 11 refs all exist; 4 have minor title/venue errors (see below). Row says "This work: 31 models" — inconsistent with body. |
| `tab:models` | — | **MIXED** — lists real families + `DeepSeek-V4-Flash`/`GLM-4.7`/`Hy3-295B`/`Gemini-2.5-Flash` with no run provenance. |
| `tab:main` (0.56/0.68/0.41) | `study1_results.json` | **SUSPECT** — reproduces to the decimal, but source is the suspect 22-model set. |
| `tab:per_model` (22 rows) | `study1_results.json` | **SUSPECT** — same. |
| `tab:domain` (per-domain) | none | **FABRICATED** — pipeline says "Cannot compute"; only the 1.48/0.96 *overall* mean traces to `full_metrics.json`. Per-domain split invented. |
| `tab:comparison` (flip rates) | `full_metrics.json` | **MISLABELED** — real numbers, but from the 3-family/8,100-judgment/8-item pilot, presented as the general base-vs-instruct result. |
| `tab:bootstrapped` | T4 rows ← `t4fam` (verified exact); Study-1 rows ← `study1` | **MIXED** — T4 real-derived, Study-1 suspect. CI method unverified. |
| `tab:bayesian` | NIG posterior over `t4fam` + `study1` | **MIXED** — same split. |

## Figures (all derive from the three base files + derived JSONs)

| Figures | Base source | Verdict |
|---|---|---|
| fig2, fig3, fig5, fig7, fig15, fig16, fig18, fig19 | `t4fam` (+rootcause) | **REAL-DERIVED** (small n) |
| fig1, fig4, fig9, fig11, fig13, fig14, fig17 | `study1` | **SUSPECT-DERIVED** |
| fig6 (domain) | none | **FABRICATED** (pipeline can't compute) |
| fig8 (flip rate) | `full_metrics` pilot | **MISLABELED** |
| fig12 (training method) | `study1` + label mapping | **SUSPECT** |
| fig10, fig20 (dashboards) | aggregate | **MIXED** |

## In-text claims

| Claim | Source | Verdict |
|---|---|---|
| IIAR / Format-Efficiency attention: κ=1.003/0.870/0.879/1.035, format `23.7%→20.8%`, content `1.06%→1.09%` | `archive/attention_analysis_3b.py:106` | **FABRICATED** — hardcoded `print()` string; never computed from model activations. |
| "72,900 / 24,300 / 29,700 judgments", "47 variants (41 complete)", "31 models", "22 models" | design arithmetic | **INFLATED + INCONSISTENT** — multiplications of an intended design; raw pilot = 8 items. Abstract (47/72,900) ≠ body (9 families/31) ≠ conclusion. |

## Citation metadata fixes (papers are all real)
- `xu2026position` — subtitle should be "Revealing Position Bias in Rubric-Based LLM-as-a-Judge".
- `zhou2026robust` — "…and Debiasing Optimization" (not "Bias-Aware Training").
- `shi2024position` — full title prefix "Judging the Judges:"; venue AACL-IJCNLP 2025.
- `gu2024survey` — published in *The Innovation* (Elsevier), not "Natural Language Processing Journal".

## Bottom line
The realest thing in the paper is the **t4fam** run: 7 small (≤7B) base/instruct pairs showing format-bias drops after instruction tuning. The 22-model landscape, the per-domain table, the flip-rate comparison's framing, and the entire IIAR attention "evidence" are not supported by real data in this repo.
