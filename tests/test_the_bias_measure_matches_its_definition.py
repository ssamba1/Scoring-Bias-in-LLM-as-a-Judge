r"""Do the analyses compute the bias the paper says they compute?

The paper defines its primary outcome once:

    For each model and probe we summarise bias by Delta = max_v s_v - min_v s_v

Three analysis scripts implement that independently -- analyze_peritem,
analyze_mechanism and analyze_robustness each carry their own `delta`. Three
copies of one definition is three chances for one to drift, and a drift would
not announce itself: every file would still produce plausible numbers, and only
the cross-file comparisons would quietly stop meaning the same thing.

The functions are exercised rather than read. Each is extracted from its module
and run on a small input whose max-minus-min answer is known, which
distinguishes it from the alternatives it might drift into -- a mean absolute
deviation from a control, a standard deviation, a difference from the first
variant. A textual check that the source still says "max" would pass all three.

This is the measurement-side companion to the mixed-model check: there the paper
described a model it did not fit, here it would be a measure it did not compute.
"""

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
REPRO = HONEST / "repro"

# Four copies, not three. I listed the three I had grepped for; the coverage
# check at the bottom of this file found analyze_stages carrying a fourth, which
# is exactly the drift risk the file is about.
IMPLEMENTORS = [
    "analyze_peritem.py", "analyze_mechanism.py", "analyze_robustness.py",
    "analyze_stages.py",
]


def _extract(path, name):
    """Compile just one function out of a module, without importing the module."""
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            namespace = {}
            exec(compile(ast.Module([node], []), str(path), "exec"), namespace)
            return namespace[name]
    return None


@pytest.mark.parametrize("script", IMPLEMENTORS)
def test_each_delta_is_the_spread_of_the_variant_means(script):
    path = REPRO / script
    if not path.exists():
        pytest.skip(f"[{script}] not present")
    delta = _extract(path, "delta")
    assert delta is not None, f"{script} no longer defines delta(); the measure moved"

    # max - min = 3.0. A mean deviation from the first variant gives 1.5, a
    # population standard deviation about 1.25, a last-minus-first 1.0.
    variants = {"control": 1.0, "reversed": 4.0, "random": 2.0}
    result = delta(dict(variants))
    assert abs(result - 3.0) < 1e-9, (
        f"{script}: delta of {variants} is {result}, but the paper defines the "
        f"bias as max minus min, which is 3.0"
    )

    # Order must not matter, and a single variant has no spread to speak of.
    assert abs(delta({"b": 4.0, "a": 1.0, "c": 2.0}) - 3.0) < 1e-9, (
        f"{script}: delta depends on the order of the variants"
    )
    assert abs(delta({"only": 2.5})) < 1e-9, f"{script}: a lone variant has a non-zero spread"


def test_the_paper_still_states_the_definition():
    """If the definition changes, these checks must be revisited, not left."""
    tex = HONEST / "scoring_bias_v2.tex"
    if not tex.exists():
        pytest.skip("[paper] source not present")
    text = tex.read_text(encoding="utf-8", errors="replace")
    assert re.search(r"\\Delta=\\max_v[^$]*-\\min_v", text), (
        "the paper no longer defines Delta as max minus min over variants; the "
        "implementations above are checked against that definition"
    )


def test_every_implementation_is_covered():
    """Vacuity guard: a fourth copy of the measure must not appear unchecked."""
    found = [
        path.name
        for path in sorted(REPRO.glob("analyze_*.py"))
        if re.search(r"^def delta\b", path.read_text(encoding="utf-8", errors="replace"), re.M)
    ]
    assert set(found) == set(IMPLEMENTORS), (
        f"the scripts defining delta() are {found}, but this test checks "
        f"{IMPLEMENTORS}. A new copy of the bias measure is a new chance for it "
        f"to disagree with the others."
    )
