"""Does the check the docs demand before committing actually pass?

`.hermes.md` rule 8 and the pull request template both told contributors to run
`make lint` before committing. It had never passed. The target ran flake8 *and*
`black --check`, and black has never been applied here: 72 of the 88 files it
covers would be reformatted. flake8 alone reported 42 violations. So the first
thing a new contributor was told to do failed on code they had not written, and
nothing in the suite noticed, because no test ran the linter.

The 42 are fixed -- four dead imports, three blank-line and spacing issues, an
f-string with no placeholder, and 24 over-long lines wrapped. The two remaining
categories are exemptions with reasons in setup.cfg rather than fixes: E203 is
where flake8 and black disagree about slice spacing, and mutation_check.py is
exempt from the line-length rule because its strings are the exact bytes it
matches against other files -- wrapping them stops the mutation from applying,
which the harness reports as never having run.

black is out of the gate and into `make format-diff`, advisory. Adopting it
would rewrite those same anchors. That is a real cost against no correctness
benefit, and the honest response to a gate that has never passed is either to
make it pass or to stop calling it a gate -- not to leave it failing in the
documentation.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TARGETS = ["tests/", "mutation_check.py", "verify_like_ci.py", "scan_secrets.py"]


def test_flake8_is_clean():
    if shutil.which("flake8") is None:
        try:
            import flake8  # noqa: F401
        except ImportError:
            pytest.skip("[lint] flake8 not installed; `make lint` installs it")
    result = subprocess.run(
        [sys.executable, "-m", "flake8", *TARGETS],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert result.returncode == 0, (
        "`make lint` does not pass, and both .hermes.md and the pull request "
        "template tell contributors to run it before committing:\n"
        + (result.stdout or result.stderr)[:2000]
    )


def test_the_config_explains_every_exemption():
    config = REPO / "setup.cfg"
    if not config.exists():
        pytest.skip("[lint] setup.cfg not present")
    text = config.read_text(encoding="utf-8", errors="replace")
    for token in ("E203", "mutation_check.py"):
        assert token in text, (
            f"setup.cfg no longer mentions {token}; an exemption without its "
            f"reason written down is how the next one gets added silently"
        )
    # Every ignore should sit under a comment saying why.
    assert text.count("#") >= 4, (
        "setup.cfg has lost its explanatory comments; the exemptions are only "
        "defensible with the reasoning attached"
    )


def test_the_documented_gate_is_the_gate_that_runs():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8", errors="replace")
    hermes = (REPO / ".hermes.md").read_text(encoding="utf-8", errors="replace")

    lint_body = makefile.split("\nlint:", 1)[1].split("\n\n", 1)[0] if "\nlint:" in makefile else ""
    assert "flake8" in lint_body, "the lint target no longer runs flake8"
    assert "black" not in lint_body, (
        "black is back in the lint gate. It reformats 72 of 88 files, including "
        "the exact-match strings in mutation_check.py; if it is genuinely being "
        "adopted, the anchors have to be re-registered first"
    )
    assert "make lint" in hermes, (
        ".hermes.md no longer points contributors at `make lint`, which is the "
        "only check that catches dead imports here"
    )
