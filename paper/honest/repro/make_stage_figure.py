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
COLORS = {"OLMo-2-1B": "#4878a8", "OLMo-2-7B": "#b04848", "Tulu-3-8B": "#508050"}

fig, axes = plt.subplots(1, 3, figsize=(9.6, 2.6))
panels = [("entropy", "(a) Decisiveness: entropy (bits)"),
          ("resp", "(b) Responsiveness: TV shift"),
          ("bias", "(c) Bias $\\Delta$")]
for ax, (key, title) in zip(axes, panels):
    for fam, t in traj.items():
        xs = [STAGES.index(s) for s in STAGES if s in t]
        ys = [t[s][key] for s in STAGES if s in t]
        ax.plot(xs, ys, "o-", color=COLORS[fam], label=fam, lw=1.6, ms=4)
    ax.set_xticks(range(4))
    ax.set_xticklabels(STAGES, fontsize=8)
    ax.set_title(title, fontsize=9)
axes[0].legend(frameon=False, fontsize=7.5)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
