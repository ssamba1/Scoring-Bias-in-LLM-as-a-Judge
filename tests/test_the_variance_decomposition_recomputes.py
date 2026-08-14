"""Where does the paper's bias variance actually go?

The anatomy-of-variance section reports how the 130 cell-level bias spreads
divide up: probe 0.236, family:probe 0.368, family 0.084, checkpoint kind 0.056,
residual 0.256. The reading that matters is that the probe and the family-probe
interaction dominate -- bias is mostly about which nuisance you test and which
model you test it on, not a single global judge trait.

It was checked only for summing to one. Five proportions summing to one is a
property any normalised vector has, including a wrong one: scale every component
by the same factor, or swap two labels, and the sum is still one.

This recomputes them from the raw runs. The design is fully crossed and exactly
balanced -- thirteen families by five probes by two checkpoint kinds, one
observation per cell -- and for a balanced design the Type II sums of squares
the analyzer takes from statsmodels are equal to the classical ones, which are
short enough to write out directly. That matters: computing it with the same
library the analyzer used would re-run the analyzer's assumptions rather than
check them. Here the grand mean, the marginal means and the interaction
deviations are formed by hand and the residual is what is left of the total.

All five reproduce: 0.0842, 0.2364, 0.0557, 0.3675, 0.2562 against 0.084,
0.236, 0.056, 0.368, 0.256.
"""

import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PROBES = ["rubric_order", "score_id", "authority", "verbosity", "reference_answer"]

# analyzer term name -> key in the released record
TERMS = {
    "family": "family",
    "probe": "probe",
    "kind": "kind",
    "family:probe": "family:probe",
    "Residual": "Residual",
}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _cells():
    """(family, probe, kind, bias spread) for every cell of the panel."""
    scaled = _load("results_scaled.json")["results"]
    rows = []
    for family, arms in scaled.items():
        for kind in ("base", "instruct"):
            cell = arms.get(kind)
            if not isinstance(cell, dict):
                continue
            for probe in PROBES:
                variants = cell.get(probe)
                if not isinstance(variants, dict):
                    continue
                if not all(isinstance(v, dict) and "per_item" in v
                           for v in variants.values()):
                    continue
                means = {n: statistics.mean(r["per_item"]) for n, r in variants.items()}
                rows.append((family, probe, kind, max(means.values()) - min(means.values())))
    if not rows:
        pytest.skip("[repro] no cells to decompose")
    return rows


def _proportions(rows):
    families = sorted({r[0] for r in rows})
    probes = sorted({r[1] for r in rows})
    kinds = sorted({r[2] for r in rows})
    grand = statistics.mean(r[3] for r in rows)

    def group(pred):
        values = [r[3] for r in rows if pred(r)]
        return statistics.mean(values), len(values)

    ss = {}
    for name, levels, index in (("family", families, 0), ("probe", probes, 1),
                                ("kind", kinds, 2)):
        total = 0.0
        for level in levels:
            mean, n = group(lambda r, i=index, lv=level: r[i] == lv)
            total += n * (mean - grand) ** 2
        ss[name] = total

    interaction = 0.0
    for family in families:
        mf, _ = group(lambda r, f=family: r[0] == f)
        for probe in probes:
            mp, _ = group(lambda r, p=probe: r[1] == p)
            cell, n = group(lambda r, f=family, p=probe: r[0] == f and r[1] == p)
            interaction += n * (cell - mf - mp + grand) ** 2
    ss["family:probe"] = interaction

    total_ss = sum((r[3] - grand) ** 2 for r in rows)
    ss["Residual"] = total_ss - sum(ss.values())
    return {k: v / total_ss for k, v in ss.items()}, total_ss


def test_the_design_is_balanced():
    """The recomputation below is only valid for a balanced design."""
    rows = _cells()
    families = {r[0] for r in rows}
    probes = {r[1] for r in rows}
    kinds = {r[2] for r in rows}
    assert len(rows) == len(families) * len(probes) * len(kinds), (
        f"{len(rows)} cells for {len(families)}x{len(probes)}x{len(kinds)}; the "
        f"design is no longer fully crossed, and Type II sums of squares stop "
        f"equalling the classical ones this test computes"
    )
    counts = {}
    for family, probe, kind, _ in rows:
        counts[(family, probe, kind)] = counts.get((family, probe, kind), 0) + 1
    assert set(counts.values()) == {1}, (
        f"cells are not singly observed: {sorted(set(counts.values()))}"
    )


def test_every_variance_component_recomputes():
    stored = _load("results_robustness.json").get("E_variance_decomposition")
    if not stored or "error" in stored:
        pytest.skip("[repro] no variance decomposition recorded")
    recomputed, _ = _proportions(_cells())

    wrong = []
    for term, key in TERMS.items():
        if key not in stored:
            continue
        if abs(recomputed[term] - stored[key]) > 0.0015:
            wrong.append(f"{key}: released {stored[key]}, recomputed {recomputed[term]:.4f}")
    assert not wrong, (
        f"the variance decomposition does not follow from the cells it "
        f"describes: {wrong}"
    )


def test_the_probe_terms_still_dominate():
    """The reading the section rests on, not just the arithmetic."""
    recomputed, _ = _proportions(_cells())
    probe_side = recomputed["probe"] + recomputed["family:probe"]
    assert probe_side > recomputed["family"] + recomputed["kind"], (
        f"probe and family:probe together account for {probe_side:.3f} of the "
        f"variance against {recomputed['family'] + recomputed['kind']:.3f} for "
        f"family and kind; the section reads the split the other way round"
    )
