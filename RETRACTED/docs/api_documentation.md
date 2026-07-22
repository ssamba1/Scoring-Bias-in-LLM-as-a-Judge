# API Reference  `scoring_bias` Package

> **Complete API reference for the `scoring_bias` package.**
>
> Every function, class, and method with signatures, parameters, return types, and examples.

---

## Package Overview

```
scoring_bias/
├── __init__.py          # Package exports, version info
├── models.py            # Data structures (dataclasses, enums)
├── analysis.py          # Core analysis functions
├── metrics.py           # Statistical metrics utilities
└── visualization.py     # Plotting and figure generation
```

### Package Metadata

```python
from scoring_bias import __version__, __author__
print(__version__)  # "1.0.0"
print(__author__)   # "Sricharan Samba"
```

---

## Module: `scoring_bias.models`

Core data structures used throughout the analysis pipeline.

### `ProbeType` (Enum)

```python
class ProbeType(str, Enum):
    """The three bias probes used in the study."""
    RUBRIC_ORDER = "rubric_order"
    SCORE_ID = "score_id"
    REFERENCE_ANSWER = "reference_answer"
```

**Description**: Enum of the three scoring bias probes tested in the paper.

**Values**:
| Member | Value | Description |
|--------|-------|-------------|
| `RUBRIC_ORDER` | `"rubric_order"` | Tests bias from reversed rubric direction |
| `SCORE_ID` | `"score_id"` | Tests bias from different score labeling |
| `REFERENCE_ANSWER` | `"reference_answer"` | Tests bias from showing sample answers |

**Example**:
```python
from scoring_bias.models import ProbeType

# Iterate over all probes
for probe in ProbeType:
    print(probe.value)  # "rubric_order", "score_id", "reference_answer"

# Access by string value
pt = ProbeType("rubric_order")
assert pt == ProbeType.RUBRIC_ORDER
```

---

### `ScoreRecord` (Dataclass)

```python
@dataclass
class ScoreRecord:
    """A single score from a model-judge on one probe-item."""
    model_name: str
    probe: ProbeType
    item_id: str
    condition: str
    score: float
    raw_response: Optional[str] = None
    is_base: bool = False
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `model_name` | `str` | Name of the model (e.g., `"Meta-Llama-3.1-8B"`) |
| `probe` | `ProbeType` | Which bias probe this record belongs to |
| `item_id` | `str` | Identifier for the evaluation item |
| `condition` | `str` | Experimental condition (e.g., `"normal"`, `"reversed"`, `"present"`, `"absent"`) |
| `score` | `float` | Score assigned by the model (1–5 scale) |
| `raw_response` | `Optional[str]` | Raw text output from the model (default: `None`) |
| `is_base` | `bool` | Whether this is from a base (vs instruct) variant (default: `False`) |

**Example**:
```python
rec = ScoreRecord(
    model_name="Meta-Llama-3.1-8B-Instruct",
    probe=ProbeType.RUBRIC_ORDER,
    item_id="item_042",
    condition="reversed",
    score=4.0,
    raw_response="I rate this 4 out of 5.",
    is_base=False,
)
```

---

### `ProbeResult` (Dataclass)

```python
@dataclass
class ProbeResult:
    """Aggregated results for one probe on one model."""
    model_name: str
    probe: ProbeType
    condition_scores: Dict[str, List[float]] = field(default_factory=dict)
    delta: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    flip_rate: Optional[float] = None
    is_base: bool = False
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `model_name` | `str` | Name of the model |
| `probe` | `ProbeType` | The bias probe |
| `condition_scores` | `Dict[str, List[float]]` | Scores grouped by condition (e.g., `{"normal": [3.0, 4.0], "reversed": [4.0, 4.5]}`) |
| `delta` | `Optional[float]` | Mean bias delta (Δ = treatment − control) |
| `ci_lower` | `Optional[float]` | Lower bound of 95% confidence interval |
| `ci_upper` | `Optional[float]` | Upper bound of 95% confidence interval |
| `flip_rate` | `Optional[float]` | Fraction of items where score direction changes |
| `is_base` | `bool` | Whether base variant |

**Properties**:

#### `mean_abs_bias` → `Optional[float]`

Returns `abs(self.delta)` if delta is not `None`, else `None`.

**Example**:
```python
pr = ProbeResult(
    model_name="test",
    probe=ProbeType.RUBRIC_ORDER,
    delta=0.5,
    ci_lower=0.2,
    ci_upper=0.8,
    flip_rate=0.3,
)
print(pr.mean_abs_bias)  # 0.5
```

---

### `ModelProfile` (Dataclass)

```python
@dataclass
class ModelProfile:
    """Full profile of a single judge model."""
    name: str
    family: str
    size: str
    is_base: bool = False
    probe_results: Dict[ProbeType, ProbeResult] = field(default_factory=dict)
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Full model name (e.g., `"Meta-Llama-3.1-8B"`) |
| `family` | `str` | Model family (e.g., `"Llama"`, `"Gemma"`, `"Qwen"`) |
| `size` | `str` | Parameter count (e.g., `"8B"`, `"27B"`, `"70B"`) |
| `is_base` | `bool` | Whether this is a base variant |
| `probe_results` | `Dict[ProbeType, ProbeResult]` | Results for each probe |

**Properties**:

#### `avg_delta` → `Optional[float]`

Average delta across all probes. Returns `None` if no probe results exist.

#### `avg_flip_rate` → `Optional[float]`

Average flip rate across all probes. Returns `None` if no probe results exist.

**Example**:
```python
profile = ModelProfile(
    name="Meta-Llama-3.1-8B",
    family="Llama",
    size="8B",
    is_base=True,
)
profile.probe_results[ProbeType.RUBRIC_ORDER] = ProbeResult(
    model_name="Meta-Llama-3.1-8B",
    probe=ProbeType.RUBRIC_ORDER,
    delta=0.5,
    flip_rate=0.3,
)
print(profile.avg_delta)  # 0.5
print(profile.avg_flip_rate)  # 0.3
```

---

### `BiasResult` (Dataclass)

```python
@dataclass
class BiasResult:
    """Top-level container for all bias analysis results."""
    model_profiles: Dict[str, ModelProfile] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `model_profiles` | `Dict[str, ModelProfile]` | Dictionary mapping model names to their profiles |
| `metadata` | `Dict[str, Any]` | Arbitrary metadata (e.g., analysis parameters) |

**Methods**:

#### `get_model(name: str) -> Optional[ModelProfile]`

Get a model profile by name. Returns `None` if not found.

**Properties**:

#### `model_names` → `List[str]`

List of all model names in the result.

#### `num_models` → `int`

Number of models in the result.

**Example**:
```python
results = BiasResult()
results.model_profiles["llama-8b"] = ModelProfile(
    name="llama-8b", family="Llama", size="8B"
)
print(results.num_models)  # 1
print(results.model_names)  # ["llama-8b"]
print(results.get_model("llama-8b"))  # ModelProfile(...)
print(results.get_model("nonexistent"))  # None
```

---

### `ComparisonResult` (Dataclass)

```python
@dataclass
class ComparisonResult:
    """Result of comparing base vs instruct variants of a model family."""
    family: str
    base_name: str
    instruct_name: str
    base_deltas: Dict[ProbeType, float] = field(default_factory=dict)
    instruct_deltas: Dict[ProbeType, float] = field(default_factory=dict)
    delta_of_deltas: Dict[ProbeType, float] = field(default_factory=dict)
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `family` | `str` | Model family name (e.g., `"Llama"`) |
| `base_name` | `str` | Name of the base model variant |
| `instruct_name` | `str` | Name of the instruct model variant |
| `base_deltas` | `Dict[ProbeType, float]` | Δ values for the base variant |
| `instruct_deltas` | `Dict[ProbeType, float]` | Δ values for the instruct variant |
| `delta_of_deltas` | `Dict[ProbeType, float]` | `\|Δ_base\| − \|Δ_instruct\|` per probe |

**Properties**:

#### `avg_delta_of_deltas` → `Optional[float]`

Average delta-of-deltas across all probes.

**Example**:
```python
comp = ComparisonResult(
    family="Llama",
    base_name="llama-8b",
    instruct_name="llama-8b-it",
    delta_of_deltas={
        ProbeType.RUBRIC_ORDER: 0.5,
        ProbeType.SCORE_ID: -0.2,
    },
)
print(comp.avg_delta_of_deltas)  # 0.15
```

---

## Module: `scoring_bias.analysis`

Core analysis functions for computing bias metrics.

### `compute_delta(control_scores, treatment_scores)` → `Optional[float]`

```python
def compute_delta(
    control_scores: List[float],
    treatment_scores: List[float],
) -> Optional[float]:
    """Compute the bias delta: mean(treatment) - mean(control)."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `control_scores` | `List[float]` | Scores under the control (normal) condition |
| `treatment_scores` | `List[float]` | Scores under the biased condition |

**Returns**: Mean difference (`treatment − control`), or `None` if either list is empty.

**Example**:
```python
delta = compute_delta([3.0, 4.0, 3.5], [4.0, 4.5, 4.0])
print(delta)  # 0.6666...
```

---

### `compute_flip_rate(control_scores, treatment_scores, threshold=0.5)` → `Optional[float]`

```python
def compute_flip_rate(
    control_scores: List[float],
    treatment_scores: List[float],
    threshold: float = 0.5,
) -> Optional[float]:
    """Compute the flip rate between two conditions."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `control_scores` | `List[float]` |  | Scores under control condition (per item) |
| `treatment_scores` | `List[float]` |  | Scores under treatment condition (per item) |
| `threshold` | `float` | `0.5` | Minimum absolute difference to count as a flip |

**Returns**: Fraction of items that flipped (`0.0`–`1.0`), or `None` if lists are empty or mismatched.

**Example**:
```python
rate = compute_flip_rate([3.0, 4.0], [4.0, 4.5], threshold=0.5)
print(rate)  # 1.0 (both flipped)
```

---

### `bootstrap_ci(control_scores, treatment_scores, n_resamples=10000, ci=0.95, seed=None)` → `Tuple[Optional[float], ...]`

```python
def bootstrap_ci(
    control_scores: List[float],
    treatment_scores: List[float],
    n_resamples: int = 10_000,
    ci: float = 0.95,
    seed: Optional[int] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Bootstrap confidence interval for the bias delta."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `control_scores` | `List[float]` |  | Scores under control condition |
| `treatment_scores` | `List[float]` |  | Scores under treatment condition |
| `n_resamples` | `int` | `10000` | Number of bootstrap resamples |
| `ci` | `float` | `0.95` | Confidence level |
| `seed` | `Optional[int]` | `None` | Random seed for reproducibility |

**Returns**: Tuple of `(delta, ci_lower, ci_upper)`. All `None` if inputs invalid.

**Example**:
```python
delta, lo, hi = bootstrap_ci(
    [3.0, 4.0, 3.5, 4.0],
    [4.0, 4.5, 4.0, 3.5],
    n_resamples=5000, seed=42,
)
print(f"Δ = {delta:.4f} [{lo:.4f}, {hi:.4f}]")
```

---

### `compute_model_summary(model_name, scores_by_probe, is_base=False, n_bootstrap=10000, seed=42)` → `ModelProfile`

```python
def compute_model_summary(
    model_name: str,
    scores_by_probe: Dict[ProbeType, Dict[str, List[float]]],
    is_base: bool = False,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ModelProfile:
    """Build a ModelProfile from per-probe score dictionaries."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` |  | Name of the model |
| `scores_by_probe` | `Dict[ProbeType, Dict[str, List[float]]]` |  | Dict mapping ProbeType → condition → scores |
| `is_base` | `bool` | `False` | Whether this is a base variant |
| `n_bootstrap` | `int` | `10000` | Bootstrap resamples for CI |
| `seed` | `int` | `42` | Random seed |

**Returns**: Populated `ModelProfile` with `ProbeResult` entries.

**Example**:
```python
scores = {
    ProbeType.RUBRIC_ORDER: {
        "normal": [3.0, 4.0, 3.5],
        "reversed": [4.0, 4.5, 4.0],
    },
}
profile = compute_model_summary("test-model", scores)
```

---

### `compute_base_instruct_comparison(base_name, instruct_name, results)` → `Optional[ComparisonResult]`

```python
def compute_base_instruct_comparison(
    base_name: str,
    instruct_name: str,
    results: BiasResult,
) -> Optional[ComparisonResult]:
    """Compare base vs instruct variants of the same model family."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `base_name` | `str` | Name of the base model |
| `instruct_name` | `str` | Name of the instruct model |
| `results` | `BiasResult` | Full BiasResult containing both profiles |

**Returns**: `ComparisonResult` with delta-of-deltas, or `None` if either model is missing.

---

### `load_scores_from_csv(csv_path)` → `BiasResult`

```python
def load_scores_from_csv(
    csv_path: str,
) -> BiasResult:
    """Load analysis results from a CSV file."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `csv_path` | `str` | Path to CSV file |

**CSV Format**:
| Column | Required | Description |
|--------|----------|-------------|
| `model_name` | Yes | Model identifier |
| `probe` | Yes | Probe type string (must match ProbeType values) |
| `condition` | Yes | Experimental condition |
| `score` | Yes | Score value (float) |
| `item_id` | No | Item identifier |
| `is_base` | No | "true"/"false" string |
| `raw_response` | No | Raw model output |

**Returns**: Populated `BiasResult` with computed deltas and CIs.

**Example**:
```python
results = load_scores_from_csv("experiment_results.csv")
print(f"Loaded {results.num_models} models")
```

---

## Module: `scoring_bias.metrics`

Statistical metrics and utility functions.

### `pooled_std(group1, group2)` → `Optional[float]`

```python
def pooled_std(
    group1: List[float],
    group2: List[float],
) -> Optional[float]:
    """Compute pooled standard deviation for two independent groups."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `group1` | `List[float]` | First group of scores |
| `group2` | `List[float]` | Second group of scores |

**Returns**: Pooled standard deviation, or `None` if either group has < 2 elements.

---

### `cohens_d(group1, group2)` → `Optional[float]`

```python
def cohens_d(
    group1: List[float],
    group2: List[float],
) -> Optional[float]:
    """Compute Cohen's d effect size between two groups."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `group1` | `List[float]` | First group of scores |
| `group2` | `List[float]` | Second group of scores |

**Returns**: Cohen's d value, or `None` if cannot compute.

**Interpretation**:
| |d| | Interpretation |
|-----|---------------|
| < 0.2 | Negligible |
| 0.2–0.5 | Small |
| 0.5–0.8 | Medium |
| > 0.8 | Large |

---

### `mean_absolute_deviation(scores, center=None)` → `Optional[float]`

```python
def mean_absolute_deviation(
    scores: List[float],
    center: Optional[float] = None,
) -> Optional[float]:
    """Compute mean absolute deviation from a center point."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scores` | `List[float]` |  | List of score values |
| `center` | `Optional[float]` | `None` | Center point (default: mean of scores) |

**Returns**: Mean absolute deviation, or `None` if list is empty.

---

### `effect_size_interpretation(d)` → `str`

```python
def effect_size_interpretation(d: float) -> str:
    """Interpret Cohen's d effect size qualitatively."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `d` | `float` | Cohen's d value |

**Returns**: `"negligible"`, `"small"`, `"medium"`, or `"large"`.

---

### `family_from_model(model_name)` → `str`

```python
def family_from_model(model_name: str) -> str:
    """Extract model family from a model name string."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `model_name` | `str` | e.g. `"Meta-Llama-3.1-8B"`, `"gemma-2-27b-it"` |

**Returns**: Family name: `"Llama"`, `"Gemma"`, `"Qwen"`, `"Mistral"`, `"DeepSeek"`, `"Mixtral"`, `"Falcon"`, `"OpenAI"`, or `"Other"`.

---

### `size_from_model(model_name)` → `str`

```python
def size_from_model(model_name: str) -> str:
    """Extract model size (parameter count) from a model name."""
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `model_name` | `str` | e.g. `"Meta-Llama-3.1-8B"` |

**Returns**: Size string e.g. `"8B"`, `"27B"`, `"70B"`, or `"Unknown"`.

---

## Module: `scoring_bias.visualization`

Publication-quality figure generation.

### `plot_bias_landscape(results, save_path=None, figsize=(14, 8))` → `plt.Figure`

```python
def plot_bias_landscape(
    results: BiasResult,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """Plot the bias landscape: all models sorted by average delta."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `results` | `BiasResult` |  | BiasResult with model profiles |
| `save_path` | `Optional[str]` | `None` | Optional path to save figure |
| `figsize` | `Tuple[int, int]` | `(14, 8)` | Figure dimensions |

**Returns**: Matplotlib figure object. Automatically saved to `save_path` if provided.

---

### `plot_model_comparison(model1, model2, save_path=None, figsize=(10, 6))` → `plt.Figure`

```python
def plot_model_comparison(
    model1: ModelProfile,
    model2: ModelProfile,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
) -> plt.Figure:
    """Side-by-side comparison of two models."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model1` | `ModelProfile` |  | First model profile |
| `model2` | `ModelProfile` |  | Second model profile |
| `save_path` | `Optional[str]` | `None` | Optional path to save figure |
| `figsize` | `Tuple[int, int]` | `(10, 6)` | Figure dimensions |

---

### `plot_probe_breakdown(model, save_path=None, figsize=(12, 5))` → `plt.Figure`

```python
def plot_probe_breakdown(
    model: ModelProfile,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 5),
) -> plt.Figure:
    """Plot per-probe breakdown for a single model."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `ModelProfile` |  | The model profile to plot |
| `save_path` | `Optional[str]` | `None` | Optional path to save figure |
| `figsize` | `Tuple[int, int]` | `(12, 5)` | Figure dimensions |

**Shows**: Box plots of score distributions for each condition within each probe.

---

### `plot_flip_rate_chart(results, save_path=None, figsize=(12, 7))` → `plt.Figure`

```python
def plot_flip_rate_chart(
    results: BiasResult,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 7),
) -> plt.Figure:
    """Plot flip rates across all models and probes."""
```

---

### `plot_base_instruct_comparison(comparisons, save_path=None, figsize=(12, 6))` → `plt.Figure`

```python
def plot_base_instruct_comparison(
    comparisons: List[Any],
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
) -> plt.Figure:
    """Plot base vs instruct delta-of-deltas comparison."""
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `comparisons` | `List[ComparisonResult]` |  | List of ComparisonResult objects |
| `save_path` | `Optional[str]` | `None` | Optional path to save figure |
| `figsize` | `Tuple[int, int]` | `(12, 6)` | Figure dimensions |

---

### Internal Helper: `_save_or_show(fig, save_path)` → `plt.Figure`

```python
def _save_or_show(fig: plt.Figure, save_path: Optional[str] = None) -> plt.Figure:
    """Save figure to path if provided, otherwise just return it."""
```

**Used internally by all plot functions.**

---

## Color Schemes

The visualization module defines consistent color schemes:

```python
# Model family colors
COLORS = {
    "Llama": "#E74C3C",    # Red
    "Gemma": "#3498DB",    # Blue
    "Qwen": "#2ECC71",     # Green
    "Mistral": "#F39C12",  # Orange
    "DeepSeek": "#9B59B6", # Purple
    "Other": "#95A5A6",    # Gray
}

# Probe colors and labels
PROBE_COLORS = {
    ProbeType.RUBRIC_ORDER: "#E74C3C",
    ProbeType.SCORE_ID: "#3498DB",
    ProbeType.REFERENCE_ANSWER: "#2ECC71",
}

PROBE_LABELS = {
    ProbeType.RUBRIC_ORDER: "Rubric Order",
    ProbeType.SCORE_ID: "Score ID",
    ProbeType.REFERENCE_ANSWER: "Reference Answer",
}
```

---

## Module: `scoring_bias.__init__`

Package exports and metadata.

```python
__version__ = "1.0.0"
__author__ = "Sricharan Samba"
```

**Exports**:
- `ModelProfile`, `ProbeResult`, `ScoreRecord`, `BiasResult`, `ComparisonResult` (from `models`)
- `compute_delta`, `compute_flip_rate`, `bootstrap_ci`, `compute_model_summary`, `compute_base_instruct_comparison` (from `analysis`)
- `cohens_d`, `mean_absolute_deviation`, `pooled_std`, `effect_size_interpretation` (from `metrics`)
- `plot_bias_landscape`, `plot_model_comparison`, `plot_probe_breakdown`, `plot_flip_rate_chart`, `plot_base_instruct_comparison` (from `visualization`)
