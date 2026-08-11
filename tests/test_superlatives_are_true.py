"""Are the paper's superlatives still the maxima they claim to be?

A superlative is the one kind of claim that can be falsified by adding data
without touching the sentence. Every other number in the paper goes stale
visibly -- it stops matching its source. "The largest effect in this study"
stops being true when some *other* run gets larger, and nothing about the
sentence, its source, or its analysis changes.

The paper carried one that had gone false exactly this way. Sycophancy was
written up as "the largest tuning effect in this entire study" at +0.46, which
it is on the 13-family panel; the Chinese replication, added later, has three
probe-level changes above it (verbosity +0.76, rubric order +0.64, score ID
+0.47) on four families. The claim is now scoped to the panel and names the
exception, and this recomputes both halves.

Each superlative here is recomputed over every released measurement of the same
kind rather than compared against a stored maximum, because a stored maximum is
a second place for the same staleness to hide.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"

PANEL_FAMILIES = 13


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text())


def _prose():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    return MACROS.read_text(encoding="utf-8", errors="replace")


def _tuning_effects():
    """(source, probe, n_families, mean_change) for every released per-probe effect."""
    effects = []
    for path in sorted(REPRO.glob("*_analysis.json")):
        blob = json.loads(path.read_text())
        for probe, stats in (blob.get("per_probe") or {}).items():
            if "mean_change" in stats:
                effects.append((path.name, probe, stats.get("n_families"),
                                stats["mean_change"]))
    summary = _load("results_peritem.json")["summary"]
    for probe, stats in summary.items():
        effects.append(("results_peritem.json", probe, stats["n_families"],
                        stats["mean_change"]))
    if not effects:
        pytest.skip("[repro] no per-probe tuning effects found")
    return effects


def test_sycophancy_is_the_largest_effect_on_the_panel():
    effects = _tuning_effects()
    panel = [e for e in effects if e[2] == PANEL_FAMILIES]
    assert len(panel) >= 6, (
        f"only {len(panel)} panel-wide probe effects found; the superlative "
        f"would be over a set too small to mean anything"
    )
    source, probe, _, change = max(panel, key=lambda e: e[3])
    assert probe == "sycophancy", (
        f"the paper calls sycophancy the largest tuning effect on the panel; "
        f"the largest is now {probe} at {change:+.3f} ({source})"
    )


def test_the_larger_effects_elsewhere_are_disclosed():
    """Anything above the panel maximum has to be named, not quietly outranked."""
    effects = _tuning_effects()
    panel_max = max(e[3] for e in effects if e[2] == PANEL_FAMILIES)
    bigger = sorted((e for e in effects if e[3] > panel_max),
                    key=lambda e: -e[3])
    prose = _prose()
    if not bigger:
        pytest.skip("[repro] nothing outranks the panel maximum")

    undisclosed = []
    for source, probe, families, change in bigger:
        if f"{change:+.2f}".replace("+", "$+") not in prose and f"{change:.2f}" not in prose:
            undisclosed.append(f"{probe}={change:+.3f} ({source})")
    assert not undisclosed, (
        f"these exceed the panel maximum of {panel_max:+.3f} and the paper does "
        f"not state them: {undisclosed}. A scoped superlative is only honest "
        f"while the exceptions outside its scope are named."
    )


def test_the_instruct_side_comparison_holds():
    """"larger than any of the original five probes" -- the second half."""
    summary = _load("results_peritem.json")["summary"]
    probes2 = _load("results_probes2_analysis.json")["per_probe"]
    if "sycophancy" not in probes2:
        pytest.skip("[repro] sycophancy not present")
    syco = probes2["sycophancy"]["mean_instruct"]
    originals = {p: s["instruct_mean_delta"] for p, s in summary.items()}
    biggest = max(originals, key=originals.get)
    assert syco > originals[biggest], (
        f"the paper says sycophancy's instruct-side bias ({syco}) exceeds any "
        f"of the original five probes; {biggest} is now {originals[biggest]}"
    )
    assert f"${syco:.2f}$" in _prose(), (
        f"the paper no longer quotes sycophancy's instruct-side bias as "
        f"{syco:.2f}"
    )


def test_the_frontier_maximum_is_the_maximum():
    """"the largest biases measured anywhere in this project" -- the frontier trio."""
    prose = _prose()
    match = re.search(
        r"rubric-order \$\\Delta\$ of \$?([\d.]+)\$?, \$?([\d.]+)\$?, and \$?([\d.]+)\$?",
        prose,
    )
    if not match:
        pytest.skip("[paper] the frontier maxima are not stated in that form")
    stated = max(float(g) for g in match.groups())

    judges = _load("results_closed_analysis.json")["judges"]
    rubric = {name: j["delta_by_probe"]["rubric_order"] for name, j in judges.items()}
    assert len(rubric) == 3, (
        f"the sentence names three frontier judges; the release has {sorted(rubric)}"
    )
    assert abs(max(rubric.values()) - stated) < 0.005, (
        f"the paper states a largest frontier rubric-order bias of {stated}; "
        f"the released maximum is {max(rubric.values()):.3f}"
    )

    # "the largest biases measured anywhere in this project" -- against the
    # open panel it is being compared with, per cell, not against its own trio.
    panel = _load("results_peritem.json")["summary"]
    panel_max = max(s["instruct_mean_delta"] for s in panel.values())
    assert max(rubric.values()) > panel_max, (
        f"the frontier maximum ({max(rubric.values())}) no longer exceeds the "
        f"panel's largest mean bias ({panel_max})"
    )
