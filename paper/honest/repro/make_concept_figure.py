"""Concept figure: the decisiveness x responsiveness decomposition, schematically.

Left: a judge's score distribution; its mean is the score, its spread is
decisiveness. Middle: a nuisance shifts the logits; how far, is responsiveness.
Right: instruction tuning trims the first a little, inflates the second a lot.
Output: figures/fig_concept.pdf
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_concept.pdf"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

fig, axes = plt.subplots(1, 3, figsize=(9.6, 2.7))
vals = np.arange(1, 6)

# ---- (a) the score is the mean of a distribution ----
ax = axes[0]
p = np.array([0.10, 0.18, 0.34, 0.24, 0.14])
ax.bar(vals, p, color="#4878a8", width=0.62)
s = float((p * vals).sum())
ax.axvline(s, color="k", lw=1.4, ls="--")
ax.annotate(f"score $s=E_\\sigma[v]$", (s + 0.08, 0.345), fontsize=9)
ax.annotate("", xy=(s - 1.15, 0.06), xytext=(s + 1.15, 0.06),
            arrowprops=dict(arrowstyle="<->", color="#a04040", lw=1.3))
ax.text(s, 0.075, "decisiveness:\n$\\sqrt{\\mathrm{Var}_\\sigma(v)}$, $H(\\sigma)$",
        ha="center", fontsize=8, color="#a04040")
ax.set_xticks(vals); ax.set_ylim(0, 0.42)
ax.set_xlabel("answer token value $v_k$"); ax.set_ylabel("$\\sigma_k$")
ax.set_title("(a) A judge's score distribution", fontsize=9)

# ---- (b) a nuisance shifts the distribution ----
ax = axes[1]
q = np.array([0.05, 0.10, 0.24, 0.33, 0.28])
ax.bar(vals - 0.17, p, color="#4878a8", width=0.32, label="control")
ax.bar(vals + 0.17, q, color="#d09040", width=0.32, label="perturbed")
s2 = float((q * vals).sum())
ax.axvline(s, color="#4878a8", lw=1.2, ls="--")
ax.axvline(s2, color="#d09040", lw=1.2, ls="--")
ax.annotate("", xy=(s2, 0.40), xytext=(s, 0.40),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.4))
ax.text((s + s2) / 2, 0.415, "bias", ha="center", fontsize=9)
ax.text(4.15, 0.13, "responsiveness:\n$\\|\\delta_\\pi\\|$", ha="center",
        fontsize=8, color="#7a5010")
ax.set_xticks(vals); ax.set_ylim(0, 0.46)
ax.set_xlabel("answer token value $v_k$"); ax.legend(frameon=False, fontsize=7.5, loc="upper left")
ax.set_title("(b) A nuisance moves the mean", fontsize=9)

# ---- (c) what instruction tuning does to each term ----
ax = axes[2]
terms = ["decisiveness\n(spread)", "responsiveness\n(nuisance shift)", "bias\n(product)"]
base_v = [1.0, 1.0, 1.0]
inst_v = [0.71, 1.73, 1.59]   # entropy 2.04->1.45 bits; TV .15->.26; mean Delta x1.59
x = np.arange(3)
ax.bar(x - 0.17, base_v, width=0.32, color="#808898", label="base")
ax.bar(x + 0.17, inst_v, width=0.32, color="#b04848", label="instruct")
for xi, (b, i) in enumerate(zip(base_v, inst_v)):
    ax.annotate("", xy=(xi + 0.17, i), xytext=(xi + 0.17, b),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.1))
ax.axhline(1.0, color="k", lw=0.6, ls=":")
ax.set_xticks(x); ax.set_xticklabels(terms, fontsize=8)
ax.set_ylabel("relative to base")
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
ax.set_title("(c) Tuning trims one, inflates the other", fontsize=9)

fig.tight_layout()
OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
