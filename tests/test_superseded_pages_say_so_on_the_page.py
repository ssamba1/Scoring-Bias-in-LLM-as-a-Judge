"""A superseded results page must carry its own warning.

`results_rootcause/README.md` is clear that this directory is a superseded
pilot, that its conclusion was overturned, and that the direction in its outputs
should not be cited. But `publication/figures_study1.html` is a standalone page
a reader opens directly, and it carried none of that: it presented "Key finding:
format bias down, content bias up", marked rows "IMPROVED", and reported
"instruct models less biased on average" -- the overturned direction, stated as
a finding, with the correction living one directory up in a file nobody opening
the figures would read.

This is the same shape as `paper/interactive/base_vs_instruct.html`, which does
carry its own header saying the direction did not survive. The context has to be
on the artefact, because the artefact is what gets opened, linked and screenshot.

`test_no_document_states_the_overturned_direction.py` does scan this directory,
and did not catch it: its patterns are phrasings of the claim, and this page
says the same thing in different words ("less biased on average", "IMPROVED",
"format robustness improves"). Rather than widen those patterns -- which would
start flagging the README warnings that exist to say the direction is wrong --
this requires the page to carry a warning of its own.
"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PAGES = [
    REPO / "results_rootcause" / "publication" / "figures_study1.html",
    REPO / "paper" / "interactive" / "base_vs_instruct.html",
]

# One of these has to appear for the page to count as self-describing.
WARNINGS = ("did not survive", "superseded", "not as a finding", "not as the finding")


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_the_page_says_its_direction_was_overturned(page):
    if not page.exists():
        pytest.skip(f"[pages] {page.name} not present")
    text = " ".join(page.read_text(encoding="utf-8", errors="replace").split())

    assert any(w in text.lower() for w in WARNINGS), (
        f"{page.name} reports the superseded direction and says nothing about "
        f"it on the page. The correction cannot live only in a README one "
        f"directory up: this file is what a reader opens."
    )


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_the_warning_names_what_replaced_it(page):
    """A warning that does not point anywhere leaves the reader stuck."""
    if not page.exists():
        pytest.skip(f"[pages] {page.name} not present")
    text = " ".join(page.read_text(encoding="utf-8", errors="replace").split())
    assert "13-family" in text or "13 famil" in text, (
        f"{page.name} warns that its direction was overturned but does not name "
        f"the panel that overturned it, so a reader cannot find what to trust "
        f"instead."
    )
