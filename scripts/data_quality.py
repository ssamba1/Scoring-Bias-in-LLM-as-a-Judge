#!/usr/bin/env python3
"""
DATA QUALITY REPORT
- For each data file: row count, column count, missing values, data types, value ranges
- Check for: duplicates, outliers, impossible values, inconsistencies
- Generate: summary statistics for every numeric field
"""
import json, sys, statistics
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "results_rootcause" / "data_quality_report.json"

DATA_FILES = {
    "t4fam_results": BASE / "results_rootcause" / "t4fam_results.json",
    "study1_results": BASE / "results_rootcause" / "study1_results.json",
    "study1_max_scale": BASE / "results_rootcause" / "study1_max_scale.json",
    "rootcause_analysis": BASE / "results_rootcause" / "rootcause_analysis.json",
}


def analyze_json_data(file_key, file_path):
    """Analyze a JSON data file for quality metrics."""
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    with open(file_path) as f:
        data = json.load(f)

    report = {
        "file": file_key,
        "path": str(file_path),
        "exists": True,
        "file_size_bytes": file_path.stat().st_size,
        "top_level_type": type(data).__name__,
    }

    if isinstance(data, dict):
        top_keys = list(data.keys())
        report["num_top_level_keys"] = len(top_keys)
        report["top_level_keys"] = top_keys[:20]

        # Examine structure
        all_numeric_values = []
        probes_found = set()
        models_with_issues = []
        missing_probes = 0
        total_variants = 0
        variant_names = set()

        for model_name, probes in data.items():
            if model_name in ("metadata", "description", "method", "note", "interpretation"):
                continue
            if not isinstance(probes, dict):
                continue

            # Check each probe
            for probe_name, probe_variants in probes.items():
                if isinstance(probe_variants, dict):
                    probes_found.add(probe_name)
                    for variant_name, value in probe_variants.items():
                        variant_names.add(variant_name)
                        total_variants += 1
                        if value is None:
                            missing_probes += 1
                            models_with_issues.append((model_name, probe_name, variant_name, "missing"))
                        elif isinstance(value, (int, float)):
                            all_numeric_values.append(value)
                            if value < 0:
                                models_with_issues.append((model_name, probe_name, variant_name, "negative_value"))
                            elif value > 5:
                                models_with_issues.append((model_name, probe_name, variant_name, "above_max_scale"))
                        else:
                            models_with_issues.append((model_name, probe_name, variant_name, "non_numeric"))

        report["probes_found"] = list(probes_found)
        report["variant_names"] = list(variant_names)
        report["total_variant_entries"] = total_variants
        report["missing_values"] = missing_probes

        if all_numeric_values:
            report["numeric_summary"] = {
                "count": len(all_numeric_values),
                "mean": round(statistics.mean(all_numeric_values), 4),
                "stdev": round(statistics.stdev(all_numeric_values), 4) if len(all_numeric_values) > 1 else 0,
                "min": min(all_numeric_values),
                "max": max(all_numeric_values),
                "range": max(all_numeric_values) - min(all_numeric_values),
                "unique_values": len(set(all_numeric_values)),
            }
            # Outlier detection via IQR
            sorted_vals = sorted(all_numeric_values)
            n = len(sorted_vals)
            q1 = sorted_vals[int(n * 0.25)]
            q3 = sorted_vals[int(n * 0.75)]
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            outliers = [v for v in sorted_vals if v < lower_fence or v > upper_fence]
            report["outliers"] = {
                "method": "IQR (1.5*IQR rule)",
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_fence": lower_fence,
                "upper_fence": upper_fence,
                "num_outliers": len(outliers),
                "outlier_values": outliers[:20],
            }

        # Per-probe stats
        per_probe_stats = {}
        for p in sorted(probes_found):
            p_vals = []
            for model_name, probes in data.items():
                if model_name in ("metadata", "description", "method", "note", "interpretation"):
                    continue
                if isinstance(probes, dict) and p in probes and isinstance(probes[p], dict):
                    for v in probes[p].values():
                        if isinstance(v, (int, float)):
                            p_vals.append(v)
            if p_vals:
                per_probe_stats[p] = {
                    "count": len(p_vals),
                    "mean": round(statistics.mean(p_vals), 4),
                    "stdev": round(statistics.stdev(p_vals), 4) if len(p_vals) > 1 else 0,
                    "min": min(p_vals),
                    "max": max(p_vals),
                }
        report["per_probe_stats"] = per_probe_stats

        # Check for impossible values (outside 1-5 scale)
        if all_numeric_values:
            impossible = [v for v in all_numeric_values if v < 0 or v > 6]
            report["impossible_values"] = {
                "count": len(impossible),
                "values": impossible[:20],
                "note": "Standard scoring scale is 1-5. Values <0 or >6 are suspicious.",
            }

        # Duplicate model names check
        model_names = [k for k in top_keys if k not in ("metadata", "description", "method", "note", "interpretation")]
        report["num_models"] = len(model_names)
        if len(model_names) != len(set(model_names)):
            report["duplicate_model_names"] = True

        # Model naming issues
        naming_issues = [m for m in model_names if not m.replace("-", "").replace(".", "").replace("/", "").isalnum()]
        report["naming_issues"] = len(naming_issues)

        # Check for inconsistencies: all probes should have the same variant structure
        variant_structure = {}
        for model_name, probes in data.items():
            if not isinstance(probes, dict):
                continue
            for probe_name, probe_variants in probes.items():
                if isinstance(probe_variants, dict):
                    vset = frozenset(probe_variants.keys())
                    key = f"{probe_name}:{sorted(vset)}"
                    variant_structure[key] = variant_structure.get(key, 0) + 1
        report["variant_structure_uniqueness"] = len(variant_structure)
        report["variant_structures"] = {k: v for k, v in variant_structure.items()}

        report["num_issues"] = len(models_with_issues)
        report["sample_issues"] = models_with_issues[:10]

    elif isinstance(data, list):
        report["num_items"] = len(data)
    else:
        report["note"] = "Unexpected top-level type"

    return report


def main():
    print("=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)

    report = {}

    for file_key, file_path in DATA_FILES.items():
        print(f"\nAnalyzing: {file_key}")
        analysis = analyze_json_data(file_key, file_path)
        report[file_key] = analysis

        if "error" in analysis:
            print(f"  ERROR: {analysis['error']}")
            continue

        print(f"  File size: {analysis.get('file_size_bytes', '?')} bytes")
        print(f"  Top-level type: {analysis.get('top_level_type', '?')}")
        print(f"  Models/entries: {analysis.get('num_models', analysis.get('num_items', '?'))}")
        print(f"  Numeric values: {analysis.get('numeric_summary', {}).get('count', '?')}")
        if "outliers" in analysis:
            print(f"  Outliers (IQR): {analysis['outliers']['num_outliers']}")
        if "impossible_values" in analysis:
            print(f"  Impossible values: {analysis['impossible_values']['count']}")
        if "missing_values" in analysis:
            print(f"  Missing values: {analysis['missing_values']}")

    # Cross-file consistency checks
    print("\n--- Cross-file Consistency ---")
    cross_check = {}

    # Check if study1_results and study1_max_scale are identical
    if "study1_results" in report and "study1_max_scale" in report:
        s1_path = DATA_FILES["study1_results"]
        max_path = DATA_FILES["study1_max_scale"]
        if s1_path.exists() and max_path.exists():
            with open(s1_path) as f:
                s1 = json.load(f)
            with open(max_path) as f:
                max_s = json.load(f)
            s1_keys = set(k for k in s1 if isinstance(s1[k], dict) and "rubric_order" in s1[k])
            max_keys = set(k for k in max_s if isinstance(max_s[k], dict) and "rubric_order" in max_s[k])
            common = s1_keys & max_keys
            different = []
            for mk in common:
                if s1.get(mk) != max_s.get(mk):
                    different.append(mk)
            cross_check["study1_vs_max_scale"] = {
                "models_in_both": len(common),
                "models_with_differences": len(different),
                "sample_differences": different[:5],
            }
            print(f"  study1 vs max_scale: {len(different)} models differ out of {len(common)}")

    # Check if T4 models appear in rootcause_analysis
    if "t4fam_results" in report and "rootcause_analysis" in report:
        t4_path = DATA_FILES["t4fam_results"]
        rc_path = DATA_FILES["rootcause_analysis"]
        if t4_path.exists() and rc_path.exists():
            with open(t4_path) as f:
                t4 = json.load(f)
            with open(rc_path) as f:
                rc = json.load(f)
            t4_models = set(t4.keys())
            rc_models = set(rc.keys())
            missing_in_rc = t4_models - rc_models
            cross_check["t4_in_rootcause_analysis"] = {
                "t4_models": len(t4_models),
                "in_rc_analysis": len(t4_models & rc_models),
                "missing_from_rc": list(missing_in_rc),
            }
            print(f"  T4 models in rootcause_analysis: {len(t4_models & rc_models)}/{len(t4_models)}")

    report["cross_file_consistency"] = cross_check
    report["overall_assessment"] = assess_overall_quality(report)

    with open(OUT, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nData quality report saved to {OUT}")


def assess_overall_quality(report):
    """Provide an overall data quality assessment."""
    issues = []
    total_missing = sum(r.get("missing_values", 0) for r in report.values() if isinstance(r, dict))
    total_outliers = sum(r.get("outliers", {}).get("num_outliers", 0) for r in report.values() if isinstance(r, dict))
    total_impossible = sum(r.get("impossible_values", {}).get("count", 0) for r in report.values() if isinstance(r, dict))

    if total_missing > 0:
        issues.append(f"{total_missing} total missing values")
    if total_outliers > 10:
        issues.append(f"{total_outliers} potential outliers detected")
    if total_impossible > 0:
        issues.append(f"{total_impossible} impossible values found")

    if not issues:
        return {
            "grade": "PASS",
            "summary": "All data files pass quality checks. No missing values, outliers within expected range.",
        }
    else:
        return {
            "grade": "REVIEW",
            "summary": f"Issues found: {', '.join(issues)}",
            "details": issues,
        }


if __name__ == "__main__":
    main()
