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
