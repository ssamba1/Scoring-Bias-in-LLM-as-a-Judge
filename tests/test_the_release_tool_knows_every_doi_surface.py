"""Does the DOI-updating tool know about every file that cites the DOI?

Five files name the Zenodo deposit and README names it three times. When the
author mints a corrected deposit, all of them have to move together: a paper
citing the new record while CITATION.cff still points at the old one is worse
than either, because the machine-readable metadata is what Zenodo and GitHub's
citation widget read, and it travels further than the PDF.

`release_doi.py set-doi` rewrites them in one pass. Its list of surfaces is
hardcoded, which makes it exactly the kind of hand-maintained inventory this
project has watched rot before -- a CI lint list that had frozen while six
scripts were added, and a checker whose file set predated the files it was meant
to cover.

So the list is checked against the tree rather than trusted: any tracked file
that names a Zenodo DOI must be one the tool will update.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "release_doi.py"
DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")

# Paths that hold the superseded record on purpose, or are build outputs
# regenerated from a source that is itself updated.
EXEMPT_PREFIXES = ("RETRACTED/", "paper/honest/arxiv_submission/",
                   "paper/honest/superseded/", "paper/archive/", "dist/")


def _surfaces_from_tool():
    if not TOOL.exists():
        pytest.skip("[release] release_doi.py not present")
    sys.path.insert(0, str(REPO))
    try:
        import release_doi
    finally:
        sys.path.pop(0)
    return set(release_doi.DOI_SURFACES), dict(release_doi.DOI_FROZEN)


def _tracked():
    out = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("[git] not a repository")
    return [p for p in out.stdout.splitlines() if p]


def test_every_file_citing_a_doi_is_one_the_tool_updates():
    known, frozen = _surfaces_from_tool()
    citing = set()
    for rel in _tracked():
        if rel.startswith(EXEMPT_PREFIXES):
            continue
        path = REPO / rel
        if not path.is_file() or path.suffix.lower() in {".pdf", ".png", ".gz", ".ico"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        if DOI_RE.search(text):
            citing.add(rel)

    missed = sorted(citing - known - set(frozen))
    assert not missed, (
        f"{missed} cite a Zenodo DOI but release_doi.py will not update them. "
        f"A deposit refresh would leave them pointing at the old record, and the "
        f"machine-readable ones travel furthest. If one deliberately names "
        f"an old deposit, add it to DOI_FROZEN with the reason instead."
    )

    absent = sorted(n for n in known if not (REPO / n).exists())
    assert not absent, (
        f"the tool lists {absent}, which no longer exist -- a stale inventory "
        f"reads as coverage it does not have"
    )


def test_the_sweep_actually_finds_the_known_surfaces():
    """Vacuity guard: an over-broad exemption would make the check pass empty."""
    known, _ = _surfaces_from_tool()
    present = [n for n in known if (REPO / n).exists()]
    assert len(present) >= 3, (
        f"only {len(present)} of the tool's surfaces exist; the comparison above "
        f"would pass while covering almost nothing"
    )
    citing_now = [n for n in present
                  if DOI_RE.search((REPO / n).read_text(encoding="utf-8", errors="replace"))]
    assert citing_now, (
        "none of the listed surfaces currently names a DOI, so the sweep has "
        "nothing to compare and would pass regardless"
    )


_WORDS = {
    "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12,
}


def _surfaces_naming_the_live_doi():
    """file -> how many times it names the DOI the paper currently cites.

    Taken from the tool's own sweep rather than reimplemented, so the guard and
    the tool cannot disagree about what counts as a surface.
    """
    if not TOOL.exists():
        pytest.skip("[release] release_doi.py not present")
    sys.path.insert(0, str(REPO))
    try:
        import release_doi
    finally:
        sys.path.pop(0)
    return dict(release_doi.current_dois().get(release_doi.LIVE, {}))


def _stated(haystack, pattern, label):
    found = re.search(pattern, haystack, re.I)
    assert found, f"{label} is no longer stated in the form this guard reads"
    word = found.group(1).lower()
    assert word in _WORDS, f"{label}: {word!r} is not a number-word this guard knows"
    return _WORDS[word]


def test_the_prose_counts_of_doi_surfaces_recompute():
    """Three places state how many files name the DOI. Two of them were wrong.

    The tool's own docstring said "Five files cite it (README three times)" and
    the checklist said eight, twice. The sweep reports nine, README five times,
    every time it runs. DOI_SURFACES was correct throughout -- release_doi.py
    became a surface itself when it grew a LIVE constant, and neither sentence
    followed.

    The existing guards compare the declared list against the filesystem. That
    is the right check and structurally could not catch this: the list was not
    wrong. The English beside it was, and nothing read the English.
    """
    surfaces = _surfaces_naming_the_live_doi()
    total = len(surfaces)
    readme = surfaces.get("README.md")
    assert readme, "README.md no longer names the DOI; re-anchor this guard"

    doc = (REPO / "release_doi.py").read_text(encoding="utf-8", errors="replace")
    stated = _stated(doc, r"(\w+) files cite it", "the tool's docstring count")
    assert stated == total, (
        f"release_doi.py's docstring states {stated} citing files; the sweep "
        f"finds {total}: {sorted(surfaces)}"
    )
    stated = _stated(doc, r"README (\w+) times", "the tool's README count")
    assert stated == readme, (
        f"release_doi.py's docstring states README names it {stated} times; the "
        f"sweep finds {readme}"
    )

    checklist = (REPO / "paper" / "submission_checklist.md").read_text(
        encoding="utf-8", errors="replace")
    flat = " ".join(checklist.split())
    stated = _stated(flat, r"(\w+) files name the DOI", "the checklist count")
    assert stated == total, (
        f"the checklist states {stated} files name the DOI; the sweep finds {total}"
    )
    stated = _stated(flat, r"the swap touches (\w+) files", "the checklist swap count")
    assert stated == total, (
        f"the checklist states the swap touches {stated} files; the sweep finds {total}"
    )
