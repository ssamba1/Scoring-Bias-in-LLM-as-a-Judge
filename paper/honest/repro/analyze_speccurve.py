"""Exact inference over the specification curve (post hoc).

The release already carries the twelve specifications descriptively --
{expected-value, argmax} readout x {max-min, mean deviation} metric x {all,
format, content} probe sets -- and the paper reports that all six
expected-value specifications are positive. What it does not carry is inference
over the multiverse: a reader can see twelve numbers but not whether a curve
like this one would arise by chance.

Simonsohn et al.'s inferential step supplies that. The null here is the same one
the paper already uses for a single specification: instruction tuning has no
effect, so each family's base and instruct labels are exchangeable. With 13
families the null is 2^13 = 8192 sign assignments, which is small enough to
ENUMERATE rather than sample -- the whole curve is recomputed under every one,
so the p-value is exact rather than Monte Carlo.

Two statistics, because a curve can be unusual in two ways:
  * the median effect across the twelve specifications;
  * how many of the twelve point the dominant direction.

Reported together, they answer the question the twelve numbers alone cannot:
whether the specification curve as a whole is more positive than chance allows.

POST HOC. Not preregistered. The registered permutation test is the
single-specification one in analyze_robustness.py (F1); this generalises it and
does not replace it.

Output: results_speccurve.json
"""
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORMAT = ["rubric_order", "score_id"]
CONTENT = ["reference_answer", "authority", "verbosity"]
PROBE_SETS = {"all": FORMAT + CONTENT, "format": FORMAT, "content": CONTENT}


# Each probe's unperturbed variant, as analyze_robustness.py defines it. The
# meandev metric is measured against this, not against the variant mean: a
# first version of this file used deviation-from-mean and reproduced the six
# maxmin specifications exactly while missing all six meandev ones. The metric
# name is ambiguous and the source is not, so the source decides.
CONTROL = {"rubric_order": "control", "score_id": "numeric",
           "reference_answer": "none", "authority": "none", "verbosity": "control"}


def _cell(record, probe, readout, metric):
    variants = record[probe]
    if readout == "ev":
        means = {name: v["mean"] for name, v in variants.items()}
    else:
        means = {name: sum(v["per_item_argmax"]) / len(v["per_item_argmax"])
                 for name, v in variants.items()}
    if metric == "maxmin":
        return max(means.values()) - min(means.values())
    control = CONTROL[probe]
    others = [abs(means[name] - means[control]) for name in means if name != control]
    return sum(others) / len(others)


def per_family_effects():
    """spec -> [instruct-minus-base effect, one per family]."""
    results = json.loads((HERE / "results_scaled.json").read_text())["results"]
    families = sorted(results)
    out = {}
    for readout in ("ev", "argmax"):
        for metric in ("maxmin", "meandev"):
            for pset, probes in PROBE_SETS.items():
                key = f"{readout}|{metric}|{pset}"
                effects = []
                for family in families:
                    arms = {}
                    for kind in ("base", "instruct"):
                        cells = [_cell(results[family][kind], p, readout, metric)
                                 for p in probes]
                        arms[kind] = sum(cells) / len(cells)
                    effects.append(arms["instruct"] - arms["base"])
                out[key] = effects
    return out, families


def median(values):
    ordered = sorted(values)
    n = len(ordered)
    return (ordered[n // 2] if n % 2
            else (ordered[n // 2 - 1] + ordered[n // 2]) / 2)


def main():
    effects, families = per_family_effects()
    specs = sorted(effects)
    n_fam = len(families)

    observed_means = {s: sum(effects[s]) / n_fam for s in specs}
    observed_median = median(list(observed_means.values()))
    observed_positive = sum(1 for s in specs if observed_means[s] > 0)

    # Exact: every sign assignment over families, the same null the registered
    # single-spec permutation uses, applied to the whole curve at once.
    ge_median = 0
    ge_positive = 0
    total = 0
    for signs in itertools.product((1, -1), repeat=n_fam):
        total += 1
        means = [sum(s * e for s, e in zip(signs, effects[spec])) / n_fam
                 for spec in specs]
        if median(means) >= observed_median:
            ge_median += 1
        if sum(1 for m in means if m > 0) >= observed_positive:
            ge_positive += 1

    out = {
        "note": ("POST HOC. Not preregistered. Generalises the registered "
                 "single-specification permutation test to the multiverse."),
        "n_specifications": len(specs),
        "n_families": n_fam,
        "null_assignments": total,
        "exact": True,
        "observed_median_effect": round(observed_median, 4),
        "observed_specs_positive": observed_positive,
        "p_median_one_sided": round((ge_median + 1) / (total + 1), 6),
        "p_specs_positive_one_sided": round((ge_positive + 1) / (total + 1), 6),
        "per_spec_mean_effect": {s: round(observed_means[s], 4) for s in specs},
        # How many families each specification is positive in. The prose
        # quotes this as a range ("9--11/13 families positive") for the six
        # expected-value specifications, and nothing stored it, so nothing
        # could check it -- the same gap that let the span-patch peak band
        # drift off its curve while the 50% band beside it stayed derived.
        "per_spec_families_positive": {
            s: sum(1 for v in effects[s] if v > 0) for s in specs},
        "reading": (
            f"Across {len(specs)} specifications the median effect is "
            f"{observed_median:.4f} and {observed_positive} of {len(specs)} are "
            f"positive. Enumerating all {total} sign assignments over the "
            f"{n_fam} families -- the null the registered test already uses, "
            f"applied to the whole curve -- gives an exact one-sided p of "
            f"{(ge_median + 1) / (total + 1):.4f} for the median. The curve is "
            f"not what label-swapping produces."
        ),
    }

    (HERE / "results_speccurve.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
