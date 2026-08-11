"""Is the "exact" permutation test actually exact, and is its p-value right?

The paper's strongest distribution-free claim is an exact sign-flip permutation
test over the 13 family-level effects: p = 0.00098. "Exact" is a specific word.
It means every one of the 2^13 = 8192 sign assignments was enumerated, not
sampled -- and a Monte Carlo approximation reported under that name would be a
misdescription of the method, not merely an imprecise number.

Two things are checked, both by recomputation rather than by reading the label:

  * the enumeration covers 2^n patterns for the n families actually analysed,
    so a sampled test cannot be described as exact and a dropped family cannot
    go unnoticed
  * the p-value equals the proportion of sign assignments whose mean effect is
    at least as extreme as the observed one, computed here from the per-family
    data with no reference to the published number

At n = 13 the smallest attainable two-sided p is 2/8192 = 0.00024, and the
observed 8/8192 is four sign patterns either side. That granularity is the
reason to recompute rather than trust: a small error in the counting rule moves
the p-value by a visible amount but leaves it looking entirely plausible.
"""

import itertools
import json
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PERITEM = REPRO / "results_peritem.json"
ROBUSTNESS = REPRO / "results_robustness.json"


def _load(path, label):
    if not path.exists():
        pytest.skip(f"[{label}] {path.name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _family_effects():
    """Mean over probes of (instruct - base), one value per family."""
    peritem = _load(PERITEM, "peritem")
    probes = list(peritem["summary"])
    effects = []
    for record in peritem["per_family"].values():
        values = [
            record[p]["instruct_delta"] - record[p]["base_delta"]
            for p in probes
            if isinstance(record.get(p), dict) and "base_delta" in record[p]
        ]
        if values:
            effects.append(float(np.mean(values)))
    return np.asarray(effects)


def _published():
    return _load(ROBUSTNESS, "robustness")["F1_exact_permutation"]


def test_the_enumeration_is_exhaustive_not_sampled():
    """n_patterns must be 2^n for the families analysed, or it is not exact."""
    effects = _family_effects()
    assert len(effects) >= 2, "too few family effects to permute"
    published = _published()
    assert published["n_patterns"] == 2 ** len(effects), (
        f"the test is reported as exact over {published['n_patterns']} patterns, "
        f"but exhaustive enumeration of {len(effects)} families is "
        f"{2 ** len(effects)}. Either families were dropped or the test is a "
        f"Monte Carlo approximation described as exact."
    )


def test_the_p_value_is_the_enumerated_proportion():
    effects = _family_effects()
    published = _published()
    observed = abs(effects.mean())

    extreme = sum(
        1
        for signs in itertools.product((1, -1), repeat=len(effects))
        if abs((effects * np.asarray(signs)).mean()) >= observed - 1e-12
    )
    recomputed = extreme / 2 ** len(effects)

    assert abs(recomputed - published["exact_p_two_sided"]) < 0.0002, (
        f"recomputed exact p = {extreme}/{2 ** len(effects)} = {recomputed:.6f}, "
        f"published {published['exact_p_two_sided']}"
    )


def test_the_observed_effect_matches_the_per_family_data():
    """The statistic being permuted must be the one the paper reports."""
    effects = _family_effects()
    published = _published()
    assert abs(effects.mean() - published["observed_mean_effect"]) < 0.002, (
        f"the permutation test's observed effect is {effects.mean():.4f}, the "
        f"published value is {published['observed_mean_effect']}"
    )


def test_the_p_value_is_attainable_at_this_sample_size():
    """A p-value finer than 1/2^n cannot come from this enumeration.

    Vacuity guard of a different shape: it catches a published p that no exact
    test at this n could have produced, which the comparison above would miss if
    both the analysis and this test drifted the same way.
    """
    effects = _family_effects()
    published = _published()
    grain = 1 / 2 ** len(effects)
    p = published["exact_p_two_sided"]

    # Compare in p units, not as a ratio. The published value is rounded to five
    # decimals -- 8/8192 = 0.000977 is stored as 0.00098 -- and dividing by a
    # grain of 0.000122 inflates that 3.4e-6 rounding into a ratio error of 0.03.
    # Checking |p - k*grain| keeps the tolerance in the units the rounding
    # happened in, so it stays tight where it matters.
    nearest = round(p / grain) * grain
    assert abs(p - nearest) <= 1e-5, (
        f"published p = {p} is not within rounding of any multiple of "
        f"1/2^{len(effects)} = {grain:.6f} (nearest is {nearest:.6f}), so it "
        f"cannot be the output of an exact enumeration over {len(effects)} "
        f"families"
    )
