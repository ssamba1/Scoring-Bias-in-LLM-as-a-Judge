"""Dose-response analysis (P14). Committed before the CPU run completed.

Reads results_dose.json: per family/checkpoint, mean score at each nuisance dose
(verbosity: filler units 0/1/2/4/8; authority: framing strengths 0-4).
Tests: (a) |score(dose) - score(0)| increases monotonically with dose
(Spearman of |shift| vs dose level), (b) instruct slope > base slope per
family x probe (slope = OLS of |shift| on dose index).
Output: results_dose_analysis.json
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent


def load(name):
    p = HERE / name
    if p.exists():
        return json.loads(p.read_text())
    return json.loads(gzip.decompress((HERE / (name + ".gz")).read_bytes()).decode())


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "results_dose.json"
    payload = load(name)
    res = payload["results"]
    out = {"per_cell": [], "P14a_monotonic": {}, "P14b_slope": {}}
    slopes = {"base": {}, "instruct": {}}
    mono = []
    for fam, rec in res.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for probe in ("verbosity", "authority"):
                d = kd.get(probe)
                if not d:
                    continue
                doses = sorted(d, key=lambda x: int(x))
                base_mean = d[doses[0]]["mean"]
                shifts = [abs(d[k]["mean"] - base_mean) for k in doses]
                idx = list(range(len(doses)))
                rho = stats.spearmanr(idx[1:], shifts[1:]).statistic if len(doses) > 2 else None
                slope = float(np.polyfit(idx, shifts, 1)[0])
                out["per_cell"].append({"family": fam, "kind": kind, "probe": probe,
                                        "shifts": [round(s, 4) for s in shifts],
                                        "dose_spearman": None if rho is None or np.isnan(rho)
                                        else round(float(rho), 3),
                                        "slope": round(slope, 4)})
                slopes[kind][(fam, probe)] = slope
                if rho is not None and not np.isnan(rho):
                    mono.append(rho)
    out["P14a_monotonic"] = {
        "mean_dose_spearman": round(float(np.mean(mono)), 3) if mono else None,
        "frac_positive": round(float(np.mean([r > 0 for r in mono])), 3) if mono else None,
        "n_cells": len(mono)}
    pairs = [(k, slopes["base"][k], slopes["instruct"][k])
             for k in slopes["base"] if k in slopes["instruct"]]
    steeper = [i > b for _k, b, i in pairs]
    out["P14b_slope"] = {
        "n_pairs": len(pairs),
        "instruct_steeper": f"{sum(steeper)}/{len(steeper)}",
        "mean_base_slope": round(float(np.mean([b for _k, b, _i in pairs])), 4),
        "mean_instruct_slope": round(float(np.mean([i for _k, _b, i in pairs])), 4)}
    if len(pairs) >= 6:
        w = stats.wilcoxon([i - b for _k, b, i in pairs])
        out["P14b_slope"]["wilcoxon_p"] = round(float(w.pvalue), 5)
    (HERE / "results_dose_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_cell"}, indent=2))


if __name__ == "__main__":
    main()
