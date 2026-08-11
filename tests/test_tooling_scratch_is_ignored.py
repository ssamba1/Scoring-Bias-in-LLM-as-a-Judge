"""Is every working directory the tooling creates kept out of the repository?

mutation_check.py copies the paper's sources into `.mutation_stash/` before it
edits them, and verify_like_ci.py builds a pinned virtualenv at `.verify-venv/`.
Both clean up on a normal exit, so both are invisible almost all the time. After
an interrupted run they are not, and neither was in .gitignore -- so a `git add
-A` at the wrong moment would commit stashed copies of the paper's own sources,
or several hundred megabytes of virtualenv, into the release repository.

The stash case is the worse one. It contains pre-mutation copies of exactly the
files the mutation edits, under flattened names. Committed, it would look like a
duplicate set of the paper's data files with no explanation.

The directories are read out of the tools rather than listed here, so a tool
that starts using a new scratch path fails this until the path is ignored. A
hand-written list would go stale silently, which is the failure mode this whole
suite exists to refuse.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOLS = ("mutation_check.py", "verify_like_ci.py")


def _declared_scratch():
    """Root-relative scratch paths the tools construct, e.g. BASE / ".stash"."""
    found = {}
    for name in TOOLS:
        path = REPO / name
        if not path.exists():
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        # Assignments only. mutation_check.py carries the same expression as a
        # bare string inside a mutation it registers against this very check,
        # and matching that made the check fail against its own registration.
        for match in re.finditer(
            r"^\s*\w+\s*=\s*(?:BASE|REPO|HERE)\s*/\s*\"(\.[\w.-]+)\"", body, re.M
        ):
            found[match.group(1)] = name
    if not found:
        pytest.skip("[tooling] no scratch directories declared")
    return found


def test_every_scratch_directory_is_ignored():
    scratch = _declared_scratch()
    gitignore = REPO / ".gitignore"
    assert gitignore.exists(), "no .gitignore, so nothing is excluded from a commit"
    patterns = {
        line.strip().rstrip("/")
        for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    unignored = sorted(f"{name} ({tool})" for name, tool in scratch.items()
                       if name not in patterns)
    assert not unignored, (
        f"these are created inside the repository and are not ignored: "
        f"{unignored}. They survive an interrupted run, and `git add -A` would "
        f"commit them."
    )


def test_git_agrees_that_they_are_ignored():
    """.gitignore syntax is not obvious; ask git rather than parse it twice."""
    scratch = _declared_scratch()
    probe = subprocess.run(
        ["git", "check-ignore"] + [f"{name}/probe" for name in scratch],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    ignored = {line.split("/")[0] for line in probe.stdout.splitlines()}
    missed = sorted(set(scratch) - ignored)
    assert not missed, (
        f"git does not consider {missed} ignored, whatever .gitignore appears "
        f"to say"
    )


def test_no_scratch_directory_was_ever_committed():
    scratch = _declared_scratch()
    for name in scratch:
        listing = subprocess.run(
            ["git", "ls-files", name], cwd=REPO, capture_output=True, text=True, timeout=300,
        )
        tracked = listing.stdout.split()
        assert not tracked, (
            f"{len(tracked)} file(s) under {name} are tracked, e.g. "
            f"{tracked[:3]} -- an interrupted run was committed"
        )
