#!/usr/bin/env python3
"""
Mechanism + causal figures for the paper. Reads results_mechanism.json (from
analyze_mechanism.py) and patch_results.json (from the patching kernel). Emits
figures/fig_mech.pdf|png (3 panels) and figures/fig_patch.pdf|png. Deterministic.
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
C_BASE, C_INST, C_ACC = "#4C72B0", "#DD8452", "#55A868"


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for e in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{e}")
    plt.close(fig)


def _paired_panel(ax, per_fam, ylabel, title):
    for f in per_fam:
        ax.plot([0, 1], [per_fam[f]["base"], per_fam[f]["instruct"]], "-o", color="0.6", ms=3.5)
    ax.scatter([0]*len(per_fam), [per_fam[f]["base"] for f in per_fam], color=C_BASE, zorder=3, s=22, label="base")
    ax.scatter([1]*len(per_fam), [per_fam[f]["instruct"] for f in per_fam], color=C_INST, zorder=3, s=22, label="instruct")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["base", "instruct"]); ax.set_xlim(-0.3, 1.3)
    ax.set_ylabel(ylabel); ax.set_title(title, fontsize=8)


def _scatter_panel(ax, x, y, rho, xlabel, title, col):
    x, y = np.array(x), np.array(y)
    ax.scatter(x, y, s=11, alpha=0.5, color=col)
    if len(x) > 2:
        b, a = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 20)
        ax.plot(xs, a + b*xs, color="0.2", lw=1.2)
    ax.set_xlabel(xlabel); ax.set_ylabel(r"bias $\Delta$")
    ax.set_title(title + f"\n$\\rho={rho}$", fontsize=8)


def fig_mech(m):
    """Four-panel decomposition: both terms (base->instruct) and both bias correlations."""
    has_resp = "responsiveness_per_family" in m
    n = 4 if has_resp else 2
    fig, ax = plt.subplots(1, n, figsize=(2.4 * n, 2.7))
    _paired_panel(ax[0], m["decisiveness_per_family"], "score entropy (bits)",
                  "(a) tuning sharpens\n(decisiveness $\\downarrow$)")
    ax[0].legend(frameon=False, fontsize=6, loc="lower left")
    lp = m["link_points"]
    _scatter_panel(ax[1], lp["entropy"], lp["delta"], m["entropy_bias_link"]["spearman_rho"],
                   "score entropy (bits)", "(b) decisive $\\Rightarrow$ more biased", C_ACC)
    if has_resp:
        _paired_panel(ax[2], m["responsiveness_per_family"], "distribution shift (TV)",
                      "(c) tuning raises\nresponsiveness $\\uparrow$")
        rp = m["responsiveness_link_points"]
        _scatter_panel(ax[3], rp["resp"], rp["delta"], m["responsiveness_bias_link"]["spearman_rho"],
                       "responsiveness (TV)", "(d) responsive $\\Rightarrow$ more biased", "#C44E52")
    fig.tight_layout()
    save(fig, "fig_mech")


def fig_patch(p):
    gc = p.get("frac_toward_instruct") or p.get("per_layer_gap_closed")
    layers = sorted(int(k) for k in gc)
    vals = [gc[str(L)] if str(L) in gc else gc[L] for L in layers]
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    ax.axhline(0.5, color="0.7", lw=0.8, ls=":")
    ax.plot(layers, vals, "-o", color=C_ACC, ms=4)
    if p.get("best_layer"):
        bl = p["best_layer"]; y = bl.get("frac_toward", bl.get("gap_closed"))
        ax.scatter([bl["layer"]], [y], color="#C44E52", zorder=4,
                   label=f"peak: layer {bl['layer']}")
        ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("patched layer")
    ax.set_ylabel("frac. moved toward instruct")
    ax.set_ylim(0, 1)
    ax.set_title("Causal patching localizes the fix (P3)")
    save(fig, "fig_patch")


def fig_predictor(m):
    pr = m.get("predictor", {})
    pts = pr.get("points")
    if not pts:
        return
    fig, ax = plt.subplots(figsize=(3.6, 3.2))
    col = [C_BASE if k == "base" else C_INST for k in pts["kind"]]
    ax.scatter(pts["actual"], pts["predicted"], c=col, s=28, zorder=3)
    lo = min(min(pts["actual"]), min(pts["predicted"]))
    hi = max(max(pts["actual"]), max(pts["predicted"]))
    ax.plot([lo, hi], [lo, hi], "--", color="0.5", lw=1)
    ax.scatter([], [], color=C_BASE, label="base"); ax.scatter([], [], color=C_INST, label="instruct")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.set_xlabel(r"actual bias $\bar\Delta$"); ax.set_ylabel(r"predicted $\bar\Delta$")
    ax.set_title(f"Predicting bias from one forward pass\nLOO $R^2$={pr.get('loo_r2')}, r={pr.get('loo_pearson_r')}")
    save(fig, "fig_predictor")


PROBES = ["rubric_order", "score_id", "reference_answer"]


def fig_main(pi):
    """Main base-vs-instruct bar figure from the scaled per-item summary (all probes)."""
    s = pi["summary"]; probes = list(s.keys()); labels = [s[p]["label"] for p in probes]
    base = [s[p]["base_mean_delta"] for p in probes]
    inst = [s[p]["instruct_mean_delta"] for p in probes]
    fig, ax = plt.subplots(figsize=(5.6, 2.8)); x = range(len(probes)); w = 0.38
    ax.bar([i - w/2 for i in x], base, w, label="Base", color=C_BASE)
    ax.bar([i + w/2 for i in x], inst, w, label="Instruct", color=C_INST)
    for i, p in enumerate(probes):
        if s[p]["ci_excludes_zero"]:
            ax.text(i, max(base[i], inst[i]) + 0.03, "$*$", ha="center", fontsize=11)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel(r"Mean bias $\Delta$"); ax.legend(frameon=False, loc="upper right")
    ax.set_title(f"Scoring bias, base vs instruct ($n={pi['n_families']}$ families)")
    save(fig, "fig1_base_vs_instruct")


if __name__ == "__main__":
    pj = HERE / "results_peritem.json"
    if pj.exists():
        fig_main(json.loads(pj.read_text())); print("wrote fig1_base_vs_instruct")
    m = HERE / "results_mechanism.json"
    if m.exists():
        md = json.loads(m.read_text())
        fig_mech(md); print("wrote fig_mech")
        fig_predictor(md); print("wrote fig_predictor")
    pp = HERE / "patch_results.json"
    if pp.exists():
        fig_patch(json.loads(pp.read_text())); print("wrote fig_patch")
