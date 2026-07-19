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


def fig_mech(m):
    fig, ax = plt.subplots(1, 3, figsize=(9.2, 2.8))
    # (a) entropy base->instruct per family
    df = m["decisiveness_per_family"]
    for j, f in enumerate(df):
        ax[0].plot([0, 1], [df[f]["base"], df[f]["instruct"]], "-o", color="0.6", ms=4)
    ax[0].scatter([0]*len(df), [df[f]["base"] for f in df], color=C_BASE, zorder=3, label="base")
    ax[0].scatter([1]*len(df), [df[f]["instruct"] for f in df], color=C_INST, zorder=3, label="instruct")
    ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(["base", "instruct"])
    ax[0].set_ylabel("score entropy (bits)"); ax[0].set_title("(a) tuning sharpens (P1)")
    # (b) entropy vs bias scatter + fit
    lp = m["link_points"]; x = np.array(lp["entropy"]); y = np.array(lp["delta"])
    ax[1].scatter(x, y, s=12, alpha=0.5, color=C_ACC)
    if len(x) > 2:
        b, a = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 20)
        ax[1].plot(xs, a + b*xs, color="0.2", lw=1.2)
    r = m["entropy_bias_link"]
    ax[1].set_xlabel("score entropy (bits)"); ax[1].set_ylabel(r"bias $\Delta$")
    ax[1].set_title(f"(b) entropy predicts bias (P2)\n$\\rho$={r['spearman_rho']}, p={r['spearman_p']}")
    # (c) compliance mass base->instruct
    cf = m["compliance_per_family"]
    for f in cf:
        ax[2].plot([0, 1], [cf[f]["base"], cf[f]["instruct"]], "-o", color="0.6", ms=4)
    ax[2].scatter([0]*len(cf), [cf[f]["base"] for f in cf], color=C_BASE, zorder=3)
    ax[2].scatter([1]*len(cf), [cf[f]["instruct"] for f in cf], color=C_INST, zorder=3)
    ax[2].set_xticks([0, 1]); ax[2].set_xticklabels(["base", "instruct"])
    ax[2].set_ylabel("answer-token mass"); ax[2].set_title("(c) compliance rises")
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
    """Main base-vs-instruct bar figure from the scaled per-item summary."""
    s = pi["summary"]; labels = [s[p]["label"] for p in PROBES]
    base = [s[p]["base_mean_delta"] for p in PROBES]
    inst = [s[p]["instruct_mean_delta"] for p in PROBES]
    fig, ax = plt.subplots(figsize=(4.4, 2.8)); x = range(len(PROBES)); w = 0.38
    ax.bar([i - w/2 for i in x], base, w, label="Base", color=C_BASE)
    ax.bar([i + w/2 for i in x], inst, w, label="Instruct", color=C_INST)
    for i, p in enumerate(PROBES):
        if s[p]["ci_excludes_zero"]:
            ax.text(i, max(base[i], inst[i]) + 0.03, "$*$", ha="center", fontsize=11)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
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
