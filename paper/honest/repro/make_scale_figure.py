"""Tuning effect against judge scale, with the 14B point shown for what it is.

Input : results_scaled.json (the 13-family panel), results_14b.json (the 4-bit
        extension), results_quantization.json (the control that interprets it)
Output: figures/fig_scale.pdf

The paper's scope rests on how the effect behaves with size, and no figure
showed it. The panel spans 0.1-8B and the only point above that is a 4-bit 14B
run, attenuated to +0.06. Until the quantization control was run, that point
could not be read at all: it was confounded by the one variable most likely to
shrink it. The control settles that -- 4-bit inflates the tuning delta by about
6% at 7B, so the attenuation is not an artefact of quantization -- and the point
becomes interpretable as a single unreplicated observation at one scale.

Plotting it is the honest way to show what the panel does and does not support:
a positive effect that is noisy across families, no clean trend within
0.1-8B, and one low point above it that a reader should weigh as one point.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "fig_scale.pdf"
PROBES = ["rubric_order", "score_id", "reference_answer", "authority", "verbosity"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def tuning_delta(record):
    arms = {}
    for kind in ("base", "instruct"):
        vals = []
        for probe in PROBES:
            means = [v["mean"] for v in record[kind][probe].values()]
            vals.append(max(means) - min(means))
        arms[kind] = sum(vals) / len(vals)
    return arms["instruct"] - arms["base"]


panel = json.loads((HERE / "results_scaled.json").read_text())["results"]
points = sorted((float(rec["params_b"]), fam, tuning_delta(rec))
                for fam, rec in panel.items())

ext = json.loads((HERE / "results_14b.json").read_text())["results"]["Qwen2.5-14B"]
ext_delta = tuning_delta(ext)

quant = json.loads((HERE / "results_quantization.json").read_text())
pct = quant["delta_change_pct"]

fig, ax = plt.subplots(figsize=(6.4, 3.2))
xs = [p[0] for p in points]
ys = [p[2] for p in points]
ax.axhline(0, color="#999999", lw=0.8, zorder=1)
ax.scatter(xs, ys, s=34, color="#4878a8", zorder=3, label="panel (fp16), 13 families")
ax.scatter([14.0], [ext_delta], s=58, marker="D", facecolor="white",
           edgecolor="#b04848", lw=1.6, zorder=4,
           label="14B extension (4-bit), 1 family")

mean_panel = sum(ys) / len(ys)
ax.axhline(mean_panel, color="#4878a8", lw=0.9, ls="--", zorder=2)
ax.annotate(f"panel mean {mean_panel:+.2f}", xy=(0.13, mean_panel),
            xytext=(0, 4), textcoords="offset points", fontsize=7.5,
            color="#4878a8")
ax.annotate(f"4-bit inflates the delta by {pct:.0f}%\nat 7B, so this point is not\n"
            f"a quantization artefact",
            xy=(14.0, ext_delta), xytext=(-118, 26), textcoords="offset points",
            fontsize=7.2, color="#b04848",
            arrowprops=dict(arrowstyle="->", color="#b04848", lw=0.8))

ax.set_xscale("log")
ax.set_xlabel("judge size (billions of parameters, log scale)")
ax.set_ylabel(r"tuning effect: $\Delta_{\mathrm{instruct}}-\Delta_{\mathrm{base}}$")
ax.set_title("The tuning effect against scale", fontsize=9)
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
fig.tight_layout()
for ext_name in ("pdf", "png"):
    fig.savefig(OUT.with_suffix("." + ext_name))
print("wrote fig_scale")
