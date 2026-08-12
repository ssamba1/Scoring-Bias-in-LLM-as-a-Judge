"""Do the stored statistics satisfy the identities that define them?

Some numbers in the release are not independent of each other. Spearman-Brown is
a function of the split-half correlation. Variance components sum to one. An
entropy over a five-point scale cannot exceed log2(5), and a probability mass
cannot exceed one. A mean change is the difference of the two means beside it.

None of that was checked. Each quantity was compared against the prose, or
against nothing, and a value that violates its own definition would still match
the sentence quoting it -- the sentence is where it came from.

These are cheap and they fail loudly for the failures that matter: a statistic
computed on the wrong axis, a rounding applied twice, a component silently
dropped from a decomposition.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# The judges answer on a five-point scale, so entropy is bounded by log2(5).
SCALE_POINTS = 5


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[{name}] not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def test_spearman_brown_follows_from_the_split_half_correlation():
    f4 = _load("results_robustness.json").get("F4_split_half")
    if not f4:
        pytest.skip("[F4] split-half measurement absent")
    r = f4["split_half_spearman"]
    expected = 2 * r / (1 + r)
    assert abs(expected - f4["spearman_brown"]) < 0.0006, (
        f"Spearman-Brown of {r} is {expected:.4f}, stored as {f4['spearman_brown']}"
    )
    assert 0 < r <= 1, f"a split-half correlation of {r} is not a correlation"


def test_the_variance_components_sum_to_one():
    components = _load("results_robustness.json").get("E_variance_decomposition")
    if not components:
        pytest.skip("[E] variance decomposition absent")
    total = sum(components.values())
    assert abs(total - 1.0) < 0.002, (
        f"the variance components sum to {total:.4f}, not 1: {components}. A "
        f"component has been dropped or double-counted."
    )
    assert "Residual" in components, "a decomposition with no residual term is not a decomposition"
    negative = {k: v for k, v in components.items() if v < 0}
    assert not negative, f"negative variance shares: {negative}"


def test_probability_masses_stay_within_zero_and_one():
    collapse = _load("results_robustness.json").get("E3_score_collapse")
    if not collapse:
        pytest.skip("[E3] score-collapse measurement absent")
    out_of_range = [
        f"{arm}.{key}={value}"
        for arm, record in collapse.items()
        for key, value in record.items()
        if not 0.0 <= value <= 1.0
    ]
    assert not out_of_range, f"masses outside [0, 1]: {out_of_range}"

    # No inequality holds between maxp and top2_mass, and asserting one is an
    # easy mistake: the name suggests "the two most probable scores", in which
    # case maxp could not exceed it. The paper defines top2_mass as the mass on
    # scores 4-5 -- the top *ratings* -- so with the mode at 3 the instruct arm
    # legitimately has maxp 0.525 against top2_mass 0.509. My first version of
    # this test asserted the containment and failed on correct data.
    for arm, record in collapse.items():
        assert {"maxp", "top2_mass"} <= set(record), (
            f"{arm}: the score-collapse record no longer carries both masses, so "
            f"the paper's 'concentration, not leniency' contrast has changed shape"
        )


def test_entropies_stay_within_the_scale():
    mech = _load("results_mechanism.json")
    decisiveness = mech.get("decisiveness")
    if not decisiveness:
        pytest.skip("[decisiveness] measurement absent")
    limit = math.log2(SCALE_POINTS)

    values = [decisiveness["base_mean"], decisiveness["instruct_mean"]]
    values += [
        v for record in mech.get("decisiveness_per_family", {}).values() for v in record.values()
    ]
    assert len(values) >= 10, f"only {len(values)} entropies found; the panel is 13 families"
    assert max(values) <= limit + 1e-9, (
        f"an entropy of {max(values)} exceeds log2({SCALE_POINTS}) = {limit:.4f}, "
        f"which no distribution over {SCALE_POINTS} points can reach"
    )
    assert min(values) >= 0, f"negative entropy: {min(values)}"


def test_each_mean_change_is_the_difference_of_its_means():
    mech = _load("results_mechanism.json")
    wrong = []
    for name in ("decisiveness", "responsiveness", "compliance"):
        record = mech.get(name)
        if not isinstance(record, dict) or "mean_change" not in record:
            continue
        expected = record["instruct_mean"] - record["base_mean"]
        # 0.00015, not 0.002. All three values are stored to four decimals, so
        # the identity can only fail by rounding: each operand carries at most
        # 5e-5 and the stored difference another 5e-5. Measured residuals here
        # are 0.0000, 0.0001, 0.0000. At 0.002 the check would accept a stored
        # change that is simply a different number.
        if abs(expected - record["mean_change"]) > 0.00015:
            wrong.append(
                f"{name}: {record['instruct_mean']} - {record['base_mean']} = "
                f"{expected:.4f}, stored {record['mean_change']}"
            )
    assert not wrong, f"a stored change does not equal the difference of its means: {wrong}"
