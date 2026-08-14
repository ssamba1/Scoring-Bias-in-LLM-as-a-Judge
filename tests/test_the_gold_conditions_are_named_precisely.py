"""Does the ground-truth section claim more nuisances than it ran?

The ground-truth test perturbs good/bad pairs and asks whether the judge still
tells them apart. It ran three perturbations: rubric reversal, verbosity
padding, and one authority framing. The prose said "authority framing is nearly
harmless (0.97/0.97)".

The authority probe has two framings, expert and novice, and this run used only
novice. The generated table says so -- its row is labelled Novice -- but the
sentence beside it generalised to authority framing as a category. A reader
taking the sentence at face value would conclude that telling a judge the answer
came from an expert is as harmless as telling it the answer came from a novice,
which this run does not show and which is the direction one would expect to
matter more.

This is the same shape as two corrections already made here: the sycophancy
superlative that held only on the panel, and the stage-transition claim that
held at seven of eight steps. A sentence broader than its run.

So the conditions named in the prose must be the conditions the run holds, and
where a probe has several variants and the run used one, the prose must name the
variant rather than the probe.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"

# Probes with more than one perturbation variant in the main panel. Naming the
# probe rather than the variant claims the others were tested too.
MULTI_VARIANT = {"novice": "authority", "expert": "authority"}


def _gold_raw():
    path = REPRO / "gold_results.json"
    if not path.exists():
        pytest.skip("[repro] gold_results.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _gold_analysis():
    path = REPRO / "results_gold.json"
    if not path.exists():
        pytest.skip("[repro] results_gold.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _prose():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    if "GOLDPROSE" not in text:
        pytest.skip("[paper] no ground-truth prose")
    start = text.index("GOLDPROSE")
    return text[start:start + 1400]


def test_the_analysis_covers_every_perturbation_the_run_holds():
    """control plus the perturbations should account for the raw conditions."""
    raw = _gold_raw().get("conditions")
    analysis = _gold_analysis()
    perturbations = analysis.get("conditions")
    if not isinstance(raw, list) or not isinstance(perturbations, list):
        pytest.skip("[repro] conditions not declared")

    accounted = set(perturbations) | {"control"}
    missing = sorted(set(raw) - accounted)
    assert not missing, (
        f"the run holds conditions {sorted(raw)} but the analysis accounts for "
        f"{sorted(accounted)}; {missing} were measured and then dropped without "
        f"appearing in the released summary"
    )
    assert "control" in analysis, (
        "the analysis no longer carries the unperturbed baseline separately; "
        "every degradation figure is measured against it"
    )


def test_the_prose_names_the_variant_it_ran():
    """A one-variant run must not be described by its probe's name."""
    perturbations = _gold_analysis().get("conditions")
    if not isinstance(perturbations, list):
        pytest.skip("[repro] no perturbation list")
    prose = _prose()

    unnamed = []
    for condition in perturbations:
        probe = MULTI_VARIANT.get(condition)
        if not probe:
            continue
        if condition not in prose.lower():
            unnamed.append(f"{condition} (ran) described only as {probe}")
    assert not unnamed, (
        f"the ground-truth prose names a probe where the run used one of its "
        f"variants: {unnamed}. The generated table labels the row correctly, so "
        f"the sentence is the only place a reader is told otherwise."
    )
