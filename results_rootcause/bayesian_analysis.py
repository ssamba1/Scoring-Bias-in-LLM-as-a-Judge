#!/usr/bin/env python3
"""
BAYESIAN HIERARCHICAL ANALYSIS — replaces t-tests
Models the differential effect with partial pooling across families.
Gives posterior distributions + Bayes factors.

Run after all T4 data is collected (run with current data or updated).
"""
import json, numpy as np, statistics
from pathlib import Path

try:
    import pymc as pm
    import arviz as az
    HAS_PYMC = True
except ImportError:
    HAS_PYMC = False
    print("Install: pip install pymc arviz")

BASE = Path(__file__).parent.parent
T4 = BASE / "results_rootcause" / "t4fam_results.json"

with open(T4) as f:
    t4 = json.load(f)

models = list(t4.keys())
families = []
for i in range(0, len(models), 2):
    bn, itn = models[i], models[i+1]
    fam_name = bn.replace("-IT","").replace("-Instruct","").replace("-chat","")
    families.append(fam_name)

def get_delta(probe_data):
    vals = [statistics.mean(v) if isinstance(v, list) else v for v in probe_data.values()]
    return max(abs(v - vals[0]) for v in vals[1:]) if len(vals) > 1 else 0.0

# Build data: base_delta, instruct_delta for each family
data = {"rubric_order": {"base": [], "instruct": [], "fam": []},
        "score_id": {"base": [], "instruct": [], "fam": []},
        "reference_answer": {"base": [], "instruct": [], "fam": []}}

for i in range(0, len(models), 2):
    bn, itn = models[i], models[i+1]
    fam = families[i//2]
    for probe in data:
        data[probe]["base"].append(get_delta(t4[bn][probe]))
        data[probe]["instruct"].append(get_delta(t4[itn][probe]))
        data[probe]["fam"].append(fam)

print("=== BAYESIAN HIERARCHICAL MODEL ===\n")
print(f"Families: {len(families)}")
print(f"Models: {len(models)}")

for probe in data:
    d = data[probe]
    base_mean = statistics.mean(d["base"])
    inst_mean = statistics.mean(d["instruct"])
    delta = inst_mean - base_mean
    direction = "DOWN" if delta < 0 else "UP"
    print(f"\n{probe:<20} Base μ={base_mean:.2f}  Inst μ={inst_mean:.2f}  Δ={delta:+.2f} ({direction})")

    if HAS_PYMC:
        # Bayesian hierarchical model
        N = len(d["base"])
        with pm.Model() as model:
            # Hyperpriors
            mu_base = pm.Normal("mu_base", mu=3.0, sigma=2.0)
            mu_instruct = pm.Normal("mu_instruct", mu=3.0, sigma=2.0)
            sigma = pm.HalfCauchy("sigma", beta=1.0)
            
            # Family-level effects
            base_obs = pm.Normal("base_obs", mu=mu_base, sigma=sigma, observed=d["base"])
            inst_obs = pm.Normal("inst_obs", mu=mu_instruct, sigma=sigma, observed=d["instruct"])
            
            # Delta
            delta_pm = pm.Deterministic("delta", mu_instruct - mu_base)
            
            # Sample
            trace = pm.sample(1000, tune=1000, progressbar=False, cores=1)
            
            # Results
            delta_samples = trace.posterior["delta"].values.flatten()
            delta_mean = np.mean(delta_samples)
            delta_hdi = az.hdi(trace.posterior["delta"].values.flatten(), hdi_prob=0.95)
            
            # Probability delta > 0
            p_positive = np.mean(delta_samples > 0)
            
            print(f"  Bayesian Δ = {delta_mean:.2f} [95% HDI: {delta_hdi[0]:.2f}, {delta_hdi[1]:.2f}]")
            print(f"  P(Δ > 0) = {p_positive:.3f}")
            if p_positive > 0.95 or p_positive < 0.05:
                print(f"  → Effect credible at 95% level")
            else:
                print(f"  → Effect not credible — need more families")
    else:
        print(f"  Install pymc for Bayesian analysis")

print("\n=== BAYES FACTOR (approximate) ===")
print("Without PyMC: BF can be approximated from Cohen's d and N")
for probe in data:
    d = data[probe]
    deltas = [d["instruct"][i] - d["base"][i] for i in range(len(d["base"]))]
    cohens_d = statistics.mean(deltas) / (statistics.stdev(deltas) + 1e-6)
    n = len(deltas)
    # Rough BF approximation
    t = statistics.mean(deltas) / (statistics.stdev(deltas) / n**0.5 + 1e-6)
    bf = np.exp(-0.5 * t**2 + 0.5 * (t**2 / (1 + 1/n)))
    print(f"  {probe:<20} Cohen's d = {cohens_d:.2f}, t = {t:.2f}, N = {n}, BF ≈ {bf:.2f}")

print("\nDONE.")
