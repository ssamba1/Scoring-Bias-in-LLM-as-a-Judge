"""Does the estimator's reliability come from the data, or only from itself?

"The bias estimator's split-half reliability is 0.99" is load-bearing. It is
what the paper offers against the obvious objection to thirteen families -- that
the unit of inference is small -- and the rebuttal FAQ leans on it for the same
purpose. A reader who doubts n=13 is told the measurement is stable.

It was checked, but only against itself. test_stored_statistics_satisfy_their_
identities confirms that the stored Spearman-Brown figure equals 2r/(1+r) for
the stored split-half correlation, which is an arithmetic identity between two
numbers in the same file. Both could be wrong together and the identity would
still hold. That is the shape of error internal consistency cannot see: the
analysis being consistently wrong rather than inconsistently wrong.

So this reimplements the measurement from the raw per-item scores instead of
reading either stored number: split each cell's fifty items into evens and odds,
take the max-min spread across that probe's variants on each half, and correlate
the two halves across cells by average-rank Spearman. It reproduces 130 cells,
rho = 0.9864 against a stored 0.986, and Spearman-Brown 0.9931 against a stored
0.993 -- so the claim holds, and now holds for a reason independent of the file
that states it.
"""

import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


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


def _halves():
    """Per cell, the bias spread measured on even items and on odd items."""
    scaled = _load("results_scaled.json")["results"]
    even, odd = [], []
    for _family, arms in scaled.items():
        for checkpoint in ("base", "instruct"):
            cell = arms.get(checkpoint)
            if not isinstance(cell, dict):
                continue
            for _probe, variants in cell.items():
                if not isinstance(variants, dict):
                    continue
                if not all(isinstance(v, dict) and "per_item" in v
                           for v in variants.values()):
                    continue
                spreads = []
                for part in (slice(0, None, 2), slice(1, None, 2)):
                    means = {
                        name: statistics.mean(rec["per_item"][part])
                        for name, rec in variants.items()
                    }
                    spreads.append(max(means.values()) - min(means.values()))
                even.append(spreads[0])
                odd.append(spreads[1])
    if not even:
        pytest.skip("[repro] no per-item cells to split")
    return even, odd


def test_the_split_half_correlation_recomputes_from_the_scores():
    stored = _load("results_robustness.json").get("F4_split_half")
    if not stored:
        pytest.skip("[repro] no split-half record")
    even, odd = _halves()

    assert len(even) == stored["n_cells"], (
        f"the release measures reliability over {stored['n_cells']} cells; the "
        f"raw scores yield {len(even)}"
    )
    rho = _pearson(_average_ranks(even), _average_ranks(odd))
    assert abs(rho - stored["split_half_spearman"]) <= 0.0015, (
        f"the release reports a split-half correlation of "
        f"{stored['split_half_spearman']}; recomputing it from the per-item "
        f"scores gives {rho:.4f}"
    )


def test_the_reported_reliability_recomputes_from_the_scores():
    """Spearman-Brown, from the raw scores rather than the stored rho."""
    stored = _load("results_robustness.json").get("F4_split_half")
    if not stored:
        pytest.skip("[repro] no split-half record")
    even, odd = _halves()
    rho = _pearson(_average_ranks(even), _average_ranks(odd))
    reliability = 2 * rho / (1 + rho)

    assert abs(reliability - stored["spearman_brown"]) <= 0.0015, (
        f"the release reports a reliability of {stored['spearman_brown']}; the "
        f"per-item scores give {reliability:.4f}"
    )
    assert reliability > 0.9, (
        f"the estimator's reliability is {reliability:.3f}. The paper offers "
        f"this figure against the objection that thirteen families is a small "
        f"inferential unit; below 0.9 that defence no longer stands as written."
    )
