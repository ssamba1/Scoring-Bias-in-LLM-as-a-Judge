#!/usr/bin/env python3
"""Analyze attention results and update paper."""
import json

with open(".hermes/desktop-attachments/attention_results.json") as f:
    data = json.load(f)

base = data["Qwen2.5-0.5B-base"]
instruct = data["Qwen2.5-0.5B-instruct"]

k_format = instruct["mean_format_attn"] / base["mean_format_attn"]
k_content = instruct["mean_content_attn"] / base["mean_content_attn"]

print("=== IIAR ATTENTION TEST RESULTS ===")
print(f"Model: Qwen2.5-0.5B (24 layers)")
print(f"\n{'Metric':<25} {'Base':<10} {'Instruct':<10} {'Ratio':<10}")
print("-"*55)
for metric in ["Format attention", "Content attention"]:
    b = base[f"mean_{metric.lower().split()[0]}_attn"]
    i = instruct[f"mean_{metric.lower().split()[0]}_attn"]
    k = i / b if b > 0 else 0
    print(f"{metric:<25} {b:<10.2f} {i:<10.2f} {k:<10.2f}")

print(f"\n=== IIAR VERDICT ===")
print(f"IIAR predicts: κ > 1.0 for BOTH format AND content")
print(f"Format κ = {k_format:.2f}x {'✅' if k_format > 1.05 else '❌'}")
print(f"Content κ = {k_content:.2f}x {'✅' if k_content > 1.05 else '❌'}")
print(f"\nResult: IIAR NOT supported at 0.5B scale")
print(f"Possible explanations:")
print(f"  1. 0.5B model is too small for attention redistribution")
print(f"  2. Token classification misses many content tokens")
print(f"  3. IIAR hypothesis is wrong")
print(f"\nRecommendation: Test at 1.5B, 7B, or larger scales")
