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
    layout_a = any(isinstance(v, dict) and ("params_b" in v or "base" in v or "instruct" in v)
                   and not is_probes(v) for v in results.values())
    if results and layout_a:
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


# score_id's "letter" variant records its distribution in TOKEN order, A..E,
# which the harness maps to scores 5..1 (token_values returns range(5, 0, -1)
# for that list alone). Every other variant records ascending scores, so
# comparing them index-wise compares P(score 1) with P(score 5). Only
# comparisons *between* variants need this; the stored means already apply the
# value map, and entropy and sqrt_var are unchanged by reversing a support.
DESCENDING = {("score_id", "letter")}


def score_ordered(probe, variant, record):
    """The variant's distribution indexed by ascending score."""
    dist = record["mean_dist"]
    return list(reversed(dist)) if (probe, variant) in DESCENDING else dist


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
                                "spearman_p": round(float(pv), 4), "n": len(xs),
                                "entropy_definition": "mean over the probe's variants"}

    # The same word, "entropy", denotes two quantities in this analysis: the
    # decisiveness result above uses the CONTROL variant only, while the link
    # above averages over a probe's variants. Recomputing the link the other way
    # is what a replicator reading the paper would do, so report it rather than
    # leave them to discover the gap: the relation is weaker but holds.
    xs_ctrl = []
    for f in fams:
        for kind in ("base", "instruct"):
            d = pairs[f][kind]
            for p in PROBES:
                xs_ctrl.append(float(d[p][CONTROL[p]]["mean_entropy"]))
    rho_c, pv_c = stats.spearmanr(xs_ctrl, ys)
    out["entropy_bias_link_control_only"] = {
        "spearman_rho": round(float(rho_c), 3), "spearman_p": round(float(pv_c), 6),
        "n": len(xs_ctrl), "entropy_definition": "control variant only",
        "note": "robustness: the headline link under the other reading of 'entropy'"}
    # per-point + per-family data for figures
    out["link_points"] = {"entropy": [round(x, 4) for x in xs], "delta": [round(y, 4) for y in ys]}

    # within-group test: does the entropy->bias relation hold WITHIN base-only and
    # WITHIN instruct-only (not just across the base/instruct split)? kinds aligns
    # with xs/ys in family,kind,probe order.
    kinds_seq = [k for f in fams for k in ("base", "instruct") for _ in PROBES]
    for grp in ("base", "instruct"):
        gx = [xs[i] for i in range(len(xs)) if kinds_seq[i] == grp]
        gy = [ys[i] for i in range(len(ys)) if kinds_seq[i] == grp]
        if len(gx) > 3:
            r, p = stats.spearmanr(gx, gy)
            out.setdefault("within_group_link", {})[grp] = {
                "spearman_rho": round(float(r), 3), "spearman_p": round(float(p), 4), "n": len(gx)}

    # size-confound control: does the entropy->bias relation survive partialling out
    # model size? (rank partial correlation given log10 params, plus size bands)
    sizes_seq = [pairs[f].get("_meta", {}).get("params_b")
                 for f in fams for _k in ("base", "instruct") for _p in PROBES]
    if all(s is not None for s in sizes_seq):
        ls = np.log10(np.array(sizes_seq, dtype=float))
        rE, rB, rS = (stats.rankdata(v) for v in (xs, ys, ls))

        def _resid(y, x):
            b = np.polyfit(x, y, 1)
            return y - np.polyval(b, x)
        pr, pp = stats.pearsonr(_resid(rE, rS), _resid(rB, rS))
        sb = stats.spearmanr(ls, ys)
        bands = {}
        for lo, hi, lab in [(0, 1, "<1B"), (1, 3.01, "1-3B"), (3.01, 1e9, ">3B")]:
            m = (10 ** ls >= lo) & (10 ** ls < hi)
            if m.sum() > 5:
                br = stats.spearmanr(np.array(xs)[m], np.array(ys)[m])
                bands[lab] = {"n": int(m.sum()), "spearman_rho": round(float(br.statistic), 3),
                              "spearman_p": round(float(br.pvalue), 4)}
        out["size_confound_control"] = {
            "partial_rank_rho_given_log10_params": round(float(pr), 3),
            "partial_p": round(float(pp), 6),
            "size_bias_spearman_rho": round(float(sb.statistic), 3),
            "size_bias_p": round(float(sb.pvalue), 4),
            "bands": bands}

    # same test using sqrt(Var_sigma(v)) directly (the exact quantity in Prop. 1)
    def sqrt_var(dist):
        vals = list(range(1, len(dist) + 1))
        mean = sum(p * v for p, v in zip(dist, vals))
        return (sum(p * (v - mean) ** 2 for p, v in zip(dist, vals))) ** 0.5
    vx, vy = [], []
    try:
        for f in fams:
            for kind in ("base", "instruct"):
                d = pairs[f][kind]
                for p in PROBES:
                    md = [d[p][v].get("mean_dist") for v in d[p]]
                    if any(m is None for m in md):
                        raise KeyError
                    vx.append(sum(sqrt_var(m) for m in md) / len(md))
                    vy.append(delta({v: d[p][v]["mean"] for v in d[p]}))
        vr, vp = stats.spearmanr(vx, vy)
        out["var_bias_link"] = {"spearman_rho": round(float(vr), 3),
                                "spearman_p": round(float(vp), 4), "n": len(vx)}
    except (KeyError, TypeError):
        out["var_bias_link"] = {"note": "mean_dist not in data"}
    out["decisiveness_per_family"] = {
        f: {"base": round(ctrl_stat(pairs[f]["base"], "mean_entropy"), 4),
            "instruct": round(ctrl_stat(pairs[f]["instruct"], "mean_entropy"), 4)} for f in fams}
    out["compliance_per_family"] = {
        f: {"base": round(ctrl_stat(pairs[f]["base"], "mean_mass"), 4),
            "instruct": round(ctrl_stat(pairs[f]["instruct"], "mean_mass"), 4)} for f in fams}

    # ---- Generality: entropy->bias law within each bias-type group ----
    out["generality"] = {}
    # P4 registered the content group as (authority, verbosity) specifically. The
    # analysis groups reference_answer with them, which is defensible -- it injects
    # text too -- but it is not the registered set, so compute both and let the
    # paper report the registered one beside it.
    for gname, glist in [("format", [p for p in FORMAT_PROBES if p in PROBES]),
                         ("content", [p for p in CONTENT_PROBES if p in PROBES]),
                         ("content_as_registered_P4",
                          [p for p in ("authority", "verbosity") if p in PROBES])]:
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

    # ---- Direct measurement of the RESPONSIVENESS term (Corollary 1) ----
    # responsiveness = how far a nuisance moves the answer distribution from control,
    # measured as mean total-variation distance between control and perturbed mean_dist.
    # The theory says bias = decisiveness x responsiveness; we test (a) that tuning
    # raises responsiveness, and (b) that responsiveness correlates POSITIVELY with bias.
    def has_dist(d):
        return all("mean_dist" in d[p][v] for p in PROBES for v in d[p])
    if all(has_dist(pairs[f]["base"]) and has_dist(pairs[f]["instruct"]) for f in fams):
        def responsiveness(model):
            tvs = []
            for p in PROBES:
                c = score_ordered(p, CONTROL[p], model[p][CONTROL[p]])
                for v in model[p]:
                    if v == CONTROL[p]:
                        continue
                    d = score_ordered(p, v, model[p][v])
                    tvs.append(0.5 * sum(abs(a - b) for a, b in zip(c, d)))  # total variation
            return float(np.mean(tvs))
        rb = [responsiveness(pairs[f]["base"]) for f in fams]
        ri = [responsiveness(pairs[f]["instruct"]) for f in fams]
        out["responsiveness"] = paired(rb, ri)
        # responsiveness vs bias, per (family, kind, probe)
        rx, ry = [], []
        for f in fams:
            for kind in ("base", "instruct"):
                d = pairs[f][kind]
                for p in PROBES:
                    c = score_ordered(p, CONTROL[p], d[p][CONTROL[p]])
                    resp = np.mean([0.5 * sum(abs(a - b) for a, b in
                                              zip(c, score_ordered(p, v, d[p][v])))
                                    for v in d[p] if v != CONTROL[p]])
                    rx.append(resp); ry.append(delta({v: d[p][v]["mean"] for v in d[p]}))
        rr, rp = stats.spearmanr(rx, ry)
        out["responsiveness_bias_link"] = {"spearman_rho": round(float(rr), 3),
                                           "spearman_p": round(float(rp), 4), "n": len(rx)}
        rkinds = [k for f in fams for k in ("base", "instruct") for _ in PROBES]
        for grp in ("base", "instruct"):
            gx = [rx[i] for i in range(len(rx)) if rkinds[i] == grp]
            gy = [ry[i] for i in range(len(ry)) if rkinds[i] == grp]
            if len(gx) > 3:
                r2, p2 = stats.spearmanr(gx, gy)
                out.setdefault("responsiveness_within_group", {})[grp] = {
                    "spearman_rho": round(float(r2), 3), "spearman_p": round(float(p2), 4), "n": len(gx)}
        out["responsiveness_per_family"] = {f: {"base": round(responsiveness(pairs[f]["base"]), 4),
                                                "instruct": round(responsiveness(pairs[f]["instruct"]), 4)} for f in fams}
        out["responsiveness_link_points"] = {"resp": [round(x, 4) for x in rx], "delta": [round(y, 4) for y in ry]}

    # ---- Predictive tool: predict a model's bias from ONE unperturbed forward
    # pass (its control-condition entropy), validated leave-one-family-out ----
    out["predictor"] = loo_predictor(pairs, fams)

    # ---- Mitigation: score-ID bias measured 3 ways ----
    out["mitigation"] = mitigation(pairs)

    # ---- Mixed-effects model on per-item deviation from control ----
    out["lmm"] = lmm(pairs)

    (HERE / "results_mechanism.json").write_text(json.dumps(out, indent=2) + "\n")
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
    # The paper reports the *rank* correlation between predicted and actual bias,
    # because with 13 families the linear fit is not the claim -- the ordering is.
    # Emit it and its own p-value: reporting the rank coefficient beside the
    # Pearson p-value pairs a statistic with a test it did not come from.
    srho, sp = stats.spearmanr(preds, Y)
    kinds = [k for f in fams for k in ("base", "instruct")]
    return {"loo_r2": round(r2, 3), "loo_pearson_r": round(float(r), 3),
            "loo_p": round(float(pv), 5),
            "loo_spearman_rho": round(float(srho), 3),
            "loo_spearman_p": round(float(sp), 5), "n_models": len(X),
            "points": {"entropy": [round(v, 4) for v in X.tolist()],
                       "actual": [round(v, 4) for v in Y.tolist()],
                       "predicted": [round(v, 4) for v in preds.tolist()],
                       "kind": kinds},
            "note": "predict bias from one unperturbed forward pass (control entropy)"}


def mitigation(pairs):
    """Score-ID bias under three readouts, with the estimator held fixed.

    An earlier version compared "expected" and "argmax" as max-min spreads
    against "marginalized" as a mean absolute deviation, and reported the gap as
    a 59% bias reduction. Those are different dispersion statistics: for three
    values a max-min spread runs about three times a mean absolute deviation, so
    most of that 59% was the change of estimator, not the mitigation. Holding
    the estimator fixed, the unmitigated mean absolute deviation is 0.41 against
    the "mitigated" 0.45 -- no reduction at all.

    The deeper problem is that marginalizing over the score-ID formats is
    averaging over the very dimension score-ID bias is measured on, so the
    mitigated bias is exactly zero by construction and cannot be a finding. What
    the 0.45 actually measured is the per-item cost of committing to one format
    instead of the average, which is a useful quantity under its own name.

    So: the two max-min readouts are compared with each other, the definitional
    result is stated as definitional, and the deviation is reported as what it
    is. The genuine measured mitigation is the template ensemble in
    analyze_robustness.py (C8), which averages over templates while measuring
    bias over score variants -- a different dimension, so nothing is built in.
    """
    maxmin, argmax_maxmin, single_format_cost, mad_unmitigated = [], [], [], []
    for f in pairs:
        for kind in ("base", "instruct"):
            d = pairs[f][kind]["score_id"]
            means = [d[v]["mean"] for v in d]
            maxmin.append(max(means) - min(means))

            arg = [float(np.mean(d[v]["per_item_argmax"])) for v in d]
            argmax_maxmin.append(max(arg) - min(arg))

            per_item = np.array([d[v]["per_item"] for v in d])   # (formats, items)
            marg = per_item.mean(axis=0)
            single_format_cost.append(float(np.abs(per_item - marg).mean()))
            # The same statistic as the line above, applied to the UNMITIGATED
            # format means: this is the like-for-like comparator that shows the
            # old 59% was an estimator artefact.
            fm = np.array(means)
            mad_unmitigated.append(float(np.abs(fm - fm.mean()).mean()))

    return {
        "estimator_note": ("max-min spreads are comparable with each other; the "
                           "deviation measures are comparable with each other; "
                           "the two families are not comparable across"),
        "expected_maxmin": round(float(np.mean(maxmin)), 4),
        "argmax_maxmin": round(float(np.mean(argmax_maxmin)), 4),
        "marginalized_maxmin": 0.0,
        "marginalized_is_zero_by_construction": True,
        "single_format_cost_mad": round(float(np.mean(single_format_cost)), 4),
        "unmitigated_mad": round(float(np.mean(mad_unmitigated)), 4),
        "reading": ("Marginalizing over the score-ID formats removes score-ID "
                    "bias by construction, since one averaged score per item "
                    "has no spread across formats; that is definitional, not a "
                    "measurement. Committing to a single format instead costs "
                    "0.45 per item on average. The like-for-like comparison "
                    "against the unmitigated deviation (0.41) shows no "
                    "reduction, so the previously reported 59% was the "
                    "difference between a max-min spread and a mean absolute "
                    "deviation. The argmax comparison is like-for-like and "
                    "stands: a more decisive readout raises the spread from "
                    "1.09 to 1.88."),
    }


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
        # This is the model the abstract quotes as "mixed-effects p<1e-3", and
        # it was the only fit in the project reporting a coefficient with no
        # diagnosis beside it: no convergence flag, no variance component, no
        # cluster-robust cross-check. analyze_robustness.py's B1_lmm has carried
        # all three since it was found not to converge, and the argument for
        # them there applies here with more force, because this coefficient is
        # in the abstract.
        import warnings

        import numpy as np

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            m = smf.mixedlm("dev ~ C(kind, Treatment('base'))", df,
                            groups=df["family"], re_formula="1"
                            ).fit(reml=False, method="lbfgs")
            notes = sorted({str(w.message)[:80] for w in caught})
        coef = [c for c in m.params.index if "kind" in c][0]

        group_var = float(m.cov_re.iloc[0, 0])
        resid = float(m.scale)
        # Share of variance sitting between families rather than within them.
        # With a boundary-ish variance component this is near zero, which is
        # itself the useful statement: the effect is not a family-level artefact.
        icc = group_var / (group_var + resid) if (group_var + resid) else float("nan")

        # Same estimate without the random effect, with family-clustered errors.
        # If the two agree, the conclusion does not rest on the variance
        # component that statsmodels is struggling with.
        clustered = smf.ols("dev ~ C(kind, Treatment('base'))", df).fit(
            cov_type="cluster", cov_kwds={"groups": df["family"]})
        ccoef = [c for c in clustered.params.index if "kind" in c][0]

        return {"instruct_coef": round(float(m.params[coef]), 4),
                "instruct_p": round(float(m.pvalues[coef]), 6),
                "note": "dev = |score - control score|; negative coef = instruct less biased",
                "n_obs": len(df), "n_families": df["family"].nunique(),
                "converged": bool(m.converged),
                "group_var": round(group_var, 6),
                "resid_scale": round(resid, 6),
                "icc": round(icc, 6),
                "se_finite": bool(np.isfinite(m.bse).all()),
                "clustered_ols_coef": round(float(clustered.params[ccoef]), 4),
                "clustered_ols_p": round(float(clustered.pvalues[ccoef]), 6),
                "fit_warnings": notes}
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
    if "responsiveness" in out:
        r = out["responsiveness"]
        print(f"\nRESPONSIVENESS (nuisance-induced distribution shift, TV):")
        print(f"  base={r['base_mean']:.3f}  instruct={r['instruct_mean']:.3f}  change={r['mean_change']:+.3f}"
              f"  dz={r['dz']}  {r['n_decreased']}/{r['n']} decreased  p={r['wilcoxon_p']}")
        rl = out.get("responsiveness_bias_link", {})
        print(f"  responsiveness vs bias: rho={rl.get('spearman_rho')} p={rl.get('spearman_p')} n={rl.get('n')}")
    print(f"\nGenerality (entropy->bias by bias type): {out.get('generality')}")
    print(f"Predictor (leave-one-family-out): {out.get('predictor')}")
    print(f"\nMitigation (score-ID bias by scoring rule): {out['mitigation']}")
    print(f"Mixed-effects: {out['lmm']}")


if __name__ == "__main__":
    main()
