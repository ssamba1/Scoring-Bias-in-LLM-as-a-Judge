"""Ten-template analysis (P15). Committed before the CPU run completed.

Reads results_t10.json: 10 templates x 3 probes x variants, 3 small families,
base+instruct. Tests: (a) pooled entropy-bias Spearman negative; (b) per template,
mean instruct Delta > mean base Delta.
Output: results_t10_analysis.json
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
    name = sys.argv[1] if len(sys.argv) > 1 else "results_t10.json"
    payload = load(name)
    res = payload["results"]
    xs, ys = [], []
    per_t = {}
    for fam, rec in res.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for tname, probes in kd.items():
                for probe, variants in probes.items():
                    means = [v["mean"] for v in variants.values()]
                    ent = float(np.mean([v["mean_entropy"] for v in variants.values()]))
                    bias = max(means) - min(means)
                    xs.append(ent); ys.append(bias)
                    per_t.setdefault(tname, {}).setdefault(kind, []).append(bias)
    r = stats.spearmanr(xs, ys)
    out = {"P15a_entropy_bias": {"spearman_rho": round(float(r.statistic), 3),
                                 "p": round(float(r.pvalue), 6), "n": len(xs)},
           "P15b_per_template": {}}
    n_pos = 0
    for tname in sorted(per_t):
        d = per_t[tname]
        if "base" in d and "instruct" in d:
            diff = float(np.mean(d["instruct"]) - np.mean(d["base"]))
            out["P15b_per_template"][tname] = round(diff, 3)
            n_pos += diff > 0
    out["P15b_summary"] = f"{n_pos}/{len(out['P15b_per_template'])} templates with instruct>base"
    (HERE / "results_t10_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
