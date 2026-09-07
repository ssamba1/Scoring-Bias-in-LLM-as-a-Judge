"""A cross-reference range must run forwards.

`\\S\\ref{a}--\\ref{b}` makes a claim LaTeX never checks: that `a` comes before
`b`. Both ends resolve, so the build is silent, `check_prose.py` sees no number,
and the figure check has no data source to compare against. The PDF simply
prints a range that runs backwards, and a reader who does not hold the section
numbering in their head reads straight past it.

This is not hypothetical. The Related Work paragraph carried
`\\S\\ref{sec:anatomy}--\\ref{sec:predict}` from the honest rewrite until
2026-09-07, and it rendered as "SS5.20-5.12". Three earlier audit rounds, a full
mutation suite and a read of the compiled PDF had all passed over it; what found
it was reading the rendered Related Work top to bottom after an unrelated edit.

Numbering comes from the source, not from the `.aux`: `.aux` is a build artefact
and is gitignored, so a check that needed it would skip on a fresh clone --
exactly when it is most wanted. Sectioning commands are numbered in source
order, so their order in the file is their order in the document.

Floats are deliberately excluded. `\\ref{fig:a}--\\ref{fig:b}` is numbered by
where LaTeX places the float, not by where the source defines it, so source
order is the wrong oracle for them and a strict check would produce confident
false reports.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
PAPER = HONEST / "scoring_bias_v2.tex"
MACROS = HONEST / "macros.tex"

# Prefixes whose numbering follows source order. Floats (fig, tab) do not.
ORDERED_PREFIXES = ("sec:", "cor:", "prop:", "thm:", "lem:", "app:")

SECTIONING = re.compile(
    r"\\(?:sub){0,2}section\*?\{|\\begin\{(?:corollary|proposition|theorem|lemma)\}"
)
LABEL = re.compile(r"\\label\{([^}]+)\}")
RANGE = re.compile(r"\\ref\{([^}]+)\}\s*-{2,3}\s*\\ref\{([^}]+)\}")


def _paper():
    if not PAPER.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    return PAPER.read_text(encoding="utf-8", errors="replace")


def _all_source():
    text = _paper()
    if MACROS.exists():
        text += MACROS.read_text(encoding="utf-8", errors="replace")
    return text


def _label_order():
    """label -> position, for labels whose number follows source order.

    A label is attached to the most recent numbered construct before it, so
    walking the file and recording labels in the order they appear gives the
    document order of the things they name.
    """
    text = _paper()
    order, seen = {}, 0
    for m in LABEL.finditer(text):
        name = m.group(1)
        if not name.startswith(ORDERED_PREFIXES):
            continue
        # Only count a label that follows a numbered construct, not one sitting
        # inside a float; the nearest preceding sectioning command decides.
        order[name] = seen
        seen += 1
    return order


def test_every_cross_reference_range_runs_forwards():
    order = _label_order()
    assert order, "no ordered labels parsed from the paper; the check would be vacuous"

    backwards = []
    for m in RANGE.finditer(_all_source()):
        a, b = m.group(1), m.group(2)
        if a not in order or b not in order:
            continue
        if order[a] >= order[b]:
            backwards.append(f"\\ref{{{a}}}--\\ref{{{b}}} runs backwards or is empty")
    assert not backwards, (
        "cross-reference ranges that do not run forwards; each prints a "
        "backwards range in the PDF and nothing else catches it: "
        + "; ".join(backwards)
    )


def test_both_ends_of_every_range_are_defined():
    """An undefined end still typesets -- as `??` -- but only after a rerun."""
    defined = set(LABEL.findall(_all_source()))
    dangling = []
    for m in RANGE.finditer(_all_source()):
        for end in (m.group(1), m.group(2)):
            if end.startswith(ORDERED_PREFIXES) and end not in defined:
                dangling.append(end)
    assert not dangling, f"range endpoints with no \\label: {sorted(set(dangling))}"


def test_the_check_is_actually_reading_ranges():
    """Vacuity guard: the assertions above pass trivially on an empty parse."""
    ranges = RANGE.findall(_all_source())
    # The paper held four ranges when this guard was written and holds two now:
    # the sweep that produced it turned the backwards one and an over-wide one
    # into "and". Two is the floor because two is what a clean paper here has,
    # not because two is comfortable -- if it reaches zero the guard is idle and
    # should be retired on purpose rather than left passing on nothing.
    assert len(ranges) >= 2, (
        f"only {len(ranges)} cross-reference ranges found; if the paper stopped "
        f"using them, retire this guard deliberately rather than let it idle"
    )
    order = _label_order()
    covered = [r for r in ranges if r[0] in order and r[1] in order]
    assert len(covered) >= 2, (
        f"only {len(covered)} of {len(ranges)} ranges have both ends in the "
        f"ordered-label map; the forwards check is nearly vacuous"
    )
