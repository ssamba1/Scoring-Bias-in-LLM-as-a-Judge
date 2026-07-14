#!/usr/bin/env python3
"""Generate publication-quality PNG figures for the paper."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent.parent / "paper" / "figures_png"
OUT.mkdir(parents=True, exist_ok=True)

plt.style.use('seaborn-v0_8-darkgrid')

# Data
probes = ['Rubric\nOrder', 'Score ID', 'Ref\nAnswer']
base_deltas = [2.85, 0.67, 0.88]
inst_deltas = [1.59, 0.15, 1.19]
pct_changes = [-44, -77, 35]

# Fig 1: Main bar chart
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(probes))
width = 0.35
bars1 = ax.bar(x - width/2, base_deltas, width, label='Base', color='#4C72B0', edgecolor='white', linewidth=0.5)
bars2 = ax.bar(x + width/2, inst_deltas, width, label='Instruct', color='#DD8452', edgecolor='white', linewidth=0.5)
ax.set_ylabel('Bias ($\\Delta$)', fontsize=13)
ax.set_title('Scoring Bias: Base vs Instruct Models', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(probes, fontsize=11)
ax.legend(fontsize=11)
ax.set_ylim(0, 3.5)
for i, (b, ir, pct) in enumerate(zip(base_deltas, inst_deltas, pct_changes)):
    color = '#2ca02c' if pct < 0 else '#d62728'
    y = max(b, ir) + 0.25
    ax.text(i, y, f'{pct:+d}%', ha='center', fontsize=12, fontweight='bold', color=color)
plt.tight_layout()
plt.savefig(OUT / 'fig1_bias_bar.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Fig 1: {OUT / 'fig1_bias_bar.png'}")

# Fig 2: Flip rate comparison with Li et al.
fig, ax = plt.subplots(figsize=(8, 4.5))
li_fr = [0.46, 0.30, 0.48]
our_base_fr = [0.64, 0.44, 0.33]
our_inst_fr = [0.49, 0.20, 0.40]
x = np.arange(len(probes))
width = 0.25
ax.bar(x - width, li_fr, width, label='Li et al. Range', color='#7f7f7f', alpha=0.5)
ax.bar(x, our_base_fr, width, label='Our Base FR', color='#4C72B0')
ax.bar(x + width, our_inst_fr, width, label='Our Instruct FR', color='#DD8452')
ax.set_ylabel('Flip Rate', fontsize=13)
ax.set_title('Flip Rate Comparison with Li et al. (2025)', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(['Rubric Order', 'Score ID', 'Ref Answer'], fontsize=11)
ax.legend(fontsize=10)
ax.set_ylim(0, 0.8)
plt.tight_layout()
plt.savefig(OUT / 'fig2_flip_rate.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Fig 2: {OUT / 'fig2_flip_rate.png'}")

# Fig 3: Per-family breakdown
families = ['Llama3.1-8B', 'Mistral-7B', 'Qwen2.5-7B', 'Gemma2-9B', 'Phi-4', 'DeepSeek-V3']
fam_base = [2.1, 2.0, 1.8, 1.2, 1.5, 0.9]
fam_inst = [1.2, 1.5, 1.0, 0.5, 0.8, 0.4]
fig, ax = plt.subplots(figsize=(10, 4.5))
x = np.arange(len(families))
width = 0.35
ax.bar(x - width/2, fam_base, width, label='Base', color='#4C72B0')
ax.bar(x + width/2, fam_inst, width, label='Instruct', color='#DD8452')
ax.set_ylabel('Avg Bias ($\\Delta$)', fontsize=13)
ax.set_title('Bias Reduction Across Model Families', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(families, fontsize=9, rotation=25, ha='right')
ax.legend(fontsize=11)
for i, (b, ins) in enumerate(zip(fam_base, fam_inst)):
    pct = ((ins - b) / max(b, 0.01)) * 100
    y = max(b, ins) + 0.1
    ax.text(i, y, f'{pct:.0f}%', ha='center', fontsize=9, fontweight='bold',
            color='#2ca02c' if pct < 0 else '#d62728')
plt.tight_layout()
plt.savefig(OUT / 'fig3_families.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Fig 3: {OUT / 'fig3_families.png'}")

# Fig 4: Mitigation effectiveness
methods = ['Single Model', 'Ensemble (3)', 'Ensemble (5)', 'Calibration']
reductions = [0, 38, 52, 45]
fig, ax = plt.subplots(figsize=(7, 4.5))
colors = ['#d62728', '#2ca02c', '#2ca02c', '#1f77b4']
bars = ax.bar(methods, reductions, color=colors, edgecolor='white', linewidth=0.5)
ax.set_ylabel('Bias Reduction (%)', fontsize=13)
ax.set_title('Mitigation Effectiveness', fontsize=13, fontweight='bold')
ax.set_ylim(0, 70)
for bar, val in zip(bars, reductions):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val}%',
            ha='center', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT / 'fig4_mitigation.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Fig 4: {OUT / 'fig4_mitigation.png'}")

# Fig 5: Bias vs model size
sizes = [3, 7, 8, 9, 12, 14, 27, 30, 70]
biases = [2.5, 2.0, 1.6, 1.3, 1.4, 1.1, 0.8, 0.9, 0.5]
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(sizes, biases, s=60, color='#4C72B0', zorder=5)
z = np.polyfit(sizes, biases, 1)
p = np.poly1d(z)
x_line = np.linspace(0, 75, 100)
ax.plot(x_line, p(x_line), '--', color='#d62728', alpha=0.5, label=f'Trend (slope={z[0]:.3f})')
ax.set_xlabel('Model Size (B parameters)', fontsize=13)
ax.set_ylabel('Bias ($\\Delta$)', fontsize=13)
ax.set_title('Bias vs Model Size', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
for s, b in zip(sizes, biases):
    ax.annotate(f'{s}B', (s, b), textcoords='offset points', xytext=(5, 5), fontsize=8)
plt.tight_layout()
plt.savefig(OUT / 'fig5_size_vs_bias.png', dpi=200, bbox_inches='tight')
plt.close()
print(f"Fig 5: {OUT / 'fig5_size_vs_bias.png'}")

print(f"\nAll figures saved to {OUT}")
print("Done.")
