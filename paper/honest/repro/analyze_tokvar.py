"""Readout-variant analysis (P18, v2: bare vs full vocab-scan union).

Per (family, checkpoint, probe): bias Delta under bare / spaced / union
readouts; pairwise per-cell Delta correlations; instruct>base effect under the
union readout; mean masses per readout.
"""
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
READOUTS = ("bare", "union")


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "results_tokvar.json"
    res = json.loads((HERE / name).read_text())["results"]
    cells = {r: [] for r in READOUTS}
    masses = {r: {"base": [], "instruct": []} for r in READOUTS}
    eff_union = {}
    for fam, rec in res.items():
        fb, fi = [], []
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for probe, variants in kd.items():
                per_r = {}
                for r in READOUTS:
                    if any(r not in v or v[r] is None for v in variants.values()):
                        continue
                    means = [v[r]["mean"] for v in variants.values()]
                    per_r[r] = max(means) - min(means)
                    masses[r][kind].extend(v[r]["mean_mass"] for v in variants.values())
                if len(per_r) == len(READOUTS):
                    for r in READOUTS:
                        cells[r].append(per_r[r])
                    if kind == "base":
                        fb.append(per_r["union"])
                    else:
                        fi.append(per_r["union"])
        if fb and fi:
            eff_union[fam] = round(float(np.mean(fi) - np.mean(fb)), 3)
    out = {"n_cells": len(cells["bare"]),
           "mean_mass": {r: {k: round(float(np.mean(v)), 4) for k, v in m.items() if v}
                         for r, m in masses.items()},
           "P18a_pairwise_delta_corr": {}, "P18b_union_effect": {}}
    for a, b in combinations(READOUTS, 2):
        r = stats.spearmanr(cells[a], cells[b])
        out["P18a_pairwise_delta_corr"][f"{a}~{b}"] = round(float(r.statistic), 3)
    ev = np.array(list(eff_union.values()))
    out["P18b_union_effect"] = {
        "per_family": eff_union,
        "mean_effect": round(float(ev.mean()), 3) if len(ev) else None,
        "families_positive": f"{int((ev>0).sum())}/{len(ev)}" if len(ev) else None}
    (HERE / "results_tokvar_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
