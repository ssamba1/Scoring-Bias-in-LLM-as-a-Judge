"""Does the specification curve follow from the panel it summarises?

The paper's answer to "did you pick the analysis that worked?" is the
specification curve: every expected-value specification gives a positive mean
effect, with 9--11 of 13 families positive. Six numbers, quoted as a range, and
the whole point of them is that they were not chosen.

They were stored by the analysis and compared against nothing. This recomputes
all six from results_scaled.json, implemented from the definitions rather than
by calling the analysis's own helper -- the readout is the variant means, the
metric is either max-minus-min across variants or the mean absolute deviation
from the control variant, the probe set is all five or the format or content
half, and a family's effect is its mean instruct bias minus its mean base bias.

Recomputing with the analysis's own function would only prove the function is
deterministic. Recomputing from the definitions is what makes the agreement
evidence.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONTROL = {
    "rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
    "authority": "none", "verbosity": "control",
}
PROBE_SETS = {
    "all": list(CONTROL),
    "format": ["rubric_order", "score_id"],
    "content": ["reference_answer", "authority", "verbosity"],
}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[{name}] not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _cell_bias(cell, control, metric):
    means = {v: c["mean"] for v, c in cell.items() if isinstance(c, dict) and "mean" in c}
    if len(means) < 2:
        return None
    if metric == "maxmin":
        return max(means.values()) - min(means.values())
    reference = means.get(control)
    if reference is None:
        return None
    deviations = [abs(m - reference) for v, m in means.items() if v != control]
    return sum(deviations) / len(deviations) if deviations else None


def _family_effects(panel, probes, metric):
    effects = []
    for arms in panel.values():
        per_arm = {}
        for kind in ("base", "instruct"):
            cells = arms.get(kind)
            if not isinstance(cells, dict):
                continue
            values = [
                _cell_bias(cells[p], CONTROL[p], metric) for p in probes if p in cells
            ]
            values = [v for v in values if v is not None]
            if values:
                per_arm[kind] = sum(values) / len(values)
        if len(per_arm) == 2:
            effects.append(per_arm["instruct"] - per_arm["base"])
    return effects


@pytest.mark.parametrize("metric", ["maxmin", "meandev"])
@pytest.mark.parametrize("probe_set", sorted(PROBE_SETS))
def test_each_expected_value_specification_recomputes(metric, probe_set):
    specs = _load("results_robustness.json")["F3_specification_curve"]["specs"]
    key = f"ev|{metric}|{probe_set}"
    if key not in specs:
        pytest.skip(f"[{key}] not in the specification curve")
    stored = specs[key]

    results = _load("results_scaled.json")["results"]
    effects = _family_effects(results, PROBE_SETS[probe_set], metric)
    assert len(effects) >= 10, f"{key}: only {len(effects)} families; the panel is 13"

    recomputed_positive = f"{sum(1 for e in effects if e > 0)}/{len(effects)}"
    assert stored["families_positive"] == recomputed_positive, (
        f"{key}: stored {stored['families_positive']}, panel gives {recomputed_positive}"
    )
    mean = sum(effects) / len(effects)
    assert abs(mean - stored["mean_effect"]) < 0.002, (
        f"{key}: stored mean effect {stored['mean_effect']}, panel gives {mean:.4f}"
    )


def test_the_curve_supports_what_the_paper_says_about_it():
    """"All six give a positive mean effect (9--11/13 families positive)."""
    specs = _load("results_robustness.json")["F3_specification_curve"]["specs"]
    ev = {k: v for k, v in specs.items() if k.startswith("ev|")}
    assert len(ev) == 6, f"{len(ev)} expected-value specifications; the paper says six"

    negative = {k: v["mean_effect"] for k, v in ev.items() if v["mean_effect"] <= 0}
    assert not negative, f"the paper says every specification is positive; {negative} are not"

    counts = sorted(int(v["families_positive"].split("/")[0]) for v in ev.values())
    assert (counts[0], counts[-1]) == (9, 11), (
        f"the paper quotes 9--11 families positive; the curve spans "
        f"{counts[0]}--{counts[-1]}"
    )
