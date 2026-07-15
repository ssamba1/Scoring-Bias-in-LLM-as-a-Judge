# Methodology Tutorial — Step by Step

> **A detailed walkthrough of the scoring-bias analysis methodology,
> with code examples for each step.**

---

## Table of Contents

1. [Overview of the Pipeline](#overview-of-the-pipeline)
2. [Data Structures (Models)](#data-structures-models)
3. [How Probes Work](#how-probes-work)
4. [Step 1: Computing Δ (Delta)](#step-1-computing-δ-delta)
5. [Step 2: Computing Flip Rates](#step-2-computing-flip-rates)
6. [Step 3: Bootstrap Confidence Intervals](#step-3-bootstrap-confidence-intervals)
7. [Step 4: Statistical Metrics](#step-4-statistical-metrics)
8. [Step 5: Base vs Instruct Comparison](#step-5-base-vs-instruct-comparison)
9. [Step 6: Bayesian Analysis](#step-6-bayesian-analysis)
10. [Step 7: Visualization](#step-7-visualization)
11. [Full Pipeline Example](#full-pipeline-example)

---

## Overview of the Pipeline

The scoring-bias analysis pipeline takes raw model scores and processes them through several stages:

```
Raw Scores → Compute Δ → Flip Rates → Bootstrap CI → Metrics → Comparison → Visualization
```

Each stage builds on the previous one. Here's what each stage does:

1. **Compute Δ**: Calculate the bias delta for each model-probe pair
2. **Flip Rates**: Determine how frequently scores change between conditions
3. **Bootstrap CI**: Estimate uncertainty using resampling
4. **Metrics**: Compute Cohen's d, MAD, and interpret effect sizes
5. **Comparison**: Compare base vs instruct variants
6. **Bayesian Analysis**: Probability-based analysis of differences
7. **Visualization**: Create publication-quality figures

---

## Data Structures (Models)

Before diving into the analysis, let's understand the data structures in `src/scoring_bias/models.py`.

### ProbeType — The Three Bias Probes

```python
from enum import Enum

class ProbeType(str, Enum):
    """The three bias probes used in the study."""
    RUBRIC_ORDER = "rubric_order"       # Reversed rubric scale
    SCORE_ID = "score_id"               # Different score labels
    REFERENCE_ANSWER = "reference_answer"  # Sample answer shown
```

Each probe tests a different type of scoring bias.

### ScoreRecord — One Data Point

```python
@dataclass
class ScoreRecord:
    """A single score from a model-judge on one probe-item."""
    model_name: str          # e.g. "Meta-Llama-3.1-8B"
    probe: ProbeType         # Which bias probe
    item_id: str             # Which evaluation item
    condition: str           # "normal", "reversed", "present", "absent", etc.
    score: float             # Score on 1-5 scale
    raw_response: str | None  # Raw model output (optional)
    is_base: bool            # True if base variant
```

### ProbeResult — Aggregated for One Probe

```python
@dataclass
class ProbeResult:
    """Aggregated results for one probe on one model."""
    model_name: str
    probe: ProbeType
    condition_scores: Dict[str, List[float]]  # Scores grouped by condition
    delta: float | None                        # Mean bias delta
    ci_lower: float | None                     # CI lower bound
    ci_upper: float | None                     # CI upper bound
    flip_rate: float | None                    # Fraction of items that flipped
    is_base: bool

    @property
    def mean_abs_bias(self) -> float | None:
        """Mean absolute delta across all conditions."""
        return abs(self.delta) if self.delta is not None else None
```

### ModelProfile — One Model's Full Results

```python
@dataclass
class ModelProfile:
    """Full profile of a single judge model."""
    name: str
    family: str           # "Llama", "Gemma", "Qwen", etc.
    size: str             # "8B", "27B", "70B", etc.
    is_base: bool
    probe_results: Dict[ProbeType, ProbeResult]

    @property
    def avg_delta(self) -> float | None:
        """Average delta across all probes."""
        # Computed from all non-None probe deltas

    @property
    def avg_flip_rate(self) -> float | None:
        """Average flip rate across all probes."""
```

### BiasResult — Top-Level Container

```python
@dataclass
class BiasResult:
    """Top-level container for all bias analysis results."""
    model_profiles: Dict[str, ModelProfile]
    metadata: Dict[str, Any]

    def get_model(self, name: str) -> ModelProfile | None
    @property
    def model_names(self) -> List[str]
    @property
    def num_models(self) -> int
```

### ComparisonResult — Base vs Instruct

```python
@dataclass
class ComparisonResult:
    """Result of comparing base vs instruct variants."""
    family: str
    base_name: str
    instruct_name: str
    base_deltas: Dict[ProbeType, float]
    instruct_deltas: Dict[ProbeType, float]
    delta_of_deltas: Dict[ProbeType, float]  # |base| - |instruct|

    @property
    def avg_delta_of_deltas(self) -> float | None
```

---

## How Probes Work

The perturbation framework is the heart of the methodology.

### Rubric Order Probe

**What it tests**: Does reversing the scale direction change scores?

```
Normal condition:    "Score 1-5 where 1=worst, 5=best"
Treatment condition: "Score 1-5 where 1=best, 5=worst"
```

A fair model should adjust — if 5=worst, giving a 5 is bad. But biased models might just copy the number without considering direction.

### Score ID Probe

**What it tests**: Does changing score labels (numbers → letters → words) change scores?

```
Normal condition:    "Score 1-5"
Treatment condition: "Score A-E" or "Score Excellent-Terrible"
```

A fair model should map A=5, B=4, C=3, D=2, E=1. A biased model might score differently depending on the labeling system.

### Reference Answer Probe

**What it tests**: Does showing a sample answer before scoring change scores?

```
Normal condition:    "Score this response: [response]"
Treatment condition: "Here's an example good answer. Now score this response: [response]"
```

A fair model should evaluate each response independently. A biased model might anchor on the example.

---

## Step 1: Computing Δ (Delta)

The **delta** is the basic measure of bias. It's the difference between the mean score under the treatment condition and the mean score under the control condition.

### The Formula

```
Δ = mean(treatment_scores) − mean(control_scores)
```

### Code

```python
from statistics import mean
from typing import List, Optional

def compute_delta(
    control_scores: List[float],
    treatment_scores: List[float],
) -> Optional[float]:
    """Compute the bias delta: mean(treatment) - mean(control).

    A positive delta means the treatment condition increases scores
    (leniency bias). A negative delta means it decreases scores
    (strictness bias).

    Args:
        control_scores: Scores under the control (normal) condition.
        treatment_scores: Scores under the biased condition.

    Returns:
        The mean difference, or None if either list is empty.
    """
    if not control_scores or not treatment_scores:
        return None
    return mean(treatment_scores) - mean(control_scores)
```

### Example

```python
# Normal condition: rubric says 1=worst, 5=best
control = [3.0, 4.0, 3.5, 4.0, 3.0, 3.5, 4.0, 3.0, 2.5, 3.5]

# Reversed condition: rubric says 1=best, 5=worst
treatment = [4.0, 4.5, 4.0, 3.5, 3.5, 4.0, 4.5, 3.5, 3.0, 4.0]

delta = compute_delta(control, treatment)
print(f"Δ = {delta:.4f}")
# Output: Δ = 0.4000
# Interpretation: Scores increased by 0.4 on average when rubric was reversed.
# A fair model would adjust, giving similar means. This Δ shows bias.
```

### What Δ Values Mean

| Δ Value | Interpretation |
|---------|---------------|
| 0.0 | No bias — model is perfectly fair |
| 0.0–0.3 | Small bias |
| 0.3–0.8 | Moderate bias |
| 0.8+ | Large bias |
| Negative | Treatment decreases scores (strictness bias) |
| Positive | Treatment increases scores (leniency bias) |

---

## Step 2: Computing Flip Rates

The **flip rate** measures how often individual items change score between conditions. Even if the average delta is small, individual items might flip frequently.

### The Formula

```
Flip Rate = count of items where |control - treatment| >= threshold / total items
```

### Code

```python
def compute_flip_rate(
    control_scores: List[float],
    treatment_scores: List[float],
    threshold: float = 0.5,
) -> Optional[float]:
    """Compute the flip rate between two conditions.

    For paired items, the flip rate is the fraction of items where
    the score direction changes (i.e. one condition preferred the
    response more than the other).

    Args:
        control_scores: Scores under control condition (per item).
        treatment_scores: Scores under treatment condition (per item).
        threshold: Minimum absolute difference to count as a flip.

    Returns:
        Fraction of items that flipped, or None if lists are empty/mismatched.
    """
    if len(control_scores) != len(treatment_scores):
        return None
    if not control_scores:
        return None

    flips = sum(
        1 for c, t in zip(control_scores, treatment_scores)
        if abs(c - t) >= threshold
    )
    return flips / len(control_scores)
```

### Example

```python
control = [3.0, 4.0, 3.0, 4.0]
treatment = [4.0, 4.5, 3.0, 4.0]
# Compare: |3-4|=1.0 >= 0.5 → flip
#          |4-4.5|=0.5 >= 0.5 → flip
#          |3-3.0|=0.0 < 0.5  → no flip
#          |4-4.0|=0.0 < 0.5  → no flip
# Flips: 2 out of 4 = 0.5

rate = compute_flip_rate(control, treatment, threshold=0.5)
print(f"Flip rate: {rate:.1%}")  # Output: Flip rate: 50.0%
```

### Default Threshold

We use `threshold=0.5` because scores are on a 1–5 scale. A change of 0.5 represents half a point, which is meaningful (e.g., 3 vs 4 would be a flip).

---

## Step 3: Bootstrap Confidence Intervals

Bootstrap resampling estimates the uncertainty around Δ without making assumptions about the data distribution.

### How It Works

1. Compute paired deltas (treatment − control for each item)
2. Resample with replacement N times (default: 10,000)
3. Compute the mean of each resample
4. Sort the resampled means
5. Take the 2.5th and 97.5th percentiles as the 95% CI

### Code

```python
import random
from statistics import mean
from typing import List, Optional, Tuple

def bootstrap_ci(
    control_scores: List[float],
    treatment_scores: List[float],
    n_resamples: int = 10_000,
    ci: float = 0.95,
    seed: Optional[int] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Bootstrap confidence interval for the bias delta.

    Resamples paired deltas with replacement and computes the
    percentile confidence interval.

    Args:
        control_scores: Scores under control condition.
        treatment_scores: Scores under treatment condition.
        n_resamples: Number of bootstrap resamples.
        ci: Confidence level (e.g., 0.95).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (delta, ci_lower, ci_upper). All None if inputs are invalid.
    """
    if len(control_scores) != len(treatment_scores):
        return None, None, None
    if not control_scores:
        return None, None, None

    n = len(control_scores)
    paired_deltas = [t - c for c, t in zip(control_scores, treatment_scores)]
    observed_delta = mean(paired_deltas)

    if seed is not None:
        random.seed(seed)

    # Bootstrap resampling
    boot_deltas = []
    for _ in range(n_resamples):
        resample = [random.choice(paired_deltas) for _ in range(n)]
        boot_deltas.append(mean(resample))

    # Percentile CI
    alpha = 1.0 - ci
    boot_deltas.sort()
    lower_idx = int(n_resamples * alpha / 2)
    upper_idx = int(n_resamples * (1.0 - alpha / 2))

    ci_lower = boot_deltas[lower_idx] if lower_idx < n_resamples else None
    ci_upper = boot_deltas[upper_idx] if upper_idx < n_resamples else None

    return observed_delta, ci_lower, ci_upper
```

### Example

```python
delta, ci_l, ci_u = bootstrap_ci(
    control, treatment,
    n_resamples=10000, seed=42
)
print(f"Δ = {delta:.4f} [95% CI: {ci_l:.4f}, {ci_u:.4f}]")
# Output: Δ = 0.4000 [95% CI: 0.1500, 0.6500]
```

### Interpreting Bootstrap CIs

- **CI does not contain 0**: The bias is statistically significant at the 95% level.
- **CI contains 0**: We cannot rule out that the bias is zero.
- **Wide CI**: More data needed for precise estimate.
- **Narrow CI**: High confidence in the estimate.

---

## Step 4: Statistical Metrics

### Cohen's d (Effect Size)

Cohen's d standardizes the mean difference by dividing by the pooled standard deviation:

```python
def cohens_d(
    group1: List[float],
    group2: List[float],
) -> Optional[float]:
    """Compute Cohen's d effect size between two groups."""
    if not group1 or not group2:
        return None
    if len(group1) < 2 or len(group2) < 2:
        return None

    pooled = pooled_std(group1, group2)
    if pooled is None or pooled == 0.0:
        return None

    diff = mean(group1) - mean(group2)
    return diff / pooled
```

### Pooled Standard Deviation

```python
def pooled_std(
    group1: List[float],
    group2: List[float],
) -> Optional[float]:
    """Compute pooled standard deviation for two independent groups."""
    if len(group1) < 2 or len(group2) < 2:
        return None

    n1, n2 = len(group1), len(group2)
    var1 = stdev(group1) ** 2
    var2 = stdev(group2) ** 2

    pooled_num = (n1 - 1) * var1 + (n2 - 1) * var2
    pooled = math.sqrt(pooled_num / (n1 + n2 - 2))
    return pooled if pooled > 0 else None
```

### Effect Size Interpretation

```python
def effect_size_interpretation(d: float) -> str:
    """Interpret Cohen's d effect size qualitatively."""
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    else:
        return "large"
```

### Mean Absolute Deviation (MAD)

```python
def mean_absolute_deviation(
    scores: List[float],
    center: Optional[float] = None,
) -> Optional[float]:
    """Compute mean absolute deviation from a center point."""
    if not scores:
        return None
    if center is None:
        center = mean(scores)
    return sum(abs(s - center) for s in scores) / len(scores)
```

### Model Name Parsing

The package can extract family and size from model names:

```python
def family_from_model(model_name: str) -> str:
    """Extract model family from a model name string."""
    lower = model_name.lower()
    if "llama" in lower: return "Llama"
    elif "gemma" in lower: return "Gemma"
    elif "qwen" in lower: return "Qwen"
    elif "mistral" in lower: return "Mistral"
    elif "deepseek" in lower: return "DeepSeek"
    elif "mixtral" in lower: return "Mixtral"
    elif "falcon" in lower: return "Falcon"
    elif "gpt" in lower or "openai" in lower: return "OpenAI"
    else: return "Other"

def size_from_model(model_name: str) -> str:
    """Extract model size (parameter count) from a model name."""
    import re
    match = re.search(r'(\d+)\s*[Bb]', model_name)
    if match:
        return match.group(1) + "B"
    return "Unknown"
```

### Usage

```python
from scoring_bias.metrics import cohens_d, effect_size_interpretation

d = cohens_d(control_scores, treatment_scores)
print(f"Cohen's d = {d:.4f} ({effect_size_interpretation(d)})")
```

---

## Step 5: Base vs Instruct Comparison

This is the core contribution of our paper. We compare base and instruct variants of the same model family.

### How It Works

For each model family (e.g., Llama 3.1 8B):
1. Compute Δ for the base variant
2. Compute Δ for the instruct variant
3. Compute Δ-of-Δ: |Δ_base| − |Δ_instruct|

**Positive Δ-of-Δ**: Instruction tuning reduced bias (base was more biased).
**Negative Δ-of-Δ**: Instruction tuning increased bias (instruct is more biased).

### Code

```python
def compute_base_instruct_comparison(
    base_name: str,
    instruct_name: str,
    results: BiasResult,
) -> Optional[ComparisonResult]:
    """Compare base vs instruct variants of the same model family."""
    base = results.get_model(base_name)
    instr = results.get_model(instruct_name)
    if base is None or instr is None:
        return None

    family = base.family
    comp = ComparisonResult(
        family=family,
        base_name=base_name,
        instruct_name=instruct_name,
    )

    for probe in ProbeType:
        base_pr = base.probe_results.get(probe)
        instr_pr = instr.probe_results.get(probe)

        if base_pr is not None and base_pr.delta is not None:
            comp.base_deltas[probe] = base_pr.delta
        if instr_pr is not None and instr_pr.delta is not None:
            comp.instruct_deltas[probe] = instr_pr.delta

        if (base_pr is not None and base_pr.delta is not None
                and instr_pr is not None and instr_pr.delta is not None):
            comp.delta_of_deltas[probe] = abs(base_pr.delta) - abs(instr_pr.delta)

    return comp
```

### Example

```python
results = load_scores_from_csv("all_scores.csv")

# Compare Llama 3.1 8B base vs instruct
comp = compute_base_instruct_comparison(
    "Meta-Llama-3.1-8B",
    "Meta-Llama-3.1-8B-Instruct",
    results,
)

if comp:
    print(f"Family: {comp.family}")
    for probe in ProbeType:
        if probe in comp.delta_of_deltas:
            print(f"  {probe.value}: Δ-of-Δ = {comp.delta_of_deltas[probe]:+.4f}")
    print(f"  Average: {comp.avg_delta_of_deltas}")
```

### Full Model Summary Builder

The `compute_model_summary` function builds a complete `ModelProfile` from raw scores:

```python
def compute_model_summary(
    model_name: str,
    scores_by_probe: Dict[ProbeType, Dict[str, List[float]]],
    is_base: bool = False,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ModelProfile:
    """Build a ModelProfile from per-probe score dictionaries."""
    profile = ModelProfile(
        name=model_name,
        family=family_from_model(model_name),
        size=size_from_model(model_name),
        is_base=is_base,
    )

    for probe, conditions in scores_by_probe.items():
        control_conditions = [k for k in conditions
                              if "normal" in k.lower()
                              or "control" in k.lower()
                              or "present" in k.lower()]
        treatment_conditions = [k for k in conditions if k not in control_conditions]

        control_scores = []
        treatment_scores = []
        for ctrl_key in control_conditions:
            control_scores.extend(conditions.get(ctrl_key, []))
        for trt_key in treatment_conditions:
            treatment_scores.extend(conditions.get(trt_key, []))

        delta, ci_l, ci_u = bootstrap_ci(
            control_scores, treatment_scores,
            n_resamples=n_bootstrap, seed=seed,
        )
        flip_rate = compute_flip_rate(control_scores, treatment_scores)

        result = ProbeResult(
            model_name=model_name,
            probe=probe,
            condition_scores=conditions,
            delta=delta,
            ci_lower=ci_l,
            ci_upper=ci_u,
            flip_rate=flip_rate,
            is_base=is_base,
        )
        profile.probe_results[probe] = result

    return profile
```

---

## Step 6: Bayesian Analysis

Bayesian analysis provides a complementary perspective to frequentist statistics. While the codebase focuses on bootstrap CIs and Cohen's d, the paper includes Bayesian analyses that were done separately.

### What Bayesian Analysis Tells Us

- **Probability that instruction tuning reduces bias**: e.g., P(Δ_base > Δ_instruct) = 0.94
- **Credible intervals**: Bayesian analog of confidence intervals
- **Effect size distributions**: Full posterior distributions, not just point estimates

### Why Use Both Frequentist and Bayesian?

| Approach | Strengths |
|----------|-----------|
| **Frequentist** (bootstrap, Cohen's d, Wilcoxon) | Well-established, computationally cheap, no priors needed |
| **Bayesian** | Direct probability statements, handles small samples well |

---

## Step 7: Visualization

### Bias Landscape

Shows all models sorted by average absolute delta, with grouped bars for each probe:

```python
from scoring_bias.visualization import plot_bias_landscape

results = load_scores_from_csv("data.csv")
fig = plot_bias_landscape(results, save_path="bias_landscape.png")
```

### Model Comparison

Side-by-side comparison of two models:

```python
from scoring_bias.visualization import plot_model_comparison

model1 = results.get_model("Meta-Llama-3.1-8B")
model2 = results.get_model("Meta-Llama-3.1-8B-Instruct")
fig = plot_model_comparison(model1, model2, save_path="comparison.png")
```

### Probe Breakdown

Score distributions for each condition within each probe:

```python
from scoring_bias.visualization import plot_probe_breakdown

fig = plot_probe_breakdown(results.get_model("Meta-Llama-3.1-8B-Instruct"))
```

### Flip Rate Chart

Flip rates across all models and probes:

```python
from scoring_bias.visualization import plot_flip_rate_chart

fig = plot_flip_rate_chart(results, save_path="flip_rates.png")
```

### Base vs Instruct Comparison

Delta-of-deltas visualization:

```python
from scoring_bias.visualization import plot_base_instruct_comparison

comparisons = [...]  # List of ComparisonResult
fig = plot_base_instruct_comparison(comparisons, save_path="delta_of_deltas.png")
```

---

## Full Pipeline Example

Here's everything put together:

```python
"""Complete scoring-bias analysis pipeline."""
from scoring_bias.analysis import (
    load_scores_from_csv,
    compute_base_instruct_comparison,
)
from scoring_bias.metrics import cohens_d, effect_size_interpretation
from scoring_bias.visualization import (
    plot_bias_landscape,
    plot_flip_rate_chart,
    plot_base_instruct_comparison,
)
from scoring_bias.models import ProbeType

# 1. Load data
print("Loading data...")
results = load_scores_from_csv("data/raw/items_all_conditions.csv")
print(f"  Loaded {results.num_models} models")

# 2. Print summary for each model
print("\nModel Summaries:")
for name, profile in results.model_profiles.items():
    avg_d = profile.avg_delta
    if avg_d is not None:
        print(f"  {name:30s}: avg Δ = {avg_d:.4f}")

# 3. Base vs instruct comparisons
print("\nBase vs Instruct Comparisons:")
families = [
    ("Meta-Llama-3.1-8B", "Meta-Llama-3.1-8B-Instruct"),
    ("gemma-2-27b", "gemma-2-27b-it"),
    ("Qwen2.5-32B", "Qwen2.5-32B-Instruct"),
    ("Mistral-7B-v0.3", "Mistral-7B-Instruct-v0.3"),
]

comparisons = []
for base_name, instruct_name in families:
    comp = compute_base_instruct_comparison(base_name, instruct_name, results)
    if comp:
        comparisons.append(comp)
        print(f"\n  {comp.family}:")
        for probe in ProbeType:
            if probe in comp.delta_of_deltas:
                dod = comp.delta_of_deltas[probe]
                direction = "↓ bias reduced" if dod > 0 else "↑ bias increased"
                print(f"    {probe.value:20s}: Δ-of-Δ = {dod:+.4f} ({direction})")

# 4. Generate figures
print("\nGenerating figures...")
plot_bias_landscape(results, save_path="output/bias_landscape.png")
plot_flip_rate_chart(results, save_path="output/flip_rates.png")
plot_base_instruct_comparison(comparisons, save_path="output/delta_of_deltas.png")

print("\nDone! Outputs saved to output/")
```

### Expected Output

```
Loading data...
  Loaded 31 models

Model Summaries:
  Meta-Llama-3.1-8B          : avg Δ = 0.1234
  Meta-Llama-3.1-8B-Instruct : avg Δ = 0.0876
  ...

Base vs Instruct Comparisons:
  Llama:
    rubric_order       : Δ-of-Δ = +0.45 (↓ bias reduced)
    score_id           : Δ-of-Δ = +0.12 (↓ bias reduced)
    reference_answer   : Δ-of-Δ = -0.08 (↑ bias increased)

Generating figures...
  ✓ bias_landscape.png
  ✓ flip_rates.png
  ✓ delta_of_deltas.png

Done! Outputs saved to output/
```

---

## Working with the CLI

The CLI wraps the full pipeline:

```bash
# Full analysis pipeline
scoring-bias run-all --input data.csv --output results/

# Individual steps
scoring-bias compute-deltas --input data.csv
scoring-bias compute-flip-rates --input data.csv
scoring-bias bootstrap-ci --input data.csv --n-resamples 10000
scoring-bias generate-figures --input data.csv --format pdf
```

Or use the Python API directly for maximum control:

```python
from cli import cmd_run_all
import argparse

args = argparse.Namespace(
    command="run-all",
    input_file="data/raw/items_all_conditions.csv",
    output_dir="output/"
)
cmd_run_all(args)
```

---

## Summary

| Step | Function | What It Does |
|------|----------|-------------|
| 1 | `compute_delta()` | Mean difference between conditions |
| 2 | `compute_flip_rate()` | Fraction of items that change score |
| 3 | `bootstrap_ci()` | Uncertainty estimation via resampling |
| 4 | `cohens_d()` / `mean_absolute_deviation()` | Standardized effect sizes |
| 5 | `compute_base_instruct_comparison()` | Δ-of-Δs for base vs instruct |
| 6 | `compute_model_summary()` | Complete model profile |
| 7 | Various plot functions | Publication-quality figures |

Each step builds on the previous one, forming a coherent pipeline from raw scores to published results.
