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
# # Binder Demo: Scoring Bias Interactive Visualization
#
# [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/main?labpath=notebooks%2Fbinder_demo.ipynb)
#
# Interactive demo of the *Scoring Bias in LLM-as-a-Judge* analysis.
# Loads pre-computed data and generates interactive charts.

# %% [markdown]
# ## Setup

# %%
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, Dropdown, FloatSlider, VBox, HBox, Output
import matplotlib as mpl

mpl.rcParams["figure.dpi"] = 120

print("✓ Setup complete — interactive widgets are ready below.")

# %% [markdown]
# ## Load Pre-computed Data

# %%
# Look for pre-computed data, or generate demo data
data_file = Path("output") / "deltas.json"
if data_file.exists():
    with open(data_file) as f:
        deltas_data = json.load(f)
    df = pd.DataFrame(deltas_data)
    print(f"✓ Loaded {len(df)} pre-computed entries")
else:
    print("! Pre-computed data not found. Generating demo data...")
    np.random.seed(42)
    probes = ["rubric_order", "score_id", "reference_answer"]
    models = [("llama-3.1-8b", "Llama"), ("llama-3.1-8b-it", "Llama"),
              ("gemma-2-27b", "Gemma"), ("gemma-2-27b-it", "Gemma"),
              ("qwen-2.5-32b", "Qwen"), ("qwen-2.5-32b-it", "Qwen")]
    rows = []
    for model, family in models:
        for probe in probes:
            bias = np.random.choice([-0.5, -0.3, 0, 0.3, 0.5, 0.8])
            sd = abs(bias) * 0.15 + 0.05
            ci_l = bias - 1.96 * sd
            ci_u = bias + 1.96 * sd
            rows.append({
                "model_name": model, "probe": probe,
                "family": family,
                "delta": round(bias, 4),
                "flip_rate": round(np.random.uniform(0.1, 0.6), 4),
                "ci_lower": round(ci_l, 4),
                "ci_upper": round(ci_u, 4),
            })
    df = pd.DataFrame(rows)

# %% [markdown]
# ## Interactive Model Explorer

# %%
models = sorted(df["model_name"].unique())
probes_list = list(df["probe"].unique())

def plot_model(model_name):
    subset = df[df["model_name"] == model_name].copy()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Bar chart with CI
    colors = ["#E74C3C", "#3498DB", "#2ECC71"]
    for i, (_, row) in enumerate(subset.iterrows()):
        ax1.bar(i, row["delta"], color=colors[i], alpha=0.8, width=0.5)
        ax1.errorbar(i, row["delta"],
                     yerr=[[row["delta"] - row["ci_lower"]],
                           [row["ci_upper"] - row["delta"]]],
                     fmt="none", color="black", capsize=3)
    ax1.set_xticks(range(len(subset)))
    ax1.set_xticklabels(subset["probe"].str.replace("_", " ").str.title())
    ax1.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax1.set_ylabel("Bias Delta (Δ)")
    ax1.set_title(f"Delta with 95% CI: {model_name}")

    # Flip rates
    ax2.bar(range(len(subset)), subset["flip_rate"], color="#9B59B6", alpha=0.8, width=0.5)
    ax2.set_xticks(range(len(subset)))
    ax2.set_xticklabels(subset["probe"].str.replace("_", " ").str.title())
    ax2.set_ylabel("Flip Rate")
    ax2.set_title("Score Flip Rate")

    fig.tight_layout()
    plt.show()

interact(plot_model, model_name=Dropdown(options=models, description="Model:"));

# %% [markdown]
# ## Interactive Comparison Tool

# %%
def compare_models(model_a, model_b):
    subset = df[df["model_name"].isin([model_a, model_b])].copy()
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(probes_list))
    width = 0.35
    for i, model_name in enumerate([model_a, model_b]):
        model_data = subset[subset["model_name"] == model_name]
        deltas = [model_data[model_data["probe"] == p]["delta"].iloc[0] if len(model_data[model_data["probe"] == p]) > 0 else 0
                  for p in probes_list]
        ax.bar(x + i * width, deltas, width, label=model_name,
               alpha=0.8, edgecolor="white", linewidth=0.5)

    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([p.replace("_", " ").title() for p in probes_list])
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax.set_ylabel("Bias Delta (Δ)")
    ax.set_title("Model Comparison")
    ax.legend()
    fig.tight_layout()
    plt.show()

interact(compare_models,
         model_a=Dropdown(options=models, description="Model A:"),
         model_b=Dropdown(options=models, description="Model B:"));

# %% [markdown]
# ## Bias Landscape Overview

# %%
fig, ax = plt.subplots(figsize=(14, 6))
pivot = df.pivot_table(index="model_name", columns="probe", values="delta")
pivot["abs_delta"] = pivot.abs().mean(axis=1)
pivot = pivot.sort_values("abs_delta", ascending=False)

x = np.arange(len(pivot))
width = 0.25
colors = ["#E74C3C", "#3498DB", "#2ECC71"]
for i, probe in enumerate(probes_list):
    if probe in pivot.columns:
        ax.bar(x + i * width, pivot[probe].fillna(0), width,
               label=probe.replace("_", " ").title(),
               color=colors[i], alpha=0.85, edgecolor="white")

ax.set_xticks(x + width)
ax.set_xticklabels(pivot.index, rotation=45, ha="right")
ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
ax.set_ylabel("Bias Delta (Δ)")
ax.set_title("Full Bias Landscape — All Models and Probes")
ax.legend()
fig.tight_layout()
plt.show()

# %% [markdown]
# ## About This Demo
#
# This interactive notebook demonstrates the scoring bias analysis from:
# > *"Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison"*
#
# **Key features:**
# - **Model Explorer:** Select any model to see its per-probe delta values
# - **Comparison Tool:** Side-by-side comparison of any two models
# - **Landscape Overview:** Full bias landscape across all models and probes
#
# For the full paper and code, visit:
# [github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge](https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge)

# %%
print("✓ Binder demo ready! Use the interactive widgets above.")
