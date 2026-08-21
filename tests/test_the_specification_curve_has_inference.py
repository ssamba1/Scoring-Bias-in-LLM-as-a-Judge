"""Does the specification curve survive its own null, and by how much?

The release carried twelve specifications descriptively -- {expected-value,
argmax} readout x {max-min, mean-deviation} metric x {all, format, content}
probe sets -- and the paper reports that all six expected-value ones are
positive. Twelve numbers are not inference. A reader could see the curve and
still not know whether one like it arises by chance.

The null is the one the registered single-specification test already uses:
instruction tuning has no effect, so each family's base and instruct labels are
exchangeable. Thirteen families means 2^13 = 8192 assignments, small enough to
enumerate, so the p-values here are exact rather than sampled.

Two statistics, because a curve can be unusual two ways, and here they disagree:

  median effect across specs   0.1241   exact p = 0.018
  specifications positive      9 of 12  exact p = 0.189

The count is weak and should be, since the twelve specifications are the same
data read twelve ways and move together; the median is the informative one.
Reporting both is the point -- picking whichever was smaller would be the error
this whole exercise exists to avoid.

Worth stating plainly: 0.018 is much weaker than the 0.00098 the registered
single-specification permutation gives. That is expected, because the argmax
specifications are the honest outliers the paper already discusses, and it is
the price of asking the question over the whole multiverse instead of one
preferred analysis. The guard keeps both numbers so the weaker one cannot
quietly disappear.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _curve():
    path = REPRO / "results_speccurve.json"
    if not path.exists():
        pytest.skip("[repro] results_speccurve.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _committed_specs():
    path = REPRO / "results_robustness.json"
    if not path.exists():
        pytest.skip("[repro] results_robustness.json not present")
    blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return blob.get("F3_specification_curve", {}).get("specs", {})


def test_the_curve_matches_the_one_already_released():
    """Two implementations of the same twelve specifications must agree.

    They did not at first. A deviation-from-mean reading of the meandev metric
    reproduced all six max-min specifications exactly and missed all six
    meandev ones; the committed analysis measures deviation from each probe's
    CONTROL variant. The metric name is ambiguous and the source is not.
    """
    curve = _curve()["per_spec_mean_effect"]
    committed = _committed_specs()
    if not committed:
        pytest.skip("[repro] committed curve absent")

    assert sorted(curve) == sorted(committed), (
        f"specification sets differ: {sorted(set(curve) ^ set(committed))}"
    )
    wrong = [
        f"{k}: inference {curve[k]} vs released {committed[k]['mean_effect']}"
        for k in curve
        if abs(curve[k] - committed[k]["mean_effect"]) > 0.0011
    ]
    assert not wrong, (
        f"the inference recomputes different effects than the released curve: "
        f"{wrong}. Both read the same twelve specifications; a disagreement "
        f"means one of them defines a metric differently."
    )


def test_the_null_is_enumerated_not_sampled():
    curve = _curve()
    assert curve["exact"] is True, "the specification-curve p-values are no longer exact"
    assert curve["null_assignments"] == 2 ** curve["n_families"], (
        f"{curve['null_assignments']} assignments for {curve['n_families']} "
        f"families; an exact test enumerates all 2^n sign patterns"
    )


def test_both_statistics_are_reported():
    """The weaker one must not vanish."""
    curve = _curve()
    for field in ("p_median_one_sided", "p_specs_positive_one_sided"):
        assert field in curve, (
            f"{field} is no longer reported. The two statistics disagree here, "
            f"and keeping only the smaller would be the selective reading this "
            f"analysis exists to rule out."
        )
    assert curve["p_specs_positive_one_sided"] > curve["p_median_one_sided"], (
        "the count statistic is no longer the weaker of the two. That is a "
        "change in what the curve says and should be described, not absorbed."
    )


def test_the_multiverse_p_is_weaker_than_the_single_spec_one():
    """The honest comparison: asking over all twelve costs significance."""
    curve = _curve()
    rob = REPRO / "results_robustness.json"
    if not rob.exists():
        pytest.skip("[repro] robustness results absent")
    single = json.loads(rob.read_text(encoding="utf-8", errors="replace")).get(
        "F1_exact_permutation", {}).get("exact_p_two_sided")
    if single is None:
        pytest.skip("[repro] registered permutation absent")

    assert curve["p_median_one_sided"] > single, (
        f"the multiverse p ({curve['p_median_one_sided']}) is no longer weaker "
        f"than the single-specification permutation ({single}). The paper's "
        f"account is that the argmax specifications are outliers which cost "
        f"significance when included; if that has reversed, the account is wrong."
    )
    assert curve["p_median_one_sided"] < 0.05, (
        f"the specification curve's median effect no longer clears 0.05 "
        f"(p={curve['p_median_one_sided']}). That is a materially weaker result "
        f"than the paper describes and needs saying explicitly."
    )
