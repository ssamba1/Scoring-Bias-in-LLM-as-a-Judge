"""Does the release contain what the paper promises it contains?

The conclusion says: "We release a single-script reproduction and a full
integrity audit of a prior, fabricated version of this project." Both halves are
checkable, and one of them was false until recently -- the single script,
run_all.sh, reproduced the *retracted* paper. It built camera_ready_full.tex,
regenerated the fabricated-era figures and ran the analyses over the suspect
model set, and every step succeeded, so a reader taking the paper at its word
would have reproduced the wrong paper and seen nothing wrong.

A promise in a paper is a claim like any other. These are the ones a reader acts
on rather than merely believes, so they are worth holding to the same standard
as the numbers.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
RUN_ALL = REPO / "run_all.sh"
AUDIT = REPO / "DATA_INTEGRITY_AUDIT.md"


def _paper_text():
    parts = []
    for name in ("scoring_bias_v2.tex", "macros.tex"):
        path = HONEST / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    if not parts:
        pytest.skip("[paper] sources not present")
    return "".join(parts)


def test_the_paper_still_makes_these_promises():
    """If the wording changes, the checks below must be revisited, not skipped."""
    text = _paper_text()
    assert re.search(r"single-script reproduction", text), (
        "the paper no longer promises a single-script reproduction; update this "
        "guard to match the new promise rather than deleting it"
    )
    assert re.search(r"integrity audit", text), "the paper no longer promises an integrity audit"


def test_the_paper_does_not_claim_a_single_input_file():
    """The contributions list said "every number from one file". It is not one.

    That wording is a survivor of the earlier seven-family study, where the
    t4fam run really was a single file. The paper of record derives its numbers
    from sixteen committed inputs across the panel, the stage ablation, the
    replications, the frontier judges and the patching runs. "One command" is
    true and checkable; "one file" was neither.
    """
    text = _paper_text()
    assert not re.search(r"every number from one file", text), (
        "the paper claims every number comes from one file; the analyses read "
        "sixteen committed inputs"
    )

    repro = REPO / "paper" / "honest" / "repro"
    if not repro.is_dir():
        pytest.skip("[repro] directory not present")
    inputs = set()
    for script in repro.glob("analyze_*.py"):
        body = script.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"[\"']([\w.-]+\.json(?:\.gz)?)[\"']", body):
            name = match.group(1)
            if "analysis" not in name and (repro / name).exists():
                inputs.add(name)
    assert len(inputs) > 1, (
        f"only {inputs} found as analysis inputs; if the release really has "
        f"collapsed to one file the sentence above should say so again"
    )


def test_the_single_script_reproduction_exists_and_targets_the_paper_of_record():
    assert RUN_ALL.exists(), "the paper promises a single-script reproduction; run_all.sh is absent"
    body = RUN_ALL.read_text(encoding="utf-8", errors="replace")

    assert "paper/honest" in body, (
        "run_all.sh does not mention paper/honest, so the promised single-script "
        "reproduction does not reproduce the paper of record"
    )

    # Names of the retracted build, which this script used to drive. Comments
    # are stripped first: the script's header explains what it used to do and
    # names camera_ready_full.tex in order to say so. A guard that reads its own
    # explanation as the defect is the fourth of its kind this session.
    code = "\n".join(
        line.split("#", 1)[0] for line in body.splitlines()
    )
    retracted = [name for name in ("camera_ready_full.tex", "camera_ready.tex",
                                   "generate_png_figures.py", "figures_advanced")
                 if name in code]
    assert not retracted, (
        f"run_all.sh still drives the retracted build ({retracted}); it would "
        f"reproduce the wrong paper while appearing to succeed"
    )


def test_the_reproduction_script_is_valid_shell():
    """A promised script that does not parse is not a reproduction."""
    if not RUN_ALL.exists():
        pytest.skip("[run_all] absent")
    for candidate in ("bash", "sh"):
        try:
            result = subprocess.run(
                [candidate, "-n", str(RUN_ALL)], capture_output=True, text=True, timeout=120
            )
        except (FileNotFoundError, OSError):
            continue
        assert result.returncode == 0, f"run_all.sh has a syntax error:\n{result.stderr[-500:]}"
        return
    pytest.skip("[shell] no bash or sh available to parse the script")


def test_the_scripts_the_reproduction_invokes_exist():
    """Every python file run_all.sh runs must be present in the release."""
    if not RUN_ALL.exists():
        pytest.skip("[run_all] absent")
    body = RUN_ALL.read_text(encoding="utf-8", errors="replace")
    invoked = set(re.findall(r"python3?\s+([\w./-]+\.py)", body))
    # Names invoked from inside a `cd`; resolve against the directories the
    # script actually enters as well as the repository root.
    roots = [REPO, HONEST, HONEST / "repro"]
    missing = [
        name for name in invoked
        if not any((root / name).exists() for root in roots)
    ]
    assert not missing, (
        f"run_all.sh invokes {missing}, which the release does not contain; the "
        f"promised reproduction would fail partway through"
    )
    assert len(invoked) >= 5, (
        f"only {len(invoked)} scripts parsed out of run_all.sh; the check above "
        f"is verifying less than it appears to"
    )


def test_the_integrity_audit_exists_and_names_its_evidence():
    """The audit is two documents: the narrative and the per-artefact verdicts.

    DATA_INTEGRITY_AUDIT.md establishes what happened; paper/PROVENANCE_AUDIT.md
    carries the FABRICATED / SUSPECT / MISLABELED / INFLATED rulings item by
    item. Counting verdicts in the first alone understates the audit, which is
    what a first version of this check did.
    """
    assert AUDIT.exists(), "the paper promises a full integrity audit; DATA_INTEGRITY_AUDIT.md is absent"
    body = AUDIT.read_text(encoding="utf-8", errors="replace")
    assert len(body) > 2000, "the integrity audit is too short to be the promised full audit"

    provenance = REPO / "paper" / "PROVENANCE_AUDIT.md"
    assert provenance.exists(), "the per-artefact provenance rulings are absent"
    corpus = body + provenance.read_text(encoding="utf-8", errors="replace")
    verdicts = sum(
        corpus.count(word) for word in ("FABRICATED", "SUSPECT", "MISLABELED", "INFLATED")
    )
    assert verdicts >= 10, (
        f"the audit records only {verdicts} verdicts across both documents; the "
        f"paper describes it as a full audit of the fabricated version"
    )
