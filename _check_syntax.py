#!/usr/bin/env python3
"""Quick syntax check for generate_all_figures.py"""
import sys
sys.path.insert(0, 'src')
with open('paper/figures/generate_all_figures.py') as f:
    code = f.read()
compile(code, 'generate_all_figures.py', 'exec')
print('OK: generate_all_figures.py syntax is valid')

try:
    from scoring_bias.visualization import plot_bias_landscape
    print('OK: src.scoring_bias.visualization imports successfully')
except ImportError as e:
    print(f'INFO: visualization module unavailable ({e}) — fallback will be used')
