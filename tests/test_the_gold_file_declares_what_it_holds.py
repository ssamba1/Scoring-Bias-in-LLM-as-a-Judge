"""The ground-truth file's declared count, and its aggregates, against its arrays.

`gold_results.json` backs the paper's causal claim -- that scoring bias corrupts
real quality judgments, with rubric reversal dropping good-vs-bad discrimination
from 0.98 to 0. It declares `n_gold: 20` and stores, for each of forty cells, a
`margins` array with `mean_margin` and `accuracy` beside it.

None of that was checked. `test_released_data_is_well_formed.py` sweeps every
released file for a declared item count and compares it against the arrays, and
it *skips this one* -- it looks for a field called `n_items`, and the gold file
calls it `n_gold`. The skip is reported honestly, which is why it was findable,
but a parameterised sweep that skips the one file backing a headline claim is
covering less than its name suggests.

So the declared count and both aggregates are recomputed here from the arrays
themselves. All forty cells hold exactly twenty margins, every `mean_margin` is
the mean of its array, and every `accuracy` is the fraction of margins above
zero -- which is what "sign fixed so positive means correct" has to mean if the
accuracy column is to be read the way the paper reads it.

That last one is the substantive check. `accuracy` and `margins` are stored
independently by the harness, so agreement between them is evidence the sign
convention was applied consistently; disagreement would mean the discrimination
numbers and the margin numbers describe different things, and the ground-truth
result is built on both.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GOLD = REPO / "paper" / "honest" / "repro" / "gold_results.json"

TOLERANCE = 5e-4


def _gold():
    if not GOLD.exists():
        pytest.skip("[repro] gold_results.json not present")
    return json.loads(GOLD.read_text(encoding="utf-8", errors="replace"))


def _cells(blob):
    """(family, arm, condition, record) for every cell carrying margins."""
    for family, arms in blob.get("results", {}).items():
        if not isinstance(arms, dict):
            continue
        for arm, conditions in arms.items():
            if not isinstance(conditions, dict):
                continue
            for condition, record in conditions.items():
                if isinstance(record, dict) and "margins" in record:
                    yield family, arm, condition, record


def test_every_cell_holds_exactly_the_declared_number_of_gold_pairs():
    blob = _gold()
    declared = blob.get("n_gold")
    assert declared, "gold_results.json declares no n_gold"

    cells = list(_cells(blob))
    assert cells, "no cells with margins in gold_results.json"

    wrong = [
        f"{family}/{arm}/{condition}: {len(record['margins'])} margins"
        for family, arm, condition, record in cells
        if len(record["margins"]) != declared
    ]
    assert not wrong, (
        f"n_gold is {declared} but these cells hold a different number of "
        f"margins: {wrong}. The declared count is what the paper's gold-pair "
        f"figure rests on."
    )


def test_the_mean_margin_is_the_mean_of_the_margins():
    blob = _gold()
    wrong = []
    for family, arm, condition, record in _cells(blob):
        margins = record["margins"]
        recomputed = sum(margins) / len(margins)
        stored = record.get("mean_margin")
        if stored is None or abs(recomputed - stored) > TOLERANCE:
            wrong.append(
                f"{family}/{arm}/{condition}: stored {stored}, "
                f"array gives {recomputed:.4f}"
            )
    assert not wrong, f"a mean_margin does not match its own array: {wrong}"


def test_accuracy_is_the_share_of_margins_above_zero():
    """The sign convention, checked rather than assumed.

    The harness records accuracy and margins separately. If accuracy is the
    fraction of pairs ordered correctly, and the margin's sign is fixed so that
    positive means correct, then accuracy must be the share of positive
    margins. The two agreeing is what lets the paper quote 0.98 and the margin
    drops as descriptions of the same thing.
    """
    blob = _gold()
    wrong = []
    for family, arm, condition, record in _cells(blob):
        margins = record["margins"]
        share = sum(1 for m in margins if m > 0) / len(margins)
        stored = record.get("accuracy")
        if stored is None or abs(share - stored) > TOLERANCE:
            wrong.append(
                f"{family}/{arm}/{condition}: accuracy {stored}, "
                f"share of positive margins {share:.4f}"
            )
    assert not wrong, (
        f"accuracy and margins disagree about which pairs were ordered "
        f"correctly: {wrong}. They are stored independently, so a disagreement "
        f"means the two columns describe different things."
    )


def test_the_sweep_that_skips_this_file_still_skips_for_the_reason_given():
    """Guard the reason this file exists.

    test_released_data_is_well_formed.py skips gold_results.json because it
    looks for `n_items`. If the gold file ever grows an `n_items` field, that
    sweep starts covering it and this file's first test becomes a duplicate --
    worth knowing rather than leaving two checks quietly overlapping.
    """
    blob = _gold()
    assert "n_items" not in blob, (
        "gold_results.json now declares n_items, so the general "
        "well-formedness sweep covers it and no longer skips. Reconcile the "
        "two checks rather than keeping both."
    )
    assert "n_gold" in blob, "gold_results.json no longer declares n_gold"
