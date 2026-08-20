"""Does the DOI the paper points at hold the paper the reader is reading?

The paper states, present tense, that "the repository snapshot, paper, and all
raw data are archived at DOI 10.5281/zenodo.21499823". That is a claim about an
external artifact, and it is the same shape as two the playbook already records:
"we release code and data" while the repositories were private, and the tracked
tarball that kept the pre-correction text while the manuscript moved on.

It is currently false in the direction that matters. The record is v2.1.0,
published 2026-07-22; its PDF was downloaded and inspected on 2026-08-20 and
carries d_z=1.44, 24/26, 75% sign accuracy, responsiveness 0.14->0.26 and
rho=+0.64 -- every figure the score-ordering correction changed. A referee who
follows the DOI to check a number finds the wrong one, in a paper whose previous
version was retracted.

Minting a new deposit is the author's action, not something a test can do, so
this does not try to verify the archive over the network: a test that needs the
internet fails offline and in CI for reasons unrelated to the paper. What it can
do is refuse to let the discrepancy be forgotten -- the checklist must carry the
item, unticked, naming the DOI, for as long as the paper cites that version.

The escape hatch is deliberate. Point the paper at the concept DOI, which always
resolves to the newest version, or cite a freshly minted version DOI, and this
stops applying on its own.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"
CHECKLIST = REPO / "paper" / "submission_checklist.md"

# The deposit that predates the score-ordering correction.
STALE_VERSION_DOI = "10.5281/zenodo.21499823"
CONCEPT_DOI = "10.5281/zenodo.21499822"


def _read(path, label):
    if not path.exists():
        pytest.skip(f"[{label}] {path.name} not present")
    return path.read_text(encoding="utf-8", errors="replace")


def test_the_stale_deposit_is_flagged_while_the_paper_cites_it():
    paper = _read(PAPER, "paper")
    if STALE_VERSION_DOI not in paper:
        # Re-minted, or switched to the concept DOI. Either resolves this.
        return

    checklist = _read(CHECKLIST, "checklist")
    flat = " ".join(checklist.split())

    assert STALE_VERSION_DOI in checklist, (
        f"the paper claims its snapshot is archived at {STALE_VERSION_DOI}, and "
        f"that deposit predates the corrected numbers, but the submission "
        f"checklist does not name it. The one place a reader is told the archive "
        f"is stale is the place that has to say so."
    )

    item = re.search(
        r"-\s*\[(?P<box>[ xX])\][^\n]*Zenodo DOI", checklist)
    assert item, "the checklist no longer carries a Zenodo DOI item at all"
    assert item.group("box") == " ", (
        "the Zenodo item is ticked while the paper still cites the deposit that "
        "carries the superseded numbers. Ticking it does not mint anything; if a "
        "new version exists, update the DOI in the paper and this check retires "
        "itself."
    )
    assert CONCEPT_DOI in flat, (
        "the checklist should record the concept DOI as the self-healing "
        "alternative, so the fix is not only 'remember to re-mint'"
    )


def test_the_claim_is_present_tense_and_therefore_checkable():
    """Vacuity guard: if the sentence goes, the check above stops meaning anything."""
    paper = _read(PAPER, "paper")
    if STALE_VERSION_DOI not in paper:
        pytest.skip("[paper] no longer cites the stale deposit")
    flat = " ".join(paper.split())
    assert re.search(r"are archived at", flat), (
        "the paper no longer states that the snapshot IS archived at the cited "
        "DOI. If that was softened deliberately, this guard should be retired "
        "with it rather than left asserting a sentence that is gone."
    )
