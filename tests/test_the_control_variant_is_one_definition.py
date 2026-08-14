"""Do all the analyzers agree on which variant is the control?

Entropy, responsiveness and every score shift in this paper are measured
relative to "the control condition". Which variant that is -- `numeric` for
score ID, `none` for authority, `control` for rubric order -- is written out as
a CONTROL dict, and five analyzers each carry their own copy of it:
analyze_peritem, analyze_mechanism, analyze_robustness, analyze_stages,
analyze_closed.

Copies drift. In the sibling paper a denial regex was duplicated in two files,
one copy was fixed and the other was not, and the reported rate was wrong by
fourteen points for months. Here a single disagreeing entry would mean the
decisiveness figure and the bias figure were computed against different
baselines, and both would still look entirely ordinary.

They agree today, so this pins the agreement rather than the values -- the map
is derived from the analyzers themselves, so changing the control deliberately
in all five still passes, while changing it in four does not.
"""

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _control_maps():
    """filename -> the CONTROL dict it defines."""
    maps = {}
    for path in sorted(REPRO.glob("analyze_*.py")):
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "CONTROL" not in names:
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
            if isinstance(value, dict) and value:
                maps[path.name] = value
    if not maps:
        pytest.skip("[repro] no analyzer defines CONTROL")
    return maps


def test_every_analyzer_uses_the_same_control_variant():
    maps = _control_maps()
    assert len(maps) >= 4, (
        f"only {sorted(maps)} define CONTROL; the comparison is too thin to "
        f"catch a drifting copy"
    )
    reference_name, reference = sorted(maps.items())[0]
    disagreeing = []
    for name, mapping in sorted(maps.items()):
        if mapping != reference:
            differences = {
                probe: (reference.get(probe), mapping.get(probe))
                for probe in set(reference) | set(mapping)
                if reference.get(probe) != mapping.get(probe)
            }
            disagreeing.append(f"{name} vs {reference_name}: {differences}")
    assert not disagreeing, (
        f"the analyzers disagree about which variant is the control, so "
        f"quantities measured against it are on different baselines: "
        f"{disagreeing}"
    )


def test_the_harnesses_score_that_variant_first():
    """The control must exist as a variant in the data, under that exact name."""
    maps = _control_maps()
    control = sorted(maps.values(), key=lambda m: sorted(m.items()))[0]
    harness = REPRO / "scaled_harness.py"
    if not harness.exists():
        pytest.skip("[repro] the main harness is not present")
    source = harness.read_text(encoding="utf-8", errors="replace")
    missing = []
    for probe, variant in sorted(control.items()):
        # the harness writes each probe's variants as "name": (...)
        block = re.search(rf'"{probe}":\s*\{{(.*?)\n\s*\}}', source, re.S)
        if not block:
            continue
        if f'"{variant}"' not in block.group(1):
            missing.append(
                f"{probe}: the analyzers use {variant!r}, the harness has no such variant"
            )
    assert not missing, (
        f"the analyzers measure against a variant the harness never produced: "
        f"{missing}"
    )
