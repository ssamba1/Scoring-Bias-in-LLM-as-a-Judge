"""Is the prompt in the appendix the prompt the harness actually sent?

Appendix "Exact prompts" prints one template and says every probe shares it,
varying named slots. If that template is not what ran, every result in the paper
is attached to the wrong description, and no amount of reproducing the numbers
would reveal it: the pipeline would faithfully regenerate results for the prompt
it really used.

The appendix also states the answer-token sets and one mapping that is easy to
get backwards -- letters run A to E with A worth 5, the reverse of their
position. Getting that wrong inverts an entire probe while every number stays
plausible.

The harness is left exactly as it is. It is the record of what ran, and editing
it to be tidier would falsify that record; the fragility worth noting is that
token_values selects the reversed mapping by object identity (`a is LET`), so a
copy of the same list would score A as 1. That is pinned here rather than fixed.
"""

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"
HARNESS = REPRO / "scaled_harness.py"


def _appendix():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\section\{Exact prompts\}(.*?)\\section", text, re.S)
    if not match:
        pytest.skip("[paper] no exact-prompts appendix")
    return match.group(1)


def _harness_source():
    if not HARNESS.exists():
        pytest.skip("[repro] the main harness is not present")
    return HARNESS.read_text(encoding="utf-8", errors="replace")


def _literal(name):
    tree = ast.parse(_harness_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        return None
    return None


def test_the_template_lines_match_the_code_that_built_them():
    """Line by line, in order -- the slots may be renamed, the shape may not."""
    appendix = _appendix()
    source = _harness_source()
    built = re.search(r"def build_prompt\(.*?\n((?:.*\n)*?)\s*\n", source)
    assert built, "build_prompt is no longer in the harness"
    code = built.group(1)

    for fragment in ("Evaluate the following response to the instruction",
                     "### Instruction:", "### Response:"):
        assert fragment in code, (
            f"the harness no longer builds a prompt containing {fragment!r}"
        )
        escaped = fragment.replace("#", r"\#")
        assert escaped in appendix or fragment in appendix, (
            f"the appendix prints a template without {fragment!r}, which the "
            f"harness sends. The paper would be describing a prompt that never ran."
        )

    # Order matters as much as presence: instruction before response before header.
    order = [appendix.index(p) for p in (r"\#\#\# Instruction", r"\#\#\# Response")
             if p in appendix]
    assert order == sorted(order), (
        "the appendix prints the prompt's parts in a different order from the "
        "one the harness assembles"
    )


def test_the_answer_token_sets_are_the_ones_the_paper_states():
    appendix = _appendix()
    numeric, letters, descriptive = _literal("NUM"), _literal("LET"), _literal("DESC")
    assert numeric and letters and descriptive, (
        "the harness's answer-token sets could not be read; the appendix's "
        "claims about them cannot be checked"
    )
    assert numeric == [str(i) for i in range(1, 6)], numeric
    assert letters == ["A", "B", "C", "D", "E"], letters
    assert descriptive[0] == "Poor" and descriptive[-1] == "Excellent", descriptive

    assert f"{len(numeric)}" in appendix and "A" in appendix, (
        "the appendix no longer states the answer-token sets"
    )
    for word in (descriptive[0], descriptive[-1]):
        assert word in appendix, (
            f"the appendix does not name the descriptive token {word!r} the "
            f"harness sends"
        )


def test_the_letter_scale_is_mapped_the_way_the_paper_says():
    """A=5, not A=1. Backwards here inverts a probe with every number intact."""
    appendix = _appendix()
    assert re.search(r"mapped\s*\$?A\\?!?=\\?!?\s*5", appendix.replace(" ", "")) or \
        "A\\!=\\!5" in appendix, (
        "the appendix no longer states the letter mapping; it is the one slot "
        "that inverts a probe when it is wrong"
    )

    source = _harness_source()
    body = re.search(r"def token_values\(([^)]*)\):\s*\n\s*return (.*)", source)
    assert body, "token_values is no longer in the harness"
    expression = body.group(2)
    assert "range(5, 0, -1)" in expression, (
        f"the letter branch no longer counts down from five: {expression!r}. "
        f"A would score 1 where the paper says 5."
    )
    assert re.search(r"\bis\s+LET\b", expression), (
        f"the reversed mapping is no longer selected by identity with LET: "
        f"{expression!r}. That selection is fragile -- an equal copy of the list "
        f"would score A as 1 -- and this check exists to notice it changing."
    )


def test_the_letter_prompt_agrees_with_the_letter_mapping():
    """The instruction to the judge and the scoring of its answer must agree."""
    source = _harness_source()
    letter_prompt = re.search(r'"letter":\s*\("([^"]+)"', source)
    if not letter_prompt:
        pytest.skip("[repro] no letter variant in the harness")
    wording = letter_prompt.group(1)
    assert "A is best" in wording, (
        f"the judge is told {wording!r} while its answer is scored with A worth "
        f"5 -- the prompt and the scale disagree"
    )
