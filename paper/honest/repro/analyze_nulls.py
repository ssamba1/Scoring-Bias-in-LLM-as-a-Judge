"""What do the registered per-probe nulls actually support? (post hoc)

The registered test is a paired Wilcoxon per probe, Holm-corrected across five
probes, and it is null for every one. A null p-value says "not detected". It
does not distinguish a small effect from no effect, and with n=13 paired
families the test has little power -- which the paper says, but says only in
words.

This quantifies it two ways:

  * a JZS Bayes factor (Rouder et al., 2009, Psychon Bull Rev 16:225) per probe,
    which can express evidence FOR the null rather than only failure to reject;
  * the smallest equivalence margin the data would satisfy, derived from the
    90% CI, rather than choosing a SESOI and declaring success against it.

This analysis is POST HOC. It was added while auditing, it is not in
PREREGISTRATION.md, and it does not replace the registered Wilcoxon -- which
stands as the confirmatory test and stays null. It exists to characterise that
null, not to overturn it.

Output: results_nulls.json
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy import integrate, stats

HERE = Path(__file__).resolve().parent
CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}


def paired_differences():
    """instruct - base bias, one value per family, per probe."""
    results = json.loads((HERE / "results_scaled.json").read_text())["results"]
    per_probe = {probe: [] for probe in CONTROL}
    for record in results.values():
        for probe in CONTROL:
            arms = {}
            for kind in ("base", "instruct"):
                variants = (record.get(kind) or {}).get(probe)
                if not isinstance(variants, dict):
                    continue
                means = [v["mean"] for v in variants.values()]
                arms[kind] = max(means) - min(means)
            if len(arms) == 2:
                per_probe[probe].append(arms["instruct"] - arms["base"])
    return per_probe


def jzs_bf01(values, r=0.707):
    """BF in favour of the null for a one-sample t, Cauchy(0, r) prior on delta.

    Returns BF01: >1 favours the null, <1 favours an effect. Jeffreys' rough
    reading is that 1-3 is anecdotal, 3-10 moderate.
    """
    values = np.asarray(values, dtype=float)
    n = len(values)
    df = n - 1
    t = float(values.mean() / (values.std(ddof=1) / math.sqrt(n)))

    def integrand(g):
        return ((1 + n * g) ** -0.5
                * (1 + t ** 2 / ((1 + n * g) * df)) ** (-(df + 1) / 2)
                * (r ** 2 / (2 * math.pi)) ** 0.5
                * g ** -1.5 * math.exp(-r ** 2 / (2 * g)))

    bf10, _ = integrate.quad(integrand, 1e-9, np.inf, limit=200)
    null_likelihood = (1 + t ** 2 / df) ** (-(df + 1) / 2)
    return null_likelihood / bf10, t


def main():
    out = {
        "note": "POST HOC. Not preregistered. Characterises the registered "
                "per-probe null; does not replace it.",
        "prior": "JZS / Cauchy(0, 0.707) on standardised effect size",
        "per_probe": {},
    }
    for probe, diffs in paired_differences().items():
        values = np.asarray(diffs, dtype=float)
        n = len(values)
        se = values.std(ddof=1) / math.sqrt(n)
        crit90 = stats.t.ppf(0.95, n - 1)
        low = float(values.mean() - crit90 * se)
        high = float(values.mean() + crit90 * se)
        bf01, t = jzs_bf01(values)
        out["per_probe"][probe] = {
            "n": int(n),
            "mean_difference": round(float(values.mean()), 4),
            "t": round(t, 3),
            "ci90": [round(low, 4), round(high, 4)],
            # The smallest symmetric margin for which TOST would conclude
            # equivalence: the further CI bound from zero.
            "equivalence_bound": round(max(abs(low), abs(high)), 4),
            "bf01": round(float(bf01), 3),
        }

    bfs = {p: v["bf01"] for p, v in out["per_probe"].items()}
    out["moderate_evidence_for_null"] = sorted(p for p, b in bfs.items() if b >= 3)
    out["leans_toward_effect"] = sorted(p for p, b in bfs.items() if b < 1)
    out["summary"] = (
        f"No probe reaches BF01 >= 3, so none of the registered nulls is "
        f"moderate evidence of absence; {len(out['leans_toward_effect'])} of "
        f"{len(bfs)} lean toward an effect. The nulls are uninformative rather "
        f"than supportive, which is what n=13 buys."
    )

    (HERE / "results_nulls.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
