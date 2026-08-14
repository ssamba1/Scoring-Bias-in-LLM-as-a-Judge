"""Is the theory's bound as tight in the data as the paper says?

The decomposition rests on a Cauchy-Schwarz step, and a bound is only worth
building on if it is not slack. The release measures how tight it is
empirically: the ratio of the softmax gradient norm to the square root of the
score variance, over the 130 control distributions, comes out at 0.451 with a
range of 0.375 to 0.566.

Those four numbers were read but never recomputed. The existing theory test
takes them from the release and checks their relationships to each other -- that
the mean lies inside the range, that the ratio behaves like a ratio -- which
holds for any four numbers with that shape, whatever distributions they claim to
summarise.

Recomputed here from the raw control distributions. Each mean_dist is
renormalised, the expected score s0 formed over the 1..5 scale, and the two
quantities built directly:

    grad = sqrt( sum_v  p(v)^2 (v - s0)^2 )
    sd   = sqrt( sum_v  p(v)   (v - s0)^2 )

with the ratio taken per cell. It reproduces 0.4507, 0.3752 and 0.5663 against
stored 0.451, 0.375 and 0.566, over the same 130 cells.

The difference between the two expressions is one factor of p(v) inside the sum,
which is exactly the kind of slip that leaves a plausible ratio: squaring the
weights instead of using them once still yields something between zero and one,
still varies sensibly across cells, and still looks like a tightness measure.
"""

import json
import math
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONTROL = {
    "rubric_order": "control",
    "score_id": "numeric",
    "reference_answer": "none",
    "authority": "none",
    "verbosity": "control",
}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _ratios():
    scaled = _load("results_scaled.json")["results"]
    ratios = []
    for _family, arms in scaled.items():
        for checkpoint in ("base", "instruct"):
            cell = arms.get(checkpoint)
            if not isinstance(cell, dict):
                continue
            for probe, control in CONTROL.items():
                variants = cell.get(probe)
                if not isinstance(variants, dict) or control not in variants:
                    continue
                dist = variants[control].get("mean_dist")
                if not dist:
                    continue
                total = sum(dist)
                if total <= 0:
                    continue
                probs = [x / total for x in dist]
                values = [float(i) for i in range(1, len(probs) + 1)]
                s0 = sum(p * v for p, v in zip(probs, values))
                grad = math.sqrt(sum(p ** 2 * (v - s0) ** 2 for p, v in zip(probs, values)))
                sd = math.sqrt(sum(p * (v - s0) ** 2 for p, v in zip(probs, values)))
                if sd > 1e-9:
                    ratios.append(grad / sd)
    if not ratios:
        pytest.skip("[repro] no control distributions")
    return ratios


def test_the_tightness_summary_recomputes():
    stored = _load("results_robustness.json").get("F5_bound_tightness")
    if not stored:
        pytest.skip("[repro] no bound-tightness record")
    ratios = _ratios()

    assert len(ratios) == stored["n"], (
        f"the release measures tightness over {stored['n']} distributions; the "
        f"raw runs yield {len(ratios)}"
    )
    for label, value, key in (
        ("mean", statistics.mean(ratios), "mean_gradnorm_over_sqrtvar"),
        ("min", min(ratios), "min"),
        ("max", max(ratios), "max"),
    ):
        assert abs(value - stored[key]) <= 0.0015, (
            f"the release reports a {label} ratio of {stored[key]}; the control "
            f"distributions give {value:.4f}"
        )


def test_the_bound_is_not_slack():
    """A bound with a ratio near zero would not support the decomposition."""
    ratios = _ratios()
    mean = statistics.mean(ratios)
    assert 0 < mean < 1, (
        f"the gradient-norm to standard-deviation ratio averages {mean:.3f}, "
        f"which is outside (0, 1); Cauchy-Schwarz puts it inside"
    )
    assert mean > 0.2, (
        f"the bound is slack at {mean:.3f}. The decomposition treats it as "
        f"informative rather than merely valid, and a ratio near zero would "
        f"mean the theory constrains almost nothing about the measured cells."
    )
