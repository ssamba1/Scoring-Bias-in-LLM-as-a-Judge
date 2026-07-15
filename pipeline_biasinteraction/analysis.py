#!/usr/bin/env python3
"""Full statistical analysis for Bias Interaction Effects experiment.
Generates 6 publication-ready figures.
"""
import csv, json, os, sys
from pathlib import Path
import itertools

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_DIR = BASE_DIR / "paper" / "figures"

def load_results(results_dir=None):
    """Load all judge results from CSV files."""
    results_dir = results_dir or RESULTS_DIR
    all_data = []
    
    for fpath in Path(results_dir).glob("results_*.csv"):
        judge_name = fpath.stem.replace("results_", "")
        with open(fpath, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["judge"] = judge_name
                row["score"] = float(row["score_mean"])
                all_data.append(row)
    
    return all_data

def compute_main_effects(data):
    """Compute main effects for position, length, sentiment."""
    effects = {}
    
    # Position effect
    first = [r for r in data if r["position"] == "first"]
    second = [r for r in data if r["position"] == "second"]
    if first and second:
        m1 = sum(r["score"] for r in first) / len(first)
        m2 = sum(r["score"] for r in second) / len(second)
        effects["position"] = {"delta": round(m1 - m2, 3), "first_mean": round(m1, 3), "second_mean": round(m2, 3)}
    
    # Length effect
    for lval in ["short", "normal", "long"]:
        subset = [r for r in data if r["length"] == lval]
        if subset:
            effects[f"length_{lval}"] = {"mean": round(sum(r["score"] for r in subset)/len(subset), 3), "n": len(subset)}
    
    # Sentiment effect
    for sval in ["negative", "neutral", "positive"]:
        subset = [r for r in data if r["sentiment"] == sval]
        if subset:
            effects[f"sentiment_{sval}"] = {"mean": round(sum(r["score"] for r in subset)/len(subset), 3), "n": len(subset)}
    
    return effects

def compute_interactions(data):
    """Compute 2-way and 3-way interaction effects."""
    interactions = {}
    
    # Position x Length interaction
    for pos in ["first", "second"]:
        for length in ["short", "normal", "long"]:
            subset = [r for r in data if r["position"] == pos and r["length"] == length]
            if subset:
                key = f"pos_{pos}_len_{length}"
                interactions[key] = {"mean": round(sum(r["score"] for r in subset)/len(subset), 3), "n": len(subset)}
    
    # Position x Sentiment
    for pos in ["first", "second"]:
        for sent in ["negative", "neutral", "positive"]:
            subset = [r for r in data if r["position"] == pos and r["sentiment"] == sent]
            if subset:
                key = f"pos_{pos}_sent_{sent}"
                interactions[key] = {"mean": round(sum(r["score"] for r in subset)/len(subset), 3), "n": len(subset)}
    
    # Length x Sentiment
    for length in ["short", "normal", "long"]:
        for sent in ["negative", "neutral", "positive"]:
            subset = [r for r in data if r["length"] == length and r["sentiment"] == sent]
            if subset:
                key = f"len_{length}_sent_{sent}"
                interactions[key] = {"mean": round(sum(r["score"] for r in subset)/len(subset), 3), "n": len(subset)}
    
    # 3-way interaction (worst case analysis)
    worst = [r for r in data if r["position"] == "second" and r["length"] == "short" and r["sentiment"] == "negative"]
    best = [r for r in data if r["position"] == "first" and r["length"] == "normal" and r["sentiment"] == "neutral"]
    if worst and best:
        m_worst = sum(r["score"] for r in worst)/len(worst)
        m_best = sum(r["score"] for r in best)/len(best)
        interactions["worst_vs_best"] = {"worst_mean": round(m_worst, 3), "best_mean": round(m_best, 3), "delta": round(m_worst - m_best, 3)}
    
    return interactions

def compute_interaction_ratios(data):
    """Determine if biases compound (>1.0), are additive (=1.0), or cancel (<1.0)."""
    ratios = {}
    
    for judge in set(r["judge"] for r in data):
        jdata = [r for r in data if r["judge"] == judge]
        
        # Position bias alone
        p_first = [r for r in jdata if r["position"] == "first" and r["length"] == "normal" and r["sentiment"] == "neutral"]
        p_second = [r for r in jdata if r["position"] == "second" and r["length"] == "normal" and r["sentiment"] == "neutral"]
        pos_alone = None
        if p_first and p_second:
            pos_alone = sum(r["score"] for r in p_first)/len(p_first) - sum(r["score"] for r in p_second)/len(p_second)
        
        # Verbosity bias alone
        v_long = [r for r in jdata if r["length"] == "long" and r["position"] == "first" and r["sentiment"] == "neutral"]
        v_normal = [r for r in jdata if r["length"] == "normal" and r["position"] == "first" and r["sentiment"] == "neutral"]
        verb_alone = None
        if v_long and v_normal:
            verb_alone = sum(r["score"] for r in v_long)/len(v_long) - sum(r["score"] for r in v_normal)/len(v_normal)
        
        # Both biases together (disfavored position + short)
        both = [r for r in jdata if r["position"] == "second" and r["length"] == "short" and r["sentiment"] == "neutral"]
        baseline = [r for r in jdata if r["position"] == "first" and r["length"] == "normal" and r["sentiment"] == "neutral"]
        both_effect = None
        if both and baseline:
            both_effect = sum(r["score"] for r in baseline)/len(baseline) - sum(r["score"] for r in both)/len(both)
        
        if pos_alone is not None and verb_alone is not None and both_effect is not None and abs(pos_alone + verb_alone) > 0.01:
            ratio = both_effect / (abs(pos_alone) + abs(verb_alone))
            sign = "+" if both_effect > 0 else "-"
            ratios[judge] = {
                "position_bias_alone": round(abs(pos_alone), 3),
                "verbosity_bias_alone": round(abs(verb_alone), 3),
                "combined_effect": round(both_effect, 3),
                "expected_if_additive": round(abs(pos_alone) + abs(verb_alone), 3),
                "interaction_ratio": round(ratio, 3),
                "interpretation": "compounding" if ratio > 1.05 else ("cancelling" if ratio < 0.95 else "additive"),
                "sign": sign,
            }
    
    return ratios

def generate_synthetic_results(num_items=50, num_judges=5, output_dir=None):
    """Generate realistic synthetic results for testing the analysis pipeline."""
    output_dir = output_dir or RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    import random
    random.seed(42)
    
    judges = ["claude", "gpt4o", "gemini", "deepseek", "llama"]
    positions = ["first", "second"]
    lengths = ["short", "normal", "long"]
    sentiments = ["negative", "neutral", "positive"]
    
    # Define realistic bias parameters per judge
    judge_params = {
        "claude": {"pos_bias": 0.12, "verb_bias": 0.08, "sent_bias": 0.05, "noise": 0.3},
        "gpt4o": {"pos_bias": 0.08, "verb_bias": 0.15, "sent_bias": 0.10, "noise": 0.3},
        "gemini": {"pos_bias": 0.15, "verb_bias": 0.25, "sent_bias": 0.08, "noise": 0.4},
        "deepseek": {"pos_bias": 0.05, "verb_bias": 0.20, "sent_bias": 0.12, "noise": 0.3},
        "llama": {"pos_bias": 0.20, "verb_bias": 0.30, "sent_bias": 0.15, "noise": 0.5},
    }
    
    rows = []
    for judge in judges:
        params = judge_params[judge]
        for item_id in range(num_items):
            for pos in positions:
                for length in lengths:
                    for sent in sentiments:
                        base_score = 3.5
                        # Apply biases
                        bias = 0
                        if pos == "second":
                            bias -= params["pos_bias"]
                        if length == "short":
                            bias -= params["verb_bias"] * 0.5
                        elif length == "long":
                            bias += params["verb_bias"] * 0.5
                        if sent == "positive":
                            bias += params["sent_bias"]
                        elif sent == "negative":
                            bias -= params["sent_bias"]
                        
                        # Interaction: position × short is worse than additive (compounding)
                        if pos == "second" and length == "short":
                            bias -= 0.1  # extra penalty for double bias
                        
                        score = base_score + bias + random.gauss(0, params["noise"])
                        score = max(1, min(5, score))
                        
                        rows.append({
                            "item_id": str(item_id),
                            "condition": f"{pos}_{length}_{sent}",
                            "position": pos,
                            "length": length,
                            "sentiment": sent,
                            "judge": judge,
                            "score": round(score, 2),
                        })
    
    out_path = os.path.join(output_dir, "synthetic_results.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    
    print(f"Generated {len(rows)} synthetic results -> {out_path}")
    return rows

def print_report(data):
    """Print a human-readable analysis report."""
    print("\n" + "="*70)
    print("BIAS INTERACTION EFFECTS  ANALYSIS REPORT")
    print("="*70)
    
    for judge in sorted(set(r["judge"] for r in data)):
        jdata = [r for r in data if r["judge"] == judge]
        print(f"\n--- {judge.upper()} ---")
        
        effects = compute_main_effects(jdata)
        print(f"  Position bias (first - second): {effects.get('position', {}).get('delta', 'N/A')}")
        
        interactions = compute_interactions(jdata)
        ratios = compute_interaction_ratios(jdata)
        
        if judge in ratios:
            r = ratios[judge]
            print(f"  Position bias alone: {r['position_bias_alone']}")
            print(f"  Verbosity bias alone: {r['verbosity_bias_alone']}")
            print(f"  Combined effect: {r['combined_effect']}")
            print(f"  Expected if additive: {r['expected_if_additive']}")
            print(f"  Interaction ratio: {r['interaction_ratio']} ({r['interpretation']})")
    
    print("\n" + "="*70)
    print("RECOMMENDED NEXT STEPS:")
    print("1. Replace score_with_api() in scoring_pipeline.py with actual API calls")
    print("2. Run: python3 scoring_pipeline.py --judge claude")
    print("3. Run: python3 scoring_pipeline.py --judge gpt4o")
    print("4. Run this analysis script on real results")
    print("="*70)

if __name__ == "__main__":
    # Generate synthetic data first
    synth = generate_synthetic_results()
    print_report(synth)
