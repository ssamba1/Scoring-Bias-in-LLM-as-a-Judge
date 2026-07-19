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
    gc = p["per_layer_gap_closed"]
    layers = sorted(int(k) for k in gc)
    vals = [gc[str(L)] if str(L) in gc else gc[L] for L in layers]
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    ax.axhline(0, color="0.7", lw=0.8); ax.axhline(1, color="0.7", lw=0.8, ls=":")
    ax.plot(layers, vals, "-o", color=C_ACC, ms=4)
    if p.get("best_layer"):
        bl = p["best_layer"]
        ax.scatter([bl["layer"]], [bl["gap_closed"]], color="#C44E52", zorder=4,
                   label=f"best: L{bl['layer']} ({bl['gap_closed']:.0%})")
        ax.legend(frameon=False, fontsize=8)
    ax.set_xlabel("patched layer"); ax.set_ylabel("base$\\to$instruct gap closed")
    ax.set_title("Causal patching localizes the fix (P3)")
    save(fig, "fig_patch")


if __name__ == "__main__":
    m = HERE / "results_mechanism.json"
    p = HERE / "results_mechanism.json"  # placeholder guard
    if m.exists():
        fig_mech(json.loads(m.read_text()))
        print("wrote fig_mech")
    pp = HERE / "patch_results.json"
    if pp.exists():
        fig_patch(json.loads(pp.read_text()))
        print("wrote fig_patch")
