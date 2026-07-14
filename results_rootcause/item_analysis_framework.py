#!/usr/bin/env python3
"""Item-level analysis framework.
Analyzes item difficulty, discrimination, dimensionality, and DIF.
Framework ready for when per-item scores are available.
"""
import json, math
from pathlib import Path

OUT = Path(__file__).parent.parent / "results_rootcause" / "item_analysis_framework.json"

print("=" * 60)
print("ITEM ANALYSIS FRAMEWORK")
print("=" * 60)
print()
print("This framework runs when per-item score data is available.")
print("Below: methodology specifications.")
print()

framework = {
    "item_difficulty": {
        "measure": "Mean score across all models for each item",
        "range": "1-5",
        "expected": "2.5-4.5 (avoid floor/ceiling)",
        "flag_below": 1.5,
        "flag_above": 4.5
    },
    "item_discrimination": {
        "measure": "Correlation between item score and total score (point-biserial)",
        "threshold": 0.3,
        "interpretation": "Items with r < 0.3 are poor discriminators"
    },
    "dimensionality": {
        "method": "Principal Component Analysis (PCA) on item scores",
        "expected": "1 factor (unidimensional bias)",
        "confirmation": "First eigenvalue > 2× second eigenvalue"
    },
    "local_independence": {
        "method": "Residual correlation matrix after factor extraction",
        "threshold": 0.2,
        "interpretation": "Residual correlations > 0.2 suggest local dependence"
    },
    "differential_item_functioning": {
        "method": "Compare item scores between RLHF and non-RLHF models",
        "threshold": "|Δ| > 0.5",
        "interpretation": "Items with DIF measure differently across model types"
    },
    "floor_ceiling": {
        "definition": "Floor: >15% of scores at minimum (1). Ceiling: >15% at maximum (5).",
        "impact": "Floor/ceiling items reduce variance and bias sensitivity",
        "action": "Flag items with >15% floor or ceiling for removal"
    },
    "test_information_function": {
        "method": "Item Response Theory (IRT) 2-parameter model",
        "output": "Test information across bias ability range",
        "interpretation": "Peak information at θ=0 indicates well-targeted test"
    }
}

for analysis, params in framework.items():
    print(f"  {analysis.replace('_', ' ').title()}")
    for key, value in params.items():
        print(f"    {key}: {value}")
    print()

with open(OUT, "w") as f:
    json.dump(framework, f, indent=2)
print(f"Saved: {OUT}")
print("Done.")
