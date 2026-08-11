r"""Does each figure and table carry the number its label claims?

The build reports "0 undefined references", which only proves every \ref found a
\label. A \label placed outside its float, or before the \caption, still
resolves -- and silently numbers the wrong object, so a sentence sends the
reader to a different figure. Nothing in the build log distinguishes that from
correct placement.

This compares the numbers LaTeX actually assigned, read out of the .aux, against
the order the float environments appear in the source. The Nth figure
environment must own the label numbered N.

It is a placement check, not a content check: `check_figures.py` verifies that
each figure shows what the data produces, and this verifies that the paper
points at the one it means.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
TEX = HONEST / "scoring_bias_v2.tex"
AUX = HONEST / "scoring_bias_v2.aux"


def _sources():
    if not TEX.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    if not AUX.exists():
        pytest.skip("[aux] scoring_bias_v2.aux not present; compile the paper first")
    return (
        TEX.read_text(encoding="utf-8", errors="replace"),
        AUX.read_text(encoding="utf-8", errors="replace"),
    )


def _assigned(aux):
    """label -> the number LaTeX gave it."""
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux)
    }


def _floats(tex, env):
    """(labels, caption) for each float environment, in source order."""
    out = []
    pattern = re.compile(
        r"\\begin\{" + env + r"\*?\}(.*?)\\end\{" + env + r"\*?\}", re.S
    )
    for match in pattern.finditer(tex):
        body = match.group(1)
        labels = re.findall(r"\\label\{([^}]+)\}", body)
        caption = re.search(r"\\caption\{(.{0,80})", body, re.S)
        out.append((labels, " ".join(caption.group(1).split()) if caption else "(no caption)"))
    return out


@pytest.mark.parametrize("env", ["figure", "table"])
def test_each_label_carries_its_own_floats_number(env):
    tex, aux = _sources()
    assigned = _assigned(aux)
    floats = _floats(tex, env)
    if not floats:
        pytest.skip(f"[{env}] none in the paper")

    wrong = []
    for position, (labels, caption) in enumerate(floats, start=1):
        for label in labels:
            number = assigned.get(label)
            if number is None:
                continue  # a label LaTeX did not number is caught by the build
            if number != str(position):
                wrong.append(
                    f"{label} is the {position}{'st' if position == 1 else 'th'} "
                    f"{env} in the source but is numbered {number} "
                    f"(caption: {caption[:60]})"
                )
    assert not wrong, (
        f"{len(wrong)} {env} label(s) do not number the float they sit in, so a "
        f"reference sends the reader elsewhere: {wrong}"
    )


def test_the_floats_are_actually_found():
    """Vacuity guard: an environment rename would leave nothing compared."""
    tex, aux = _sources()
    figures = _floats(tex, "figure")
    assert len(figures) >= 8, (
        f"only {len(figures)} figure environments parsed; the paper includes ten, "
        f"so this check is comparing far less than it appears to"
    )
    assert _assigned(aux), "no \\newlabel entries parsed from the .aux"


def test_every_labelled_float_has_a_caption():
    """A float labelled but uncaptioned is referenced by number and never explained."""
    tex, _ = _sources()
    bare = []
    for env in ("figure", "table"):
        for labels, caption in _floats(tex, env):
            if labels and caption == "(no caption)":
                bare.append(f"{env}: {labels}")
    assert not bare, f"labelled float(s) with no caption: {bare}"
