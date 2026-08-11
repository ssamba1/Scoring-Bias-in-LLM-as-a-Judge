r"""Every cell of the paper's main table, pinned to the value it came from.

The reproduction gate already diffs the whole tables/ directory against a fresh
run, which catches drift -- but only in the job that installs the full analysis
stack, and only as one all-or-nothing comparison that says "tables/ differs"
without saying which number. These cases run in the integrity job, which
installs nothing but pytest, and each names the family, probe and arm whose cell
stopped matching its source.

The table is the densest set of claims in the paper: 13 families x 5 probes x 2
arms, each rounded to one decimal from a value in results_peritem.json, plus the
size and training columns. Every one is generated at collection time from the
JSON rather than typed here, so this cannot drift into a second copy of the
data -- the failure mode of writing expected values into a test by hand.

Rounding is compared the way the generator does it, and the tolerance is exact:
a cell is either the correctly rounded value or it is wrong. Values landing on a
rounding tie are the one exception, and they are compared against both
neighbours, because which way Python rounds .05 at one decimal depends on the
binary representation -- the same fragility that turned CI red once already
(see test_analysis_stack_matches_the_pins.py).
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
TABLE = HONEST / "tables" / "tab_v2_family.tex"
SOURCE = HONEST / "repro" / "results_peritem.json"

# Table column order, after Family / B / Train.
PROBES = ["rubric_order", "score_id", "reference_answer", "authority", "verbosity"]
ARMS = [("b", "base_delta"), ("i", "instruct_delta")]


def _rows():
    """(family, params, training, [12 numeric cells]) per body row of the table."""
    if not TABLE.exists():
        return []
    rows = []
    for line in TABLE.read_text(encoding="utf-8", errors="replace").splitlines():
        if "&" not in line or line.lstrip().startswith(("%", "\\multirow", "\\multicolumn")):
            continue
        cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
        if len(cells) != 3 + 2 * len(PROBES):
            continue
        if not re.match(r"^[A-Za-z]", cells[0]):
            continue
        rows.append((cells[0], cells[1], cells[2], cells[3:]))
    return rows


def _source():
    if not SOURCE.exists():
        return {}
    return json.loads(SOURCE.read_text(encoding="utf-8", errors="replace")).get("per_family", {})


def _cases():
    """One case per numeric cell: (family, probe, arm-label, printed, expected)."""
    data = _source()
    out = []
    for family, _params, _train, cells in _rows():
        record = data.get(family)
        if not record:
            continue
        for probe_index, probe in enumerate(PROBES):
            for arm_index, (arm_label, key) in enumerate(ARMS):
                printed = cells[probe_index * 2 + arm_index]
                value = record.get(probe, {}).get(key)
                if value is None:
                    continue
                out.append(
                    pytest.param(
                        family, probe, arm_label, printed, value,
                        id=f"{family}-{probe}-{arm_label}",
                    )
                )
    return out


CASES = _cases()


@pytest.mark.skipif(not CASES, reason="[table] tab_v2_family.tex or its source is absent")
@pytest.mark.parametrize("family,probe,arm,printed,value", CASES)
def test_table_cell_matches_its_source(family, probe, arm, printed, value):
    expected = round(value, 1)
    # A value sitting exactly on a rounding tie may print either neighbour
    # depending on its binary representation; both are correct roundings.
    on_tie = abs(round(value * 100) % 10) == 5
    allowed = {f"{expected:.1f}"}
    if on_tie:
        allowed |= {f"{expected - 0.1:.1f}", f"{expected + 0.1:.1f}"}
    assert printed in allowed, (
        f"{family} / {probe} / {arm}: the table prints {printed}, but "
        f"results_peritem.json holds {value} (rounds to {expected:.1f})"
    )


def _metadata_cases():
    data = _source()
    out = []
    for family, params, training, _cells in _rows():
        record = data.get(family)
        if record:
            out.append(pytest.param(family, params, training, record, id=family))
    return out


METADATA = _metadata_cases()


@pytest.mark.skipif(not METADATA, reason="[table] tab_v2_family.tex or its source is absent")
@pytest.mark.parametrize("family,params,training,record", METADATA)
def test_table_metadata_matches_its_source(family, params, training, record):
    assert float(params) == float(record["params_b"]), (
        f"{family}: the table says {params}B, the data says {record['params_b']}B"
    )
    assert training == record["training"], (
        f"{family}: the table says {training!r}, the data says {record['training']!r}"
    )


def test_the_table_is_actually_being_read():
    """Vacuity guard: a parse that returns nothing makes every case above vanish."""
    rows = _rows()
    assert len(rows) == 13, f"parsed {len(rows)} body rows from tab_v2_family.tex, expected 13"
    assert len(CASES) == 130, f"generated {len(CASES)} cell cases, expected 130 (13 x 5 x 2)"


def test_every_family_in_the_data_appears_in_the_table():
    """A family dropped from the table would otherwise just reduce the case count."""
    data = _source()
    if not data:
        pytest.skip("[source] results_peritem.json not present")
    printed = {family for family, _, _, _ in _rows()}
    missing = sorted(set(data) - printed)
    assert not missing, f"families in the data but absent from the table: {missing}"
