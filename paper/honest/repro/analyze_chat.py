"""Chat-template control analysis (P19).

Per (family, probe): Delta for base-raw, instruct-raw, instruct-chat.
Clauses: (a) chat-format bias substantial; (b) raw~chat per-cell correlation;
(c) instruct-chat vs base-raw effect.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "results_chat.json"
    res = json.loads((HERE / name).read_text())["results"]
    raw_i, chat_i, base_r = {}, {}, {}
    for fam, rec in res.items():
        for kind in ("base", "instruct"):
            for fmt, probes in rec.get(kind, {}).items():
                for p, variants in probes.items():
                    means = [v["mean"] for v in variants.values()]
                    delta = max(means) - min(means)
                    key = (fam, p)
                    if kind == "instruct" and fmt == "raw":
                        raw_i[key] = delta
                    elif kind == "instruct" and fmt == "chat":
                        chat_i[key] = delta
                    elif kind == "base":
                        base_r[key] = delta
    keys = sorted(k for k in raw_i if k in chat_i and k in base_r)
    r = [raw_i[k] for k in keys]
    c = [chat_i[k] for k in keys]
    b = [base_r[k] for k in keys]
    sr = stats.spearmanr(r, c)
    fams = sorted({k[0] for k in keys})
    per_family = {}
    for f in fams:
        ci = float(np.mean([chat_i[k] for k in keys if k[0] == f]))
        br = float(np.mean([base_r[k] for k in keys if k[0] == f]))
        per_family[f] = round(ci - br, 3)
    out = {
        "n_cells": len(keys),
        "P19a": {"mean_chat_delta": round(float(np.mean(c)), 3),
                 "all_cells_gt_0p1": bool(all(x > 0.1 for x in c)),
                 "chat_ge_raw_cells": f"{sum(cc >= rr for cc, rr in zip(c, r))}/{len(c)}"},
        "P19b": {"raw_chat_spearman": round(float(sr.statistic), 3),
                 "p": round(float(sr.pvalue), 3)},
        "P19c": {"mean_chat_minus_base": round(float(np.mean(c) - np.mean(b)), 3),
                 "per_family": per_family,
                 "families_positive": f"{sum(v > 0 for v in per_family.values())}/{len(per_family)}"}}
    (HERE / "results_chat_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
