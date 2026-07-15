#!/usr/bin/env python3
"""Rebuild the paper with all fixes applied."""
# Read original, apply all fixes at Python level (no JSON escaping issues)

src = r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex'
with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Broken Table~ ref in Domain Analysis
content = content.replace(
    'Scoring bias varies across item domains. Table~\n ef{tab:domain} shows bias',
    'Scoring bias varies across item domains. Table~\\ref{tab:domain} shows bias'
)

# Fix 2: All broken Figure~ refs (various broken patterns after the binary fix and subsequent bad patches)
# The current state has a mix of broken patterns. Let's find and fix systematically.

# Check what we have
import re
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    s = line.strip()
    # Look for any 'ef{' that isn't a proper \ref or \label
    if 'ef{' in s and '\\ref' not in s and '\\label' not in s:
        print(f'ISSUE Line {i}: {s[:80]}')

# Now apply targeted fixes
# Replace each mangled Figure~\n+ef{...} variant with proper Figure~\ref{...}
content = content.replace('Figure~\n ef{fig:domain_bias}', 'Figure~\\ref{fig:domain_bias}')
content = content.replace('Figure~\n ef{fig:error_analysis}', 'Figure~\\ref{fig:error_analysis}')
content = content.replace('Figure~\n ef{fig:item_analysis}', 'Figure~\\ref{fig:item_analysis}')
content = content.replace('Figure~\n ef{fig:item_discrimination}', 'Figure~\\ref{fig:item_discrimination}')

# Handle remaining issues with \nef{ patterns from JSON \r interpretation
# The text might have literal 0x0D (carriage return) characters from JSON parsing
content = content.replace('\r', '')  # Remove stray CR chars

with open(src, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(content)

print('Rebuild complete.')
