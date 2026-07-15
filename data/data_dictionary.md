# Data Dictionary  Scoring Bias in LLM-as-a-Judge

This document documents every field across all data files in the repository. Each JSON file is
covered with its structure, field types, ranges, and examples.

---

## 1. `data/dataset.json`  Unified Dataset

### Top-Level Structure

| Field | Type | Description |
|-------|------|-------------|
| `metadata` | object | Dataset-level metadata (version, totals, citation) |
| `models` | object | Model metadata registry |
| `scores` | object | Per-model per-probe per-variant mean scores |
| `bias_metrics` | object | Computed bias metrics (deltas, flip rates, effect sizes) |
| `statistical_analysis` | object | Wilcoxon, Bayesian, bootstrap, power, variance results |
| `items` | object | Evaluation item descriptions |
| `base_instruct_comparison` | object | Per-family base→instruct delta changes |
| `probe_correlations` | object | Pearson cross-probe correlation matrix |

### `metadata` Fields

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `dataset_name` | string | `"Scoring Bias in LLM-as-a-Judge  Unified Dataset"` | Full dataset name |
| `version` | string | `"1.0.0"` | Dataset version (semver) |
| `description` | string | `"Complete experimental dataset..."` | Full description |
| `total_judgments` | int | `40500` | Total number of LLM judgments |
| `total_models` | int | `31` | Total model variants |
| `model_variants.base` | int | `9` | Number of base (pre-trained) models |
| `model_variants.instruct` | int | `22` | Number of instruct (fine-tuned) models |
| `base_instruct_paired_families` | int | `11` | Families with both variants |
| `probe_types` | string[] | `["rubric_order", ...]` | Three probes used |
| `probe_variants_per_type` | int | `3` | Conditions per probe |
| `score_scale` | string | `"1-5 (integer)"` | Score range |
| `items` | int | `80` | Total evaluation items |
| `domains` | string[] | `["science", ...]` | Content domains |
| `repeats_per_condition` | int | `3` | Deterministic repeats |
| `decoding` | string | `"greedy (temperature=0)"` | Decoding strategy |
| `total_api_cost_usd` | float | `3.0` | Total API cost |
| `inference_platforms` | string[] | `["Kaggle T4 GPU", ...]` | Platforms used |
| `citation` | string | `"Samba, S. (2026)..."` | Preferred citation |

### `models.metadata.fields`

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `name` | string | `"Qwen2.5-0.5B"` | Model identifier |
| `family` | string | `"Qwen2.5"` | Model family/architecture |
| `size` | string | `"0.5B"` | Parameter count (B = billions) |
| `is_base` | bool | `true` | `true` = pre-trained only; `false` = instruction-tuned |
| `training_method` | string | `"SFT"` | Alignment method: `base`, `SFT`, `RLHF`, `DPO`, `unknown` |
| `access` | string | `"kaggle_t4"` | Platform: `kaggle_t4`, `openrouter_api`, `local_cpu` |
| `excluded` | bool | `false` | `true` if model was excluded (stop-token truncation) |
| `notes` | string | `"T4 GPU inference..."` | Free-text notes |

### `models.entries.*`

One entry per model variant (31 total + 5 excluded). See `models.metadata.fields` for field
descriptions. Excluded models have `"excluded": true`.

### `scores.models.*`

Each model entry has per-probe scores. Structure:

```json
{
  "ModelName": {
    "rubric_order": {
      "normal": 3.5,     // mean score across items [1.0, 5.0]
      "reversed": 3.4,   // mean score across items [1.0, 5.0]
      "random": 3.0      // mean score across items [1.0, 5.0] (if available)
    },
    "score_id": {
      "numeric": 3.5,    // mean score [1.0, 5.0]
      "letter": 2.2,     // mean score (A=5, B=4, C=3, D=2, E=1 mapped)
      "descriptive": 3.0 // mean score (labels mapped to 1-5)
    },
    "reference_answer": {
      "no_ref": 3.5,     // control condition [1.0, 5.0]
      "good_ref": 4.2,   // good exemplar [1.0, 5.0]
      "poor_ref": 1.6    // poor exemplar [1.0, 5.0]
    }
  }
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `rubric_order.normal` | float | [1.0, 5.0] | Standard rubric (1=worst, 5=best) |
| `rubric_order.reversed` | float | [1.0, 5.0] | Reversed rubric (1=best, 5=worst) |
| `rubric_order.random` | float | [1.0, 5.0] | Random label mapping |
| `score_id.numeric` | float | [1.0, 5.0] | Numeric labels 1-5 |
| `score_id.letter` | float | [1.0, 5.0] | Letter grades A-E (converted) |
| `score_id.descriptive` | float | [1.0, 5.0] | Descriptive labels (converted) |
| `reference_answer.no_ref` | float | [1.0, 5.0] | No exemplar |
| `reference_answer.good_ref` | float | [1.0, 5.0] | Good exemplar shown |
| `reference_answer.poor_ref` | float | [1.0, 5.0] | Poor exemplar shown |

### `bias_metrics.metrics_definitions`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `max_delta` | float | [0.0, 4.0] | Max inter-variant mean difference |
| `flip_rate` | float | [0.0, 1.0] | Proportion of items where score differs from control |
| `cohens_d` | float | (-∞, ∞) | (biased_mean - control_mean) / pooled_std |
| `mean_abs_bias` | float | [0.0, 4.0] | Mean absolute deviation across all variants |

### `bias_metrics.training_method_analysis`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `n_models` | int | 2-12 | Models in this training method group |
| `rubric_order_mean` | float | [0.0, 4.0] | Mean rubric order delta for this group |
| `score_id_mean` | float | [0.0, 4.0] | Mean score ID delta |
| `reference_answer_mean` | float | [0.0, 4.0] | Mean reference answer delta |
| `overall_mean` | float | [0.0, 4.0] | Mean across all three probes |

### `statistical_analysis.wilcoxon_signed_rank`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `mean_change` | float | (-4.0, 4.0) | Mean of (instruct_delta − base_delta) across families |
| `p_value` | float | [0.0, 1.0] | Two-sided Wilcoxon p-value |
| `significant` | bool | true/false | p < 0.05 |
| `effect_size_r` | float | [0.0, 1.0] | Wilcoxon effect size (r = Z/√N) |

### `statistical_analysis.bayesian`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `posterior_mean` | float | (-∞, ∞) | Posterior mean of delta |
| `bf10_vs_null` | float | [0, ∞) | Bayes factor for H1 vs H0. >3=moderate, >10=strong, >100=decisive |
| `p_positive` | float | [0.0, 1.0] | Posterior probability that true delta > 0 |

### `statistical_analysis.bootstrapped_cis`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `mean` | float | [0.0, 5.0] | Bootstrap mean estimate |
| `ci_95` | float[] | [lower, upper] | 95% bias-corrected accelerated bootstrap CI |

### `base_instruct_comparison.summary`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `mean_change` | float | (-4.0, 4.0) | Mean delta change across 7 families |
| `n_decrease` | int | [0, 7] | Families where bias decreased |
| `n_increase` | int | [0, 7] | Families where bias increased |

### `probe_correlations`

Each field is a Pearson r value:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `rubric_order.rubric_order` | float | 1.0 | Self-correlation (identity) |
| `rubric_order.score_id` | float | [-1.0, 1.0] | Correlation between rubric and score ID across 22 models |
| `rubric_order.reference_answer` | float | [-1.0, 1.0] | Correlation between rubric and ref answer across 22 models |
| `score_id.*` | float | [-1.0, 1.0] | As above |
| `reference_answer.*` | float | [-1.0, 1.0] | As above |

---

## 2. `results_rootcause/study1_results.json`  Study 1 (Instruct-Only Models)

22 models × 3 probes × up to 3 conditions each. Structure identical to `scores.models.*` above.

### Key Fields

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `{model_name}` | object | `"Llama3.1-8B"` | Model identifier |
| `{model_name}.rubric_order.{variant}` | float | `3.6` | Mean score under rubric order variant |
| `{model_name}.score_id.{variant}` | float | `3.7` | Mean score under score ID variant |
| `{model_name}.reference_answer.{variant}` | float | `3.6` | Mean score under reference answer variant |

Note: T4 models have only 2 rubric_order conditions (normal, reversed) while the
24,300-judgment Kaggle root cause study all conditions.

---

## 3. `results_rootcause/t4fam_results.json`  T4 Families (Base + Instruct)

14 models (7 families × 2 variants) with per-probe scores. Same structure as study1_results.json.

---

## 4. `results_rootcause/analysis_output/t4fam_deltas.json`  Per-Model Deltas

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `{model_name}.rubric_order` | float | [0.0, 4.0] | Max delta for rubric order |
| `{model_name}.score_id` | float | [0.0, 4.0] | Max delta for score ID |
| `{model_name}.reference_answer` | float | [0.0, 4.0] | Max delta for reference answer |

For families with base+instruct, both names appear (e.g., `Qwen2.5-0.5B` and `Qwen2.5-0.5B-IT`).

---

## 5. `results_rootcause/analysis_output/model_ranking.json`  Model Rankings

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `by_mean_delta[].rank` | int | [1, 22] | Rank (1 = least biased) |
| `by_mean_delta[].model` | string | model name | Model identifier |
| `by_mean_delta[].mean_delta` | float | [0.0, 4.0] | Mean delta across 3 probes |
| `by_mean_delta[].rubric_order_delta` | float | [0.0, 4.0] | Per-probe rubric delta |
| `by_mean_delta[].score_id_delta` | float | [0.0, 4.0] | Per-probe score ID delta |
| `by_mean_delta[].reference_answer_delta` | float | [0.0, 4.0] | Per-probe reference answer delta |
| `kendalls_w.W` | float | [0.0, 1.0] | Kendall's W coefficient of concordance |
| `kendalls_w.chi_square` | float | [0, ∞) | Chi-square statistic |
| `kendalls_w.df` | int | `21` | Degrees of freedom |
| `kendalls_w.p_value` | float | [0.0, 1.0] | P-value for Kendall's W test |
| `kendalls_w.interpretation` | string | `"Moderate agreement"` | Text interpretation |

---

## 6. `results_rootcause/analysis_output/bootstrapped_cis.json`  Bootstrap CIs

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `{group}.{probe}.mean` | float | [0.0, 5.0] | Bootstrap mean |
| `{group}.{probe}.std` | float | [0.0, ∞) | Bootstrap standard deviation |
| `{group}.{probe}.ci_95_lower` | float | [0.0, 5.0] | 95% CI lower bound |
| `{group}.{probe}.ci_95_upper` | float | [0.0, 5.0] | 95% CI upper bound |
| `{group}.{probe}.n` | int | [7, 22] | Sample size |

Groups: `t4fam_base`, `t4fam_instruct`, `study1_22`.

---

## 7. `results_rootcause/analysis_output/bayesian_results.json`  Bayesian Analysis

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `metadata` | object |  | Prior specification |
| `data.format_delta_changes` | float[] | [-4.0, 4.0] | Per-family format delta change |
| `data.content_delta_changes` | float[] | [-4.0, 4.0] | Per-family content delta change |
| `{section}.{probe}.n` | int | [7, 22] | Sample size |
| `{section}.{probe}.sample_mean` | float | (-∞, ∞) | Observed sample mean |
| `{section}.{probe}.posterior_mean` | float | (-∞, ∞) | Posterior mean |
| `{section}.{probe}.posterior_var` | float | [0, ∞) | Posterior variance |
| `{section}.{probe}.credible_interval_95` | float[2] | [lower, upper] | 95% highest density interval |
| `{section}.{probe}.p_positive` | float | [0.0, 1.0] | P(true delta > 0 \| data) |
| `{section}.{probe}.bf10_vs_null` | float | [0, ∞) | Bayes factor for H1 vs H0 |

---

## 8. `results_rootcause/analysis_output/cohens_d.json`  Effect Sizes

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `{group}.{model}.{probe}.control_mean` | float | [1.0, 5.0] | Mean score in control condition |
| `{group}.{model}.{probe}.biased_mean` | float | [1.0, 5.0] | Mean score in biased condition |
| `{group}.{model}.{probe}.cohens_d` | float | (-∞, ∞) | Standardized effect size |
| `{group}.{model}.{probe}.direction` | string | `"biased_higher"`, `"biased_lower"` | Direction of bias |
| `{group}.{model}.{probe}.effect_size` | string | `"negligible"`, `"small"`, `"medium"`, `"large"` | Qualitative label |

---

## 9. `results_rootcause/analysis_output/wilcoxon_results.json`  Wilcoxon Tests

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `{probe}.n_families` | int | `7` | Number of paired families |
| `{probe}.mean_delta_change` | float | (-4.0, 4.0) | Mean of (instruct - base) delta |
| `{probe}.median_delta_change` | float | (-4.0, 4.0) | Median delta change |
| `{probe}.std_delta_change` | float | [0, ∞) | Standard deviation of delta changes |
| `{probe}.wilcoxon_W` | float | [0, 28] | Wilcoxon test statistic |
| `{probe}.z_statistic` | float | (-∞, ∞) | Normal approximation Z-score |
| `{probe}.p_value` | float | [0.0, 1.0] | Two-sided p-value |
| `{probe}.significant_at_005` | bool | true/false | p < 0.05 |
| `{probe}.effect_size_r` | float | [0.0, 1.0] | Effect size r = Z/√N |
| `{probe}.direction` | string | `"decrease"`, `"increase"` | Net change direction |
| `{probe}.changes_per_family` | object | {family: change, ...} | Per-family delta changes |

---

## 10. `results_rootcause/analysis_output/family_profiles.json`  Family Profiles

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `profiles[].family` | string | family name | Family identifier |
| `profiles[].probes.{probe}.base_delta` | float | [0.0, 4.0] | Base model delta |
| `profiles[].probes.{probe}.instruct_delta` | float | [0.0, 4.0] | Instruct model delta |
| `profiles[].probes.{probe}.delta_change` | float | (-4.0, 4.0) | Instruct − base |
| `profiles[].probes.{probe}.direction` | string | `"decrease"`, `"increase"` | Change direction |
| `profiles[].mean_delta_change` | float | (-4.0, 4.0) | Mean across probes |
| `profiles[].most_improved_probe` | string | probe name | Probe with largest reduction |
| `profiles[].least_improved_probe` | string | probe name | Probe with smallest reduction / largest increase |
| `profiles[].overall_improvement` | string | `"improved"`, `"worsened"` | Net verdict |

---

## 11. CSV Files in `data/raw/`

### `items_all_conditions.csv`

| Column | Type | Description |
|--------|------|-------------|
| `item_id` | int | Item index [0-79] |
| `domain` | string | Content domain |
| `instruction` | string | The instruction/question |
| `response` | string | The evaluand response |
| `probe_type` | string | `rubric_order`, `score_id`, `reference_answer` |
| `condition` | string | Variant name |
| `condition_description` | string | Human-readable description |
| `prompt_template` | string | Full prompt with rubric |
| `score_{model_name}` | float | Score from that model |

---

## 12. `results_rootcause/analysis_output/variance_decomposition.json`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `{group}.between_model_pct` | float | [0.0, 100.0] | % of variance explained by between-model differences |
| `{group}.within_model_pct` | float | [0.0, 100.0] | % of variance explained by within-model (probe) differences |

---

## 13. `results_rootcause/analysis_output/power_curve.json`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `power_by_N.{n}.{probe}.simulated_power` | float | [0.0, 1.0] | Simulated statistical power at N families |
| `power_by_N.{n}.{probe}.effect_size` | float | [0, ∞) | Estimated effect size d_z |

---

## 14. `results_rootcause/analysis_output/probe_correlations.json`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `correlation_matrix.{probe1}.{probe2}` | float | [-1.0, 1.0] | Pearson r between probe deltas |

---

## 15. `results_rootcause/analysis_output/robustness_metrics.json`

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `per_model_metrics.{model}.mean` | float | [1.0, 5.0] | Mean score across all conditions |
| `per_model_metrics.{model}.mad` | float | [0.0, 4.0] | Mean absolute deviation |
| `per_model_metrics.{model}.std` | float | [0.0, ∞) | Standard deviation |
| `per_model_metrics.{model}.cv` | float | [0.0, ∞) | Coefficient of variation |
| `per_model_metrics.{model}.max_min_delta` | float | [0.0, 4.0] | Max-min range |
| `per_model_metrics.{model}.n_variants` | int | [6, 9] | Number of probe variants tested |

### Changelog

- Initial release with 40,500+ judgments across 31 model variants
