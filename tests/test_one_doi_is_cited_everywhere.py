"""Do the artifacts that publish a DOI publish the same one?

Four files state where this work is archived: CITATION.cff, README.md, the
paper, and the agent instructions. Three of them carried
10.5281/zenodo.21499823. The fourth said "No DOI yet" and named only the
withdrawn record, so an agent reading it would have told someone there is no
archive, or reached for the deleted DOI as the only one it knew.

The withdrawn record is the reason this matters. 10.5281/zenodo.21361920
archived the fabricated version and was removed at the author's request before
any dissemination. It has to remain nameable -- every one of these files
explains what happened to it -- while never being offered as the citable DOI.
So the check is not "the retracted DOI is absent" but "it is never the one on
offer", which is a different and more useful property.

What this cannot check is whether the live DOI resolves. That is a claim about
Zenodo, not about this repository, and a test that pretended to verify it by
matching a string would be the kind of guard that reads stronger than it is.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

LIVE_DOI = "10.5281/zenodo.21499823"
WITHDRAWN_DOI = "10.5281/zenodo.21361920"

# Files that state where the work is archived. Each must agree.
PUBLISHING = (
    "CITATION.cff",
    "README.md",
    ".hermes.md",
    "paper/honest/scoring_bias_v2.tex",
)

# Words that mark a mention of the withdrawn record as an explanation of its
# withdrawal rather than an invitation to cite it.
DISAVOWING = (
    "remov", "delet", "retract", "fabricat", "withdraw", "must not", "never",
    "prior", "earlier", "previous",
)


def _text(rel):
    path = REPO / rel
    if not path.exists():
        pytest.skip(f"[repo] {rel} not present")
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.parametrize("rel", PUBLISHING)
def test_the_live_doi_is_the_one_stated(rel):
    text = _text(rel)
    assert LIVE_DOI in text, (
        f"{rel} does not state {LIVE_DOI}, which the other publishing files "
        f"give as the archive of record; a reader comparing two of these files "
        f"sees two different answers about where the work lives"
    )


@pytest.mark.parametrize("rel", PUBLISHING)
def test_the_withdrawn_doi_is_never_on_offer(rel):
    """It may be named, but only in a sentence that disowns it."""
    text = _text(rel)
    if WITHDRAWN_DOI not in text:
        return
    lines = text.splitlines()
    for line_no, line in enumerate(lines, 1):
        if WITHDRAWN_DOI not in line:
            continue
        # The line itself and the one after it. A wider window was the first
        # thing written here and it could not fail: replacing the disavowing
        # sentence with "See also <withdrawn DOI>" still passed, because the
        # rest of the paragraph three lines away still said "fabricated".
        # Disavowal has to be attached to the mention, not merely nearby.
        window = " ".join(lines[line_no - 1:line_no + 1]).lower()
        assert any(word in window for word in DISAVOWING), (
            f"{rel}:{line_no} names the withdrawn record {WITHDRAWN_DOI} with "
            f"nothing nearby saying it was removed or why; it reads as a "
            f"citable DOI for a version that was fabricated"
        )


def test_no_other_doi_is_advertised():
    """A third DOI appearing anywhere means one of these files drifted."""
    stray = {}
    for rel in PUBLISHING:
        found = set(re.findall(r"10\.5281/zenodo\.\d+", _text(rel)))
        extra = found - {LIVE_DOI, WITHDRAWN_DOI}
        if extra:
            stray[rel] = sorted(extra)
    assert not stray, (
        f"{stray} name a Zenodo DOI that is neither the archive of record nor "
        f"the withdrawn one; every DOI this project publishes has to be "
        f"accounted for"
    )
