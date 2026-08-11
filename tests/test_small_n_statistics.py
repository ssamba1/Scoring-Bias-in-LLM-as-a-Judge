"""A rank statistic at small n must not rest on an asymptotic p-value.

Both companion papers reported a Spearman correlation over five units with a
p-value taken from scipy's t-approximation. At n = 5 there are only 120
orderings, so the attainable two-sided p-values are multiples of 1/60 and the
quoted 0.037 was not among them; the exact permutation value was 0.083. One
claim moved from the significant side of 0.05 to the other.

This project's rank statistics are computed over families rather than judges, so
the smallest are n = 10 and n = 13, and every one of them currently sits between
p = 0.45 and p = 0.83 -- far enough from any threshold that the approximation
cannot change a verdict. Checked, not assumed.

The guard is therefore forward-looking. It fails when a *new* small-n
correlation appears close enough to a conventional threshold for the choice of
p-value method to matter. That is the situation where an exact or permutation
test has to be run before the claim is made, and it is exactly the situation
that went unnoticed in the companion work.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "paper" / "honest" / "repro"

# Below this, the discreteness of the permutation distribution is coarse enough
# that an asymptotic p can mislead.
SMALL_N = 20
# A p in this band is close enough to 0.05 that the method used to compute it
# can decide the verdict.
DANGER_BAND = (0.01, 0.10)

CORRELATION_HINTS = ("rho", "spearman", "kendall", "pearson", "tau")


def _flatten(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _flatten(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _flatten(value, f"{path}[{index}]")
    else:
        yield path, obj


def _correlation_blocks():
    """(file, path, n, p) for every stored correlation that records its own n."""
    blocks = []
    if not REPRO.exists():
        return blocks
    for path in sorted(REPRO.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        flat = dict(_flatten(data))
        for keypath, value in flat.items():
            name = keypath.rsplit(".", 1)[-1].lower()
            if not any(hint in name for hint in CORRELATION_HINTS):
                continue
            if name.endswith("_p") or not isinstance(value, (int, float)):
                continue
            parent = keypath.rsplit(".", 1)[0]
            n = flat.get(f"{parent}.n")
            p = flat.get(f"{parent}.spearman_p")
            if p is None:
                p = flat.get(f"{parent}.p")
            if isinstance(n, (int, float)) and isinstance(p, (int, float)):
                blocks.append((path.name, parent, int(n), float(p)))
    return blocks


def test_the_scan_finds_the_correlations_it_is_meant_to_check():
    """Otherwise an empty result would make the guard below vacuous."""
    blocks = _correlation_blocks()
    if not blocks:
        pytest.skip("no derived results present; run the analyses")
    assert len(blocks) >= 3, (
        f"only {len(blocks)} correlations discovered; the parser has probably "
        f"stopped matching the result schema and this guard is checking nothing"
    )


def test_no_small_n_correlation_sits_near_a_threshold():
    blocks = _correlation_blocks()
    if not blocks:
        pytest.skip("no derived results present; run the analyses")
    risky = [
        (name, path, n, p)
        for name, path, n, p in blocks
        if n <= SMALL_N and DANGER_BAND[0] <= p <= DANGER_BAND[1]
    ]
    assert not risky, (
        f"these correlations are computed over {SMALL_N} units or fewer and land "
        f"near p = 0.05, where the asymptotic approximation can decide the "
        f"verdict: {risky}. Recompute the p-value by exact enumeration or "
        f"permutation before the paper states it. The companion papers reported "
        f"one such claim as significant when the exact value was 0.083."
    )
