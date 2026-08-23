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


# The English runs do not each have their own items -- scaled, stage, q14b and
# q32b share one list, which is why the paper can say "this item set" and mean
# all of them. The Chinese replication has its own translated list with the same
# single-sentence property and an ideographic-period split.
ENGLISH_HARNESSES = ("scaled_harness.py", "stage_harness.py",
                     "q14b_harness.py", "q32b_harness.py")
ZH_HARNESS = "zh_harness.py"


def _items_from(name):
    path = REPO / "paper" / "honest" / "repro" / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    for node in ast.parse(path.read_text(encoding="utf-8", errors="replace")).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ITEMS":
            return ast.literal_eval(node.value)
    pytest.skip(f"[repro] no ITEMS in {name}")


def _terse_from(name):
    path = REPO / "paper" / "honest" / "repro" / name
    src = path.read_text(encoding="utf-8", errors="replace")
    start = src.find("def _terse")
    if start < 0:
        pytest.skip(f"[repro] no _terse in {name}")
    end = src.find(chr(10), start)
    ns = {}
    exec(compile(src[start:end if end > 0 else len(src)], "t", "exec"), ns)
    return ns["_terse"]


def test_the_english_runs_share_the_one_item_set():
    """"This item set" in the paper has to mean all of them, or it means less."""
    sets = {name: _items_from(name) for name in ENGLISH_HARNESSES}
    first = sets[ENGLISH_HARNESSES[0]]
    differing = [n for n, v in sets.items() if v != first]
    assert not differing, (
        f"these harnesses no longer share the panel's item set: {differing}. "
        f"The paper's terse-variant caveat is written as a property of one item "
        f"set; if they diverge it no longer covers every English run."
    )


def test_the_chinese_items_have_the_same_property():
    """Verbosity is the Chinese section's largest effect, so this matters there."""
    items = _items_from(ZH_HARNESS)
    terse = _terse_from(ZH_HARNESS)
    responses = [t[1] for t in items]
    shortened = [r for r in responses if terse(r) != r]
    assert len(responses) == 50, f"the Chinese item set is now {len(responses)} items"
    assert len(shortened) == 1, (
        f"the Chinese terse arm now shortens {len(shortened)} of "
        f"{len(responses)} responses, not 1; the paper states 49 of 50 are "
        f"unchanged there too"
    )


def test_the_chinese_terse_splits_on_the_ideographic_period():
    """An ASCII split here would be a no-op for every item, not 49 of 50."""
    path = REPO / "paper" / "honest" / "repro" / ZH_HARNESS
    src = path.read_text(encoding="utf-8", errors="replace")
    start = src.find("def _terse")
    line = src[start:src.find(chr(10), start)]
    ideographic_period = chr(0x3002)
    assert ideographic_period in line, (
        f"the Chinese terse transform does not split on the ideographic period: "
        f"{line.strip()!r}. Splitting on an ASCII period would make it a no-op "
        f"for all 50 items, and the paper's 49-of-50 statement would be wrong."
    )
