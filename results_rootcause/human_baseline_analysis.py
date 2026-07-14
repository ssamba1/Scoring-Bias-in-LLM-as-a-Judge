#!/usr/bin/env python3
"""Human baseline analysis. Compare human vs model scores.
Expects data/human_baseline_scores.csv with columns: item_id,domain,rater1,rater2,rater3
"""
import json, statistics, sys
from pathlib import Path

BASE = Path(__file__).parent.parent
CSV = BASE / "data" / "human_baseline_scores.csv"
MODEL_DATA = BASE / "results_rootcause" / "study1_results.json"

if not CSV.exists():
    print("ERROR: Run human baseline first. Save scores to data/human_baseline_scores.csv")
    sys.exit(1)

# Load human scores
with open(CSV) as f:
    lines = f.read().strip().split("\n")[1:]  # skip header

humans = {}
for line in lines:
    parts = line.split(",")
    item_id = int(parts[0])
    domain = parts[1]
    scores = [int(x) for x in parts[2:5]]
    humans[item_id] = {"domain": domain, "mean": statistics.mean(scores), "stdev": statistics.stdev(scores)} 

print(f"Loaded {len(humans)} items from {len(set(h['domain'] for h in humans.values()))} domains")
print(f"Avg human score: {statistics.mean(h['mean'] for h in humans.values()):.2f}")
print(f"Human inter-rater SD: {statistics.mean(h['stdev'] for h in humans.values()):.2f}")

# Compare with model scores (which models score each item on normal rubric)
print("\n=== HUMAN vs MODEL COMPARISON ===")
# This analysis requires per-item model scores which are in the raw data
print("Per-item model scores needed for full comparison.")
print("Placeholder: human mean = %.2f" % statistics.mean(h['mean'] for h in humans.values()))

# Compute human bias: do humans show the same susceptibility?
print("\n=== HUMAN BIAS CHECK ===")
print("To measure human bias, show raters the same probe variants")
print("(reversed rubric, letter grades, etc.) and compare.") 
print("Currently: standard rubric only (control condition).")

print("\nDONE.")
