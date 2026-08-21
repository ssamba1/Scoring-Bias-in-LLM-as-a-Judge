"""Stage-ablation figure: entropy / responsiveness / bias across alignment stages.
Input : results_stages_analysis.json (from analyze_stages.py)
Output: figures/fig_stages.pdf
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_stages.pdf"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

traj = json.loads((HERE / "results_stages_analysis.json").read_text())["trajectories"]
STAGES = ["base", "SFT", "DPO", "RLVR"]
# Three series in one panel, so they must separate without colour. The green
# was #508050, which put red and green side by side as the only thing telling
# OLMo-2-7B from Tulu-3-8B -- the pair roughly one man in twelve cannot
# distinguish. Orange replaces it, and each series carries its own marker so
# the figure also survives greyscale printing.
COLORS = {"OLMo-2-1B": "#4878a8", "OLMo-2-7B": "#b04848", "Tulu-3-8B": "#d08030"}
MARKERS = {"OLMo-2-1B": "o", "OLMo-2-7B": "s", "Tulu-3-8B": "^"}

fig, axes = plt.subplots(1, 3, figsize=(9.6, 2.6))
panels = [("entropy", "(a) Decisiveness: entropy (bits)"),
          ("resp", "(b) Responsiveness: TV shift"),
          ("bias", "(c) Bias $\\Delta$")]
for ax, (key, title) in zip(axes, panels):
    for fam, t in traj.items():
        xs = [STAGES.index(s) for s in STAGES if s in t]
        ys = [t[s][key] for s in STAGES if s in t]
        ax.plot(xs, ys, marker=MARKERS[fam], linestyle="-", color=COLORS[fam],
                label=fam, lw=1.6, ms=4.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(STAGES, fontsize=8)
    ax.set_title(title, fontsize=9)
axes[0].legend(frameon=False, fontsize=7.5)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
