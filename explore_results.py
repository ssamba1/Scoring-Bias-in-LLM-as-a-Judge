#!/usr/bin/env python3
"""Interactive CLI explorer for bias interaction synthetic results.
Usage: python3 explore_results.py
"""
import csv, json, os, sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

def load_data():
    path = RESULTS_DIR / "bias_interaction_synthetic.csv"
    if not path.exists():
        print("No results found. Run generate_synthetic_pilot.py first.")
        return []
    with open(path) as f:
        return list(csv.DictReader(f))

def show_help():
    print("""
Commands:
  summary           Show overview of all judges
  judge <name>      Show details for a judge (claude, gpt4o, gemini, deepseek, llama)
  compare <a> <b>   Compare two judges
  worst             Show worst-case vs baseline for all judges
  interaction       Show interaction ratios for all judges
  export <file>     Export summary to CSV
  help              Show this help
  quit              Exit
""")

def cmd_summary(data):
    judges = sorted(set(r["judge"] for r in data))
    print(f"\n{'Judge':<12} {'Baseline':<10} {'Worst Case':<12} {'Degradation':<12} {'Items':<8}")
    print("-"*54)
    for judge in judges:
        jd = [r for r in data if r["judge"] == judge]
        base = [r for r in jd if r["condition"] == "baseline"]
        worst = [r for r in jd if r["condition"] == "worst"]
        if base and worst:
            mb = sum(float(r["score"]) for r in base)/len(base)
            mw = sum(float(r["score"]) for r in worst)/len(worst)
            print(f"{judge:<12} {mb:<10.2f} {mw:<12.2f} {mw-mb:<12.2f} {len(jd):<8}")

def cmd_judge(data, name):
    jd = [r for r in data if r["judge"] == name]
    if not jd:
        print(f"Judge '{name}' not found. Options: {sorted(set(r['judge'] for r in data))}")
        return
    conditions = sorted(set(r["condition"] for r in jd))
    print(f"\n{name.upper()}:")
    print(f"{'Condition':<16} {'Score':<8} {'N':<6}")
    print("-"*30)
    for cond in conditions:
        cd = [r for r in jd if r["condition"] == cond]
        mean = sum(float(r["score"]) for r in cd)/len(cd)
        print(f"{cond:<16} {mean:<8.2f} {len(cd):<6}")

def cmd_compare(data, a, b):
    for judge in [a, b]:
        jd = [r for r in data if r["judge"] == judge]
        if not jd:
            print(f"Judge '{judge}' not found")
            return
    print(f"\nComparing {a} vs {b}:")
    print(f"{'Condition':<16} {a:<8} {b:<8} {'Diff':<8}")
    print("-"*40)
    conds = sorted(set(r["condition"] for r in data))
    for cond in conds:
        sa = sum(float(r["score"]) for r in data if r["judge"]==a and r["condition"]==cond)
        ca = len([r for r in data if r["judge"]==a and r["condition"]==cond])
        sb = sum(float(r["score"]) for r in data if r["judge"]==b and r["condition"]==cond)
        cb = len([r for r in data if r["judge"]==b and r["condition"]==cond])
        if ca and cb:
            ma, mb = sa/ca, sb/cb
            print(f"{cond:<16} {ma:<8.2f} {mb:<8.2f} {ma-mb:<8.2f}")

def cmd_worst(data):
    print(f"\n{'Judge':<12} {'Baseline':<10} {'Worst':<10} {'Drop':<10} {'Ratio':<10}")
    print("-"*52)
    for judge in sorted(set(r["judge"] for r in data)):
        jd = [r for r in data if r["judge"] == judge]
        base = [r for r in jd if r["condition"] == "baseline"]
        worst = [r for r in jd if r["condition"] == "worst"]
        if base and worst:
            mb = sum(float(r["score"]) for r in base)/len(base)
            mw = sum(float(r["score"]) for r in worst)/len(worst)
            drop = mb - mw
            ratio = drop / 0.2 if drop > 0 else 0  # normalized
            print(f"{judge:<12} {mb:<10.2f} {mw:<10.2f} {drop:<10.2f} {ratio:<10.2f}")

def cmd_interaction(data):
    print(f"\nInteraction Ratios (Position × Verbosity):")
    print(f"{'Judge':<12} {'Pos Alone':<12} {'Verb Alone':<12} {'Combined':<12} {'IR':<10} {'Effect':<12}")
    print("-"*70)
    for judge in sorted(set(r["judge"] for r in data)):
        jd = [r for r in data if r["judge"] == judge]
        p_f = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        p_s = [r for r in jd if r["position"]=="second" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        v_l = [r for r in jd if r["length"]=="long" and r["position"]=="first" and r["sentiment"]=="neutral"]
        v_n = [r for r in jd if r["length"]=="normal" and r["position"]=="first" and r["sentiment"]=="neutral"]
        both = [r for r in jd if r["position"]=="second" and r["length"]=="short" and r["sentiment"]=="neutral"]
        base = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        
        if p_f and p_s and v_l and v_n and both and base:
            pos = sum(float(r["score"]) for r in p_f)/len(p_f) - sum(float(r["score"]) for r in p_s)/len(p_s)
            verb = sum(float(r["score"]) for r in v_l)/len(v_l) - sum(float(r["score"]) for r in v_n)/len(v_n)
            comb = sum(float(r["score"]) for r in base)/len(base) - sum(float(r["score"]) for r in both)/len(both)
            pos_a, verb_a = abs(pos), abs(verb)
            ir = comb / (pos_a + verb_a) if (pos_a + verb_a) > 0 else 0
            effect = "compounding" if ir > 1.05 else ("cancelling" if ir < 0.95 else "additive")
            print(f"{judge:<12} {pos_a:<12.3f} {verb_a:<12.3f} {comb:<12.3f} {ir:<10.2f} {effect:<12}")

def cmd_export(data, filename):
    judges = sorted(set(r["judge"] for r in data))
    rows = []
    for judge in judges:
        jd = [r for r in data if r["judge"] == judge]
        conds = sorted(set(r["condition"] for r in jd))
        for cond in conds:
            cd = [r for r in jd if r["condition"] == cond]
            if cd:
                rows.append({"judge": judge, "condition": cond, 
                           "mean_score": f"{sum(float(r['score']) for r in cd)/len(cd):.2f}",
                           "n": len(cd)})
    with open(filename, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["judge", "condition", "mean_score", "n"])
        w.writeheader(); w.writerows(rows)
    print(f"Exported {len(rows)} rows to {filename}")

def main():
    data = load_data()
    if not data:
        return
    
    print("="*50)
    print(" Bias Interaction Explorer".ljust(49))
    print("="*50)
    print(f"Loaded {len(data)} data points")
    print(f"Judges: {sorted(set(r['judge'] for r in data))}")
    show_help()
    
    while True:
        try:
            cmd = input("\n> ").strip().split()
            if not cmd:
                continue
            if cmd[0] == "quit" or cmd[0] == "q" or cmd[0] == "exit":
                break
            elif cmd[0] == "help":
                show_help()
            elif cmd[0] == "summary":
                cmd_summary(data)
            elif cmd[0] == "judge" and len(cmd) > 1:
                cmd_judge(data, cmd[1])
            elif cmd[0] == "compare" and len(cmd) > 2:
                cmd_compare(data, cmd[1], cmd[2])
            elif cmd[0] == "worst":
                cmd_worst(data)
            elif cmd[0] == "interaction":
                cmd_interaction(data)
            elif cmd[0] == "export" and len(cmd) > 1:
                cmd_export(data, cmd[1])
            else:
                print("Unknown command. Type 'help'.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
