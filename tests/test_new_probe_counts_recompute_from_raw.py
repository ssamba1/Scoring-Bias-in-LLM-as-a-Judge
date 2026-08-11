"""Do the new-probe summaries follow from the runs they claim to summarise?

analyze_newprobes reduces three raw runs to per-probe summaries: the two
preregistered extension probes (sycophancy, anchoring), the Chinese-items
replication, and the 14B extension. The paper reports these as adjudications --
"sycophancy confirms, anchoring refuses", "positive for 3/5 probes at 14B" --
and the previous round showed that a summary sitting next to its inputs is not
the same as a summary derived from them.

Here the inputs are a raw run rather than a sibling field, so the recomputation
crosses from the analysis back to the measurement: per family, the change in
bias is the instruct spread minus the base spread, where the spread is the
max-minus-min over a probe's variants. Counting the positives reproduces
`families_positive`, and averaging reproduces `mean_change`.

That closes the loop analyze_newprobes opens, and it is the loop that matters
for a preregistered claim: the registry says what would count as confirmation,
the analysis says whether it happened, and until now nothing checked the second
against the data.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# analysis file -> the raw run it reduces
PAIRS = {
    "results_probes2_analysis.json": "results_probes2.json",
    "results_zh_analysis.json": "results_zh.json",
    "results_14b_analysis.json": "results_14b.json",
}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[{name}] not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _spread(cell):
    """Max-minus-min of a probe's variant means: the bias for that cell."""
    means = [v["mean"] for v in cell.values() if isinstance(v, dict) and "mean" in v]
    return max(means) - min(means) if len(means) >= 2 else None


def _per_family_change(results, probe):
    changes = {}
    for family, arms in results.items():
        base, instruct = arms.get("base"), arms.get("instruct")
        if not (isinstance(base, dict) and isinstance(instruct, dict)):
            continue
        if probe not in base or probe not in instruct:
            continue
        b, i = _spread(base[probe]), _spread(instruct[probe])
        if b is None or i is None:
            continue
        changes[family] = i - b
    return changes


@pytest.mark.parametrize("analysis,raw", sorted(PAIRS.items()))
def test_per_probe_counts_recompute_from_the_raw_run(analysis, raw):
    summaries = _load(analysis).get("per_probe")
    if not summaries:
        pytest.skip(f"[{analysis}] carries no per-probe summaries")
    results = _load(raw)["results"]

    checked = 0
    wrong = []
    for probe, stored in summaries.items():
        changes = _per_family_change(results, probe)
        if not changes:
            wrong.append(f"{probe}: no family in {raw} yields a change; the summary rests on nothing")
            continue
        checked += 1
        recomputed = f"{sum(1 for v in changes.values() if v > 0)}/{len(changes)}"
        if stored["families_positive"] != recomputed:
            wrong.append(
                f"{probe}: stored {stored['families_positive']}, "
                f"the raw run gives {recomputed}"
            )
        mean = sum(changes.values()) / len(changes)
        if abs(mean - stored["mean_change"]) > 0.002:
            wrong.append(
                f"{probe}: stored mean change {stored['mean_change']}, "
                f"recomputed {mean:.4f}"
            )
        if stored["n_families"] != len(changes):
            wrong.append(
                f"{probe}: n_families says {stored['n_families']}, the raw run "
                f"has {len(changes)}"
            )
    assert not wrong, f"{analysis} does not follow from {raw}: {wrong}"
    assert checked, f"{analysis}: nothing was recomputed, so this check is vacuous"
