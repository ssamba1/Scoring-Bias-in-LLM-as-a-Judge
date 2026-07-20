"""Scale-granularity analysis (P17). Committed before the CPU run completed.

Bias per scale (K3/K5/K10), normalized by value range; tests (a) raw bias grows
with range, (b) instruct > base at every granularity.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "results_gran.json"
    res = json.loads((HERE / name).read_text())["results"]
    out = {"per_scale": {}, "P17a_growth": {}, "P17b_instruct_gt_base": {}}
    for sk in ("K3", "K5", "K10"):
        rows = {"base": [], "instruct": []}
        rng_ = None
        for fam, rec in res.items():
            for kind in ("base", "instruct"):
                kd = rec.get(kind, {}).get(sk)
                if not kd:
                    continue
                rng_ = kd["range"]
                for probe, variants in kd["probes"].items():
                    means = [v["mean"] for v in variants.values()]
                    rows[kind].append(max(means) - min(means))
        if rng_ is None:
            continue
        out["per_scale"][sk] = {
            "range": rng_,
            "mean_bias_base": round(float(np.mean(rows["base"])), 3),
            "mean_bias_instruct": round(float(np.mean(rows["instruct"])), 3),
            "bias_per_unit_range_base": round(float(np.mean(rows["base"])) / rng_, 4),
            "bias_per_unit_range_instruct": round(float(np.mean(rows["instruct"])) / rng_, 4)}
    ks = [k for k in ("K3", "K5", "K10") if k in out["per_scale"]]
    for kind in ("base", "instruct"):
        vals = [out["per_scale"][k][f"mean_bias_{kind}"] for k in ks]
        out["P17a_growth"][kind] = {"biases_by_scale": vals,
                                    "monotone_increasing": bool(all(b <= a for b, a in
                                                                    zip(vals, vals[1:])))}
    out["P17b_instruct_gt_base"] = {
        k: bool(out["per_scale"][k]["mean_bias_instruct"] >
                out["per_scale"][k]["mean_bias_base"]) for k in ks}
    (HERE / "results_gran_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
