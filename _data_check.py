#!/usr/bin/env python3
"""Detailed data integrity checks."""
import json
import os

PROJECT = r'C:\Users\Admin\Research\research-draft'

files = {
    't4fam_results.json': os.path.join(PROJECT, 'results_rootcause', 't4fam_results.json'),
    'study1_results.json': os.path.join(PROJECT, 'results_rootcause', 'study1_results.json'),
    'rootcause_analysis.json': os.path.join(PROJECT, 'results_rootcause', 'rootcause_analysis.json'),
}

all_names = {}
for name, path in files.items():
    with open(path) as f:
        data = json.load(f)
    models = list(data.keys())
    print(f"{name}: {len(models)} models")
    for m in sorted(models):
        val = data[m]
        if isinstance(val, dict):
            # Check for nested model info
            if 'probe_scores' in val or 'scores' in val or 'mean_scores' in val:
                all_names[m] = name
            elif any(k in val for k in ['rubric_order', 'score_id', 'reference_answer', 'probes']):
                all_names[m] = name
            else:
                all_names[m] = name
        else:
            all_names[m] = name

print(f"\nAll unique model/entity keys across files:")
for m in sorted(all_names):
    print(f"  {m} ({all_names[m]})")

# Count unique models (remove -IT, -Instruct suffixes for dedup)
import re
base_names = set()
for m in all_names:
    base = re.sub(r'-(IT|Instruct|it)$', '', m, flags=re.IGNORECASE)
    base_names.add(base)
print(f"\nUnique base model names (stripped variant suffix): {len(base_names)}")
for b in sorted(base_names):
    print(f"  {b}")

# Estimate total judgments
# t4fam: 14 models x 3 probes x 3 variants x 50 items x 3 repeats (but some are base/instruct pairs only)
# Actually let me check structure
for name, path in files.items():
    with open(path) as f:
        data = json.load(f)
    # Check first model's structure
    first_model = list(data.keys())[0]
    val = data[first_model]
    print(f"\n{name}: {first_model} -> keys: {list(val.keys()) if isinstance(val, dict) else type(val).__name__}")
    if isinstance(val, dict) and 'probes' in val:
        print(f"  probes: {list(val['probes'].keys()) if isinstance(val['probes'], dict) else type(val['probes'])}")
