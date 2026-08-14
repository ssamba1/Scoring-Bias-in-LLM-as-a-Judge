"""Does run_all.sh do what the Reproducibility section says it does?

The section listed the nineteen raw files, said each was "collected by the
matching repro/*_harness.py script", and then said "run_all.sh runs all of them
in order". It does not. It names no harness at all: it installs, runs the
guards, regenerates the derived results with the fourteen analyzers, diffs them
against what is committed, runs the prose and figure checks, compiles the paper
and rebuilds the submission package.

That is the honest and useful thing for it to do -- re-collecting the raw data
needs GPU and API access, which is the whole reason the raw files are committed
-- but the sentence told a reviewer that one command reproduces the collection
end to end. Overstating what one command reproduces is the same species of
error as overstating a result, and it sat in the section a skeptical reader
turns to first.

So the two are checked against each other in both directions: the script must
still run the analyzers and the checks it is credited with, and the paper must
not claim it runs the harnesses.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "run_all.sh"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"
REPRO = REPO / "paper" / "honest" / "repro"


def _script():
    if not SCRIPT.exists():
        pytest.skip("[repo] run_all.sh not present")
    return SCRIPT.read_text(encoding="utf-8", errors="replace")


def _paper():
    if not PAPER.exists():
        pytest.skip("[paper] not present")
    return PAPER.read_text(encoding="utf-8", errors="replace")


def test_the_script_runs_no_harness():
    """The premise of the correction: it really does not collect data."""
    named = sorted({
        m.group(0) for m in re.finditer(r"\b\w+_harness\.py", _script())
    })
    assert not named, (
        f"run_all.sh now runs {named}. If it collects data again, the "
        f"Reproducibility section should say so; this test encodes that it "
        f"does not."
    )


def test_the_script_runs_every_analyzer_it_is_credited_with():
    script = _script()
    analyzers = sorted(p.name for p in REPRO.glob("analyze_*.py"))
    if not analyzers:
        pytest.skip("[repro] no analyzers present")
    missing = [a for a in analyzers if a not in script]
    assert not missing, (
        f"run_all.sh does not run {missing}, but the paper credits it with "
        f"regenerating every derived number; a reader running it would get a "
        f"clean pass over an incomplete regeneration"
    )


def test_the_script_still_checks_what_it_regenerates():
    script = _script()
    for expected in ("check_prose.py", "check_figures.py", "mutation_check.py",
                     "git diff --exit-code"):
        assert expected in script, (
            f"run_all.sh no longer runs {expected!r}; regenerating results "
            f"without comparing them to what is committed proves nothing"
        )


def test_the_paper_does_not_claim_the_script_collects_data():
    paper = _paper()
    match = re.search(r"run_all\.sh[^.]{0,120}", paper)
    if not match:
        pytest.skip("[paper] does not mention run_all.sh")
    sentence = match.group(0)
    assert "runs all of them in order" not in sentence, (
        "the paper says run_all.sh 'runs all of them in order' after listing "
        "the harnesses; it runs none of them"
    )
    assert "does not rerun the harnesses" in paper, (
        "the paper no longer states that run_all.sh does not rerun the "
        "harnesses, which is the limit a reader needs in order to know what "
        "one command actually reproduces"
    )
