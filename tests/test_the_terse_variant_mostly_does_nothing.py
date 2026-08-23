"""How often does the terse variant actually shorten anything?

The verbosity probe is described as "response padded vs.\\ shortened", and its
terse arm is `(r.split(".")[0] or r).strip() + "."` -- the first sentence, with
its period restored. Applied to a response that is already one sentence ending
in a period, that returns the response unchanged.

Forty-nine of the fifty responses in `scaled_harness.py` are exactly that. So
the terse arm is a no-op for 49 of 50 items, and only one response --
"Entropy measures disorder. Second law says entropy always increases." -- is
genuinely truncated. The measured consequence matches: across the 26
checkpoints, |terse - control| averages 0.004 while |verbose - control|
averages 0.407, and dropping the terse arm entirely changes the verbosity bias
by under one percent.

The paper's *empirical* statement was already right -- it attributes 99% of the
verbosity bias to the padded variant and 1% to the terse one. What was wrong was
the *method* description: a reader rebuilding the prompts from "padded vs.
shortened" would construct a two-sided manipulation and not reproduce this
design. Stating it also strengthens the result rather than weakening it, since
padding is the unambiguously quality-preserving direction and is what the probe
turns out to measure.

This recomputes the count from the harness's own items and its own transform, so
that changing either -- a longer response, a different truncation rule -- fails
here instead of quietly making the paper's sentence false.
"""

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HARNESS = REPO / "paper" / "honest" / "repro" / "scaled_harness.py"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"


def _harness_source():
    if not HARNESS.exists():
        pytest.skip("[repro] scaled_harness.py not present")
    return HARNESS.read_text(encoding="utf-8", errors="replace")


def _items():
    """ITEMS as the harness defines it, without importing it (it needs torch)."""
    for node in ast.parse(_harness_source()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ITEMS":
            return ast.literal_eval(node.value)
    pytest.skip("[repro] ITEMS not found in scaled_harness.py")


def _terse():
    """The harness's own _terse, executed from its source rather than copied."""
    src = _harness_source()
    start = src.find("def _terse")
    if start < 0:
        pytest.skip("[repro] _terse not found")
    end = src.find("\n", start)          # it is written as a one-line def
    line = src[start:end if end > 0 else len(src)]
    if "return" not in line:
        pytest.skip("[repro] _terse is no longer a one-line def; update this reader")
    namespace = {}
    exec(compile(line, "terse", "exec"), namespace)
    return namespace["_terse"]


def test_the_terse_transform_is_a_no_op_for_all_but_one_item():
    items = _items()
    terse = _terse()
    unchanged = [r for _, r, _ in items if terse(r) == r]
    shortened = [r for _, r, _ in items if terse(r) != r]

    assert len(items) == 50, f"the item set is now {len(items)} items"
    assert len(shortened) == 1, (
        f"the terse variant now shortens {len(shortened)} of {len(items)} "
        f"responses, not 1. The paper states that 49 of 50 responses are a "
        f"single sentence and the transform returns them unchanged; that "
        f"sentence is now wrong."
    )
    assert len(unchanged) == 49, f"{len(unchanged)} unchanged, expected 49"


def test_the_paper_states_the_no_op_count():
    """The design fact has to be in the paper, not only in this file."""
    if not PAPER.exists():
        pytest.skip("[paper] sources not present")
    text = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    assert "$49$ of the $50$ responses are a single sentence" in text, (
        "the paper no longer states that 49 of 50 responses are a single "
        "sentence, so its description of the terse variant as truncating is "
        "unqualified again -- which is what a replicator would build from."
    )


def test_the_one_shortened_response_is_the_one_with_two_sentences():
    """Not just a count: the mechanism is that the others are single sentences."""
    items = _items()
    terse = _terse()
    for _, response, _ in items:
        body = response.rstrip(".")
        has_internal_period = "." in body
        changed = terse(response) != response
        assert changed == has_internal_period, (
            f"terse changed={changed} but internal-period={has_internal_period} "
            f"for {response!r}. The paper's explanation is that single-sentence "
            f"responses pass through unchanged; if that stops being the reason, "
            f"the explanation is wrong even where the count still holds."
        )
