"""Frontier-judge analysis (P20). Adjudicates the preregistered clauses.

Inputs : results_closed.json (OpenRouter logprob runs), results_scaled.json
Output : results_closed_analysis.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}
COMPLETE_MIN_ITEMS = 40


def main():
    closed = json.loads((HERE / "results_closed.json").read_text())["results"]
    scaled = json.loads((HERE / "results_scaled.json").read_text())["results"]

    out = {"judges": {}, "excluded": [], "P20a": {}, "P20b": {}, "P20c": {}, "pooled": {}}
    fx, fy = [], []
    for m, rec in closed.items():
        probes = rec.get("instruct", {})
        cells = [len(v.get("per_item", [])) for vs in probes.values() for v in vs.values()]
        if not cells or min(cells) < COMPLETE_MIN_ITEMS:
            out["excluded"].append({"model": m, "reason": "incomplete/no logprob provider",
                                    "cells": len(cells)})
            continue
        ds, ents = {}, []
        for p, variants in probes.items():
            means = [v["mean"] for v in variants.values()]
            ds[p] = round(max(means) - min(means), 3)
            ent = float(np.mean([v["mean_entropy"] for v in variants.values()]))
            ents.append(ent)
            fx.append(ent); fy.append(max(means) - min(means))
        out["judges"][m] = {"delta_by_probe": ds,
                            "mean_delta": round(float(np.mean(list(ds.values()))), 3),
                            "mean_entropy": round(float(np.mean(ents)), 3),
                            "probes_delta_gt_0.1": sum(1 for v in ds.values() if v > 0.1)}

    js = out["judges"]
    out["P20a"] = {"all_judges_ge_half_probes": bool(all(j["probes_delta_gt_0.1"] >= 3
                                                         for j in js.values())),
                   "detail": {m: f"{j['probes_delta_gt_0.1']}/5" for m, j in js.items()}}
    if len(js) >= 3:
        es = [j["mean_entropy"] for j in js.values()]
        bs = [j["mean_delta"] for j in js.values()]
        r = stats.spearmanr(es, bs)
        out["P20b"] = {"within_frontier_rho": round(float(r.statistic), 2),
                       "n_judges": len(js),
                       "registered_direction_negative_observed": bool(r.statistic < 0)}
    # open-panel comparison + pooled law
    ox, oy = [], []
    oim = []
    for fam, rec in scaled.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for p in CONTROL:
                if p not in kd:
                    continue
                means = [v["mean"] for v in kd[p].values()]
                ent = float(np.mean([v["mean_entropy"] for v in kd[p].values()]))
                ox.append(ent); oy.append(max(means) - min(means))
                if kind == "instruct":
                    oim.append(max(means) - min(means))
    frontier_mean = float(np.mean([j["mean_delta"] for j in js.values()]))
    out["P20c"] = {"frontier_mean_delta": round(frontier_mean, 3),
                   "open_instruct_mean_delta": round(float(np.mean(oim)), 3),
                   "frontier_below_open": bool(frontier_mean < float(np.mean(oim)))}
    r_open = stats.spearmanr(ox, oy)
    r_pool = stats.spearmanr(ox + fx, oy + fy)
    out["pooled"] = {"open_only_rho": round(float(r_open.statistic), 3),
                     "pooled_rho": round(float(r_pool.statistic), 3),
                     "pooled_p": float(f"{r_pool.pvalue:.2e}"),
                     "n_pooled": len(ox) + len(fx),
                     "frontier_mean_entropy": round(float(np.mean(fx)), 2),
                     "frontier_mean_delta_cells": round(float(np.mean(fy)), 2),
                     "open_mean_entropy": round(float(np.mean(ox)), 2),
                     "open_mean_delta_cells": round(float(np.mean(oy)), 2)}
    (HERE / "results_closed_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
