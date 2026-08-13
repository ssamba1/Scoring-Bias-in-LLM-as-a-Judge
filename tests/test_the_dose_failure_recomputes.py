"""Do the dose-response summaries follow from the cells they summarise?

P14 predicted that bias would scale with the magnitude of the nuisance and that
instruct slopes would be steeper. Both clauses failed, and the paper reports the
failure: the mean dose-rank correlation is 0.06 with 8 of 16 cells positive, and
instruct slopes are steeper in only 3 of 8 pairs.

A reported failure needs guarding as much as a reported success -- arguably
more, because nobody re-derives a number that already says the prediction did
not work. Drift in either direction is invisible: a summary that quietly became
9/16 would still read as a failure, and one that became 14/16 would turn a
failed preregistration into a confirmed one with no other number moving.

check_prose pins the strings "8/16" and "3/8" as they appear in the paper. That
catches the paper drifting from the release. It cannot catch the release
disagreeing with its own sixteen cells, which is what this does.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _analysis():
    path = REPRO / "results_dose_analysis.json"
    if not path.exists():
        pytest.skip("[repro] dose analysis not present")
    blob = json.loads(path.read_text())
    if not blob.get("per_cell"):
        pytest.skip("[repro] no per-cell dose records")
    return blob


def test_the_monotonicity_summary_recomputes_from_the_cells():
    blob = _analysis()
    cells = blob["per_cell"]
    stored = blob.get("P14a_monotonic")
    if not isinstance(stored, dict):
        pytest.skip("[repro] no P14a summary")

    rhos = [cell["dose_spearman"] for cell in cells]
    assert len(rhos) == stored["n_cells"], (
        f"the summary counts {stored['n_cells']} cells; the file holds {len(rhos)}"
    )
    mean = sum(rhos) / len(rhos)
    assert abs(mean - stored["mean_dose_spearman"]) <= 0.0015, (
        f"the release stores a mean dose correlation of "
        f"{stored['mean_dose_spearman']}; its cells give {mean:.4f}"
    )
    positive = sum(1 for rho in rhos if rho > 0) / len(rhos)
    assert abs(positive - stored["frac_positive"]) <= 0.001, (
        f"the release stores {stored['frac_positive']} of cells positive; its "
        f"cells give {positive:.4f}"
    )


def test_the_slope_summary_recomputes_from_the_pairs():
    blob = _analysis()
    stored = blob.get("P14b_slope")
    if not isinstance(stored, dict):
        pytest.skip("[repro] no P14b summary")

    slopes = {
        (cell["family"], cell["probe"], cell["kind"]): cell["slope"]
        for cell in blob["per_cell"]
    }
    pairs = [
        (base, slopes[(family, probe, "instruct")])
        for (family, probe, kind), base in slopes.items()
        if kind == "base" and (family, probe, "instruct") in slopes
    ]
    assert len(pairs) == stored["n_pairs"], (
        f"the summary counts {stored['n_pairs']} base/instruct pairs; the cells "
        f"form {len(pairs)}"
    )

    steeper = sum(1 for base, instruct in pairs if instruct > base)
    assert f"{steeper}/{len(pairs)}" == stored["instruct_steeper"], (
        f"the release stores {stored['instruct_steeper']} pairs with a steeper "
        f"instruct slope; its cells give {steeper}/{len(pairs)}"
    )

    for label, values, key in (
        ("base", [b for b, _ in pairs], "mean_base_slope"),
        ("instruct", [i for _, i in pairs], "mean_instruct_slope"),
    ):
        mine = sum(values) / len(values)
        assert abs(mine - stored[key]) <= 0.0015, (
            f"the release stores a mean {label} slope of {stored[key]}; its "
            f"cells give {mine:.4f}"
        )


def test_both_clauses_are_still_failures():
    """The paper reports P14 as failed on both clauses. It has to stay failed."""
    blob = _analysis()
    monotonic, slope = blob.get("P14a_monotonic"), blob.get("P14b_slope")
    if not (isinstance(monotonic, dict) and isinstance(slope, dict)):
        pytest.skip("[repro] the P14 summaries are not both present")

    assert monotonic["mean_dose_spearman"] < 0.2, (
        f"the mean dose correlation is now {monotonic['mean_dose_spearman']}; "
        f"the paper reports this clause as failed"
    )
    steeper, total = (int(part) for part in slope["instruct_steeper"].split("/"))
    assert steeper <= total / 2, (
        f"instruct slopes are now steeper in {slope['instruct_steeper']} pairs; "
        f"the paper reports that clause as failed too"
    )
