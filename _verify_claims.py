#!/usr/bin/env python3
"""
Verification script for all claims in camera_ready_full.tex.
Run from repo root: python3 _verify_claims.py

Reads data files from results_rootcause/ and compares to paper values.
"""
import json, statistics
from pathlib import Path

BASE = Path("results_rootcause")

def load(fname):
    return json.loads((BASE / fname).read_text())

t4 = load("t4fam_results.json")
s1 = load("study1_results.json")
rc = load("rootcause_results.json")
rca = load("rootcause_analysis.json")
fm = load("full_metrics.json")

def delta(d, probe):
    pd = d.get(probe, {})
    vals = [v for v in pd.values() if isinstance(v, (int, float))]
    return max(vals) - min(vals) if len(vals) >= 2 else None

def check(label, computed, expected, tol=0.05):
    ok = abs(computed - expected) < tol
    print(f"  {label:45s} computed={computed:.2f} paper={expected:.2f}  {'✓' if ok else '✗'}")
    return ok

print("=" * 72)
print("CLAIM VERIFICATION: camera_ready_full.tex vs DATA FILES")
print("=" * 72)

# 1. Model counts
t4_models = sorted(t4.keys())
t4_fams = set(m.replace("-IT","") for m in t4_models)
s1_models = sorted(s1.keys())
print(f"\n## Model counts ##")
print(f"  t4fam: {len(t4_models)} variants, {len(t4_fams)} families")
print(f"  study1: {len(s1_models)} models")
print(f"  rootcause: {len(rc)} models")
print(f"  Paper claims 47/41/31/9/22 — see DATA_INTEGRITY_AUDIT.md")

# 2. tab:main 22-model Δ
print(f"\n## tab:main (22-model) ##")
s1_r, s1_s, s1_a = [], [], []
for m in s1_models:
    d = s1[m]
    for lst, p in [(s1_r,"rubric_order"),(s1_s,"score_id"),(s1_a,"reference_answer")]:
        v = delta(d, p)
        if v is not None: lst.append(v)
check("Rubric Order", statistics.mean(s1_r), 0.56)
check("Score ID", statistics.mean(s1_s), 0.68)
check("Reference Answer", statistics.mean(s1_a), 0.41)

# 3. tab:bootstrapped T4
print(f"\n## tab:bootstrapped T4 ##")
for label, tgt, exp in [
    ("Base", [t4[m] for m in t4_models if "-IT" not in m], {"rubric_order":0.69,"score_id":2.41,"reference_answer":2.76}),
    ("Instruct", [t4[m] for m in t4_models if "-IT" in m], {"rubric_order":0.29,"score_id":1.44,"reference_answer":1.93})
]:
    vals = {"rubric_order":[],"score_id":[],"reference_answer":[]}
    for d in tgt:
        for p in vals:
            v = delta(d, p)
            if v is not None: vals[p].append(v)
    print(f"  T4 {label} (n={len(tgt)}):")
    for p, name in [("rubric_order","Rubric"),("score_id","Score"),("reference_answer","Ref")]:
        check(f"  {name}", statistics.mean(vals[p]), exp[p])

# 4. tab:bootstrapped Study1
print(f"\n## tab:bootstrapped Study1 ##")
for lst, name, exp in [(s1_r,"Rubric",0.56),(s1_s,"Score",0.68),(s1_a,"Ref",0.41)]:
    check(name, statistics.mean(lst), exp)

# 5. tab:per_model spot check
print(f"\n## tab:per_model spot check ##")
checks = {
    "Command-R": (0.30,1.10,0.90), "DeepSeek-V3": (0.20,0.80,0.30),
    "Qwen2.5-7B": (0.70,1.70,0.10), "GPT-OSS-20B": (0.10,0.10,0.10),
    "Gemma3-27B": (0.80,0.20,0.50), "MythoMax-13B": (1.50,1.30,0.20),
    "Phi-4": (0.60,0.70,0.10),
}
for m, exp in sorted(checks.items()):
    d = s1.get(m)
    if not d: print(f"  {m:20s} NOT FOUND ✗"); continue
    cd = (delta(d,"rubric_order"), delta(d,"score_id"), delta(d,"reference_answer"))
    ok = all(abs(cd[i]-exp[i])<0.05 for i in range(3))
    print(f"  {m:20s} ({cd[0]:.2f},{cd[1]:.2f},{cd[2]:.2f}) vs ({exp[0]:.2f},{exp[1]:.2f},{exp[2]:.2f}) {'✓' if ok else '✗'}")

# 6. Byte-identical analysis
print(f"\n## rootcause_analysis byte-identicality ##")
for m in ["llama3-8b-instruct","mistral-7b-instruct","gemma2-2b-instruct"]:
    d = rca[m]
    print(f"  {m:28s} rubric={d['rubric_order']['mean_delta']}  score={d['score_id']['mean_max_gap']}  ref={d['reference_answer']['high_minus_low']}")

# 7. Wilcoxon
print(f"\n## Wilcoxon tests ##")
w = load("analysis_output/wilcoxon_results.json")
for probe in ["rubric_order","score_id","reference_answer"]:
    p = w.get(probe,{})
    print(f"  {probe:20s} p={p.get('p_value',0):.6f}  sig={p.get('significant_at_005')}")

print(f"\nDone. See DATA_INTEGRITY_AUDIT.md for full report.")
