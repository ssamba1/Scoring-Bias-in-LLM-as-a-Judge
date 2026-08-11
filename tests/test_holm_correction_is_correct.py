"""Is the multiple-comparison correction in the summary table actually Holm?

The table's last-but-one column is the only place the paper controls for testing
five probes at once, and it is what a reader checks before believing any single
probe's p-value. Until now nothing verified it: the pipeline computed the
adjustment and the pipeline's output was compared against itself.

This recomputes the correction from the raw Wilcoxon p-values with an
independent implementation and requires the table to match. Holm is a step-down
procedure, and the two places it goes wrong are exactly the two this checks:

  * the multiplier must be (m - i) for the i-th smallest p, not m for all of
    them (that is Bonferroni, which is more conservative and a different claim)
  * the adjusted values must be made monotone non-decreasing down the sorted
    order, otherwise a later p can come out smaller than an earlier one and the
    procedure loses its error guarantee

Ties matter here: score ID and authority have identical raw p (0.0266), and a
correction that mishandles ties would separate them.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
PERITEM = HONEST / "repro" / "results_peritem.json"
TABLE = HONEST / "tables" / "tab_v2_summary.tex"

# The printed column carries four significant figures at most; the table rounds
# to three decimals, so allow just over half a unit in the last place.
TOL = 0.0006


def _summary():
    if not PERITEM.exists():
        pytest.skip("[peritem] results_peritem.json not present")
    return json.loads(PERITEM.read_text(encoding="utf-8", errors="replace"))["summary"]


def _holm(raw):
    """Holm step-down adjusted p-values. Independent of the analysis code."""
    m = len(raw)
    adjusted, running = {}, 0.0
    for i, probe in enumerate(sorted(raw, key=lambda p: raw[p])):
        running = max(running, (m - i) * raw[probe])
        adjusted[probe] = min(1.0, running)
    return adjusted


def _table_column():
    """probe label -> the p_Holm value the table prints."""
    if not TABLE.exists():
        pytest.skip("[table] tab_v2_summary.tex not present")
    printed = {}
    for line in TABLE.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = [c.strip() for c in line.split("&")]
        if len(cells) < 7 or not re.match(r"^[A-Z]", cells[0]):
            continue
        try:
            printed[cells[0].lower().replace(" ", "_")] = float(cells[6])
        except ValueError:
            continue
    return printed


def test_the_table_prints_holm_adjusted_values():
    summary = _summary()
    raw = {p: summary[p]["wilcoxon_p"] for p in summary}
    expected = _holm(raw)
    printed = _table_column()
    assert printed, "no p-value column parsed from tab_v2_summary.tex"

    wrong = []
    for probe, value in expected.items():
        if probe not in printed:
            wrong.append(f"{probe}: absent from the table")
        elif abs(printed[probe] - value) > TOL:
            wrong.append(f"{probe}: table {printed[probe]}, Holm gives {value:.4f}")
    assert not wrong, f"the p_Holm column is not Holm-adjusted: {wrong}"


def test_the_correction_is_not_bonferroni():
    """Every value equal to m*p would mean the column is Bonferroni, not Holm.

    Bonferroni is uniformly more conservative, so mislabelling it as Holm
    understates the evidence while claiming a different procedure. It passes the
    test above only for the single smallest p, where the two coincide.
    """
    summary = _summary()
    raw = {p: summary[p]["wilcoxon_p"] for p in summary}
    m = len(raw)
    bonferroni = {p: min(1.0, m * v) for p, v in raw.items()}
    holm = _holm(raw)
    differing = [p for p in raw if abs(bonferroni[p] - holm[p]) > TOL]
    assert differing, (
        "Holm and Bonferroni agree on every probe here, so this test cannot "
        "distinguish them and gives no assurance -- rewrite it against data "
        "where they differ"
    )
    printed = _table_column()
    matches_bonferroni = [
        p for p in differing if p in printed and abs(printed[p] - bonferroni[p]) <= TOL
    ]
    assert not matches_bonferroni, (
        f"the table's value for {matches_bonferroni} equals the Bonferroni "
        f"adjustment, not the Holm one the header claims"
    )


def test_adjusted_values_are_monotone():
    """Holm output must not decrease as the raw p-values increase."""
    summary = _summary()
    raw = {p: summary[p]["wilcoxon_p"] for p in summary}
    printed = _table_column()
    ordered = [p for p in sorted(raw, key=lambda x: raw[x]) if p in printed]
    values = [printed[p] for p in ordered]
    assert values == sorted(values), (
        f"the p_Holm column is not monotone in the raw p-values: "
        f"{list(zip(ordered, values))}"
    )


def test_the_parser_finds_every_probe():
    """Vacuity guard: a table reformat must not silently empty the comparison."""
    summary = _summary()
    printed = _table_column()
    missing = sorted(set(summary) - set(printed))
    assert not missing, (
        f"{missing} were not parsed out of the table; the column layout changed "
        f"and the checks above are comparing fewer rows than they appear to"
    )
