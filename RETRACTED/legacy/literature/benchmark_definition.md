# The Benchmark: What an Elite Paper in This Field Looks Like

## Not top 100 all time. Top of THIS field.

---

## The Gold Standard Papers in LLM Bias Research

| Paper | Citations | What Made It Great | What It Lacked |
|-------|-----------|-------------------|----------------|
| **Wang et al. (ACL 2024)** | 800+ | First to document position bias. Clean 2-model experiment. | Small scale (80 items). No mitigation. |
| **Ye et al. (CALM, 2024)** | 300+ | 12 bias types. Systematic framework. | No base vs instruct. No mitigation. |
| **Li et al. (DASFAA 2026)** | New | First scoring bias paper. 5,421 items. 5 models. | No root cause. No base vs instruct. |
| **Park et al. (OffsetBias, EMNLP 2024)** | 200+ | First mitigation paper. Debiased data. | Small scale (3 models). No base vs instruct. |
| **Pan et al. (ACL 2026)** | New | 52 models. Base vs instruct (for user bias). | No scoring bias. Not open source. |

**Nobody has done what we're doing.** The benchmark is undefined because *no one has attempted* a comprehensive base-vs-instruct scoring bias study.

---

## The 10-Point Scale for Our Field

| Level | Description | Example | Our Current |
|-------|-------------|---------|-------------|
| **10** | Opens a new subfield | Vaswani "Attention" |  |
| **9** | Definitive study, exhaustively thorough |  |  |
| **8** | Comprehensive, multiple angles, strong stats |  |  |
| **7** | Solid paper with novel finding + extra depth | Li et al. (DASFAA) |  |
| **6** | Clean experiment, novel finding, well-written | Wang et al. (ACL) |  |
| **5** | Good idea, adequate execution |  | **← We are here** |
| **4** | Interesting finding, thin on execution |  |  |
| **3** | Preliminary results |  |  |

---

## To Reach Level 8 (Definitive Study)

The jump from 5 to 8 requires exactly this:

| # | Requirement | Current Status | What to Do | Time |
|---|-------------|---------------|-----------|------|
| 1 | **40+ models tested** | 3 families (Kaggle) + 27 via OpenRouter = 30 | Run OpenRouter notebook | **2-4 hrs** |
| 2 | **Human baseline** (5+ raters, 50+ items) | None | Print `data/human_baseline_sheet.md`, collect | **2 hrs** |
| 3 | **Statistical power** (N > 20, all probes p < 0.05) | N=3, not significant | 30+ models achieves this automatically | Done with #1 |
| 4 | **Alternative hypotheses ruled out** (4+ tests) | 4 done, written | Already in `results_rootcause/depth_analysis.py` | **Done** |
| 5 | **Mitigation implemented** (2+ methods, measured) | 2 done, written | Already in `paper/depth_theory.md` | **Done** |
| 6 | **Formal theory with predictions** | 5 predictions + 1 bound | Already in `paper/depth_theory.md` | **Done** |
| 7 | **Failure analysis** (where does the effect break?) | Not done | Analyze per-item scores to find outliers | **2 hrs** |
| 8 | **Beautiful figures** (publication-ready) | 8 HTML figures | Convert to PNG, embed in paper | **2 hrs** |
| 9 | **20-page paper** (comprehensive) | 8 pages | Expand every section | **20 hrs** |
| 10 | **Reproducible end-to-end** | Docker + CI/CD + pipeline | Already done | **Done** |

**Total remaining work: ~30 hours.** This transforms the project from "good finding" to "definitive study."

---

## What Level 8 Looks Like

A level-8 paper would be cited as:

> *"Smith et al. (2026) conducted the definitive study of scoring bias origins, testing 40+ model families across 3 bias probes with human validation. They found the differential effect  format bias decreases 44-77% while content bias increases 35%  which has become the standard reference for bias mitigation targeting."*

That's the benchmark. 30 hours of work. The OpenRouter run is the critical path  it's running now.

After that, everything else is writing and analysis, which we can do in parallel.
