"""The abstract arXiv actually stores, and whether it still says the paper's claims.

arXiv's abstract metadata field caps at 1920 characters and truncates from the
END. The paper's own abstract is 3,184 characters of plain text, so pasting it
into the submission form silently discards the last 1,264 -- which here would be
the ground-truth result, the mitigation number, the frontier-judge finding, and,
last of all, the sentence disclosing that a prior fabricated version of this
project exists and was fully audited. That is the single sentence this project
can least afford to lose, and nothing would have reported its loss.

`ARXIV_ABSTRACT.txt` is therefore the version that goes in the form. Adding a
second abstract creates the exact risk this repository keeps finding elsewhere:
a summary maintained separately from the thing it summarises, drifting toward a
cleaner claim. The companion papers did precisely that -- an abstract quoting an
in-sample figure the body had superseded, and a "most self-checks deny" that the
body qualified with a second classifier.

So the short version is held to the long one mechanically. Every number in it
must already appear in the paper's abstract; it may drop claims, since that is
what shortening is, but it may not state a number the paper does not. And the
integrity sentence is pinned by name, because the whole reason this file exists
is that truncation eats the end.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
SHORT = HONEST / "ARXIV_ABSTRACT.txt"
PAPER = HONEST / "scoring_bias_v2.tex"
MACROS = HONEST / "macros.tex"

ARXIV_ABSTRACT_LIMIT = 1920

NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def _short():
    if not SHORT.exists():
        pytest.skip("[submission] ARXIV_ABSTRACT.txt not present")
    return SHORT.read_text(encoding="utf-8", errors="replace").strip()


def _paper_abstract():
    if not PAPER.exists():
        pytest.skip("[paper] main tex not present")
    tex = PAPER.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if not match:
        pytest.fail("the paper has no abstract environment to compare against")
    # The paper writes 56{,}000: the brace group is a LaTeX thousands
    # separator, not a break between two numbers, and leaving it in makes
    # the paper look like it says "56" and "000".
    body = " ".join(match.group(1).split()).replace("{,}", ",")
    if MACROS.exists():
        macros = MACROS.read_text(encoding="utf-8", errors="replace")
        for name, text in re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}", macros):
            body = body.replace("\\" + name + "{}", text)
    return body


def _digits(text):
    """Numbers as bare digit strings, so 56,000 and 56000 compare equal."""
    return {token.replace(",", "") for token in NUMBER.findall(text)}


def test_the_short_abstract_fits_the_metadata_field():
    short = _short()
    assert len(short) <= ARXIV_ABSTRACT_LIMIT, (
        f"the submission abstract is {len(short)} characters against arXiv's "
        f"{ARXIV_ABSTRACT_LIMIT}. It truncates from the end, so the overflow is "
        f"silently dropped rather than refused: {short[ARXIV_ABSTRACT_LIMIT:]!r}"
    )


def test_it_states_no_number_the_paper_does_not():
    """Shortening may drop claims. It may not introduce or alter one."""
    short, full = _short(), _paper_abstract()
    invented = sorted(_digits(short) - _digits(full))
    assert not invented, (
        f"{invented} appear in the submission abstract but not in the paper's "
        f"own abstract. A shorter version may leave things out; a number that "
        f"is only in the short one is a claim the paper does not make."
    )


def test_the_integrity_sentence_survives():
    """The clause truncation would eat last is the one that must not go."""
    short = _short()
    required = [
        ("regenerates from committed raw files", "the reproducibility claim"),
        ("no synthetic data", "the no-synthetic-data statement"),
        ("fabricated version of this project", "the disclosure of the prior fabrication"),
    ]
    missing = [why for phrase, why in required if phrase not in short]
    assert not missing, (
        f"the submission abstract has lost {missing}. This project retracted a "
        f"fabricated predecessor; the disclosure is not an optional flourish at "
        f"the end of the abstract, and it is the first thing a length limit "
        f"takes."
    )


def test_the_paper_abstract_is_measured_not_assumed():
    """Guard the premise: if the paper's abstract now fits, say so.

    This file exists because the paper's abstract overruns the field. If it is
    ever shortened below the cap, the second surface stops being necessary and
    should be reconsidered rather than maintained out of habit.
    """
    full = _paper_abstract()
    plain = re.sub(r"\\[a-zA-Z]+\*?(?:\{[^{}]*\})?", " ", full)
    plain = re.sub(r"[{}$\\]", " ", plain)
    plain = " ".join(plain.split())
    assert len(plain) > ARXIV_ABSTRACT_LIMIT, (
        f"the paper's abstract is now {len(plain)} characters, which fits "
        f"arXiv's {ARXIV_ABSTRACT_LIMIT}. Keeping a separate short abstract is "
        f"then maintaining two summaries for no reason -- decide deliberately "
        f"rather than leaving both to drift apart."
    )
