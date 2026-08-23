"""Reversal drives the judge past chance, into inversion. The paper must say so.

The ground-truth test pairs a good answer with a bad one and records `accuracy`
as the share of pairs the judge orders correctly. For binary pairs, chance is
$0.5$. Unperturbed, judges score $0.98$. Under rubric reversal the release
measures $0.02$ (base) and $0.00$ (instruct).

The prose described that as collapsing "to chance". It is not chance. An
accuracy of $0.00$ means the judge ordered *every* pair the wrong way round --
it is chance's opposite, and a stronger result than the sentence claimed: a
judge that follows a reversed rubric literally should invert, and it does.
Calling it chance turns a systematic, explainable failure into noise.

Every number in that sentence was correct and traceable; only the word joining
them was wrong. That is why this file checks the characterisation rather than
the digits -- `check_prose.py` already pins the digits, and pinning digits is
exactly what fails to catch a claim that misdescribes them.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
GOLD = HONEST / "repro" / "results_gold.json"

CHANCE = 0.5


def _gold():
    if not GOLD.exists():
        pytest.skip("[repro] results_gold.json not present")
    return json.loads(GOLD.read_text(encoding="utf-8", errors="replace"))


def _paper():
    text = ""
    for name in ("macros.tex", "scoring_bias_v2.tex"):
        path = HONEST / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace")
    if not text:
        pytest.skip("[paper] no LaTeX sources present")
    return text


def test_reversal_drives_accuracy_below_chance():
    reversed_ = _gold()["degradation"]["reversed"]
    for arm in ("base", "instruct"):
        acc = reversed_[arm]["accuracy_under_bias"]
        assert acc < CHANCE, (
            f"the {arm} judge scores {acc} under rubric reversal, at or above "
            f"the {CHANCE} chance level for binary good-vs-bad pairs. The paper "
            f"describes near-total inversion; that reading needs an accuracy "
            f"well below chance, not merely a low one."
        )


def test_the_collapse_is_not_described_as_chance():
    """The wording that was wrong, guarded as wording."""
    text = _paper()
    offenders = []
    for m in re.finditer(r"chance", text, re.I):
        window = " ".join(text[max(0, m.start() - 240): m.end() + 120].split())
        if "accuracy" in window.lower() and "reversal" in window.lower():
            # naming the chance level to contrast against it is the correct use
            if re.search(r"not to chance|past it to|which .{0,40}chance .{0,20}is",
                         window, re.I):
                continue
            offenders.append(window[-220:])
    assert not offenders, (
        "the paper describes the rubric-reversal accuracy collapse as reaching "
        "chance. The measured accuracies are 0.02 and 0.00 against a chance "
        f"level of {CHANCE}: that is inversion, not chance, and a stronger "
        f"result than 'chance' reports. Offending passage(s): {offenders}"
    )


def test_the_paper_states_the_chance_level_it_contrasts_against():
    """A reader cannot judge "past chance" without knowing where chance is."""
    text = _paper()
    assert re.search(r"good-vs-bad pairs is \$0\.5\$", text), (
        "the paper contrasts the reversal collapse against chance but no longer "
        "states what chance is for these pairs. Without the 0.5 the contrast is "
        "not checkable by a reader."
    )
