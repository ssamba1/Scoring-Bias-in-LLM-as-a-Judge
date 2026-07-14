#!/usr/bin/env python3
"""Quick analysis from printed output data.
Computes per-probe deltas, generates paper tables.
"""
import json, statistics
from pathlib import Path

DATA = Path(__file__).parent.parent / "results_rootcause" / "study1_results.json"
with open(DATA) as f:
    raw = json.load(f)

print("="*60)
print("QUICK ANALYSIS: 22 Models from Printed Output")
print("="*60)
print()

# Compute max delta per probe for each model
results = {}
for model_name, probes in raw.items():
    deltas = {}
    for probe_type, variants in probes.items():
        vals = list(variants.values())
        if len(vals) > 1:
            delta = max(abs(v - vals[0]) for v in vals[1:])
        else:
            delta = 0.0
        deltas[probe_type] = delta
    results[model_name] = deltas

# Aggregate
probes = ["rubric_order", "score_id", "reference_answer"]
probe_labels = ["Rubric Order", "Score ID", "Ref Answer"]
for probe, label in zip(probes, probe_labels):
    vals = [results[m][probe] for m in results]
    avg = statistics.mean(vals)
    stdev = statistics.stdev(vals) if len(vals) > 1 else 0
    print(f"  {label:<20} avg Δ = {avg:.2f} (σ = {stdev:.2f})")

print()
print("="*60)
print("PER-MODEL BIAS SCORES")
print("="*60)
print(f"\n{'Model':<25} {'Rubric':<10} {'ScoreID':<10} {'RefAns':<10}")
print("-"*55)
for model_name in sorted(results.keys()):
    r = results[model_name]["rubric_order"]
    s = results[model_name]["score_id"]
    ref = results[model_name]["reference_answer"]
    print(f"{model_name:<25} {r:<10.2f} {s:<10.2f} {ref:<10.2f}")

# Write summary to JSON for paper
summary = {}
for probe, label in zip(probes, probe_labels):
    vals = [results[m][probe] for m in results]
    summary[probe] = {
        "mean": round(statistics.mean(vals), 2),
        "stdev": round(statistics.stdev(vals), 2) if len(vals) > 1 else 0,
        "min": round(min(vals), 2),
        "max": round(max(vals), 2)
    }
    label = probe
summary["model_count"] = len(results)

OUT = Path(__file__).parent.parent / "results_rootcause" / "quick_analysis.json"
with open(OUT, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved: {OUT}")
