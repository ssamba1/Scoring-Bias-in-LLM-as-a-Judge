"""Alignment-stage ablation analysis (preregistered P7-P9; see PREREGISTRATION.md).

Which post-training stage (SFT, DPO, RLVR) inflates responsiveness and bias?
Input : results_stages.json  (from stage_harness.py)
Output: results_stages_analysis.json + printed report + LaTeX table rows

Committed BEFORE the stage run finished; metric definitions identical to
analyze_mechanism.py / analyze_robustness.py.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}
PROBES = list(CONTROL)
STAGE_ORDER = ["base", "SFT", "DPO", "RLVR"]


def delta(means):
    return max(means.values()) - min(means.values())


def tv(a, b):
    return 0.5 * sum(abs(x - y) for x, y in zip(a, b))


def cell_feats(d, cv):
    ctrl = d[cv]
    ent = float(np.mean([d[v]["mean_entropy"] for v in d]))
    resp = float(np.mean([tv(ctrl["mean_dist"], d[v]["mean_dist"])
                          for v in d if v != cv]))
    bias = delta({v: d[v]["mean"] for v in d})
    return ent, resp, bias


def main():
    src = HERE / (sys.argv[1] if len(sys.argv) > 1 else "results_stages.json")
    payload = json.loads(src.read_text())
    res = payload["results"]

    # per (family, stage, probe) features
    rows = []
    for label, rec in res.items():
        if "scores" not in rec:
            continue
        for p in PROBES:
            if p not in rec["scores"]:
                continue
            ent, resp, bias = cell_feats(rec["scores"][p], CONTROL[p])
            rows.append(dict(family=rec["family"], stage=rec["stage"],
                             order=rec["stage_order"], probe=p,
                             entropy=round(ent, 4), resp=round(resp, 4),
                             bias=round(bias, 4)))
    fams = sorted({r["family"] for r in rows})
    out = {"n_models_scored": len({(r['family'], r['stage']) for r in rows}),
           "families": fams, "per_cell": rows}

    # stage means per family
    traj = {}
    for fam in fams:
        traj[fam] = {}
        for st in STAGE_ORDER:
            grp = [r for r in rows if r["family"] == fam and r["stage"] == st]
            if grp:
                traj[fam][st] = {k: round(float(np.mean([g[k] for g in grp])), 4)
                                 for k in ("entropy", "resp", "bias")}
    out["trajectories"] = traj

    # ---- P7: responsiveness rise appears at SFT ----
    sft_up, sft_share = [], []
    for fam in fams:
        t = traj[fam]
        if "base" not in t or "SFT" not in t:
            continue
        cells_b = [r for r in rows if r["family"] == fam and r["stage"] == "base"]
        cells_s = [r for r in rows if r["family"] == fam and r["stage"] == "SFT"]
        for p in PROBES:
            b = next((c for c in cells_b if c["probe"] == p), None)
            s = next((c for c in cells_s if c["probe"] == p), None)
            if b and s:
                sft_up.append(s["resp"] > b["resp"])
        final = t.get("RLVR") or t.get("DPO")
        if final and final["resp"] != t["base"]["resp"]:
            share = (t["SFT"]["resp"] - t["base"]["resp"]) / (final["resp"] - t["base"]["resp"])
            sft_share.append(share)
    out["P7"] = {"sft_resp_up_cells": f"{int(np.sum(sft_up))}/{len(sft_up)}",
                 "sft_share_of_total_rise": [round(float(s), 3) for s in sft_share]}

    # ---- P8: DPO/RLVR sharpen further but add less responsiveness than SFT ----
    p8 = {}
    for fam in fams:
        t = traj[fam]
        steps = [s for s in STAGE_ORDER if s in t]
        p8[fam] = {"entropy_path": [t[s]["entropy"] for s in steps],
                   "resp_path": [t[s]["resp"] for s in steps],
                   "bias_path": [t[s]["bias"] for s in steps],
                   "stages": steps}
    out["P8_paths"] = p8

    # ---- P9: bias moves with responsiveness per stage transition ----
    agree = []
    for fam in fams:
        t = traj[fam]
        steps = [s for s in STAGE_ORDER if s in t]
        for a, b in zip(steps, steps[1:]):
            dr = t[b]["resp"] - t[a]["resp"]
            db = t[b]["bias"] - t[a]["bias"]
            if abs(dr) > 1e-4 and abs(db) > 1e-4:
                agree.append(np.sign(dr) == np.sign(db))
    bt = stats.binomtest(int(np.sum(agree)), len(agree)) if agree else None
    out["P9"] = {"transitions": len(agree),
                 "sign_agreement": f"{int(np.sum(agree))}/{len(agree)}",
                 "binom_p": round(float(bt.pvalue), 5) if bt else None}

    (HERE / "results_stages_analysis.json").write_text(json.dumps(out, indent=2))
    for fam in fams:
        t = traj[fam]
        print(fam, {s: (t[s]["entropy"], t[s]["resp"], t[s]["bias"]) for s in t})
    print("P7", out["P7"])
    print("P9", out["P9"])


if __name__ == "__main__":
    main()
