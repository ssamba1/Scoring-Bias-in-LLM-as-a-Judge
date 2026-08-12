"""Does a macro end a sentence in a place the surrounding text does not?

The abstract read "...transfers the shift in a sharply localized mid-network
layer band.), a preregistered stage ablation..." -- a full stop inside a
parenthesis, mid-sentence, twice.

It came from reuse. Two macros were written as standalone sentences, ending in a
period, and then dropped inside parentheses in the abstract. Neither LaTeX nor
any check in this suite has an opinion about that: it compiles, no box is
overfull, no reference is undefined, and every number in the sentence is right.
It only shows up when someone reads the rendered page, which is how it survived
into the most-read paragraph of the paper.

The rule this enforces is narrow: a macro used inside parentheses must not carry
its own sentence-final punctuation. Where a macro is used both ways -- inside
parentheses and as a standalone sentence -- the period belongs at the call site
that needs it, not inside the macro.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
MACROS = HONEST / "macros.tex"
PAPER = HONEST / "scoring_bias_v2.tex"


def _macro_bodies():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    bodies = {}
    for line in MACROS.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}\s*$", line)
        if match:
            bodies[match.group(1)] = match.group(2)
    if not bodies:
        pytest.skip("[paper] no single-line macros parsed")
    return bodies


def _paper():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    return PAPER.read_text(encoding="utf-8", errors="replace")


def _parenthesised_uses(text):
    """Macro names invoked directly inside a parenthesis: "(\\NAME{}" or "(\\NAME{} ...)"."""
    return set(re.findall(r"\(\s*\\(\w+)\{\}", text))


def test_no_parenthesised_macro_carries_a_sentence_period():
    bodies = _macro_bodies()
    paper = _paper()
    offenders = []
    for name in sorted(_parenthesised_uses(paper)):
        body = bodies.get(name)
        if body is None:
            continue
        if body.rstrip().endswith("."):
            offenders.append(f"\\{name}")
    assert not offenders, (
        f"these macros end with a full stop and are used inside parentheses, so "
        f"the sentence stops mid-clause on the page: {offenders}. Move the "
        f"period to the call site that needs it."
    )


def test_the_sweep_finds_parenthesised_macros():
    """Vacuity guard: if the pattern stops matching, the check above is empty."""
    used = _parenthesised_uses(_paper())
    assert len(used) >= 2, (
        f"only {len(used)} parenthesised macro uses found ({sorted(used)}); the "
        f"pattern no longer matches how the paper invokes them"
    )


def test_the_standalone_use_supplies_the_period_the_macro_gave_up():
    """Removing a period from a macro is only correct if its call sites add one.

    Scoped to the macro that is used both ways -- GOLDSENTENCE runs inside the
    abstract's parentheses and as a sentence of its own in the discussion. A
    blanket rule over every macro is wrong: value macros (\\NFAM) and the
    abstract's clause macros are joined by semicolons and correctly carry no
    punctuation at all.
    """
    bodies = _macro_bodies()
    if "GOLDSENTENCE" not in bodies:
        pytest.skip("[paper] GOLDSENTENCE is gone")
    paper = _paper()
    if bodies["GOLDSENTENCE"].rstrip().endswith("."):
        pytest.skip("[paper] the macro carries its own period again")

    standalone = re.findall(r"(?<!\()\\GOLDSENTENCE\{\}(.)", paper)
    assert standalone, "GOLDSENTENCE is no longer used outside parentheses"
    unpunctuated = [c for c in standalone if c not in ".,;:"]
    assert not unpunctuated, (
        f"GOLDSENTENCE gave up its full stop for the parenthesised use, and a "
        f"standalone use is now followed by {unpunctuated} instead of a period"
    )
