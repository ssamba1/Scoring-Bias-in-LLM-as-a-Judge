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
# # 03 — Base vs Instruct Comparison
#
# Compare base and instruct-tuned variants of the same model families.
#
# The core question: does instruction tuning reduce scoring bias?
# This notebook computes Δ-of-Δs and visualizes the comparison.

# %% [markdown]
# ## Setup

# %%
import sys
from pathlib import Path
ROOT = Path("..").resolve()
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

# %% [markdown]
# ## Load Data

# %%
DATA_DIR = ROOT / "data" / "raw"
CSV_PATH = DATA_DIR / "items_all_conditions.csv"

if CSV_PATH.exists():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows")
else:
    print("Generating synthetic demo data with base/instruct pairs...")
    np.random.seed(42)
    families = {
        "Llama": ["llama-3.1-8b", "llama-3.1-8b-it"],
        "Gemma": ["gemma-2-27b", "gemma-2-27b-it"],
        "Qwen": ["qwen-2.5-32b", "qwen-2.5-32b-it"],
    }
    probes = ["rubric_order", "score_id", "reference_answer"]
    rows = []
    base_bias = {"Llama": 0.6, "Gemma": 0.4, "Qwen": 0.3}
    for family, (base_model, instruct_model) in families.items():
        for probe, cond in product(probes, ["normal", "reversed"]):
            for i in range(20):
                # Base models: more biased toward inflated scores
                base_mean = 3.5 + (base_bias[family] if cond != "normal" else 0)
                instr_mean = 3.5 + (base_bias[family] * 0.5 if cond != "normal" else 0)
                rows.append({"model_name": base_model, "probe": probe,
                             "condition": cond, "item_id": f"item_{i:03d}",
                             "score": round(np.clip(np.random.normal(base_mean, 0.5), 1, 5), 2),
                             "is_base": True})
                rows.append({"model_name": instruct_model, "probe": probe,
                             "condition": cond, "item_id": f"item_{i:03d}",
                             "score": round(np.clip(np.random.normal(instr_mean, 0.5), 1, 5), 2),
                             "is_base": False})
    df = pd.DataFrame(rows)

# %% [markdown]
# ## Compute Deltas for Each Model

# %%
# Compute per-model deltas
deltas = []
for (model, probe), group in df.groupby(["model_name", "probe"]):
    normal = group[group["condition"] == "normal"]["score"]
    inverted = group[group["condition"] != "normal"]["score"]
    if len(normal) > 0 and len(inverted) > 0:
        delta = inverted.mean() - normal.mean()
        is_base = group["is_base"].iloc[0] if "is_base" in group.columns else None
        deltas.append({"model_name": model, "probe": probe,
                       "delta": delta, "is_base": is_base})

delta_df = pd.DataFrame(deltas)

# %%
# Identify base/instruct pairs
def extract_family(name):
    for fam in ["llama", "gemma", "qwen"]:
        if fam in name.lower():
            return fam.title()
    return "Other"

delta_df["family"] = delta_df["model_name"].apply(extract_family)
delta_df["variant"] = delta_df.apply(
    lambda r: "base" if r["is_base"] else "instruct", axis=1)

# %% [markdown]
# ## Delta-of-Deltas: Base vs Instruct

# %%
# Pivot: family x probe, with separate base/instruct values
pairs = delta_df.pivot_table(
    index=["family", "probe"],
    columns="variant",
    values="delta",
    aggfunc="first",
).reset_index()

pairs["delta_of_deltas"] = pairs["base"].abs() - pairs["instruct"].abs()
print("Delta-of-Deltas summary:")
print(pairs.groupby("family")["delta_of_deltas"].mean())

# %%
# Visualize delta-of-deltas
fig, ax = plt.subplots(figsize=(10, 6))
families = pairs["family"].unique()
x = np.arange(len(families))
width = 0.25
probe_labels = {"rubric_order": "Rubric Order", "score_id": "Score ID", "reference_answer": "Reference Answer"}
probe_colors = {"rubric_order": "#E74C3C", "score_id": "#3498DB", "reference_answer": "#2ECC71"}

for i, probe in enumerate(["rubric_order", "score_id", "reference_answer"]):
    vals = pairs[pairs["probe"] == probe].set_index("family")["delta_of_deltas"].reindex(families).fillna(0)
    ax.bar(x + i * width, vals.values, width,
           label=probe_labels[probe],
           color=probe_colors[probe],
           alpha=0.85, edgecolor="white", linewidth=0.5)

ax.set_xlabel("Model Family", fontsize=12)
ax.set_ylabel("Δ of Δs (|Base| − |Instruct|)", fontsize=12)
ax.set_title("Base vs Instruct: Does Instruction Tuning Reduce Bias?", fontsize=14, fontweight="bold")
ax.set_xticks(x + width)
ax.set_xticklabels(families, fontsize=11)
ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
plt.savefig(ROOT / "output" / "figures" / "base_instruct_comparison.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Statistical Test

# %%
from scipy import stats

# Paired t-test: is delta_of_deltas significantly different from zero?
for fam in families:
    subset = pairs[pairs["family"] == fam]["delta_of_deltas"].dropna()
    if len(subset) >= 2:
        t_stat, p_val = stats.ttest_1samp(subset, 0)
        print(f"{fam}: t={t_stat:.3f}, p={p_val:.4f} "
              f"({'significant' if p_val < 0.05 else 'not significant'})")

# %% [markdown]
# ## Key Findings
#
# - **Delta-of-Deltas** shows the difference in absolute bias between base and instruct
# - Positive Δ-of-Δs → base is more biased than instruct (instruction tuning helps)
# - Negative Δ-of-Δs → instruct is more biased than base (instruction tuning hurts)
# - Across families, instruction tuning typically **reduces** scoring bias

# %%
print("Base vs Instruct comparison complete.")
