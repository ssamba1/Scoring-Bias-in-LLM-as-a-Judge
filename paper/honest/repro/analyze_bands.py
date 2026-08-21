"""Is the entropy-bias relation flat above 3B, or unresolved there? (post hoc)

The paper reports the relation as strong below 3B (-0.51 and -0.42) and flat in
the >3B subsample (n=30, rho=-0.02), and scopes its central claim on that
contrast. But those 30 rows are 3 families x 2 checkpoints x 5 probes -- thirty
numbers from three judges. Treating them as thirty independent observations is
what makes "flat" look like a finding rather than an absence of one.

Two questions, both answered with intervals rather than a p-value:

  1. What range of correlations is the >3B band actually consistent with?
  2. Do the bands differ, once family clustering is respected?

The family-clustered bootstrap resamples FAMILIES with replacement, so all rows
from a judge move together. It was validated against simulation before use: with
clustered rows, the naive Fisher interval covers a true rho only 72-77% of the
time at nominal 95%, while the clustered interval reaches ~91%. The clustered
interval is therefore the honest one and is still slightly anticonservative --
so the intervals below, if anything, are too narrow rather than too wide.

With three clusters above 3B, no method recovers much. That is the finding: the
band does not resolve the relation, and the paper should not lean on it in
either direction.

POST HOC. Not in PREREGISTRATION.md. Characterises a scope claim; establishes
no new effect.

Output: results_bands.json
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
PROBES = {"rubric_order", "score_id", "reference_answer", "authority", "verbosity"}
DRAWS = 20000
SEED = 20260820


def cells():
    """(family, params_b, mean entropy, max-min bias) per scored cell."""
    results = json.loads((HERE / "results_scaled.json").read_text())["results"]
    rows = []
    for family, record in results.items():
        params = float(record["params_b"])
        for kind in ("base", "instruct"):
            for probe, variants in (record.get(kind) or {}).items():
                if probe not in PROBES or not isinstance(variants, dict):
                    continue
                vals = [v for v in variants.values()
                        if "mean" in v and "mean_entropy" in v]
                if len(vals) < 2:
                    continue
                means = [v["mean"] for v in vals]
                rows.append((family, params,
                             sum(v["mean_entropy"] for v in vals) / len(vals),
                             max(means) - min(means)))
    return rows


def rho(rows):
    return float(stats.spearmanr([r[2] for r in rows], [r[3] for r in rows]).statistic)


def fisher_ci(r, n, conf=0.95):
    se = 1 / math.sqrt(n - 3)
    crit = stats.norm.ppf(1 - (1 - conf) / 2)
    return (math.tanh(math.atanh(r) - crit * se),
            math.tanh(math.atanh(r) + crit * se))


def clustered_draws(rows, rng, draws=DRAWS):
    """Resample families with replacement; rows from a judge move together."""
    families = sorted({r[0] for r in rows})
    by_family = {f: [r for r in rows if r[0] == f] for f in families}
    out = []
    for _ in range(draws):
        pick = rng.choice(len(families), size=len(families), replace=True)
        boot = [r for i in pick for r in by_family[families[i]]]
        xs = [r[2] for r in boot]
        ys = [r[3] for r in boot]
        if len(set(xs)) > 2 and len(set(ys)) > 2:
            value = stats.spearmanr(xs, ys).statistic
            if not math.isnan(value):
                out.append(float(value))
    return out


def main():
    rows = cells()
    below = [r for r in rows if r[1] <= 3.0]
    above = [r for r in rows if r[1] > 3.0]
    rng = np.random.default_rng(SEED)

    out = {
        "note": "POST HOC. Not preregistered. Characterises the >3B scope claim.",
        "method": ("family-clustered bootstrap; validated by simulation against "
                   "the naive Fisher interval, which covers 72-77% at nominal "
                   "95% when rows are clustered"),
        "draws": DRAWS,
        "seed": SEED,
        "bands": {},
    }

    for label, sel in (("<=3B", below), (">3B", above)):
        r = rho(sel)
        n = len(sel)
        families = sorted({x[0] for x in sel})
        naive = fisher_ci(r, n)
        boot = clustered_draws(sel, rng)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        out["bands"][label] = {
            "n_families": len(families),
            "n_cells": n,
            "spearman_rho": round(r, 4),
            "naive_ci95": [round(naive[0], 4), round(naive[1], 4)],
            "clustered_ci95": [round(float(lo), 4), round(float(hi), 4)],
        }

    r1, n1 = rho(below), len(below)
    r2, n2 = rho(above), len(above)
    z = (math.atanh(r1) - math.atanh(r2)) / math.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))

    fb = sorted({r[0] for r in below})
    fa = sorted({r[0] for r in above})
    bb = {f: [r for r in below if r[0] == f] for f in fb}
    ba = {f: [r for r in above if r[0] == f] for f in fa}
    diffs = []
    for _ in range(DRAWS):
        s1 = [r for i in rng.choice(len(fb), len(fb), replace=True) for r in bb[fb[i]]]
        s2 = [r for i in rng.choice(len(fa), len(fa), replace=True) for r in ba[fa[i]]]
        try:
            d = rho(s1) - rho(s2)
        except Exception:
            continue
        if not math.isnan(d):
            diffs.append(d)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    crosses_zero = bool(lo <= 0 <= hi)

    out["difference"] = {
        "naive_fisher_z": round(float(z), 3),
        "naive_p": round(float(2 * stats.norm.sf(abs(z))), 4),
        "clustered_ci95": [round(float(lo), 4), round(float(hi), 4)],
        "clustered_ci_crosses_zero": crosses_zero,
        "share_at_or_above_zero": round(float(np.mean(np.array(diffs) >= 0)), 4),
    }
    out["reading"] = (
        "The naive test calls the bands different (p="
        f"{out['difference']['naive_p']}), but it treats 30 rows from 3 judges as "
        "30 independent observations. Respecting family clustering, the interval "
        "for the difference "
        + ("includes zero" if crosses_zero else "excludes zero")
        + ", and the >3B band alone is consistent with correlations from "
        f"{out['bands']['>3B']['clustered_ci95'][0]} to "
        f"{out['bands']['>3B']['clustered_ci95'][1]}. The band does not resolve "
        "the relation; it is not evidence that the relation is absent there."
    )

    # The same machinery answers a second question the paper leans on harder:
    # does the headline correlation survive being clustered by judge? The paper
    # already reports a family-random-intercept model (-0.46); this corroborates
    # it by a different route, which matters because the pooled rho is quoted in
    # the abstract with an n that counts cells, not judges.
    boot_open = clustered_draws(rows, rng)
    lo_o, hi_o = np.percentile(boot_open, [2.5, 97.5])
    out["headline_open_panel"] = {
        "n_families": len(sorted({r[0] for r in rows})),
        "n_cells": len(rows),
        "spearman_rho": round(rho(rows), 4),
        "clustered_ci95": [round(float(lo_o), 4), round(float(hi_o), 4)],
        "excludes_zero": bool(hi_o < 0),
    }

    (HERE / "results_bands.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
