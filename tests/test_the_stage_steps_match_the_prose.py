"""The stage ladder's prose numbers, against the ladder's own arrays.

`test_the_stage_ladder_recomputes.py` rebuilds the entropy paths from per-item
data and counts the seven falling transitions. It never reads the paper. The
prose, though, quotes derived quantities the JSON does not store -- the *steps
between* stages -- and one of them was wrong: OLMo-2-7B's SFT responsiveness
step is $+0.0671$, and the paper printed $+0.06$. That is the value you get by
rounding both endpoints to two decimals before subtracting ($0.21 - 0.15$), or
by truncating; it is not the step.

`test_every_number_is_accounted_for.py` could not have caught it, and the reason
is worth stating because it bounds what that sweep proves. It asks whether each
number appears somewhere in the released data at its own printed precision, and
$0.06$ does -- as an unrelated per-cell responsiveness in the same file.
Provenance is not attribution. A value that genuinely exists in the data can
still be attached to the wrong quantity, and the sweep that checks every number
exists will pass while the sentence is false.

So this file checks the attachment: each quoted step is recomputed from the
array it is a step of. The steps are the vulnerable numbers because they are the
ones no file stores -- every endpoint here is stored and therefore already
covered, while every difference between endpoints is arithmetic performed in
prose.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
MACROS = REPO / "paper" / "honest" / "macros.tex"
STAGES = REPO / "paper" / "honest" / "repro" / "results_stages_analysis.json"

# The endpoints are stored to four decimals, so a step is certain to three.
TOLERANCE = 5e-3

NUMBER = re.compile(r"[-+]?\d+\.\d+")


def _macro(name):
    """The body of one \\newcommand, by brace matching."""
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    src = MACROS.read_text(encoding="utf-8", errors="replace")
    tag = "newcommand{"
    pos = 0
    while True:
        start = src.find(tag, pos)
        if start < 0:
            pytest.skip(f"[paper] {name} not defined in macros.tex")
        close = src.find("}", start)
        found = src[start + len(tag) + 1 : close]
        i = close + 2
        depth, body_start = 1, i
        while i < len(src) and depth:
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
            i += 1
        if found == name:
            return src[body_start : i - 1]
        pos = i


def _paths():
    if not STAGES.exists():
        pytest.skip("[repro] results_stages_analysis.json not present")
    return json.loads(STAGES.read_text(encoding="utf-8", errors="replace"))["P8_paths"]


def _quoted(anchor, count):
    """The `count` numbers the prose prints starting at `anchor`."""
    body = _macro("STAGEPROSE")
    at = body.find(anchor)
    assert at >= 0, (
        f"STAGEPROSE no longer contains {anchor!r}. This file pins the numbers "
        f"in that sentence; if the sentence was rewritten, repoint the anchor."
    )
    nums = NUMBER.findall(body[at : at + 220])[:count]
    assert len(nums) == count, (
        f"expected {count} numbers after {anchor!r}, found {nums}"
    )
    return [float(n) for n in nums]


def _steps(path):
    return [b - a for a, b in zip(path, path[1:])]


def test_the_olmo7b_responsiveness_steps_are_the_steps_they_claim_to_be():
    """The defect this file was written for.

    The sentence contrasts the SFT step against the two preference steps, which
    is the evidence for "preference tuning adds little further responsiveness".
    If the SFT step is understated the contrast is understated with it, so this
    is the number carrying the claim.
    """
    resp = _paths()["OLMo-2-7B"]["resp_path"]
    dpo_step, rlvr_step, sft_step = _steps(resp)[1], _steps(resp)[2], _steps(resp)[0]
    quoted_dpo, quoted_rlvr, quoted_sft = _quoted("OLMo-7B: DPO", 3)

    for label, quoted, actual in (
        ("DPO", quoted_dpo, dpo_step),
        ("RLVR", quoted_rlvr, rlvr_step),
        ("SFT", quoted_sft, sft_step),
    ):
        assert abs(quoted - actual) <= TOLERANCE, (
            f"the paper prints {quoted:+.2f} for OLMo-2-7B's {label} "
            f"responsiveness step; the path gives {actual:+.4f}, which rounds "
            f"to {round(actual, 2):+.2f}. Rounding the endpoints before "
            f"subtracting is what produces the wrong digit."
        )


def test_the_olmo7b_entropy_drops_compare_as_the_paper_says():
    """"the SFT step falls further (0.43 vs. DPO's 0.24)" -- both are steps."""
    entropy = _paths()["OLMo-2-7B"]["entropy_path"]
    sft_drop, dpo_drop = -_steps(entropy)[0], -_steps(entropy)[1]
    quoted_sft, quoted_dpo = _quoted("the SFT step falls further", 2)

    assert abs(quoted_sft - sft_drop) <= TOLERANCE, (
        f"paper says the SFT entropy drop is {quoted_sft}; path gives {sft_drop:.4f}"
    )
    assert abs(quoted_dpo - dpo_drop) <= TOLERANCE, (
        f"paper says the DPO entropy drop is {quoted_dpo}; path gives {dpo_drop:.4f}"
    )
    assert sft_drop > dpo_drop, (
        "the paper claims the SFT step falls further than DPO's; it does not"
    )


def test_the_olmo1b_entropy_path_is_quoted_in_order():
    """Endpoints, not steps -- but the ordering is a claim of its own."""
    entropy = _paths()["OLMo-2-1B"]["entropy_path"]
    quoted = _quoted("OLMo-1B entropy", 4)

    for i, (q, a) in enumerate(zip(quoted, entropy)):
        assert abs(q - a) <= TOLERANCE, (
            f"OLMo-2-1B entropy stage {i}: paper prints {q}, path holds {a}"
        )
    assert quoted == sorted(quoted, reverse=True), (
        f"the paper prints this path as monotonically falling: {quoted}"
    )


def test_the_olmo1b_bias_jump_matches_the_path():
    """"Bias jumps with it (OLMo-1B Delta: 0.24 -> 0.80 at SFT)"."""
    bias = _paths()["OLMo-2-1B"]["bias_path"]
    quoted_base, quoted_sft = _quoted("OLMo-1B $\\Delta$", 2)

    assert abs(quoted_base - bias[0]) <= TOLERANCE, (
        f"paper prints base bias {quoted_base}; path holds {bias[0]}"
    )
    assert abs(quoted_sft - bias[1]) <= TOLERANCE, (
        f"paper prints SFT bias {quoted_sft}; path holds {bias[1]}"
    )


def test_no_quoted_step_could_have_come_from_rounded_endpoints():
    """The defect's shape, not just its one instance.

    Every step quoted in this macro is checked against the difference of the
    stored endpoints *and* against the difference of the endpoints rounded to
    two decimals first. Where those two disagree, the paper must match the
    former. This is what makes the file a guard against the mistake rather than
    against the single number that revealed it.
    """
    resp = _paths()["OLMo-2-7B"]["resp_path"]
    quoted = _quoted("OLMo-7B: DPO", 3)

    # the prose orders them DPO, RLVR, SFT -- not the path's own order
    endpoints = [(resp[1], resp[2]), (resp[2], resp[3]), (resp[0], resp[1])]
    for quoted_value, (a, b) in zip(quoted, endpoints):
        exact = b - a
        rounded_first = round(b, 2) - round(a, 2)
        if abs(round(exact, 2) - round(rounded_first, 2)) > 1e-9:
            assert abs(quoted_value - exact) <= TOLERANCE, (
                f"{quoted_value:+.2f} equals the rounded-endpoint difference "
                f"{rounded_first:+.2f} rather than the step {exact:+.4f}"
            )
