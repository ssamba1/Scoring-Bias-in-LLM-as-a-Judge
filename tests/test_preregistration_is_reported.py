r"""Does every preregistered prediction get reported?

A preregistration is only worth something if each registered prediction comes
back with an outcome. The failure mode is not fraud, it is attrition: a
prediction whose result is unremarkable stops being interesting to write up, and
nothing anywhere notices it went missing. The reader cannot notice either --
checking requires holding twenty ids in their head while reading the paper.

P4 was registered here and never mentioned. Its result had in fact been computed
and was sitting in the released JSON, and the substance of it was even in the
paper; what was missing was the link between the sentence and the registration,
which is precisely what a compliance check needs. Two smaller things fell out of
the same gap: P4 registered the content group as (authority, verbosity), and the
reported analysis grouped reference_answer with them without saying so.

This guard checks the linkage, not the verdict -- whether a prediction was
confirmed is a matter for the prose. What it refuses to allow is a registered
prediction that the paper never mentions at all.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
PREREG = HONEST / "PREREGISTRATION.md"
SOURCES = ("scoring_bias_v2.tex", "macros.tex")


def _prereg():
    if not PREREG.exists():
        pytest.skip("[preregistration] PREREGISTRATION.md not present")
    return PREREG.read_text(encoding="utf-8", errors="replace")


def _paper():
    text = ""
    for name in SOURCES:
        path = HONEST / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace")
    if not text:
        pytest.skip("[paper] no LaTeX sources present")
    return text


def _registered_ids():
    """Ids introduced as a registered prediction, e.g. "**P4 (generality).**"."""
    return sorted(
        {int(n) for n in re.findall(r"\*\*P(\d{1,2})\s*\(", _prereg())}
    )


def test_every_registered_prediction_is_mentioned_in_the_paper():
    registered = _registered_ids()
    assert registered, "no registered predictions parsed from PREREGISTRATION.md"
    cited = {int(n) for n in re.findall(r"\bP(\d{1,2})\b", _paper())}
    missing = [f"P{i}" for i in registered if i not in cited]
    assert not missing, (
        f"registered but never mentioned in the paper: {missing}. A registered "
        f"prediction needs a reported outcome, even when the outcome is dull."
    )


def test_the_paper_invents_no_prediction_ids():
    registered = set(_registered_ids())
    # Only ids written in a preregistration context, so P2_0 (a theory symbol)
    # and stray matches in prose do not count as claims of registration.
    claimed = {
        int(n)
        for pair in re.findall(
            r"preregistered\s+P(\d{1,2})\b|\bP(\d{1,2})\b[^.]{0,40}registered", _paper()
        )
        for n in pair
        if n
    }
    invented = sorted(claimed - registered)
    assert not invented, f"the paper cites P{invented} as preregistered; not in PREREGISTRATION.md"


def test_the_registered_grouping_is_reported_where_it_differs():
    """P4's registered probe set is narrower than the one the analysis groups.

    The paper may report the wider grouping -- it is defensible -- but it has to
    also report the registered one, or the registered prediction has no verdict
    on its own terms.
    """
    paper = _paper()
    if "P4" not in paper:
        pytest.skip("[paper] P4 not discussed")
    flat = " ".join(paper.split())
    assert re.search(r"authority and verbosity alone|as registered", flat), (
        "P4 registered the content group as (authority, verbosity); the paper "
        "must report that grouping, not only the wider one"
    )


def test_the_prediction_list_is_actually_parsed():
    """Vacuity guard: an empty id list satisfies every check above."""
    registered = _registered_ids()
    assert len(registered) >= 15, (
        f"only {len(registered)} registered predictions parsed: {registered}. "
        f"If the preregistration's formatting changed, fix the parse rather than "
        f"letting the check pass on an empty set."
    )
