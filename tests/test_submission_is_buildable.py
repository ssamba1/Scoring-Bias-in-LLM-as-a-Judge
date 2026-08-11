"""The submission must build clean and stand on its own.

The previous packager built from `camera_ready.tex`, carried "Student A, Student
B" as the author list, and described the retracted finding in its abstract
metadata. The archive it produced sat tracked in the repository for two weeks
after the retraction, still containing the fabricated model names -- and a
tarball is the one artefact people upload without opening.

These checks are about the honest paper's submission bundle:

  * the archive exists and its digests still match the paper sources, so an edit
    without repackaging is detectable rather than silent;
  * it ships a .bbl, because arXiv does not run BibTeX and the references would
    otherwise vanish from the announced version;
  * nothing retracted is inside it;
  * the paper's own build is clean -- no overfull boxes, no undefined
    references.

The expensive half (extract the archive and compile it) lives in
`paper/honest/arxiv_package.py --check`, which needs a LaTeX installation. These
tests read the artefacts instead, so they run anywhere, and skip rather than
fail when an artefact has not been generated in this checkout.
"""

import json
import re
import tarfile
from pathlib import Path

import pytest

from fabricated_signatures import PATTERNS

ROOT = Path(__file__).resolve().parents[1]
HONEST = ROOT / "paper" / "honest"
ARCHIVE = HONEST / "arxiv_submission.tar.gz"
LOG = HONEST / "scoring_bias_v2.log"

RETRACTED_SIGNATURES = list(PATTERNS.values())


@pytest.fixture(scope="module")
def archive_members():
    if not ARCHIVE.exists():
        pytest.skip("no archive; run paper/honest/arxiv_package.py")
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        return {
            m.name: tar.extractfile(m).read()
            for m in tar.getmembers()
            if m.isfile()
        }


def test_the_archive_ships_a_bbl(archive_members):
    """arXiv does not run BibTeX; a missing .bbl silently drops the references."""
    assert "main.bbl" in archive_members, sorted(archive_members)
    assert len(archive_members["main.bbl"]) > 500, "the .bbl is suspiciously small"


def test_the_archive_contains_the_paper_and_its_assets(archive_members):
    assert "main.tex" in archive_members
    figures = [n for n in archive_members if n.startswith("figures/")]
    tables = [n for n in archive_members if n.startswith("tables/")]
    assert len(figures) >= 8, f"only {len(figures)} figures bundled"
    assert len(tables) >= 3, f"only {len(tables)} tables bundled"


def test_nothing_retracted_is_inside_the_archive(archive_members):
    offenders = []
    for name, data in archive_members.items():
        text = data.decode("utf-8", "ignore")
        for pattern in RETRACTED_SIGNATURES:
            if re.search(pattern, text):
                offenders.append((name, pattern))
    assert not offenders, (
        f"the submission archive carries retracted content: {offenders}. This is "
        f"how the previous tarball stayed contaminated for two weeks after the "
        f"manuscripts were retracted."
    )


def test_the_archive_matches_the_current_sources(archive_members):
    """A paper edited after packaging would otherwise ship stale."""
    import hashlib

    assert "SOURCE.json" in archive_members, "no digest manifest in the archive"
    manifest = json.loads(archive_members["SOURCE.json"].decode("utf-8"))
    stale = []
    for name, digest in manifest["sources"].items():
        path = HONEST / name
        if not path.exists():
            stale.append(f"{name} (missing)")
            continue
        data = path.read_bytes()
        if path.suffix in {".tex", ".bib", ".md"}:
            data = data.replace(b"\r\n", b"\n")
        if hashlib.sha256(data).hexdigest() != digest:
            stale.append(name)
    assert not stale, (
        f"the archive predates edits to {stale}; rerun "
        f"paper/honest/arxiv_package.py before submitting"
    )


def test_the_paper_builds_without_overfull_boxes():
    """The bar the companion papers hold: nothing in the margin."""
    if not LOG.exists():
        pytest.skip("no build log; compile paper/honest/scoring_bias_v2.tex")
    log = LOG.read_text(encoding="utf-8", errors="ignore")
    boxes = re.findall(r"Overfull \\hbox \(([\d.]+)pt", log)
    assert not boxes, f"{len(boxes)} overfull box(es): {boxes[:5]}"


def test_the_paper_has_no_undefined_references():
    if not LOG.exists():
        pytest.skip("no build log; compile paper/honest/scoring_bias_v2.tex")
    log = LOG.read_text(encoding="utf-8", errors="ignore")
    undefined = re.findall(r"(?:Citation|Reference) .*? undefined", log)
    assert not undefined, f"{len(undefined)} undefined: {undefined[:3]}"
