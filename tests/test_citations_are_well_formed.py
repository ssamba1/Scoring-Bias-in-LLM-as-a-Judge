"""Can a reader find every work this paper cites?

The retracted version of this project cited works that did not exist. That is
not detectable from the LaTeX build: an undefined *key* is reported, but a
defined key pointing at a fabricated paper compiles silently and looks the same
on the page as a real one. Nothing here checked the bibliography at all.

This cannot prove a reference is real -- that needs the network, and a test that
silently passes when offline would be worse than none. What it can do is require
every entry to be findable: a well-formed arXiv identifier, or a DOI, or a
venue. A fabricated reference has to survive that, and the easiest fabrications
do not.

Scope matters more than it looks. The first version of this check scanned each
entry for the first YYYY.NNNNN-looking string and found four "defects" -- every
one an artefact of the checker. Three were entries pairing a preprint eprint
with a later venue year, which is correct practice, and the fourth matched
inside a DOI (10.1016/j.xinn.2025.100456 -> "2025.10045", an impossible month
25). So: read the eprint field, not the entry text, and only require the year to
agree with the identifier when there is no venue to disagree with it.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
BIB = HONEST / "honest.bib"
SOURCES = ("scoring_bias_v2.tex", "macros.tex")

# The paper is dated August 2026; nothing it cites can be posted after that.
LATEST_YY, LATEST_MM = 26, 8


def _bib():
    if not BIB.exists():
        pytest.skip("[bibliography] honest.bib not present")
    return BIB.read_text(encoding="utf-8", errors="replace")


def _entries():
    """(key, entry_type, body) per bibliography entry."""
    out = []
    for block in re.split(r"\n(?=@)", _bib()):
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", block)
        if m:
            out.append((m.group(2), m.group(1).lower(), block))
    return out


def _field(body, name):
    m = re.search(name + r"\s*=\s*[{\"]([^}\"]*)[}\"]", body, re.I)
    return m.group(1).strip() if m else None


def _cited_keys():
    text = ""
    for name in SOURCES:
        path = HONEST / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace")
    if not text:
        pytest.skip("[paper] no LaTeX sources present")
    keys = set()
    for m in re.finditer(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}", text):
        keys |= {k.strip() for k in m.group(1).split(",") if k.strip()}
    return keys


def test_every_cited_key_is_defined():
    defined = {key for key, _, _ in _entries()}
    missing = sorted(_cited_keys() - defined)
    assert not missing, f"cited but absent from honest.bib: {missing}"


def test_no_duplicate_bibliography_keys():
    keys = [key for key, _, _ in _entries()]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    assert not dups, f"duplicate bibliography keys (BibTeX silently keeps one): {dups}"


def test_arxiv_identifiers_are_well_formed():
    """A malformed identifier resolves to nothing, so the citation is unusable."""
    bad = []
    for key, _, body in _entries():
        eprint = _field(body, "eprint")
        if not eprint:
            continue
        m = re.fullmatch(r"(\d{2})(\d{2})\.(\d{4,5})(v\d+)?", eprint)
        if not m:
            bad.append(f"{key}: eprint {eprint!r} is not a YYMM.NNNNN arXiv id")
            continue
        yy, mm = int(m.group(1)), int(m.group(2))
        if not 1 <= mm <= 12:
            bad.append(f"{key}: eprint {eprint} has month {mm:02d}")
        elif yy > LATEST_YY or (yy == LATEST_YY and mm > LATEST_MM):
            bad.append(f"{key}: eprint {eprint} is dated after this paper")
    assert not bad, "malformed arXiv identifiers: " + "; ".join(bad)


def test_every_cited_work_is_findable():
    """Each cited entry carries an identifier or a venue a reader can follow."""
    unfindable = []
    for key, _, body in _entries():
        if key not in _cited_keys():
            continue
        if not any(_field(body, f) for f in ("eprint", "doi", "url", "journal", "booktitle")):
            unfindable.append(key)
    assert not unfindable, (
        f"cited with no arXiv id, DOI, URL or venue -- a reader cannot check "
        f"these at all: {unfindable}"
    )


def test_preprint_years_agree_with_their_identifiers():
    """For entries with no venue, the year must match the identifier's date.

    Only applied where there is no journal or booktitle: an entry that pairs a
    2024 preprint with a 2026 proceedings is correct, and flagging it was this
    checker's own first bug.
    """
    wrong = []
    for key, _, body in _entries():
        if _field(body, "journal") or _field(body, "booktitle"):
            continue
        eprint, year = _field(body, "eprint"), _field(body, "year")
        if not (eprint and year):
            continue
        m = re.match(r"(\d{2})(\d{2})\.", eprint)
        if m and 1 <= int(m.group(2)) <= 12 and int(year) != 2000 + int(m.group(1)):
            wrong.append(f"{key}: year={year} but eprint {eprint} is from 20{m.group(1)}")
    assert not wrong, "; ".join(wrong)


def test_the_bibliography_is_actually_being_read():
    """Vacuity guard: every check above passes trivially on an empty parse."""
    entries = _entries()
    assert len(entries) >= 20, f"only {len(entries)} bibliography entries parsed"
    cited = _cited_keys()
    assert len(cited) >= 20, f"only {len(cited)} citation keys found in the paper"
    with_eprint = [k for k, _, b in entries if _field(b, "eprint")]
    assert len(with_eprint) >= 15, (
        f"only {len(with_eprint)} entries have an eprint field; the identifier "
        f"checks would be nearly vacuous"
    )
