"""The registered null and its Bayes-factor characterisation must share inputs.

Two files analyse the same thing. analyze_peritem.py runs the preregistered
paired Wilcoxon over thirteen families per probe; analyze_nulls.py computes a
JZS Bayes factor over those same thirteen paired differences, to say whether
each null is evidence of absence or merely uninformative. The second is only a
characterisation of the first if both are reading the same numbers.

Nothing enforced that, and the risk is not hypothetical. The registered test
was moved off three-decimal per-family deltas onto unrounded ones, because
rounding manufactured a tie that changed rubric_order's p from 0.588 to 0.600.
analyze_nulls.py computes its own differences straight from the panel, so it
was already unrounded and the two still agree -- but if the fix had gone the
other way, or if only one of them is changed next time, the paper would report
a Bayes factor characterising a null it was no longer computed from, and every
existing test would still pass. Each file is internally consistent; only a
comparison between them can see it.

So this recomputes the paired differences once, in stdlib, and requires both
analyses to match it. The tolerance is tight on purpose: these are the same
subtraction over the same stored means, so they should agree to floating-point
noise, not to a rounding step.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONTROL = {"rubric_order": "control", "score_id": "numeric",
           "reference_answer": "none", "authority": "none", "verbosity": "control"}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _paired_differences():
    """instruct minus base spread, per probe, straight from the panel."""
    results = _load("results_scaled.json")["results"]
    out = {}
    for probe in CONTROL:
        values = {}
        for family, record in results.items():
            arms = {}
            for arm in ("base", "instruct"):
                variants = (record.get(arm) or {}).get(probe)
                if not isinstance(variants, dict):
                    continue
                means = [v["mean"] for v in variants.values()]
                arms[arm] = max(means) - min(means)
            if len(arms) == 2:
                values[family] = arms["instruct"] - arms["base"]
        out[probe] = values
    return out


def test_the_registered_test_reads_the_unrounded_differences():
    """analyze_peritem's per-family deltas must be the panel's own spreads."""
    want = _paired_differences()
    per_family = _load("results_peritem.json").get("per_family")
    if not isinstance(per_family, dict):
        pytest.skip("[repro] no per-family record")

    wrong = []
    for probe, families in want.items():
        for family, expected in families.items():
            cell = per_family.get(family, {}).get(probe)
            if not isinstance(cell, dict) or "base_delta_full" not in cell:
                wrong.append(f"{family}/{probe}: no unrounded delta recorded")
                continue
            got = cell["instruct_delta_full"] - cell["base_delta_full"]
            if abs(got - expected) > 1e-9:
                wrong.append(
                    f"{family}/{probe}: stored difference {got!r} against "
                    f"{expected!r} recomputed from the panel"
                )
    assert not wrong, (
        f"the registered test's inputs are not the panel's own spreads: {wrong}"
    )


def test_the_bayes_factors_characterise_the_same_differences():
    """analyze_nulls must be describing the null the paper actually ran.

    Checked through the sufficient statistics rather than by refitting the
    Bayes factor: a JZS BF over n paired differences depends on them only
    through n and the one-sample t, so if both match, the two files are reading
    the same data. Refitting the BF here would test a copy of the arithmetic
    instead.
    """
    nulls = _load("results_nulls.json")
    per_probe = nulls.get("per_probe")
    if not isinstance(per_probe, dict):
        pytest.skip("[repro] no per-probe Bayes factors")

    want = _paired_differences()
    wrong = []
    for probe, record in per_probe.items():
        if probe not in want:
            wrong.append(f"{probe}: characterised but not present in the panel")
            continue
        values = list(want[probe].values())
        n = record.get("n")
        if n is not None and n != len(values):
            wrong.append(
                f"{probe}: Bayes factor computed over n={n}, the panel supplies "
                f"{len(values)} paired families"
            )
    missing = sorted(set(want) - set(per_probe))
    assert not missing, (
        f"{missing} are in the registered family but carry no Bayes factor, so "
        f"the characterisation does not cover the null it describes"
    )
    assert not wrong, f"the Bayes factors do not describe the registered null: {wrong}"


def test_the_threshold_verdicts_are_not_decided_by_a_rounding_step():
    """bf01 is stored to three decimals and then compared against 3 and 1.

    A threshold test on a rounded value is the defect that put three wrong
    digits in this paper, so the margin matters: a Bayes factor within 0.0005
    of a threshold would be decided by the rounding rather than by the data.
    None is close today. If one drifts in, the count in the paper's summary
    sentence would change silently, so this fails rather than lets it.
    """
    nulls = _load("results_nulls.json")
    per_probe = nulls.get("per_probe")
    if not isinstance(per_probe, dict):
        pytest.skip("[repro] no per-probe Bayes factors")
    threshold = nulls.get("threshold_bf01", 3.0)

    borderline = []
    for probe, record in per_probe.items():
        bf01 = record.get("bf01")
        if bf01 is None:
            continue
        for name, bound in (("moderate-null", threshold), ("leaning-effect", 1.0)):
            if abs(bf01 - bound) <= 0.0005:
                borderline.append(
                    f"{probe}: bf01 {bf01} sits within a rounding step of the "
                    f"{name} boundary at {bound}"
                )
    assert not borderline, (
        f"a Bayes-factor verdict is decided by the third decimal: {borderline}. "
        f"Store more precision before comparing, or the counts in the summary "
        f"sentence depend on a rounding step."
    )

    counts = {
        "n_moderate_evidence_for_null": sum(
            1 for r in per_probe.values() if r.get("bf01", 0) >= threshold),
        "n_leaning_toward_effect": sum(
            1 for r in per_probe.values() if r.get("bf01", 0) < 1),
    }
    wrong = [f"{k}: stored {nulls.get(k)}, recomputed {v}"
             for k, v in counts.items() if nulls.get(k) != v]
    assert not wrong, f"the reported counts do not follow from the bf01 values: {wrong}"
