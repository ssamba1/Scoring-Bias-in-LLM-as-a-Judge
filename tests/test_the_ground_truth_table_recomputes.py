"""Does the ground-truth table recompute from the runs behind it?

Section "bias corrupts real judgments" is the paper's answer to the obvious
objection -- that a shifting score might be harmless if the ranking survives.
Its table carries three quantities per condition and arm: the margin drop, the
accuracy drop, and the accuracy under bias. The headline sentences come straight
off it ("rubric reversal collapses accuracy to chance for both, 0.02 base and
0.00 instruct") and so does P6's split verdict.

results_gold.json is derived from gold_results.json, and nothing recomputed one
from the other. The derived file is what the paper quotes, the prose gate checks
the paper against the derived file, and the derived file regenerates by rerunning
the script that wrote it -- the same closed loop the other headline statistics
were in.

Recomputed here per family and averaged, which is the aggregation the analyzer
documents. All eighteen cells agree exactly. The margin drops in particular are
what P6's failed second clause rests on -- instruct loses more margin than base,
2.43 against 1.33 under reversal -- so they are worth being able to derive rather
than trust.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONDITIONS = ("reversed", "novice", "verbose")
ARMS = ("base", "instruct")
TOLERANCE = 0.0006


def _runs():
    path = REPRO / "gold_results.json"
    if not path.exists():
        pytest.skip("[repro] gold_results.json not present")
    results = json.loads(path.read_text())["results"]
    families = [
        name for name, record in results.items()
        if isinstance(record, dict) and all(arm in record for arm in ARMS)
    ]
    if not families:
        pytest.skip("[repro] no family carries both arms")
    return results, sorted(families)


def _derived():
    path = REPRO / "results_gold.json"
    if not path.exists():
        pytest.skip("[repro] results_gold.json not present")
    return json.loads(path.read_text())


def _mean(values):
    return sum(values) / len(values)


def test_the_control_row_recomputes():
    results, families = _runs()
    control = _derived()["control"]
    for arm in ARMS:
        accuracy = _mean([results[f][arm]["control"]["accuracy"] for f in families])
        margin = _mean([results[f][arm]["control"]["mean_margin"] for f in families])
        assert abs(accuracy - control[arm]["mean_accuracy"]) <= TOLERANCE, (
            f"{arm} control accuracy: stored {control[arm]['mean_accuracy']}, "
            f"recomputed {accuracy:.4f}"
        )
        assert abs(margin - control[arm]["mean_margin"]) <= TOLERANCE, (
            f"{arm} control margin: stored {control[arm]['mean_margin']}, "
            f"recomputed {margin:.4f}"
        )


@pytest.mark.parametrize("condition", CONDITIONS)
def test_every_degradation_cell_recomputes(condition):
    results, families = _runs()
    row = _derived()["degradation"].get(condition)
    if not isinstance(row, dict):
        pytest.skip(f"[repro] no {condition} row")

    wrong = []
    for arm in ARMS:
        stored = row[arm]
        margin_drop = _mean([
            results[f][arm]["control"]["mean_margin"] - results[f][arm][condition]["mean_margin"]
            for f in families
        ])
        accuracy_drop = _mean([
            results[f][arm]["control"]["accuracy"] - results[f][arm][condition]["accuracy"]
            for f in families
        ])
        under_bias = _mean([results[f][arm][condition]["accuracy"] for f in families])

        for label, mine, theirs in (
            ("margin_drop", margin_drop, stored["margin_drop"]),
            ("accuracy_drop", accuracy_drop, stored["accuracy_drop"]),
            ("accuracy_under_bias", under_bias, stored["accuracy_under_bias"]),
        ):
            if abs(mine - theirs) > TOLERANCE:
                wrong.append(f"{condition}/{arm}/{label}: stored {theirs}, recomputed {mine:.4f}")

    assert not wrong, f"the ground-truth table does not match its runs: {wrong}"


def test_accuracy_under_bias_and_its_drop_are_consistent():
    """Two of the three columns determine the third, given the control row."""
    derived = _derived()
    control = derived["control"]
    wrong = []
    for condition in CONDITIONS:
        row = derived["degradation"].get(condition)
        if not isinstance(row, dict):
            continue
        for arm in ARMS:
            expected = control[arm]["mean_accuracy"] - row[arm]["accuracy_drop"]
            if abs(expected - row[arm]["accuracy_under_bias"]) > 0.0015:
                wrong.append(
                    f"{condition}/{arm}: control {control[arm]['mean_accuracy']} minus "
                    f"drop {row[arm]['accuracy_drop']} is {expected:.4f}, but the "
                    f"table says accuracy under bias is {row[arm]['accuracy_under_bias']}"
                )
    assert not wrong, f"the table disagrees with itself: {wrong}"
