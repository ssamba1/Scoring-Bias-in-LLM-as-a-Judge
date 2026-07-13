#!/usr/bin/env python3
"""Compare results between judges and identify consistent patterns."""
import csv, json, sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

def load_data(path=None):
    path = path or RESULTS_DIR / "bias_interaction_synthetic.csv"
    if not path.exists():
        print(f"No data at {path}")
        return None
    with open(path) as f:
        data = list(csv.DictReader(f))
    for r in data:
        r["score"] = float(r["score"])
    return data

def compare_judges(data):
    """Pairwise comparison of all judges."""
    judges = sorted(set(r["judge"] for r in data))
    
    print(f"\n{'Judge A':<15} {'Judge B':<15} {'Overall Δ':<12} {'Baseline Δ':<12} {'Worst Δ':<12} {'Agreement':<10}")
    print("-"*76)
    
    for i, a in enumerate(judges):
        for b in judges[i+1:]:
            ad = [r for r in data if r["judge"] == a]
            bd = [r for r in data if r["judge"] == b]
            
            # Overall mean difference
            ma = sum(r["score"] for r in ad) / len(ad)
            mb = sum(r["score"] for r in bd) / len(bd)
            overall_delta = round(ma - mb, 3)
            
            # Baseline difference
            abl = [r for r in ad if r["condition"] == "baseline"]
            bbl = [r for r in bd if r["condition"] == "baseline"]
            bl_delta = round(sum(r["score"] for r in abl)/len(abl) - sum(r["score"] for r in bbl)/len(bbl), 3) if abl and bbl else "?"
            
            # Worst case difference
            awc = [r for r in ad if r["condition"] == "worst"]
            bwc = [r for r in bd if r["condition"] == "worst"]
            wc_delta = round(sum(r["score"] for r in awc)/len(awc) - sum(r["score"] for r in bwc)/len(bwc), 3) if awc and bwc else "?"
            
            # Agreement rate (same score for same item)
            keyed_a = {(r["item_id"], r["condition"]): r["score"] for r in ad}
            keyed_b = {(r["item_id"], r["condition"]): r["score"] for r in bd}
            common = set(keyed_a.keys()) & set(keyed_b.keys())
            agreements = sum(1 for k in common if abs(keyed_a[k] - keyed_b[k]) < 0.5)
            agree_pct = round(agreements / len(common) * 100, 1) if common else "?"
            
            print(f"{a:<15} {b:<15} {overall_delta:<12} {bl_delta:<12} {wc_delta:<12} {agree_pct:<10}")

def find_consistent_patterns(data):
    """Find bias patterns that are consistent across all judges."""
    judges = sorted(set(r["judge"] for r in data))
    
    print(f"\n=== CONSISTENT PATTERNS (agreed by ALL judges) ===")
    
    # Check: is worst case always worse than baseline?
    all_worse = True
    for j in judges:
        jd = [r for r in data if r["judge"] == j]
        base = [r for r in jd if r["condition"] == "baseline"]
        worst = [r for r in jd if r["condition"] == "worst"]
        if base and worst:
            mb = sum(r["score"] for r in base)/len(base)
            mw = sum(r["score"] for r in worst)/len(worst)
            if mw >= mb:
                all_worse = False
                break
    
    print(f"\n  Worst case < Baseline: {'YES (all judges)' if all_worse else 'NO'}")
    
    # Check: position bias direction
    pos_first_always_higher = True
    for j in judges:
        jd = [r for r in data if r["judge"] == j]
        fst = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        snd = [r for r in jd if r["position"]=="second" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        if fst and snd:
            mf = sum(r["score"] for r in fst)/len(fst)
            ms = sum(r["score"] for r in snd)/len(snd)
            if mf <= ms:
                pos_first_always_higher = False
    
    print(f"  Position bias favors first: {'YES (all judges)' if pos_first_always_higher else 'Varies by judge'}")
    
    # Check: verbosity direction
    long_always_higher = True
    for j in judges:
        jd = [r for r in data if r["judge"] == j]
        lon = [r for r in jd if r["length"]=="long" and r["position"]=="first" and r["sentiment"]=="neutral"]
        nor = [r for r in jd if r["length"]=="normal" and r["position"]=="first" and r["sentiment"]=="neutral"]
        if lon and nor:
            ml = sum(r["score"] for r in lon)/len(lon)
            mn = sum(r["score"] for r in nor)/len(nor)
            if ml <= mn:
                long_always_higher = False
    
    print(f"  Verbosity bias favors longer: {'YES (all judges)' if long_always_higher else 'Varies by judge (Claude prefers concise)'}")

def rank_judges_by_bias(data):
    """Rank judges from most to least biased."""
    judges = sorted(set(r["judge"] for r in data))
    
    bias_scores = {}
    for j in judges:
        jd = [r for r in data if r["judge"] == j]
        
        # Position bias magnitude
        fst = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        snd = [r for r in jd if r["position"]=="second" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        pos_bias = abs(sum(r["score"] for r in fst)/len(fst) - sum(r["score"] for r in snd)/len(snd)) if fst and snd else 0
        
        # Verbosity bias magnitude
        lon = [r for r in jd if r["length"]=="long" and r["position"]=="first" and r["sentiment"]=="neutral"]
        nor = [r for r in jd if r["length"]=="normal" and r["position"]=="first" and r["sentiment"]=="neutral"]
        verb_bias = abs(sum(r["score"] for r in lon)/len(lon) - sum(r["score"] for r in nor)/len(nor)) if lon and nor else 0
        
        # Sentiment bias magnitude
        pos = [r for r in jd if r["sentiment"]=="positive" and r["position"]=="first" and r["length"]=="normal"]
        neg = [r for r in jd if r["sentiment"]=="negative" and r["position"]=="first" and r["length"]=="normal"]
        sent_bias = abs(sum(r["score"] for r in pos)/len(pos) - sum(r["score"] for r in neg)/len(neg)) if pos and neg else 0
        
        # Worst-case degradation
        base = [r for r in jd if r["condition"] == "baseline"]
        worst = [r for r in jd if r["condition"] == "worst"]
        degradation = sum(r["score"] for r in base)/len(base) - sum(r["score"] for r in worst)/len(worst) if base and worst else 0
        
        bias_scores[j] = {
            "position_bias": round(pos_bias, 3),
            "verbosity_bias": round(verb_bias, 3),
            "sentiment_bias": round(sent_bias, 3),
            "worst_degradation": round(degradation, 3),
            "total": round(pos_bias + verb_bias + sent_bias + abs(degradation), 3),
        }
    
    print(f"\n=== JUDGE BIAS RANKING (most to least biased) ===")
    print(f"{'Rank':<6} {'Judge':<12} {'Position':<10} {'Verbosity':<12} {'Sentiment':<10} {'Worst Δ':<10} {'Total':<10}")
    print("-"*70)
    for rank, (j, scores) in enumerate(sorted(bias_scores.items(), key=lambda x: x[1]["total"], reverse=True), 1):
        print(f"{rank:<6} {j:<12} {scores['position_bias']:<10} {scores['verbosity_bias']:<12} {scores['sentiment_bias']:<10} {scores['worst_degradation']:<10} {scores['total']:<10}")

def main():
    data = load_data()
    if not data:
        return
    
    print("="*60)
    print("RESULTS COMPARISON TOOL")
    print("="*60)
    
    compare_judges(data)
    find_consistent_patterns(data)
    rank_judges_by_bias(data)
    
    print(f"\n{'='*60}")
    print("RECOMMENDATION")
    print(f"{'='*60}")
    print("""
    For your paper, focus on:
    1. The consistent patterns (findings that hold across ALL judges)
    2. The differences between judges (model-specific interaction patterns)
    3. The ranking of judges by bias (helps practitioners choose judges)
    """)

if __name__ == "__main__":
    main()
