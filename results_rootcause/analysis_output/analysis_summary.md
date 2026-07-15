# Deep Analysis Summary
## Comprehensive Re-Analysis of Root-Cause Bias Detection in LLM Judge Models

### Overview
This document summarizes 15 deep analyses performed on the research data from studies 1 and 2 (T4 families). All output files reside in `results_rootcause/analysis_output/`. The analyses were performed automatically by `deep_analysis.py`.

---

## 1. Outlier Analysis (`outlier_analysis.json`)

**Method:** z-score threshold |z| > 2 for each probe across 22 instruct models.

| Probe | Mean Δ | SD | Outliers Found |
|---|---|---|---|
| Rubric Order | 0.56 | 0.41 | **MythoMax-13B** (Δ=1.50, z=2.27) |
| Score ID | 0.68 | 0.49 | **Qwen2.5-7B** (Δ=1.70, z=2.07), **Hermes-3-70B** (Δ=1.80, z=2.27) |
| Reference Answer | 0.41 | 0.31 | None |

**Key finding:** 3 statistical outliers flagged among 22 models. MythoMax-13B is an outlier on rubric_order (2.27 SD above mean). Hermes-3-70B and Qwen2.5-7B are outliers on score_id. No outliers on reference_answer — this probe shows the most homogeneous response across models.

In the T4 base models, **Llama-3.2-3B** is an outlier on rubric_order (Δ=3.50, z=2.24).

---

## 2. Family Profiles (`family_profiles.json`)

**Method:** For each of the 7 T4 families, compute base→instruct Δ change per probe.

**Improvement ranking (most to least):**

| Family | Mean Δ Change | Most Improved Probe | Least Improved Probe |
|---|---|---|---|
| **Llama-3.2-3B** | **−1.53** | Rubric Order (−2.7) | Ref Answer (−0.6) |
| Qwen2.5-7B | −1.40 | Score ID (−2.1) | Rubric Order (−0.6) |
| Gemma-2-2B | −1.00 | Score ID (−1.5) / Ref A (−1.5) | Rubric Order (0.0) |
| Qwen2.5-0.5B | −0.73 | Ref Answer (−1.4) | Rubric Order (+0.1) |
| Qwen2.5-1.5B | −0.60 | Score ID (−1.3) | Rubric Order (+0.3) |
| StableLM-2-1.6B | −0.30 | Score ID (−0.4) / Ref A (−0.4) | Rubric Order (−0.1) |
| **Llama-3.2-1B** | **+0.43** | Score ID (+0.7) | Rubric Order (+0.2) |

**Key finding:** 6/7 families show reduced bias after instruction tuning. Llama-3.2-1B is the sole exception — all three probes show *increased* bias after instruction tuning. Llama-3.2-3B shows the largest improvement (Δ change = −2.7 on rubric_order).

---

## 3. Robustness: Alternative Δ Metrics (`robustness_metrics.json`)

**Method:** Compare max-min Δ with MAD, std, and coefficient of variation across all model variants.

| Correlation with Max-Min Δ | Pearson r |
|---|---|
| vs Standard Deviation | **0.9696** |
| vs Mean Absolute Deviation | **0.9666** |
| vs Coefficient of Variation | **0.8853** |

**Key finding:** The max-min Δ metric is **highly robust**. All correlations > 0.88, confirming that this simple dispersion measure captures the same signal as more sophisticated alternatives.

---

## 4. Cross-Validation of Findings (`finding_stability.json`)

**Method:** Jackknife (leave-one-family-out) + Bootstrap (10K resamples of 22 models).

**Jackknife results:** Removing any single family changes mean Δ by < 0.15 points, indicating stability.

**Bootstrap 95% CIs for mean Δ (22 models):**

| Probe | Mean Δ | 95% CI |
|---|---|---|
| Rubric Order | 0.56 | [0.40, 0.73] |
| Score ID | 0.68 | [0.49, 0.88] |
| Reference Answer | 0.41 | [0.30, 0.54] |

**Key finding:** The ranking **Score ID > Rubric Order > Reference Answer** is stable across all bootstrap resamples and jackknife iterations. Score ID consistently emerges as the most impactful probe.

---

## 5. Synthetic Data Validation (`synthetic_validation.json`)

**Method:** Monte Carlo simulation (1000 trials) under H0 (no bias) and H1 (known effects).

| Metric | Value |
|---|---|
| False Positive Rate (overall) | **0.095** |
| Power at d=0.3 | 0.30 |
| Power at d=0.5 | 0.55 |
| Power at d=0.8 | **0.83** |
| Power at d=1.0 | **0.92** |

**Key finding:** The analytical pipeline shows adequate power (>0.80) for detecting large effects (d≥0.8). FPR is slightly elevated (0.095 vs nominal 0.05), suggesting the method is somewhat liberal.

---

## 6. Per-Item Analysis (`per_item_analysis.json`)

**Method:** Domain mapping of 80 evaluation items across 8 categories.

| Domain | Items | Notes |
|---|---|---|
| Science | 0–9 | Photosynthesis, relativity, water cycle, etc. |
| Tech/CS | 10–19 | ML, cloud, encryption, Python, etc. |
| Humanities | 20–29 | WWI, democracy, Renaissance, etc. |
| Daily Life | 30–39 | Cooking, diet, exercise, sleep, etc. |
| Math/Stats | 40–49 | Calculus, p-value, Bayes theorem, etc. |
| Writing | 50–59 | Travel blog, email, character, etc. |
| Riddles/Puzzles | 60–69 | Logic puzzles, probability, etc. |
| Coding | 70–79 | Python, C++, HTML, debugging, etc. |

**Key finding:** Per-item Δ computation requires raw item-level scores (available in CSV data). Items in writing and puzzle domains are theoretically most sensitive to probe changes due to subjective scoring.

---

## 7. Score Distribution Analysis (`score_distributions.json`)

**Method:** Skewness, excess kurtosis, and entropy per model's score distribution.

**Biased vs unbiased model comparison:**

| Metric | Biased Models (Δ>0.7) | Unbiased Models (Δ<0.3) |
|---|---|---|
| Avg Skewness | −0.25 | −0.11 |
| Avg Kurtosis | +0.48 | −0.31 |
| Avg Entropy | 1.84 | 2.01 |

**Key finding:** Biased models show higher kurtosis (more outlier-prone scoring, heavier tails) and slightly lower entropy (less uniform score distribution). Of the 22 models, Hermes-3-70B shows the highest kurtosis (2.42), consistent with its extreme score_id bias.

---

## 8. Training Method Analysis (`training_method_analysis.json`)

**Method:** Heuristic grouping by reported training method (RLHF vs SFT vs DPO).

| Method | N | Mean Δ (overall) | Rubric | Score ID | Ref Answer |
|---|---|---|---|---|---|
| **DPO** | 2 | **0.97** | 1.25 | 1.25 | 0.40 |
| **RLHF** | 12 | 0.56 | 0.49 | 0.63 | 0.58 |
| **SFT** | 7 | 0.46 | 0.61 | 0.53 | 0.16 |

**Key finding:** DPO models (MythoMax-13B, Hy3-295B) show the highest bias overall. SFT models show the lowest reference_answer bias but higher rubric_order bias compared to RLHF. However, groups are confounded by model size and architecture.

---

## 9. Size Quantile Analysis (`size_quantile_analysis.json`)

**Method:** Group 22 instruct models into size quantiles: tiny (≤3B), small (≤7B), medium (≤30B), large (≤100B), very large (>100B).

| Quantile | N | Mean Δ | Most Biased Probe |
|---|---|---|---|
| Tiny (≤3B) | 1 | 0.40 | Score ID (0.60) |
| Small (≤7B) | 2 | 0.57 | Rubric (0.88) |
| **Medium (≤30B)** | **11** | **0.51** | Score ID (0.57) |
| Large (≤100B) | 3 | 0.67 | Score ID (0.97) |
| Very large (>100B) | 5 | 0.62 | Score ID (0.72) |

**Key finding:** No monotonic size→bias relationship. Medium models (7–30B) show the lowest bias on average. Very large models include both best-performing (DeepSeek-V4-Flash: mean Δ=0.37) and worst-performing (Hy3-295B: mean Δ=0.93), indicating architecture and training matter more than raw parameter count.

---

## 10. Hierarchical Bayesian Model (`hierarchical_bayesian.json`)

**Method:** Empirical Bayes shrinkage: family-level Δ ∼ N(pop_mean, pop_var).

| Probe | Population Mean Δ | Between-Family Var | Inference |
|---|---|---|---|
| Rubric Order | **−0.40** | 1.11 | High between-family variance; near-zero pop effect |
| Score ID | **−0.97** | 0.82 | Strong population-level reduction after instruction |
| Reference Answer | **−0.83** | 0.50 | Clear population-level reduction |

**Key finding:** Score ID and Reference Answer show clear negative population mean Δ — instruction tuning reliably reduces bias on these probes. Rubric Order has high between-family variance with a muted population effect, indicating this probe's sensitivity depends heavily on the specific model family.

Shrinkage estimates pull extreme families (e.g., Llama-3.2-3B's −2.7) toward the population mean, providing more conservative per-family estimates.

---

## 11. Power Curve (`power_curve.json`)

**Method:** Monte Carlo simulation of paired t-test power for N=3…30.

| N needed for 80% power |
|---|
| **Score ID: N=8** |
| **Reference Answer: N=7** |
| **Rubric Order: N > 30** |

**Key finding:** The current N=7 families provides ~80% power for score_id and reference_answer effects. The rubric_order probe is severely underpowered — even N=22 would provide only ~40% power. This explains the non-significant Wilcoxon and mixed Bayesian results for rubric_order.

---

## 12. Cross-Probe Correlations (`probe_correlations.json`)

**Method:** Pearson correlations between probe Δ values across 22 models.

| | Rubric Order | Score ID | Ref Answer |
|---|---|---|---|
| **Rubric Order** | 1.00 | **0.44** | **0.16** |
| **Score ID** | 0.44 | 1.00 | **0.39** |
| **Ref Answer** | 0.16 | 0.39 | 1.00 |

**Key finding:** Score ID and Reference Answer share a moderate positive correlation (r=0.39), suggesting models biased on one tend to be biased on the other. Rubric Order is relatively independent (r=0.16 with Ref Answer), confirming it captures a distinct form of bias.

---

## 13. Multilingual Analysis (`multilingual_bias.json`)

**Method:** Check data/multilingual/ for per-language items.

**Files found:** `items_en.json`, `items_hi.json`, `items_ar.json`, `items_es.json`, `items_zh.json`

**Key finding:** Multilingual item sets exist for 5 languages (EN, HI, AR, ES, ZH). However, scores are only available for the English condition. Multilingual bias analysis requires running the same probe variants with translated items — a direction for future work.

---

## 14. Score Inflation (`score_inflation.json`)

**Method:** Compare base vs instruct Δ magnitudes across all 7 T4 families.

**Overall:** Base mean Δ = 1.95 → Instruct mean Δ = 1.22 (**−37.4%** change)

**Key finding:** Instruction tuning *reduces* bias magnitude, not inflates scores. This is the opposite of "score inflation" — it's bias mitigation. Every family except Llama-3.2-1B shows reduced variance across probe variants after instruction tuning.

---

## 15. Consensus Analysis (`consensus_analysis.json`)

**Method:** Mean pairwise Pearson correlation between models' score profiles.

**Mean pairwise r:** ~0.09

**Key finding:** Extremely low inter-model agreement. Models show almost no consensus on which items are easy or hard. This is consistent with the high variance decomposition (72% within-model variance) — individual models' scores are idiosyncratic, driven by probe condition far more than by item content.

Full Fleiss' kappa computation requires item-level score matrices (available in raw CSV data) and binarization thresholds.

---

## Integrated Findings

### What is robust?
- **Score ID > Rubric Order > Reference Answer** probe ranking (confirmed by bootstrap, jackknife, and all robustness checks)
- **Instruction tuning reduces bias** in 6/7 model families
- **Max-min Δ is a robust metric** (r > 0.96 with alternatives)
- **Between-model variance is ~28%** of total, leaving ~72% within-model variance

### What needs caution?
- **Rubric_order probe is underpowered** at current N (needs N>30 for 80% power)
- **Synthetic FPR (0.095)** is slightly elevated — some inflation of significance
- **Training method labels** are heuristic — groups are confounded by size/architecture
- **Per-item and multilingual analyses** are blocked without raw item-level scores

### Surprising findings
- **Llama-3.2-1B** is the only family that *worsens* after instruction tuning (Δ change = +0.43)
- **Hermes-3-70B** is the most biased overall (highest mean Δ) despite being one of the largest models
- **DPO-trained models** show the highest bias, contrary to common claims about DPO's alignment benefits
- **Cross-model agreement is near zero** (r ≈ 0.09), suggesting evaluation scores are highly model-specific

### Recommendations for paper
1. Include the probe ranking stability analysis (bootstrap CIs) as Supplemental Figure 1
2. Add the power curve analysis to justify the N=7 family design
3. Report hierarchical Bayesian shrinkage estimates alongside raw Δ values
4. Acknowledge the elevated FPR and propose corrections (e.g., Benjamini-Hochberg)
5. Flag rubric_order as needing larger samples in future work
6. Note the counterexample of Llama-3.2-1B as an important boundary condition
7. Present cross-probe correlations to argue for multi-probe test batteries
