"""Does anything unfinished survive into what a reader receives?

A TODO, a "citation needed", or an unresolved [?] in a published PDF is
permanent in a way a repository defect is not: the arXiv version of record does
not get quietly amended, and this project's whole position is that its
artefacts can be trusted.

Checked in the archive's own sources rather than only in the built PDF, so it
runs without LaTeX -- and separately in the PDF where one exists, because a
marker can also arrive through a figure or a bibliography entry, neither of
which appears in main.tex.
"""

import re
import tarfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
ARCHIVE = HONEST / "arxiv_submission.tar.gz"
PDF = HONEST / "scoring_bias_v2.pdf"

# label -> (pattern, a string it must match, so a broken regex fails loudly)
# Probed against restatements on 2026-08-14. The four shouted markers were
# case-sensitive, so "todo:", "fixme" and "tbd" -- how they are actually typed
# when someone is mid-thought rather than mid-shout -- all passed. That is the
# fourth pattern set in this repository found matching only the casing of the
# example that prompted it.
#
# The additions are markers this project has already produced. The bib entry
# quarantined earlier today carried `eprint = {2607.xxxxx}`: a placeholder
# arXiv identifier, in a citation, formatted for pasting. None of the words
# below appears anywhere in the paper sources, so each is an unambiguous sign
# that something was left unfinished.
MARKERS = {
    "TODO": (r"(?i)\bTODO\b", "TODO: rewrite this"),
    "FIXME": (r"(?i)\bFIXME\b", "FIXME before submission"),
    "XXX": (r"\bXXX\b", "XXX check this number"),
    "TBD": (r"(?i)\bTBD\b", "value TBD"),
    "HACK": (r"(?i)\bHACK:", "HACK: temporary"),
    "placeholder": (r"(?i)\bplaceholder\b", "PLACEHOLDER value"),
    "to be determined": (r"(?i)\bto be determined\b", "count to be determined"),
    "placeholder identifier": (
        r"(?i)\b(?:arxiv:)?\d{4}\.x{4,}|\bx{4,}\.x{4,}",
        "2607.xxxxx",
    ),
    "citation needed": (r"(?i)citation needed", "[citation needed]"),
    "lorem ipsum": (r"(?i)lorem ipsum", "Lorem ipsum dolor"),
    "note to self": (r"(?i)\bnote to self\b", "note to self: check"),
    "unresolved reference": (r"\[\?\]", "see [?] for details"),
}


def _archive_sources():
    if not ARCHIVE.exists():
        pytest.skip("[submission] archive not present")
    text = []
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith((".tex", ".bbl")):
                text.append(tar.extractfile(member).read().decode("utf-8", "replace"))
    if not text:
        pytest.skip("[submission] archive carries no tex sources")
    return "\n".join(text)


def _working_tree_sources():
    """The sources as they are now, which is what the next packaging will ship.

    Checking only the archive means a marker introduced today is invisible until
    someone reruns arxiv_package.py -- and the archive is a tarball, so no
    mutation can reach it either. These are tracked text files, so the guard is
    exercisable rather than merely asserted.
    """
    parts = []
    for name in ("scoring_bias_v2.tex", "macros.tex"):
        path = HONEST / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    if not parts:
        pytest.skip("[paper] sources not present")
    return "\n".join(parts)


@pytest.mark.parametrize("label", sorted(MARKERS))
def test_the_working_sources_carry_no_draft_marker(label):
    pattern = MARKERS[label][0]
    body = "\n".join(
        re.sub(r"(?<!\\)%.*", "", line) for line in _working_tree_sources().splitlines()
    )
    found = [
        " ".join(body[max(0, m.start() - 60): m.end() + 40].split())
        for m in re.finditer(pattern, body)
    ]
    assert not found, f"{label} appears in the paper sources: {found[:3]}"


@pytest.mark.parametrize("label", sorted(MARKERS))
def test_the_submission_sources_carry_no_draft_marker(label):
    pattern = MARKERS[label][0]
    text = _archive_sources()
    # LaTeX comments are not shipped to the reader; a note behind % is fine.
    body = "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())
    found = [
        " ".join(body[max(0, m.start() - 60): m.end() + 40].split())
        for m in re.finditer(pattern, body)
    ]
    assert not found, f"{label} appears in the submission sources: {found[:3]}"


@pytest.mark.parametrize("label", sorted(MARKERS))
def test_the_pattern_matches_its_own_sample(label):
    """A broken regex would otherwise sweep a clean bill of health."""
    pattern, sample = MARKERS[label]
    assert re.search(pattern, sample), f"the {label} pattern no longer matches its sample"


def test_the_built_pdf_carries_no_draft_marker():
    """The artefact itself, which can pick up markers the sources do not show."""
    import shutil
    import subprocess

    if not PDF.exists():
        pytest.skip("[pdf] not built; the source check above still applies")
    if shutil.which("pdftotext") is None:
        pytest.skip("[pdftotext] not installed; the source check above still applies")
    result = subprocess.run(
        ["pdftotext", "-raw", str(PDF), "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    assert result.returncode == 0, "could not read the built PDF"
    text = result.stdout
    assert len(text) > 20000, f"the PDF yielded only {len(text)} characters of text"

    offenders = {
        label: len(re.findall(pattern, text))
        for label, (pattern, _) in MARKERS.items()
        if re.search(pattern, text)
    }
    assert not offenders, f"draft markers in the built PDF: {offenders}"
