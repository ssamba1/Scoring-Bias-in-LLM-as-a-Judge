#!/usr/bin/env python3
"""Analyze Study 1 results from Kaggle and update paper."""
import json

results = {
    "llama3-base": {
        "rubric_order": {"control":5.000,"b1":1.000,"b2":4.720,"max_delta":4.000},
        "score_id": {"control":5.000,"b1":4.980,"b2":3.000,"max_delta":2.000},
        "reference_answer": {"control":5.000,"b1":4.600,"b2":4.600,"max_delta":0.400}
    },
    "llama3-inst": {
        "rubric_order": {"control":3.280,"b1":2.960,"b2":4.080,"max_delta":0.800},
        "score_id": {"control":4.680,"b1":4.480,"b2":4.220,"max_delta":0.460},
        "reference_answer": {"control":2.680,"b1":3.880,"b2":4.660,"max_delta":1.980}
    },
    "mistral-base": {
        "rubric_order": {"control":4.040,"b1":1.080,"b2":3.000,"max_delta":2.960},
        "score_id": {"control":3.960,"b1":4.900,"b2":2.440,"max_delta":1.520},
        "reference_answer": {"control":4.060,"b1":2.260,"b2":4.500,"max_delta":1.800}
    },
    "mistral-inst": {
        "rubric_order": {"control":4.780,"b1":1.160,"b2":3.020,"max_delta":3.620},
        "score_id": {"control":4.900,"b1":5.000,"b2":3.640,"max_delta":1.260},
        "reference_answer": {"control":4.460,"b1":4.080,"b2":4.960,"max_delta":0.500}
    },
    "gemma2-base": {
        "rubric_order": {"control":1.400,"b1":1.440,"b2":3.000,"max_delta":1.600},
        "score_id": {"control":3.940,"b1":5.000,"b2":2.020,"max_delta":1.920},
        "reference_answer": {"control":1.000,"b1":1.000,"b2":1.000,"max_delta":0.000}
    },
    "gemma2-inst": {
        "rubric_order": {"control":3.740,"b1":3.800,"b2":3.400,"max_delta":0.340},
        "score_id": {"control":3.880,"b1":4.040,"b2":3.320,"max_delta":0.560},
        "reference_answer": {"control":3.860,"b1":3.160,"b2":3.700,"max_delta":0.700}
    }
}

print("="*65)
print("STUDY 1: COMPLETE ROOT CAUSE ANALYSIS")
print("="*65)

# By probe type
print("\nBY PROBE TYPE:")
print(f"{'Probe':<20} {'Base Avg':<12} {'Instruct Avg':<15} {'Delta':<10}")
print("-"*55)
for probe in ["rubric_order", "score_id", "reference_answer"]:
    base_vals = [results[f"{f}-base"][probe]["max_delta"] for f in ["llama3","mistral","gemma2"]]
    inst_vals = [results[f"{f}-inst"][probe]["max_delta"] for f in ["llama3","mistral","gemma2"]]
    ba = sum(base_vals)/len(base_vals)
    ia = sum(inst_vals)/len(inst_vals)
    d = ia - ba
    print(f"{probe:<20} {ba:<12.3f} {ia:<15.3f} {d:<+.3f}")

# By model family
print("\nBY MODEL FAMILY:")
for family in ["llama3","mistral","gemma2"]:
    b = results[f"{family}-base"]
    i = results[f"{family}-inst"]
    bb = sum(b[p]["max_delta"] for p in ["rubric_order","score_id","reference_answer"])/3
    bi = sum(i[p]["max_delta"] for p in ["rubric_order","score_id","reference_answer"])/3
    amp = 1 - bi/max(bb,0.001)  # negative = reduction
    print(f"  {family:<10} base={bb:.3f} instruct={bi:.3f} change={bi-bb:+.3f} ({amp*100:.0f}%)")

# Overall
print("\nOVERALL:")
base_all = [results[f"{f}-{v}"][p]["max_delta"] for f in ["llama3","mistral","gemma2"] for v in ["base"] for p in ["rubric_order","score_id","reference_answer"]]
inst_all = [results[f"{f}-{v}"][p]["max_delta"] for f in ["llama3","mistral","gemma2"] for v in ["inst"] for p in ["rubric_order","score_id","reference_answer"]]
ba = sum(base_all)/len(base_all)
ia = sum(inst_all)/len(inst_all)
print(f"  Base average bias: {ba:.3f}")
print(f"  Instruct average bias: {ia:.3f}")
print(f"  Change: {ia-ba:+.3f} ({(ia/ba*100-100):+.0f}%)")
print(f"  N=6 models × 3 probes × 50 items × 3 repeats = 8,100 judgments")
print(f"  Cost: $0 (Kaggle T4 free tier)")
