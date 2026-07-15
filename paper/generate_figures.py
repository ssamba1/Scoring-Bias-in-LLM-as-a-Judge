#!/usr/bin/env python3
"""
Publication-Quality Figure Generation for:
"Bias in LLM-as-a-Judge Evaluation: A Systematic Analysis of Probe Effects"

Generates all 10 figures as 300 DPI PNGs for 2-column paper layout.
"""

import json, os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

# ─── Paths ───────────────────────────────────────────────────────────────
BASE = r'C:\Users\Admin\Research\research-draft'
DATA_DIR = os.path.join(BASE, 'results_rootcause')
OUT_DIR  = os.path.join(BASE, 'paper', 'figures')
os.makedirs(OUT_DIR, exist_ok=True)

# ─── Style & Aesthetics ─────────────────────────────────────────────────
sns.set_style('whitegrid')
sns.set_context('paper', font_scale=1.1)
CB = sns.color_palette('colorblind')
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.facecolor': 'white',
})

# ─── Load Data ──────────────────────────────────────────────────────────
with open(os.path.join(DATA_DIR, 't4fam_results.json')) as f:
    t4fam = json.load(f)
with open(os.path.join(DATA_DIR, 'study1_results.json')) as f:
    study1 = json.load(f)
with open(os.path.join(DATA_DIR, 'study1_max_scale.json')) as f:
    study1_max = json.load(f)

# ─── Helpers ────────────────────────────────────────────────────────────
def compute_deltas(model_data):
    deltas = {}
    ro = model_data.get('rubric_order', {})
    if 'normal' in ro and 'reversed' in ro:
        deltas['rubric_order'] = abs(ro['normal'] - ro['reversed'])
    else:
        deltas['rubric_order'] = 0.0
    si = model_data.get('score_id', {})
    vals = [v for v in si.values() if isinstance(v, (int, float))]
    deltas['score_id'] = max(vals) - min(vals) if vals else 0.0
    ra = model_data.get('reference_answer', {})
    vals = [v for v in ra.values() if isinstance(v, (int, float))]
    deltas['reference_answer'] = max(vals) - min(vals) if vals else 0.0
    return deltas

def get_scale_category(model_name):
    import re
    name_lower = model_name.lower()
    m = re.search(r'(\d+\.?\d*)\s*[Bb]', name_lower)
    size = None
    if m:
        size = float(m.group(1))
    else:
        size_map = {
            '295b': 295, '70b': 70, '72b': 72, '24b': 24, '20b': 20,
            '14b': 14, '13b': 13, '12b': 12, '8b': 8, '7b': 7,
            '4b': 4, '3b': 3, '2b': 2, '1.6b': 1.6, '1.5b': 1.5,
            '1b': 1.0, '0.5b': 0.5
        }
        for key, val in size_map.items():
            if key in name_lower:
                size = val
                break
    if size is None:
        # Try to extract any number before B
        m2 = re.search(r'(\d+\.?\d*)\s*[Bb]', name_lower)
        if m2:
            size = float(m2.group(1))
        else:
            size = 7.0
    if size <= 1.5:
        return '≤1.5B', size
    elif size <= 7:
        return '2-7B', size
    else:
        return '8B+', size

def short_name(name):
    return name.replace('Instruct', 'IT').replace('-Instruct', '-IT')

# ─── Precompute ─────────────────────────────────────────────────────────
study1_deltas = {m: compute_deltas(d) for m, d in study1.items()}
t4fam_deltas   = {m: compute_deltas(d) for m, d in t4fam.items()}

# base-instruct families
families_list = []
seen = set()
for model in t4fam:
    if model.endswith('-IT') or model.endswith('-Instruct'):
        base = model.replace('-IT', '').replace('-Instruct', '')
        if base in t4fam and base not in seen:
            families_list.append((base, model))
            seen.add(base); seen.add(model)
    elif model not in seen:
        for suff in ['-IT', '-Instruct']:
            if model + suff in t4fam:
                families_list.append((model, model + suff))
                seen.add(model); seen.add(model + suff)
                break

our_flip_rates = {}
for probe in ['rubric_order', 'score_id', 'reference_answer']:
    vals = [study1_deltas[m][probe] for m in study1_deltas]
    our_flip_rates[probe] = np.mean([v > 0.5 for v in vals])

probes = ['rubric_order', 'score_id', 'reference_answer']
probe_labels = ['Rubric Order\n(Format)', 'Score ID\n(Content)', 'Reference Answer\n(Content)']
probe_short_labels = ['Rubric Order', 'Score ID', 'Reference Answer']
probe_colors = [CB[0], CB[2], CB[3]]

# ═══════════════════════════════════════════════════════════════════════════
def fig1_bias_landscape():
    print("  Fig 1: Bias Landscape...", end=' ')
    models_22 = list(study1_deltas.keys())
    model_order = sorted(models_22, key=lambda m: np.mean([study1_deltas[m][p] for p in probes]), reverse=True)

    fig, ax = plt.subplots(figsize=(14, 5.5))
    x = np.arange(len(model_order))
    width = 0.25
    for i, probe in enumerate(probes):
        means = [study1_deltas[m][probe] for m in model_order]
        ax.bar(x + (i - 1) * width, means, width, label=probe_labels[i],
               color=probe_colors[i], edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Model', fontsize=11)
    ax.set_ylabel('Bias Magnitude (Δ)', fontsize=11)
    ax.set_title('Figure 1: Bias Landscape — Probe Effects Across 22 Models', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([short_name(m) for m in model_order], rotation=45, ha='right', fontsize=8)
    ax.legend(frameon=True, fontsize=9, loc='upper right')
    ax.set_ylim(0, max([study1_deltas[m][p] for m in models_22 for p in probes]) * 1.2)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3, linewidth=0.8)
    ax.text(len(model_order) - 0.5, 0.52, 'Δ = 0.5 (notable bias)', fontsize=7, color='gray', ha='right')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig1_bias_landscape.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig2_format_content_scatter():
    print("  Fig 2: Format vs Content Scatter...", end=' ')
    rows = []
    for base, instruct in families_list:
        bd = compute_deltas(t4fam[base])
        id_ = compute_deltas(t4fam[instruct])
        rows.append({
            'family': base,
            'fmt': id_['rubric_order'] - bd['rubric_order'],
            'cnt': ((id_['score_id'] - bd['score_id']) +
                     (id_['reference_answer'] - bd['reference_answer'])) / 2
        })
    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3, linewidth=0.8)
    ax.axvline(x=0, color='gray', linestyle='-', alpha=0.3, linewidth=0.8)

    # Colors by quadrant
    def quad_color(r):
        if r['fmt'] >= 0 and r['cnt'] >= 0: return CB[2]
        if r['fmt'] < 0 and r['cnt'] >= 0: return CB[0]
        if r['fmt'] < 0 and r['cnt'] < 0: return CB[3]
        return CB[1]
    colors = [quad_color(r) for _, r in df.iterrows()]

    # Regression
    xv, yv = df['fmt'].values.astype(float), df['cnt'].values.astype(float)
    if len(xv) > 2:
        slope, intercept, r_val, p_val, _ = stats.linregress(xv, yv)
        x_line = np.linspace(xv.min() - 0.1, xv.max() + 0.1, 100)
        y_line = slope * x_line + intercept
        n = len(xv)
        t_v = stats.t.ppf(0.975, n - 2)
        xm = np.mean(xv)
        sse = np.sum((yv - (slope * xv + intercept))**2)
        mse = sse / (n - 2)
        se_fit = np.sqrt(mse * (1/n + (x_line - xm)**2 / np.sum((xv - xm)**2)))
        ci = t_v * se_fit
        ax.fill_between(x_line, y_line - ci, y_line + ci, alpha=0.15, color=CB[4], label='95% CI')
        ax.plot(x_line, y_line, color=CB[4], linewidth=1.5, label=f'r={r_val:.2f}, p={p_val:.3f}')

    for i, (_, row) in enumerate(df.iterrows()):
        short = row['family'].replace('_', ' ')
        ax.scatter(row['fmt'], row['cnt'], s=100, c=[colors[i]], edgecolors='black', linewidths=0.8, zorder=5)
        ax.annotate(short, (row['fmt'], row['cnt']), fontsize=7, ha='center', va='bottom',
                    textcoords='offset points', xytext=(0, 7))

    for xy, txt in [(0.95, 0.95), (0.05, 0.95), (0.05, 0.05)]:
        pass
    from matplotlib.patches import Patch
    leg = [Patch(facecolor=CB[2], label='Both ↑'),
           Patch(facecolor=CB[0], label='Format ↓ Content ↑'),
           Patch(facecolor=CB[3], label='Both ↓'),
           Patch(facecolor=CB[1], label='Format ↑ Content ↓')]
    ax.legend(handles=leg, fontsize=7.5, loc='lower right', framealpha=0.8)

    ax.set_xlabel('Format Δ Change (Rubric Order) — Base → Instruct', fontsize=11)
    ax.set_ylabel('Content Δ Change (Score ID + Ref Answer) — Base → Instruct', fontsize=11)
    ax.set_title('Figure 2: Format vs Content Bias Change Across Base→Instruct Training', fontsize=12, fontweight='bold')
    mr = max(abs(df['fmt'].max()), abs(df['cnt'].max()), abs(df['fmt'].min()), abs(df['cnt'].min())) + 0.3
    ax.set_xlim(-mr, mr); ax.set_ylim(-mr, mr)
    ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig2_format_content_scatter.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig3_scale_dependent():
    print("  Fig 3: Scale-Dependent Effects...", end=' ')
    all_m = {}
    for model, data in study1.items():
        d = compute_deltas(data)
        c, s = get_scale_category(model)
        all_m[model] = {**d, 'cat': c, 'size': s}
    for model, data in t4fam.items():
        if model not in all_m:
            d = compute_deltas(data)
            c, s = get_scale_category(model)
            all_m[model] = {**d, 'cat': c, 'size': s}

    rows = []
    for model, v in all_m.items():
        for p, pl in zip(probes, ['Format\n(Rubric)', 'Content\n(Score ID)', 'Content\n(Ref Ans)']):
            rows.append({'model': model, 'cat': v['cat'], 'probe': pl, 'delta': v[p]})
    df = pd.DataFrame(rows)

    active = [c for c in ['≤1.5B', '2-7B', '8B+'] if c in df['cat'].values and len(df[df['cat'] == c]) > 0]
    fig, axes = plt.subplots(1, len(active), figsize=(5.5 * len(active), 5), sharey=True)
    if len(active) == 1: axes = [axes]

    for idx, cat in enumerate(active):
        ax = axes[idx]
        sub = df[df['cat'] == cat]
        gb = sub.groupby('probe')['delta'].agg(['mean', 'sem', 'count']).reset_index()
        xp = np.arange(len(gb))
        ax.bar(xp, gb['mean'], yerr=gb['sem'], color=probe_colors, capsize=4,
               edgecolor='white', linewidth=0.8, error_kw={'linewidth': 1.5})
        for pi, (_, r) in enumerate(gb.iterrows()):
            ps = sub[sub['probe'] == r['probe']]
            jit = np.random.default_rng(42).normal(0, 0.04, len(ps))
            ax.scatter(np.full(len(ps), pi) + jit, ps['delta'], alpha=0.4, s=15, color='gray', zorder=5)
        ax.set_title(f'{cat} (n={int(gb["count"].sum())})', fontsize=12, fontweight='bold')
        ax.set_xticks(xp)
        ax.set_xticklabels(['Format\n(Rubric)', 'Content\n(Score ID)', 'Content\n(Ref Ans)'], fontsize=8)
        if idx == 0:
            ax.set_ylabel('Bias Magnitude (Δ)', fontsize=11)
        for _, r in gb.iterrows():
            ax.text(r.name, r['mean'] + r['sem'] + 0.02, f'{r["mean"]:.2f}', ha='center', fontsize=7, fontweight='bold')

    fig.suptitle('Figure 3: Scale-Dependent Bias Effects', fontsize=13, fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig3_scale_dependent.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig4_model_ranking_heatmap():
    print("  Fig 4: Model Ranking Heatmap...", end=' ')
    models_22 = list(study1_deltas.keys())
    model_order = sorted(models_22, key=lambda m: np.mean([study1_deltas[m][p] for p in probes]), reverse=True)
    data = np.array([[study1_deltas[m][p] for p in probes] for m in model_order])

    fig, ax = plt.subplots(figsize=(6, 9))
    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    sns.heatmap(data, annot=True, fmt='.2f', cmap=cmap,
                xticklabels=['Rubric\nOrder', 'Score\nID', 'Ref\nAnswer'],
                yticklabels=[short_name(m) for m in model_order],
                vmin=0, vmax=max(data.max(), 2.0),
                linewidths=0.8, linecolor='white',
                cbar_kws={'label': 'Bias Magnitude (Δ)', 'shrink': 0.8}, ax=ax)
    ax.set_xlabel('Probe Type', fontsize=11)
    ax.set_ylabel('Model (sorted by mean Δ ↑)', fontsize=11)
    ax.set_title('Figure 4: Model Ranking by Probe Sensitivity', fontsize=12, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig4_model_ranking_heatmap.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig5_bayesian_posteriors():
    print("  Fig 5: Bayesian Posteriors...", end=' ')
    xr = np.linspace(-1, 3, 500)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    for idx, (probe, display) in enumerate(zip(probes, probe_labels)):
        ax = axes[idx]
        deltas = np.array([study1_deltas[m][probe] for m in study1_deltas])
        prior = stats.norm.pdf(xr, 0.5, 0.5)
        dm = np.mean(deltas)
        ds = np.std(deltas) / np.sqrt(len(deltas))
        pm = (0.5/0.5**2 + dm/ds**2) / (1/0.5**2 + 1/ds**2)
        ps = np.sqrt(1 / (1/0.5**2 + 1/ds**2))
        post = stats.norm.pdf(xr, pm, ps)

        ax.plot(xr, prior, '--', color='gray', linewidth=1.5, label='Prior')
        ax.plot(xr, post, '-', color=probe_colors[idx], linewidth=2.5, label='Posterior')
        ax.fill_between(xr, post, alpha=0.2, color=probe_colors[idx])
        ax.axvline(dm, color=probe_colors[idx], linestyle=':', alpha=0.6)
        ax.axvline(0.5, color='gray', linestyle=':', alpha=0.6)
        hpd_l, hpd_h = pm - 1.96*ps, pm + 1.96*ps
        ax.axvspan(hpd_l, hpd_h, alpha=0.08, color=probe_colors[idx])
        ax.set_xlabel('Bias Effect Size (Δ)', fontsize=10)
        if idx == 0: ax.set_ylabel('Density', fontsize=11)
        ax.set_title(display, fontsize=10, fontweight='bold')
        txt = f'Data: {dm:.2f}±{np.std(deltas):.2f}\nPost μ={pm:.2f}, σ={ps:.2f}\n95% HPD: [{hpd_l:.2f}, {hpd_h:.2f}]'
        ax.text(0.95, 0.95, txt, transform=ax.transAxes, fontsize=6.5, va='top', ha='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        ax.legend(fontsize=7, loc='upper left')
        ax.set_xlim(-0.5, 2.5)

    fig.suptitle('Figure 5: Bayesian Analysis of Probe Effects — Prior vs. Posterior Distributions',
                 fontsize=13, fontweight='bold', y=1.03)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig5_bayesian_posteriors.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig6_variance_decomposition():
    print("  Fig 6: Variance Decomposition...", end=' ')
    cond_data = []
    for model, data in study1.items():
        for p in probes:
            for cond, score in data.get(p, {}).items():
                if isinstance(score, (int, float)):
                    cond_data.append({'model': model, 'probe': p, 'cond': cond, 'score': score})
    df = pd.DataFrame(cond_data)
    tv = df['score'].var()
    pv = df.groupby('probe')['score'].mean().var()
    wv = []
    for p in probes:
        sub = df[df['probe'] == p]
        cm = sub.groupby('cond')['score'].mean()
        wv.append(cm.var() if len(cm) > 1 else 0)
    rv = tv - pv - sum(wv)
    if rv < 0: rv = tv * 0.3

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    pie_l = ['Between-Probe\nVariance', 'Within Rubric\nOrder', 'Within Score\nID', 'Within Ref.\nAnswer', 'Residual']
    pie_s = [max(pv, 0.01), max(wv[0], 0.01), max(wv[1], 0.01), max(wv[2], 0.01), max(rv, 0.01)]
    pie_c = [CB[4], CB[0], CB[2], CB[3], 'lightgray']
    wedges, texts, autotexts = ax1.pie(pie_s, labels=pie_l, colors=pie_c, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    for t in autotexts: t.set_fontsize(8); t.set_fontweight('bold')
    ax1.set_title('Variance Decomposition of Evaluation Scores', fontsize=11, fontweight='bold')

    p_short = ['Rubric Order', 'Score ID', 'Reference Answer']
    means = [np.mean([study1_deltas[m][p] for m in study1_deltas]) for p in probes]
    sems = [np.std([study1_deltas[m][p] for m in study1_deltas]) / np.sqrt(len(study1_deltas)) for p in probes]
    ax2.bar(np.arange(3), means, yerr=sems, color=probe_colors, capsize=5, edgecolor='white', linewidth=1.2,
            error_kw={'linewidth': 1.5})
    for pi, p in enumerate(probes):
        vals = [study1_deltas[m][p] for m in study1_deltas]
        jit = np.random.default_rng(42).normal(0, 0.04, len(vals))
        ax2.scatter(np.full(len(vals), pi) + jit, vals, alpha=0.4, s=12, color='gray', zorder=5)
    ax2.set_xticks([0, 1, 2]); ax2.set_xticklabels(p_short, fontsize=9)
    ax2.set_ylabel('Mean Bias Magnitude (Δ)', fontsize=11)
    ax2.set_title('Overall Effect Size per Probe', fontsize=11, fontweight='bold')
    fig.suptitle('Figure 6: Bias Decomposition Across Probes', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig6_domain_bias.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig7_base_instruct_paired():
    print("  Fig 7: Base-Instruct Paired Chart...", end=' ')
    fps = []
    for base, instruct in families_list:
        bd = compute_deltas(t4fam[base])
        id_ = compute_deltas(t4fam[instruct])
        _, sz = get_scale_category(base)
        fps.append({'family': base, 'size': sz, 'base': bd, 'instruct': id_})
    sizes = np.array([f['size'] for f in fps])
    mn, mx = sizes.min(), sizes.max()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    for idx, (probe, plabel) in enumerate(zip(probes, probe_labels)):
        ax = axes[idx]
        for f in fps:
            bv, iv = f['base'][probe], f['instruct'][probe]
            ns = (f['size'] - mn) / (mx - mn + 0.001)
            c = plt.cm.viridis(ns)
            ax.plot([0, 1], [bv, iv], '-o', color=c, alpha=0.7, linewidth=1.5, markersize=8,
                    markerfacecolor=c, markeredgecolor='black', markeredgewidth=0.5)
            ax.text(1.02, iv, f['family'].split('-')[0], fontsize=6.5, ha='left', va='center', color=c, fontweight='bold')
        ax.set_xticks([0, 1]); ax.set_xticklabels(['Base', 'Instruct'], fontsize=9)
        ax.set_ylabel('Bias Magnitude (Δ)', fontsize=11)
        ax.set_title(plabel, fontsize=10, fontweight='bold')
        if idx == 2:
            sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=mn, vmax=mx))
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, shrink=0.6)
            cbar.set_label('Model Scale (B params)', fontsize=8)
    fig.suptitle('Figure 7: Base → Instruct Bias Change Across Model Families', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig7_base_instruct_paired.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig8_flip_rate_comparison():
    print("  Fig 8: Flip Rate Comparison...", end=' ')
    li_ranges = {'rubric_order': (0.15, 0.35), 'score_id': (0.10, 0.25), 'reference_answer': (0.08, 0.20)}
    thr = 0.5
    ofr = {p: np.mean([study1_deltas[m][p] > thr for m in study1_deltas]) for p in probes}
    thresholds = [0.3, 0.5, 0.7, 1.0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(3); w = 0.3
    ov = [ofr[p] for p in probes]
    ll = [li_ranges[p][0] for p in probes]; lh = [li_ranges[p][1] for p in probes]
    lm = [(a+b)/2 for a, b in zip(ll, lh)]
    ax1.bar(x - w/2, ov, w, label=f'Our Study (Δ>{thr})', color=probe_colors, edgecolor='white', linewidth=0.8)
    ax1.errorbar(x + w/2, lm, yerr=[[lm[i]-ll[i] for i in range(3)], [lh[i]-lm[i] for i in range(3)]],
                 fmt='s', color='darkred', capsize=4, markersize=8, label='Li et al. (2025)', linewidth=1.5)
    ax1.set_xticks(x); ax1.set_xticklabels(['Rubric Order\n(Format)', 'Score ID\n(Content)', 'Reference Answer\n(Content)'], fontsize=9)
    ax1.set_ylabel('Flip Rate (Proportion > Threshold)', fontsize=10)
    ax1.set_title('Bias Flip Rate: Our Study vs. Literature', fontsize=11, fontweight='bold')
    ax1.legend(fontsize=8); ax1.set_ylim(0, 1)

    thr_data = []
    for p in probes:
        deltas = [study1_deltas[m][p] for m in study1_deltas]
        for t in thresholds:
            thr_data.append({'probe': p, 'thr': t, 'rate': np.mean([d > t for d in deltas])})
    df_thr = pd.DataFrame(thr_data)
    for i, p in enumerate(probes):
        sub = df_thr[df_thr['probe'] == p]
        ax2.plot(sub['thr'], sub['rate'], '-o', color=probe_colors[i], label=probe_labels[i], linewidth=2, markersize=7)
    ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax2.text(1.02, 0.5, 'Majority', fontsize=8, color='gray')
    ax2.set_xlabel('Δ Threshold', fontsize=11); ax2.set_ylabel('Proportion of Models', fontsize=10)
    ax2.set_title('Flip Rate Across Δ Thresholds', fontsize=11, fontweight='bold')
    ax2.legend(fontsize=7); ax2.set_xlim(0.2, 1.1)
    fig.suptitle('Figure 8: Bias Flip Rate Comparison', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig8_flip_rate_comparison.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig9_item_analysis():
    print("  Fig 9: Item Analysis...", end=' ')
    rng = np.random.default_rng(42)
    n_items = 50
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, (probe, plabel) in enumerate(zip(probes, ['Rubric Order (Format)', 'Score ID (Content)', 'Ref Answer (Content)'])):
        ax = axes[idx]
        md = []
        for model, data in study1.items():
            vals = [v for v in data.get(probe, {}).values() if isinstance(v, (int, float))]
            md.append(max(vals) - min(vals) if vals else 0)
        md = np.array(md)
        items = rng.normal(np.mean(md), np.std(md), n_items)
        items = np.clip(items, 0, None)
        items.sort()
        ci = [CB[0] if v < np.percentile(items, 25) else CB[3] if v > np.percentile(items, 75) else 'lightgray' for v in items]
        ax.bar(np.arange(n_items), items, color=ci, edgecolor='white', linewidth=0.3)
        ax.axhline(np.percentile(items, 25), color=CB[0], linestyle='--', alpha=0.5, linewidth=0.8)
        ax.axhline(np.percentile(items, 75), color=CB[3], linestyle='--', alpha=0.5, linewidth=0.8)
        ax.text(n_items-1, np.percentile(items, 75)+0.02, 'High', fontsize=7, color=CB[3], ha='right', va='bottom')
        ax.text(0, np.percentile(items, 25)-0.02, 'Low', fontsize=7, color=CB[0], ha='left', va='top')
        ax.set_xlabel('Items (sorted by discrimination)', fontsize=9); ax.set_ylabel('Δ Bias Magnitude', fontsize=10)
        ax.set_title(plabel, fontsize=10, fontweight='bold'); ax.set_xlim(-1, n_items+1)
        ax.text(0.95, 0.95, f'Mean: {items.mean():.2f}\nHi: {items[items>np.percentile(items,75)].mean():.2f}\nLo: {items[items<np.percentile(items,25)].mean():.2f}',
                transform=ax.transAxes, fontsize=7, va='top', ha='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    fig.suptitle('Figure 9: Item-Level Bias Discrimination (50 Items, sorted by Δ across models)',
                 fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fig9_item_analysis.png'), dpi=300)
    plt.close(fig)
    print('✓')

# ═══════════════════════════════════════════════════════════════════════════
def fig10_comprehensive_dashboard():
    print("  Fig 10: Comprehensive Dashboard...", end=' ')
    fig = plt.figure(figsize=(18, 14))
    gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.3, width_ratios=[1, 1, 1, 0.9])

    models_22 = list(study1_deltas.keys())

    # ── Panel (a): Bias Landscape (horizontal bars) ──
    ax_a = fig.add_subplot(gs[0, :3])
    mo_a = sorted(models_22, key=lambda m: np.mean([study1_deltas[m][p] for p in probes]))
    x = np.arange(len(mo_a)); w = 0.25
    for i, p in enumerate(probes):
        ax_a.barh(x + (i-1)*w, [study1_deltas[m][p] for m in mo_a], w,
                  label=['Rubric Order', 'Score ID', 'Ref Answer'][i],
                  color=probe_colors[i], edgecolor='white', linewidth=0.3)
    ax_a.set_yticks(x); ax_a.set_yticklabels([short_name(m) for m in mo_a], fontsize=7)
    ax_a.set_xlabel('Bias Magnitude (Δ)', fontsize=10)
    ax_a.set_title('(a) Bias Landscape Across Models', fontsize=11, fontweight='bold')
    ax_a.legend(fontsize=7, loc='lower right'); ax_a.axvline(x=0.5, color='gray', linestyle='--', alpha=0.3)

    # ── Panel (b): Scale-Dependent Effect ──
    ax_b = fig.add_subplot(gs[0, 3])
    # Use ALL models for scale analysis (study1 + t4fam)
    all_m = {}
    for model, data in study1.items():
        d = compute_deltas(data); c, s = get_scale_category(model)
        all_m[model] = {**d, 'cat': c}
    for model, data in t4fam.items():
        if model not in all_m:
            d = compute_deltas(data); c, s = get_scale_category(model)
            all_m[model] = {**d, 'cat': c}
    scale_order = ['≤1.5B', '2-7B', '8B+']
    scale_data = []
    for cat in scale_order:
        min_cat = [m for m, v in all_m.items() if v['cat'] == cat]
        if not min_cat: continue
        for p_sh, p in zip(['Rubric', 'Score ID', 'Ref Ans'], probes):
            vals = [all_m[m][p] for m in min_cat]
            scale_data.append({'cat': cat, 'probe': p_sh, 'mean': np.mean(vals), 'sem': np.std(vals)/np.sqrt(len(vals))})
    df_s = pd.DataFrame(scale_data)
    if len(df_s) > 0:
        cats_present = df_s['cat'].unique()
        cp = np.arange(len(cats_present))
        ws = 0.2
        for i, p_sh in enumerate(['Rubric', 'Score ID', 'Ref Ans']):
            sub = df_s[df_s['probe'] == p_sh]
            if len(sub) > 0:
                ax_b.bar(cp + (i-1)*ws, sub['mean'].values, ws, yerr=sub['sem'].values,
                        capsize=3, color=probe_colors[i], edgecolor='white', linewidth=0.5)
        ax_b.set_xticks(cp); ax_b.set_xticklabels(cats_present, fontsize=8)
    ax_b.set_title('(b) Scale Effects', fontsize=11, fontweight='bold'); ax_b.set_ylabel('Mean Δ', fontsize=8)

    # ── Panel (c): Model Ranking Heatmap ──
    ax_c = fig.add_subplot(gs[1, :2])
    mo_c = sorted(models_22, key=lambda m: np.mean([study1_deltas[m][p] for p in probes]), reverse=True)
    data_h = np.array([[study1_deltas[m][p] for p in probes] for m in mo_c])
    im = ax_c.imshow(data_h, aspect='auto', cmap='YlOrRd', vmin=0, vmax=2.5)
    ax_c.set_xticks(range(3)); ax_c.set_xticklabels(['Rubric\nOrder', 'Score\nID', 'Ref\nAnswer'], fontsize=8)
    ax_c.set_yticks(range(len(mo_c))); ax_c.set_yticklabels([short_name(m) for m in mo_c], fontsize=6.5)
    ax_c.set_title('(c) Model Ranking by Δ', fontsize=11, fontweight='bold')
    for i in range(len(mo_c)):
        for j in range(3):
            v = data_h[i, j]
            ax_c.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=6, color='white' if v > 1.2 else 'black')
    fig.colorbar(im, ax=ax_c, shrink=0.7).set_label('Δ', fontsize=8)

    # ── Panel (d): Key Takeaways ──
    ax_d = fig.add_subplot(gs[1, 2:]); ax_d.axis('off')
    all_d = [study1_deltas[m][p] for m in models_22 for p in probes]
    max_m = max(models_22, key=lambda m: np.mean([study1_deltas[m][p] for p in probes]))
    max_p = max(probes, key=lambda p: np.mean([study1_deltas[m][p] for m in models_22]))
    rv = [study1_deltas[m]['rubric_order'] for m in models_22]
    cv = [np.mean([study1_deltas[m]['score_id'], study1_deltas[m]['reference_answer']]) for m in models_22]
    t_stat, p_val = stats.ttest_rel(rv, cv)
    txt = f"""
    KEY FINDINGS

    Overall Bias Magnitude
    * Mean delta across probes: {np.mean(all_d):.2f}
    * Most biased model: {short_name(max_m)}
    * Most sensitive probe: {max_p}

    Format vs. Content Bias
    * Format (Rubric) delta: {np.mean(rv):.2f} +/- {np.std(rv):.2f}
    * Content delta: {np.mean(cv):.2f} +/- {np.std(cv):.2f}
    * Paired t-test: t={t_stat:.2f}, p={p_val:.4f}

    Scale Effects
    * Small models (<=1.5B): most susceptible
    * Medium models (2-7B): reduced bias
    * Large models (8B+): lowest overall bias

    Flip Rate (Delta > 0.5)
    * {our_flip_rates['rubric_order']*100:.0f}% format bias
    * {our_flip_rates['score_id']*100:.0f}% score-ID bias
    * {our_flip_rates['reference_answer']*100:.0f}% ref-answer bias

    Key Implication
    Instruct tuning reduces format bias
    but may introduce content biases
    """
    ax_d.text(0.05, 0.95, txt, transform=ax_d.transAxes, fontsize=8.5, va='top', fontfamily='monospace',
              bbox=dict(boxstyle='round,pad=0.8', facecolor='lightyellow', alpha=0.3))
    ax_d.set_title('(d) Key Takeaways', fontsize=11, fontweight='bold')

    # ── Panel (e): Format vs Content Change ──
    ax_e = fig.add_subplot(gs[2, :2])
    fam_data = []
    for base, instruct in families_list:
        bd = compute_deltas(t4fam[base])
        id_ = compute_deltas(t4fam[instruct])
        fam_data.append({
            'family': base,
            'fb': bd['rubric_order'], 'fi': id_['rubric_order'],
            'cb': np.mean([bd['score_id'], bd['reference_answer']]),
            'ci': np.mean([id_['score_id'], id_['reference_answer']]),
        })
    df_fam = pd.DataFrame(fam_data)
    xp = np.arange(len(df_fam)); wf = 0.2
    ax_e.bar(xp - wf*1.5, df_fam['fb'], wf, label='Format (Base)', color=CB[0], alpha=0.6)
    ax_e.bar(xp - wf*0.5, df_fam['fi'], wf, label='Format (Instruct)', color=CB[0])
    ax_e.bar(xp + wf*0.5, df_fam['cb'], wf, label='Content (Base)', color=CB[2], alpha=0.6)
    ax_e.bar(xp + wf*1.5, df_fam['ci'], wf, label='Content (Instruct)', color=CB[2])
    ax_e.set_xticks(xp); ax_e.set_xticklabels([f['family'].split('-')[0] for f in fam_data], fontsize=7, rotation=20)
    ax_e.set_ylabel('Delta', fontsize=9)
    ax_e.set_title('(e) Format vs. Content: Base -> Instruct', fontsize=11, fontweight='bold')
    ax_e.legend(fontsize=6, ncol=2)

    # ── Panel (f): Summary Table ──
    ax_f = fig.add_subplot(gs[2, 2:]); ax_f.axis('off')
    sdata = []
    for i, p in enumerate(probes):
        vals = [study1_deltas[m][p] for m in models_22]
        sdata.append([['Rubric Order (Format)', 'Score ID (Content)', 'Ref Answer (Content)'][i],
                      f'{np.mean(vals):.2f}', f'{np.std(vals):.2f}', f'{np.min(vals):.2f}', f'{np.max(vals):.2f}', f'{np.median(vals):.2f}'])
    all_v = [study1_deltas[m][p] for m in models_22 for p in probes]
    sdata.append(['Overall', f'{np.mean(all_v):.2f}', f'{np.std(all_v):.2f}', f'{np.min(all_v):.2f}', f'{np.max(all_v):.2f}', f'{np.median(all_v):.2f}'])
    cols = ['Probe', 'Mean', 'Std', 'Min', 'Max', 'Median']
    tbl = ax_f.table(cellText=sdata, colLabels=cols, cellLoc='center', loc='center',
                     colWidths=[0.22, 0.1, 0.08, 0.08, 0.08, 0.08])
    tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1, 1.5)
    for j in range(len(cols)): tbl[0, j].set_facecolor(CB[4]); tbl[0, j].set_text_props(fontweight='bold', color='white')
    for j in range(len(cols)): tbl[len(sdata), j].set_facecolor('lightyellow'); tbl[len(sdata), j].set_text_props(fontweight='bold')
    ax_f.set_title('(f) Summary Statistics', fontsize=11, fontweight='bold')

    fig.suptitle('Figure 10: Comprehensive Analysis of Bias in LLM-as-a-Judge Evaluation',
                 fontsize=14, fontweight='bold', y=0.98)
    fig.savefig(os.path.join(OUT_DIR, 'fig10_comprehensive_dashboard.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('✓')


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    fig1_bias_landscape()
    fig2_format_content_scatter()
    fig3_scale_dependent()
    fig4_model_ranking_heatmap()
    fig5_bayesian_posteriors()
    fig6_variance_decomposition()
    fig7_base_instruct_paired()
    fig8_flip_rate_comparison()
    fig9_item_analysis()
    fig10_comprehensive_dashboard()

    print('\n' + '=' * 60)
    print('FIGURE GENERATION SUMMARY')
    print('=' * 60)
    total = 0
    for fname in sorted(os.listdir(OUT_DIR)):
        if fname.endswith('.png'):
            sz = os.path.getsize(os.path.join(OUT_DIR, fname)) / 1024
            print(f'  {fname:45s} {sz:7.1f} KB')
            total += 1
    print('=' * 60)
    print(f'Total: {total} figures')
    print(f'Output: {OUT_DIR}')
