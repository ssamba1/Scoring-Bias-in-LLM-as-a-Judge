#!/usr/bin/env python3
"""Power analysis for bias interaction experiment.
Determines required sample size for detecting interaction effects.
"""
import math
import numpy as np
from scipy import stats

def estimate_sample_size(effect_size=0.1, power=0.8, alpha=0.05, n_groups=8):
    """
    Estimate required sample size for ANOVA with interaction terms.

    Parameters:
    - effect_size: Cohen's f (small=0.1, medium=0.25, large=0.4)
    - power: desired statistical power (0.8 = standard)
    - alpha: significance level
    - n_groups: number of conditions in factorial design
    """
    # Approximate using F-test power calculation
    # For a 2x3x3 design with one 2-way interaction: df_numerator = (2-1)*(3-1) = 2
    df_numerator = 2  # position × length interaction

    # Total df for error
    # Need to solve for N iteratively
    for n in range(5, 500):
        df_denominator = n * n_groups - n_groups - df_numerator
        if df_denominator < 1:
            continue

        # Non-centrality parameter
        ncp = effect_size**2 * n * n_groups

        # Critical F value
        f_crit = stats.f.ppf(1 - alpha, df_numerator, df_denominator)

        # Power
        power_calc = 1 - stats.ncf.cdf(f_crit, df_numerator, df_denominator, ncp)

        if power_calc >= power:
            return n

    return 500  # fallback

def main():
    print("="*65)
    print("POWER ANALYSIS  Bias Interaction Experiment")
    print("="*65)

    print("\nSample size required per condition (n):")
    print(f"{'Effect Size':<15} {'Small (f=0.10)':<20} {'Medium (f=0.25)':<20} {'Large (f=0.40)':<20}")
    print("-"*75)

    for power_level, label in [(0.8, "80% power"), (0.9, "90% power"), (0.95, "95% power")]:
        small = estimate_sample_size(effect_size=0.10, power=power_level)
        medium = estimate_sample_size(effect_size=0.25, power=power_level)
        large = estimate_sample_size(effect_size=0.40, power=power_level)
        print(f"{label:<15} {small:<20} {medium:<20} {large:<20}")

    print("\n" + "="*65)
    print("RECOMMENDATION")
    print("="*65)
    print("""
    For detecting medium interaction effects (f=0.25) at 80% power:
    - Need n ≈ 30-50 items per condition
    - With 8 conditions: 240-400 total items per judge
    - Our 400 items × 8 conditions (50 per cell) is ADEQUATE

    For detecting small interaction effects (f=0.10) at 80% power:
    - Need n ≈ 300+ items per condition
    - 400 × 8 = 50 per cell  may miss small interactions

    Conclusion: 400 items is sufficient for medium-to-large interactions.
    If you expect small effects, increase to 1000+ items.
    """)

    print("\nMinimal detectable effect size (at 80% power, n=50 per cell):")
    print("-"*45)
    for n_per_cell in [25, 50, 100, 200]:
        mdes = estimate_minimal_effect(n_per_cell, 0.8, 0.05)
        print(f"  n={n_per_cell:<5} → f={mdes:.3f} {'(ADEQUATE)' if mdes <= 0.25 else '(LIMITED)'}")

def estimate_minimal_effect(n, power=0.8, alpha=0.05):
    """Estimate minimal detectable Cohen's f given sample size."""
    df_num = 2
    df_den = n * 8 - 8 - df_num
    if df_den < 1:
        return 1.0

    # Binary search for effect size
    lo, hi = 0.001, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        ncp = mid**2 * n * 8
        f_crit = stats.f.ppf(1 - alpha, df_num, df_den)
        p = 1 - stats.ncf.cdf(f_crit, df_num, df_den, ncp)
        if p >= power:
            hi = mid
        else:
            lo = mid
    return round((lo + hi) / 2, 3)

if __name__ == "__main__":
    main()
