#!/usr/bin/env python3
"""Mixed-effects model for 44-family analysis.
Accounts for model family as random effect → proper statistical inference.
"""
import json, math
from pathlib import Path

print("="*60)
print("MIXED-EFFECTS MODEL — Template")
print("="*60)
print("""
This script implements a mixed-effects model for the 44-family experiment.
It accounts for:
- FIXED effects: training type (base vs instruct), bias probe
- RANDOM effects: model family (each family has its own intercept)
- COVARIATES: model size, model family architecture

Formula: score ~ training_type + probe + (1|family) + size + architecture

This is the standard analysis for papers with multiple model comparisons.
""")

# Template code
template = '''
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd

# Load data from study1_max_scale.json
with open("results_rootcause/study1_max_scale.json") as f:
    data = json.load(f)

# Reshape into long format for mixed-effects
rows = []
for model_name, results in data.items():
    if "error" in results:
        continue
    parts = model_name.rsplit("_", 1)
    family = parts[0]
    vtype = parts[1] if len(parts) > 1 else "unknown"
    
    for probe_type, probe_results in results.items():
        if not isinstance(probe_results, dict):
            continue
        for var_name, scores in probe_results.items():
            if isinstance(scores, list) and len(scores) > 0:
                for rep_idx, rep in enumerate(scores):
                    for item_idx, score in enumerate(rep):
                        rows.append({
                            "family": family,
                            "training": vtype,  # base or instruct
                            "probe": probe_type,
                            "variant": var_name,
                            "repeat": rep_idx,
                            "item": item_idx,
                            "score": score
                        })

df = pd.DataFrame(rows)
print(f"Data: {len(df)} rows, {df['family'].nunique()} families")

# Fit mixed-effects model
model = smf.mixedlm(
    "score ~ C(training) + C(probe) + C(training):C(probe)",
    df,
    groups=df["family"]
)
result = model.fit()
print(result.summary())

# Extract key findings
print("\\nKEY FINDINGS:")
print(f"  Base vs instruct effect: {result.params['C(training)[T.instruct]']:.3f}")
print(f"  p-value: {result.pvalues['C(training)[T.instruct]']:.4f}")
'''

print("To run after data is available:")
print(template)
print()
print("="*60)
print("BIAS CLUSTERING — Template")
print("="*60)

cluster_template = '''
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import json

# Load summary data
with open("results_rootcause/study1_max_scale/summary.json") as f:
    data = json.load(f)

# Build feature matrix: each model has [rubric_delta, score_delta, ref_delta]
families = []
features = []
for family, variants in data.get("per_family", {}).items():
    if "base" in variants and "instruct" in variants:
        b = variants["base"]
        i = variants["instruct"]
        vec = [
            i.get("rubric_order", {}).get("max_delta", 0) - b.get("rubric_order", {}).get("max_delta", 0),
            i.get("score_id", {}).get("max_delta", 0) - b.get("score_id", {}).get("max_delta", 0),
            i.get("reference_answer", {}).get("max_delta", 0) - b.get("reference_answer", {}).get("max_delta", 0),
        ]
        families.append(family)
        features.append(vec)

# PCA
X = StandardScaler().fit_transform(features)
pca = PCA(n_components=2)
coords = pca.fit_transform(X)

plt.figure(figsize=(10, 8))
plt.scatter(coords[:, 0], coords[:, 1], alpha=0.7)
for i, fam in enumerate(families):
    plt.annotate(fam, (coords[i, 0], coords[i, 1]), fontsize=6)
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
plt.title("Bias Profile PCA — 44 Families")
plt.savefig("paper/figures/study1/bias_clusters.png", dpi=150)
print("Saved: paper/figures/study1/bias_clusters.png")
print(f"Explained variance: {sum(pca.explained_variance_ratio_):.1%}")
'''

print(cluster_template)
print("="*60)
