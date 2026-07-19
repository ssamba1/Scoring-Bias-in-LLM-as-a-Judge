"""Sampled-readout analysis (P16). Committed before the CPU run completed.

(a) parse-failure rate base vs instruct; (b) per-cell sampled-score Delta vs
expected-value Delta correlation (parseable cells only).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "results_sampled.json"
    res = json.loads((HERE / name).read_text())["results"]
    parse = {"base": [], "instruct": []}
    ev_d, sm_d = [], []
    for fam, rec in res.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for probe, variants in kd.items():
                for v in variants.values():
                    parse[kind].append(v["parse_rate"])
                ev_means = {vn: v["ev_mean"] for vn, v in variants.items()}
                sm_means = {vn: v["sampled_mean"] for vn, v in variants.items()
                            if v["sampled_mean"] is not None}
                if len(sm_means) == len(variants):
                    ev_d.append(max(ev_means.values()) - min(ev_means.values()))
                    sm_d.append(max(sm_means.values()) - min(sm_means.values()))
    out = {"P16a_parse_rate": {k: round(float(np.mean(v)), 3) for k, v in parse.items()},
           "P16b_delta_agreement": {}}
    if len(ev_d) >= 5:
        r = stats.spearmanr(ev_d, sm_d)
        out["P16b_delta_agreement"] = {
            "n_cells": len(ev_d),
            "spearman_ev_vs_sampled_delta": round(float(r.statistic), 3),
            "p": round(float(r.pvalue), 5)}
    (HERE / "results_sampled_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
