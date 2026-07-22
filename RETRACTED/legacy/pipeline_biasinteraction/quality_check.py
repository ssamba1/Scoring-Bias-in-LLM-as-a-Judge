#!/usr/bin/env python3
"""Data quality checker for bias experiment results.
Validates scores, detects anomalies, generates quality reports.
"""
import csv, json, sys, os
from pathlib import Path
from collections import Counter
import math

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"

def load_results(path=None):
    path = path or RESULTS_DIR / "bias_interaction_synthetic.csv"
    if not path.exists():
        print(f"File not found: {path}")
        return None
    with open(path) as f:
        data = list(csv.DictReader(f))
    for r in data:
        r["score"] = float(r["score"])
    return data

def check_score_range(data):
    """Check all scores are valid (1-5)."""
    scores = [r["score"] for r in data]
    out_of_range = [s for s in scores if s < 1 or s > 5]
    print(f"\n1. Score Range Check")
    print(f"   Total scores: {len(scores)}")
    print(f"   In range 1-5: {len(scores) - len(out_of_range)} ({100*(1-len(out_of_range)/len(scores)):.1f}%)")
    if out_of_range:
        print(f"   OUT OF RANGE: {len(out_of_range)}")
        print(f"   Examples: {out_of_range[:10]}")
    else:
        print(f"   ✓ ALL IN RANGE")
    return len(out_of_range) == 0

def check_missing_data(data):
    """Check for missing values."""
    missing = 0
    for r in data:
        for k, v in r.items():
            if v is None or v == "" or v == "nan":
                missing += 1
    print(f"\n2. Missing Data Check")
    print(f"   Total fields: {len(data) * len(data[0].keys())}")
    print(f"   {'✓ NO MISSING DATA' if missing == 0 else f'✗ {missing} MISSING VALUES'}")
    return missing == 0

def check_judge_distribution(data):
    """Check each judge has approximately equal items."""
    judges = Counter(r["judge"] for r in data)
    print(f"\n3. Judge Distribution")
    for judge, count in judges.most_common():
        print(f"   {judge:<12} {count:>6} items")

    counts = list(judges.values())
    if len(counts) > 1:
        cv = (max(counts) - min(counts)) / (sum(counts)/len(counts))
        status = "✓ BALANCED" if cv < 0.1 else "⚠ IMBALANCED"
        print(f"   {status} (CV={cv:.3f})")

def check_condition_coverage(data):
    """Check all conditions are represented."""
    conditions = Counter((r["judge"], r["condition"]) for r in data)
    print(f"\n4. Condition Coverage")
    print(f"   Unique judge-condition pairs: {len(conditions)}")

    # Expected: 5 judges × 8 conditions = 40
    if len(conditions) == 40:
        print(f"   ✓ ALL 40 JUDGE-CONDITION PAIRS PRESENT")
    else:
        print(f"   ⚠ Expected 40, got {len(conditions)}")
        missing = []
        for judge in set(r["judge"] for r in data):
            for cond in set(r["condition"] for r in data):
                if (judge, cond) not in conditions:
                    missing.append(f"{judge}/{cond}")
        if missing:
            print(f"   Missing: {missing}")

def check_score_distribution(data):
    """Check score distribution per judge."""
    print(f"\n5. Score Distribution (per judge)")
    print(f"{'Judge':<12} {'1':>6} {'2':>6} {'3':>6} {'4':>6} {'5':>6} {'Mean':>6}")
    print("-"*48)
    for judge in sorted(set(r["judge"] for r in data)):
        jd = [r for r in data if r["judge"] == judge]
        scores = [r["score"] for r in jd]
        hist = Counter(int(round(s)) for s in scores)
        mean = sum(scores)/len(scores)
        print(f"{judge:<12} {hist.get(1,0):>6} {hist.get(2,0):>6} {hist.get(3,0):>6} {hist.get(4,0):>6} {hist.get(5,0):>6} {mean:>6.2f}")

def check_anomalous_items(data):
    """Detect items with unusually high variance across conditions."""
    print(f"\n6. Anomalous Items (high variance across conditions)")

    items = {}
    for r in data:
        key = (r["judge"], r["item_id"])
        if key not in items:
            items[key] = []
        items[key].append(r["score"])

    # Find items with high variance
    high_var = []
    for (judge, item_id), scores in items.items():
        var = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
        if var > 1.0:  # threshold
            high_var.append((judge, item_id, round(var, 3)))

    if high_var:
        print(f"   Found {len(high_var)} items with variance > 1.0")
        for judge, item_id, var in high_var[:10]:
            print(f"   {judge:<10} item {item_id:<5} var={var}")
    else:
        print(f"   ✓ No anomalous items detected")

def generate_report(data, output_path=None):
    """Generate full quality report."""
    print("="*65)
    print("DATA QUALITY REPORT  Bias Interaction Experiment")
    print("="*65)

    checks = [
        check_score_range(data),
        check_missing_data(data),
        check_judge_distribution(data),
        check_condition_coverage(data),
        check_score_distribution(data),
        check_anomalous_items(data),
    ]

    all_pass = all(c for c in checks if isinstance(c, bool))
    print("\n" + "="*65)
    print(f"{'✓ ALL CHECKS PASSED' if all_pass else '✗ SOME CHECKS FAILED'}")
    print("="*65)

    if output_path:
        # Redirect output to file (simplified)
        print(f"\n(Report would save to {output_path})")

if __name__ == "__main__":
    data = load_results()
    if data:
        generate_report(data)
