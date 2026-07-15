#!/usr/bin/env python3
"""
SIMULATION STUDY
- Generate synthetic data with known ground-truth Δ values
- Run analysis pipeline on synthetic data
- Measure recovery of known Δ values
- Test at different effect sizes (Δ = 0.1, 0.3, 0.5, 0.8, 1.0)
- Test at different N (N = 5, 10, 15, 20 families)
"""
import json, sys, statistics, math, random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "results_rootcause" / "simulation_results.json"

random.seed(42)


def generate_synthetic_family(base_score, effect_size, n_variants=8):
    """
    Generate synthetic scores for one family.
    base_score: ground-truth score
    effect_size: Δ to add to biased variants
    n_variants: number of scoring variants (default 8 = 2 rubric_order + 3 score_id + 3 reference_answer)
    """
    # We simulate scores for 8 variants matching the real probe structure
    variants = {
        "rubric_order": {
            "normal": round(base_score + random.gauss(0, 0.3), 1),
            "reversed": round(base_score + effect_size + random.gauss(0, 0.3), 1),
        },
        "score_id": {
            "numeric": round(base_score + random.gauss(0, 0.3), 1),
            "letter": round(base_score + effect_size + random.gauss(0, 0.3), 1),
            "descriptive": round(base_score + random.gauss(0, 0.3), 1),
        },
        "reference_answer": {
            "no_ref": round(base_score + random.gauss(0, 0.3), 1),
            "good_ref": round(base_score + effect_size + random.gauss(0, 0.3), 1),
            "poor_ref": round(base_score + random.gauss(0, 0.3), 1),
        },
    }
    return variants


def compute_delta(probe_data):
    vals = list(probe_data.values())
    if len(vals) < 2:
        return 0.0
    first = vals[0]
    return max(abs(v - first) for v in vals[1:])


def compute_model_deltas(data):
    deltas = {}
    for model_name, probes in data.items():
        deltas[model_name] = {p: compute_delta(probes[p]) for p in probes}
    return deltas


def compute_aggregate_stats(deltas):
    probes = ["rubric_order", "score_id", "reference_answer"]
    stats = {}
    for p in probes:
        vals = [deltas[m][p] for m in deltas if p in deltas[m]]
        stats[p] = {
            "mean": round(statistics.mean(vals), 4),
            "stdev": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0,
            "n": len(vals),
        }
    return stats


def run_simulation(n_families, true_effect_size):
    """Generate data for n_families, run analysis, return recovered Δ."""
    base_score = 3.0  # typical baseline
    data = {}
    for i in range(n_families):
        fam_name = f"SynthModel-{i+1}"
        data[fam_name] = generate_synthetic_family(base_score, true_effect_size)

    deltas = compute_model_deltas(data)
    stats = compute_aggregate_stats(deltas)

    # Average recovered effect across all probes
    recovered_mean = statistics.mean(stats[p]["mean"] for p in stats)
    recovery_error = recovered_mean - true_effect_size
    recovery_pct_error = (recovery_error / true_effect_size) * 100 if true_effect_size != 0 else 0

    return {
        "n_families": n_families,
        "true_effect_size": true_effect_size,
        "recovered_mean_delta": round(recovered_mean, 4),
        "recovery_error": round(recovery_error, 4),
        "recovery_pct_error": round(recovery_pct_error, 2),
        "per_probe": stats,
        "data_generated": len(data),
    }


def main():
    print("=" * 60)
    print("SIMULATION STUDY — Synthetic Data Recovery")
    print("=" * 60)

    effect_sizes = [0.1, 0.3, 0.5, 0.8, 1.0]
    n_families_list = [5, 10, 15, 20]

    all_results = {}
    all_results["metadata"] = {
        "description": "Synthetic data pipeline validation",
        "n_repetitions": 1,
        "effect_sizes_tested": effect_sizes,
        "n_families_tested": n_families_list,
    }

    # Grid search
    grid_results = {}
    for ne in effect_sizes:
        for nf in n_families_list:
            key = f"Δ={ne}_N={nf}"
            result = run_simulation(nf, ne)
            grid_results[key] = result
            print(f"  {key}: recovered Δ mean = {result['recovered_mean_delta']:.4f}, "
                  f"error = {result['recovery_error']:.4f} ({result['recovery_pct_error']:+.2f}%)")
    all_results["grid"] = grid_results

    # Summary analysis
    summary = {"effect_size_recovery": {}, "sample_size_recovery": {}}

    for es in effect_sizes:
        es_results = [v for k, v in grid_results.items() if f"Δ={es}" in k]
        errors = [r["recovery_error"] for r in es_results]
        summary["effect_size_recovery"][str(es)] = {
            "mean_abs_error": round(statistics.mean(abs(e) for e in errors), 4),
            "mean_error": round(statistics.mean(errors), 4),
            "n_conditions": len(es_results),
        }

    for nf in n_families_list:
        nf_results = [v for k, v in grid_results.items() if f"_N={nf}" in k]
        errors = [r["recovery_error"] for r in nf_results]
        summary["sample_size_recovery"][str(nf)] = {
            "mean_abs_error": round(statistics.mean(abs(e) for e in errors), 4),
            "mean_error": round(statistics.mean(errors), 4),
            "n_conditions": len(nf_results),
        }

    all_results["summary"] = summary

    # Interpretation
    all_results["interpretation"] = (
        "Recovery error = recovered_mean_delta - true_effect_size. "
        "Values near 0 indicate accurate recovery. "
        "Larger N should reduce error. Larger effect sizes may be easier to detect."
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
