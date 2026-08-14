"""Do the separate runs measure the same quantity, so their numbers compare?

The paper puts arms beside each other constantly: sycophancy is "the largest
tuning effect of any probe on the panel", the Chinese replication's changes are
compared against the English ones, the 14B extension is called "attenuated"
relative to the panel's +0.26. Every one of those sentences assumes the arms
were measured the same way.

They are separate scripts. Each carries its own copy of the scoring code --
`token_values`, `build_prompt`, the answer-token sets -- and a copy is free to
drift. Nothing compared them. A harness that scored letters A=1 instead of A=5,
or asked for a "Rating" where the others ask for a "Score", would produce a
perfectly plausible Δ that does not belong on the same axis as the others.

What is deliberately allowed to differ: the Chinese harness translates the
prompt (that is the experiment), and probes2 freezes the scale and header to
constants because sycophancy and anchoring vary only the prefix. What must not
differ is the measure -- the token-to-value mapping -- and the skeleton of the
prompt that surrounds the varying slot.
"""

import ast
import hashlib
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Smoke harnesses run six items to check the plumbing; they are not an arm.
NOT_AN_ARM = {"harness_smoke.py"}

# The Chinese replication translates the prompt on purpose.
TRANSLATED = {"zh_harness.py"}


def _harnesses():
    found = [p for p in sorted(REPRO.glob("*harness*.py")) if p.name not in NOT_AN_ARM]
    if not found:
        pytest.skip("[repro] no harnesses present")
    return found


def _function(path, name):
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            segment = ast.get_source_segment(source, node)
            if segment:
                return re.sub(r"\s+", " ", segment).strip()
    return None


def test_every_arm_maps_answer_tokens_to_the_same_values():
    """A=5 or A=1 is the difference between a probe and its mirror image."""
    variants = {}
    for path in _harnesses():
        body = _function(path, "token_values")
        if body is None:
            continue
        variants.setdefault(hashlib.sha256(body.encode()).hexdigest()[:12], []).append(path.name)
    if not variants:
        pytest.skip("[repro] no harness defines token_values")
    assert len(variants) == 1, (
        f"the answer-token mapping differs between arms, so their Δ values are "
        f"not on the same scale: {dict(variants)}"
    )
    assert len(next(iter(variants.values()))) >= 5, (
        "fewer than five harnesses define token_values; the comparison is thin"
    )


def test_every_english_arm_builds_the_same_prompt_skeleton():
    """The varying slot varies; the scaffolding around it must not."""
    # Compare the invariant text, not the source. probes2 freezes the header to
    # the literal "Score" where the others pass it as an argument that the
    # control conditions fill with "Score" -- the emitted prompt is the same, and
    # a check that cannot see that would be reporting a difference that is not
    # there.
    REQUIRED = (
        "Evaluate the following response to the instruction",
        "### Instruction: ",
        "### Response: ",
    )
    wrong = []
    checked = 0
    for path in _harnesses():
        if path.name in TRANSLATED:
            continue
        body = _function(path, "build_prompt")
        if body is None:
            continue
        checked += 1
        for fragment in REQUIRED:
            if fragment not in body:
                wrong.append(f"{path.name}: missing {fragment!r}")
        # The header is either the slot or the panel's own value.
        if not re.search(r'### \{header\}:|### Score:', body):
            wrong.append(f"{path.name}: asks for a header other than Score")
    assert checked >= 4, f"only {checked} English harnesses define build_prompt"
    assert not wrong, (
        f"English arms build different prompts, so their scores do not belong "
        f"on the same axis: {wrong}"
    )


def test_the_translated_arm_keeps_the_same_shape():
    """Chinese text, same three fields in the same order."""
    path = REPRO / "zh_harness.py"
    if not path.exists():
        pytest.skip("[repro] the Chinese harness is not present")
    body = _function(path, "build_prompt")
    assert body, "the Chinese harness no longer defines build_prompt"
    assert body.count("###") == 3, (
        f"the Chinese prompt has {body.count('###')} labelled fields; the "
        f"English one has three, and the arms are compared directly"
    )


def test_the_frozen_scale_matches_the_panel_control():
    """probes2 freezes the scale; frozen to the wrong string it is a new probe."""
    probes2 = REPRO / "probes2_harness.py"
    scaled = REPRO / "scaled_harness.py"
    if not (probes2.exists() and scaled.exists()):
        pytest.skip("[repro] harnesses not present")
    frozen = re.search(r'^SCALE\s*=\s*"([^"]+)"', probes2.read_text(encoding="utf-8",
                       errors="replace"), re.M)
    control = re.search(r'^_NUM_SCALE\s*=\s*"([^"]+)"', scaled.read_text(encoding="utf-8",
                        errors="replace"), re.M)
    if not (frozen and control):
        pytest.skip("[repro] the scale constants are no longer named that way")
    assert frozen.group(1) == control.group(1), (
        f"sycophancy and anchoring were scored under a different rubric wording "
        f"from the panel they are compared against:\n  probes2: {frozen.group(1)}\n"
        f"  panel:   {control.group(1)}"
    )
