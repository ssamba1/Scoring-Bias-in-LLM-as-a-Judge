"""Do the preregistered per-probe p-values follow from the thirteen pairs?

This is the test the preregistration registered, and its result is the paper's
most consequential null: paired Wilcoxon across the thirteen families, one test
per probe, null for every probe after Holm. The rebuttal FAQ said the opposite
until this week -- it claimed three of five probes were individually significant
-- so these five numbers are exactly the ones a hostile reader will recompute.

The correction applied to them was already checked: an independent Holm
implementation, ties included. But Holm takes the raw p-values as given, and
nothing recomputed those. Verifying a correction while trusting its inputs is a
familiar shape here -- the split-half reliability and the variance decomposition
were both in it -- and it leaves the whole chain resting on numbers no test has
seen the derivation of.

These are recomputed by enumeration rather than by calling a library. At n = 13
the exact null distribution is 8192 sign assignments of the signed ranks, small
enough to walk directly, which is the same argument the paper makes for its
sign-flip permutation test being exact rather than sampled. All five reproduce:
0.6003, 0.0266, 0.0266, 0.0681, 0.1099.

Ties are the reason to check rather than assume. rubric_order has repeated
values among the absolute differences, so its ranks are averaged; a tie-blind
implementation gets a different p there and the same p everywhere else, which is
the kind of discrepancy that looks like a rounding difference until someone
checks which probe it lands on.
"""

import itertools
import json
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


def _exact_signed_rank_p(diffs):
    """Two-sided exact p, by walking the 2^n sign assignments."""
    nonzero = [d for d in diffs if d != 0]
    n = len(nonzero)
    if n == 0 or n > 20:
        pytest.skip(f"[stats] enumeration not attempted for n={n}")
    ranks = _average_ranks([abs(d) for d in nonzero])
    total = sum(ranks)
    positive = sum(r for d, r in zip(nonzero, ranks) if d > 0)
    observed = min(positive, total - positive)

    extreme = 0
    for signs in itertools.product((0, 1), repeat=n):
        w = sum(r for s, r in zip(signs, ranks) if s)
        if min(w, total - w) <= observed + 1e-12:
            extreme += 1
    return min(1.0, extreme / 2 ** n)


def _pairs(probe):
    per_family = _load("results_peritem.json").get("per_family")
    if not isinstance(per_family, dict):
        pytest.skip("[repro] no per-family record")
    diffs = []
    for _family, record in per_family.items():
        cell = record.get(probe)
        if isinstance(cell, dict) and "base_delta" in cell and "instruct_delta" in cell:
            diffs.append(cell["base_delta"] - cell["instruct_delta"])
    if not diffs:
        pytest.skip(f"[repro] no paired deltas for {probe}")
    return diffs


@pytest.mark.parametrize("probe", PROBES)
def test_the_raw_p_value_recomputes(probe):
    summary = _load("results_peritem.json").get("summary", {}).get(probe)
    if not summary or summary.get("wilcoxon_p") is None:
        pytest.skip(f"[repro] no Wilcoxon p for {probe}")
    diffs = _pairs(probe)

    assert len(diffs) == summary["n_families"], (
        f"{probe} reports {summary['n_families']} families; the per-family "
        f"record holds {len(diffs)} pairs"
    )
    recomputed = _exact_signed_rank_p(diffs)
    assert abs(recomputed - summary["wilcoxon_p"]) <= 0.0006, (
        f"{probe}: the release reports a Wilcoxon p of "
        f"{summary['wilcoxon_p']}; enumerating the exact null over "
        f"{2 ** len(diffs)} sign assignments gives {recomputed:.4f}"
    )


def test_no_probe_is_individually_significant_after_correction():
    """The registered outcome, stated as a property rather than a string."""
    summary = _load("results_peritem.json").get("summary", {})
    corrected = {
        probe: summary[probe]["wilcoxon_p_holm"]
        for probe in PROBES
        if probe in summary and summary[probe].get("wilcoxon_p_holm") is not None
    }
    if not corrected:
        pytest.skip("[repro] no corrected p-values")
    significant = {p: v for p, v in corrected.items() if v < 0.05}
    assert not significant, (
        f"{significant} now clear 0.05 after Holm. The preregistered per-probe "
        f"test is reported as null for every probe, and the paper's aggregate "
        f"claim is built to not rest on any single one; if this changes, the "
        f"prose and the preregistration outcome both have to change with it."
    )
