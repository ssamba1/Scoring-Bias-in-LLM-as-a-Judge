"""Is the causal test's sample size a count of the thing the paper says it is?

The patching section reported "n=35 items with a non-trivial base-instruct score
gap". The panel holds 20 items. The harness loops over items and rubric orders
together and increments its counter inside both loops, so 35 is a count of
item x rubric-order pairs -- 20 items under each of two orders gives 40
candidates, of which 35 cleared the gap threshold.

The number was right and its unit was wrong, which is the harder version to
notice. Nothing in the release contradicted it: n_items_used is 35, the figure
plots 35 measurements, and every check that compared the paper against the data
compared 35 to 35. Only the arithmetic gives it away -- 35 items cannot come out
of a 20-item panel -- and no check was doing arithmetic on it.

It matters because it overstates independence. Thirty-five items reads as
thirty-five separate pieces of evidence; thirty-five pairs drawn from twenty
items are correlated within item, and a reader assessing the causal claim needs
to know which they are looking at.

So: the used count must be reachable as items x variants and must not exceed it,
and the paper must not call it a count of items.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"

PATCH_RUNS = ["patch_results.json", "patch_results_qwen05.json"]


def _run(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


@pytest.mark.parametrize("name", PATCH_RUNS)
def test_the_used_count_cannot_exceed_the_candidates(name):
    run = _run(name)
    used = run.get("n_items_used")
    items = run.get("n_items")
    variants = run.get("variants")
    if used is None or items is None or not isinstance(variants, list):
        pytest.skip(f"[repro] {name} declares no patched-unit counts")

    candidates = items * len(variants)
    assert used <= candidates, (
        f"{name} patched {used} units from {items} items under "
        f"{len(variants)} variants, which allows at most {candidates}"
    )
    assert used > items or used <= items, "unreachable; keeps the comparison explicit"


@pytest.mark.parametrize("name", PATCH_RUNS)
def test_a_used_count_above_the_item_count_is_pairs(name):
    """If more units were patched than items exist, they are pairs."""
    run = _run(name)
    used, items = run.get("n_items_used"), run.get("n_items")
    variants = run.get("variants")
    if used is None or items is None or not isinstance(variants, list):
        pytest.skip(f"[repro] {name} declares no patched-unit counts")
    if used <= items:
        pytest.skip(f"[{name}] {used} units from {items} items; no conflation possible")

    assert len(variants) > 1, (
        f"{name} reports {used} units from {items} items with a single variant, "
        f"which cannot happen"
    )


def test_the_paper_does_not_call_the_pairs_items():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    if "PATCHPROSE" not in text:
        pytest.skip("[paper] no patching prose")

    run = _run("patch_results.json")
    used, items = run.get("n_items_used"), run.get("n_items")
    if used is None or items is None or used <= items:
        pytest.skip("[repro] no pair/item distinction to describe")

    offending = re.search(rf"\$n={used}\$ items\b", text)
    assert not offending, (
        f"the paper says {offending.group(0) if offending else ''}, but the "
        f"panel holds {items} items; {used} is a count of item x variant pairs "
        f"and calling it items overstates how independent the sample is"
    )
    assert "pairs" in text, (
        "the patching prose no longer describes its unit as pairs; with "
        f"{used} measurements from {items} items, the unit is the thing a "
        f"reader needs in order to weigh the causal claim"
    )
