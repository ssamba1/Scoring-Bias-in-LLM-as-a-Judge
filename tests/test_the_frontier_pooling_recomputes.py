"""Does adding the frontier judges strengthen the law, as P20 reports?

The frontier result is the paper's sharpest test of the confidence-bias
relation: three deployed judges scored through API logprobs, pooled with the
open panel to give rho = -0.45 over 145 cells, against -0.41 on the open cells
alone. "Pooling them strengthens the relation" is the claim, and the comparison
between those two numbers is the whole of it.

Neither was recomputed. The tests touching this release check the compute
disclosure, the ethics statement, that no cell is missing a variant -- all
worth having, none of them the correlation.

Recomputed here from both raw runs at once, which is what the claim requires:
the 130 open cells from results_scaled.json and the 15 frontier cells from
results_closed.json, entropy as the mean of the variants' mean_entropy and bias
as their max-min spread, then average-rank Spearman over each set. It reproduces
-0.4135 against a stored -0.413 for the open cells and -0.4522 against -0.452
pooled.

The excluded judge needs no special handling here and gets none. qwen-2.5-72b
appears in the raw file with no usable cells, so a reconstruction that simply
takes what is there arrives at 15 frontier cells without knowing it was
excluded -- and the count is asserted, so a judge that silently gains or loses
cells is visible rather than absorbed into the correlation.
"""

import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PROBES = ["rubric_order", "score_id", "authority", "verbosity", "reference_answer"]


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = shared
        i = j + 1
    return ranks


def _pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    if den == 0:
        pytest.skip("[repro] degenerate spread")
    return num / den


def _cells_from(variants_by_probe):
    """(entropy, bias) for each probe whose variants carry both fields."""
    out = []
    for probe in PROBES:
        variants = variants_by_probe.get(probe)
        if not isinstance(variants, dict):
            continue
        usable = [v for v in variants.values()
                  if isinstance(v, dict) and "mean" in v and "mean_entropy" in v]
        if len(usable) < 2:
            continue
        means = [v["mean"] for v in usable]
        out.append((statistics.mean(v["mean_entropy"] for v in usable),
                    max(means) - min(means)))
    return out


def _open_cells():
    cells = []
    for _family, arms in _load("results_scaled.json")["results"].items():
        for checkpoint in ("base", "instruct"):
            cell = arms.get(checkpoint)
            if isinstance(cell, dict):
                cells.extend(_cells_from(cell))
    if not cells:
        pytest.skip("[repro] no open cells")
    return cells


def _frontier_cells():
    results = _load("results_closed.json").get("results", {})
    cells = []
    for _judge, record in results.items():
        if isinstance(record, dict):
            cells.extend(_cells_from(record.get("instruct", record)))
    if not cells:
        pytest.skip("[repro] no frontier cells")
    return cells


def test_the_open_only_correlation_recomputes():
    stored = _load("results_closed_analysis.json").get("pooled")
    if not stored:
        pytest.skip("[repro] no pooled record")
    cells = _open_cells()
    rho = _pearson(_average_ranks([c[0] for c in cells]),
                   _average_ranks([c[1] for c in cells]))
    assert abs(rho - stored["open_only_rho"]) <= 0.0015, (
        f"the release reports {stored['open_only_rho']} on the open cells; "
        f"recomputing gives {rho:.4f}"
    )


def test_the_pooled_correlation_recomputes():
    stored = _load("results_closed_analysis.json").get("pooled")
    if not stored:
        pytest.skip("[repro] no pooled record")
    cells = _open_cells() + _frontier_cells()

    assert len(cells) == stored["n_pooled"], (
        f"the release pools {stored['n_pooled']} cells; the two raw runs give "
        f"{len(cells)}. A judge gaining or losing cells would otherwise be "
        f"absorbed into the correlation."
    )
    rho = _pearson(_average_ranks([c[0] for c in cells]),
                   _average_ranks([c[1] for c in cells]))
    assert abs(rho - stored["pooled_rho"]) <= 0.0015, (
        f"the release reports a pooled {stored['pooled_rho']}; recomputing "
        f"from both runs gives {rho:.4f}"
    )


def test_pooling_strengthens_rather_than_weakens():
    """The claim itself: the frontier judges make the relation stronger."""
    stored = _load("results_closed_analysis.json").get("pooled")
    if not stored:
        pytest.skip("[repro] no pooled record")
    open_cells = _open_cells()
    pooled = open_cells + _frontier_cells()

    open_rho = _pearson(_average_ranks([c[0] for c in open_cells]),
                        _average_ranks([c[1] for c in open_cells]))
    pooled_rho = _pearson(_average_ranks([c[0] for c in pooled]),
                          _average_ranks([c[1] for c in pooled]))
    assert pooled_rho < open_rho, (
        f"pooling the frontier judges moves the correlation from {open_rho:.3f} "
        f"to {pooled_rho:.3f}, which is weaker rather than stronger. The paper "
        f"states the opposite, and it is the point of running them."
    )
