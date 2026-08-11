"""Does the paper's proposition survive contact with the paper's measurements?

Proposition 1 bounds the first-order sensitivity of the score by the standard
deviation of the answer distribution: ||grad_l s|| <= sqrt(Var_sigma(v)). The
proof is Cauchy-Schwarz, using sigma_j <= 1 so that sum sigma_j^2 (v_j - s)^2 <=
sum sigma_j (v_j - s)^2 = Var_sigma(v). That is sound on paper.

What is checked here is that it is also true of the numbers the paper released,
which is a different question. Every quantity in the bound is measured -- the
gradient norm from the control distributions, the variance from the same
distributions, the exact tilted change by direct computation -- so the
inequality is falsifiable against the release, and a violation would mean either
the measurement is wrong or the proposition does not describe these judges.

Nothing checked it. The bound's slack is quoted as a number in the text (0.45 on
average) and that number is pinned, but the inequality it summarises was not:
a rerun producing a ratio above 1, or an exact change exceeding its own
first-order term, would have passed every existing check while contradicting the
theory section.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ROBUSTNESS = REPO / "paper" / "honest" / "repro" / "results_robustness.json"


def _robustness():
    if not ROBUSTNESS.exists():
        pytest.skip("[robustness] results_robustness.json not present")
    return json.loads(ROBUSTNESS.read_text(encoding="utf-8", errors="replace"))


def test_the_gradient_norm_never_exceeds_the_standard_deviation():
    """The proposition itself: the ratio cannot exceed 1."""
    tight = _robustness().get("F5_bound_tightness")
    if not tight:
        pytest.skip("[F5] bound-tightness measurement absent")
    assert tight["max"] <= 1.0, (
        f"the measured ||grad s|| / sqrt(Var) reaches {tight['max']}, which "
        f"violates Proposition 1. Either the gradient measurement is wrong or "
        f"the bound does not hold for these judges."
    )
    assert tight["min"] > 0, f"a non-positive ratio ({tight['min']}) is not measurable"
    assert tight["n"] >= 100, f"only {tight['n']} cells measured; the range is not the panel's"


def test_the_first_order_term_dominates_the_exact_change():
    """The linearisation must over-estimate, or the bound is not an upper bound.

    Checked at every step along the worst-case direction, not only at the
    endpoint: a crossing anywhere would mean the first-order term understates
    the true sensitivity somewhere in the range the figure plots.
    """
    exact_vs_first = _robustness().get("E4_exact_vs_first_order")
    if not exact_vs_first:
        pytest.skip("[E4] exact-vs-first-order measurement absent")

    crossings = []
    for arm, record in exact_vs_first.items():
        steps = list(zip(record["t"], record["exact"], record["first_order"]))
        assert len(steps) >= 5, f"{arm}: only {len(steps)} points along the direction"
        for t, exact, first_order in steps:
            if exact > first_order + 1e-9:
                crossings.append(f"{arm} at t={t}: exact {exact} > first-order {first_order}")
    assert not crossings, (
        f"the exact tilted score change exceeds its own first-order term: "
        f"{crossings[:4]}. The first-order term is presented as an upper bound."
    )


def test_the_slack_is_real_and_not_an_artefact_of_a_flat_curve():
    """The comparison is only meaningful if the curves actually move."""
    exact_vs_first = _robustness().get("E4_exact_vs_first_order")
    if not exact_vs_first:
        pytest.skip("[E4] measurement absent")
    for arm, record in exact_vs_first.items():
        exact = record["exact"]
        assert max(exact) - min(exact) > 0.1, (
            f"{arm}: the exact curve spans only {max(exact) - min(exact):.4f}, so "
            f"'the first-order term dominates' would hold trivially"
        )
        assert record["sqrtvar"] > 0, f"{arm}: non-positive sqrt(Var)"
