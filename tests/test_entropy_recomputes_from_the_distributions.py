"""Is the decisiveness statistic the entropy of what it claims?

Entropy is half the paper's mechanism -- the "confidence" in "Confidence Is Not
Robustness", the x-axis of the headline correlation, the 2.04 -> 1.45 claim. The
release stores a `mean_entropy` per cell and nothing recomputed it from the
distributions stored beside it.

There are two different quantities here and they are easy to confuse. A cell
holds `per_item_entropy` (the entropy of each item's answer distribution) and
`mean_dist` (those distributions averaged). The mean of the per-item entropies
and the entropy of the mean distribution are NOT equal: by Jensen's inequality
the second is always the larger, because entropy is concave. My first attempt at
this check recomputed the second and reported 278 of 390 cells as mismatched --
all of them correct, all of them off in the same direction, which is what a
systematic misreading looks like rather than a defect.

`mean_entropy` is the mean of the per-item entropies. That is checked here
exactly, and the Jensen inequality is checked as well: it must hold in every
cell, and a cell where the averaged distribution is *less* uncertain than the
average item would mean one of the two was computed over the wrong axis.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Both quantities are stored to four decimals, so rounding permits 1e-4.
TOLERANCE = 0.00015


def _cells():
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] scaled results not present")
    results = json.loads(path.read_text())["results"]
    found = []
    for family, arms in results.items():
        for arm, probes in arms.items():
            if not isinstance(probes, dict):
                continue
            for probe, variants in probes.items():
                if not isinstance(variants, dict):
                    continue
                for variant, record in variants.items():
                    if isinstance(record, dict) and "mean_entropy" in record:
                        found.append((f"{family}/{arm}/{probe}/{variant}", record))
    if not found:
        pytest.skip("[repro] no cells carry an entropy")
    return found


def _entropy(distribution):
    total = sum(distribution)
    return -sum(
        (p / total) * math.log2(p / total) for p in distribution if p > 0
    )


def test_the_stored_entropy_is_the_mean_of_the_per_item_entropies():
    wrong = []
    checked = 0
    for label, record in _cells():
        per_item = record.get("per_item_entropy")
        if not per_item:
            continue
        checked += 1
        recomputed = sum(per_item) / len(per_item)
        if abs(recomputed - record["mean_entropy"]) > TOLERANCE:
            wrong.append(
                f"{label}: stored {record['mean_entropy']}, its own items give "
                f"{recomputed:.4f}"
            )
    assert checked >= 300, f"only {checked} cells carried per-item entropies"
    assert not wrong, (
        f"the decisiveness statistic does not match the per-item entropies it "
        f"averages: {wrong[:5]}"
    )


def test_the_averaged_distribution_is_never_less_uncertain_than_its_items():
    """Jensen, as a check that the two quantities are on the axes they claim.

    Entropy is concave, so H(mean of the distributions) >= mean of H. A cell
    violating that would mean one of the two was computed over the wrong axis --
    per-item entropies averaged into the distribution slot, or the reverse.
    """
    violations = []
    checked = 0
    for label, record in _cells():
        distribution = record.get("mean_dist")
        if not distribution:
            continue
        checked += 1
        if _entropy(distribution) < record["mean_entropy"] - 1e-6:
            violations.append(
                f"{label}: H(mean dist) = {_entropy(distribution):.4f} < mean H = "
                f"{record['mean_entropy']}"
            )
    assert checked >= 300, f"only {checked} cells carried a mean distribution"
    assert not violations, (
        f"entropy is concave, so these are impossible unless one of the two "
        f"quantities is computed over the wrong axis: {violations[:5]}"
    )


def test_no_entropy_exceeds_the_scale():
    limit = math.log2(5)
    out_of_range = [
        f"{label}={record['mean_entropy']}"
        for label, record in _cells()
        if not 0 <= record["mean_entropy"] <= limit + 1e-9
    ]
    assert not out_of_range, (
        f"an entropy outside [0, log2(5)] over a five-point scale: {out_of_range[:5]}"
    )
