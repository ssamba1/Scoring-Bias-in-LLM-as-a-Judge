"""Does every float carry a caption, and does anything point at it?

The checklist ticks "Every figure and table has a caption and is referenced in
the text". LaTeX cannot check either half: an uncaptioned float typesets
silently, and a figure nobody references is invisible to the build and obvious
to a referee. The claim was ticked by eye and was not quite true -- the Notation
glossary was a `table` float carrying neither caption nor label.

One trap, worth stating because the first version of this sweep fell into it and
reported a referenced figure as unreferenced. Comments cannot be stripped with
`%.*`: `\\%` is an escaped percent sign, and macros.tex writes each definition on
one long line, so the `100\\%` inside the patching prose swallowed the rest of
the line -- including the `\\ref{fig:patch}` that followed it. Strip only a `%`
not preceded by a backslash.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
SOURCES = ("scoring_bias_v2.tex", "macros.tex")

FLOAT = re.compile(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", re.S)
LABEL = re.compile(r"\\label\{((?:fig|tab):[^}]+)\}")
REF = re.compile(r"\\(?:ref|autoref|cref|Cref)\{([^}]*)\}")


def _source():
    text = ""
    for name in SOURCES:
        path = HONEST / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace")
    if not text:
        pytest.skip("[paper] no LaTeX sources present")
    return re.sub(r"(?<!\\)%.*", " ", text)


def _labels(text):
    return set(LABEL.findall(text))


def _refs(text):
    out = set()
    for match in REF.finditer(text):
        out |= {part.strip() for part in match.group(1).split(",")}
    return out


def test_every_float_carries_a_caption():
    uncaptioned = [
        kind for kind, body in FLOAT.findall(_source()) if "\\caption" not in body
    ]
    assert not uncaptioned, (
        f"{len(uncaptioned)} float(s) of kind {sorted(set(uncaptioned))} carry no "
        f"caption. A float without one is numbered but unexplained, and the "
        f"submission checklist claims every one has a caption. If the content is "
        f"a section's body rather than a float, make it a plain block."
    )


def test_every_labelled_float_is_referenced():
    text = _source()
    orphans = sorted(_labels(text) - _refs(text))
    assert not orphans, (
        f"floats defined but never pointed at: {orphans}. LaTeX typesets these "
        f"without complaint; a referee notices immediately."
    )


def test_no_float_reference_dangles():
    text = _source()
    labels, refs = _labels(text), _refs(text)
    dangling = sorted(
        ref for ref in refs if ref.startswith(("fig:", "tab:")) and ref not in labels
    )
    assert not dangling, f"references to floats that do not exist: {dangling}"


def test_the_sweep_is_actually_reading_floats():
    """Vacuity guard, and a regression test for the escaped-percent trap.

    If comment stripping breaks again the reference set collapses and the
    orphan check starts failing loudly rather than passing quietly -- but the
    counts here catch it first.
    """
    text = _source()
    floats = FLOAT.findall(text)
    assert len(floats) >= 12, f"only {len(floats)} floats parsed from the paper"
    assert len(_labels(text)) >= 12, "float labels no longer parse"
    assert len(_refs(text)) >= 20, (
        "suspiciously few references parsed; check that comment stripping is not "
        "eating lines at an escaped percent sign"
    )
