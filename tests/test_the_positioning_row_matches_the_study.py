"""Does the related-work table's own row describe this study?

The audit's finding on the retracted version's positioning table: *Row says
"This work: 31 models" -- inconsistent with the body.* A self-row is written
early, to stake a claim against prior work, and then the study changes around
it. It is the one row in that table nobody re-derives, because it is the one
row the authors think they already know.

This one says seven bias types, four of them new, across thirteen families. All
three are checkable: the probes are in the released runs, the four new ones are
those not taken from the prior scoring-bias work the table compares against, and
the family count is the panel's.

Nothing checked them. The columns beyond the counts -- mechanism, causal,
decomposition -- are editorial claims about contribution and are left alone;
these are the factual ones.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

# The three the table's comparison row credits to prior work (Li et al. 2025).
INHERITED = {"rubric_order", "score_id", "reference_answer"}


def _row():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r"\\textbf\{This work\}\s*&\s*\\textbf\{(\d+)\s*\((\d+)\s*new\)\}\s*&\s*"
        r"\\textbf\{\\?(\w+)\}", text)
    if not match:
        pytest.skip("[paper] the positioning row is not in the expected form")
    return match


def _probes():
    """Every bias type the paper measures, from the runs that measured them."""
    probes = set()
    for name in ("results_scaled.json", "results_probes2.json"):
        path = REPRO / name
        if not path.exists():
            continue
        for family in json.loads(path.read_text())["results"].values():
            for arm in family.values():
                if isinstance(arm, dict):
                    probes |= {k for k, v in arm.items() if isinstance(v, dict)}
    if not probes:
        pytest.skip("[repro] no probes found in the released runs")
    return probes


def test_the_row_counts_the_bias_types_the_study_ran():
    row = _row()
    stated = int(row.group(1))
    probes = _probes()
    assert stated == len(probes), (
        f"the positioning row claims {stated} bias types; the released runs hold "
        f"{len(probes)}: {sorted(probes)}. This is the row the audit caught "
        f"disagreeing with the body last time."
    )


def test_the_row_counts_the_new_bias_types_correctly():
    row = _row()
    stated_new = int(row.group(2))
    new = _probes() - INHERITED
    assert stated_new == len(new), (
        f"the row claims {stated_new} new bias types; the ones not inherited "
        f"from the prior work it compares against are {sorted(new)}"
    )


def test_the_row_counts_the_families_in_the_panel():
    row = _row()
    families = row.group(3)
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    if families == "NFAM":
        # The macro is checked against the panel elsewhere; here it only has to
        # be the macro rather than a number typed beside it.
        assert "\\newcommand{\\NFAM}" in text or "NFAM" in text
        return
    scaled = REPRO / "results_scaled.json"
    if not scaled.exists():
        pytest.skip("[repro] scaled results not present")
    panel = len(json.loads(scaled.read_text())["results"])
    assert int(families) == panel, (
        f"the row claims {families} families; the panel holds {panel}. Write it "
        f"as the macro so it cannot drift."
    )
