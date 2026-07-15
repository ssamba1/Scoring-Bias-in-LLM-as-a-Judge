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
# # 01  Data Overview
#
# Load and explore the scoring bias dataset.
#
# **Paper:** *Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison*
#
# This notebook loads the experimental data and produces summary statistics
# describing the models, probes, conditions, and score distributions.

# %% [markdown]
# ## Setup

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

# %%
# Locate data
DATA_DIR = Path("..") / "data" / "raw"
CSV_PATH = DATA_DIR / "items_all_conditions.csv"

if CSV_PATH.exists():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows from {CSV_PATH}")
else:
    print(f"Data file not found: {CSV_PATH}")
    print("Using synthetic demo data instead.")
    # Create synthetic demo data
    np.random.seed(42)
    models = ["llama-3.1-8b", "llama-3.1-8b-it", "gemma-2-27b", "gemma-2-27b-it"]
    probes = ["rubric_order", "score_id", "reference_answer"]
    conditions = ["normal", "reversed"]
    rows = []
    for model in models:
        for probe in probes:
            for cond in conditions:
                for i in range(20):
                    mean_score = 3.5 if cond == "normal" else 4.0
                    score = np.clip(np.random.normal(mean_score, 0.5), 1.0, 5.0)
                    rows.append({
                        "model_name": model,
                        "probe": probe,
                        "condition": cond,
                        "item_id": f"item_{i:03d}",
                        "score": round(score, 2),
                    })
    df = pd.DataFrame(rows)
    print(f"Generated {len(df):,} synthetic rows")

# %% [markdown]
# ## Data Shape

# %%
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nModels: {sorted(df['model_name'].unique())}")
print(f"Probes: {sorted(df['probe'].unique())}")
print(f"Conditions: {sorted(df['condition'].unique())}")

# %%
df.head(10)

# %% [markdown]
# ## Summary Statistics

# %%
summary = df.groupby(["model_name", "probe", "condition"])["score"].describe()
summary

# %%
# Overall score distribution
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, probe in zip(axes, df["probe"].unique()):
    subset = df[df["probe"] == probe]
    for cond in subset["condition"].unique():
        sns.kdeplot(subset[subset["condition"] == cond]["score"],
                    label=cond, ax=ax, fill=True, alpha=0.3)
    ax.set_title(f"Probe: {probe}")
    ax.set_xlabel("Score")
    ax.legend()
fig.suptitle("Score Distributions by Probe and Condition", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.savefig("../output/figures/data_overview_scores.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Model Counts

# %%
models_per_family = df["model_name"].apply(lambda x: x.split("-")[0] if "-" in x else x)
print("Models per family:")
print(models_per_family.value_counts())

# %% [markdown]
# ## Missing Data Check

# %%
missing = df.isnull().sum()
print("Missing values per column:")
print(missing[missing > 0] if missing.any() else "  No missing values found.")

# %% [markdown]
# ## Key Observations
#
# - **N models:** {len(df['model_name'].unique())}
# - **N probes:** {len(df['probe'].unique())}
# - **Conditions:** {list(df['condition'].unique())}
# - **Score range:** {df['score'].min():.1f} – {df['score'].max():.1f}
# - **Missing data:** {df.isnull().sum().sum()} cells

# %%
print("Data overview complete.")
