# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 02  Bias Landscape
#
# Visualize the scoring bias landscape across all models and probes.
#
# This notebook computes bias deltas (Δ = treatment − control) and produces
# the core figures for the paper: the bias landscape bar chart, flip rates,
# and probe-level breakdowns.

# %% [markdown]
# ## Setup

# %%
import sys
from pathlib import Path

# Ensure scoring_bias package is importable
ROOT = Path("..").resolve()
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

# %% [markdown]
# ## Load & Prepare Data

# %%
DATA_DIR = ROOT / "data" / "raw"
CSV_PATH = DATA_DIR / "items_all_conditions.csv"

if CSV_PATH.exists():
    df = pd.read_csv(CSV_PATH)
else:
    print("Using synthetic demo data.")
    np.random.seed(42)
    models = ["llama-3.1-8b", "llama-3.1-8b-it", "gemma-2-27b", "gemma-2-27b-it",
              "qwen-2.5-32b", "qwen-2.5-32b-it"]
    probes = ["rubric_order", "score_id", "reference_answer"]
    rows = []
    for model in models:
        for probe in probes:
            for cond in ["normal", "reversed"]:
                for i in range(20):
                    mean_s = 3.5 if cond == "normal" else (3.5 + np.random.choice([-0.5, 0, 0.5, 1.0]))
                    score = np.clip(np.random.normal(mean_s, 0.5), 1.0, 5.0)
                    rows.append({"model_name": model, "probe": probe,
                                 "condition": cond, "item_id": f"item_{i:03d}",
                                 "score": round(score, 2)})
    df = pd.DataFrame(rows)

# %%
# Compute deltas per model-probe
deltas = []
for (model, probe), group in df.groupby(["model_name", "probe"]):
    normal = group[group["condition"] == "normal"]["score"]
    inverted = group[group["condition"] != "normal"]["score"]
    if len(normal) > 0 and len(inverted) > 0:
        delta = inverted.mean() - normal.mean()
        deltas.append({"model_name": model, "probe": probe, "delta": delta})

delta_df = pd.DataFrame(deltas)
print("Delta range: {:.3f} to {:.3f}".format(delta_df["delta"].min(), delta_df["delta"].max()))

# %% [markdown]
# ## Bias Landscape Figure

# %%
# Pivot for plotting: models as rows, probes as columns
pivot = delta_df.pivot_table(index="model_name", columns="probe", values="delta")
pivot["avg_abs_delta"] = pivot.abs().mean(axis=1)
pivot = pivot.sort_values("avg_abs_delta", ascending=False)

fig, ax = plt.subplots(figsize=(14, 7))
x = np.arange(len(pivot))
width = 0.25
colors = {"rubric_order": "#E74C3C", "score_id": "#3498DB", "reference_answer": "#2ECC71"}

for i, probe in enumerate(["rubric_order", "score_id", "reference_answer"]):
    if probe in pivot.columns:
        vals = pivot[probe].fillna(0)
        ax.bar(x + i * width, vals, width,
               label=probe.replace("_", " ").title(),
               color=colors.get(probe, "#95A5A6"),
               alpha=0.85, edgecolor="white", linewidth=0.5)

ax.set_xlabel("Model", fontsize=12)
ax.set_ylabel("Bias Delta (Δ)", fontsize=12)
ax.set_title("Scoring Bias Landscape", fontsize=14, fontweight="bold")
ax.set_xticks(x + width)
ax.set_xticklabels(pivot.index, rotation=45, ha="right", fontsize=9)
ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
plt.savefig(ROOT / "output" / "figures" / "bias_landscape.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Flip Rates

# %%
# Compute flip rates
flip_rates = []
for (model, probe), group in df.groupby(["model_name", "probe"]):
    normal = group[group["condition"] == "normal"]["score"].values
    inverted = group[group["condition"] != "normal"]["score"].values
    if len(normal) > 0 and len(inverted) > 0 and len(normal) == len(inverted):
        flips = np.sum(np.abs(normal - inverted) >= 0.5) / len(normal)
        flip_rates.append({"model_name": model, "probe": probe, "flip_rate": flips})

flip_df = pd.DataFrame(flip_rates)
pivot_flip = flip_df.pivot_table(index="model_name", columns="probe", values="flip_rate")
pivot_flip = pivot_flip.fillna(0)

fig, ax = plt.subplots(figsize=(14, 7))
for i, probe in enumerate(["rubric_order", "score_id", "reference_answer"]):
    if probe in pivot_flip.columns:
        ax.bar(x + i * width, pivot_flip[probe], width,
               label=probe.replace("_", " ").title(),
               color=colors.get(probe, "#95A5A6"),
               alpha=0.85, edgecolor="white", linewidth=0.5)

ax.set_xlabel("Model", fontsize=12)
ax.set_ylabel("Flip Rate", fontsize=12)
ax.set_title("Score Flip Rates", fontsize=14, fontweight="bold")
ax.set_xticks(x + width)
ax.set_xticklabels(pivot_flip.index, rotation=45, ha="right", fontsize=9)
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
plt.savefig(ROOT / "output" / "figures" / "flip_rates.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Key Findings
#
# - Models with the largest |Δ|: models at the top of the landscape plot
# - Models with the smallest |Δ|: models at the bottom
# - Rubric order tends to show the most consistent bias across models
# - Some models show **leniency bias** (Δ > 0), others show **strictness bias** (Δ < 0)

# %%
print("Bias landscape analysis complete.")
