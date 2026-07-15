#!/usr/bin/env python3
"""Validate all created files."""
import json, os, sys
from pathlib import Path

base = Path(r'C:\Users\Admin\Research\research-draft')
errors = []

# 1. dataset.json
try:
    d = json.load(open(base / 'data' / 'dataset.json'))
    n_models = len(d['models']['entries'])
    print(f'✓ data/dataset.json: {len(d)} top-level keys, {n_models} model entries')
except Exception as e:
    errors.append(f'data/dataset.json: {e}')

# 2. data_dictionary.md
dd = base / 'data' / 'data_dictionary.md'
if dd.exists():
    size = dd.stat().st_size
    print(f'✓ data/data_dictionary.md: {size} bytes')
else:
    errors.append('data/data_dictionary.md missing')

# 3. dataset_card.md
dc = base / 'data' / 'dataset_card.md'
if dc.exists():
    print(f'✓ data/dataset_card.md: {dc.stat().st_size} bytes')
else:
    errors.append('data/dataset_card.md missing')

# 4. README.md
rm = base / 'README.md'
if rm.exists():
    print(f'✓ README.md: {rm.stat().st_size} bytes')
else:
    errors.append('README.md missing')

# 5. generate_all_figures.py
gf = base / 'paper' / 'figures' / 'generate_all_figures.py'
if gf.exists():
    code = gf.read_text()
    compile(code, str(gf), 'exec')
    print(f'✓ paper/figures/generate_all_figures.py: valid syntax, {len(code.splitlines())} lines')
else:
    errors.append('paper/figures/generate_all_figures.py missing')

# 6. figure_captions.tex
fc = base / 'paper' / 'figures' / 'figure_captions.tex'
if fc.exists():
    print(f'✓ paper/figures/figure_captions.tex: {fc.stat().st_size} bytes')
else:
    errors.append('paper/figures/figure_captions.tex missing')

# 7. Tables
tables_dir = base / 'paper' / 'tables'
expected_tables = [
    'tab_main.tex', 'tab_per_model.tex', 'tab_related.tex',
    'tab_models.tex', 'tab_bayesian.tex', 'tab_bootstrapped.tex',
    'tab_domain.tex', 'tab_comparison.tex',
]
if tables_dir.exists():
    files = list(tables_dir.glob('*.tex'))
    print(f'✓ paper/tables/: {len(files)} table files')
    for t in expected_tables:
        if (tables_dir / t).exists():
            print(f'    ✓ {t}')
        else:
            errors.append(f'paper/tables/{t} missing')
else:
    errors.append('paper/tables/ directory missing')

# Summary
print()
if errors:
    print(f'ERRORS ({len(errors)}):')
    for e in errors:
        print(f'  ✗ {e}')
    sys.exit(1)
else:
    print('✓ ALL FILES VALIDATED SUCCESSFULLY')
