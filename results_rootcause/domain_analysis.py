#!/usr/bin/env python3
"""
Domain analysis  compute bias per domain (science, tech, humanities, daily, math).
Requires per-item scores (not just per-variant averages).
Needs: results_rootcause/12_families_results.json (from run_12_families.py) 
  or results_rootcause/study1_per_item.json (per-item breakdown from experiment)

Run after collecting per-item data.
"""
import json, statistics
from pathlib import Path

DOMAINS = {
    "science": list(range(1, 11)),
    "tech": list(range(11, 21)),
    "humanities": list(range(21, 31)),
    "daily_life": list(range(31, 41)),
    "math": list(range(41, 51)),
}

DATA = Path(__file__).parent.parent / "results_rootcause" / "12_families_results.json"
if not DATA.exists():
    print(f"ERROR: {DATA} not found.")
    print("Run pipeline_rootcause/run_12_families.py first to collect per-item data.")
    print("Or place study1_per_item.json in results_rootcause/")
    exit(1)

with open(DATA) as f:
    data = json.load(f)

print("DOMAIN ANALYSIS")
print("="*60)

for model_name, probes in data.items():
    print(f"\n{model_name}")
    for domain, items in DOMAINS.items():
        # Extract scores for items in this domain
        scores = {}
        for probe_type, variants in probes.items():
            for variant_name, item_scores in variants.items():
                domain_scores = [item_scores[i-1] for i in items if i <= len(item_scores)]
                if domain_scores:
                    key = f"{probe_type}_{variant_name}"
                    scores[key] = statistics.mean(domain_scores)
        
        # Compute delta for this domain
        rubric_normal = scores.get("rubric_order_normal", 0)
        rubric_reversed = scores.get("rubric_order_reversed", 0)
        rubric_delta = abs(rubric_normal - rubric_reversed)
        
        ref_no = scores.get("reference_answer_no_ref", 0)
        ref_good = scores.get("reference_answer_good_ref", 0)
        ref_delta = abs(ref_no - ref_good)
        
        print(f"  {domain:<15} rubric +{rubric_delta:.2f}  ref +{ref_delta:.2f}")

print("\nDONE.")
