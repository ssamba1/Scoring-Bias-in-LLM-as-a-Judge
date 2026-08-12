#!/usr/bin/env python3
"""Final validation of the paper."""
import re

path = r'C:\Users\Admin\Research\research-draft\paper\camera_ready_full.tex'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print('=== PAPER STATISTICS ===')
print(f'Lines: {len(lines)}')
print(f'Characters: {len(content)}')

# Count figures
fig_includes = re.findall(r'\\includegraphics\[.*?\]\{(.*?)\}', content)
print(f'\n=== FIGURES ({len(fig_includes)}) ===')
for i, f in enumerate(fig_includes, 1):
    print(f'  {i}. {f}')

# Count figure environments
fig_envs = re.findall(r'\\begin\{figure\*?\}', content)
print(f'\nFigure environments: {len(fig_envs)}')

# Count figure labels
fig_labels = re.findall(r'\\label\{fig:([^}]+)\}', content)
print(f'\n=== FIGURE LABELS ({len(fig_labels)}) ===')
for lbl in fig_labels:
    print(f'  fig:{lbl}')

# Count tables
tab_envs = re.findall(r'\\begin\{table\*?\}', content)
print(f'\nTable environments: {len(tab_envs)}')

tab_labels = re.findall(r'\\label\{tab:([^}]+)\}', content)
print(f'\n=== TABLE LABELS ({len(tab_labels)}) ===')
for lbl in tab_labels:
    print(f'  tab:{lbl}')

# Check all \ref targets
refs = re.findall(r'\\ref\{([^}]+)\}', content)
labels = re.findall(r'\\label\{([^}]+)\}', content)
print(f'\n=== CROSS-REFERENCE AUDIT ===')
print(f'Total \\ref calls: {len(refs)}')
print(f'Total \\label definitions: {len(labels)}')

label_set = set(labels)
broken = [r for r in refs if r not in label_set]
if broken:
    print(f'\n!!! BROKEN REFERENCES: {len(broken)}')
    for b in broken:
        print(f'  MISSING: {b}')
else:
    print('All references valid!')

# Check each figure's figX naming
expected_figs = [f'fig{i}' for i in range(1, 21)]
fig_labels_only = [l for l in fig_labels if l.startswith('fig')]
# Check if it starts with a number prefix
named_figs = set()
for fl in fig_labels_only:
    named_figs.add(fl)

print(f'\n=== KEY FIGURES CHECK ===')
found_count = 0
for i in range(1, 21):
    # Check various naming conventions
    found = False
    for label in fig_labels:
        if str(i) in label or f'fig{i}' in label:
            found = True
            found_count += 1
            break
    if not found:
        # Check include path
        for inc in fig_includes:
            if f'fig{i}' in inc:
                found = True
                found_count += 1
                break
    print(f'  fig{i}: {"✓" if found else "✗ MISSING!"}')

print(f'\nTotal figures found: {found_count}/20')

# Check for \ref issues
if '\\ref{' in content:
    # Check if any refs are broken by line endings
    for i, line in enumerate(lines, 1):
        if 'ef{' in line and '\\ref' not in line and '\\label' not in line and 'href' not in line and 'https' not in line:
            print(f'WARNING Line {i}: possible broken ref: {line.strip()[:80]}')
