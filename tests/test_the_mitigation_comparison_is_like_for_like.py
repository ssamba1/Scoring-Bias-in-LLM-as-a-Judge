"""Are the mitigation numbers measured the same way on both sides?

The paper reported that marginalizing the score over the three score-ID formats
cut bias from 1.09 to 0.45, a 59% reduction, and the figure reached the
abstract. Two things were wrong with it.

The estimators differed. 1.09 was a max-min spread of the three format means;
0.45 was a mean absolute deviation of per-item scores from their cross-format
mean. For three values a max-min spread runs about three times a mean absolute
deviation, so most of the gap was the change of statistic. Holding the estimator
fixed, the unmitigated deviation is 0.41 against the mitigated 0.45 -- no
reduction at all, and if anything the wrong sign.

And the comparison could not fail. Score-ID bias is defined as the spread across
score-ID formats, and the mitigation averages over those same formats, so the
mitigated bias is exactly zero by construction. Averaging over the dimension the
bias is measured on is not an intervention whose effect can be estimated.

Both are now stated as what they are: the definitional result is labelled
definitional, the 0.45 is reported as the per-item cost of committing to one
format, and the reduction claim in the abstract is the template ensemble --
which averages over templates while bias is still read over score variants, a
different dimension, so nothing is built in.

This guard keeps the two estimator families apart. A future edit that compares a
deviation against a spread gets the same answer this one did, and the same
number would go back into the abstract.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"


def _mitigation():
    path = REPRO / "results_mechanism.json"
    if not path.exists():
        pytest.skip("[repro] results_mechanism.json not present")
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    mit = data.get("mitigation")
    if not mit:
        pytest.skip("[repro] no mitigation block")
    return mit


def test_the_marginalized_spread_is_zero_by_construction():
    mit = _mitigation()
    # Re-derive the flag rather than read it: averaging over the formats leaves
    # one score per item, so there is no spread across formats left to measure.
    recomputed = mit["marginalized_maxmin"] == 0.0
    assert recomputed == mit["marginalized_is_zero_by_construction"], (
        f"the release records marginalized_is_zero_by_construction="
        f"{mit['marginalized_is_zero_by_construction']} while its own "
        f"marginalized_maxmin={mit['marginalized_maxmin']} gives {recomputed}"
    )
    assert recomputed, (
        "the marginalized max-min spread is no longer zero. If marginalizing "
        "has stopped collapsing the format dimension, the mitigation is no "
        "longer definitional and the section needs rewriting, not patching."
    )


def test_the_two_estimator_families_are_not_mixed():
    mit = _mitigation()
    spreads = {"expected_maxmin", "argmax_maxmin", "marginalized_maxmin"}
    deviations = {"single_format_cost_mad", "unmitigated_mad"}
    missing = sorted((spreads | deviations) - set(mit))
    assert not missing, (
        f"{missing} absent from the mitigation block. The names carry the "
        f"estimator, which is what stops the two families being compared "
        f"across -- the error that produced the retired 59%."
    )


def test_holding_the_estimator_fixed_shows_no_reduction():
    """The finding that retired the 59%: like-for-like, there is no gain."""
    mit = _mitigation()
    unmitigated = mit["unmitigated_mad"]
    mitigated = mit["single_format_cost_mad"]
    assert mitigated >= unmitigated * 0.95, (
        f"the single-format cost ({mitigated}) has dropped well below the "
        f"unmitigated deviation ({unmitigated}). That would be a real reduction "
        f"in the same estimator and belongs in the paper as one -- it is not "
        f"what the data showed when this was written (0.4467 vs 0.4116)."
    )


def test_the_paper_does_not_claim_the_retired_reduction():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = " ".join(MACROS.read_text(encoding="utf-8", errors="replace").split())
    if "MITIGPROSE" not in text:
        pytest.skip("[paper] no mitigation prose")
    prose = text[text.index("MITIGPROSE"):][:2600]

    # The number may appear as history -- the paper explains why it was retired,
    # which is better than deleting it silently -- but not as a live claim. So
    # require the retraction context wherever it appears, rather than banning
    # the digits.
    if "59\\%" in prose:
        window = prose[max(0, prose.index("59\\%") - 320):prose.index("59\\%") + 200]
        assert "earlier version" in window, (
            "the mitigation prose states 59% without the context that retires "
            "it. That figure compared a mean absolute deviation against a "
            "max-min spread; like-for-like the data give 0.41 against 0.45, "
            "which is no reduction. If it is being reported again as a result, "
            "it is the same error."
        )
    assert "by construction" in prose, (
        "the mitigation prose no longer says the marginalized result is "
        "definitional. Averaging over the dimension the bias is measured on "
        "cannot fail, and a reader needs to be told that before the number."
    )
