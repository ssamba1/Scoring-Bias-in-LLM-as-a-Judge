"""Does the environment document describe the environment actually pinned?

repro/ENVIRONMENT.md tells a reader which stack reproduces the paper and, more
usefully, where bit-exact reproduction is verified and where it is not. Both
halves rot the same way: the pins move and the document keeps quoting the old
versions, so someone installs what it says and gets numbers that differ for a
reason the document has stopped explaining.

The platform caveat is the part worth having. Reproducing on Windows with the
same pins moves eight values in the fourth decimal, all in the responsiveness
term. Nothing the paper reports changes, but a reader running `git diff` sees a
mismatch, and a reproducibility claim that does not say where it holds invites
exactly that confusion.
"""

import itertools
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
DOC = REPRO / "ENVIRONMENT.md"
PINS = REPRO / "requirements-repro.txt"


def _doc():
    if not DOC.exists():
        pytest.skip("[environment] ENVIRONMENT.md not present")
    return DOC.read_text(encoding="utf-8", errors="replace")


def _pins():
    if not PINS.exists():
        pytest.skip("[pins] requirements-repro.txt not present")
    pins = {}
    for line in PINS.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^([A-Za-z][\w-]*)==([\d.]+)", line.strip())
        if match:
            pins[match.group(1).lower()] = match.group(2)
    return pins


def test_the_document_quotes_the_pinned_versions():
    doc, pins = _doc(), _pins()
    assert pins, "no pinned versions parsed from requirements-repro.txt"

    wrong = []
    for package in ("numpy", "scipy", "statsmodels"):
        if package not in pins:
            continue
        expected = f"{package}=={pins[package]}"
        if expected not in doc.replace("`", ""):
            stated = re.search(rf"{package}==([\d.]+)", doc)
            wrong.append(
                f"{package}: pinned {pins[package]}, document says "
                f"{stated.group(1) if stated else 'nothing'}"
            )
    assert not wrong, f"ENVIRONMENT.md does not match the pins: {wrong}"


def test_the_document_says_where_reproduction_is_verified():
    doc = _doc()
    assert re.search(r"(?i)linux|ubuntu", doc), (
        "the document does not say on which platform bit-exact reproduction is "
        "verified, which is the question a reader running git diff is asking"
    )
    assert "regenerate-and-diff" in doc, (
        "the document does not name the job that verifies reproduction, so the "
        "claim cannot be checked by the reader"
    )


def test_the_platform_caveat_names_the_affected_values():
    """A caveat without the numbers is not checkable, and would not be believed."""
    doc = _doc()
    for value in ("0.4863", "0.1967", "0.839"):
        assert value in doc, (
            f"the platform caveat no longer names {value}; a reader seeing that "
            f"value in their own diff cannot tell whether it is the known "
            f"difference or a real one"
        )
    assert re.search(r"(?i)no number the paper reports changes", doc), (
        "the document no longer states whether the platform difference affects "
        "anything the paper reports"
    )


def test_the_job_the_document_names_still_exists():
    """The document points at a CI job for its guarantee; that job must exist."""
    workflow = REPO / ".github" / "workflows" / "repro.yml"
    if not workflow.exists():
        pytest.skip("[workflow] repro.yml not present")
    body = workflow.read_text(encoding="utf-8", errors="replace")
    assert "regenerate-and-diff:" in body, (
        "ENVIRONMENT.md credits the regenerate-and-diff job with verifying "
        "reproduction; that job is gone"
    )
    assert "ubuntu-latest" in body, "the workflow no longer runs on Linux"


def _pin_files():
    """Every tracked file that pins a version, with its (package -> version)."""
    listing = subprocess.run(
        ["git", "ls-files", "*.txt", "*.yml", "Dockerfile"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    ).stdout.split()
    pins = {}
    for rel in listing:
        if rel.startswith(("RETRACTED/", ".verify-venv")):
            continue
        path = REPO / rel
        if not path.exists():
            continue
        found = {}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            code = line.split("#", 1)[0].strip()
            match = re.match(r"^-?\s*([A-Za-z][\w.-]*)\s*==\s*([\w.+]+)", code)
            if match:
                found[match.group(1).lower()] = match.group(2)
        if found:
            pins[rel] = found
    return pins


def test_no_two_files_pin_the_same_package_differently():
    """One package, one version, across the whole repository.

    requirements.txt pinned numpy==1.26.4 and scipy==1.13.1 while the analysis
    stack pins 2.4.4 and 1.17.1, and the Dockerfile installed the former -- so
    the published container reproduced none of the paper's numbers. A second set
    of pins is not redundancy; it is a second answer to the same question.
    """
    pins = _pin_files()
    assert len(pins) >= 2, f"only {sorted(pins)} carry pins; the sweep found too little"

    conflicts = []
    for (left, right) in itertools.combinations(sorted(pins), 2):
        for package in set(pins[left]) & set(pins[right]):
            if pins[left][package] != pins[right][package]:
                conflicts.append(
                    f"{package}: {left} says {pins[left][package]}, "
                    f"{right} says {pins[right][package]}"
                )
    assert not conflicts, (
        f"the same package is pinned to different versions in different files: "
        f"{conflicts}"
    )
