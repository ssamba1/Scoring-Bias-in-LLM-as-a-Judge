#!/usr/bin/env python3
"""
BOOTSTRAP STABILITY ANALYSIS
- Bootstrap the entire analysis pipeline 1000 times
- Report 95% CI on every finding (mean Δ, effect sizes, etc.)
- Compare with the analytic CIs already computed in analysis_output/bootstrapped_cis.json
"""
import json, sys, statistics, random, math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "results_rootcause" / "bootstrap_stability.json"
T4_PATH = BASE / "results_rootcause" / "t4fam_results.json"
STUDY1_PATH = BASE / "results_rootcause" / "study1_results.json"
EXISTING_CIS = BASE / "results_rootcause" / "analysis_output" / "bootstrapped_cis.json"
COHENS_D = BASE / "results_rootcause" / "analysis_output" / "cohens_d.json"
MODEL_RANKING = BASE / "results_rootcause" / "analysis_output" / "model_ranking.json"

random.seed(42)

N_BOOTSTRAP = 1000
ALPHA = 0.05


def load_data():
    with open(T4_PATH) as f:
        t4 = json.load(f)
    with open(STUDY1_PATH) as f:
        s1 = json.load(f)
    existing_cis = None
    if EXISTING_CIS.exists():
        with open(EXISTING_CIS) as f:
            existing_cis = json.load(f)
    cohens_d = None
    if COHENS_D.exists():
        with open(COHENS_D) as f:
            cohens_d = json.load(f)
    model_ranking = None
    if MODEL_RANKING.exists():
        with open(MODEL_RANKING) as f:
            model_ranking = json.load(f)
    return t4, s1, existing_cis, cohens_d, model_ranking


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


def percentile_ci(values, alpha=0.05):
    """Compute percentile bootstrap CI."""
    sorted_vals = sorted(values)
    lower_idx = max(0, int(len(sorted_vals) * alpha / 2))
    upper_idx = min(len(sorted_vals) - 1, int(len(sorted_vals) * (1 - alpha / 2)))
    return sorted_vals[lower_idx], sorted_vals[upper_idx]


def bootstrap_analysis(data, n_bootstrap=N_BOOTSTRAP):
    """
    Bootstrap the entire pipeline: resample models with replacement, recompute deltas.
    """
    model_names = list(data.keys())
    probes = ["rubric_order", "score_id", "reference_answer"]

    bootstrap_means = {p: [] for p in probes}
    bootstrap_stdevs = {p: [] for p in probes}

    for i in range(n_bootstrap):
        # Resample models with replacement
        resampled = {}
        for _ in range(len(model_names)):
            chosen = random.choice(model_names)
            resampled[chosen] = data[chosen]

        deltas = compute_model_deltas(resampled)
        stats = compute_aggregate_stats(deltas)
        for p in probes:
            bootstrap_means[p].append(stats[p]["mean"])
            bootstrap_stdevs[p].append(stats[p]["stdev"])

    # Compute CIs
    results = {}
    for p in probes:
        ci_lower, ci_upper = percentile_ci(bootstrap_means[p])
        sd_lower, sd_upper = percentile_ci(bootstrap_stdevs[p])
        results[p] = {
            "mean": round(statistics.mean(bootstrap_means[p]), 4),
            "stdev": round(statistics.mean(bootstrap_stdevs[p]), 4),
            "ci_95_lower": round(ci_lower, 4),
            "ci_95_upper": round(ci_upper, 4),
            "ci_width": round(ci_upper - ci_lower, 4),
            "sd_ci_lower": round(sd_lower, 4),
            "sd_ci_upper": round(sd_upper, 4),
            "n_bootstrap": n_bootstrap,
        }

    return results


def bootstrap_cohens_d(data, n_bootstrap=N_BOOTSTRAP):
    """Bootstrap Cohen's d estimates."""
    model_names = list(data.keys())

    # Define probe control/biased pairs
    probe_pairs = {
        "rubric_order": ("normal", "reversed"),
        "score_id": ("numeric", "letter"),
        "reference_answer": ("no_ref", "good_ref"),
    }

    cohens_d = {p: [] for p in probe_pairs}

    for _ in range(n_bootstrap):
        resampled = {}
        for _ in range(len(model_names)):
            chosen = random.choice(model_names)
            resampled[chosen] = data[chosen]

        for p, (ctrl, biased) in probe_pairs.items():
            d_vals = []
            for model_name, probes in resampled.items():
                if p in probes and ctrl in probes[p] and biased in probes[p]:
                    control = probes[p][ctrl]
                    biased_val = probes[p][biased]
                    pooled_sd = math.sqrt(
                        (control ** 2 + biased_val ** 2) / 2.0
                    ) if control != 0 or biased_val != 0 else 1.0
                    d = (biased_val - control) / pooled_sd if pooled_sd > 0 else 0
                    d_vals.append(d)
            if d_vals:
                cohens_d[p].append(statistics.mean(d_vals))

    results = {}
    for p in probe_pairs:
        if cohens_d[p]:
            ci_l, ci_u = percentile_ci(cohens_d[p])
            results[p] = {
                "mean_d": round(statistics.mean(cohens_d[p]), 4),
                "ci_95_lower": round(ci_l, 4),
                "ci_95_upper": round(ci_u, 4),
                "ci_width": round(ci_u - ci_l, 4),
            }

    return results


def compare_with_existing(new_results, existing_cis):
    """Compare new bootstrap CIs with the existing analytic bootstrapped CIs.
    Matches dataset keys by checking if the existing key (e.g. 't4fam_base')
    maps to a corresponding new_results key (e.g. 't4fam_base' or 't4_base')."""
    comparison = {}
    for dataset_key, dataset_data in existing_cis.items():
        if dataset_key == "metadata":
            continue
        if dataset_key not in comparison:
            comparison[dataset_key] = {}

        # Map existing dataset key to new results key
        new_key = None
        for nk in new_results:
            # Exact match or abbreviated match (e.g., 't4fam_base' -> 't4fam_base', 't4_base')
            if nk == dataset_key:
                new_key = nk
                break
            # Handle abbreviated keys: 't4fam_base' -> key containing 't4' AND 'base'
            ds_parts = dataset_key.replace("t4fam_", "t4_").split("_")
            nk_parts = nk.split("_")
            if ds_parts == nk_parts:
                new_key = nk
                break
        if new_key is None:
            continue

        for probe_key, probe_data in dataset_data.items():
            if probe_key not in new_results[new_key]:
                continue

            existing_ci_lower = probe_data.get("ci_95_lower")
            existing_ci_upper = probe_data.get("ci_95_upper")
            existing_mean = probe_data.get("mean")
            new_match = new_results[new_key][probe_key]

            if existing_ci_lower is not None:
                ci_overlap = (
                    max(new_match["ci_95_lower"], existing_ci_lower),
                    min(new_match["ci_95_upper"], existing_ci_upper)
                )
                overlap_exists = ci_overlap[0] <= ci_overlap[1]
                comparison[dataset_key][probe_key] = {
                    "existing_mean": existing_mean,
                    "new_mean": new_match["mean"],
                    "existing_ci": [existing_ci_lower, existing_ci_upper],
                    "new_ci": [new_match["ci_95_lower"], new_match["ci_95_upper"]],
                    "cis_overlap": overlap_exists,
                    "mean_difference": round(new_match["mean"] - existing_mean, 4) if existing_mean else None,
                }

    return comparison


def main():
    print("=" * 60)
    print("BOOTSTRAP STABILITY ANALYSIS")
    print("=" * 60)

    t4_data, s1_data, existing_cis, cohens_d_data, model_ranking_data = load_data()

    # 1. Bootstrap T4 base models
    print("\n--- Bootstrap: T4 Base Models ---")
    t4_base_names = [m for m in t4_data if "IT" not in m]
    t4_base_data = {m: t4_data[m] for m in t4_base_names}
    t4_base_results = bootstrap_analysis(t4_base_data)

    # 2. Bootstrap T4 instruct models
    print("\n--- Bootstrap: T4 Instruct Models ---")
    t4_it_names = [m for m in t4_data if "IT" in m]
    t4_it_data = {m: t4_data[m] for m in t4_it_names}
    t4_it_results = bootstrap_analysis(t4_it_data)

    # 3. Bootstrap all T4 models together
    print("\n--- Bootstrap: All T4 Models ---")
    t4_all_results = bootstrap_analysis(t4_data)

    # 4. Bootstrap Study1 (22 instruct models)
    print("\n--- Bootstrap: Study1 (22 models) ---")
    s1_results = bootstrap_analysis(s1_data)

    # 5. Bootstrap Cohen's d on Study1
    print("\n--- Bootstrap Cohen's d: Study1 ---")
    d_results = bootstrap_cohens_d(s1_data)

    output = {
        "metadata": {
            "method": f"Bootstrap with {N_BOOTSTRAP} resamples, percentile CI (α={ALPHA})",
            "n_resamples": N_BOOTSTRAP,
        },
        "t4_base": t4_base_results,
        "t4_instruct": t4_it_results,
        "t4_all": t4_all_results,
        "study1_22": s1_results,
        "study1_cohens_d": d_results,
    }

    # Compare with existing analytic CIs
    if existing_cis:
        print("\n--- Comparison with Existing Analytic CIs ---")
        all_new = {
            "t4fam_base": t4_base_results,
            "t4fam_instruct": t4_it_results,
            "study1_22": s1_results,
        }
        comparison = compare_with_existing(all_new, existing_cis)
        output["comparison_with_existing"] = comparison

        for ds, probes in comparison.items():
            for p, info in probes.items():
                overlap = "OVERLAP" if info["cis_overlap"] else "MISMATCH"
                print(f"  {ds}/{p}: {overlap} — existing CI={info['existing_ci']}, "
                      f"new CI={info['new_ci']}, mean_diff={info['mean_difference']}")

    # Summarize
    print("\n--- Key Bootstrap Results ---")
    for label, results in [("T4 base", t4_base_results), ("T4 instruct", t4_it_results),
                           ("Study1 22", s1_results)]:
        print(f"\n  {label}:")
        for p, info in results.items():
            print(f"    {p}: Δ={info['mean']:.4f} [95% CI: {info['ci_95_lower']:.4f}, {info['ci_95_upper']:.4f}]")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
