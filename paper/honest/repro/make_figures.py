#!/usr/bin/env python3
"""
Figure generation for "Where Does Scoring Bias Come From?"

Reads ONLY repro/results.json (produced by analyze.py) and the real dataset.
Emits three publication-quality figures to ../figures/ as both PDF (vector,
for LaTeX) and PNG (for preview). No synthetic data. Deterministic.

  fig1_base_vs_instruct  grouped bars: base vs instruct mean bias per probe
  fig2_family_dumbbell   per-family base->instruct delta, one panel per probe
  fig3_forest            mean paired change per probe with 95% bootstrap CI
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager  # noqa: F401

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
RESULTS = json.loads((HERE / "results.json").read_text())
ROOT = HERE.resolve().parents[2]
T4 = json.loads((ROOT / "results_rootcause" / "t4fam_results.json").read_text())

PROBES = ["rubric_order", "score_id", "reference_answer"]
LABEL = {p: RESULTS["summary"][p]["label"] for p in PROBES}
FAMILIES = list(RESULTS["per_family"].keys())

# ---- shared style: clean, serif, colour-blind-safe --------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman"],
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "axes.titlesize": 9,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})
C_BASE, C_INST, C_ACC = "#4C72B0", "#DD8452", "#55A868"


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}")
    plt.close(fig)


def fig1():
    fig, ax = plt.subplots(figsize=(4.2, 2.7))
    x = range(len(PROBES)); w = 0.38
    base = [RESULTS["summary"][p]["base_mean"] for p in PROBES]
    inst = [RESULTS["summary"][p]["instruct_mean"] for p in PROBES]
    ax.bar([i - w/2 for i in x], base, w, label="Base", color=C_BASE)
    ax.bar([i + w/2 for i in x], inst, w, label="Instruct", color=C_INST)
    for i, p in enumerate(PROBES):
        s = RESULTS["summary"][p]
        if s["ci_excludes_zero"]:
            top = max(base[i], inst[i])
            ax.text(i, top + 0.08, "$*$", ha="center", va="bottom", fontsize=11)
    ax.set_xticks(list(x)); ax.set_xticklabels([LABEL[p] for p in PROBES])
    ax.set_ylabel(r"Mean bias  $\Delta$  (score points)")
    ax.set_ylim(0, 3.2)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Instruction tuning reduces scoring bias ($n=7$ families)")
    ax.text(0.99, 0.02, r"$*$ = 95% CI excludes 0", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7, color="0.35")
    save(fig, "fig1_base_vs_instruct")


def _delta(model, probe):
    v = list(T4[model][probe].values()); return max(v) - min(v)


def fig2():
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.9), sharey=True)
    order = sorted(FAMILIES, key=lambda f: RESULTS["per_family"][f]["params_b"])
    for ax, p in zip(axes, PROBES):
        for j, fam in enumerate(order):
            b, i = _delta(fam, p), _delta(f"{fam}-IT", p)
            ax.plot([b, i], [j, j], color="0.7", lw=1.2, zorder=1)
            ax.scatter([b], [j], color=C_BASE, s=22, zorder=2)
            ax.scatter([i], [j], color=C_INST, s=22, zorder=2)
        ax.set_title(LABEL[p])
        ax.set_xlim(-0.15, 4.0)
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([f"{f} ({RESULTS['per_family'][f]['params_b']:g}B)"
                            for f in order] if ax is axes[0] else [])
        ax.set_xlabel(r"$\Delta$")
        ax.grid(axis="x", color="0.9", lw=0.6)
    axes[0].scatter([], [], color=C_BASE, s=22, label="Base")
    axes[0].scatter([], [], color=C_INST, s=22, label="Instruct")
    axes[0].legend(frameon=False, loc="lower right", fontsize=7)
    fig.suptitle("Per-family bias: base $\\rightarrow$ instruct", y=1.02)
    fig.tight_layout()
    save(fig, "fig2_family_dumbbell")


def fig3():
    fig, ax = plt.subplots(figsize=(4.2, 2.3))
    ys = range(len(PROBES))
    for y, p in zip(ys, PROBES):
        s = RESULTS["summary"][p]
        lo, hi = s["boot_ci95"]; mid = s["mean_change"]
        col = C_ACC if s["ci_excludes_zero"] else "0.55"
        ax.plot([lo, hi], [y, y], color=col, lw=2.2)
        ax.scatter([mid], [y], color=col, s=40, zorder=3)
        ax.text(hi + 0.05, y, f"$d_z={s['cohen_dz']:+.2f}$, {s['n_families_decreased']}/7$\\downarrow$",
                va="center", fontsize=7, color="0.3")
    ax.axvline(0, color="0.2", lw=0.8, ls="--")
    ax.set_yticks(list(ys)); ax.set_yticklabels([LABEL[p] for p in PROBES])
    ax.set_ylim(-0.6, len(PROBES) - 0.2)
    ax.set_xlim(-1.9, 1.4)
    ax.set_xlabel(r"Mean change in bias, instruct $-$ base (95% bootstrap CI)")
    ax.set_title("Effect of instruction tuning on scoring bias")
    save(fig, "fig3_forest")


if __name__ == "__main__":
    fig1(); fig2(); fig3()
    print("Wrote figures to", FIG)
    for f in sorted(FIG.glob("*.pdf")):
        print("  ", f.name)
