#!/usr/bin/env python3
"""
Mechanism analysis for the enriched harness output (results_scaled.json with
per-item entropy / decisiveness / answer-mass).

Tests, honestly and from data, WHY instruction tuning changes scoring bias:

  H-sharp : instruction tuning lowers the entropy of the judge's score
            distribution (sharper, more decisive scoring).
  H-comply: instruction tuning increases the probability mass placed on the
            valid answer tokens (better format compliance).
  H-link  : across families and probes, a more entropic (less decisive) score
            distribution predicts larger bias (Delta) -- the mechanism linking
            decisiveness to bias.
  Mitig   : compares bias measured three ways (expected value, discrete argmax,
            format-marginalized) to see which scoring method is least biased.

Plus a linear mixed-effects model (random intercepts for family and item) on the
per-item absolute deviation from the control variant, testing the base-vs-instruct
effect while accounting for family and item heterogeneity.

Usage:  python analyze_mechanism.py [results_scaled.json]
Output: results_mechanism.json  (+ printed report)
"""
from __future__ import annotations
import json, sys, math
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "results_scaled.json"
CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}
FORMAT_PROBES = ["rubric_order", "score_id"]
CONTENT_PROBES = ["reference_answer", "authority", "verbosity"]
PROBES = ["rubric_order", "score_id", "reference_answer"]  # reset in main() from data
INSTRUCT_SUFFIXES = ("-Instruct", "-instruct", "-IT", "-it", "-chat", "-Chat", "-Base", "-base")


def pairs_from(payload):
    results = payload["results"]

    def is_probes(d):
        return isinstance(d, dict) and "rubric_order" in d
    fams = {}
    if results and all(("base" in v or "instruct" in v) and not is_probes(v) for v in results.values()):
        for fam, rec in results.items():
            fams[fam] = {k: rec[k] for k in ("base", "instruct") if k in rec}
            fams[fam]["_meta"] = {"params_b": rec.get("params_b"), "training": rec.get("training")}
    else:
        for model, data in results.items():
            fam = model
            for s in INSTRUCT_SUFFIXES:
                if fam.endswith(s):
                    fam = fam[: -len(s)]; break
            kind = "instruct" if any(model.endswith(s) for s in INSTRUCT_SUFFIXES[:6]) else "base"
            fams.setdefault(fam, {})[kind] = data
    return {f: d for f, d in fams.items() if "base" in d and "instruct" in d}


def paired(a, b):
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    try:
        _, p = stats.wilcoxon(a, b); p = float(p)
    except ValueError:
        p = float("nan")
    sd = d.std(ddof=1)
    return {"base_mean": round(float(a.mean()), 4), "instruct_mean": round(float(b.mean()), 4),
            "mean_change": round(float(d.mean()), 4),
            "dz": round(float(d.mean() / sd), 3) if sd > 0 else None,
            "n_decreased": int((d < 0).sum()), "n": len(d),
            "wilcoxon_p": None if math.isnan(p) else round(p, 4)}


def delta(vmeans):
    v = list(vmeans.values()); return max(v) - min(v)


def main():
    payload = json.loads(SRC.read_text())
    pairs = pairs_from(payload)
    fams = list(pairs)
    global PROBES
    sample = next(iter(pairs.values()))["base"]
    PROBES = [p for p in CONTROL if p in sample]
    out = {"source": SRC.name, "n_families": len(fams), "families": fams, "probes": PROBES}

    # ---- H-sharp: control-variant entropy, base vs instruct ----
    def ctrl_stat(d, key):
        return float(np.mean([d[p][CONTROL[p]][key] for p in PROBES]))
    out["decisiveness"] = paired([ctrl_stat(pairs[f]["base"], "mean_entropy") for f in fams],
                                 [ctrl_stat(pairs[f]["instruct"], "mean_entropy") for f in fams])
    # ---- H-comply: answer-token mass, base vs instruct ----
    out["compliance"] = paired([ctrl_stat(pairs[f]["base"], "mean_mass") for f in fams],
                               [ctrl_stat(pairs[f]["instruct"], "mean_mass") for f in fams])

    # ---- H-link: entropy vs bias across (family, kind, probe) ----
    xs, ys = [], []
    for f in fams:
        for kind in ("base", "instruct"):
            d = pairs[f][kind]
            for p in PROBES:
                ent = np.mean([d[p][v]["mean_entropy"] for v in d[p]])
                dl = delta({v: d[p][v]["mean"] for v in d[p]})
                xs.append(ent); ys.append(dl)
    rho, pv = stats.spearmanr(xs, ys)
    out["entropy_bias_link"] = {"spearman_rho": round(float(rho), 3),
                                "spearman_p": round(float(pv), 4), "n": len(xs)}
    # per-point + per-family data for figures
    out["link_points"] = {"entropy": [round(x, 4) for x in xs], "delta": [round(y, 4) for y in ys]}
    out["decisiveness_per_family"] = {
        f: {"base": round(ctrl_stat(pairs[f]["base"], "mean_entropy"), 4),
            "instruct": round(ctrl_stat(pairs[f]["instruct"], "mean_entropy"), 4)} for f in fams}
    out["compliance_per_family"] = {
        f: {"base": round(ctrl_stat(pairs[f]["base"], "mean_mass"), 4),
            "instruct": round(ctrl_stat(pairs[f]["instruct"], "mean_mass"), 4)} for f in fams}

    # ---- Generality: entropy->bias law within each bias-type group ----
    out["generality"] = {}
    for gname, glist in [("format", [p for p in FORMAT_PROBES if p in PROBES]),
                         ("content", [p for p in CONTENT_PROBES if p in PROBES])]:
        gx, gy = [], []
        for f in fams:
            for kind in ("base", "instruct"):
                d = pairs[f][kind]
                for p in glist:
                    gx.append(np.mean([d[p][v]["mean_entropy"] for v in d[p]]))
                    gy.append(delta({v: d[p][v]["mean"] for v in d[p]}))
        if len(gx) > 3:
            r, pv = stats.spearmanr(gx, gy)
            out["generality"][gname] = {"probes": glist, "spearman_rho": round(float(r), 3),
                                        "spearman_p": round(float(pv), 4), "n": len(gx)}

    # ---- Predictive tool: predict a model's bias from ONE unperturbed forward
    # pass (its control-condition entropy), validated leave-one-family-out ----
    out["predictor"] = loo_predictor(pairs, fams)

    # ---- Mitigation: score-ID bias measured 3 ways ----
    out["mitigation"] = mitigation(pairs)

    # ---- Mixed-effects model on per-item deviation from control ----
    out["lmm"] = lmm(pairs)

    (HERE / "results_mechanism.json").write_text(json.dumps(out, indent=2))
    _report(out)


def loo_predictor(pairs, fams):
    """Can we predict a model's overall bias from ONE unperturbed forward pass?
    Feature x = mean control-condition score entropy (over probes); target
    y = mean bias Delta (over probes). Leave-one-family-out: fit a line on the
    other models, predict the held-out one. Reports out-of-sample correlation/R2."""
    def feats(model):
        d = model
        x = np.mean([d[p][CONTROL[p]]["mean_entropy"] for p in PROBES])
        y = np.mean([delta({v: d[p][v]["mean"] for v in d[p]}) for p in PROBES])
        return float(x), float(y)
    pts = []
    for f in fams:
        for kind in ("base", "instruct"):
            pts.append(feats(pairs[f][kind]))
    if len(pts) < 5:
        return {"note": "need >=5 models", "n": len(pts)}
    X = np.array([p[0] for p in pts]); Y = np.array([p[1] for p in pts])
    preds = np.zeros_like(Y)
    for i in range(len(X)):
        m = np.ones(len(X), bool); m[i] = False
        b, a = np.polyfit(X[m], Y[m], 1)
        preds[i] = a + b * X[i]
    ss_res = float(np.sum((Y - preds) ** 2)); ss_tot = float(np.sum((Y - Y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    r, pv = stats.pearsonr(preds, Y)
    kinds = [k for f in fams for k in ("base", "instruct")]
    return {"loo_r2": round(r2, 3), "loo_pearson_r": round(float(r), 3),
            "loo_p": round(float(pv), 5), "n_models": len(X),
            "points": {"entropy": [round(v, 4) for v in X.tolist()],
                       "actual": [round(v, 4) for v in Y.tolist()],
                       "predicted": [round(v, 4) for v in preds.tolist()],
                       "kind": kinds},
            "note": "predict bias from one unperturbed forward pass (control entropy)"}


def mitigation(pairs):
    """For score_id (the format probe), compare bias measured by expected value,
    by discrete argmax, and by marginalizing over formats (mean of the three
    variant means -> residual spread). Lower = a more bias-robust scoring rule."""
    res = {}
    for method in ("expected", "argmax", "marginalized"):
        vals = []
        for f in pairs:
            for kind in ("base", "instruct"):
                d = pairs[f][kind]["score_id"]
                if method == "expected":
                    means = [d[v]["mean"] for v in d]
                    vals.append(max(means) - min(means))
                elif method == "argmax":
                    means = [float(np.mean(d[v]["per_item_argmax"])) for v in d]
                    vals.append(max(means) - min(means))
                else:  # marginalized: per-item mean across formats, then spread is ~0 by construction
                    per_item = np.array([d[v]["per_item"] for v in d])       # (3, 50)
                    marg = per_item.mean(axis=0)                             # (50,)
                    # residual bias = how far each format sits from the marginal, averaged
                    vals.append(float(np.abs(per_item - marg).mean()))
        res[method] = round(float(np.mean(vals)), 4)
    return res


def lmm(pairs):
    try:
        import pandas as pd, statsmodels.formula.api as smf
    except Exception as e:
        return {"note": f"statsmodels unavailable: {e}"}
    rows = []
    for f in pairs:
        for kind in ("base", "instruct"):
            d = pairs[f][kind]
            for p in PROBES:
                ctrl = d[p][CONTROL[p]]["per_item"]
                for v in d[p]:
                    if v == CONTROL[p]:
                        continue
                    for i, (a, b) in enumerate(zip(ctrl, d[p][v]["per_item"])):
                        rows.append({"dev": abs(b - a), "kind": kind, "family": f,
                                     "item": i, "probe": p})
    if not rows:
        return {"note": "no rows"}
    df = pd.DataFrame(rows)
    try:
        m = smf.mixedlm("dev ~ C(kind, Treatment('base'))", df, groups=df["family"],
                        re_formula="1").fit(reml=False, method="lbfgs")
        coef = [c for c in m.params.index if "kind" in c][0]
        return {"instruct_coef": round(float(m.params[coef]), 4),
                "instruct_p": round(float(m.pvalues[coef]), 4),
                "note": "dev = |score - control score|; negative coef = instruct less biased",
                "n_obs": len(df), "n_families": df["family"].nunique()}
    except Exception as e:
        return {"note": f"LMM fit failed: {e}", "n_obs": len(df)}


def _report(out):
    print(f"Source: {out['source']}  families: {out['n_families']}\n")
    for key, title in [("decisiveness", "H-sharp: score-distribution entropy (bits)"),
                       ("compliance", "H-comply: answer-token probability mass")]:
        s = out[key]
        print(f"{title}\n  base={s['base_mean']:.3f}  instruct={s['instruct_mean']:.3f}  "
              f"change={s['mean_change']:+.3f}  dz={s['dz']}  {s['n_decreased']}/{s['n']}  p={s['wilcoxon_p']}")
    el = out["entropy_bias_link"]
    print(f"\nH-link: entropy vs bias  Spearman rho={el['spearman_rho']}  p={el['spearman_p']}  n={el['n']}")
    print(f"\nGenerality (entropy->bias by bias type): {out.get('generality')}")
    print(f"Predictor (leave-one-family-out): {out.get('predictor')}")
    print(f"\nMitigation (score-ID bias by scoring rule): {out['mitigation']}")
    print(f"Mixed-effects: {out['lmm']}")


if __name__ == "__main__":
    main()
