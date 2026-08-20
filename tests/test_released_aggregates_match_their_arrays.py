"""Does every stored aggregate equal the array it summarises?

These are identities the released data must satisfy no matter how any analysis
is written: a cell's mean is the mean of its own per-item scores, its entropy
the mean of its per-item entropies, its argmax values inside the score support,
its distribution a distribution.

That last property is the generalisation of the check that found the worst bug
in this project. score_id's "letter" variant stores its answer distribution in
token order A..E, mapping to scores 5..1, while every other variant runs 1..5;
three analyses compared them index-wise and measured the distance between
P(score 1) and P(score 5). It had survived two independent reimplementations,
because both inherited the same assumption about the layout -- agreement between
implementations tests the code, never the assumption underneath it.

What broke that circle was an appeal to something outside all three: expected
score is linear in the distribution, so sum(p_i * score_i) must equal the stored
mean. This file asks the same kind of question of every other aggregate in the
release, so a second layout assumption cannot hide the way the first one did.

Swept 3,468 pairs across six released runs when written, with no violations, so
this is a ratchet rather than a bug report: it holds the property, and any
future run that stores an aggregate disagreeing with its own array fails here.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

RUNS = ["results_scaled.json", "results_t10.json", "results_zh.json",
        "results_probes2.json", "results_14b.json", "results_multitemplate.json"]

# Distributions are rounded to four decimals and the aggregates are means of
# per-item values, so allow rounding but nothing structural.
TOL = 5e-4


def _cells(node, probe=None, depth=0):
    if depth > 4 or not isinstance(node, dict):
        return
    for key, value in node.items():
        if not isinstance(value, dict):
            continue
        if "mean" in value and "per_item" in value:
            yield probe, key, value
        else:
            yield from _cells(value, key, depth + 1)


def _released():
    found = []
    for name in RUNS:
        path = REPRO / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        results = payload.get("results")
        if isinstance(results, dict):
            found.append((name, results))
    if not found:
        pytest.skip("[repro] no released runs present")
    return found


def test_each_mean_is_the_mean_of_its_own_per_item_scores():
    wrong, checked = [], 0
    for name, results in _released():
        for probe, variant, rec in _cells(results):
            values = rec.get("per_item")
            mean = rec.get("mean")
            if not (isinstance(values, list) and values and isinstance(mean, (int, float))):
                continue
            checked += 1
            recomputed = sum(values) / len(values)
            if abs(recomputed - mean) > TOL:
                wrong.append(f"{name} {probe}/{variant}: stored {mean}, "
                             f"array gives {recomputed:.4f}")
    assert checked, "no per-item arrays found; this check would pass covering nothing"
    assert not wrong, (
        f"{len(wrong)} of {checked} cells store a mean that is not the mean of "
        f"their own scores: {wrong[:5]}. Either the aggregate or the array is "
        f"describing something else."
    )


def test_each_entropy_is_the_mean_of_its_own_per_item_entropies():
    wrong, checked = [], 0
    for name, results in _released():
        for probe, variant, rec in _cells(results):
            values = rec.get("per_item_entropy")
            mean = rec.get("mean_entropy")
            if not (isinstance(values, list) and values and isinstance(mean, (int, float))):
                continue
            checked += 1
            recomputed = sum(values) / len(values)
            if abs(recomputed - mean) > TOL:
                wrong.append(f"{name} {probe}/{variant}: stored {mean}, "
                             f"array gives {recomputed:.4f}")
    if not checked:
        pytest.skip("[repro] no per-item entropy arrays")
    assert not wrong, (
        f"{len(wrong)} of {checked} cells store an entropy that is not the mean "
        f"of their per-item entropies: {wrong[:5]}. Decisiveness is the paper's "
        f"title quantity."
    )


def test_every_distribution_is_a_distribution():
    wrong, checked = [], 0
    for name, results in _released():
        for probe, variant, rec in _cells(results):
            dist = rec.get("mean_dist")
            if not (isinstance(dist, list) and dist):
                continue
            checked += 1
            if abs(sum(dist) - 1.0) > 0.01 or any(p < -1e-9 for p in dist):
                wrong.append(f"{name} {probe}/{variant}: sums to {sum(dist):.4f}")
    if not checked:
        pytest.skip("[repro] no distributions")
    assert not wrong, (
        f"{len(wrong)} of {checked} stored distributions are not distributions: "
        f"{wrong[:5]}. Every total-variation shift is computed from these."
    )


def test_discrete_scores_lie_inside_the_support():
    wrong, checked = [], 0
    for name, results in _released():
        for probe, variant, rec in _cells(results):
            values = rec.get("per_item_argmax")
            if not (isinstance(values, list) and values):
                continue
            checked += 1
            outside = sorted({v for v in values if not 1 <= v <= 5})
            if outside:
                wrong.append(f"{name} {probe}/{variant}: {outside[:5]}")
    if not checked:
        pytest.skip("[repro] no argmax arrays")
    assert not wrong, (
        f"{len(wrong)} of {checked} cells record a discrete score outside the "
        f"1-5 support: {wrong[:5]}. The letter variant maps A..E to 5..1, so an "
        f"unmapped token index would surface here as a 0."
    )


def test_the_mean_maximum_dominates_the_maximum_of_the_mean():
    """Jensen: averaging distributions cannot raise the peak above the mean peak."""
    wrong, checked = [], 0
    for name, results in _released():
        for probe, variant, rec in _cells(results):
            dist = rec.get("mean_dist")
            peak = rec.get("mean_maxprob")
            if not (isinstance(dist, list) and dist and isinstance(peak, (int, float))):
                continue
            checked += 1
            if peak < max(dist) - TOL:
                wrong.append(f"{name} {probe}/{variant}: mean_maxprob {peak} < "
                             f"max(mean_dist) {max(dist):.4f}")
    if not checked:
        pytest.skip("[repro] no maxprob values")
    assert not wrong, (
        f"{len(wrong)} of {checked} cells violate Jensen's inequality between "
        f"the mean of per-item maxima and the maximum of the mean distribution: "
        f"{wrong[:5]}. That cannot happen if both summarise the same items."
    )
