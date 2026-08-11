r"""Recompute each family's effect from the raw scores, independently.

Every other check in this suite compares one derived artifact against another:
paper against table, table against JSON, JSON against a fresh run of the same
code. All of them sit inside one circle. An analysis that is consistently wrong
satisfies every one of them.

This steps outside it. For each family it reads the per-item scores out of
results_scaled.json and computes the bias effect here, in plain Python with no
import from repro/, then compares against what the analyses stored. Doing it
once as a throwaway script is what found the entropy-definition ambiguity; doing
it as one case per family makes it permanent and names the family that stops
reconciling.

The specification is the paper's primary one, "ev | maxmin | all": the score is
the expected value over answer tokens (per_item), each condition of a probe
gives a mean over items, a probe's bias is the spread across its conditions, and
a family's effect is the mean over probes of instruct minus base.

What this reproduces is estimates, not standard errors: the bootstrap intervals
in F2_forest come from resampling and are not recomputed here. Stating that
matters -- a check that quietly covered less than it appeared to would be worse
than none.
"""

import json
import statistics as st
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PANEL = REPRO / "results_scaled.json"
ROBUSTNESS = REPRO / "results_robustness.json"
PERITEM = REPRO / "results_peritem.json"

PROBES = ["rubric_order", "score_id", "reference_answer", "authority", "verbosity"]


def _load(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


PANEL_DATA = (_load(PANEL) or {}).get("results", {})


def _bias(cell):
    """Spread of condition means for one (family, arm, probe), from per-item scores."""
    means = [
        st.fmean(c["per_item"])
        for c in cell.values()
        if isinstance(c, dict) and c.get("per_item")
    ]
    return max(means) - min(means) if len(means) > 1 else None


def _bias_as_analysed(cell):
    """The same spread, but over the stored condition means the analyses read.

    The harness writes each condition's `mean` rounded to four decimals and
    analyze_peritem averages those rather than the per-item arrays, so the two
    routes differ by ~1e-4. Reproducing the documented route is what verifies a
    stored number; recomputing from the items is what verifies the route itself,
    and both are done here rather than choosing one and calling it agreement.
    """
    means = [
        c["mean"] for c in cell.values() if isinstance(c, dict) and c.get("mean") is not None
    ]
    return max(means) - min(means) if len(means) > 1 else None


def _family_effect(family):
    arms = PANEL_DATA.get(family)
    if not arms or "base" not in arms or "instruct" not in arms:
        return None
    diffs = []
    for probe in PROBES:
        base, instruct = _bias(arms["base"].get(probe, {})), _bias(arms["instruct"].get(probe, {}))
        if base is None or instruct is None:
            return None
        diffs.append(instruct - base)
    return st.fmean(diffs)


FAMILIES = sorted(PANEL_DATA)


@pytest.mark.skipif(not FAMILIES, reason="[panel data] results_scaled.json not present")
@pytest.mark.parametrize("family", FAMILIES)
def test_family_effect_matches_the_stored_sensitivity_value(family):
    """B3_sensitivity.per_family, recomputed from the per-item scores."""
    stored = (_load(ROBUSTNESS) or {}).get("B3_sensitivity", {}).get("per_family", {})
    if family not in stored:
        pytest.skip(f"[robustness] {family} absent from B3_sensitivity")
    mine = _family_effect(family)
    assert mine is not None, f"could not recompute {family} from the panel"
    assert abs(mine - stored[family]) < 5e-4, (
        f"{family}: recomputed from raw scores gives {mine:.4f}, "
        f"results_robustness.json stores {stored[family]}"
    )


@pytest.mark.skipif(not FAMILIES, reason="[panel data] results_scaled.json not present")
@pytest.mark.parametrize("family", FAMILIES)
def test_family_effect_matches_the_forest_point_estimate(family):
    """F2_forest is what the forest figure plots; its point estimate must agree."""
    forest = (_load(ROBUSTNESS) or {}).get("F2_forest", {})
    if family not in forest:
        pytest.skip(f"[robustness] {family} absent from F2_forest")
    mine = _family_effect(family)
    assert mine is not None, f"could not recompute {family} from the panel"
    assert abs(mine - forest[family]["effect"]) < 5e-4, (
        f"{family}: recomputed {mine:.4f}, the forest plot uses "
        f"{forest[family]['effect']}"
    )


@pytest.mark.skipif(not FAMILIES, reason="[panel data] results_scaled.json not present")
@pytest.mark.parametrize("family", FAMILIES)
def test_forest_interval_brackets_its_point_estimate(family):
    """A point estimate outside its own interval is a mismatched pair of runs."""
    forest = (_load(ROBUSTNESS) or {}).get("F2_forest", {})
    if family not in forest:
        pytest.skip(f"[robustness] {family} absent from F2_forest")
    record = forest[family]
    low, high = record["ci"]
    assert low <= high, f"{family}: interval endpoints out of order: [{low}, {high}]"
    assert low <= record["effect"] <= high, (
        f"{family}: effect {record['effect']} lies outside its own interval "
        f"[{low}, {high}]"
    )


@pytest.mark.skipif(not FAMILIES, reason="[panel data] results_scaled.json not present")
@pytest.mark.parametrize("probe", PROBES)
def test_probe_means_match_the_stored_summary(probe):
    """The per-probe base/instruct means, recomputed across all families."""
    summary = (_load(PERITEM) or {}).get("summary", {}).get(probe)
    if not summary:
        pytest.skip(f"[peritem] no summary for {probe}")
    for arm, key in (("base", "base_mean_delta"), ("instruct", "instruct_mean_delta")):
        values = [
            _bias(PANEL_DATA[f][arm][probe])
            for f in FAMILIES
            if probe in PANEL_DATA[f].get(arm, {})
        ]
        values = [v for v in values if v is not None]
        assert values, f"no {arm} values recomputed for {probe}"

        # The documented route: spreads over the stored condition means, each
        # family rounded to 3dp, then averaged and rounded again.
        analysed = [
            _bias_as_analysed(PANEL_DATA[f][arm][probe])
            for f in FAMILIES
            if probe in PANEL_DATA[f].get(arm, {})
        ]
        as_pipeline = round(st.fmean([round(v, 3) for v in analysed if v is not None]), 3)
        assert as_pipeline == summary[key], (
            f"{probe}/{arm}: the documented route (spread of stored condition "
            f"means, per family to 3dp, then averaged) gives {as_pipeline}, "
            f"results_peritem.json stores {summary[key]}"
        )

        # Recomputing from the per-item scores instead must land in the same
        # place to within the precision the stored means were written at.
        exact = st.fmean(values)
        assert abs(exact - summary[key]) < 2e-3, (
            f"{probe}/{arm}: averaging the unrounded per-item effects gives "
            f"{exact:.4f} against the stored {summary[key]}. A gap this large is "
            f"more than the 4-decimal storage of condition means can explain."
        )


def test_the_headline_effect_matches_when_recomputed():
    """The single number the abstract leads with."""
    if not FAMILIES:
        pytest.skip("[panel data] results_scaled.json not present")
    stored = (_load(ROBUSTNESS) or {}).get("B3_sensitivity", {}).get("full_mean_effect")
    if stored is None:
        pytest.skip("[robustness] no full_mean_effect stored")
    effects = [e for e in (_family_effect(f) for f in FAMILIES) if e is not None]
    mine = st.fmean(effects)
    assert abs(mine - stored) < 5e-4, (
        f"recomputed mean instruct-base change is {mine:.4f}, the paper's "
        f"analyses store {stored}"
    )
    positive = sum(e > 0 for e in effects)
    stored_positive = (_load(ROBUSTNESS) or {})["B3_sensitivity"].get("n_families_positive")
    assert positive == stored_positive, (
        f"recomputed {positive}/{len(effects)} families positive, stored "
        f"{stored_positive}"
    )


def _condition_cases():
    """One case per (family, arm, probe): the stored means against their items."""
    out = []
    for family in FAMILIES:
        for arm in ("base", "instruct"):
            for probe in PROBES:
                cell = PANEL_DATA[family].get(arm, {}).get(probe)
                if isinstance(cell, dict):
                    out.append(pytest.param(family, arm, probe, cell,
                                            id=f"{family}-{arm}-{probe}"))
    return out


CONDITION_CASES = _condition_cases()


@pytest.mark.skipif(not CONDITION_CASES, reason="[panel data] results_scaled.json not present")
@pytest.mark.parametrize("family,arm,probe,cell", CONDITION_CASES)
def test_stored_condition_means_match_their_own_items(family, arm, probe, cell):
    """The harness's arithmetic, checked against the data it shipped alongside.

    Every analysis downstream reads these `mean` fields rather than the per-item
    arrays, so a wrong mean would propagate into every table and every headline
    with nothing else in the chain able to notice: recomputing a derived value
    from a corrupted intermediate reproduces the corruption exactly.
    """
    for name, condition in cell.items():
        if not isinstance(condition, dict) or not condition.get("per_item"):
            continue
        recomputed = st.fmean(condition["per_item"])
        stored = condition["mean"]
        assert abs(recomputed - stored) < 5e-4, (
            f"{family}/{arm}/{probe}/{name}: stored mean {stored}, but the mean "
            f"of its {len(condition['per_item'])} per-item scores is "
            f"{recomputed:.6f}"
        )


def test_the_recomputation_is_reading_real_data():
    """Vacuity guard: an empty panel makes every case above skip or pass."""
    assert len(FAMILIES) == 13, f"{len(FAMILIES)} families in the panel, expected 13"
    sample = PANEL_DATA[FAMILIES[0]]["base"][PROBES[0]]
    conditions = [c for c in sample.values() if isinstance(c, dict) and c.get("per_item")]
    assert len(conditions) >= 2, "a probe needs at least two conditions for a spread"
    assert len(conditions[0]["per_item"]) == 50, (
        f"{len(conditions[0]['per_item'])} items per condition, expected 50"
    )
