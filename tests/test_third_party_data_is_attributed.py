r"""Is third-party data attributed, and does the repo's licence cover what it ships?

The companion projects failed this: both shipped an MIT LICENSE presented as
covering everything while redistributing MT-Bench content, which is Apache 2.0
and requires the licence be passed on. That is a release-compliance defect,
never a wrong number, and it surfaces at artifact review rather than in any test
of the science.

This repository is in a better position and the check records why rather than
asserting it. The 50 evaluation items are author-written, inline in
repro/scaled_harness.py. The one external dataset, databricks-dolly-15k
(CC BY-SA 3.0), is loaded at run time by repro/dolly_harness.py and never
redistributed -- the committed results_dolly.json.gz holds scores and item
counts, no instruction or response text. So MIT covers what is actually
shipped.

What CC BY-SA still asks for is attribution, and the paper named the dataset
without naming its licence. That is what changed. The guards below fail if the
attribution goes away, or if item text starts being shipped -- at which point
the licence question stops being about attribution and starts being about
whether MIT can cover the release at all.
"""

import gzip
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
DOLLY_RESULTS = HONEST / "repro" / "results_dolly.json.gz"
DOLLY_HARNESS = HONEST / "repro" / "dolly_harness.py"
SOURCES = ("scoring_bias_v2.tex", "macros.tex")

# Field names that would carry redistributed source text.
TEXT_FIELDS = ("instruction", "response", "context", "prompt", "question", "answer_text")


def _paper():
    text = ""
    for name in SOURCES:
        path = HONEST / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace")
    if not text:
        pytest.skip("[paper] no LaTeX sources present")
    return " ".join(text.split())


def test_the_external_dataset_is_attributed_with_its_licence():
    paper = _paper()
    if "dolly" not in paper.lower():
        pytest.skip("[paper] the public-items replication is not described")
    assert "CC BY-SA" in paper, (
        "the paper uses databricks-dolly-15k but does not name its licence "
        "(CC BY-SA 3.0), which asks for attribution"
    )


def test_no_source_item_text_is_redistributed():
    """MIT covers this release only while no third-party text ships with it."""
    if not DOLLY_RESULTS.exists():
        pytest.skip("[data] results_dolly.json.gz not present")
    with gzip.open(DOLLY_RESULTS, "rt", encoding="utf-8", errors="replace") as handle:
        blob = json.dumps(json.load(handle))
    present = [f for f in TEXT_FIELDS if f'"{f}"' in blob]
    assert not present, (
        f"the released dolly results now carry {present}, i.e. source item text. "
        f"The repository's MIT LICENSE cannot cover redistributed CC BY-SA content "
        f"-- add the licence and attribution alongside the data before shipping it."
    )


def test_the_harness_records_where_the_items_came_from():
    """Provenance has to live with the code that fetches, not only in the paper."""
    if not DOLLY_HARNESS.exists():
        pytest.skip("[repro] dolly_harness.py not present")
    text = DOLLY_HARNESS.read_text(encoding="utf-8", errors="replace")
    assert "databricks-dolly-15k" in text, "the harness no longer names its dataset"
    assert "CC BY-SA" in text, "the harness no longer records the dataset's licence"


def test_the_check_is_reading_a_real_result_file():
    """Vacuity guard: an unreadable archive would make the text check pass empty."""
    if not DOLLY_RESULTS.exists():
        pytest.skip("[data] results_dolly.json.gz not present")
    with gzip.open(DOLLY_RESULTS, "rt", encoding="utf-8", errors="replace") as handle:
        data = json.load(handle)
    assert data.get("n_items"), "no item count in the released dolly results"
    assert data.get("results"), "no per-family results in the released dolly results"
