"""
scoring_bias  LLM-as-a-Judge Scoring Bias Analysis Package.

Core analysis toolkit for the paper:
    "Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape
     with Base-Instruct Comparison"

Provides:
- Data structures for models, probes, and scores
- Delta computation, flip-rate analysis, bootstrap confidence intervals
- Metric computation (Cohen's d, MAD, effect sizes)
- Visualization functions for bias landscapes
"""

__version__ = "1.0.0"
__author__ = "Sricharan Samba"

from scoring_bias.models import (
    ModelProfile,
    ProbeResult,
    ScoreRecord,
    BiasResult,
    ComparisonResult,
)
from scoring_bias.analysis import (
    compute_delta,
    compute_flip_rate,
    bootstrap_ci,
    compute_model_summary,
    compute_base_instruct_comparison,
)
from scoring_bias.metrics import (
    cohens_d,
    mean_absolute_deviation,
    pooled_std,
    effect_size_interpretation,
)
from scoring_bias.visualization import (
    plot_bias_landscape,
    plot_model_comparison,
    plot_probe_breakdown,
    plot_flip_rate_chart,
    plot_base_instruct_comparison,
)
