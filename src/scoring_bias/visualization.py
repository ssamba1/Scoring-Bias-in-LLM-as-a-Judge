"""
Visualization functions for scoring-bias research.

Generates publication-quality figures for bias landscapes,
model comparisons, probe breakdowns, and flip-rate charts.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from scoring_bias.models import (
    ProbeType,
    ProbeResult,
    ModelProfile,
    BiasResult,
)


# Color scheme
COLORS = {
    "Llama": "#E74C3C",
    "Gemma": "#3498DB",
    "Qwen": "#2ECC71",
    "Mistral": "#F39C12",
    "DeepSeek": "#9B59B6",
    "Other": "#95A5A6",
}
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


def _save_or_show(fig: plt.Figure, save_path: Optional[str] = None) -> plt.Figure:
    """Save figure to path if provided, otherwise just return it."""
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_bias_landscape(
    results: BiasResult,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """Plot the bias landscape: all models sorted by average delta.

    Each model shows deltas for all three probes as grouped bars.

    Args:
        results: BiasResult with model profiles.
        save_path: Optional path to save the figure.
        figsize: Figure dimensions.

    Returns:
        Matplotlib figure.
    """
    # Sort models by average absolute delta
    models_by_bias = sorted(
        results.model_profiles.values(),
        key=lambda m: abs(m.avg_delta) if m.avg_delta is not None else 0,
        reverse=True,
    )

    names = [m.name for m in models_by_bias]
    n_models = len(names)

    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(n_models)
    width = 0.25

    for i, probe in enumerate([ProbeType.RUBRIC_ORDER, ProbeType.SCORE_ID, ProbeType.REFERENCE_ANSWER]):
        deltas = []
        for m in models_by_bias:
            pr = m.probe_results.get(probe)
            deltas.append(pr.delta if pr and pr.delta is not None else 0)
        bars = ax.bar(x + i * width, deltas, width,
                      label=PROBE_LABELS[probe],
                      color=PROBE_COLORS[probe],
                      alpha=0.85,
                      edgecolor="white", linewidth=0.5)

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Bias Delta (Δ)", fontsize=12)
    ax.set_title("Scoring Bias Landscape: All Models", fontsize=14, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return _save_or_show(fig, save_path)


def plot_model_comparison(
    model1: ModelProfile,
    model2: ModelProfile,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
) -> plt.Figure:
    """Side-by-side comparison of two models.

    Args:
        model1: First model profile.
        model2: Second model profile.
        save_path: Optional path to save figure.
        figsize: Figure dimensions.

    Returns:
        Matplotlib figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    probes = [ProbeType.RUBRIC_ORDER, ProbeType.SCORE_ID, ProbeType.REFERENCE_ANSWER]
    labels = [PROBE_LABELS[p] for p in probes]

    for ax, model, color in [(ax1, model1, COLORS.get(model1.family, "#333")),
                              (ax2, model2, COLORS.get(model2.family, "#333"))]:
        deltas = []
        cis_low = []
        cis_high = []
        for p in probes:
            pr = model.probe_results.get(p)
            if pr and pr.delta is not None:
                deltas.append(pr.delta)
                cis_low.append(pr.delta - (pr.ci_lower if pr.ci_lower else 0))
                cis_high.append((pr.ci_upper if pr.ci_upper else pr.delta) - pr.delta)
            else:
                deltas.append(0)
                cis_low.append(0)
                cis_high.append(0)

        x = np.arange(len(probes))
        ax.bar(x, deltas, color=color, alpha=0.75, edgecolor="white", linewidth=0.5)
        ax.errorbar(x, deltas,
                    yerr=[cis_low, cis_high],
                    fmt="none", color="black", capsize=3, alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylabel("Bias Delta", fontsize=11)
        ax.set_title(model.name, fontsize=12, fontweight="bold")
        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Model Comparison", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save_or_show(fig, save_path)


def plot_probe_breakdown(
    model: ModelProfile,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 5),
) -> plt.Figure:
    """Plot per-probe breakdown for a single model.

    Shows score distributions for each condition within each probe.

    Args:
        model: The model profile to plot.
        save_path: Optional path to save figure.
        figsize: Figure dimensions.

    Returns:
        Matplotlib figure.
    """
    probes = [ProbeType.RUBRIC_ORDER, ProbeType.SCORE_ID, ProbeType.REFERENCE_ANSWER]
    fig, axes = plt.subplots(1, 3, figsize=figsize)

    for ax, probe in zip(axes, probes):
        pr = model.probe_results.get(probe)
        if not pr:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(PROBE_LABELS[probe])
            continue

        conditions = list(pr.condition_scores.keys())
        scores_list = list(pr.condition_scores.values())
        colors = plt.cm.Set2(np.linspace(0, 1, len(conditions)))

        bp = ax.boxplot(scores_list, labels=conditions, patch_artist=True,
                        widths=0.5)
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_title(PROBE_LABELS[probe], fontsize=11, fontweight="bold")
        ax.set_ylabel("Score (1-5)")
        ax.set_ylim(0.5, 5.5)
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(axis="x", rotation=20)

    fig.suptitle(f"Probe Breakdown: {model.name}", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return _save_or_show(fig, save_path)


def plot_flip_rate_chart(
    results: BiasResult,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 7),
) -> plt.Figure:
    """Plot flip rates across all models and probes.

    Args:
        results: BiasResult with model profiles.
        save_path: Optional path to save figure.
        figsize: Figure dimensions.

    Returns:
        Matplotlib figure.
    """
    models = sorted(
        results.model_profiles.values(),
        key=lambda m: m.avg_flip_rate if m.avg_flip_rate is not None else 0,
        reverse=True,
    )

    names = [m.name for m in models]
    x = np.arange(len(names))
    width = 0.25

    fig, ax = plt.subplots(figsize=figsize)

    for i, probe in enumerate([ProbeType.RUBRIC_ORDER, ProbeType.SCORE_ID, ProbeType.REFERENCE_ANSWER]):
        rates = []
        for m in models:
            pr = m.probe_results.get(probe)
            rates.append(pr.flip_rate if pr and pr.flip_rate is not None else 0)
        ax.bar(x + i * width, rates, width,
               label=PROBE_LABELS[probe],
               color=PROBE_COLORS[probe],
               alpha=0.85, edgecolor="white", linewidth=0.5)

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Flip Rate", fontsize=12)
    ax.set_title("Score Flip Rates Across Models and Probes", fontsize=14, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return _save_or_show(fig, save_path)


def plot_base_instruct_comparison(
    comparisons: List[Any],
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
) -> plt.Figure:
    """Plot base vs instruct delta-of-deltas comparison.

    Args:
        comparisons: List of ComparisonResult objects.
        save_path: Optional path to save figure.
        figsize: Figure dimensions.

    Returns:
        Matplotlib figure.
    """
    if not comparisons:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No comparison data available",
                ha="center", va="center", fontsize=14)
        return fig

    families = [c.family for c in comparisons]
    x = np.arange(len(families))
    width = 0.25

    fig, ax = plt.subplots(figsize=figsize)

    for i, probe in enumerate([ProbeType.RUBRIC_ORDER, ProbeType.SCORE_ID, ProbeType.REFERENCE_ANSWER]):
        dod = []
        for c in comparisons:
            dod.append(c.delta_of_deltas.get(probe, 0))
        ax.bar(x + i * width, dod, width,
               label=PROBE_LABELS[probe],
               color=PROBE_COLORS[probe],
               alpha=0.85, edgecolor="white", linewidth=0.5)

    ax.set_xlabel("Model Family", fontsize=12)
    ax.set_ylabel("Δ of Δs (|Base| − |Instruct|)", fontsize=12)
    ax.set_title("Base vs Instruct: Delta-of-Deltas", fontsize=14, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(families, fontsize=11)
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5,
               label="No difference")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return _save_or_show(fig, save_path)
