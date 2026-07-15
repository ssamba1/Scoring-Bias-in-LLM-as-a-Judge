# 500 Autonomous Improvements — S+ Tier Paper

**Rule:** Each item is a concrete action I can perform entirely on my own (CPU Python, paper editing, code writing, file creation). Items marked **[NEED USER]** require your action — I explain exactly what and why.

---

## A. PAPER TEXT — DATA MISMATCHES (32 items)

| # | Action | What I'll build/verify |
|---|--------|----------------------|
| 1 | Abstract: change "3 families" → "10 families with base-instruct comparison" | Edit `camera_ready_full.tex` line 33 |
| 2 | Abstract: change "8,100 judgments" → "27,000+ judgments" | Same line — recalculate from 10×2×3×3×50×3 |
| 3 | Abstract: update "22 instruct-tuned models (29,700 judgments)" to include 14 base+instruct models → 36 variants total | Line 33 |
| 4 | Intro: "3 families with both base and instruct pairs" → "10 families" | Line 50 |
| 5 | Intro: "3 families with both base and instruct pairs" again in per-family analysis | Line 255 |
| 6 | Methods: change "8,100 judgments" equation to 27,000 | Lines 161-165 |
| 7 | Methods: change "3 open-weight model families" → "10 open-weight families" | Line 116 |
| 8 | Methods: "6 model variants" → "20 model variants" | Line 116 |
| 9 | Methods: "An additional 22 instruct-only models provide model diversity breadth (29,700 additional judgments)" → "An additional 22 instruct-only models (16,500 judgments)" | Line 165 |
| 10 | Results: "8 families with both base and instruct variants" → "10 families" | Line 204 |
| 11 | Results: "7 of 8 families" showing format bias ↓ → "9 of 10 families" | Line 204 |
| 12 | Results: "3 families with base+instruct pairs" → "10 families" | Line 254 |
| 13 | Limitations: "Model family count (8 families)" → "(10 families)" | Line 313 |
| 14 | Limitations: "3 model families (df = 2)" → "10 families (df = 9)" | Line 274 |
| 15 | Limitations: "The primary comparison is based on 8 families" → "10 families" | Line 313 |
| 16 | Statistical significance: "3 model families (df = 2)" → "10 families (df = 9)" | Line 274 |
| 17 | Results: "This finding replicates across both small (≤3B) and larger models" — verify 10 families show this | Cross-check all 10 families |
| 18 | Results: "content increase after instruction tuning in larger models (Llama-3-8B: +1.58, Llama-3.2-3B: +0.2)" — update if new families change this | Recompute with 10 families |
| 19 | Results: "smaller models (≤1.5B: mean -0.73)" — verify with 10 families | Cross-check |
| 20 | Methods equation: "3 families × 2 variants × 3 probes × 3 variants × 50 items × 3 repeats = 8,100" → new numbers | Lines 161-164 |
| 21 | "OpenRouter" → "OpenRouter + HuggingFace local" in abstract | Abstract implies all data from OR |
| 22 | "Five models from the original OpenRouter list were excluded" — verify the list is current | Line 165 |
| 23 | Per-model table (tab:per_model): verify all 22 instruct models match actual data | Cross-check study1_results.keys() vs table rows |
| 24 | Per-model table: verify Δ values match computed values from JSON | Compute and compare |
| 25 | Model table (tab:models): verify all families listed have data | Cross-check with results |
| 26 | Model table: add base+instruct indicators for the 10 families | Add daggers |
| 27 | "3 families with both base and instruct pairs" in Discussion → "10 families" | Line 280 |
| 28 | Alternative explanations section — 4 explanations, update to reference 10 families | Lines 263-271 |
| 29 | Mitigation framework: "two RLHF-trained families... single SFT+DPO family" → update with 10-family data | Lines 255-256 |
| 30 | Model table (tab:models): add Mistral-7B-v0.3, StableLM-2-1.6B, Qwen2.5-0.5B, Qwen2.5-1.5B, etc. | Table currently missing many families |
| 31 | Abstract: update "29,700 judgments" → correct number from 10 base-instruct + 22 instruct | Recompute |
| 32 | Paper claims "22-model landscape" in title but data has 36 variants | Either adjust title or clarify |

## B. PAPER TEXT — SUBSTANTIVE IMPROVEMENTS (48 items)

| # | Action | Description |
|---|--------|-------------|
| 33 | Add Bayesian results section | Replace frequentist t-tests with Bayesian hierarchical model (P>0.999 for Score ID ↓) |
| 34 | Add Bayes factor interpretation | BF=0.01 for Score ID, what it means |
| 35 | Add equivalence test for small models | ≤1.5B models — test if content bias truly unchanged |
| 36 | Add variance decomposition section | Between-model vs within-model variance % |
| 37 | Add model ranking stability analysis | Kendall's W, top-3 Jaccard overlap |
| 38 | Add item analysis section | Difficulty, discrimination, dimensionality |
| 39 | Add score inflation analysis | Are instruct models inflating scores systematically? |
| 40 | Add interaction effects section | Do rubric × score_id biases interact? |
| 41 | Add domain-specific bias analysis | Does bias magnitude vary by subject? |
| 42 | Add multilingual item analysis | Arabic, Spanish, Hindi, Chinese items exist |
| 43 | Add training-method analysis | SFT vs DPO vs RLHF — different bias profiles? |
| 44 | Add model-size correlation analysis | Formal test of size vs bias correlation |
| 45 | Add bootstrapped confidence intervals | 10K resamples for all Δ values |
| 46 | Add non-parametric tests | Wilcoxon signed-rank, Mann-Whitney |
| 47 | Add effect size confidence intervals | Cohen's d with 95% CI |
| 48 | Add outlier analysis | Grubbs test, IQR-based detection |
| 49 | Add direction consistency analysis | Sign test across families |
| 50 | Add leave-one-out sensitivity | Remove each family, recheck pattern |
| 51 | Rewrite conclusion to cite specific data | "Score ID bias averages Δ=0.68 (Table 2)..." not generic repo URL |
| 52 | Introduce explicit RQ numbering | RQ1-RQ4 clearly labeled throughout |
| 53 | Add hypothesis numbering | H1-H4 with clear predictions |
| 54 | Add concrete example in introduction | Expand the biology answer example |
| 55 | Replace "first to" language | "We present initial evidence toward..." |
| 56 | Replace Contribution #4 (open infra) | Replace with "Format Efficiency Hypothesis" or "Scale-dependent differential effect" |
| 57 | Add explicit "Novelty" paragraph | After contributions, before related work |
| 58 | Add structured abstract | Background/Methods/Findings/Conclusions labeling |
| 59 | Add keywords section | Already exists, verify formatting |
| 60 | Add CRediT author taxonomy | Already exists, verify |
| 61 | Add pre-registration statement | Already exists, consider moving to methods |
| 62 | Add data availability with DOI | Already exists, verify link works |
| 63 | Add ethics statement | Already exists, verify |
| 64 | Normalize "base vs instruct" terminology throughout | Inconsistent: "base-instruct", "base vs instruct", "BvI" |
| 65 | Normalize model name formatting | "Llama-3.2-3B" vs "Llama3.2-3B" inconsistency |
| 66 | Fix LaTeX: `\verb` inside `\begin{quote}` | Line 145-151 uses `\verb`-like pattern, check for fragility |
| 67 | Fix LaTeX: doubled backslashes from Windows patch tool | Scan entire .tex for `\\\\` |
| 68 | Fix LaTeX: table row-end consistency | All `\\` not `\\\\` |
| 69 | Add line numbers for reviewer convenience | Already has `lineno` package, verify |
| 70 | Add appendix structure | A: Models, B: Results, C: Proofs, D: Reproduce |
| 71 | Expand limitations to 8 items | Add "single prompt template" as separate, "no cross-lingual" |
| 72 | Add broader impact with actionable items | Already exists, expand to 3 specific recommendations |
| 73 | Add "Limitations of scope" paragraph in intro | Already exists, update numbers |
| 74 | Remove "Illustrative" or "approximate" values | Check every table for non-computed values |
| 75 | Add N-overlap check | Cross-check every `\cite{}` has a matching `@` in .bib |
| 76 | Add `\usepackage{appendix}` check | Noted as potential issue on MikTeX |
| 77 | Fix "the the" and other typos | Full proofread pass |
| 78 | Add author footnote with ORCID | Corresponding author formatting |
| 79 | Add code repository URL to abstract | For arXiv readers |
| 80 | Add to methods: clearly state all 10 families with access method | Currently vague |

## C. FIGURES & VISUALIZATIONS (45 items)

| # | Action | Description |
|---|--------|-------------|
| 81 | Generate Fig1: Bias landscape bar chart | 22 models × 3 probes, Δ values, publication-quality |
| 82 | Generate Fig2: Format ↓ Content ↑ scatter plot | 10 families, format change vs content change |
| 83 | Generate Fig3: Scale-dependent differential effect | ≤1.5B vs 2-7B vs 8B+, faceted |
| 84 | Generate Fig4: Model ranking heatmap | 22 models sorted by bias magnitude |
| 85 | Generate Fig5: Per-family base→instruct delta | 10 families, paired lines |
| 86 | Generate Fig6: Domain breakdown | Science/Tech/Humanities/DailyLife/Math |
| 87 | Generate Fig7: Bias variance decomposition | Pie/bar: between-model vs within-model |
| 88 | Generate Fig8: Flip rate comparison with Li et al. | Bar chart comparing flip rate ranges |
| 89 | Generate Fig9: Bayesian posterior distributions | 3 probes, posterior plots |
| 90 | Generate Fig10: Attention analysis visualization | 0.5B vs 3B, format vs content κ |
| 91 | Generate Fig11: Training method comparison | SFT vs DPO vs RLHF bias profiles |
| 92 | Generate Fig12: Item discrimination plot | Item difficulty vs bias magnitude |
| 93 | Generate Fig13: Score distribution comparison | Base vs instruct, per-probe |
| 94 | Generate Fig14: Outlier detection plot | Grubbs/GESD flagged models |
| 95 | Generate Fig15: Bootstrap uncertainty | Δ with 95% CI bars |
| 96 | Generate Fig16: Direction consistency sign plot | 10 families, +/- matrix |
| 97 | Generate Fig17: Model size vs bias correlation | Scatter with regression line |
| 98 | Generate Fig18: Cross-probe correlation matrix | Rubric × ScoreID × RefAns |
| 99 | Generate Fig19: Leave-one-out sensitivity | Jackknife Δ values |
| 100 | Generate Fig20: Power analysis curve | N vs power for observed effect sizes |
| 101 | Generate Fig21: Multilingual bias comparison | EN/ES/ZH/AR/HI comparison |
| 102 | Generate Fig22: Item-level score distribution | 50 items, box plot per model |
| 103 | Generate Fig23: Format Efficiency Hypothesis diagram | Conceptual diagram of attention redistribution |
| 104 | Generate Fig24: IIAR framework diagram | Theoretical model |
| 105 | Generate Fig25: Experimental design diagram | Pipeline overview |
| 106 | Combine Figs 1-3 into single multi-panel figure | For paper's main results |
| 107 | Generate table figure: 10-family delta matrix | Heatmap |
| 108 | Generate figure: score inflation by model | Instruct score - base score |
| 109 | Generate figure: reference answer effect by domain | Good vs poor exemplar effect |
| 110 | Generate figure: rubric order variants | Normal, reversed, random comparison |
| 111 | Generate figure: score ID variants | Numeric, letter, descriptive |
| 112 | Generate figure: prompt ablation results | 5 templates × 2 models |
| 113 | Generate figure: bias × model family interaction | ANOVA-style interaction plot |
| 114 | Generate figure: model ranking with uncertainty | Rank with bootstrapped CI |
| 115 | Generate figure: item-level Δ per model | 50 individual item bias scores |
| 116 | Generate figure: cumulative distribution of biases | ECDF plots |
| 117 | Generate figure: bias magnitude by parameter count | Log-scale parameter count vs Δ |
| 118 | Generate figure: attention head analysis | Per-layer format/content attention |
| 119 | Generate figure: token classification visualization | Which tokens get attention |
| 120 | Generate figure: Format Efficiency vs IIAR comparison | Side-by-side predicted vs observed |
| 121 | Generate all figures in paper's figure directory | Save to `paper/figures/` |
| 122 | Add proper LaTeX figure includes | `\includegraphics` with caption, label |
| 123 | Create supplementary figures PDF | All extra figures in appendix |
| 124 | Set Seaborn style consistent across all figures | paper-quality defaults |
| 125 | Add colorblind-friendly palette | Check all figures |

## D. STATISTICAL ANALYSIS — CPU-RUNNABLE (38 items)

| # | Action | What I'll compute |
|---|--------|-------------------|
| 126 | Compute bootstrapped Δ for all 22 instruct models | 10K resamples, 95% CI |
| 127 | Compute bootstrapped Δ for all 10 base-instruct families | Same, paired design |
| 128 | Compute Cohen's d with 95% CI for all probe comparisons | Using bootstrapped variances |
| 129 | Compute Hedges' g (small-sample correction) | N=10 families, appropriate |
| 130 | Compute Wilcoxon signed-rank test for all probes | Non-parametric alternative |
| 131 | Compute Mann-Whitney U for instruct-only comparisons | Between-group |
| 132 | Compute Shapiro-Wilk normality test | For all Δ distributions |
| 133 | Compute skewness and kurtosis | For all bias metrics |
| 134 | Compute Bayesian hierarchical model on CPU | Using statsmodels or conjugate priors |
| 135 | Compute Bayes factors for all probes | BIC approximation |
| 136 | Compute equivalence test (TOST) for small models | ≤1.5B content bias |
| 137 | Compute variance decomposition (ANOVA) | Between/within model % |
| 138 | Compute intra-class correlation (ICC) | Reliability across repeats |
| 139 | Compute Kendall's W for model ranking | Ranking consistency |
| 140 | Compute top-3 Jaccard similarity | Across bootstraps |
| 141 | Compute Grubbs outlier test on all Δ distributions | Flag outlier models |
| 142 | Compute IQR-based outlier detection | Robust |
| 143 | Compute leave-one-out sensitivity | Jackknife Δ after removing each family |
| 144 | Compute direction consistency (sign test) | P(X families show same direction) |
| 145 | Compute Pearson/Spearman: size vs bias | Correlation across 22 models |
| 146 | Compute cross-probe Pearson correlation | Rubric × ScoreID × RefAns |
| 147 | Compute item discrimination (item-total correlation) | Which items detect bias best |
| 148 | Compute item difficulty (mean score) | Per-item average |
| 149 | Compute score inflation (instruct - base mean) | Per-family |
| 150 | Compute pairwise model agreement | Agreement rate between model pairs |
| 151 | Compute Fleiss' kappa for multi-model agreement | Across 22 models |
| 152 | Compute by-domain bias | 5 domains, 10 items each |
| 153 | Compute by-domain ANOVA | Domain × Probe interaction |
| 154 | Compute training method contrast | SFT vs DPO vs RLHF |
| 155 | Compute effect of excluded models | Sensitivity to 5 excluded OpenRouter models |
| 156 | Compute power analysis for N=10 | What effect sizes are detectable? |
| 157 | Compute power analysis for N=22 | Full 22-model set |
| 158 | Compute minimum detectable effect | At α=0.05, 80% power |
| 159 | Compute Bayesian posterior intervals for all Δ values | HDI with 95% |
| 160 | Compute P(Δ < 0) for all base-instruct comparisons | Probability content bias decreased |
| 161 | Compute Bayes factor for differential effect | Format vs content direction |
| 162 | Compute model-based effect size (Glass's Δ) | Using base SD as reference |
| 163 | Compute effect size for training method contrast | RLHF vs SFT+DPO |

## E. CODE QUALITY & INFRASTRUCTURE (38 items)

| # | Action | Description |
|---|--------|-------------|
| 164 | Add pre-commit config | `.pre-commit-config.yaml` |
| 165 | Add `.editorconfig` | Cross-editor consistency |
| 166 | Add `.gitattributes` | Line endings, diff settings |
| 167 | Add `requirements.txt` with pinned versions | Pinned from current environment |
| 168 | Add `environment.yml` for conda | Conda alternative |
| 169 | Add `setup.py` or `pyproject.toml` | Installable package structure |
| 170 | Add `conftest.py` for pytest | Test discovery config |
| 171 | Add `pytest.ini` | Test config |
| 172 | Add GitHub Actions CI: test | Python tests on push |
| 173 | Add GitHub Actions CI: lint | flake8/pylint on push |
| 174 | Add GitHub Actions CI: paper compile | LaTeX compilation check |
| 175 | Add GitHub Actions CI: Python version matrix | 3.10, 3.11, 3.12 |
| 176 | Add `Makefile` with `help`, `test`, `lint`, `paper`, `reproduce-all` | Already exists — audit and improve |
| 177 | Add Dockerfile | Verify and improve |
| 178 | Add `.dockerignore` | Keep image small |
| 179 | Add docker-compose.yml | For reproducibility |
| 180 | Add Binder config (`binder/`) | One-click reproduction |
| 181 | Add `postBuild` for Binder | Install commands |
| 182 | Add software version doc | `versions.md` with exact versions |
| 183 | Add `run_all.sh` | Complete reproduction from scratch |
| 184 | Add `run_all.ps1` | Windows alternative |
| 185 | Add `check_reproducibility.py` | Verify all outputs match |
| 186 | Add `pytest` tests for all analysis scripts | Unit tests |
| 187 | Add edge case tests | Empty results, missing keys, etc. |
| 188 | Add regression tests | Known values stay correct |
| 189 | Add data validation tests | Schema checks on JSON files |
| 190 | Add import tests | All modules import cleanly |
| 191 | Add CI badge to README | GitHub Actions |
| 192 | Add DOI badge to README | Zenodo |
| 193 | Add Python version badge | |
| 194 | Add license badge | |
| 195 | Add paper status badge | |
| 196 | Lint all Python scripts | flake8/pylint across project |
| 197 | Fix all Python lint errors | |
| 198 | Add type hints to all functions | Gradual typing |
| 199 | Add docstrings to all public functions | Google style |
| 200 | Add `__init__.py` to all packages | Proper Python packaging |
| 201 | Refactor duplicate code in analysis scripts | Many similar scripts |

## F. REFERENCES & CITATIONS (13 items)

| # | Action | Description |
|---|--------|-------------|
| 202 | Add DOI for every reference | Currently only some have DOIs |
| 203 | Verify all 17 bib entries have correct venue info | Check years, venues |
| 204 | Add missing references: recent 2025-2026 bias papers | Literature search |
| 205 | Add missing references: instruction tuning theory papers | |
| 206 | Add missing references: RLHF papers | |
| 207 | Add missing references: LLM evaluation methodology | |
| 208 | Standardize bib entry format | All @inproceedings/@article/@misc consistent |
| 209 | Add URL for every online reference | Currently howpublished for some |
| 210 | Add arxiv ID for all arXiv papers | |
| 211 | Sort bibliography alphabetically | Standard convention |
| 212 | Check `\cite{}` match vs bib keys | All 10+ citations resolve |
| 213 | Add related work table to supplement | 35+ bias types with refs |
| 214 | Add "Data/Software Citation" to references | Zenodo DOI for own data |

## G. REPRODUCIBILITY & DATA (25 items)

| # | Action | Description |
|---|--------|-------------|
| 215 | Verify # families in data = # families claimed in paper | Cross-check |
| 216 | Verify # models in data = # models in per-model table | Cross-check |
| 217 | Verify all Δ values in paper table match JSON computations | Compute from raw data |
| 218 | Verify excluded models are properly documented | 5 OpenRouter exclusions |
| 219 | Create data dictionary | Schema for all JSON/CSV files |
| 220 | Create experiment manifest | What was run, when, on what platform |
| 221 | Add platform metadata per result file | Kaggle vs Colab vs OpenRouter |
| 222 | Verify item files exist for all 50 items | combined_80_items.json has 80 |
| 223 | Document which 50 of 80 items were used | Selection criteria |
| 224 | Create per-model card for all 36 variants | Model cards directory exists |
| 225 | Add model cards for the 14 T4 models | Currently missing |
| 226 | Create HF dataset upload script | Code exists, verify it works |
| 227 | Create dataset card for HF | `data/dataset_card.md` exists |
| 228 | Verify all JSON result files have consistent schema | Same key structure |
| 229 | Check for NaN/null values in all result files | |
| 230 | Check for out-of-range scores (>5 or <1) | Data validation |
| 231 | Verify 3 repeats are identical (deterministic) | Expected for temp=0 |
| 232 | Document stop-token truncation for excluded models | |
| 233 | Create reproduction checklist | Step-by-step from clone to paper |
| 234 | Create platform-specific instructions | Kaggle vs Colab vs local |
| 235 | Add known-issues database | Documented limitations |
| 236 | Add cost tracking document | Exact $ spent per model |
| 237 | Add seed documentation | seed 42 everywhere |
| 238 | Add hash verification for data files | md5sum or sha256 |
| 239 | Create test data subset | 5 items for fast testing |

## H. WRITING QUALITY — AI VOICE & OVERCLAIM CLEANUP (25 items)

| # | Action | Description |
|---|--------|-------------|
| 240 | Scan for "furthermore" → remove or replace | |
| 241 | Scan for "moreover" → remove or replace | |
| 242 | Scan for "importantly" → remove or replace | |
| 243 | Scan for "notably" → remove or replace | |
| 244 | Scan for "paramount" → remove or replace | |
| 245 | Scan for "delve" → remove or replace | |
| 246 | Scan for "intriguing" → remove or replace | |
| 247 | Scan for "pivotal" → remove or replace | |
| 248 | Scan for "intricate" → remove or replace | |
| 249 | Scan for "leverage" → remove or replace | |
| 250 | Reduce em-dash overuse | Count and trim |
| 251 | Reduce "We find/show/present/propose" repetition | Vary sentence structure |
| 252 | Check for formulaic Python `print("="*60)` patterns | In analysis scripts |
| 253 | Check for overly structured output patterns | In scripts |
| 254 | Scan for "All families" → scope to actual N | |
| 255 | Scan for "First to" → "To our knowledge" | |
| 256 | Scan for "ruled out" → "tested" / "examined" | |
| 257 | Check percentages: 2 decimal places with N<10 → round | |
| 258 | Check "significant" with N<10 → report direction only | |
| 259 | Remove novelty claim from paragraph 5 → explicit paragraph | |
| 260 | Check "contributions" list for non-contributions | Fix item 4 |
| 261 | Check broader impact for boilerplate → specific | |
| 262 | Check conclusion: does it cite specific data? | Currently doesn't |
| 263 | Check for template-like abstract | Should read naturally |
| 264 | Verify paper reads like a human wrote it | Full pass |

## I. CROSS-FILE CONSISTENCY (18 items)

| # | Action | Description |
|---|--------|-------------|
| 265 | Verify model names match across: paper, JSON files, data files | Inconsistent: "Llama3.1-8B" vs "Llama-3.1-8B" |
| 266 | Normalize model names in `t4fam_results.json` | Check consistency |
| 267 | Normalize model names in `study1_results.json` | Check consistency |
| 268 | Normalize model names in `study1_max_scale.json` | Check consistency |
| 269 | Normalize in paper per-model table | |
| 270 | Normalize in model cards | |
| 271 | Verify every model in paper appears in at least one results file | |
| 272 | Verify every model in results has a model card | |
| 273 | Check `t4fam_results.json` vs `study1_results.json` overlap | Some models appear in both? |
| 274 | Create unified model registry | Single source of truth |
| 275 | Check paper model count (22) vs results file keys (20 in study1, 14 in t4fam) | Discrepancy |
| 276 | Add missing models to study1_results or document why excluded | |
| 277 | Cross-check "instruct-only" labels vs actual training method | Some may be base |
| 278 | Verify probe variant names match across files | "normal" vs "numeric" vs "no_ref" |
| 279 | Add `model_id` field to all result entries | HF model ID |
| 280 | Add `platform` field to all result entries | Kaggle/Colab/OpenRouter |
| 281 | Add `training_method` field to all result entries | |
| 282 | Add `model_size` field to all result entries | |

## J. SUPPLEMENTARY MATERIAL (25 items)

| # | Action | Description |
|---|--------|-------------|
| 283 | Create supplement: full per-model Δ table | All 36 variants |
| 284 | Create supplement: full per-probe breakdown | Variant-level means |
| 285 | Create supplement: item-level analysis | All 50 items |
| 286 | Create supplement: domain breakdown table | 5 domains |
| 287 | Create supplement: Bayesian posterior plots | |
| 288 | Create supplement: bootstrapped CI table | |
| 289 | Create supplement: outlier detection report | |
| 290 | Create supplement: leave-one-out sensitivity table | |
| 291 | Create supplement: cross-probe correlation matrix | |
| 292 | Create supplement: model ranking with CI | |
| 293 | Create supplement: training method comparison | |
| 304 | Create supplement: prompt templates | All templates used |
| 305 | Create supplement: item selection methodology | |
| 306 | Create supplement: excluded models documentation | |
| 307 | Create supplement: OpenRouter cost breakdown | |
| 308 | Create supplement: platform-specific reproduction | |
| 309 | Create supplement: software environment | |
| 310 | Create supplement: formal proofs | IIAR monotonicity theorem |
| 311 | Create supplement: Format Efficiency Hypothesis proof | |
| 312 | Create supplement: attention analysis methodology | |
| 313 | Create supplement: token classification schema | |
| 314 | Create supplement: hyperparameter details | |
| 315 | Convert supplementary to separate PDF | Standalone compilation |
| 316 | Add supplementary cross-references from main paper | |

## K. README & PROJECT DOCUMENTATION (12 items)

| # | Action | Description |
|---|--------|-------------|
| 317 | Rewrite README with graphical abstract | Current is functional only |
| 318 | Add visual badges to README | Python, DOI, license, tests |
| 319 | Add structured table to README | Key results in README |
| 320 | Add citation block to README | BibTeX format |
| 321 | Add quick-start section to README | Clone → install → run |
| 322 | Add project structure section to README | |
| 323 | Add "How to cite" section | |
| 324 | Add contribution guide | |
| 325 | Create `CONTRIBUTING.md` | |
| 326 | Create `CHANGELOG.md` | |
| 327 | Create `LICENSE` file | MIT or CC-BY |
| 328 | Create `CODE_OF_CONDUCT.md` | |

## L. FIGURE IMPROVEMENTS (existing HTML figures) (10 items)

| # | Action | Description |
|---|--------|-------------|
| 329 | Convert fig1_framework.html to PNG | arXiv compatibility |
| 330 | Convert fig2_bias_by_probe.html to PNG | |
| 331 | Convert fig3_pct_change.html to PNG | |
| 332 | Convert fig4_score_dist.html to PNG | |
| 333 | Convert fig5_bias_vs_size.html to PNG | |
| 334 | Convert fig6_domain.html to PNG | |
| 335 | Convert fig7_flip_rate_compare.html to PNG | |
| 336 | Convert fig8_mitigation.html to PNG | |
| 337 | Add proper alt text to all figures | Accessibility |
| 338 | Create combined figure PDF | All figures in one file |

## M. EXPERIMENTAL PIPELINE IMPROVEMENTS (13 items)

| # | Action | Description |
|---|--------|-------------|
| 339 | Refactor scoring_pipeline.py | Remove dead code |
| 340 | Add logging to all scripts | Replace `print()` with `logging` |
| 341 | Add argparse CLI to all pipeline scripts | Standard interfaces |
| 342 | Add progress bars to long operations | tqdm |
| 343 | Add checkpoint/restore to pipeline | Resume interrupted runs |
| 344 | Add error handling with retry | For OpenRouter flakiness |
| 345 | Add batch API calling | Rate limiting |
| 346 | Add cost budgeting to pipeline | Stop at $ threshold |
| 347 | Add model ID verification at startup | Check HF/OR IDs exist |
| 348 | Add schema validation on output | Auto-check result format |
| 349 | Add platform auto-detection | Kaggle vs Colab paths |
| 350 | Create unified config.yaml | Single source for paths, keys |
| 351 | Create experiment launcher | CLI that runs everything |

## N. EXISTING ANALYSIS — EXECUTE CPU-RUNNABLE SCRIPTS (12 items)

| # | Action | Script path | Expected output |
|---|--------|-------------|-----------------|
| 352 | Run `cross_probe_analysis.py` | `results_rootcause/` | Verify output matches existing JSON |
| 353 | Run `variance_decomposition.py` | `results_rootcause/` | Regenerate decomposition |
| 354 | Run `model_ranking_analysis.py` | `results_rootcause/` | Regenerate rankings |
| 355 | Run `item_analysis_framework.py` | `results_rootcause/` | Item metrics |
| 356 | Run `depth_analysis.py` | `results_rootcause/` | Depth metrics |
| 357 | Run `depth_findings.py` | `results_rootcause/` | Depth findings |
| 358 | Run `domain_analysis.py` | `results_rootcause/` | By-domain bias |
| 359 | Run `comprehensive_analysis.py` | `results_rootcause/` | Full analysis |
| 360 | Run `quick_analysis.py` | `results_rootcause/` | Quick metrics |
| 361 | Run `final_summary.py` | `results_rootcause/` | Summary table |
| 362 | Run `generate_publication_figures.py` | `pipeline_biasinteraction/` | Publication figures |
| 363 | Run `generate_figures.py` | `pipeline_biasinteraction/` | Standard figures |

## O. KNOWN ISSUES DATABASE (5 items)

| # | Action | Description |
|---|--------|-------------|
| 364 | Create KNOWN_ISSUES.md | Documented limitations |
| 365 | Add 4-bit loading issue | config=config blocks load_in_4bit |
| 366 | Add StableLM pad_token_id workaround | |
| 367 | Add stop-token truncation issue | 5 excluded OpenRouter models |
| 368 | Add descriptive parser issue | 1/9 comparisons affected |

## P. ISEF COMPETITION MATERIALS (12 items)

| # | Action | Description |
|---|--------|-------------|
| 369 | Create ISEF abstract | 250-word limit |
| 370 | Create ISEF project summary | 1-page overview |
| 371 | Create ISEF research paper | Competition format |
| 372 | Create ISEF bibliography | Competition-format citations |
| 373 | Create ISEF presentation slides | Google Slides or PDF |
| 374 | Create ISEF poster template | 36×48 inch |
| 375 | Create ISEF safety form | Pre-filled |
| 376 | Create research plan | ISEF format |
| 377 | Create approval letters | Template |
| 378 | Create data collection timeline | |
| 379 | Create ISEF checklist | All requirements |
| 380 | Create competition prep timeline | |

## Q. LITERATURE REVIEW ENHANCEMENTS (8 items)

| # | Action | Description |
|---|--------|-------------|
| 381 | Search for 2025-2026 scoring bias papers | Added since last search |
| 382 | Search for instruction-tuning alignment papers | |
| 383 | Search for RLHF bias papers | |
| 384 | Create comprehensive literature table | 35+ bias types cataloged |
| 385 | Add citation count data | Signal of influential papers |
| 386 | Add venue tier information | CORE ranking |
| 387 | Add missing references to related-work table | |
| 388 | Create literature review supplementary doc | |

## R. TITLE-AMBLITION CHECK (8 items)

| # | Action | Description |
|---|--------|-------------|
| 389 | Check title: "A 22-Model Landscape with Base-Instruct Comparison" | Title says 22, data has 36 variants |
| 390 | Check if "Where does scoring bias come from?" framing fits | Title is a statement, not question |
| 391 | Check abstract matches title | Both say 22 models |
| 392 | Check claims match N | "All families" vs actual N |
| 393 | Check "differential effect" claim | Supported in 9/10 families for format, but content scale-dependent |
| 394 | Check "first systematic investigation" claim | Accurate? Any prior? |
| 395 | Check "largest open comparison" claim | Verify against known literature |
| 396 | Suggest alternative titles if mismatch found | |

## S. LaTeX COMPILATION & FORMATTING (20 items)

| # | Action | Description |
|---|--------|-------------|
| 397 | Check for `\cite` without matching bib key | Cross-reference |
| 398 | Check for `\ref` without matching `\label` | |
| 399 | Check for `\verb` inside fragile environments | quote, section, caption |
| 400 | Check for doubled `\\\\` from Windows patching | |
| 401 | Check for proper `\input` paths | All .tex files |
| 402 | Check for proper `\includegraphics` paths | Once figures added |
| 403 | Check PDF figure existence | |
| 404 | Check `\bibliographystyle{unsrt}` is appropriate | |
| 405 | Check `\usepackage` for all commands used | |
| 406 | Check `\textwidth` vs `\columnwidth` in figure sizing | |
| 407 | Add `\usepackage[backend=biber]{biblatex}` alternative | |
| 408 | Add `\printbibliography` format | |
| 409 | Check for unescaped special chars in text | %, #, &, _, $ |
| 410 | Check table column alignment | l, c, r appropriate? |
| 411 | Check table width | No overflow |
| 412 | Add `\toprule`/`\midrule`/`\bottomrule` consistency | booktabs |
| 413 | Check for missing `\label` after `\caption` | |
| 414 | Check for `\paragraph` vs `\subsubsection` appropriate | |
| 415 | Check for proper math mode delimiters | \(...\) vs $...$ |
| 416 | Create compilation test script | `python -c "test_compile"` |

## T. BAYESIAN ANALYSIS (CPU) — EXECUTE (8 items)

| # | Action | What I'll produce |
|---|--------|-------------------|
| 417 | Run conjugate Bayesian for all 10 families | Posterior per probe |
| 418 | Compute HDI for all 10 families | 95% credible intervals |
| 419 | Compute P(effect < 0) for all probes | Probability content bias decreased |
| 420 | Compute Bayes factors for all 3 probes | |
| 421 | Create Bayesian results JSON | Structured for paper |
| 422 | Create Bayesian summary table | For paper inclusion |
| 423 | Create Bayesian posterior figure | For paper |
| 424 | Write Bayesian methods section | Ready-to-insert LaTeX |

## U. ATTENTION ANALYSIS EXTENSION (CPU) (6 items)

| # | Action | Description |
|---|--------|-------------|
| 425 | Run attention analysis on CPU for Qwen2.5-0.5B | Already have data? Check |
| 426 | Re-run attention classification with improved schema | |
| 427 | Compute token-level attention distributions | |
| 428 | Analyze cross-head attention patterns | |
| 429 | Create attention visualizations | |
| 430 | Write attention methodology section | |

## V. PROMPT ABLATION (CPU) (6 items)

| # | Action | Description |
|---|--------|-------------|
| 431 | Run prompt_ablation.py on CPU  | Tests 5 templates × 2 models |
| 432 | Compute ablation effect sizes | |
| 433 | Create ablation comparison table | |
| 434 | Create ablation figure | |
| 435 | Write ablation results section | |
| 436 | Add ablation to limitations | |

## W. BIBLIOGRAPHY — AUTO-FORMAT (5 items)

| # | Action | Description |
|---|--------|-------------|
| 437 | Convert all entries to standard BibLaTeX | |
| 438 | Add DOI URL for every paper | |
| 439 | Add arXiv ID for every arXiv paper | |
| 440 | Check for missing author names | "and others" vs full names |
| 441 | Create sorted bibliography | Alphabetical |

## X. PROJECT CLEANUP (24 items)

| # | Action | Description |
|---|--------|-------------|
| 442 | Remove dead .tex files | Many draft papers polluting repo |
| 443 | Archive old experiments | experiment_tracking/ from root |
| 444 | Move synthetic data to data/ | Bias interaction CSV |
| 445 | Remove duplicate .tex files | |
| 446 | Consolidate redundant analysis scripts | |
| 447 | Add .gitignore for LaTeX artifacts | .aux, .log, .out, .pdf |
| 448 | Add .gitignore for Python artifacts | __pycache__, .pyc |
| 449 | Add .gitignore for IDE files | .vscode, .idea |
| 450 | Add .gitignore for OS files | .DS_Store, Thumbs.db |
| 451 | Clean __pycache__ directories | |
| 452 | Remove large synthetic data if not needed | bias_interaction_synthetic.csv |
| 453 | Add data size tracking | |
| 454 | Check for committed credentials | API keys in any file |
| 455 | Check for committed tokens | HF_TOKEN, OpenRouter keys |
| 456 | Verify all result JSONs are valid | Parse all |
| 457 | Check for encoding issues | UTF-8 vs ASCII |
| 458 | Normalize line endings | LF only (Unix) |
| 459 | Add file header comments to all .py files | |
| 460 | Add encoding headers to all .py files | |
| 461 | Standardize function naming | snake_case consistency |
| 462 | Standardize variable naming | |
| 463 | Remove unused imports | |
| 464 | Remove debug print statements | |
| 465 | Create `clean.sh` / `clean.ps1` | Clean build artifacts |

## Y. WEB INTERACTIVE SUPPLEMENTS (10 items)

| # | Action | Description |
|---|--------|-------------|
| 466 | Create interactive bias explorer | HTML with D3.js |
| 467 | Create interactive per-model dashboard | |
| 468 | Create interactive figure HTML | Supplement existing static figures |
| 469 | Add tooltip annotations to figures | |
| 470 | Create comparison tool | Side-by-side model comparison |
| 471 | Create interactive tables | Sortable, filterable |
| 472 | Create figure toggle | Show/hide model series |
| 473 | Add responsive design | Mobile-friendly |
| 474 | Create figure export | SVG/PNG download buttons |
| 475 | Package interactive supplements | Single HTML file |

## Z. WHAT I NEED FROM YOU **[NEED USER]** (25 items)

These require your authentication, API keys, or GPU access. I tell you exactly what to run.

| # | Action | Why I can't do it | What you run |
|---|--------|-------------------|--------------|
| 476 | Upload to arXiv | Needs your account | `paper/arxiv_submission/submit.sh` |
| 477 | Upload to HuggingFace Dataset | Needs your HF_TOKEN | `python pipeline_biasinteraction/upload_to_hub.py` |
| 478 | Run Llama-3.1-8B + Mistral-7B on GPU | CPU-only env | `python pipeline_rootcause/replicate_t4_families.py` on Kaggle T4 |
| 479 | Run 7B+ models on Colab A100 | Needs GPU | Colab notebook from `notebooks/` |
| 480 | Run OpenRouter for 5 fixed models | Needs API key | `pipeline_biasinteraction/scoring_pipeline.py --models gemini-2.5-pro,...` |
| 481 | Human baseline (3 friends × 50 items) | Needs human subjects | Print `data/human_baseline_sheet.md` |
| 482 | Pre-register on OSF | Needs your account | osf.io preregistration form |
| 483 | Create Zenodo release | Needs your GitHub integration | zenodo.org hook |
| 484 | Submit to ACL SRW | Needs your submission | ACL SRW deadline Feb |
| 485 | Create Twitter/X thread | Needs your account | 8-tweet thread with figures |
| 486 | Create LinkedIn article | Needs your account | |
| 487 | Create Reddit r/MachineLearning post | Needs your account | |
| 488 | Create Hacker News post | Needs your account | |
| 489 | Set up GitHub Pages site | Needs repo settings | |
| 490 | Create YouTube video abstract | Needs recording | |
| 491 | Apply for NeurIPS HS Track | Needs your application | |
| 492 | Request API keys for excluded models | Needs your accounts | Gemini, Inflection, etc. |
| 493 | Review the 500-item output for accuracy | Final human check | Spot-check 10-20 items |
| 494 | Confirm title/abstract scope | Strategic decision | Choose framing level |
| 495 | Decide on venue strategy | Strategic decision | ACL SRW vs NeurIPS HS |
| 496 | Answer 3 clarification questions | Ambiguity resolution | See end of document |
| 497 | Review and approve figures | Aesthetic judgment | Pick preferred style |
| 498 | Review and approve paper text changes | Content judgment | Accept/reject edits |
| 499 | Create GitHub release | Needs your permissions | |
| 500 | Merge final PR | Final sign-off | |

---

## Execution Plan

**Batch 1 — Immediate (sections A-I, ~50 edits)**
Fix all data mismatches (items 1-32), normalize terminology (265-282), add Bayesian results (33-35), run CPU analyses (126-163), generate figures (81-125).

**Batch 2 — Infrastructure (sections E, G, X)**
Create CI/CD (164-194), lint code (196-200), clean project (442-465).

**Batch 3 — Polish (sections H, R, S, F)**
AI voice cleanup (240-264), title check (389-396), LaTeX fixes (397-416), references (202-214).

**Batch 4 — Supplementary (sections J, L, Y)**
Create supplement (283-316), convert HTML→PNG (329-338), interactive tools (466-475).

**Batch 5 — ISEF & Competition (section P)**
Create competition materials (369-380).

**Batch 6 — Need User (section Z)**
After all auto-work is done, hand off the 25 items requiring you.

---

## 3 Questions I Need Answered

1. **Title scope**: Current title says "22-Model Landscape" but data has 36 variants. Do you want to (a) update title to reflect 36 variants, (b) keep "22" by only counting unique model names, or (c) remove the number from the title?

2. **Figure format preference**: (a) matplotlib/seaborn PNGs (publication standard), (b) plotly interactive HTML, or (c) both? I default to seaborn.

3. **arXiv vs venue first**: Do you want to submit to arXiv now (establish priority) and iterate for venue, or wait until the venue-ready version is complete?
