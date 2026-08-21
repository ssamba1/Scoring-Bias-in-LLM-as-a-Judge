"""Every yes/no verdict in the release must survive its own stored precision.

An AST sweep of all nineteen analysers found exactly four ordered comparisons
whose operands are values the analysis has already rounded. One is a false
positive (analyze_robustness's epsilon guard reads unrounded records). The
other three each decide something the paper states:

    analyze_gran.py:46        P17b, instruct bias exceeds base at each scale
    analyze_readout.py:66     instruct_below_base, Limitation 5's asymmetry
    analyze_robustness.py:550 how many of twelve specifications are positive

A comparison between rounded values is decided by the rounding whenever the
operands are closer together than the rounding can move them. That is not a
hypothetical failure here -- it is the same composition that put three wrong
digits in this paper, where a value rounded for storage was rounded again for
display and landed on a digit that was not its own.

None of the three is close today, and the margins are not marginal: the
smallest is 0.030 against a rounding step of 0.001, thirty times over. Pinning
that is the point. These verdicts are stated in the paper as facts about the
judges, and if a future data change slides one to within a rounding step of its
boundary, the verdict would flip on a stored digit rather than on evidence and
nothing else in the suite would notice.

**The step is declared, not inferred.** A first version of this file read the
precision off each value's own repr, and a mutation exposed why that is wrong:
a value edited to carry more decimals silently widens its own tolerance, and
0.0 implies a step of 0.05 because repr gives it one decimal place. The step
therefore comes from the round() call in the analyser, recorded below, and each
source is separately checked for storing anything finer than it declares --
which would mean the declaration, not the margin, is what is wrong.

The margin required is the worst case. Rounding each operand to d decimals
moves it by at most half a step, so a pairwise comparison can shift by a whole
step and a comparison against a fixed threshold by half of one.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Decimal places each analyser rounds to, read from its round() call:
#   analyze_gran.py       round(float(np.mean(rows[kind])), 3)
#   analyze_readout.py    round(100 * sum(ordered) / n, 4)
#   analyze_robustness.py round(float(e3.mean()), 3)
GRAN_DP = 3
READOUT_DP = 4
SPECCURVE_DP = 3


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _too_precise(values, declared_dp):
    """Values carrying more decimals than the analyser claims to round to."""
    bad = []
    for label, value in values:
        text = repr(float(value))
        if "e" in text or "." not in text:
            continue
        if len(text.split(".")[1]) > declared_dp:
            bad.append(f"{label}={value} carries more than {declared_dp} decimals")
    return bad


def test_the_scale_ladder_verdicts_clear_their_rounding_step():
    """P17b compares two values the analysis rounded to three decimals."""
    gran = _load("results_gran_analysis.json")
    per_scale = gran.get("per_scale")
    verdicts = gran.get("P17b_instruct_gt_base")
    if not per_scale or not verdicts:
        pytest.skip("[repro] scale ladder absent")

    step = 10 ** -GRAN_DP
    stored = [(f"{s}/{k}", per_scale[s][k]) for s in verdicts if s in per_scale
              for k in ("mean_bias_base", "mean_bias_instruct")]
    assert not _too_precise(stored, GRAN_DP), (
        f"analyze_gran is declared to round to {GRAN_DP} places but stores finer "
        f"values, so the step used here is wrong: {_too_precise(stored, GRAN_DP)}"
    )

    problems = []
    for scale, verdict in verdicts.items():
        cell = per_scale.get(scale)
        if not cell:
            problems.append(f"{scale}: verdict recorded with no per-scale numbers")
            continue
        base, instruct = cell["mean_bias_base"], cell["mean_bias_instruct"]
        if verdict != (instruct > base):
            problems.append(
                f"{scale}: stored verdict {verdict}, but {instruct} > {base} "
                f"is {instruct > base}"
            )
        elif abs(instruct - base) <= step:
            problems.append(
                f"{scale}: instruct {instruct} and base {base} differ by "
                f"{abs(instruct - base):.6f}, no more than the {step} rounding "
                f"step, so the verdict rests on the stored digits"
            )
    assert not problems, f"the scale-ladder verdicts are not safe: {problems}"


def test_the_growth_verdict_clears_its_rounding_step():
    """P17a is a chain of comparisons over the same rounded values."""
    gran = _load("results_gran_analysis.json")
    growth = gran.get("P17a_growth")
    if not growth:
        pytest.skip("[repro] growth verdict absent")

    step = 10 ** -GRAN_DP
    problems = []
    for arm, record in growth.items():
        values = record.get("biases_by_scale")
        if not values or len(values) < 2:
            continue
        assert not _too_precise([(arm, v) for v in values], GRAN_DP), (
            f"{arm}: scale ladder stores more than {GRAN_DP} decimals"
        )
        recomputed = all(b <= a for b, a in zip(values, values[1:]))
        if record.get("monotone_increasing") != recomputed:
            problems.append(
                f"{arm}: stored monotone_increasing "
                f"{record.get('monotone_increasing')}, {values} gives {recomputed}"
            )
        for earlier, later in zip(values, values[1:]):
            if abs(later - earlier) <= step:
                problems.append(
                    f"{arm}: consecutive scales {earlier} and {later} differ by "
                    f"{abs(later - earlier):.6f}, within the {step} rounding step"
                )
    assert not problems, f"the growth verdict is not safe: {problems}"


def test_the_readout_asymmetry_clears_its_rounding_step():
    """instruct_below_base backs Limitation 5 and compares two rounded means."""
    readout = _load("results_readout.json")
    if "instruct_below_base" not in readout:
        pytest.skip("[repro] readout asymmetry absent")

    base = readout["base"]["mean_pct"]
    instruct = readout["instruct"]["mean_pct"]
    step = 10 ** -READOUT_DP
    assert not _too_precise([("base", base), ("instruct", instruct)], READOUT_DP), (
        f"analyze_readout is declared to round to {READOUT_DP} places but stores finer"
    )

    assert readout["instruct_below_base"] == (instruct < base), (
        f"stored flag {readout['instruct_below_base']}, but instruct "
        f"{instruct} < base {base} is {instruct < base}"
    )
    assert abs(instruct - base) > step, (
        f"instruct {instruct}% and base {base}% differ by "
        f"{abs(instruct - base):.6f}, no more than the {step} rounding step. "
        f"Limitation 5's asymmetry would then rest on a stored digit."
    )


def test_no_specification_sits_on_the_sign_boundary():
    """The curve's positive count compares rounded effects against zero."""
    curve = _load("results_robustness.json").get("F3_specification_curve")
    if not curve or not curve.get("specs"):
        pytest.skip("[repro] specification curve absent")
    specs = curve["specs"]

    stored = [(name, r["mean_effect"]) for name, r in specs.items()]
    assert not _too_precise(stored, SPECCURVE_DP), (
        f"the curve is declared to round to {SPECCURVE_DP} places but stores "
        f"finer values: {_too_precise(stored, SPECCURVE_DP)}"
    )

    half_step = 0.5 * 10 ** -SPECCURVE_DP
    problems = [
        f"{name}: mean effect {effect} is within {half_step} of zero, so whether "
        f"it counts as positive is decided by rounding"
        for name, effect in stored if abs(effect) <= half_step
    ]
    assert not problems, f"a specification sits on the sign boundary: {problems}"

    recomputed = sum(1 for _n, e in stored if e > 0)
    assert curve["n_specs_positive_mean"] == recomputed, (
        f"the curve reports {curve['n_specs_positive_mean']} positive "
        f"specifications; the twelve stored effects give {recomputed}"
    )
    assert curve["n_specs"] == len(specs), (
        f"n_specs is {curve['n_specs']} against {len(specs)} stored specifications"
    )
