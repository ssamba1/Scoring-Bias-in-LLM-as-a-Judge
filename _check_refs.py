#!/usr/bin/env python3
"""Check conclusion refs."""
import re

with open(r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex') as f:
    content = f.read()

# Find all \ref{} in the paper
refs = set(re.findall(r'\\ref\{([^}]+)\}', content))
# Find all \label{} in the paper
labels = set(re.findall(r'\\label\{([^}]+)\}', content))

missing = refs - labels
print(f"Total \\ref calls: {len(refs)}")
print(f"Total \\label definitions: {len(labels)}")
print(f"Missing labels (\\ref without \\label): {len(missing)}")
if missing:
    for m in sorted(missing):
        print(f"  {m}")
