"""Does every boolean in the derived results still follow from its numbers?

The analyses record verdicts alongside the measurements that produce them:
`ci_excludes_zero` beside the interval, `frontier_below_open` beside the two
means, `monotone_increasing` beside the sequence. Downstream, the prose and the
tables read the verdict, not the numbers -- the summary table's asterisks come
from `ci_excludes_zero`, and the paper's account of which preregistered clauses
failed comes from `frontier_below_open` and its neighbours.

So a flag that stops agreeing with its own numbers is silent in exactly the way
that matters: the interval moves, the asterisk stays. Each flag here is
recomputed from the values beside it. Nothing is hand-entered -- the expected
verdict is derived, so this cannot become another copy of the same claim.

All seventeen booleans in the release were checked by hand before this was
written, and all seventeen held. This keeps them holding.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[{name}] not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def test_ci_excludes_zero_follows_from_the_interval():
    summary = _load("results_peritem.json")["summary"]
    assert summary, "no probe summaries to check"
    wrong = []
    for probe, record in summary.items():
        low, high = record["boot_ci95"]
        expected = low > 0 or high < 0
        if record["ci_excludes_zero"] != expected:
            wrong.append(
                f"{probe}: interval [{low}, {high}] excludes zero = {expected}, "
                f"flag says {record['ci_excludes_zero']}"
            )
    assert not wrong, f"the summary table's asterisks disagree with the intervals: {wrong}"


def test_the_equivalence_flag_follows_from_the_interval_and_margin():
    h3 = _load("results_robustness.json").get("H3_anchoring_equivalence")
    if not h3:
        pytest.skip("[H3] equivalence test absent")
    low, high = h3["ci90"]
    margin = float(re.search(r"margin ([\d.]+)", h3.get("note", "margin 0.15")).group(1))
    expected = -margin <= low and high <= margin
    assert h3["within_pm_0p15"] == expected, (
        f"the CI [{low}, {high}] within +/-{margin} is {expected}, but the flag "
        f"says {h3['within_pm_0p15']} -- the paper reports equivalence from this flag"
    )


def test_the_frontier_verdicts_follow_from_their_measurements():
    closed = _load("results_closed_analysis.json")
    p20b, p20c = closed.get("P20b"), closed.get("P20c")
    if not (p20b and p20c):
        pytest.skip("[P20] frontier verdicts absent")

    expected_c = p20c["frontier_mean_delta"] < p20c["open_instruct_mean_delta"]
    assert p20c["frontier_below_open"] == expected_c, (
        f"frontier {p20c['frontier_mean_delta']} vs open "
        f"{p20c['open_instruct_mean_delta']}: below = {expected_c}, flag says "
        f"{p20c['frontier_below_open']}. The paper reports this clause as failed."
    )

    expected_b = p20b["within_frontier_rho"] < 0
    assert p20b["registered_direction_negative_observed"] == expected_b, (
        f"within-frontier rho is {p20b['within_frontier_rho']}: negative = "
        f"{expected_b}, flag says {p20b['registered_direction_negative_observed']}"
    )


def test_the_growth_flags_follow_from_the_sequences():
    gran = _load("results_gran_analysis.json")
    growth = gran.get("P17a_growth")
    if not growth:
        pytest.skip("[P17a] growth measurement absent")
    for arm, record in growth.items():
        series = record["biases_by_scale"]
        expected = all(b > a for a, b in zip(series, series[1:]))
        assert record["monotone_increasing"] == expected, (
            f"{arm}: {series} is monotone increasing = {expected}, flag says "
            f"{record['monotone_increasing']}"
        )
        assert len(series) >= 3, f"{arm}: only {len(series)} scales, monotonicity is trivial"

    per_scale = gran.get("per_scale", {})
    for scale, flag in gran.get("P17b_instruct_gt_base", {}).items():
        record = per_scale.get(scale)
        if not record:
            continue
        expected = record["mean_bias_instruct"] > record["mean_bias_base"]
        assert flag == expected, (
            f"{scale}: instruct {record['mean_bias_instruct']} > base "
            f"{record['mean_bias_base']} is {expected}, flag says {flag}"
        )


def test_the_span_patch_verdict_follows_from_its_reduction():
    """P13 is met when some layer's span patch removes at least half the bias.

    This flag was not in my first pass over the release -- the coverage check
    below found it, which is what that check is for. It records whether a
    preregistered prediction was met, so it is exactly the kind of verdict that
    must not drift from the measurement underneath it.
    """
    spanpatch = _load("spanpatch_analysis.json")

    # The verdicts are nested, not top level. Finding none would make this check
    # pass by skipping -- the quiet-degradation shape -- so walk for them.
    probes = {}

    def collect(node, path):
        if isinstance(node, dict):
            if "p13_met" in node:
                probes[path or "root"] = node
            for key, value in node.items():
                collect(value, f"{path}.{key}" if path else key)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                collect(value, f"{path}[{i}]")

    collect(spanpatch, "")
    assert probes, (
        "spanpatch_analysis.json records no p13_met verdict; the preregistered "
        "span-patch prediction is reported in the paper from this file"
    )

    wrong = []
    for probe, record in probes.items():
        best = record.get("max_reduction")
        expected = best is not None and best >= 0.5
        if record["p13_met"] != expected:
            wrong.append(
                f"{probe}: max reduction {best} meets the half-bias criterion = "
                f"{expected}, flag says {record['p13_met']}"
            )
        listed = record.get("layers_with_reduction_ge_50pct")
        if listed is not None and record["p13_met"] and not listed:
            wrong.append(f"{probe}: P13 met but no layer is listed as reaching 50%")
    assert not wrong, f"span-patch verdicts disagree with their reductions: {wrong}"


def test_every_boolean_in_the_release_is_covered_or_named():
    """Vacuity guard: new flags must be checked or explicitly set aside."""
    UNCHECKED = {
        "smoke": "a run-mode marker, not a verdict about the data",
        "all_cells_gt_0p1": "summarises per-cell values the analysis does not emit",
        "all_judges_ge_half_probes": "its detail field is a string per judge, checked in prose",
    }
    found = set()
    for path in sorted(REPRO.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue

        def walk(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, bool):
                        found.add(key)
                    else:
                        walk(value)
            elif isinstance(obj, list):
                for value in obj:
                    walk(value)

        walk(data)

    checked = {
        "ci_excludes_zero", "within_pm_0p15", "frontier_below_open",
        "registered_direction_negative_observed", "monotone_increasing",
        "K3", "K5", "K10", "p13_met",
    }
    unaccounted = sorted(found - checked - set(UNCHECKED))
    assert not unaccounted, (
        f"{unaccounted} are booleans in the released results that no test "
        f"recomputes and that are not listed as deliberately unchecked"
    )
    assert len(found) >= 10, (
        f"only {len(found)} booleans found; the sweep is not reading the release"
    )
