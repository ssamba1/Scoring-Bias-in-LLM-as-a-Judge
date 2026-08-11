"""Would the paper's asterisks survive a different bootstrap seed?

The summary table marks a probe when its bootstrap 95% CI excludes zero, and the
prose repeats those three probes by name. That verdict is a threshold crossing
computed from 10,000 resamples at seed 42. A threshold crossing is exactly the
kind of quantity that can depend on the draw, and nothing checked whether it
does -- the analysis produced the interval and the interval was compared against
itself.

Measured across ten seeds at the published resample count (measuring at a larger
count would answer a question nobody relies on):

    score ID          [+0.081, +0.637]   excludes zero under every seed
    authority         [+0.056, +0.436]   excludes zero under every seed
    verbosity         [+0.010, +0.517]   excludes zero under every seed
    rubric order      [-0.093, +0.746]   includes zero under every seed
    reference answer  [-0.000, +0.473]   VERDICT DEPENDS ON THE SEED

Reference answer sits exactly on the boundary: its lower bound is -0.000, and
over ten seeds it ranges [-0.003, +0.002]. The paper reports it as including
zero, which is the conservative side, and now says so explicitly.

So the property worth enforcing is not "every verdict is stable" -- one is not,
and pretending otherwise would be the fabrication this repository exists to
avoid. It is:

  1. every probe the paper *asserts* excludes zero must be seed-stable, and
  2. any probe whose verdict is seed-fragile must be disclosed in the paper.

A future rerun that flips reference answer to "excludes zero" would strengthen
the claim, but it would also silently add an asterisk to the table and
contradict the prose. This fails first.
"""

import json
import re
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
PERITEM = HONEST / "repro" / "results_peritem.json"
MACROS = HONEST / "macros.tex"

# Ten arbitrary seeds including the published one. Fixed, so the test is itself
# deterministic -- a flaky test about flakiness would be worse than none.
SEEDS = (42, 1, 7, 123, 2024, 31337, 8, 99, 555, 20260811)


def _peritem():
    if not PERITEM.exists():
        pytest.skip("[peritem] results_peritem.json not present")
    return json.loads(PERITEM.read_text(encoding="utf-8", errors="replace"))


def _diffs(per_family, probe):
    """Per-family instruct-minus-base differences, the bootstrap's unit."""
    out = []
    for record in per_family.values():
        cell = record.get(probe)
        if isinstance(cell, dict) and "base_delta" in cell and "instruct_delta" in cell:
            out.append(cell["instruct_delta"] - cell["base_delta"])
    return np.asarray(out, dtype=float)


def _ci(diffs, n_boot, seed):
    """Percentile bootstrap over families, as analyze_peritem.boot_ci computes it."""
    rng = np.random.default_rng(seed)
    n = len(diffs)
    means = np.array([rng.choice(diffs, n, replace=True).mean() for _ in range(n_boot)])
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _verdicts():
    """probe -> set of 'excludes zero' verdicts observed across the seeds."""
    data = _peritem()
    n_boot = data["n_bootstrap"]
    per_family = data["per_family"]
    observed = {}
    for probe in data["summary"]:
        diffs = _diffs(per_family, probe)
        if len(diffs) < 2:
            continue
        observed[probe] = {
            (lo > 0 or hi < 0) for lo, hi in (_ci(diffs, n_boot, s) for s in SEEDS)
        }
    return observed


def test_every_claimed_exclusion_is_seed_stable():
    """A probe the paper stars must exclude zero under every seed tried."""
    data = _peritem()
    claimed = [p for p, s in data["summary"].items() if s.get("ci_excludes_zero")]
    assert claimed, "no probe is recorded as excluding zero; this check has nothing to verify"

    observed = _verdicts()
    fragile = [p for p in claimed if observed.get(p) != {True}]
    assert not fragile, (
        f"{fragile} are reported as excluding zero, but that verdict changes with "
        f"the bootstrap seed at {data['n_bootstrap']} resamples. The asterisk in "
        f"the summary table and the probes named in the prose would move with the "
        f"draw."
    )


def test_any_seed_fragile_verdict_is_disclosed():
    """A probe whose verdict depends on the seed must be admitted in the paper."""
    observed = _verdicts()
    fragile = sorted(p for p, verdicts in observed.items() if len(verdicts) > 1)
    if not fragile:
        pytest.skip("[no fragile verdict] every CI verdict is seed-stable")

    if not MACROS.exists():
        pytest.skip("[macros] macros.tex not present")
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    assert re.search(r"not stable across bootstrap seeds", text), (
        f"the CI verdict for {fragile} depends on the bootstrap seed, and the "
        f"paper does not say so. Report the conservative reading and disclose "
        f"the instability rather than letting the draw decide an asterisk."
    )


def test_the_recomputed_interval_matches_the_published_one():
    """The reimplementation must reproduce the committed CI at the published seed.

    Without this the two tests above could be measuring something that is not
    the paper's bootstrap at all, and their agreement would mean nothing.
    """
    data = _peritem()
    per_family, n_boot, seed = data["per_family"], data["n_bootstrap"], data["seed"]
    mismatched = []
    for probe, summary in data["summary"].items():
        diffs = _diffs(per_family, probe)
        if len(diffs) < 2:
            continue
        lo, hi = _ci(diffs, n_boot, seed)
        published_lo, published_hi = summary["boot_ci95"]
        if abs(lo - published_lo) > 0.02 or abs(hi - published_hi) > 0.02:
            mismatched.append(
                f"{probe}: recomputed [{lo:+.3f},{hi:+.3f}] vs published "
                f"[{published_lo:+.3f},{published_hi:+.3f}]"
            )
    assert not mismatched, (
        "this test's bootstrap does not reproduce the published intervals, so it "
        f"is not measuring the paper's procedure: {mismatched}"
    )
