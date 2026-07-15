#!/usr/bin/env python3
"""
CROSS-VALIDATION STUDY
- Leave-one-family-out cross-validation on T4 families
- K-fold (K=3) cross-validation
- Robustness ranking: which finding is most/least robust to data removal
"""
import json, sys, statistics, random
from pathlib import Path
from copy import deepcopy

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "results_rootcause" / "cross_validation.json"
T4_PATH = BASE / "results_rootcause" / "t4fam_results.json"
STUDY1_PATH = BASE / "results_rootcause" / "study1_results.json"

random.seed(42)


def load_data():
    with open(T4_PATH) as f:
        t4 = json.load(f)
    with open(STUDY1_PATH) as f:
        s1 = json.load(f)
    return t4, s1


def compute_delta(probe_data):
    vals = list(probe_data.values())
    if len(vals) < 2:
        return 0.0
    first = vals[0]
    return max(abs(v - first) for v in vals[1:])


def compute_model_deltas(data):
    """Compute per-model per-probe deltas (max - baseline)."""
    deltas = {}
    for model_name, probes in data.items():
        deltas[model_name] = {p: compute_delta(probes[p]) for p in probes}
    return deltas


def compute_aggregate_stats(deltas):
    """Compute mean delta per probe across all models."""
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


def leave_one_family_out(t4_data, pairs):
    """
    For each family, remove BOTH base and instruct models, recompute aggregate findings.
    """
    results = {}
    families_ordered = sorted(set(p[0] for p in pairs))

    # Full data baseline
    all_deltas = compute_model_deltas(t4_data)
    full_stats = compute_aggregate_stats(all_deltas)
    results["all_families"] = {"n_families": len(families_ordered), "stats": full_stats}

    loo_results = {}
    for family_base, family_it in pairs:
        subset = {m: v for m, v in t4_data.items()
                  if m != family_base and m != family_it}
        loo_deltas = compute_model_deltas(subset)
        loo_stats = compute_aggregate_stats(loo_deltas)

        # Compute change from full
        changes = {}
        for p in full_stats:
            changes[p] = {
                "full_mean": full_stats[p]["mean"],
                "loo_mean": loo_stats[p]["mean"],
                "change": round(loo_stats[p]["mean"] - full_stats[p]["mean"], 4),
                "pct_change": round(
                    100 * (loo_stats[p]["mean"] - full_stats[p]["mean"]) / full_stats[p]["mean"]
                    if full_stats[p]["mean"] != 0 else 0, 2
                ),
            }

        loo_results[f"{family_base}_+_{family_it}"] = {
            "family_base": family_base,
            "family_instruct": family_it,
            "n_families": len(families_ordered) - 1,
            "changes": changes,
            "stats": loo_stats,
        }

    results["leave_one_out"] = loo_results

    # Robustness ranking: which finding is most stable?
    # Measure = mean absolute % change across all LOO folds
    probe_robustness = {}
    for p in full_stats:
        pct_changes = []
        for loo_key, loo_val in loo_results.items():
            pct_changes.append(abs(loo_val["changes"][p]["pct_change"]))
        probe_robustness[p] = {
            "mean_abs_pct_change": round(statistics.mean(pct_changes), 2),
            "max_abs_pct_change": round(max(pct_changes), 2),
            "stability_rank": None,
        }

    # Rank: lower mean_abs_pct_change = more robust
    sorted_probes = sorted(probe_robustness.items(), key=lambda x: x[1]["mean_abs_pct_change"])
    for rank, (probe, _) in enumerate(sorted_probes, 1):
        probe_robustness[probe]["stability_rank"] = rank
        probe_robustness[probe]["label"] = (
            "most_robust" if rank == 1 else
            "least_robust" if rank == len(sorted_probes) else "intermediate"
        )

    # Which family removal causes the biggest change?
    family_impact = {}
    for loo_key, loo_val in loo_results.items():
        family_impact[loo_key] = {
            "family_base": loo_val["family_base"],
            "mean_abs_change": round(
                statistics.mean(abs(loo_val["changes"][p]["change"]) for p in loo_val["changes"]), 4
            ),
        }
    sorted_families = sorted(family_impact.items(), key=lambda x: x[1]["mean_abs_change"], reverse=True)
    for rank, (fam_key, fam_val) in enumerate(sorted_families, 1):
        family_impact[fam_key]["impact_rank"] = rank
        family_impact[fam_key]["impact_label"] = (
            "most_influential" if rank == 1 else
            "least_influential" if rank == len(sorted_families) else "intermediate"
        )

    results["probe_robustness"] = probe_robustness
    results["family_impact"] = family_impact
    return results


def kfold_cross_validation(t4_data, pairs, k=3):
    """K-fold: split families into k groups, recompute per group."""
    families = list(pairs)
    random.shuffle(families)
    folds = [[] for _ in range(k)]
    for i, fam in enumerate(families):
        folds[i % k].append(fam)

    results = {"k": k, "folds": []}
    for fold_idx, fold_families in enumerate(folds):
        fold_models = set()
        for fb, fi in fold_families:
            fold_models.add(fb)
            fold_models.add(fi)
        subset = {m: v for m, v in t4_data.items() if m in fold_models}
        loo_deltas = compute_model_deltas(subset)
        loo_stats = compute_aggregate_stats(loo_deltas)
        results["folds"].append({
            "fold": fold_idx + 1,
            "n_families": len(fold_families),
            "families": [fb for fb, _ in fold_families],
            "stats": loo_stats,
        })

    # Cross-fold means and variances
    probes = ["rubric_order", "score_id", "reference_answer"]
    cross_fold = {}
    for p in probes:
        means = [f["stats"][p]["mean"] for f in results["folds"]]
        cross_fold[p] = {
            "mean_across_folds": round(statistics.mean(means), 4),
            "stdev_across_folds": round(statistics.stdev(means), 4) if len(means) > 1 else 0,
            "min_fold": round(min(means), 4),
            "max_fold": round(max(means), 4),
            "range": round(max(means) - min(means), 4),
        }
    results["cross_fold_summary"] = cross_fold

    # Also run on study1 (22 instruct models) using leave-one-model-out
    return results


def leave_one_model_out_study1(s1_data):
    """Leave-one-model-out on the 22 study1 instruct models."""
    models = list(s1_data.keys())
    full_deltas = compute_model_deltas(s1_data)
    full_stats = compute_aggregate_stats(full_deltas)

    results = {
        "n_models": len(models),
        "full_stats": full_stats,
        "loo_results": {},
    }

    for left_out in models:
        subset = {m: v for m, v in s1_data.items() if m != left_out}
        loo_deltas = compute_model_deltas(subset)
        loo_stats = compute_aggregate_stats(loo_deltas)

        changes = {}
        for p in full_stats:
            changes[p] = {
                "full_mean": full_stats[p]["mean"],
                "loo_mean": loo_stats[p]["mean"],
                "change": round(loo_stats[p]["mean"] - full_stats[p]["mean"], 4),
            }
        results["loo_results"][left_out] = {
            "n_models": len(models) - 1,
            "changes": changes,
        }

    return results


def main():
    print("=" * 60)
    print("CROSS-VALIDATION STUDY")
    print("=" * 60)

    t4_data, s1_data = load_data()

    # T4 family pairs
    t4_pairs = [
        ("Qwen2.5-0.5B", "Qwen2.5-0.5B-IT"),
        ("Qwen2.5-1.5B", "Qwen2.5-1.5B-IT"),
        ("Llama-3.2-1B", "Llama-3.2-1B-IT"),
        ("Llama-3.2-3B", "Llama-3.2-3B-IT"),
        ("Gemma-2-2B", "Gemma-2-2B-IT"),
        ("StableLM-2-1.6B", "StableLM-2-1.6B-IT"),
        ("Qwen2.5-7B", "Qwen2.5-7B-IT"),
    ]

    print(f"\nT4 families: {len(t4_pairs)}")
    print(f"Study1 instruct models: {len(s1_data)}")

    # 1. Leave-one-family-out on T4
    print("\n--- Leave-One-Family-Out (T4) ---")
    loo_results = leave_one_family_out(t4_data, t4_pairs)

    print("\nProbe robustness ranking (most robust first):")
    sorted_probes = sorted(
        loo_results["probe_robustness"].items(),
        key=lambda x: x[1]["stability_rank"],
    )
    for probe, info in sorted_probes:
        print(f"  {probe}: rank={info['stability_rank']}, "
              f"mean|%Δ|={info['mean_abs_pct_change']}%")

    print("\nFamily impact ranking (most influential first):")
    sorted_families = sorted(
        loo_results["family_impact"].items(),
        key=lambda x: x[1]["impact_rank"],
    )
    for fam_key, info in sorted_families:
        print(f"  {info['family_base']}: rank={info['impact_rank']}, "
              f"mean|Δ|={info['mean_abs_change']}")

    # 2. K-fold on T4
    print("\n--- K-Fold (K=3) on T4 ---")
    kf_results = kfold_cross_validation(t4_data, t4_pairs, k=3)
    print("Cross-fold summary:")
    for p, info in kf_results["cross_fold_summary"].items():
        print(f"  {p}: mean={info['mean_across_folds']}, "
              f"stdev={info['stdev_across_folds']}, "
              f"range={info['range']}")

    # 3. Leave-one-model-out on Study1
    print("\n--- Leave-One-Model-Out (Study1, 22 models) ---")
    s1_loo = leave_one_model_out_study1(s1_data)

    # Overall
    output = {
        "method": "Cross-validation: LOO-family + K-fold + LOO-model",
        "t4_leave_one_family_out": loo_results,
        "t4_kfold": kf_results,
        "study1_leave_one_model_out": s1_loo,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
