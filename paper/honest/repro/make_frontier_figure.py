"""Frontier scatter: entropy vs bias, open panel + frontier judges.
Inputs : results_scaled.json, results_closed.json
Output : figures/fig_frontier.pdf
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_frontier.pdf"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}

scaled = json.loads((HERE / "results_scaled.json").read_text())["results"]
closed = json.loads((HERE / "results_closed.json").read_text())["results"]
ana = json.loads((HERE / "results_closed_analysis.json").read_text())

ox, oy = [], []
for fam, rec in scaled.items():
    for kind in ("base", "instruct"):
        kd = rec.get(kind)
        if not isinstance(kd, dict):
            continue
        for p in CONTROL:
            if p not in kd:
                continue
            means = [v["mean"] for v in kd[p].values()]
            ox.append(float(np.mean([v["mean_entropy"] for v in kd[p].values()])))
            oy.append(max(means) - min(means))
fx, fy, fl = [], [], []
for m in ana["judges"]:
    for p, variants in closed[m]["instruct"].items():
        means = [v["mean"] for v in variants.values()]
        fx.append(float(np.mean([v["mean_entropy"] for v in variants.values()])))
        fy.append(max(means) - min(means))
        fl.append(m)

fig, ax = plt.subplots(figsize=(5.2, 3.4))
ax.scatter(ox, oy, s=18, color="#8898a8", alpha=0.55, label="open 0.1–8B (130 cells)")
mk = {"gpt-4o-mini": ("o", "#b04848"), "gpt-4o": ("s", "#7a2020"),
      "llama-3.1-70b-instruct": ("D", "#d09040")}
for m, (marker, col) in mk.items():
    xs = [x for x, l in zip(fx, fl) if l == m]
    ys = [y for y, l in zip(fy, fl) if l == m]
    ax.scatter(xs, ys, s=42, marker=marker, color=col, edgecolor="k",
               linewidth=0.4, label=m, zorder=3)
rho = ana["pooled"]["pooled_rho"]
ax.set_xlabel("mean score-distribution entropy (bits)")
ax.set_ylabel(r"bias $\Delta$")
ax.set_title(f"Confidence vs bias, open panel + frontier judges "
             f"(pooled $\\rho={rho}$, $n={ana['pooled']['n_pooled']}$)", fontsize=9)
ax.legend(frameon=False, fontsize=7.2, loc="upper right")
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
