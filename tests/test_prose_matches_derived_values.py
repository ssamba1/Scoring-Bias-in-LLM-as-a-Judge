r"""Run the prose-consistency gate here, not only where the analyses run.

check_prose.py compares every headline number in the paper against the derived
JSON it came from. It has been running in the reproduction job, which installs
numpy, scipy, statsmodels, pandas and matplotlib before it can start -- yet the
checker itself imports nothing but json, math, re and pathlib. So the gate that
protects the paper's numbers was gated behind a dependency install it never
needed, and did not run at all in the integrity job.

Running it here changes two things. It executes wherever pytest does, including
the stack-free CI job and a bare clone. And it becomes reachable by the mutation
harness, which runs pytest files: before this, no registered mutation could
demonstrate that a drifted headline number would be caught, because the thing
that would catch it was not a test.

The checker is invoked as a subprocess rather than imported. It is written as a
script that exits non-zero on failure, and importing it would run its checks at
import time -- which would make collection failures look like errors and hide
the names it prints.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
CHECKER = REPRO / "check_prose.py"


def _run():
    return subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=REPRO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )


def test_every_headline_number_in_the_prose_matches_its_source():
    if not CHECKER.exists():
        pytest.skip("[repro] check_prose.py not present")
    result = _run()
    assert result.returncode == 0, (
        "the paper quotes numbers that no longer match the derived results:\n"
        + (result.stdout or result.stderr)
    )


def test_the_prose_checker_reports_what_it_checked():
    """A checker that silently checks nothing passes exactly like a clean one."""
    if not CHECKER.exists():
        pytest.skip("[repro] check_prose.py not present")
    result = _run()
    assert "prose-consistency" in (result.stdout + result.stderr).lower(), (
        f"check_prose.py produced no verdict line; stdout was {result.stdout!r}"
    )


def test_the_prose_checker_needs_no_analysis_stack():
    """It must stay importable where the heavy dependencies are absent.

    The whole point of running it here is that the integrity job installs only
    pytest. If someone adds `import numpy` to the checker, it starts skipping in
    exactly the environment this test exists to cover, and it should fail loudly
    instead.
    """
    if not CHECKER.exists():
        pytest.skip("[repro] check_prose.py not present")
    source = CHECKER.read_text(encoding="utf-8", errors="replace")
    heavy = [
        name
        for name in ("numpy", "scipy", "statsmodels", "pandas", "matplotlib")
        if f"import {name}" in source
    ]
    assert not heavy, (
        f"check_prose.py now imports {heavy}, so it can no longer run in the "
        f"stack-free job this test covers"
    )
