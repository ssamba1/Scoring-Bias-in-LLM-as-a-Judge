"""Does 4-bit quantization explain the 14B attenuation? It does not.

The paper's only causal point above 8B is a 4-bit Qwen2.5-14B run, attenuated to
+0.06 against the panel's +0.26. That made it uninterpretable: quantization
reshapes the score distribution, which is the quantity being measured, so the
one piece of evidence for the effect fading with scale was confounded by the
variable most likely to fade it artificially. The 14B cannot be run at fp16 on a
16 GB card, so the confound could not be resolved there.

Qwen2.5-7B resolves it. It is in the main panel at fp16 on these exact items, so
nf4 against it is a direct difference. nf4 moves the tuning delta from +0.5436
to +0.5757 -- about +6%, and inflating rather than attenuating. A 6% inflation
cannot produce a 77% attenuation, so the 14B result is not a quantization
artefact and the scale reading is the one left standing.

The guard exists because that conclusion is load-bearing in the wrong direction
for the paper: it makes the scale limit more likely to be real, which is the
finding a tired author would rather not have. If the numbers ever drift toward
"quantization attenuates", the paper's scope claim becomes defensible again for
the wrong reason, and this test refuses that quietly happening.

It also pins the caveat. This is one family and one scheme, and individual
probes move sharply under quantization even though the contrast does not --
rubric_order base 0.113 to 0.474, authority instruct 0.063 to 0.214. The stable
quantity is the base-versus-instruct difference, not the biases themselves.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PROBES = ["rubric_order", "score_id", "reference_answer", "authority", "verbosity"]
FAMILY = "Qwen2.5-7B"


def _stored():
    path = REPRO / "results_quantization.json"
    if not path.exists():
        pytest.skip("[repro] results_quantization.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _bias(record, probe):
    means = [v["mean"] for v in record[probe].values()]
    return max(means) - min(means)


def _arm_means(record):
    return {kind: sum(_bias(record[kind], p) for p in PROBES) / len(PROBES)
            for kind in ("base", "instruct")}


def _runs():
    panel = REPRO / "results_scaled.json"
    nf4 = REPRO / "results_7b_nf4.json"
    if not (panel.exists() and nf4.exists()):
        pytest.skip("[repro] both arms required")
    return (json.loads(panel.read_text(encoding="utf-8", errors="replace"))["results"][FAMILY],
            json.loads(nf4.read_text(encoding="utf-8", errors="replace"))["results"][FAMILY])


def test_both_arms_scored_the_same_panel():
    """A difference is only meaningful if the items and probes match."""
    panel, nf4 = _runs()
    for kind in ("base", "instruct"):
        assert sorted(panel[kind]) == sorted(nf4[kind]), (
            f"{kind}: probe sets differ between arms"
        )
        for probe in PROBES:
            assert sorted(panel[kind][probe]) == sorted(nf4[kind][probe]), (
                f"{kind}/{probe}: variant sets differ between arms"
            )
            a = len(panel[kind][probe][sorted(panel[kind][probe])[0]]["per_item"])
            b = len(nf4[kind][probe][sorted(nf4[kind][probe])[0]]["per_item"])
            assert a == b, f"{kind}/{probe}: {a} items vs {b}"


def test_the_deltas_recompute_from_the_two_runs():
    panel, nf4 = _runs()
    stored = _stored()
    fp16 = _arm_means(panel)
    quant = _arm_means(nf4)

    assert abs((fp16["instruct"] - fp16["base"]) - stored["fp16_tuning_delta"]) < 5e-4, (
        f"fp16 delta recomputes to {fp16['instruct'] - fp16['base']:.4f}, stored "
        f"{stored['fp16_tuning_delta']}"
    )
    assert abs((quant["instruct"] - quant["base"]) - stored["nf4_tuning_delta"]) < 5e-4, (
        f"nf4 delta recomputes to {quant['instruct'] - quant['base']:.4f}, stored "
        f"{stored['nf4_tuning_delta']}"
    )


def test_quantization_does_not_attenuate_the_tuning_effect():
    """The finding that makes the 14B point interpretable."""
    stored = _stored()
    fp16, nf4 = stored["fp16_tuning_delta"], stored["nf4_tuning_delta"]

    recomputed = abs(nf4) < abs(fp16)
    assert recomputed == stored["quantization_attenuates_delta"], (
        f"the release records quantization_attenuates_delta="
        f"{stored['quantization_attenuates_delta']} while its own deltas "
        f"({fp16}, {nf4}) give {recomputed}"
    )
    assert not recomputed, (
        f"nf4 now attenuates the tuning delta ({fp16} -> {nf4}). That would "
        f"restore the confound on the 14B point and make the paper's scale "
        f"claim uninterpretable again -- it is a different result and needs "
        f"saying, not absorbing."
    )
    assert abs(stored["delta_change_pct"]) < 25, (
        f"quantization now moves the delta by {stored['delta_change_pct']}%. "
        f"The argument is that a small change cannot explain the 14B's ~77% "
        f"attenuation; at this size that argument no longer holds."
    )


def test_individual_probes_are_not_claimed_to_be_stable():
    """Only the contrast survives quantization; the biases themselves do not."""
    stored = _stored()
    per_probe = stored.get("per_probe")
    if not per_probe:
        pytest.skip("[repro] no per-probe record")

    moved = [
        probe for probe, arms in per_probe.items()
        for arm in ("base", "instruct")
        if abs(arms[arm]["nf4"] - arms[arm]["fp16"]) > 0.1
    ]
    assert moved, (
        "no individual probe moves by more than 0.1 under quantization. The "
        "release states that individual biases do shift while the contrast "
        "holds; if nothing shifts, that caveat is now wrong."
    )
