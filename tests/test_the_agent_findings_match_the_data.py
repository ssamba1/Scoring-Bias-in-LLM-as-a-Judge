"""Are the findings the agent instructions call binding actually the data's?

.hermes.md has a section headed "Key Findings (must be correct in all outputs)"
and tells the reader they "are checked against the data by check_prose.py".
Every figure in it was -- every figure except one. "62,940 scored judgments"
appeared in no other document, was absent from macros.tex, and matched no count
of the released files. The main panel holds 19,500 per-item scores and the ten
raw files that record per-item scores hold 63,040 between them. Excluding the
nine unparsed sampled cells gives 63,031. Nothing gives 62,940.

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


def _count(blob):
    total = 0
    stack = [blob]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if key in SCORE_KEYS and isinstance(value, list):
                    total += len(value)
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


def test_the_main_panel_count_is_the_panel():
    per_file = _totals()
    scaled = per_file.get("results_scaled.json")
    if scaled is None:
        pytest.skip("[repro] results_scaled.json absent")
    assert f"{scaled:,}" in _hermes(), (
        f"the main panel holds {scaled:,} per-item scores; .hermes.md does not "
        f"say so, and it instructs whoever reads it to reproduce its numbers"
    )


def test_the_total_count_is_the_total():
    per_file = _totals()
    total = sum(per_file.values())
    assert f"{total:,}" in _hermes(), (
        f"the released raw files hold {total:,} per-item scores between them; "
        f".hermes.md states a different total"
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
