"""Does every scored cell carry the full variant set its Δ is computed over?

Δ is defined as the maximum inter-variant spread of mean scores. Compute it over
two variants where the design has three and it is systematically smaller -- a
spread over a subset can only be smaller than the spread over the whole set. A
cell missing one variant therefore reports a bias that is too low, in a paper
whose headline is that bias RISES, so the error is conservative in the aggregate
and invisible in the individual number.

Nothing checked it. Every other guard on this data reads what is there: the
arrays are the right length, the values are in range, the statistics recompute.
None of them can see a variant that was never written.

The one legitimate hole is recorded rather than assumed: the frontier run holds
a fourth judge with no cells at all, because no provider served its logprobs.
That exclusion is stated in the paper and in results_closed_analysis.json, so it
is allowed here only while the analysis still records it with zero cells.
"""

import collections
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

RUNS = (
    "results_scaled.json",
    "results_probes2.json",
    "results_zh.json",
    "results_14b.json",
    "results_closed.json",
)


def _cells(blob):
    """(family, arm, probe) -> the variants that carry a record."""
    found = {}
    for family, arms in blob.get("results", {}).items():
        for arm, probes in arms.items():
            if not isinstance(probes, dict):
                continue
            for probe, variants in probes.items():
                if isinstance(variants, dict):
                    found[(family, arm, probe)] = tuple(sorted(
                        name for name, record in variants.items()
                        if isinstance(record, dict)
                    ))
    return found


@pytest.mark.parametrize("name", RUNS)
def test_every_cell_has_the_full_variant_set(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    blob = json.loads(path.read_text(encoding="utf-8"))
    cells = _cells(blob)
    if not cells:
        pytest.skip(f"[{name}] holds no scored cells")

    # The expected set per probe is the one the run itself uses most often --
    # derived, so a probe that legitimately gains a variant does not need this
    # test edited, while a cell that loses one still fails.
    expected = {}
    for (_, _, probe), variants in cells.items():
        if variants:
            expected.setdefault(probe, collections.Counter())[variants] += 1
    expected = {probe: counts.most_common(1)[0][0] for probe, counts in expected.items()}

    short, empty = [], []
    for (family, arm, probe), variants in sorted(cells.items()):
        if not variants:
            empty.append(f"{family}/{arm}/{probe}")
            continue
        missing = set(expected[probe]) - set(variants)
        if missing:
            short.append(f"{family}/{arm}/{probe}: missing {sorted(missing)}")

    assert not short, (
        f"{name}: these cells are scored over fewer variants than the probe "
        f"defines, so their Δ -- a max-minus-min over variants -- is too small: "
        f"{short}"
    )

    if empty:
        excluded = json.loads(
            (REPRO / "results_closed_analysis.json").read_text()
        ).get("excluded", []) if (REPRO / "results_closed_analysis.json").exists() else []
        recorded = {entry.get("model") for entry in excluded if entry.get("cells") == 0}
        unrecorded = [c for c in empty if not any(
            model and model.split("/")[-1].lower() in c.lower() for model in recorded
        )]
        assert not unrecorded, (
            f"{name}: these cells hold no variants at all and no exclusion "
            f"record explains them: {unrecorded}"
        )


def test_the_sweep_reads_the_cells_it_claims_to():
    """Vacuity guard: a key rename would leave every check above scanning nothing."""
    total = 0
    for name in RUNS:
        path = REPRO / name
        if path.exists():
            total += len(_cells(json.loads(path.read_text(encoding="utf-8"))))
    assert total >= 200, (
        f"only {total} cells found across the released runs; the traversal no "
        f"longer matches the data's shape"
    )
