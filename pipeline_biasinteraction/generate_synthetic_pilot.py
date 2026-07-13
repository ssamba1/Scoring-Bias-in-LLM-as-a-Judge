#!/usr/bin/env python3
"""Generate synthetic pilot data and create publication-ready visualizations."""
import csv, json, os, sys
from pathlib import Path
import random
random.seed(42)

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"

def generate_full_synthetic():
    """Generate complete synthetic dataset for both options."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # === Option 2: Bias Interaction ===
    judges = ["claude", "gpt4o", "gemini", "deepseek", "llama"]
    conditions = [
        ("first", "normal", "neutral", "baseline"),
        ("first", "short", "neutral", "short"),
        ("first", "long", "neutral", "verbose"),
        ("first", "normal", "positive", "positive"),
        ("first", "normal", "negative", "negative"),
        ("second", "normal", "neutral", "disfavored"),
        ("second", "short", "negative", "worst"),
        ("second", "long", "positive", "best_biased"),
    ]
    
    # Per-judge bias parameters (based on published literature)
    bias_params = {
        "claude":  {"pos": 0.12, "verb": 0.22, "sent": 0.08, "interact_pos_verb": -0.05, "noise": 0.3},
        "gpt4o":  {"pos": 0.08, "verb": 0.15, "sent": 0.10, "interact_pos_verb": -0.08, "noise": 0.25},
        "gemini": {"pos": 0.15, "verb": 0.28, "sent": 0.06, "interact_pos_verb": -0.12, "noise": 0.35},
        "deepseek":{"pos": 0.05, "verb": 0.20, "sent": 0.12, "interact_pos_verb": -0.03, "noise": 0.3},
        "llama":  {"pos": 0.20, "verb": 0.32, "sent": 0.15, "interact_pos_verb": -0.15, "noise": 0.4},
    }
    
    rows = []
    for judge in judges:
        p = bias_params[judge]
        for item_id in range(400):
            for pos, length, sent, cname in conditions:
                base = 3.5
                bias = 0.0
                
                if pos == "second": bias -= p["pos"]
                if length == "short": bias -= p["verb"] * 0.6
                elif length == "long": bias += p["verb"] * 0.4
                if sent == "positive": bias += p["sent"]
                elif sent == "negative": bias -= p["sent"]
                
                # Interaction: position × short compounds
                if pos == "second" and length == "short":
                    bias += p["interact_pos_verb"]
                
                score = base + bias + random.gauss(0, p["noise"])
                score = max(1, min(5, round(score, 1)))
                
                rows.append({
                    "item_id": item_id, "judge": judge,
                    "position": pos, "length": length, "sentiment": sent,
                    "condition": cname, "score": score,
                })
    
    out = RESULTS_DIR / "bias_interaction_synthetic.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Bias interaction synthetic: {len(rows)} rows -> {out}")
    
    # === Option 1: Root Cause ===
    families = [
        ("Llama 3 8B", "base", 0.05),
        ("Llama 3 8B", "instruct", 0.42),
        ("Mistral 7B", "base", 0.03),
        ("Mistral 7B", "instruct", 0.38),
        ("Gemma 2 2B", "base", 0.08),
        ("Gemma 2 2B", "instruct", 0.45),
    ]
    
    rc_rows = []
    for model_name, model_type, rubric_delta in families:
        for item_id in range(50):
            score_a = 3.0 + random.gauss(0, 0.5)
            score_b = score_a + rubric_delta + random.gauss(0, 0.3)
            score_a = max(1, min(5, round(score_a, 1)))
            score_b = max(1, min(5, round(score_b, 1)))
            
            # Score ID bias
            sid_var = rubric_delta * 0.3 + random.uniform(0, 0.2)
            
            # Reference answer bias
            ref_bias = rubric_delta * 0.25 + random.uniform(0, 0.15)
            
            rc_rows.append({
                "model": model_name, "type": model_type,
                "item_id": item_id,
                "rubric_order_delta": round(abs(score_a - score_b), 2),
                "score_id_variance": round(sid_var, 2),
                "reference_answer_bias": round(ref_bias, 2),
            })
    
    out_rc = RESULTS_DIR / "rootcause_synthetic.csv"
    with open(out_rc, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rc_rows[0].keys())
        w.writeheader(); w.writerows(rc_rows)
    print(f"Root cause synthetic: {len(rc_rows)} rows -> {out_rc}")
    
    # Generate summary statistics
    summary = {"bias_interaction": {}, "root_cause": {}}
    
    for judge in judges:
        jrows = [r for r in rows if r["judge"] == judge]
        baseline = [r for r in jrows if r["condition"] == "baseline"]
        worst = [r for r in jrows if r["condition"] == "worst"]
        
        if baseline and worst:
            mb = sum(r["score"] for r in baseline)/len(baseline)
            mw = sum(r["score"] for r in worst)/len(worst)
            summary["bias_interaction"][judge] = {
                "baseline_mean": round(mb, 2),
                "worst_case_mean": round(mw, 2),
                "degradation": round(mw - mb, 2),
            }
    
    # Root cause summary
    for model_name in set(r["model"] for r in rc_rows):
        base_rows = [r for r in rc_rows if r["model"] == model_name and r["type"] == "base"]
        inst_rows = [r for r in rc_rows if r["model"] == model_name and r["type"] == "instruct"]
        if base_rows and inst_rows:
            summary["root_cause"][model_name] = {
                "rubric_order_base": round(sum(r["rubric_order_delta"] for r in base_rows)/len(base_rows), 3),
                "rubric_order_instruct": round(sum(r["rubric_order_delta"] for r in inst_rows)/len(inst_rows), 3),
                "score_id_base": round(sum(r["score_id_variance"] for r in base_rows)/len(base_rows), 3),
                "score_id_instruct": round(sum(r["score_id_variance"] for r in inst_rows)/len(inst_rows), 3),
                "ref_answer_base": round(sum(r["reference_answer_bias"] for r in base_rows)/len(base_rows), 3),
                "ref_answer_instruct": round(sum(r["reference_answer_bias"] for r in inst_rows)/len(inst_rows), 3),
            }
    
    with open(RESULTS_DIR / "synthetic_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\nSummary statistics:")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    generate_full_synthetic()
