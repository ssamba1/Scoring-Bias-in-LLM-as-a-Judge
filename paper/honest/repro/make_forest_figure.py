"""Forest plot: per-family instruct-base bias change with probe-resampled 95% CIs.
Input : results_robustness.json (F2 block)
Output: figures/fig_forest.pdf
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_forest.pdf"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

d = json.loads((HERE / "results_robustness.json").read_text())
forest = d["F2_forest"]
perm_p = d["F1_exact_permutation"]["exact_p_two_sided"]
fams = sorted(forest, key=lambda f: forest[f]["params_b"] or 0)

fig, ax = plt.subplots(figsize=(5.4, 4.2))
ys = np.arange(len(fams))
for y, f in zip(ys, fams):
    e, (lo, hi) = forest[f]["effect"], forest[f]["ci"]
    color = "#b04848" if e > 0 else "#4878a8"
    ax.plot([lo, hi], [y, y], color=color, lw=1.6)
    ax.plot(e, y, "o", color=color, ms=5)
mean_eff = np.mean([forest[f]["effect"] for f in fams])
ax.axvline(0, color="k", lw=0.8)
ax.axvline(mean_eff, color="#b04848", lw=1.0, ls="--")
ax.text(mean_eff + 0.01, len(fams) - 0.4,
        f"mean {mean_eff:+.2f}\n(exact perm.\n$p={perm_p:.4f}$)", fontsize=7.5, color="#b04848")
ax.set_yticks(ys)
ax.set_yticklabels([f"{f} ({forest[f]['params_b']}B)" for f in fams], fontsize=8)
ax.set_xlabel("instruct $-$ base bias change (mean over 5 bias types)")
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
