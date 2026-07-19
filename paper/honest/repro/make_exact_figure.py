"""Appendix figure: exact tilted score change vs the first-order bound.
Input : results_robustness.json (E4 block)
Output: figures/fig_exact.pdf
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_exact.pdf"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

cur = json.loads((HERE / "results_robustness.json").read_text())["E4_exact_vs_first_order"]
fig, ax = plt.subplots(figsize=(4.6, 3.0))
colors = {"base": "#4878a8", "instruct": "#b04848"}
for kind, c in cur.items():
    ax.plot(c["t"], c["exact"], "o-", color=colors[kind], lw=1.6, ms=3.5,
            label=f"{kind}: exact (Var$^{{1/2}}$={c['sqrtvar']})")
    ax.plot(c["t"], c["first_order"], "--", color=colors[kind], lw=1.1, alpha=0.6,
            label=f"{kind}: first-order $t\\,\\mathrm{{Var}}_\\sigma(v)$")
ax.set_xlabel("tilt magnitude $t$ (worst-case direction $\\delta = t\\,v$)")
ax.set_ylabel("score change $s(\\ell + t v) - s(\\ell)$")
ax.legend(frameon=False, fontsize=7.5)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
