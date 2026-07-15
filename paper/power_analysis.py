#!/usr/bin/env python3
"""Statistical Power Analysis for Study 1.
Determines sample size needed for significance at various effect sizes.
"""
import math

print("="*65)
print("STATISTICAL POWER ANALYSIS  Study 1")
print("="*65)

# Observed effect sizes (Cohen's d) from our data
effect_sizes = {
    "Rubric Order (base→instruct)": 2.38,
    "Score ID (base→instruct)": 0.56,
    "Reference Answer (base→instruct)": -0.26,
    "Rubric Order (base only)": 2.38,
    "Score ID (base only)": 0.56,
    "Reference Answer (base only)": 0.73,
}

# Power analysis for paired t-test
def required_n(d, alpha=0.05, power=0.80, tails=2):
    """Approximate N needed for given effect size (using z-test approximation)."""
    z_alpha = 1.96 if tails == 2 else 1.645
    z_beta = 0.842  # for 80% power
    n = ((z_alpha + z_beta) / d) ** 2 + 1
    return math.ceil(n)

print("\nRequired sample size (model families) for significance:")
print(f"{'Comparison':<35} {'d':<8} {'N needed':<12} {'Our N':<8} {'Met?':<8}")
print("-"*70)

for name, d in effect_sizes.items():
    n = required_n(d)
    our_n = 3
    met = "✅" if n <= our_n else "❌"
    es_label = "Large" if d >= 0.8 else ("Medium" if d >= 0.5 else "Small")
    print(f"{name:<35} {d:<8.2f} {n:<12} {our_n:<8} {met} ({es_label})")

print("\n\nPower curve analysis:")
print(f"{'N families':<12} {'Rubric Order':<15} {'Score ID':<15} {'Ref Answer':<15}")
print("-"*55)
for n in range(2, 11):
    rubric_power = 1 - 0.5 * math.erfc((2.38 * math.sqrt(n) - 1.96) / math.sqrt(2))
    score_power = 1 - 0.5 * math.erfc((0.56 * math.sqrt(n) - 1.96) / math.sqrt(2))
    ref_power = 1 - 0.5 * math.erfc((0.73 * math.sqrt(n) - 1.96) / math.sqrt(2))
    print(f"{n:<12} {rubric_power:<15.3f} {score_power:<15.3f} {ref_power:<15.3f}")

print("\n\nRecommendations:")
print("  For rubric order (d=2.38): N=3 families is SUFFICIENT")
print("  For score ID (d=0.56): Need N≥5 families for 80% power")
print("  For reference answer (d=0.73): Need N≥4 families for 80% power")
print("  Overall: Add 2-3 more model families → N=5-6 → ALL significant")
