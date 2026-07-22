#!/usr/bin/env python3
"""Generate publication-ready figures from synthetic results.
Usage: python3 generate_figures.py
"""
import csv, os, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "paper" / "figures"

def load_data():
    path = RESULTS_DIR / "bias_interaction_synthetic.csv"
    if not path.exists():
        print("No data found. Run generate_synthetic_pilot.py first.")
        return None
    data = []
    with open(path) as f:
        for row in csv.DictReader(f):
            row["score"] = float(row["score"])
            row["item_id"] = int(row["item_id"])
            data.append(row)
    return data

def fig_interaction_ratios(data):
    """Bar chart of interaction ratios per judge."""
    judges = sorted(set(r["judge"] for r in data))
    ratios = []
    for judge in judges:
        jd = [r for r in data if r["judge"] == judge]
        pf = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        ps = [r for r in jd if r["position"]=="second" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        vl = [r for r in jd if r["length"]=="long" and r["position"]=="first" and r["sentiment"]=="neutral"]
        vn = [r for r in jd if r["length"]=="normal" and r["position"]=="first" and r["sentiment"]=="neutral"]
        both = [r for r in jd if r["position"]=="second" and r["length"]=="short" and r["sentiment"]=="neutral"]
        base = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]

        if pf and ps and vl and vn and both and base:
            pos = sum(r["score"] for r in pf)/len(pf) - sum(r["score"] for r in ps)/len(ps)
            verb = sum(r["score"] for r in vl)/len(vl) - sum(r["score"] for r in vn)/len(vn)
            comb = sum(r["score"] for r in base)/len(base) - sum(r["score"] for r in both)/len(both)
            pa, va = abs(pos), abs(verb)
            ir = comb / (pa + va) if (pa + va) > 0 else 0
            ratios.append(ir)

    plt.figure(figsize=(10, 6))
    colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B2']
    bars = plt.bar(judges, ratios, color=colors, edgecolor='white', linewidth=1.5)

    # Add horizontal line at 1.0 (additive baseline)
    plt.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Additive baseline')
    plt.axhline(y=1.05, color='orange', linestyle=':', alpha=0.5, label='Compounding threshold')
    plt.axhline(y=0.95, color='orange', linestyle=':', alpha=0.5, label='Cancelling threshold')

    plt.ylabel('Interaction Ratio', fontsize=14)
    plt.title('Position × Verbosity Interaction Ratio by Judge Model', fontsize=16)
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar, ratio in zip(bars, ratios):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{ratio:.2f}', ha='center', fontsize=11, fontweight='bold')

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'interaction_ratios.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {FIGURES_DIR / 'interaction_ratios.png'}")

def fig_worst_case_comparison(data):
    """Grouped bar chart comparing baseline vs worst case per judge."""
    judges = sorted(set(r["judge"] for r in data))
    baselines, worsts = [], []

    for judge in judges:
        jd = [r for r in data if r["judge"] == judge]
        base = [r for r in jd if r["condition"] == "baseline"]
        worst = [r for r in jd if r["condition"] == "worst"]
        if base and worst:
            baselines.append(sum(r["score"] for r in base)/len(base))
            worsts.append(sum(r["score"] for r in worst)/len(worst))

    x = np.arange(len(judges))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(x - width/2, baselines, width, label='Baseline', color='#55A868', edgecolor='white')
    plt.bar(x + width/2, worsts, width, label='Worst Case', color='#C44E52', edgecolor='white')

    # Add degradation labels
    for i, (b, w) in enumerate(zip(baselines, worsts)):
        plt.text(i, max(b, w) + 0.1, f'Δ={b-w:.2f}', ha='center', fontsize=9, fontweight='bold')

    plt.xlabel('Judge Model', fontsize=14)
    plt.ylabel('Score (1-5)', fontsize=14)
    plt.title('Baseline vs Worst Case: Bias Degradation', fontsize=16)
    plt.xticks(x, judges, fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.ylim(2.5, 4.0)

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'worst_case_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {FIGURES_DIR / 'worst_case_comparison.png'}")

def fig_heatmap(data):
    """Heatmap of 8 conditions x judges."""
    judges = sorted(set(r["judge"] for r in data))
    conditions = ["baseline", "short", "verbose", "positive", "negative", "disfavored", "worst", "best_biased"]

    scores = np.zeros((len(judges), len(conditions)))
    for i, judge in enumerate(judges):
        for j, cond in enumerate(conditions):
            subset = [r for r in data if r["judge"] == judge and r["condition"] == cond]
            if subset:
                scores[i, j] = sum(r["score"] for r in subset) / len(subset)

    plt.figure(figsize=(14, 7))
    ax = sns.heatmap(scores, annot=True, fmt='.2f', cmap='RdYlGn_r',
                     xticklabels=conditions, yticklabels=judges,
                     linewidths=1, cbar_kws={'label': 'Score (1-5)'})
    plt.title('Score Heatmap: 8 Conditions × 5 Judges', fontsize=16)
    plt.xlabel('Condition', fontsize=14)
    plt.ylabel('Judge Model', fontsize=14)
    plt.xticks(rotation=30, ha='right')

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'condition_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {FIGURES_DIR / 'condition_heatmap.png'}")

def fig_effect_sizes(data):
    """Bar chart of individual bias effect sizes per judge."""
    judges = sorted(set(r["judge"] for r in data))

    pos_effects, verb_effects, sent_effects = [], [], []

    for judge in judges:
        jd = [r for r in data if r["judge"] == judge]

        pf = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        ps = [r for r in jd if r["position"]=="second" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        pos = abs(sum(r["score"] for r in pf)/len(pf) - sum(r["score"] for r in ps)/len(ps)) if pf and ps else 0

        vl = [r for r in jd if r["length"]=="long" and r["position"]=="first" and r["sentiment"]=="neutral"]
        vn = [r for r in jd if r["length"]=="normal" and r["position"]=="first" and r["sentiment"]=="neutral"]
        verb = abs(sum(r["score"] for r in vl)/len(vl) - sum(r["score"] for r in vn)/len(vn)) if vl and vn else 0

        sp = [r for r in jd if r["sentiment"]=="positive" and r["position"]=="first" and r["length"]=="normal"]
        sn = [r for r in jd if r["sentiment"]=="negative" and r["position"]=="first" and r["length"]=="normal"]
        sent = abs(sum(r["score"] for r in sp)/len(sp) - sum(r["score"] for r in sn)/len(sn)) if sp and sn else 0

        pos_effects.append(pos)
        verb_effects.append(verb)
        sent_effects.append(sent)

    x = np.arange(len(judges))
    width = 0.25

    plt.figure(figsize=(12, 6))
    plt.bar(x - width, pos_effects, width, label='Position Bias', color='#4C72B0')
    plt.bar(x, verb_effects, width, label='Verbosity Bias', color='#DD8452')
    plt.bar(x + width, sent_effects, width, label='Sentiment Bias', color='#55A868')

    plt.xlabel('Judge Model', fontsize=14)
    plt.ylabel('Effect Size (Δ score)', fontsize=14)
    plt.title('Individual Bias Effect Sizes by Judge', fontsize=16)
    plt.xticks(x, judges, fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'effect_sizes.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {FIGURES_DIR / 'effect_sizes.png'}")

if __name__ == "__main__":
    data = load_data()
    if data:
        print("Generating figures...")
        fig_interaction_ratios(data)
        fig_worst_case_comparison(data)
        fig_heatmap(data)
        fig_effect_sizes(data)
        print(f"\nAll figures saved to {FIGURES_DIR}")
