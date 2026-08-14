"""Is the item panel the one the paper describes, everywhere it is used?

"Every model scores the same 50 mid-quality items (10 in each of 5 domains)
under every variant." That sentence carries more weight than its length
suggests. Balance across domains is what licenses the not-domain-specific
claim; identity across harnesses is what licenses comparing a 14B checkpoint
against a 0.5B one at all; and 50 is the denominator under most per-item
statistics in the paper.

None of it was checked. The panel is a literal in each harness, copied between
them, and a copy that drifted would leave every downstream comparison quietly
comparing different things while every number still recomputed cleanly from the
raw runs.

The harnesses also truncate the panel to six items under a smoke flag. A smoke
run whose output reached the release would look like a real run in every
respect except the denominator, so the released cells are checked to be
full-sized rather than trusting that the flag was off.
"""

import ast
import collections
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

PANEL_SIZE = 50
DOMAINS = 5
PER_DOMAIN = 10


def _items(path):
    """The first ITEMS literal in a harness -- later ones are smoke truncations."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "ITEMS" for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
            if isinstance(value, list) and value:
                return value
    return None


def _domain_tagged_panels():
    """Harnesses declaring a domain-tagged panel, by file name."""
    panels = {}
    for path in sorted(REPRO.glob("*harness*.py")):
        items = _items(path)
        if not items:
            continue
        if all(isinstance(i, (list, tuple)) and len(i) >= 3 and isinstance(i[2], str)
               for i in items) and len({i[2] for i in items}) > 1:
            panels[path.name] = items
    if not panels:
        pytest.skip("[repro] no domain-tagged item panels found")
    return panels


def test_the_main_panel_is_balanced_across_domains():
    panels = _domain_tagged_panels()
    assert "scaled_harness.py" in panels, (
        "the main panel harness declares no domain-tagged items; the paper's "
        "'10 in each of 5 domains' would have nothing behind it"
    )
    items = panels["scaled_harness.py"]
    counts = collections.Counter(i[2] for i in items)
    assert len(items) == PANEL_SIZE, (
        f"the panel has {len(items)} items, the paper says {PANEL_SIZE}"
    )
    assert len(counts) == DOMAINS, (
        f"the panel spans {len(counts)} domains, the paper says {DOMAINS}"
    )
    unbalanced = {d: n for d, n in counts.items() if n != PER_DOMAIN}
    assert not unbalanced, (
        f"the paper says 10 items in each domain; {unbalanced} say otherwise. "
        f"Domain balance is what licenses reading the per-domain comparison as "
        f"a comparison of domains rather than of sample sizes."
    )


def test_every_panel_of_this_size_is_the_same_panel():
    """"The same 50 items" -- across harnesses, not only within one.

    The panel is a copied literal. Comparing checkpoints run on quietly
    different items is the failure this catches, and it is invisible
    downstream: every number would still recompute from its own raw file.
    """
    panels = {name: p for name, p in _domain_tagged_panels().items()
              if len(p) == PANEL_SIZE}
    assert "scaled_harness.py" in panels
    reference = [(i[0], i[2]) for i in panels["scaled_harness.py"]]
    for name, items in sorted(panels.items()):
        mine = [(i[0], i[2]) for i in items]
        if mine == reference:
            continue
        differing = [a for a, b in zip(mine, reference) if a != b][:3]
        assert mine == reference, (
            f"{name} declares a different 50-item panel from scaled_harness.py "
            f"(first differences: {differing}); the paper says every model "
            f"scores the same items"
        )


def _is_per_item_key(key):
    """Does this key name a vector with one entry per scored item?

    Matching the literal key "per_item" and nothing else made this check skip
    the whole sampled harness -- it names its vectors ev_per_item and
    sampled_per_item -- and ignore per_item_argmax and per_item_entropy
    everywhere, which is 780 unchecked vectors in results_scaled.json alone.
    The harnesses agree on the phrase and disagree on the affix, so the phrase
    is what to match, as a whole underscore-separated component so that a
    future per_items_dropped counter is not mistaken for a score vector.
    """
    parts = str(key).split("_")
    return any(a == "per" and b == "item" for a, b in zip(parts, parts[1:]))


def _per_cell_lengths(blob):
    """(path, len) for every per-item score vector in a released raw file."""
    found = []

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                if _is_per_item_key(key) and isinstance(value, list):
                    found.append((f"{path}/{key}", len(value)))
                else:
                    walk(value, path + "/" + str(key))
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    walk(blob, "")
    return found


RAW_WITH_PANEL = sorted(
    p.name for p in REPRO.glob("results_*.json")
    if not p.name.endswith("_analysis.json")
)


@pytest.mark.parametrize("name", RAW_WITH_PANEL)
def test_no_released_cell_was_scored_on_a_truncated_panel(name):
    """The harnesses truncate the panel to six items under a smoke flag.

    A smoke run looks like a real run in every respect except the denominator,
    so this reads the released cells rather than trusting the flag was off. The
    declared n_items is the file's own claim about its panel; every per-item
    vector in it has to be that long, which is the same check the analyzers
    would need before dividing by 50 and never make.

    test_released_data_is_well_formed compares the *modal* array length against
    the declared count, which passes if half the cells are short. This compares
    every cell, which is the difference between catching a truncated write and
    catching a truncated run.
    """
    path = REPRO / name
    blob = json.loads(path.read_text())
    cells = _per_cell_lengths(blob) if isinstance(blob, dict) else []
    if not cells:
        pytest.skip(f"[{name}] records no per-item vectors")

    declared = blob.get("n_items")
    if not isinstance(declared, int):
        # results_closed.json is the one that matters here, and raggedness in it
        # is already caught by test_arrays_all_have_the_same_length, which
        # compares cells against their modal length. Without a declared size
        # that is the strongest available check, so this defers to it rather
        # than restating it.
        pytest.skip(f"[{name}] declares no panel size; raggedness is covered by "
                    f"test_arrays_all_have_the_same_length")

    short = sorted({n for _, n in cells if n != declared})
    assert not short, (
        f"{name} declares {declared} items; {sum(1 for _, n in cells if n != declared)} "
        f"of its {len(cells)} cells hold {short} scores instead -- a truncated "
        f"run reached the release, and every per-item statistic over it divides "
        f"by the wrong denominator"
    )
    if declared == PANEL_SIZE:
        assert len(cells) > 1, (
            f"{name} exposes one cell, so this check cannot tell a full run "
            f"from a truncated one"
        )


def test_the_paper_still_describes_this_panel():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    claim = "same 50 mid-quality items (10 in each of 5 domains)"
    assert claim in text, (
        f"the paper no longer states {claim!r}; update the constants in this "
        f"check to whatever it states now, rather than leaving the panel "
        f"checked against a description the paper has abandoned"
    )
