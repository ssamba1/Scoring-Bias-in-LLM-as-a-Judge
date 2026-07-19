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
    path = HERE / name
    if path.exists():
        return json.loads(path.read_text())
    gz = HERE / (name + ".gz")
    if gz.exists():
        import gzip
        return json.loads(gzip.decompress(gz.read_bytes()).decode())
    raise FileNotFoundError(name)


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

    # ---- C5: replication on public-dataset items (results_dolly.json) ----
    try:
        dolly = load("results_dolly.json")["results"]
        eff, xs2, ys2 = {}, [], []
        probe_diff = {}
        for fam, rec in dolly.items():
            fb, fi = [], []
            for kind, acc in (("base", fb), ("instruct", fi)):
                kd = rec.get(kind, {})
                for p, cv in CONTROL.items():
                    if p not in kd:
                        continue
                    means = [v["mean"] for v in kd[p].values()]
                    ent = float(np.mean([v["mean_entropy"] for v in kd[p].values()]))
                    bias = max(means) - min(means)
                    xs2.append(ent); ys2.append(bias)
                    probe_diff.setdefault(p, {}).setdefault(kind, []).append(bias)
                    acc.append(bias)
            if fb and fi:
                eff[fam] = round(float(np.mean(fi) - np.mean(fb)), 3)
        e = np.array(list(eff.values()))
        rr = stats.spearmanr(xs2, ys2)
        out["C5_public_items"] = {
            "source": "databricks-dolly-15k (open_qa/general_qa), 50 items, seed 42",
            "n_families": len(eff), "mean_effect": round(float(e.mean()), 3),
            "families_positive": f"{int((e > 0).sum())}/{len(e)}",
            "entropy_bias_rho": round(float(rr.statistic), 3),
            "entropy_bias_p": round(float(rr.pvalue), 6), "n_points": len(xs2),
            "per_probe_delta": {p: round(float(np.mean(v["instruct"]) - np.mean(v["base"])), 3)
                                for p, v in probe_diff.items()
                                if "base" in v and "instruct" in v},
            "per_family": eff}
    except FileNotFoundError:
        out["C5_public_items"] = {"note": "results_dolly.json absent"}

    # ---- E: variance decomposition of bias across factors ----
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
        df2 = pd.DataFrame(recs)
        m_full = smf.ols("bias ~ C(family) + C(probe) + C(kind) + C(family):C(probe)",
                         df2).fit()
        import statsmodels.api as sm
        an = sm.stats.anova_lm(m_full, typ=2)
        ss = an["sum_sq"]
        tot = float(ss.sum())
        out["E_variance_decomposition"] = {
            k.replace("C(", "").replace(")", ""): round(float(v) / tot, 3)
            for k, v in ss.items()}
    except Exception as e:  # noqa: BLE001
        out["E_variance_decomposition"] = {"error": str(e)[:120]}

    # ---- E2: are some ITEMS systematically bias-prone across judges? ----
    # per-item |deviation from control| under each perturbed variant, averaged over
    # variants, gives an item-bias profile per (checkpoint, probe); correlate the
    # profiles across checkpoints.
    item_prof = {}
    for fam, rec in scaled.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            for p in PROBES:
                if p not in kd:
                    continue
                d = kd[p]
                ctrl = d[CONTROL[p]]["per_item"]
                devs = np.mean([[abs(a - c) for a, c in zip(d[v]["per_item"], ctrl)]
                                for v in d if v != CONTROL[p]], axis=0)
                item_prof[(fam, kind, p)] = devs
    keys = list(item_prof)
    cors = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if keys[i][2] == keys[j][2] and keys[i][:2] != keys[j][:2]:
                r = stats.spearmanr(item_prof[keys[i]], item_prof[keys[j]]).statistic
                if not math.isnan(r):
                    cors.append(r)
    out["E2_item_consistency"] = {
        "mean_cross_judge_item_corr": round(float(np.mean(cors)), 3),
        "n_pairs": len(cors),
        "note": "same-probe item-bias profiles correlated across different checkpoints"}

    # ---- E3: score collapse -- distribution shape before/after tuning ----
    shape = {"base": {"top2_mass": [], "maxp": []}, "instruct": {"top2_mass": [], "maxp": []}}
    for fam, rec in scaled.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if not isinstance(kd, dict):
                continue
            mds = [kd[p][CONTROL[p]]["mean_dist"] for p in PROBES if p in kd]
            for md in mds:
                shape[kind]["top2_mass"].append(md[3] + md[4])
                shape[kind]["maxp"].append(max(md))
    out["E3_score_collapse"] = {
        kind: {k: round(float(np.mean(v)), 3) for k, v in d.items()}
        for kind, d in shape.items()}

    # ---- E4: exact tilted score vs first-order bound (data for appendix fig) ----
    def tilt_curve(dist, ts):
        vals = np.arange(1, 6, dtype=float)
        p = np.array(dist) / np.sum(dist)
        s0 = float((p * vals).sum())
        sd = math.sqrt(float((p * (vals - s0) ** 2).sum()))
        exact, linear = [], []
        for t in ts:
            w = p * np.exp(t * vals)
            w = w / w.sum()
            exact.append(float((w * vals).sum()) - s0)
            linear.append(t * sd ** 2)  # d/dt E[v] under tilt tv at t=0 is Var(v)
        return s0, sd, exact, linear
    mean_dist_of = {"base": [], "instruct": []}
    for fam, rec in scaled.items():
        for kind in ("base", "instruct"):
            kd = rec.get(kind)
            if isinstance(kd, dict) and "rubric_order" in kd:
                mean_dist_of[kind].append(kd["rubric_order"]["control"]["mean_dist"])
    ts = [round(x, 2) for x in np.linspace(0, 1.0, 11)]
    curves = {}
    for kind, dists in mean_dist_of.items():
        avg = np.mean(dists, axis=0)
        s0, sd, exact, linear = tilt_curve(avg, ts)
        curves[kind] = {"s0": round(s0, 3), "sqrtvar": round(sd, 3),
                        "t": ts, "exact": [round(x, 4) for x in exact],
                        "first_order": [round(x, 4) for x in linear]}
    out["E4_exact_vs_first_order"] = curves

    # ---- F1: exact sign-flip permutation test for the headline effect ----
    # Under H0 (tuning direction exchangeable within family), each family's effect
    # has a random sign. n=13 -> enumerate all 2^13 = 8192 patterns exactly.
    effs2 = np.array(list(fam_effect.values()))
    obs = abs(effs2.mean())
    n = len(effs2)
    count = 0
    for mask in range(1 << n):
        signs = np.array([1 if mask >> i & 1 else -1 for i in range(n)])
        if abs((signs * effs2).mean()) >= obs - 1e-12:
            count += 1
    out["F1_exact_permutation"] = {
        "observed_mean_effect": round(float(effs2.mean()), 3),
        "exact_p_two_sided": round(count / (1 << n), 5),
        "n_patterns": 1 << n}

    # ---- F2: per-family effects with probe-resampled bootstrap CIs (forest) ----
    forest = {}
    for fam in fams:
        b = np.array([r["bias"] for r in recs if r["family"] == fam and r["kind"] == "base"])
        i = np.array([r["bias"] for r in recs if r["family"] == fam and r["kind"] == "instruct"])
        if len(b) != len(i) or not len(b):
            continue
        diff = i - b
        bs = [float(rng.choice(diff, len(diff), replace=True).mean()) for _ in range(10_000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        forest[fam] = {"effect": round(float(diff.mean()), 3),
                       "ci": [round(float(lo), 3), round(float(hi), 3)],
                       "params_b": scaled[fam].get("params_b")}
    out["F2_forest"] = forest

    # ---- F3: specification curve -- 12 analysis specifications ----
    def cell_bias(d, cv, readout, metric):
        if readout == "ev":
            means = {v: d[v]["mean"] for v in d}
        else:
            means = {v: float(np.mean(d[v]["per_item_argmax"])) for v in d}
        if metric == "maxmin":
            return max(means.values()) - min(means.values())
        return float(np.mean([abs(means[v] - means[cv]) for v in means if v != cv]))
    FORMAT_P, CONTENT_P = ["rubric_order", "score_id"], ["reference_answer", "authority", "verbosity"]
    spec_out = {}
    for readout in ("ev", "argmax"):
        for metric in ("maxmin", "meandev"):
            for pset_name, pset in (("all", PROBES), ("format", FORMAT_P), ("content", CONTENT_P)):
                effs3 = []
                for fam in fams:
                    fb, fi = [], []
                    for kind, acc in (("base", fb), ("instruct", fi)):
                        kd = scaled[fam].get(kind)
                        if not isinstance(kd, dict):
                            continue
                        for p in pset:
                            if p in kd:
                                acc.append(cell_bias(kd[p], CONTROL[p], readout, metric))
                    if fb and fi:
                        effs3.append(float(np.mean(fi) - np.mean(fb)))
                e3 = np.array(effs3)
                spec_out[f"{readout}|{metric}|{pset_name}"] = {
                    "mean_effect": round(float(e3.mean()), 3),
                    "families_positive": f"{int((e3 > 0).sum())}/{len(e3)}"}
    out["F3_specification_curve"] = {
        "specs": spec_out,
        "n_specs_positive_mean": sum(1 for v in spec_out.values() if v["mean_effect"] > 0),
        "n_specs": len(spec_out)}

    # ---- F4: split-half reliability of the bias estimator ----
    d_even, d_odd = [], []
    for fam in fams:
        for kind in ("base", "instruct"):
            kd = scaled[fam].get(kind)
            if not isinstance(kd, dict):
                continue
            for p in PROBES:
                if p not in kd:
                    continue
                halves = []
                for sl in (slice(0, None, 2), slice(1, None, 2)):
                    means = {v: float(np.mean(kd[p][v]["per_item"][sl])) for v in kd[p]}
                    halves.append(max(means.values()) - min(means.values()))
                d_even.append(halves[0]); d_odd.append(halves[1])
    r_half = stats.spearmanr(d_even, d_odd).statistic
    out["F4_split_half"] = {
        "split_half_spearman": round(float(r_half), 3),
        "spearman_brown": round(float(2 * r_half / (1 + r_half)), 3),
        "n_cells": len(d_even)}

    # ---- F5: empirical tightness of the gradient-norm bound ----
    ratios = []
    for fam in fams:
        for kind in ("base", "instruct"):
            kd = scaled[fam].get(kind)
            if not isinstance(kd, dict):
                continue
            for p in PROBES:
                if p not in kd:
                    continue
                md = np.array(kd[p][CONTROL[p]]["mean_dist"], dtype=float)
                md = md / md.sum()
                vals = np.arange(1, 6, dtype=float)
                s0 = float((md * vals).sum())
                grad = math.sqrt(float((md ** 2 * (vals - s0) ** 2).sum()))
                sv = math.sqrt(float((md * (vals - s0) ** 2).sum()))
                if sv > 1e-9:
                    ratios.append(grad / sv)
    out["F5_bound_tightness"] = {
        "mean_gradnorm_over_sqrtvar": round(float(np.mean(ratios)), 3),
        "min": round(float(np.min(ratios)), 3), "max": round(float(np.max(ratios)), 3),
        "n": len(ratios)}

    # ---- G1: variant-level decomposition -- which variant carries each bias ----
    var_share = {}
    for p in PROBES:
        acc = {}
        for fam in fams:
            for kind in ("base", "instruct"):
                kd = scaled[fam].get(kind)
                if not isinstance(kd, dict) or p not in kd:
                    continue
                ctrl = kd[p][CONTROL[p]]["mean"]
                for v in kd[p]:
                    if v != CONTROL[p]:
                        acc.setdefault(v, []).append(abs(kd[p][v]["mean"] - ctrl))
        tot = sum(float(np.mean(a)) for a in acc.values())
        var_share[p] = {v: round(float(np.mean(a)) / tot, 3) for v, a in acc.items()}
    out["G1_variant_decomposition"] = var_share

    # ---- G2: cross-dataset synthesis (main, public items, templates) ----
    datasets = {}
    datasets["main_items"] = {"mean_effect": round(float(np.array(list(fam_effect.values())).mean()), 3),
                              "families_positive": f"{int((np.array(list(fam_effect.values()))>0).sum())}/{len(fam_effect)}",
                              "n_families": len(fam_effect)}
    if "C5_public_items" in out and "mean_effect" in out["C5_public_items"]:
        c5 = out["C5_public_items"]
        datasets["public_items"] = {"mean_effect": c5["mean_effect"],
                                    "families_positive": c5["families_positive"],
                                    "n_families": c5["n_families"]}
    try:
        mt = load("results_multitemplate.json")["results"]
        effs_mt = []
        for key, rec in mt.items():
            fb, fi = [], []
            for kind, acc2 in (("base", fb), ("instruct", fi)):
                kd = rec.get(kind)
                if not isinstance(kd, dict):
                    continue
                for p, cv in CONTROL.items():
                    if p in kd:
                        means = [v["mean"] for v in kd[p].values()]
                        acc2.append(max(means) - min(means))
            if fb and fi:
                effs_mt.append(float(np.mean(fi) - np.mean(fb)))
        em = np.array(effs_mt)
        datasets["alt_templates"] = {"mean_effect": round(float(em.mean()), 3),
                                     "families_positive": f"{int((em>0).sum())}/{len(em)}",
                                     "n_families": len(em)}
    except FileNotFoundError:
        pass
    ws = np.array([d["n_families"] for d in datasets.values()], dtype=float)
    es_ = np.array([d["mean_effect"] for d in datasets.values()])
    datasets["_combined"] = {"weighted_mean_effect": round(float((ws * es_).sum() / ws.sum()), 3),
                             "total_family_measurements": int(ws.sum()),
                             "note": "n-weighted descriptive synthesis; datasets share model families"}
    out["G2_cross_dataset"] = datasets

    (HERE / "results_robustness.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    sys.exit(main())
