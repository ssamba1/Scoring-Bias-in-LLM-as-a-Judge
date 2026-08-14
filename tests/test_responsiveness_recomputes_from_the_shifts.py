"""Is responsiveness the total-variation shift the paper defines it as?

Bias factorizes into decisiveness and responsiveness, and the paper's argument
turns on the second: "it rises sharply with instruction tuning (0.14 -> 0.26)
and correlates strongly and positively with bias (rho = +0.82) -- far more
tightly than decisiveness's -0.41". Responsiveness is defined as the mean total-
variation shift a nuisance induces in the answer distribution.

That definition is checkable against the released distributions, and was not
checked. The stored value came out of the analyzer and every guard on it read
what the analyzer wrote, which cannot distinguish "the analyzer computes total
variation" from "the analyzer computes something else and calls it that".

Total variation between two distributions is half the L1 distance. Computed here
from each cell's mean_dist against its probe's control, averaged over the ten
non-control variants of a checkpoint, then over families -- shaped like the
analyzer's aggregation but sharing none of its code.

Both mechanism terms now reproduce from the same released distributions:
entropy in test_entropy_recomputes_from_the_distributions, responsiveness here.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONTROL = {
    "rubric_order": "control",
    "score_id": "numeric",
    "reference_answer": "none",
    "authority": "none",
    "verbosity": "control",
}

TOLERANCE = 0.0006  # stored to four decimals, averaged over ten shifts

# score_id's "letter" variant records its distribution in TOKEN order, A..E,
# which the harness maps to scores 5..1. Every other variant records ascending
# scores, so comparing them index-wise measures the distance between P(score 1)
# and P(score 5). This test originally did exactly that, and agreed with an
# analysis making the same mistake -- two implementations, one assumption, and
# a green result that verified nothing about the alignment.
DESCENDING = {("score_id", "letter")}


def _score_ordered(probe, variant, distribution):
    """The variant's distribution indexed by ascending score."""
    if (probe, variant) in DESCENDING:
        return list(reversed(distribution))
    return distribution


def _total_variation(left, right):
    """Half the L1 distance between two distributions."""
    ls, rs = sum(left), sum(right)
    return 0.5 * sum(abs(a / ls - b / rs) for a, b in zip(left, right))


def _per_checkpoint():
    """(family, arm) -> mean TV shift across every non-control variant."""
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] scaled results not present")
    results = json.loads(path.read_text())["results"]

    shifts = {}
    for family, arms in results.items():
        for arm in ("base", "instruct"):
            cell = arms.get(arm)
            if not isinstance(cell, dict):
                continue
            values = []
            for probe, control_name in CONTROL.items():
                variants = cell.get(probe)
                if not isinstance(variants, dict):
                    continue
                control = variants.get(control_name, {})
                baseline = control.get("mean_dist") if isinstance(control, dict) else None
                if not baseline:
                    continue
                baseline = _score_ordered(probe, control_name, baseline)
                for name, record in variants.items():
                    if name == control_name or not isinstance(record, dict):
                        continue
                    distribution = record.get("mean_dist")
                    if distribution and len(distribution) == len(baseline):
                        values.append(_total_variation(
                            _score_ordered(probe, name, distribution), baseline))
            if values:
                shifts[(family, arm)] = sum(values) / len(values)
    if not shifts:
        pytest.skip("[repro] no distributions to compute shifts from")
    return shifts


def _stored():
    path = REPRO / "results_mechanism.json"
    if not path.exists():
        pytest.skip("[repro] mechanism results not present")
    return json.loads(path.read_text())


def test_the_arm_means_are_the_mean_total_variation_shifts():
    shifts, mech = _per_checkpoint(), _stored()
    responsiveness = mech.get("responsiveness")
    if not isinstance(responsiveness, dict):
        pytest.skip("[repro] no responsiveness record")

    for arm in ("base", "instruct"):
        values = [v for (_, kind), v in shifts.items() if kind == arm]
        assert values, f"no {arm} checkpoints yielded a shift"
        mine = sum(values) / len(values)
        stored = responsiveness[f"{arm}_mean"]
        assert abs(mine - stored) <= TOLERANCE, (
            f"{arm}: the release stores a responsiveness of {stored}; the "
            f"total-variation shifts in its own distributions give {mine:.4f}"
        )


def test_each_family_matches_its_own_shifts():
    """The pooled means could agree while individual families do not."""
    shifts, mech = _per_checkpoint(), _stored()
    per_family = mech.get("responsiveness_per_family")
    if not isinstance(per_family, dict):
        pytest.skip("[repro] no per-family responsiveness")

    wrong = []
    checked = 0
    for family, record in sorted(per_family.items()):
        for arm, stored in record.items():
            mine = shifts.get((family, arm))
            if mine is None:
                continue
            checked += 1
            if abs(mine - stored) > TOLERANCE:
                wrong.append(f"{family}/{arm}: stored {stored}, recomputed {mine:.4f}")
    assert checked >= 20, f"only {checked} family-arms compared"
    assert not wrong, f"per-family responsiveness does not match its shifts: {wrong[:5]}"


def test_every_shift_is_a_valid_total_variation():
    """TV lies in [0, 1]; a value outside it means the inputs were not distributions."""
    out_of_range = [
        f"{family}/{arm}={value:.4f}"
        for (family, arm), value in _per_checkpoint().items()
        if not 0.0 <= value <= 1.0
    ]
    assert not out_of_range, (
        f"a total-variation shift outside [0, 1]: {out_of_range}"
    )
