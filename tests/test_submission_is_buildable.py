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
    """Exactly the assets the paper draws -- not "at least eight".

    A floor passes while a figure is missing, as long as enough others are
    present, and the paper would then build on my machine (where the file is in
    the working tree) and fail on arXiv (where only the archive exists). What
    matters is correspondence: every \\includegraphics and every \\input
    resolves inside the archive, and nothing rides along that the paper does not
    draw.
    """
    assert "main.tex" in archive_members
    tex = archive_members["main.tex"].decode("utf-8", "replace")

    drawn = set()
    for match in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", tex):
        name = Path(match.group(1)).name
        drawn.add(name if "." in name else name + ".pdf")
    inputs = {
        (n if n.endswith(".tex") else n + ".tex")
        for n in (Path(m.group(1)).name for m in re.finditer(r"\\input\{([^}]*)\}", tex))
    }

    shipped_figures = {Path(n).name for n in archive_members if n.startswith("figures/")}
    shipped_tables = {Path(n).name for n in archive_members if n.startswith("tables/")}
    top_level = {Path(n).name for n in archive_members if "/" not in n}

    assert drawn, "the archive's main.tex draws no figures at all"
    missing = sorted(drawn - shipped_figures)
    assert not missing, f"the paper draws {missing}, which the archive does not carry"

    stowaways = sorted(shipped_figures - drawn)
    assert not stowaways, (
        f"the archive carries {stowaways}, which the paper never draws -- an "
        f"arXiv submission should not ship figures from a different version"
    )

    unresolved = sorted(n for n in inputs if n not in shipped_tables and n not in top_level)
    assert not unresolved, f"the paper inputs {unresolved}, which the archive does not carry"


def test_the_archived_assets_match_the_working_tree(archive_members):
    """What ships must be the figures I have been checking, not older copies."""
    import hashlib

    differing = []
    for name, data in archive_members.items():
        if not name.startswith(("figures/", "tables/")):
            continue
        live = HONEST / name
        if not live.exists():
            differing.append(f"{name}: not in the working tree")
        elif hashlib.sha256(live.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
            differing.append(f"{name}: archive copy differs")
    assert not differing, (
        f"the archive's assets are not the ones in the working tree: {differing}. "
        f"check_figures verifies the working tree against the data; if the "
        f"archive holds different bytes, that verification does not cover what "
        f"would be submitted."
    )


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
        pytest.skip(
            "no build log locally; the submission-compiles CI job builds the "
            "archive and asserts the same properties, so this is not unchecked"
        )
    log = LOG.read_text(encoding="utf-8", errors="ignore")
    boxes = re.findall(r"Overfull \\hbox \(([\d.]+)pt", log)
    assert not boxes, f"{len(boxes)} overfull box(es): {boxes[:5]}"


def test_the_paper_has_no_undefined_references():
    if not LOG.exists():
        pytest.skip(
            "no build log locally; the submission-compiles CI job builds the "
            "archive and asserts the same properties, so this is not unchecked"
        )
    log = LOG.read_text(encoding="utf-8", errors="ignore")
    undefined = re.findall(r"(?:Citation|Reference) .*? undefined", log)
    assert not undefined, f"{len(undefined)} undefined: {undefined[:3]}"


def _unresolved_citations(tex, bbl):
    """Keys cited in `tex` that `bbl` does not define. Pure, so it can be tested."""
    cited = set()
    for match in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", tex):
        cited |= {k.strip() for k in match.group(1).split(",") if k.strip()}
    defined = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", bbl))
    return sorted(cited - defined), sorted(defined - cited)


def test_the_shipped_bibliography_defines_every_citation():
    """arXiv does not run BibTeX; the shipped .bbl is the bibliography.

    A key cited in the text but missing from the .bbl renders as a bold [?] in
    the published PDF. The local build catches it as "Citation undefined", but
    only where LaTeX is installed -- which is not most machines, and has not
    been CI for the whole of this session. This reads the archive directly.
    """
    import tarfile

    if not ARCHIVE.exists():
        pytest.skip("[submission] archive not present")
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        names = {m.name for m in tar.getmembers()}
        if not {"main.tex", "main.bbl"} <= names:
            pytest.skip("[submission] archive lacks main.tex or main.bbl")
        tex = tar.extractfile("main.tex").read().decode("utf-8", "replace")
        if "macros.tex" in names:
            tex += tar.extractfile("macros.tex").read().decode("utf-8", "replace")
        bbl = tar.extractfile("main.bbl").read().decode("utf-8", "replace")

    missing, unused = _unresolved_citations(tex, bbl)
    assert not missing, (
        f"{len(missing)} citation(s) have no entry in the shipped bibliography "
        f"and would render as [?] on arXiv: {missing}"
    )
    assert len(bbl) > 1000, f"the shipped .bbl is only {len(bbl)} characters"
    # Unused entries are harmless, but a large excess means the .bbl came from a
    # different paper -- which is how a stale bibliography usually looks.
    assert len(unused) <= 3, f"{len(unused)} entries in the .bbl are never cited: {unused[:6]}"


def test_the_citation_check_can_fail():
    """The comparison above must actually detect a missing entry."""
    tex = r"Text \citep{present} and \citet{absent}."
    bbl = r"\bibitem[P]{present} A paper."
    missing, _ = _unresolved_citations(tex, bbl)
    assert missing == ["absent"], f"the check missed an unresolved citation: {missing}"


def test_the_staged_directory_and_the_tarball_are_the_same_submission():
    """Two copies of the submission are committed; they must not disagree.

    `arxiv_submission/` is the staging directory and `arxiv_submission.tar.gz`
    is what gets uploaded. Both are in the repository, which makes it easy to
    edit the readable one -- a quick fix to main.tex before submitting -- and
    upload the other. Nothing then says which is the paper: the digests in
    SOURCE.json tie the archive to the *sources*, not to the directory sitting
    beside it.
    """
    import hashlib
    import tarfile

    staged = HONEST / "arxiv_submission"
    if not ARCHIVE.exists() or not staged.is_dir():
        pytest.skip("[submission] archive or staging directory not present")

    with tarfile.open(ARCHIVE, "r:gz") as tar:
        in_tar = {
            m.name: hashlib.sha256(tar.extractfile(m).read()).hexdigest()
            for m in tar.getmembers() if m.isfile()
        }
    on_disk = {
        p.relative_to(staged).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in staged.rglob("*") if p.is_file()
    }

    assert in_tar, "the archive contains no files"
    only_tar = sorted(set(in_tar) - set(on_disk))
    only_dir = sorted(set(on_disk) - set(in_tar))
    differ = sorted(n for n in set(in_tar) & set(on_disk) if in_tar[n] != on_disk[n])
    assert not (only_tar or only_dir or differ), (
        f"the staged directory and the tarball are not the same submission -- "
        f"only in the tarball: {only_tar}; only in the directory: {only_dir}; "
        f"same name but different bytes: {differ}. Rerun arxiv_package.py so "
        f"both describe what would actually be uploaded."
    )


def test_ci_really_compiles_the_archive():
    """The two skips above claim CI covers them. Check that it does.

    Both build-log assertions skip without a local build, and their skip message
    says the submission-compiles job checks the same properties. A skip that
    points elsewhere for its coverage is only honest while the elsewhere exists;
    otherwise it is a nicer-sounding way of not checking.

    This asserts the job is present, builds the archive rather than the working
    tree, and asserts the same three properties.
    """
    workflow = ROOT / ".github" / "workflows" / "repro.yml"
    if not workflow.exists():
        pytest.skip("[workflow] repro.yml not present")
    body = workflow.read_text(encoding="utf-8", errors="replace")

    assert "submission-compiles:" in body, (
        "the build-log tests skip on the promise that a submission-compiles job "
        "covers them; that job is gone"
    )
    job = body[body.index("submission-compiles:"):]
    job = job[: job.find("\n  regenerate-and-diff:")] if "\n  regenerate-and-diff:" in job else job

    for needle, what in (
        ("arxiv_submission.tar.gz", "builds the archive rather than the working tree"),
        ("pdflatex", "runs a LaTeX build"),
        ("main.bbl", "checks the bibliography ships"),
        ("Overfull", "checks for overfull boxes"),
        ("undefined", "checks for undefined references"),
        ("not found", "checks for missing files"),
    ):
        assert needle in job, f"the submission-compiles job no longer {what}"
