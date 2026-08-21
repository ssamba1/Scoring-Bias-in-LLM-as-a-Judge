"""The bibliography must still be the one that was checked against arXiv.

`test_citations_are_well_formed.py` is explicit about its limit: it can require
every entry to be *findable* -- a well-formed identifier, a DOI, a URL -- but it
cannot prove one is *real*, because that needs the network, and a test that
passes silently when offline would be worse than none.

So the network half was done once, on 2026-08-21, and written down in
`paper/honest/CITATION_VERIFICATION.md`: every arXiv identifier in the
bibliography was fetched from `export.arxiv.org`, and its title and first author
compared against the entry. This file turns that one-time check into a standing
offline one. If an identifier is changed, added, or swapped, the bibliography
stops matching the record and this fails -- without needing the network again.

The concern is not hypothetical in this repository. A previous version of this
bibliography cited arXiv:2410.17703 for IBM Granite; that identifier is real and
resolves, to "Schemes of Associative Algebras", a math.AG paper. The companion
project attributed a sentence in quotation marks to a survey that does not
contain it. Both compile clean and read plausibly. A resolving identifier and a
correct one are different things, and only a comparison against the source can
tell them apart.

One deliberate subtlety: the bibliography carries that phantom identifier to
this day, in a `%` comment explaining what it was and why it was replaced. A
scan that does not strip comments reads it as a live citation -- which happened
while building the record, and is why the parsing here drops comment lines
first. Keeping the note is right; reading it as a citation is not.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BIB = REPO / "paper" / "honest" / "honest.bib"
RECORD = REPO / "paper" / "honest" / "CITATION_VERIFICATION.md"

# `eprint = {2506.22316}` and `note = {arXiv:2303.16634}` are both used.
IDENTIFIER = re.compile(r"(?:eprint\s*=\s*\{|arXiv:)\s*(\d{4}\.\d{4,5})")
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(\d{4}\.\d{4,5})\s*\|([^|]*)\|([^|]*)\|", re.M)


def _bib_without_comments():
    if not BIB.exists():
        pytest.skip("[bib] honest.bib not present")
    raw = BIB.read_text(encoding="utf-8", errors="replace")
    return "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("%")
    )


def _cited_identifiers():
    """key -> arXiv id, for every entry that carries one."""
    found = {}
    for block in re.split(r"\n(?=@)", _bib_without_comments()):
        key = re.search(r"@\w+\{([^,]+),", block)
        ident = IDENTIFIER.search(block)
        if key and ident:
            found[key.group(1)] = ident.group(1)
    return found


def _record():
    if not RECORD.exists():
        pytest.skip("[bib] CITATION_VERIFICATION.md not present")
    text = RECORD.read_text(encoding="utf-8", errors="replace")
    return {
        m.group(1): (m.group(2), m.group(3).strip(), m.group(4).strip())
        for m in ROW.finditer(text)
    }


def test_every_arxiv_citation_was_verified():
    cited, record = _cited_identifiers(), _record()
    assert cited, "no arXiv identifiers found in the bibliography at all"

    unverified = sorted(
        f"{key} cites {aid}" for key, aid in cited.items()
        if key not in record or record[key][0] != aid
    )
    assert not unverified, (
        f"{unverified} are not in CITATION_VERIFICATION.md, or are recorded "
        f"against a different identifier. Every arXiv citation has to have been "
        f"checked against the source; an identifier that resolves is not the "
        f"same as one that is right."
    )


def test_the_record_does_not_outlive_the_bibliography():
    """An entry recorded as verified but no longer cited is stale bookkeeping."""
    cited, record = _cited_identifiers(), _record()
    dropped = sorted(set(record) - set(cited))
    assert not dropped, (
        f"{dropped} are recorded as verified but no longer carry that identifier "
        f"in the bibliography. Update the record rather than leaving it claiming "
        f"a check that no longer applies to anything."
    )


def test_the_phantom_identifier_is_only_ever_a_comment():
    """The note explaining the old wrong identifier must not become a citation.

    arXiv:2410.17703 is a real paper -- it is simply not the one that entry was
    for. Keeping the explanation is right; having it read as a live citation
    would restore exactly the defect the note records.
    """
    if not BIB.exists():
        pytest.skip("[bib] honest.bib not present")
    raw = BIB.read_text(encoding="utf-8", errors="replace")
    if "2410.17703" not in raw:
        pytest.skip("[bib] the note about the replaced identifier is gone")

    live = _bib_without_comments()
    assert "2410.17703" not in live, (
        "arXiv:2410.17703 appears outside a comment in honest.bib. That "
        "identifier belongs to 'Schemes of Associative Algebras' and was "
        "previously cited for IBM Granite; it is kept only as a note about the "
        "correction."
    )


def test_the_record_reports_what_it_checked():
    """A record that lost its counts or its date is not a record."""
    text = RECORD.read_text(encoding="utf-8", errors="replace") if RECORD.exists() else ""
    if not text:
        pytest.skip("[bib] CITATION_VERIFICATION.md not present")
    cited = _cited_identifiers()
    assert "2026-08-21" in text, "the verification record no longer says when it was made"
    assert str(len(cited)) in text, (
        f"the record does not state how many identifiers were checked; the "
        f"bibliography carries {len(cited)}"
    )
