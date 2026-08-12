#!/usr/bin/env python3
"""Fix broken \ref patterns caused by line-ending issues."""
import re

path = r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix broken patterns: where \ref{tab:...} got split across lines
content = content.replace('Table~\n ef{tab:domain}', 'Table~\\ref{tab:domain}')
content = content.replace('Figure~\n ef{fig:domain_bias}', 'Figure~\\ref{fig:domain_bias}')
content = content.replace('Figure~\n ef{fig:error_analysis}', 'Figure~\\ref{fig:error_analysis}')
content = content.replace('Figure~\n ef{fig:item_analysis}', 'Figure~\\ref{fig:item_analysis}')
content = content.replace('Figure~\n ef{fig:item_discrimination}', 'Figure~\\ref{fig:item_discrimination}')

# Check for remaining issues
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('ef{') and '\\ref' not in stripped:
        print(f'PROBLEM LINE {i}: {stripped[:60]}')

with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(content)

print('Done fixing refs.')
