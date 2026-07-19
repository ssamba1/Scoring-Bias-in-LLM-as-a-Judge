"""Robustness / depth analyses on the committed raw files. No new data.

Adds, per the peer-review roadmap:
  B1  cluster-respecting entropy->bias inference (within-checkpoint rank corr +
      mixed-effects with family random intercept)
  B2  family-clustered bootstrap CI on the leave-one-family-out predictor R^2
  B3  leave-one-family / leave-one-vendor / size-band sensitivity of the
      headline instruct effect
  B4  concordance of expected-value bias with discrete flip-rate bias
  D1  cumulants (kappa2..kappa4) of the control score distribution, base vs instruct
  D3  per-family first-order test of the decomposition:
      sign(dlog decisiveness + dlog responsiveness) vs sign(dlog bias)
  C8  template-ensembling mitigation from results_multitemplate.json

Inputs : results_scaled.json, results_multitemplate.json  (committed raw)
Output : results_robustness.json + printed report
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
QWEN_PREFIX = "Qwen"
SEED = 42


def delta(means):
    return max(means.values()) - min(means.values())


def sqrt_var(dist):
    vals = list(range(1, len(dist) + 1))
    m = sum(p * v for p, v in zip(dist, vals))
    return math.sqrt(sum(p * (v - m) ** 2 for p, v in zip(dist, vals)))


def cumulants(dist):
    vals = np.arange(1, len(dist) + 1, dtype=float)
    p = np.array(dist, dtype=float)
    p = p / p.sum()
    m1 = float((p * vals).sum())
    c = vals - m1
    mu2 = float((p * c ** 2).sum())
    mu3 = float((p * c ** 3).sum())
    mu4 = float((p * c ** 4).sum())
    return {"k2": mu2, "k3": mu3, "k4": mu4 - 3 * mu2 ** 2}


def tv(a, b):
    return 0.5 * sum(abs(x - y) for x, y in zip(a, b))


def load(name):
    return json.loads((HERE / name).read_text())


def main():
    rng = np.random.default_rng(SEED)
    scaled = load("results_scaled.json")["results"]
    out = {}

    # ---- assemble per (family, kind, probe) records ----
    recs = []          # entropy, sqrtvar, resp(TV), bias, fliprate, family, kind, probe
    for fam, rec in scaled.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for p in PROBES:
                if p not in kd:
                    continue
                d = kd[p]
                ctrl = d[CONTROL[p]]
                ent = float(np.mean([d[v]["mean_entropy"] for v in d]))
                sv = float(np.mean([sqrt_var(d[v]["mean_dist"]) for v in d]))
                resp = float(np.mean([tv(ctrl["mean_dist"], d[v]["mean_dist"])
                                      for v in d if v != CONTROL[p]]))
                bias = delta({v: d[v]["mean"] for v in d})
                ca = ctrl["per_item_argmax"]
                flip = float(np.mean([np.mean([1 if a != b else 0
                                               for a, b in zip(ca, d[v]["per_item_argmax"])])
                                      for v in d if v != CONTROL[p]]))
                recs.append(dict(family=fam, kind=kind, probe=p, entropy=ent,
                                 sqrtvar=sv, resp=resp, bias=bias, flip=flip,
                                 params_b=rec.get("params_b")))
    fams = sorted({r["family"] for r in recs})

    # ---- B1: cluster-respecting entropy->bias ----
    within = []
    for fam in fams:
        for kind in ("base", "instruct"):
            grp = [r for r in recs if r["family"] == fam and r["kind"] == kind]
            if len(grp) >= 4:
                rho = stats.spearmanr([g["entropy"] for g in grp],
                                      [g["bias"] for g in grp]).statistic
                if not math.isnan(rho):
                    within.append(rho)
    wt = stats.wilcoxon(within)
    out["B1_within_checkpoint"] = {
        "n_checkpoints": len(within), "mean_within_rho": round(float(np.mean(within)), 3),
        "frac_negative": round(float(np.mean([r < 0 for r in within])), 3),
        "wilcoxon_p": round(float(wt.pvalue), 5)}
    # contrast: does RESPONSIVENESS rank probes within a judge where entropy cannot?
    within_r = []
    for fam in fams:
        for kind in ("base", "instruct"):
            grp = [r for r in recs if r["family"] == fam and r["kind"] == kind]
            if len(grp) >= 4:
                rho = stats.spearmanr([g["resp"] for g in grp],
                                      [g["bias"] for g in grp]).statistic
                if not math.isnan(rho):
                    within_r.append(rho)
    wtr = stats.wilcoxon(within_r)
    out["B1_within_checkpoint_responsiveness"] = {
        "n_checkpoints": len(within_r),
        "mean_within_rho": round(float(np.mean(within_r)), 3),
        "frac_positive": round(float(np.mean([r > 0 for r in within_r])), 3),
        "wilcoxon_p": round(float(wtr.pvalue), 6)}
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
        df = pd.DataFrame(recs)
        m = smf.mixedlm("bias ~ entropy", df, groups=df["family"]).fit(reml=False)
        out["B1_lmm"] = {"entropy_coef": round(float(m.params["entropy"]), 4),
                         "entropy_p": round(float(m.pvalues["entropy"]), 6), "n": len(df)}
    except Exception as e:  # noqa: BLE001
        out["B1_lmm"] = {"error": str(e)[:120]}

    # ---- B2: family-clustered bootstrap CI on the LOO predictor ----
    mech = load("results_mechanism.json")
    pts = mech["predictor"]["points"]
    ent, act, pred = (np.array(pts[k]) for k in ("entropy", "actual", "predicted"))
    fam_of_point = np.repeat(np.arange(len(ent) // 2), 2)  # base,instruct adjacent per family

    def r2(a, p):
        ss = float(((a - p) ** 2).sum())
        return 1 - ss / float(((a - a.mean()) ** 2).sum())
    boots = []
    nf = fam_of_point.max() + 1
    for _ in range(10_000):
        pick = rng.integers(0, nf, nf)
        idx = np.concatenate([np.where(fam_of_point == f)[0] for f in pick])
        if np.std(act[idx]) < 1e-9:
            continue
        boots.append(r2(act[idx], pred[idx]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    out["B2_predictor_bootstrap"] = {
        "loo_r2": round(r2(act, pred), 3),
        "r2_ci95": [round(float(lo), 3), round(float(hi), 3)],
        "spearman_pred_actual": round(float(stats.spearmanr(pred, act).statistic), 3),
        "n_boot": len(boots)}

    # ---- B3: sensitivity of the headline effect (mean instruct-base Delta) ----
    fam_effect = {}
    for fam in fams:
        b = [r["bias"] for r in recs if r["family"] == fam and r["kind"] == "base"]
        i = [r["bias"] for r in recs if r["family"] == fam and r["kind"] == "instruct"]
        if b and i:
            fam_effect[fam] = float(np.mean(i) - np.mean(b))
    effs = np.array(list(fam_effect.values()))
    loo_eff = {f: round(float(np.mean([e for g, e in fam_effect.items() if g != f])), 3)
               for f in fam_effect}
    non_qwen = [e for f, e in fam_effect.items() if not f.startswith(QWEN_PREFIX)]
    big = [e for f, e in fam_effect.items()
           if (scaled[f].get("params_b") or 0) >= 1.0]
    out["B3_sensitivity"] = {
        "full_mean_effect": round(float(effs.mean()), 3),
        "n_families_positive": int((effs > 0).sum()), "n_families": len(effs),
        "loo_range": [min(loo_eff.values()), max(loo_eff.values())],
        "excl_qwen_mean": round(float(np.mean(non_qwen)), 3),
        "excl_qwen_positive": f"{int(np.sum(np.array(non_qwen) > 0))}/{len(non_qwen)}",
        "only_ge1B_mean": round(float(np.mean(big)), 3),
        "only_ge1B_positive": f"{int(np.sum(np.array(big) > 0))}/{len(big)}",
        "per_family": {f: round(e, 3) for f, e in fam_effect.items()}}

    # ---- B4: EV-bias vs flip-rate concordance ----
    rb = stats.spearmanr([r["bias"] for r in recs], [r["flip"] for r in recs])
    out["B4_readout_concordance"] = {
        "spearman_evbias_fliprate": round(float(rb.statistic), 3),
        "p": round(float(rb.pvalue), 6), "n": len(recs)}

    # ---- D1: cumulants of the control distribution, base vs instruct ----
    cum = {"base": [], "instruct": []}
    for fam in fams:
        for kind in ("base", "instruct"):
            kd = scaled[fam].get(kind)
            if not isinstance(kd, dict):
                continue
            ks = [cumulants(kd[p][CONTROL[p]]["mean_dist"]) for p in PROBES if p in kd]
            cum[kind].append({k: float(np.mean([c[k] for c in ks])) for k in ("k2", "k3", "k4")})
    out["D1_cumulants"] = {
        kind: {k: round(float(np.mean([c[k] for c in cum[kind]])), 3)
               for k in ("k2", "k3", "k4")} for kind in cum}
    k2b = [c["k2"] for c in cum["base"]]; k2i = [c["k2"] for c in cum["instruct"]]
    out["D1_cumulants"]["k2_drop_families"] = f"{sum(i < b for b, i in zip(k2b, k2i))}/{len(k2b)}"

    # ---- D3: per-cell first-order test of the decomposition ----
    # bias ~ decisiveness x responsiveness  =>  dlog bias ~ dlog sqrtvar + dlog resp
    pred_s, act_s, pairs_used = [], [], 0
    for fam in fams:
        for p in PROBES:
            b = next((r for r in recs if r["family"] == fam and r["kind"] == "base"
                      and r["probe"] == p), None)
            i = next((r for r in recs if r["family"] == fam and r["kind"] == "instruct"
                      and r["probe"] == p), None)
            if not b or not i:
                continue
            eps = 1e-6
            if min(b["sqrtvar"], i["sqrtvar"], b["resp"], i["resp"],
                   b["bias"], i["bias"]) < eps:
                continue
            dlog_pred = (math.log(i["sqrtvar"]) - math.log(b["sqrtvar"])
                         + math.log(i["resp"]) - math.log(b["resp"]))
            dlog_act = math.log(i["bias"]) - math.log(b["bias"])
            pred_s.append(dlog_pred); act_s.append(dlog_act); pairs_used += 1
    pred_a, act_a = np.array(pred_s), np.array(act_s)
    sign_acc = float(np.mean(np.sign(pred_a) == np.sign(act_a)))
    mag = stats.spearmanr(pred_a, act_a)
    bt = stats.binomtest(int(np.sum(np.sign(pred_a) == np.sign(act_a))), len(pred_a))
    out["D3_crossover"] = {
        "n_cells": pairs_used, "sign_accuracy": round(sign_acc, 3),
        "binom_p": round(float(bt.pvalue), 6),
        "spearman_dlogpred_dlogact": round(float(mag.statistic), 3),
        "spearman_p": round(float(mag.pvalue), 6)}

    # ---- C8: template-ensembling mitigation ----
    try:
        mt = load("results_multitemplate.json")["results"]
        by_model = {}
        for key, rec in mt.items():
            model, tname = key.split("__")
            for kind in ("base", "instruct"):
                kd = rec.get(kind)
                if not isinstance(kd, dict):
                    continue
                by_model.setdefault((model, kind), {})[tname] = kd
        singles, ensembles = [], []
        for (model, kind), temps in by_model.items():
            if len(temps) < 3:
                continue
            for p in PROBES:
                if any(p not in t for t in temps.values()):
                    continue
                per_t = [delta({v: t[p][v]["mean"] for v in t[p]}) for t in temps.values()]
                variants = list(next(iter(temps.values()))[p])
                ens_means = {v: float(np.mean([t[p][v]["mean"] for t in temps.values()]))
                             for v in variants}
                singles.append(float(np.mean(per_t)))
                ensembles.append(delta(ens_means))
        red = 1 - float(np.sum(ensembles)) / float(np.sum(singles))
        wt2 = stats.wilcoxon(singles, ensembles)
        out["C8_template_ensemble"] = {
            "n_cells": len(singles),
            "mean_single_template_bias": round(float(np.mean(singles)), 3),
            "mean_ensembled_bias": round(float(np.mean(ensembles)), 3),
            "reduction_frac": round(red, 3),
            "wilcoxon_p": round(float(wt2.pvalue), 6)}
    except FileNotFoundError:
        out["C8_template_ensemble"] = {"note": "results_multitemplate.json absent"}

    (HERE / "results_robustness.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    sys.exit(main())
