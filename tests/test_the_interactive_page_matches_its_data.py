"""Do the numbers on the published dashboard come from a data file?

`paper/interactive/base_vs_instruct.html` hardcodes 42 bias values -- seven
families, base and instruct, three probes -- as a JavaScript literal. It is
served as a supplementary page, so those numbers are published, and nothing
compared them to anything. Hand-copied values in a published artifact that no
check reads is the precise shape of what this project retracted.

They are correct: every one recomputes from `results_rootcause/t4fam_results.json`
as the spread between that probe's variants, which is the paper's definition of
the bias measure.

Two things this deliberately does not do. It does not require the page to exist
-- it is supplementary, and deleting it should not fail the suite. And it does
not check the page's framing, which is handled elsewhere: the surviving
dashboard says plainly that the direction on this 7-family slice did not survive
the 13-family panel, and `test_superseded_claims_are_not_asserted.py` is what
keeps that sentence honest.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "paper" / "interactive" / "base_vs_instruct.html"
DATA = REPO / "results_rootcause" / "t4fam_results.json"

# The stored means carry one decimal, so a spread of two of them can be off by
# 0.1 only through arithmetic that is wrong, not through rounding.
TOLERANCE = 0.051


def _shown():
    if not PAGE.exists():
        pytest.skip("[interactive] the dashboard is not present")
    html = PAGE.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"const DELTAS = \{(.*?)\n\};", html, re.S)
    if not block:
        pytest.skip("[interactive] the page no longer carries a DELTAS literal")
    values = {}
    for match in re.finditer(
        r'"([\w.\-]+)":\s*\{rubric_order:([\d.]+),\s*score_id:([\d.]+),'
        r'\s*reference_answer:([\d.]+)\}', block.group(1)
    ):
        values[match.group(1)] = {
            "rubric_order": float(match.group(2)),
            "score_id": float(match.group(3)),
            "reference_answer": float(match.group(4)),
        }
    return values


def _data():
    if not DATA.exists():
        pytest.skip("[repro] t4fam_results.json is not present")
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_every_published_value_recomputes_from_the_run():
    shown, data = _shown(), _data()
    wrong = []
    for name, probes in sorted(shown.items()):
        record = data.get(name)
        if record is None:
            wrong.append(f"{name}: the page shows a model absent from the run")
            continue
        for probe, value in sorted(probes.items()):
            variants = record.get(probe)
            if not isinstance(variants, dict):
                wrong.append(f"{name}/{probe}: the page shows a probe absent from the run")
                continue
            spread = max(variants.values()) - min(variants.values())
            if abs(spread - value) > TOLERANCE:
                wrong.append(f"{name}/{probe}: page {value}, run {spread:.2f}")
    assert not wrong, (
        f"the published dashboard shows values that are not in the run it "
        f"claims to display: {wrong}"
    )


def test_the_page_shows_the_whole_run():
    """A page showing four of seven families would pass the check above."""
    shown = _shown()
    assert len(shown) * 3 == 42, (
        f"the page publishes {len(shown) * 3} values, not the 42 of the "
        f"seven-family run; update this count deliberately if the page changed"
    )


def test_the_comparison_is_not_vacuous():
    """If the literal stopped parsing, every check above would pass on nothing."""
    shown = _shown()
    assert shown, "no values parsed from the page's DELTAS literal"
    data = _data()
    assert set(shown) <= set(data), (
        f"the page names models the run does not: {sorted(set(shown) - set(data))}"
    )
