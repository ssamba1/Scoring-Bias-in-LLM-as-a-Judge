"""Do the span-patching summaries follow from the per-layer curve?

P13's result is a band: patching the nuisance span erases at least half the
instruct-vs-base gap across layers 3--14, peaking near 100% at layers 6--11 --
and does nothing at all for the good-exemplar framing, max reduction 7%. The
paper states the band and the peak; the release stores the 28-layer reduction
curve, a max, and the list of layers clearing 50%.

Nothing derived the summaries from the curve. Both are printed in the same
sentence, so a max or a band that disagreed with the numbers beneath it would
read as perfectly ordinary -- and the band is the claim, since "localized in a
mid-network band" is what distinguishes a causal finding from a diffuse one.

The exemplar probe is the check that matters most here. Its list of layers
clearing 50% is empty, which is exactly the preregistered clause that failed and
is reported as failed. An empty list that stopped being empty, or a populated
one that quietly emptied, would flip a reported failure into a success or the
reverse without any other number moving.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest"

THRESHOLD = 0.5


def _probes():
    path = REPRO / "spanpatch_analysis.json"
    if not path.exists():
        pytest.skip("[repro] span-patch analysis not present")
    blob = json.loads(path.read_text())
    probes = blob.get("probes")
    if not isinstance(probes, dict) or not probes:
        pytest.skip("[repro] no span-patch probes")
    return blob, probes


def test_each_max_reduction_is_the_max_of_its_curve():
    _, probes = _probes()
    wrong = []
    for name, record in sorted(probes.items()):
        curve = record.get("per_layer_reduction")
        if not curve:
            continue
        if abs(max(curve) - record["max_reduction"]) > 0.0006:
            wrong.append(
                f"{name}: stores max {record['max_reduction']}, its curve peaks "
                f"at {max(curve)}"
            )
    assert not wrong, f"a stored maximum is not the maximum of its own curve: {wrong}"


def test_the_band_is_exactly_the_layers_that_clear_the_threshold():
    _, probes = _probes()
    wrong = []
    for name, record in sorted(probes.items()):
        curve = record.get("per_layer_reduction")
        stored = record.get("layers_with_reduction_ge_50pct")
        if curve is None or stored is None:
            continue
        recomputed = [i for i, value in enumerate(curve) if value >= THRESHOLD]
        if recomputed != list(stored):
            wrong.append(f"{name}: stores {stored}, its curve gives {recomputed}")
    assert not wrong, (
        f"the band does not match the layers that actually clear 50%: {wrong}"
    )


def test_the_failed_clause_is_still_a_failure():
    """The exemplar probe reaches no layer at all; that is the reported result."""
    _, probes = _probes()
    exemplar = next(
        (record for name, record in probes.items() if name.startswith("reference")),
        None,
    )
    if exemplar is None:
        pytest.skip("[repro] no exemplar probe in the span-patch analysis")
    assert not exemplar.get("layers_with_reduction_ge_50pct"), (
        f"the exemplar span patch now clears 50% at "
        f"{exemplar['layers_with_reduction_ge_50pct']}; the paper reports this "
        f"preregistered clause as failed"
    )
    assert exemplar["max_reduction"] < THRESHOLD, (
        f"the exemplar patch now reaches {exemplar['max_reduction']}, so the "
        f"reported failure is no longer a failure"
    )


def test_the_paper_states_the_band_the_data_gives():
    """The prose names a layer range; it must be the stored one."""
    source = PAPER / "macros.tex"
    if not source.exists():
        pytest.skip("[paper] macros not present")
    text = " ".join(source.read_text(encoding="utf-8", errors="replace").split())
    if "span" not in text.lower():
        pytest.skip("[paper] the span-patch result is not described here")

    _, probes = _probes()
    authority = next(
        (record for name, record in probes.items() if name.startswith("authority")),
        None,
    )
    if authority is None:
        pytest.skip("[repro] no authority probe")
    band = authority.get("layers_with_reduction_ge_50pct")
    if not band:
        pytest.skip("[repro] the authority band is empty")

    quoted = f"layers {min(band)}--{max(band)}"
    assert quoted in text, (
        f"the paper does not state {quoted!r}; the stored curve clears 50% from "
        f"layer {min(band)} to {max(band)}"
    )
