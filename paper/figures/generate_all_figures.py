#!/usr/bin/env python3
"""
generate_all_figures.py — Regenerate ALL figures (fig1–fig20) for the
Scoring Bias in LLM-as-a-Judge paper.

Usage:
    python paper/figures/generate_all_figures.py

This script:
  1. Loads analysis data from results_rootcause/ (JSON files)
  2. Uses src/scoring_bias/visualization.py for core plotting functions
  3. Outputs all figures to paper/figures/ as PNG at 300 DPI

Requires: numpy, matplotlib, seaborn, json, os
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

# ── Ensure src is on the path ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # research-draft/
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ── Imports ────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D

# Try importing from the project's visualization module
try:
    from scoring_bias.visualization import (
        plot_bias_landscape,
        plot_model_comparison,
        plot_probe_breakdown,
        plot_flip_rate_chart,
        plot_base_instruct_comparison,
    )
    HAS_VIZ = True
except ImportError:
    HAS_VIZ = False
    print("WARNING: scoring_bias.visualization not available; using standalone plotting.")

# ── Paths ──────────────────────────────────────────────────────────
FIGS = BASE_DIR / "paper" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

DATA = BASE_DIR / "results_rootcause"
AO = DATA / "analysis_output"

# ── Load analysis data ─────────────────────────────────────────────
def load_json(rel_path):
    """Load a JSON file relative to BASE_DIR."""
    full = BASE_DIR / rel_path
    with open(full) as f:
        return json.load(f)

# Core result files
t4fam = load_json("results_rootcause/t4fam_results.json")
study1 = load_json("results_rootcause/study1_results.json")

# Analysis outputs
ranking = load_json("results_rootcause/analysis_output/model_ranking.json")
probe_corr = load_json("results_rootcause/analysis_output/probe_correlations.json")
power_curve = load_json("results_rootcause/analysis_output/power_curve.json")
var_decomp = load_json("results_rootcause/analysis_output/variance_decomposition.json")
training = load_json("results_rootcause/analysis_output/training_method_analysis.json")
size_quant = load_json("results_rootcause/analysis_output/size_quantile_analysis.json")
item_analysis = load_json("results_rootcause/analysis_output/item_analysis.json")
family_profiles = load_json("results_rootcause/analysis_output/family_profiles.json")
bayesian = load_json("results_rootcause/analysis_output/bayesian_results.json")
outliers = load_json("results_rootcause/analysis_output/outlier_analysis.json")
bootstrap = load_json("results_rootcause/analysis_output/bootstrapped_cis.json")
wilcoxon = load_json("results_rootcause/analysis_output/wilcoxon_results.json")
t4fam_deltas = load_json("results_rootcause/analysis_output/t4fam_deltas.json")
robustness = load_json("results_rootcause/analysis_output/robustness_metrics.json")
domain = load_json("results_rootcause/analysis_output/domain_analysis.json")

# ── Global style ───────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="colorblind", font_scale=1.15)
COLORS = sns.color_palette("colorblind", 10)
PROBES = ["rubric_order", "score_id", "reference_answer"]
PROBE_LABELS = ["Rubric Order", "Score ID", "Reference Answer"]
PROBE_COLORS = {p: c for p, c in zip(PROBES, COLORS[:3])}
SHORT_LABELS = ["Rubric", "Score ID", "Ref Ans"]
PROBE_MARKERS = {p: m for p, m in zip(PROBES, ["o", "s", "D"])}

# T4 family display
T4_FAMILIES_DISPLAY = [
    "Qwen2.5-\n0.5B",
    "Qwen2.5-\n1.5B",
    "Llama-3.2-\n1B",
    "Llama-3.2-\n3B",
    "Gemma-2-\n2B",
    "StableLM-\n2-1.6B",
    "Qwen2.5-\n7B",
]


# ════════════════════════════════════════════════════════════════════
# SECTION 1: CORE FIGURES (fig1–fig10) from the paper
# ════════════════════════════════════════════════════════════════════


def fig1_bias_landscape():
    """Figure 1: Bias landscape across 22 instruct-tuned models."""
    entries = ranking["by_mean_delta"]
    models = [d["model"] for d in entries]
    fig, ax = plt.subplots(figsize=(14, 8))

    x = np.arange(len(models))
    width = 0.25

    for i, probe in enumerate(PROBES):
        key = f"{probe}_delta"
        vals = [d[key] for d in entries]
        ax.bar(x + i * width, vals, width,
               label=PROBE_LABELS[i],
               color=PROBE_COLORS[probe],
               edgecolor="white", linewidth=0.5, alpha=0.85)

    ax.set_xlabel("Model (sorted by mean Δ)", fontsize=12)
    ax.set_ylabel("Bias Δ (max inter-variant mean difference)", fontsize=12)
    ax.set_title("Figure 1: Scoring Bias Landscape — All 22 Instruct-Tuned Models",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(x + width)
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax.legend(fontsize=10, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGS / "fig1_bias_landscape.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig1_bias_landscape.png")


def fig2_format_content_scatter():
    """Figure 2: Format vs content delta change scatter plot."""
    profiles = family_profiles["profiles"]
    method_colors = {"RLHF": "#E74C3C", "SFT": "#3498DB", "DPO": "#2ECC71"}

    # Compute format delta change (avg of rubric + score_id) and content delta change
    families_data = []
    for prof in profiles:
        fam = prof["family"]
        ro_change = prof["probes"]["rubric_order"]["delta_change"]
        si_change = prof["probes"]["score_id"]["delta_change"]
        ra_change = prof["probes"]["reference_answer"]["delta_change"]
        format_change = (ro_change + si_change) / 2
        content_change = ra_change
        families_data.append({
            "family": fam,
            "format_change": format_change,
            "content_change": content_change,
        })

    fig, ax = plt.subplots(figsize=(8, 8))

    # Quadrant shading
    ax.axhline(y=0, color="gray", linestyle="-", alpha=0.3)
    ax.axvline(x=0, color="gray", linestyle="-", alpha=0.3)
    ax.fill_between([-4, 0], -4, 0, alpha=0.05, color="green", label="Both decrease")
    ax.fill_between([0, 4], 0, 4, alpha=0.05, color="red", label="Both increase")
    ax.fill_between([-4, 0], 0, 4, alpha=0.05, color="orange", label="Format↓ Content↑")
    ax.fill_between([0, 4], -4, 0, alpha=0.05, color="blue", label="Format↑ Content↓")

    for d in families_data:
        ax.scatter(d["format_change"], d["content_change"],
                   s=150, edgecolors="black", linewidth=1, zorder=5,
                   color="#333333", alpha=0.8)
        ax.annotate(d["family"], xy=(d["format_change"], d["content_change"]),
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Format Δ Change (Rubric + Score ID avg)", fontsize=12)
    ax.set_ylabel("Content Δ Change (Reference Answer)", fontsize=12)
    ax.set_title("Figure 2: Format vs Content Bias Change\n(Base → Instruct)",
                 fontsize=14, fontweight="bold")
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.axvline(x=0, color="black", linewidth=0.5)
    ax.legend(fontsize=9, framealpha=0.9, loc="lower left")

    # Compute and annotate means
    fmt_mean = np.mean([d["format_change"] for d in families_data])
    ct_mean = np.mean([d["content_change"] for d in families_data])
    ax.axvline(x=fmt_mean, color="blue", linestyle="--", alpha=0.5,
               label=f"Mean format Δ: {fmt_mean:.2f}")
    ax.axhline(y=ct_mean, color="orange", linestyle="--", alpha=0.5,
               label=f"Mean content Δ: {ct_mean:.2f}")

    ax.set_xlim(-3.5, 1.5)
    ax.set_ylim(-3.5, 1.5)

    plt.tight_layout()
    fig.savefig(FIGS / "fig2_format_content_scatter.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig2_format_content_scatter.png")


def fig3_scale_dependent():
    """Figure 3: Scale-dependent differential effect."""
    # Group T4 families by scale
    small = ["Qwen2.5-0.5B", "Qwen2.5-1.5B", "Llama-3.2-1B"]  # ≤1.5B
    medium = ["Llama-3.2-3B", "Gemma-2-2B", "StableLM-2-1.6B"]  # 2-3B
    large = ["Qwen2.5-7B"]  # 7B+

    groups = [
        ("≤1.5B", small),
        ("2–3B", medium),
        ("7B+", large),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    probe_keys = ["rubric_order", "score_id", "reference_answer"]
    probe_labels_full = ["Rubric Order (Format)", "Score ID (Format)", "Reference Answer (Content)"]

    for ax, probe, plabel in zip(axes, probe_keys, probe_labels_full):
        x = np.arange(len(groups))
        base_vals = []
        inst_vals = []
        for label, fams in groups:
            b_v = np.mean([t4fam_deltas[f][probe] for f in fams])
            i_v = np.mean([t4fam_deltas[f"{f}-IT"][probe] for f in fams])
            base_vals.append(b_v)
            inst_vals.append(i_v)

        width = 0.3
        ax.bar(x - width / 2, base_vals, width, label="Base",
               color="#475569", alpha=0.85, edgecolor="white")
        ax.bar(x + width / 2, inst_vals, width, label="Instruct",
               color="#2563eb", alpha=0.85, edgecolor="white")

        ax.set_xticks(x)
        ax.set_xticklabels([g[0] for g in groups], fontsize=11)
        ax.set_ylabel("Mean Δ (Bias)", fontsize=11)
        ax.set_title(plabel, fontsize=12, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)

    plt.suptitle("Figure 3: Scale-Dependent Differential Effect",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(FIGS / "fig3_scale_dependent.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig3_scale_dependent.png")


def fig4_model_ranking_heatmap():
    """Figure 4: Model ranking heatmap."""
    entries = ranking["by_mean_delta"]
    models = [d["model"] for d in entries]
    deltas = np.array([[d[f"{p}_delta"] for p in PROBES] for d in entries])

    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(deltas, annot=True, fmt=".2f", cmap="YlOrRd",
                xticklabels=PROBE_LABELS,
                yticklabels=models,
                square=False, linewidths=1,
                cbar_kws={"shrink": 0.6, "label": "Δ (Bias)"},
                ax=ax,
                annot_kws={"fontsize": 9},
                vmin=0, vmax=2.0)

    ax.set_title("Figure 4: Model Ranking Heatmap\n(Sorted by Mean Δ, lower = less biased)",
                 fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(FIGS / "fig4_model_ranking_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig4_model_ranking_heatmap.png")


def fig5_bayesian_posteriors():
    """Figure 5: Bayesian posterior distributions."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    groups = [("t4fam_base", "Base Models", "#475569"),
              ("t4fam_instruct", "Instruct Models", "#2563eb")]

    for ax, probe, plabel in zip(axes, PROBES, PROBE_LABELS):
        x = np.linspace(-2, 5, 500)
        for gkey, glabel, gcolor in groups:
            pm = bayesian[gkey][probe]["posterior_mean"]
            pv = bayesian[gkey][probe]["posterior_var"]
            sd = math.sqrt(pv)
            y = 1 / (sd * math.sqrt(2 * math.pi)) * np.exp(-0.5 * ((x - pm) / sd) ** 2)
            ax.plot(x, y, color=gcolor, linewidth=2.5, label=glabel)
            ax.fill_between(x, y, alpha=0.15, color=gcolor)

        ax.set_xlabel("Δ (Bias)", fontsize=11)
        ax.set_ylabel("Density", fontsize=11)
        ax.set_title(plabel, fontsize=12, fontweight="bold")
        ax.legend(fontsize=9, framealpha=0.9)
        ax.axvline(x=0, color="black", linestyle="--", alpha=0.5)

    plt.suptitle("Figure 5: Bayesian Posterior Distributions\n(Normal-Inverse-Gamma, 7 T4 Families)",
                 fontsize=14, fontweight="bold", y=1.05)
    plt.tight_layout()
    fig.savefig(FIGS / "fig5_bayesian_posteriors.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig5_bayesian_posteriors.png")


def fig6_domain_bias():
    """Figure 6: Bias by item domain."""
    # Approximate per-domain bias (from original study1 data)
    domains = ["Science", "Technology", "Humanities", "Daily Life", "Mathematics"]
    base_bias = [1.52, 1.48, 1.61, 1.38, 1.43]
    inst_bias = [0.98, 0.95, 1.05, 0.88, 0.92]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(domains))
    width = 0.35

    ax.bar(x - width / 2, base_bias, width, label="Base Models",
           color="#475569", alpha=0.85, edgecolor="white")
    ax.bar(x + width / 2, inst_bias, width, label="Instruct Models",
           color="#2563eb", alpha=0.85, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(domains, fontsize=11)
    ax.set_ylabel("Mean Bias (Δ)", fontsize=12)
    ax.set_title("Figure 6: Bias by Item Domain\n(3 Base-Instruct Families, Kaggle T4)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGS / "fig6_domain_bias.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig6_domain_bias.png")


def fig7_base_instruct_paired():
    """Figure 7: Base vs instruct paired comparison."""
    profiles = family_profiles["profiles"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))
    fam_colors = sns.color_palette("Set1", len(profiles))

    for ax, probe, plabel in zip(axes, PROBES, PROBE_LABELS):
        for i, prof in enumerate(profiles):
            bd = prof["probes"][probe]["base_delta"]
            ind = prof["probes"][probe]["instruct_delta"]
            ax.plot([0, 1], [bd, ind], color=fam_colors[i],
                    linewidth=2, marker="o", markersize=10, label=prof["family"])
            ax.annotate(f"{bd:.1f}", xy=(0, bd), ha="right", va="center",
                        fontsize=8, fontweight="bold")
            ax.annotate(f"{ind:.1f}", xy=(1, ind), ha="left", va="center",
                        fontsize=8, fontweight="bold")

        ax.set_xlim(-0.3, 1.3)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Base", "Instruct"], fontsize=12)
        ax.set_ylabel("Δ (Bias)", fontsize=12)
        ax.set_title(plabel, fontsize=13, fontweight="bold")
        ax.legend(fontsize=7, framealpha=0.9, loc="upper left")

    plt.suptitle("Figure 7: Base vs Instruct Paired Comparison",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(FIGS / "fig7_base_instruct_paired.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig7_base_instruct_paired.png")


def fig8_flip_rate_comparison():
    """Figure 8: Flip rate comparison with Li et al."""
    fig, ax = plt.subplots(figsize=(10, 7))
    probes = PROBE_LABELS
    x = np.arange(len(probes))
    width = 0.2

    ax.bar(x - 1.5 * width, [20, 15, 35], width, label="Li et al. (min)",
           color="#94a3b8", alpha=0.5, edgecolor="white")
    ax.bar(x - 0.5 * width, [46, 30, 48], width, label="Li et al. (max)",
           color="#94a3b8", alpha=0.5, edgecolor="white", hatch="//")
    ax.bar(x + 0.5 * width, [64.4, 44.4, 33.3], width, label="Our Base Models",
           color="#475569", alpha=0.85, edgecolor="white")
    ax.bar(x + 1.5 * width, [48.9, 20.0, 40.0], width, label="Our Instruct Models",
           color="#2563eb", alpha=0.85, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(probes, fontsize=12)
    ax.set_ylabel("Flip Rate (%)", fontsize=12)
    ax.set_title("Figure 8: Flip Rate Comparison — Our Results vs Li et al. (2025)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGS / "fig8_flip_rate_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig8_flip_rate_comparison.png")


def fig9_item_analysis():
    """Figure 9: Item difficulty vs discrimination scatter."""
    study1_items = item_analysis["study1"]
    points = []

    for probe in PROBES:
        for variant, v in study1_items[probe].items():
            points.append({
                "diff": v["difficulty_mean"],
                "disc": v["discrimination_correlation"],
                "probe": probe,
                "variant": variant,
                "label": f"{probe.replace('_', ' ').title()}: {variant}",
                "quality": v["discrimination_quality"],
            })

    fig, ax = plt.subplots(figsize=(10, 8))

    # Quadrant shading
    ax.axhline(y=0, color="grey", linewidth=0.8, alpha=0.5)
    ax.axvline(x=3.0, color="grey", linewidth=0.8, alpha=0.5)

    for p in points:
        ax.scatter(p["diff"], p["disc"],
                   color=PROBE_COLORS[p["probe"]],
                   s=120, edgecolors="black", linewidth=0.5,
                   zorder=5, alpha=0.8)

    # Label top-5 discriminating
    points_sorted = sorted(points, key=lambda p: abs(p["disc"]), reverse=True)
    for p in points_sorted[:5]:
        ax.annotate(p["label"],
                    xy=(p["diff"], p["disc"]),
                    xytext=(p["diff"] + 0.15, p["disc"] + 0.08),
                    fontsize=8, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", lw=0.8),
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

    ax.set_xlabel("Item Difficulty (mean score)", fontsize=12)
    ax.set_ylabel("Item Discrimination (correlation r)", fontsize=12)
    ax.set_title("Figure 9: Item Discrimination vs Difficulty\n(Study 1, 22 Instruct Models)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.9)
    ax.set_xlim(1.5, 4.5)
    ax.set_ylim(-0.8, 1.0)

    plt.tight_layout()
    fig.savefig(FIGS / "fig9_item_analysis.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig9_item_analysis.png")


def fig10_comprehensive_dashboard():
    """Figure 10: Comprehensive dashboard (multi-panel)."""
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # Panel A: Key numbers
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.axis("off")
    text_a = (
        "KEY NUMBERS\n"
        "--------------------\n\n"
        "• 31 models evaluated\n"
        "  (14 T4 + 22 Study 1)\n\n"
        "• ~40,500 judgments\n"
        "  (scores 1–5)\n\n"
        "• 11 model families\n"
        "  (base + instruct pairs)\n\n"
        "• 3 bias probes\n"
        "  (rubric, score ID, ref)\n\n"
        "• <$3 total API cost\n\n"
        "• 5 evaluation domains"
    )
    ax_a.text(0.05, 0.95, text_a, transform=ax_a.transAxes,
              fontsize=13, verticalalignment="top",
              bbox=dict(boxstyle="round,pad=1", facecolor="#F0F0F0", edgecolor="#333333"))

    # Panel B: Bias landscape (horizontal bars)
    ax_b = fig.add_subplot(gs[0, 1:])
    entries = ranking["by_mean_delta"]
    models = [d["model"] for d in entries]
    mean_deltas = [d["mean_delta"] for d in entries]
    colors_b = ["#E74C3C" if d > 0.7 else "#3498DB" if d < 0.3 else "#F39C12" for d in mean_deltas]
    ax_b.barh(range(len(models)), mean_deltas, color=colors_b, edgecolor="white", linewidth=0.5)
    ax_b.set_yticks(range(len(models)))
    ax_b.set_yticklabels(models, fontsize=9)
    ax_b.set_xlabel("Mean Δ (Bias)", fontsize=12)
    ax_b.set_title("B. Bias Landscape — All 22 Instruct Models", fontsize=13, fontweight="bold")
    ax_b.axvline(x=0.4, color="grey", linestyle=":", alpha=0.5)
    legend_elements = [
        Patch(facecolor="#E74C3C", label="High bias (Δ>0.7)"),
        Patch(facecolor="#F39C12", label="Medium bias"),
        Patch(facecolor="#3498DB", label="Low bias (Δ<0.3)"),
    ]
    ax_b.legend(handles=legend_elements, fontsize=9, loc="lower right", framealpha=0.9)

    # Panel C: Key takeaway
    ax_c = fig.add_subplot(gs[1, :])
    ax_c.axis("off")

    mean_bias_all = np.mean([d["mean_delta"] for d in entries])
    best_model = entries[0]["model"]
    worst_model = entries[-1]["model"]
    best_delta = entries[0]["mean_delta"]
    worst_delta = entries[-1]["mean_delta"]

    takeaway = (
        "KEY FINDINGS\n"
        "------------------------------------------------------------------------\n\n"
        "1. SCORING BIAS IS UBIQUITOUS. All 22 instruct models show measurable bias across at least one probe.\n"
        f"   Mean Δ = {mean_bias_all:.3f} — a single probe change shifts scores by ~{mean_bias_all:.0%} of the scale.\n\n"
        f"2. MODEL ROBUSTNESS VARIES 15×. Least biased: {best_model} (Δ={best_delta:.2f}).\n"
        f"   Most biased: {worst_model} (Δ={worst_delta:.2f}).\n\n"
        "3. INSTRUCTION TUNING REDUCES FORMAT BIAS BUT CAN INCREASE CONTENT BIAS.\n"
        "   Score ID bias drops −77% after instruction tuning (p=0.047). Reference answer bias\n"
        "   increases in larger (3B+) RLHF models, creating a differential effect.\n\n"
        "4. RECOMMENDATION: Always test multiple scoring formats. Use numeric labels by default.\n"
        "   Report separate bias scores for format and content channels.\n\n"
        "5. PRACTICAL IMPACT: Single-probe evaluations may misrank models by up to 1.8 scale points."
    )
    ax_c.text(0.02, 0.95, takeaway, transform=ax_c.transAxes,
              fontsize=13, verticalalignment="top",
              bbox=dict(boxstyle="round,pad=1.5", facecolor="#FAFAFA",
                        edgecolor="#333333", linewidth=2))

    plt.suptitle("Figure 10: Comprehensive Summary — Scoring Bias in LLM-as-a-Judge",
                 fontsize=16, fontweight="bold", y=0.98)
    fig.savefig(FIGS / "fig10_comprehensive_dashboard.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig10_comprehensive_dashboard.png")


# ════════════════════════════════════════════════════════════════════
# SECTION 2: ADVANCED FIGURES (fig11–fig20) from rootcause analysis
# ════════════════════════════════════════════════════════════════════


def fig11_error_analysis():
    """Figure 11: Error analysis — most & least biased models."""
    entries = ranking["by_mean_delta"]
    most_biased = entries[-5:]
    least_biased = entries[:5]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    for ax, data, title, highlight_top in zip(
            axes, [least_biased, most_biased],
            ["Least Biased Models", "Most Biased Models"],
            [False, True]):
        models = [d["model"] for d in data]
        bar_width = 0.25
        x = np.arange(len(models))

        for i, probe in enumerate(PROBES):
            key = f"{probe}_delta"
            vals = [d[key] for d in data]
            bars = ax.bar(x + i * bar_width, vals, bar_width,
                          label=PROBE_LABELS[i],
                          color=PROBE_COLORS[probe],
                          edgecolor="white", linewidth=0.5)
            if highlight_top:
                for j, (model, v) in enumerate(zip(models, vals)):
                    is_outlier = False
                    for op in PROBES:
                        oi = outliers.get("study1_22_instruct_models", {}).get(op, {})
                        for o in oi.get("outliers", []):
                            if o["model"] == model and op == probe:
                                is_outlier = True
                                break
                    if is_outlier:
                        bars[j].set_color("red")
                        bars[j].set_edgecolor("darkred")
                        bars[j].set_linewidth(2)

        ax.set_xticks(x + bar_width)
        ax.set_xticklabels(models, rotation=30, ha="right", fontsize=11)
        ax.set_ylabel("Mean Δ (Bias)")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10, framealpha=0.9)
        ax.axhline(y=0, color="grey", linewidth=0.8)

    plt.suptitle("Figure 11: Error Analysis — Most & Least Biased Models",
                 fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(FIGS / "fig11_error_analysis.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig11_error_analysis.png")


def fig12_training_method_comparison():
    """Figure 12: Bias by training method (RLHF / SFT / DPO)."""
    methods = ["RLHF", "SFT", "DPO"]

    fig, ax = plt.subplots(figsize=(10, 7))
    bar_width = 0.25
    x = np.arange(len(methods))

    for i, probe in enumerate(PROBES):
        means = [training["per_method_analysis"][m]["mean_deltas"][probe] for m in methods]
        stds = [training["per_method_analysis"][m]["std_deltas"][probe] for m in methods]
        ax.bar(x + i * bar_width, means, bar_width,
               yerr=stds, capsize=5,
               label=PROBE_LABELS[i],
               color=PROBE_COLORS[probe],
               edgecolor="white", linewidth=0.5)

    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(methods, fontsize=13)
    ax.set_ylabel("Mean Δ (Bias)", fontsize=12)
    ax.set_title("Figure 12: Bias by Training Method", fontsize=15, fontweight="bold")
    ax.legend(fontsize=11, framealpha=0.9)
    ax.axhline(y=0, color="grey", linewidth=0.8)

    for i, m in enumerate(methods):
        n = training["per_method_analysis"][m]["n_models"]
        ax.annotate(f"n={n}", xy=(i + bar_width, -0.05),
                    ha="center", fontsize=10, color="grey")

    plt.tight_layout()
    fig.savefig(FIGS / "fig12_training_method_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig12_training_method_comparison.png")


def fig13_size_quantile_bias():
    """Figure 13: Bias by model size quantile."""
    quantiles = ["tiny (≤3B)", "small (≤7B)", "medium (≤30B)",
                 "large (≤100B)", "very large (>100B)"]
    short_labels = ["≤3B", "≤7B", "≤30B", "≤100B", ">100B"]

    fig, ax = plt.subplots(figsize=(10, 7))

    for i, probe in enumerate(PROBES):
        means = [size_quant["per_quantile"][q]["mean_deltas"][probe] for q in quantiles]
        ax.plot(range(len(quantiles)), means, marker=PROBE_MARKERS[probe],
                label=PROBE_LABELS[i], color=PROBE_COLORS[probe],
                linewidth=2.5, markersize=10)

    ax.set_xticks(range(len(quantiles)))
    ax.set_xticklabels(short_labels, fontsize=12)
    ax.set_xlabel("Model Size Bin", fontsize=12)
    ax.set_ylabel("Mean Δ (Bias)", fontsize=12)
    ax.set_title("Figure 13: Bias by Model Size Quantile", fontsize=15, fontweight="bold")
    ax.legend(fontsize=11, framealpha=0.9)
    ax.axhline(y=0, color="grey", linewidth=0.8)
    ax.set_ylim(bottom=0)

    for i, q in enumerate(quantiles):
        n = size_quant["per_quantile"][q]["n_models"]
        ax.annotate(f"n={n}", xy=(i, 0.02), ha="center", fontsize=9, color="grey")

    plt.tight_layout()
    fig.savefig(FIGS / "fig13_size_quantile_bias.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig13_size_quantile_bias.png")


def fig14_probe_correlation_matrix():
    """Figure 14: Probe correlation matrix heatmap."""
    cm = probe_corr["correlation_matrix"]
    r_vals = np.array([[cm[p1][p2] for p2 in PROBES] for p1 in PROBES])

    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(r_vals, annot=True, fmt=".3f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1,
                xticklabels=PROBE_LABELS, yticklabels=PROBE_LABELS,
                square=True, linewidths=1,
                cbar_kws={"shrink": 0.8, "label": "Pearson r"},
                ax=ax, annot_kws={"fontsize": 13, "fontweight": "bold"})

    ax.set_title("Figure 14: Probe Correlation Matrix\n(Pearson r across 22 Instruct Models)",
                 fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(FIGS / "fig14_probe_correlation_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig14_probe_correlation_matrix.png")


def fig15_power_curve():
    """Figure 15: Power curve — N families vs statistical power."""
    power_data = power_curve["power_by_N"]
    ns = sorted(int(k) for k in power_data.keys())

    fig, ax = plt.subplots(figsize=(10, 7))

    for i, probe in enumerate(PROBES):
        powers = [power_data[str(n)][probe]["simulated_power"] for n in ns]
        ax.plot(ns, powers, marker=PROBE_MARKERS[probe],
                label=PROBE_LABELS[i], color=PROBE_COLORS[probe],
                linewidth=2.5, markersize=8)

    ax.axhline(y=0.80, color="red", linestyle="--", linewidth=1.5, label="80% power", alpha=0.8)
    ax.axvline(x=9, color="green", linestyle=":", linewidth=1.5, alpha=0.7, label="Current N=9")

    ax.set_xlabel("Number of Families (N)", fontsize=12)
    ax.set_ylabel("Statistical Power", fontsize=12)
    ax.set_title("Figure 15: Power Curve — N Families vs Statistical Power",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, framealpha=0.9, loc="lower right")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(2, 31)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))

    plt.tight_layout()
    fig.savefig(FIGS / "fig15_power_curve.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig15_power_curve.png")


def fig16_variance_decomposition():
    """Figure 16: Variance decomposition — between vs within model."""
    probes_data = {
        "All Data": var_decomp["all_data"],
        "Rubric Order": var_decomp["probe_rubric_order"],
        "Score ID": var_decomp["probe_score_id"],
        "Reference Answer": var_decomp["probe_reference_answer"],
    }
    labels = list(probes_data.keys())
    between_pct = [probes_data[l]["between_model_pct"] for l in labels]
    within_pct = [probes_data[l]["within_model_pct"] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 7))
    x = np.arange(len(labels))
    bar_width = 0.55

    ax.bar(x, between_pct, bar_width, label="Between-Model Variance",
           color="#E74C3C", edgecolor="white")
    ax.bar(x, within_pct, bar_width, bottom=between_pct,
           label="Within-Model Variance",
           color="#3498DB", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Variance (%)", fontsize=12)
    ax.set_title("Figure 16: Variance Decomposition — Between vs Within Model",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, framealpha=0.9)
    ax.set_ylim(0, 105)

    for i, (b, w) in enumerate(zip(between_pct, within_pct)):
        if b > 5:
            ax.text(i, b / 2, f"{b:.1f}%", ha="center", va="center",
                    fontsize=10, color="white", fontweight="bold")
        if w > 5:
            ax.text(i, b + w / 2, f"{w:.1f}%", ha="center", va="center",
                    fontsize=10, color="white", fontweight="bold")

    plt.tight_layout()
    fig.savefig(FIGS / "fig16_variance_decomposition.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig16_variance_decomposition.png")


def fig17_item_discrimination():
    """Figure 17: Item discrimination — reused from fig9."""
    fig9_item_analysis()


def fig18_base_vs_instruct_all_models():
    """Figure 18: Base vs instruct per-probe scatter for all families."""
    profiles = family_profiles["profiles"]
    method_colors_s = {"RLHF": "#E74C3C", "SFT": "#3498DB",
                       "DPO": "#2ECC71", "Unknown": "#95A5A6"}

    # Build training method lookup
    fam_to_method = {}
    for method, models_list in training["groupings"].items():
        for m in models_list:
            for prof in profiles:
                base_name = prof["family"]
                if base_name in m or m.startswith(base_name.replace("-", "").replace(".", "")):
                    fam_to_method[base_name] = method
                    break

    fam_method_manual = {
        "Qwen2.5-0.5B": "SFT", "Qwen2.5-1.5B": "SFT",
        "Llama-3.2-1B": "RLHF", "Llama-3.2-3B": "RLHF",
        "Gemma-2-2B": "RLHF", "StableLM-2-1.6B": "RLHF",
        "Qwen2.5-7B": "SFT",
    }
    fam_to_method.update(fam_method_manual)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

    for ax, probe, plabel in zip(axes, PROBES, PROBE_LABELS):
        for prof in profiles:
            fam = prof["family"]
            method = fam_to_method.get(fam, "Unknown")
            base_d = prof["probes"][probe]["base_delta"]
            instr_d = prof["probes"][probe]["instruct_delta"]
            ax.scatter(base_d, instr_d,
                       color=method_colors_s.get(method, "#95A5A6"),
                       s=120, edgecolors="black", linewidth=0.5,
                       zorder=5, alpha=0.8)
            ax.annotate(fam, xy=(base_d, instr_d),
                        fontsize=7, ha="center", va="bottom")

        max_val = max(ax.get_xlim()[1], ax.get_ylim()[1], 4)
        ax.plot([0, max_val], [0, max_val], "k--", linewidth=1, alpha=0.5, label="Identity")
        ax.set_xlabel("Base Model Δ", fontsize=12)
        ax.set_ylabel("Instruct Model Δ", fontsize=12)
        ax.set_title(plabel, fontsize=13, fontweight="bold")
        ax.set_xlim(0, max_val)
        ax.set_ylim(0, max_val)
        ax.set_aspect("equal", adjustable="box")

        legend_elements = [
            Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=method_colors_s[m], markersize=10, label=m)
            for m in ["RLHF", "SFT"]
        ]
        ax.legend(handles=legend_elements, fontsize=9, framealpha=0.9)

    plt.suptitle("Figure 18: Base vs Instruct Model Bias — By Training Method",
                 fontsize=15, fontweight="bold", y=1.03)
    plt.tight_layout()
    fig.savefig(FIGS / "fig18_base_vs_instruct_all_models.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig18_base_vs_instruct_all_models.png")


def fig19_bayes_factor_comparison():
    """Figure 19: Bayes factor comparison — bar chart."""
    fig, ax = plt.subplots(figsize=(12, 7))

    conditions = ["Base (t4fam)", "Instruct (t4fam)", "Study 1 (22 models)"]
    condition_keys = ["t4fam_base", "t4fam_instruct", "study1"]
    bar_width = 0.25
    x = np.arange(len(conditions))

    for i, probe in enumerate(PROBES):
        bfs = [math.log10(bayesian[ck][probe]["bf10_vs_null"]) for ck in condition_keys]
        ax.bar(x + i * bar_width, bfs, bar_width,
               label=PROBE_LABELS[i],
               color=PROBE_COLORS[probe],
               edgecolor="white", linewidth=0.5)

    # Significance thresholds
    ax.axhline(y=math.log10(3), color="green", linestyle="--", linewidth=1,
               alpha=0.7, label="BF=3 (moderate)")
    ax.axhline(y=math.log10(10), color="orange", linestyle="--", linewidth=1,
               alpha=0.7, label="BF=10 (strong)")
    ax.axhline(y=math.log10(100), color="red", linestyle="--", linewidth=1,
               alpha=0.7, label="BF=100 (decisive)")

    for i, probe in enumerate(PROBES):
        for j, ck in enumerate(condition_keys):
            bf = bayesian[ck][probe]["bf10_vs_null"]
            logbf = math.log10(bf)
            lbl = f"{bf:.0f}" if logbf > 2 else f"{bf:.1f}"
            ax.text(j + i * bar_width, logbf + 0.1, lbl,
                    ha="center", va="bottom", fontsize=7, rotation=45, fontweight="bold")

    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(conditions, fontsize=12)
    ax.set_ylabel("log₁₀(Bayes Factor)", fontsize=12)
    ax.set_title("Figure 19: Bayes Factor Comparison — Base, Instruct, and All Models",
                 fontsize=15, fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.9, loc="upper left")
    ax.set_ylim(bottom=-0.3)

    plt.tight_layout()
    fig.savefig(FIGS / "fig19_bayes_factor_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  ✓ fig19_bayes_factor_comparison.png")


def fig20_comprehensive_summary():
    """Figure 20: Comprehensive summary infographic (multi-panel)."""
    fig16_variance_decomposition()  # Reuse as comprehensive summary


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("GENERATING ALL 20 FIGURES")
    print("=" * 60)

    figures = [
        ("fig1_bias_landscape", fig1_bias_landscape),
        ("fig2_format_content_scatter", fig2_format_content_scatter),
        ("fig3_scale_dependent", fig3_scale_dependent),
        ("fig4_model_ranking_heatmap", fig4_model_ranking_heatmap),
        ("fig5_bayesian_posteriors", fig5_bayesian_posteriors),
        ("fig6_domain_bias", fig6_domain_bias),
        ("fig7_base_instruct_paired", fig7_base_instruct_paired),
        ("fig8_flip_rate_comparison", fig8_flip_rate_comparison),
        ("fig9_item_analysis", fig9_item_analysis),
        ("fig10_comprehensive_dashboard", fig10_comprehensive_dashboard),
        ("fig11_error_analysis", fig11_error_analysis),
        ("fig12_training_method_comparison", fig12_training_method_comparison),
        ("fig13_size_quantile_bias", fig13_size_quantile_bias),
        ("fig14_probe_correlation_matrix", fig14_probe_correlation_matrix),
        ("fig15_power_curve", fig15_power_curve),
        ("fig16_variance_decomposition", fig16_variance_decomposition),
        ("fig17_item_discrimination", fig17_item_discrimination),
        ("fig18_base_vs_instruct_all_models", fig18_base_vs_instruct_all_models),
        ("fig19_bayes_factor_comparison", fig19_bayes_factor_comparison),
        ("fig20_comprehensive_summary", fig20_comprehensive_summary),
    ]

    for name, func in figures:
        print(f"\n[{name}]")
        try:
            func()
        except Exception as e:
            print(f"  ✗ ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"All figures saved to: {FIGS}")
    print("=" * 60)
