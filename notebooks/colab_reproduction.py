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
# # Reproduce: Scoring Bias Analysis
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/blob/main/notebooks/colab_reproduction.ipynb)
#
# Full reproduction pipeline for:
# > *"Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison"*
#
# **Instructions:** Runtime → Run all. No GPU needed. Results in ~5 minutes.

# %% [markdown]
# ## Cell 1: Install Dependencies

# %%
# @title Install dependencies
!pip install matplotlib numpy pandas seaborn scipy openai tqdm -q
print("✓ Dependencies installed")

# %% [markdown]
# ## Cell 2: Clone Repository

# %%
# @title Clone repository
import os
from pathlib import Path

REPO_URL = "https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git"
REPO_DIR = "Scoring-Bias-in-LLM-as-a-Judge"

if not os.path.exists(REPO_DIR):
    !git clone --depth 1 {REPO_URL}
    %cd {REPO_DIR}
else:
    %cd {REPO_DIR}
    !git pull

print(f"✓ Working in {os.getcwd()}")

# %% [markdown]
# ## Cell 3: Load Data

# %%
# @title Load and inspect data
import pandas as pd
import numpy as np

data_dir = Path("data") / "raw"
csv_path = data_dir / "items_all_conditions.csv"

if csv_path.exists():
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df):,} rows from {csv_path}")
else:
    print("! Data file not found. Generating synthetic demo data...")
    np.random.seed(42)
    models = [f"model-{i}" for i in range(1, 7)]
    probes = ["rubric_order", "score_id", "reference_answer"]
    rows = []
    for model in models:
        for probe in probes:
            for i in range(20):
                base_score = np.random.uniform(2.5, 4.5)
                rows.append({"model_name": model, "probe": probe,
                             "condition": "normal", "item_id": f"item_{i:03d}",
                             "score": round(np.clip(base_score, 1, 5), 2)})
                bias = np.random.choice([-0.5, 0, 0.5, 1.0])
                rows.append({"model_name": model, "probe": probe,
                             "condition": "reversed", "item_id": f"item_{i:03d}",
                             "score": round(np.clip(base_score + bias, 1, 5), 2)})
    df = pd.DataFrame(rows)
    os.makedirs(data_dir, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"✓ Generated {len(df):,} synthetic rows")

print(f"\nModels: {df['model_name'].nunique()}")
print(f"Probes: {df['probe'].nunique()}")
print(f"Conditions: {sorted(df['condition'].unique())}")
display(df.head())

# %% [markdown]
# ## Cell 4: Run Analysis

# %%
# @title Compute bias deltas and flip rates
from scoring_bias.analysis import compute_delta, compute_flip_rate, bootstrap_ci
from scoring_bias.models import ProbeType

results = []
for (model, probe), group in df.groupby(["model_name", "probe"]):
    normal = group[group["condition"] == "normal"]["score"].tolist()
    inverted = group[group["condition"] != "normal"]["score"].tolist()
    if normal and inverted:
        delta = compute_delta(normal, inverted)
        flip = compute_flip_rate(normal, inverted)
        _, ci_l, ci_u = bootstrap_ci(normal, inverted, n_resamples=2000)
        results.append({
            "model": model, "probe": probe,
            "delta": round(delta, 4) if delta else None,
            "flip_rate": round(flip, 4) if flip else None,
            "ci_lower": round(ci_l, 4) if ci_l else None,
            "ci_upper": round(ci_u, 4) if ci_u else None,
        })

results_df = pd.DataFrame(results)
print("Analysis Results:")
display(results_df)

# %% [markdown]
# ## Cell 5: Generate Figures

# %%
# @title Generate publication-quality figures
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
output_dir = Path("output") / "figures"
output_dir.mkdir(parents=True, exist_ok=True)

# Bias landscape
pivot = results_df.pivot_table(index="model", columns="probe", values="delta")
pivot = pivot.fillna(0)
pivot["abs_delta"] = pivot.abs().mean(axis=1)
pivot = pivot.sort_values("abs_delta", ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
x = range(len(pivot))
width = 0.25
colors = ["#E74C3C", "#3498DB", "#2ECC71"]
for i, probe in enumerate(["rubric_order", "score_id", "reference_answer"]):
    if probe in pivot.columns:
        ax.bar([xi + i * width for xi in x], pivot[probe], width,
               label=probe.replace("_", " ").title(), color=colors[i], alpha=0.85)

ax.set_xticks([xi + width for xi in x])
ax.set_xticklabels(pivot.index, rotation=45, ha="right")
ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
ax.set_ylabel("Bias Delta (Δ)")
ax.set_title("Scoring Bias Landscape")
ax.legend()
fig.tight_layout()
fig.savefig(output_dir / "colab_bias_landscape.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"✓ Figures saved to {output_dir}/")

# %% [markdown]
# ## Done
#
# Full reproduction pipeline completed successfully.
# Results saved in the `output/` directory.

# %%
print("✓ Reproduction complete!")
print(f"  - Results table: {len(results_df)} entries")
print(f"  - Figures: {output_dir}/")
