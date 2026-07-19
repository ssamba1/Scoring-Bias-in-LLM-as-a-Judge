"""Dose-response figure: the preregistered-failure step shape.
Input : results_dose_analysis.json
Output: figures/fig_dose.pdf
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_dose.pdf"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

cells = json.loads((HERE / "results_dose_analysis.json").read_text())["per_cell"]
fig, axes = plt.subplots(1, 2, figsize=(7.6, 2.7), sharey=True)
titles = {"verbosity": "(a) Verbosity dose (filler units 0/1/2/4/8)",
          "authority": "(b) Authority dose (framing strength 0--4)"}
colors = {"base": "#4878a8", "instruct": "#b04848"}
for ax, probe in zip(axes, ("verbosity", "authority")):
    for c in cells:
        if c["probe"] != probe:
            continue
        ax.plot(range(len(c["shifts"])), c["shifts"], "o-", lw=1.1, ms=3,
                color=colors[c["kind"]], alpha=0.55)
    ax.set_title(titles[probe], fontsize=9)
    ax.set_xlabel("dose level")
    ax.set_xticks(range(5))
axes[0].set_ylabel("|score shift| from dose 0")
handles = [plt.Line2D([], [], color=c, marker="o", lw=1.2, label=k)
           for k, c in colors.items()]
axes[0].legend(handles=handles, frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
