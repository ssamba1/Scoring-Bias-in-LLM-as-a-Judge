# Root Cause Analysis Tool — Interactive Explorer
"""Explore root cause synthetic results.
Usage: python3 explore_rootcause.py
"""
import json, os, sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results_rootcause"

def load_results():
    path = RESULTS_DIR / "rootcause_analysis.json"
    if not path.exists():
        print(f"No results found at {path}")
        return None
    with open(path) as f:
        return json.load(f)

def show_summary(data):
    print("\n" + "="*70)
    print("ROOT CAUSE ANALYSIS — SUMMARY")
    print("="*70)
    
    # Group by family
    families = {}
    for model, results in data.items():
        family = model.rsplit("-", 1)[0] if "-" in model else model.split()[0]
        if family not in families:
            families[family] = {}
        families[family][model] = results
    
    for family, models in families.items():
        print(f"\n{family.upper()}")
        print("-"*50)
        
        base_model = [m for m in models if "base" in m.lower() or "(base)" in m.lower()]
        inst_model = [m for m in models if "instruct" in m.lower() or "(instruct)" in m.lower()]
        
        # Try different naming
        base_results = None
        inst_results = None
        for m, r in models.items():
            if "base" in m.lower() or "Base" in str(r.get("model_type", "")):
                base_results = r
            elif "instruct" in m.lower() or "Instruct" in str(r.get("model_type", "")):
                inst_results = r
        
        if base_results and inst_results:
            try:
                ro_base = base_results["rubric_order"]["mean_delta"]
                ro_inst = inst_results["rubric_order"]["mean_delta"]
                sid_base = base_results["score_id"].get("mean_max_gap", "?")
                sid_inst = inst_results["score_id"].get("mean_max_gap", "?")
                ref_base = base_results["reference_answer"].get("high_minus_low", "?")
                ref_inst = inst_results["reference_answer"].get("high_minus_low", "?")
                
                print(f"  {'Bias Type':<20} {'Base':<10} {'Instruct':<10} {'Ratio':<10}")
                print(f"  {'-'*50}")
                if isinstance(ro_base, (int, float)) and isinstance(ro_inst, (int, float)):
                    ratio = ro_inst / ro_base if ro_base > 0 else float('inf')
                    print(f"  {'Rubric Order':<20} {ro_base:<10.3f} {ro_inst:<10.3f} {ratio:<10.2f}")
                if isinstance(sid_base, (int, float)) and isinstance(sid_inst, (int, float)):
                    ratio = sid_inst / sid_base if sid_base > 0 else float('inf')
                    print(f"  {'Score ID':<20} {sid_base:<10.3f} {sid_inst:<10.3f} {ratio:<10.2f}")
                if isinstance(ref_base, (int, float)) and isinstance(ref_inst, (int, float)):
                    ratio = ref_inst / ref_base if ref_base > 0 else float('inf')
                    print(f"  {'Ref Answer':<20} {ref_base:<10.3f} {ref_inst:<10.3f} {ratio:<10.2f}")
            except (KeyError, TypeError):
                print(f"  (Could not parse results structure)")
        else:
            print(f"  Could not identify base/instruct pair")
            for m, r in models.items():
                print(f"  {m}: keys={list(r.keys())}")

def show_model(data, model_name):
    if model_name not in data:
        print(f"Model '{model_name}' not found. Available: {list(data.keys())}")
        return
    r = data[model_name]
    print(f"\n{model_name.upper()}:")
    print(json.dumps(r, indent=2))

def main():
    data = load_results()
    if not data:
        return
    
    print("="*50)
    print(" Root Cause Explorer".ljust(49))
    print("="*50)
    print(f"Models: {list(data.keys())}")
    
    while True:
        try:
            cmd = input("\n> ").strip().split()
            if not cmd:
                continue
            if cmd[0] in ("quit", "q", "exit"):
                break
            elif cmd[0] == "summary":
                show_summary(data)
            elif cmd[0] == "model" and len(cmd) > 1:
                show_model(data, cmd[1])
            elif cmd[0] == "help":
                print("Commands: summary, model <name>, quit")
            else:
                print("Unknown. Try: summary, model <name>, quit")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
