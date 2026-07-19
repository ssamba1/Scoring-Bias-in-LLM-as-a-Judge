"""Analyzer for the scaled-layout result files of the P10-P12 runs.

Usage: python analyze_newprobes.py results_probes2.json[.gz]
       python analyze_newprobes.py results_zh.json[.gz]
       python analyze_newprobes.py results_14b.json[.gz]

Computes, per probe: per-family base/instruct bias Delta, paired change; plus the
pooled entropy-bias correlation. Committed before the runs completed (P10-P12).
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
    gz = HERE / (name + ".gz") if not name.endswith(".gz") else HERE / name
    return json.loads(gzip.decompress(gz.read_bytes()).decode())


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "results_probes2.json"
    res = load(name)["results"]
    out = {"source": name, "per_probe": {}, "per_family_effect": {}}
    probes = sorted({p for rec in res.values()
                     for kind in ("base", "instruct") if isinstance(rec.get(kind), dict)
                     for p in rec[kind]})
    xs, ys = [], []
    for p in probes:
        base_d, inst_d, fams = [], [], []
        for fam, rec in res.items():
            row = {}
            for kind in ("base", "instruct"):
                kd = rec.get(kind)
                if not isinstance(kd, dict) or p not in kd:
                    continue
                means = [v["mean"] for v in kd[p].values()]
                ent = float(np.mean([v["mean_entropy"] for v in kd[p].values()]))
                bias = max(means) - min(means)
                row[kind] = bias
                xs.append(ent); ys.append(bias)
            if "base" in row and "instruct" in row:
                base_d.append(row["base"]); inst_d.append(row["instruct"]); fams.append(fam)
        if base_d:
            diff = np.array(inst_d) - np.array(base_d)
            entry = {"n_families": len(fams),
                     "mean_base": round(float(np.mean(base_d)), 3),
                     "mean_instruct": round(float(np.mean(inst_d)), 3),
                     "mean_change": round(float(diff.mean()), 3),
                     "families_positive": f"{int((diff > 0).sum())}/{len(diff)}"}
            if len(diff) >= 6:
                w = stats.wilcoxon(diff)
                entry["wilcoxon_p"] = round(float(w.pvalue), 5)
            out["per_probe"][p] = entry
    # pooled effect per family across probes
    for fam, rec in res.items():
        fb, fi = [], []
        for kind, acc in (("base", fb), ("instruct", fi)):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for p in probes:
                if p in kd:
                    means = [v["mean"] for v in kd[p].values()]
                    acc.append(max(means) - min(means))
        if fb and fi:
            out["per_family_effect"][fam] = round(float(np.mean(fi) - np.mean(fb)), 3)
    if len(xs) >= 8:
        r = stats.spearmanr(xs, ys)
        out["entropy_bias_link"] = {"spearman_rho": round(float(r.statistic), 3),
                                    "p": round(float(r.pvalue), 6), "n": len(xs)}
    stem = name.replace(".json", "").replace(".gz", "")
    (HERE / f"{stem}_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
