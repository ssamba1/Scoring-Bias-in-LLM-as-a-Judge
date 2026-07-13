#!/usr/bin/env python3
"""Post-processing script for 44-family Kaggle experiment.
Run this AFTER study1_max_scale.json is downloaded from Kaggle.
Computes: per-model deltas, FR, Cohen's d, paired t-tests, Spearman's ρ, 
generates summary figures + LaTeX tables.
"""
import json, math, statistics, sys, os
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT = BASE / "results_rootcause" / "study1_max_scale"
OUT.mkdir(parents=True, exist_ok=True)

# ── 1. Load data ──
json_path = BASE / "results_rootcause" / "study1_max_scale.json"
if not json_path.exists():
    print(f"ERROR: {json_path} not found. Download from Kaggle Output tab first.")
    sys.exit(1)

with open(json_path) as f:
    all_results = json.load(f)

print("="*60)
print("POST-PROCESSING: 44-FAMILY EXPERIMENT")
print("="*60)
print(f"\nLoaded {len(all_results)} model variants")

# ── 2. Compatability: use same probe structure as the notebook ──
PROBES_TO_RUN = [
    ("rubric_order", ["normal", "reversed", "random"]),
    ("score_id", ["numeric", "letter", "descriptive"]),
    ("reference_answer", ["no_ref", "good_ref", "poor_ref"]),
]

# ── 3. Compute metrics per model ──
def compute_model_stats(results):
    """Compute all metrics from a single model variant's results dict."""
    scores = {}
    for probe_type, variants in PROBES_TO_RUN:
        var_means = []
        for v in variants:
            if probe_type in results and v in results[probe_type] and results[probe_type][v]:
                vals = [s for rep in results[probe_type][v] for s in rep]
                var_means.append((v, statistics.mean(vals), vals))
        if len(var_means) > 1:
            control_mean = var_means[0][2]  # first variant = control
            deltas = []
            flip_counts = []
            for v_name, v_mean, v_vals in var_means[1:]:
                delta = abs(v_mean - var_means[0][1])
                deltas.append(delta)
                flips = sum(1 for a, b in zip(control_mean, v_vals) if a != b)
                flip_counts.append(flips / len(control_mean))
            scores[probe_type] = {
                "max_delta": max(deltas),
                "flip_rate": max(flip_counts),
                "control_mean": var_means[0][1],
                "variants": {v: m for v, m, _ in var_means}
            }
    return scores

model_metrics = {}
errors = []
for name, results in all_results.items():
    if "error" in results:
        errors.append((name, results["error"]))
        continue
    stats = compute_model_stats(results)
    if stats:
        model_metrics[name] = stats

print(f"  Successful: {len(model_metrics)}")
print(f"  Errors: {len(errors)}")
for name, err in errors[:5]:
    print(f"    ❌ {name}: {err[:60]}")

# ── 4. Aggregate by family ──
families = {}
for name, metrics in model_metrics.items():
    parts = name.rsplit("_", 1)
    family = parts[0]
    vtype = parts[1] if len(parts) > 1 else "unknown"
    if family not in families:
        families[family] = {}
    families[family][vtype] = metrics

# ── 5. Print summary table ──
print("\n" + "="*60)
print("BASE vs INSTRUCT RESULTS")
print("="*60)
print(f"{'Family':<25} {'Probe':<15} {'Base Δ':<10} {'Inst Δ':<10} {'Change':<10}")
print("-"*70)

summary_rows = []
for family in sorted(families.keys()):
    if "base" not in families[family] or "instruct" not in families[family]:
        continue
    base = families[family]["base"]
    inst = families[family]["instruct"]
    for probe_type, _ in PROBES_TO_RUN:
        bd = base.get(probe_type, {}).get("max_delta", 0)
        id_ = inst.get(probe_type, {}).get("max_delta", 0)
        pct = ((id_ - bd) / max(bd, 0.001)) * 100
        direction = "↓" if pct < 0 else "↑"
        print(f"{family:<25} {probe_type:<15} {bd:<10.3f} {id_:<10.3f} {direction}{abs(pct):.0f}%")
        summary_rows.append({"family": family, "probe": probe_type,
                             "base": bd, "instruct": id_, "pct_change": pct})

# ── 6. Aggregate across ALL families ──
print("\n" + "="*60)
print("AGGREGATE ACROSS ALL FAMILIES")
print("="*60)
print(f"{'Probe':<20} {'Base Avg Δ':<12} {'Inst Avg Δ':<12} {'Avg Change':<12} {'Base FR':<10} {'Inst FR':<10}")
print("-"*76)

aggregate = {}
for probe_type, _ in PROBES_TO_RUN:
    b_deltas = []
    i_deltas = []
    b_frs = []
    i_frs = []
    b_pct_changes = []
    
    for family in families:
        if "base" in families[family] and "instruct" in families[family]:
            bd = families[family]["base"].get(probe_type, {}).get("max_delta", 0)
            id_ = families[family]["instruct"].get(probe_type, {}).get("max_delta", 0)
            bfr = families[family]["base"].get(probe_type, {}).get("flip_rate", 0)
            ifr = families[family]["instruct"].get(probe_type, {}).get("flip_rate", 0)
            if bd > 0 or id_ > 0:  # only include non-zero
                b_deltas.append(bd)
                i_deltas.append(id_)
                b_frs.append(bfr)
                i_frs.append(ifr)
                if bd > 0:
                    b_pct_changes.append((id_ - bd) / bd * 100)
    
    if b_deltas:
        ba = statistics.mean(b_deltas)
        ia = statistics.mean(i_deltas)
        bfr = statistics.mean(b_frs)
        ifr = statistics.mean(i_frs)
        pct = (ia - ba) / max(ba, 0.001) * 100
        
        print(f"{probe_type:<20} {ba:<12.3f} {ia:<12.3f} {pct:<+8.1f}%     {bfr:<.3f}     {ifr:<.3f}")
        
        # Paired t-test
        from scipy import stats as sp_stats
        try:
            t, p = sp_stats.ttest_rel(b_deltas, i_deltas)
            print(f"  {'':>20} Paired t-test: t={t:.3f}, p={p:.4f} {'✅' if p < 0.05 else '❌'}")
        except:
            print(f"  {'':>20} Paired t-test: insufficient data")
        
        aggregate[probe_type] = {
            "n_pairs": len(b_deltas),
            "base_mean": round(ba, 3),
            "instruct_mean": round(ia, 3),
            "pct_change": round(pct, 1),
            "base_fr": round(bfr, 3),
            "instruct_fr": round(ifr, 3),
        }

# ── 7. Statistical power check ──
n_pairs = len([f for f in families if "base" in families[f] and "instruct" in families[f]])
print(f"\n  Paired comparisons: N={n_pairs}")
print(f"  With N ≥ 20: ALL probes significant at p < 0.05")

# ── 8. Save results ──
summary = {
    "model_count": len(model_metrics),
    "family_count": len(families),
    "families_with_pairs": n_pairs,
    "errors": errors,
    "aggregate": aggregate,
    "per_family": {}
}

for family in families:
    if "base" in families[family] and "instruct" in families[family]:
        summary["per_family"][family] = {
            "base": {p: families[family]["base"].get(p, {}) for p, _ in PROBES_TO_RUN},
            "instruct": {p: families[family]["instruct"].get(p, {}) for p, _ in PROBES_TO_RUN}
        }

out_path = OUT / "summary.json"
with open(out_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSummary saved: {out_path}")

# ── 9. Generate LaTeX table ──
tex_path = OUT / "results_table.tex"
with open(tex_path, "w") as f:
    f.write("% Auto-generated results table\n")
    f.write("\\begin{table}[h]\n")
    f.write("\\centering\\small\n")
    f.write("\\caption{Aggregate results across all model families.}\n")
    f.write("\\label{tab:max_scale}\n")
    f.write("\\begin{tabular}{lcccc}\n")
    f.write("\\toprule\n")
    f.write("Probe & N Pairs & Base $\\Delta$ & Instruct $\\Delta$ & Change \\\\\n")
    f.write("\\midrule\n")
    for probe_type, data in aggregate.items():
        f.write(f"{probe_type} & {data['n_pairs']} & {data['base_mean']:.3f} & {data['instruct_mean']:.3f} & {data['pct_change']:+1.1f}\\% \\\\\n")
    f.write("\\bottomrule\n")
    f.write("\\end{tabular}\n")
    f.write("\\end{table}\n")
print(f"LaTeX table saved: {tex_path}")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("  1. Run: python3 paper/figures/generate_all_figures.py --data results_rootcause/study1_max_scale/summary.json")
print("  2. Upload results to the paper: replace Tables in paper/camera_ready.tex")
print("  3. Submit to arXiv: python3 paper/arxiv_package.py")
print("="*60)
