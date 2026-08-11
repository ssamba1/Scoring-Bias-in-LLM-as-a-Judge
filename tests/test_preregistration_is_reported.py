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


def test_every_registered_prediction_has_a_recorded_outcome():
    """An outcome in the preregistration itself, not only in the paper.

    Outcomes were recorded for every addendum -- P7 through P20 -- and for none
    of H0 and P1--P6, the confirmatory core. A reader opening this file found
    verdicts for the exploratory additions and nothing for the predictions the
    study was designed around. P2 was the worst of it: registered as a positive
    correlation, measured negative, and reported in the paper under a different
    label (P2_0), so the registered id looked simply unadjudicated.

    Outcomes are written in two shapes here -- a per-prediction line ("**P12
    outcome ...**") and a grouped block ("- P7 **confirmed**: ..."), so both
    count. What does not count is silence.
    """
    text = _prereg()
    registered = _registered_ids()
    assert registered, "no registered predictions parsed from PREREGISTRATION.md"

    adjudicated = {int(n) for n in re.findall(r"\*\*P(\d{1,2}) outcome", text)}
    adjudicated |= {int(n) for n in re.findall(r"^\s*-\s+P(\d{1,2})\s+\*\*", text, re.M)}
    # "- **P1 (sharpening) -- confirmed.**": the dash after the closing paren is
    # what separates an outcome from the registration line, which reads
    # "- **P1 (sharpening).** Instruction tuning lowers ...".
    adjudicated |= {
        int(n) for n in re.findall(r"\*\*P(\d{1,2})\s*\([^)]*\)\s*(?:--|—)", text)
    }

    missing = [f"P{i}" for i in registered if i not in adjudicated]
    assert not missing, (
        f"registered with no outcome recorded in the preregistration: {missing}. "
        f"The paper may well report them, but a preregistration that records "
        f"outcomes for some predictions and not others is not evidence of "
        f"anything -- the omissions are exactly where a reader would look."
    )


def test_the_null_hypothesis_has_an_outcome_too():
    """H0 is registered without a P-number, so the id sweep cannot see it."""
    text = _prereg()
    if "**H0" not in text:
        pytest.skip("[preregistration] H0 not registered under that name")
    assert re.search(r"\*\*H0\s*(\([^)]*\))?\s*(--|—)", text), (
        "H0 is registered but no outcome is recorded for it; it is the "
        "hypothesis the whole panel was run to test"
    )


def test_the_multiplicity_limitation_matches_the_register():
    """The limitation names the count and the failures. Both come from this file.

    A limitation that understates how many tests were run, or names a prediction
    as failed that is recorded as confirmed, is worse than none: it reads as a
    reckoning that has been done. Both halves are checked against the register.
    """
    paper = _paper()
    if "no family-wise error rate is controlled" not in paper:
        pytest.skip("[paper] the multiplicity limitation is not stated")

    registered = _registered_ids()
    words = {20: "twenty", 21: "twenty-one", 19: "nineteen", 22: "twenty-two"}
    count = words.get(len(registered), str(len(registered)))
    assert f"preregistered {count} predictions" in paper, (
        f"the limitation states a number of registered predictions that is not "
        f"{count}; the register holds {len(registered)}"
    )

    prereg = _prereg()
    flat = " ".join(paper.split())
    claimed = re.search(r"reported as failures \(([^)]*)\)", flat)
    assert claimed, "the limitation no longer lists which predictions failed"
    for ident in re.findall(r"P(\d{1,2})", claimed.group(1)):
        block = re.search(rf"\*\*P{ident} outcome[^*]*\*\*(.{{0,120}})", prereg, re.S)
        grouped = re.search(rf"^\s*-\s+P{ident}\s+\*\*([^*]*)\*\*", prereg, re.M)
        verdict = (block.group(1) if block else "") + (grouped.group(1) if grouped else "")
        assert verdict, f"P{ident} is named as failed but records no outcome"
        assert re.search(r"(?i)fail|split|nominal", verdict), (
            f"the limitation names P{ident} among the failures, but its recorded "
            f"outcome reads {verdict.strip()[:60]!r}"
        )


def test_the_prediction_list_is_actually_parsed():
    """Vacuity guard: an empty id list satisfies every check above."""
    registered = _registered_ids()
    assert len(registered) >= 15, (
        f"only {len(registered)} registered predictions parsed: {registered}. "
        f"If the preregistration's formatting changed, fix the parse rather than "
        f"letting the check pass on an empty set."
    )
