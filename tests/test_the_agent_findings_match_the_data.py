"""Are the findings the agent instructions call binding actually the data's?

.hermes.md has a section headed "Key Findings (must be correct in all outputs)"
and tells the reader they "are checked against the data by check_prose.py".
Every figure in it was -- every figure except one. "62,940 scored judgments"
appeared in no other document, was absent from macros.tex, and matched no count
of the released files. The main panel holds 19,500 per-item scores, and the
eleven raw files that record per-item scores hold 64,531 between them.

That total is the number of scores actually recorded, which is neither of the
two figures this repository was computing. Nine sampled cells failed to parse
and are stored as `null`, in five arrays of twenty. Counting every slot gives
64,540 and credits the study with nine judgments it never made; discarding each
array that contains a null gives 64,440 and throws away the 91 scores that did
come back. Two guards had drifted onto opposite sides of that hundred, and
`_scored` below is now the single rule both use.

A wrong number in that section is worse than a wrong number in the paper,
because the section instructs whoever reads it to reproduce it downstream.
Nothing was checking it, and the sentence claiming it was checked is what made
that easy to miss.

The counts here are recomputed rather than pinned, so the section moves when
the data moves. The other figures in it are already gate-asserted through
macros.tex; this covers the one that was not.
"""

import gzip
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
HERMES = REPO / ".hermes.md"

# The vectors that hold one recorded score per item. per_item_argmax and
# per_item_entropy are derived from the same judgments, so counting them would
# treble the total.
SCORE_KEYS = {"per_item", "ev_per_item", "sampled_per_item"}


def _load(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _scored(value):
    """Entries in a score vector that hold a score.

    A `null` is a recorded parse failure: the harness tried and got nothing
    back. Counting it inflates the study by cells that were never scored, and
    discarding the whole array around it throws away the ones that were. Nine
    nulls sit in five arrays of twenty, so the two mistakes differ by a hundred
    -- which is exactly how far the two counters in this repository drifted
    apart before both were pointed at this function's rule.
    """
    if not value:
        return 0
    for entry in value:
        if entry is None:
            continue
        if not isinstance(entry, (int, float)) or isinstance(entry, bool):
            return 0  # not a score vector at all
    return sum(1 for entry in value if entry is not None)


def _count(blob):
    total = 0
    stack = [blob]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if key in SCORE_KEYS and isinstance(value, list):
                    total += _scored(value)
                else:
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)
    return total


def _totals():
    if not REPRO.exists():
        pytest.skip("[repro] not present")
    per_file = {}
    for path in sorted(REPRO.glob("*.json")) + sorted(REPRO.glob("*.json.gz")):
        if path.name.endswith("_analysis.json"):
            continue
        try:
            count = _count(_load(path))
        except (json.JSONDecodeError, OSError):
            continue
        if count:
            per_file[path.name] = count
    if not per_file:
        pytest.skip("[repro] no per-item score vectors found")
    return per_file


def _hermes():
    if not HERMES.exists():
        pytest.skip("[repo] .hermes.md not present")
    return HERMES.read_text(encoding="utf-8", errors="replace")


def _claimed(pattern, label):
    """The number the brief states *as* a given claim, not merely somewhere.

    Both checks below used to ask whether the correct figure appeared anywhere
    in the file. That is satisfiable by prose that is not the claim: when the
    corrected total was explained in a note beneath the bullet, the file
    mentioned it twice, so deleting the live one left the check green. The
    registered mutation on this very line stopped being caught, and only the
    hour-long mutation pass noticed. A guard on a number has to name where the
    number is supposed to be.
    """
    import re

    found = re.search(pattern, _hermes())
    assert found, (
        f"the brief no longer states {label} in the form this guard reads. "
        f"Re-anchor it deliberately rather than leaving the claim unchecked."
    )
    return int(found.group(1).replace(",", ""))


def test_the_main_panel_count_is_the_panel():
    per_file = _totals()
    scaled = per_file.get("results_scaled.json")
    if scaled is None:
        pytest.skip("[repro] results_scaled.json absent")
    stated = _claimed(r"([\d,]+)\s+per-item scores in the main panel",
                      "the main-panel count")
    assert stated == scaled, (
        f"the brief says the main panel holds {stated:,} per-item scores; "
        f"results_scaled.json holds {scaled:,}"
    )


def test_the_total_count_is_the_total():
    per_file = _totals()
    total = sum(per_file.values())
    stated = _claimed(r"([\d,]+)\s+across the\s+\w+\s+released raw files",
                      "the total across the raw files")
    assert stated == total, (
        f"the brief says {stated:,} scored judgments across the raw files; the "
        f"released data holds {total:,}. Per file: {per_file}"
    )


def test_the_file_count_is_the_file_count():
    """The count of files was never checked, and was wrong for weeks.

    Ten is what you get by looking for the literal `per_item` key;
    results_sampled.json stores `ev_per_item` and `sampled_per_item`, so the
    narrow reading misses it. The same narrowing has been corrected in two
    per-item detectors already.
    """
    per_file = _totals()
    words = {9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen"}
    expected = words.get(len(per_file))
    assert expected, (
        f"{len(per_file)} raw files carry score vectors; extend this word list"
    )
    assert f"{expected} released raw files" in _hermes(), (
        f"{len(per_file)} released raw files carry per-item score vectors "
        f"({sorted(per_file)}); .hermes.md does not say {expected}"
    )


def test_no_uncountable_total_survives():
    """The specific wrong number, and any restatement of it."""
    hermes = _hermes()
    per_file = _totals()
    countable = {
        f"{sum(per_file.values()):,}",
        f"{per_file.get('results_scaled.json', 0):,}",
    }
    stated = set(re.findall(r"\b\d{2},\d{3}\b", hermes))
    # A number may appear while being described as wrong, which is what the
    # corrected line does. Only counts offered as the study's size matter.
    offered = {
        n for n in stated
        if n not in countable and not re.search(
            rf'"{re.escape(n)}[^"]*"|{re.escape(n)}[^.\n]{{0,60}}until 2026', hermes
        )
    }
    assert not offered, (
        f".hermes.md states {sorted(offered)} as a count of the study, and no "
        f"count of the released files produces it. The releases hold "
        f"{sorted(countable)}."
    )
