"""Does the stage ladder's entropy actually fall where the paper says?

P8 is the preregistered claim that preference tuning sharpens the answer
distribution further, and its outcome is stated with an exception: entropy falls
at seven of the eight stage transitions, the exception being Tulu-3-8B's RLVR
step, where it rises from 0.92 to 1.11. That exception was found and written in
during an earlier pass -- the figure caption had claimed every stage sharpens --
so the count and the named exception are corrections, not original text, and
nothing recomputed either.

The stored paths sit two derivations away from the run: per-item entropies are
averaged into a per-variant mean_entropy, those into a per-probe figure, those
into a per-checkpoint one. Every check on P8 so far reads the final layer.

This rebuilds all three paths from the raw stage file, twice: once from the
stored mean_entropy per variant, and once from the per_item_entropy vectors
underneath it. Both give the same eleven checkpoints, and both reproduce the
released paths exactly.

The two-way recompute is deliberate. mean_entropy is the mean of the per-item
entropies, not the entropy of the mean distribution, and those differ by
Jensen's inequality -- confusing them produced a 278-of-390 mismatch on a
previous pass that looked like a serious defect and was entirely my own error.
Computing it both ways pins which definition the release uses.
"""

import gzip
import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _analysis():
    path = REPRO / "results_stages_analysis.json"
    if not path.exists():
        pytest.skip("[repro] stage analysis not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _raw():
    path = REPRO / "results_stages.json.gz"
    if not path.exists():
        pytest.skip("[repro] raw stage run not present")
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        return json.load(handle)["results"]


def _checkpoint_entropy(from_per_item):
    """(family, stage) -> mean entropy, averaged over probes then variants."""
    out = {}
    for _name, record in _raw().items():
        scores = record.get("scores")
        if not isinstance(scores, dict):
            continue
        per_probe = []
        for _probe, variants in scores.items():
            if from_per_item:
                if not all("per_item_entropy" in v for v in variants.values()):
                    continue
                per_probe.append(statistics.mean(
                    statistics.mean(v["per_item_entropy"]) for v in variants.values()
                ))
            else:
                if not all("mean_entropy" in v for v in variants.values()):
                    continue
                per_probe.append(statistics.mean(
                    v["mean_entropy"] for v in variants.values()
                ))
        if per_probe:
            out[(record["family"], record["stage"])] = statistics.mean(per_probe)
    if not out:
        pytest.skip("[repro] no stage checkpoints with entropy")
    return out


@pytest.mark.parametrize("from_per_item", [False, True],
                         ids=["from-mean-entropy", "from-per-item"])
def test_every_entropy_path_recomputes(from_per_item):
    paths = _analysis().get("P8_paths")
    if not paths:
        pytest.skip("[repro] no P8 paths")
    entropy = _checkpoint_entropy(from_per_item)

    wrong = []
    for family, record in paths.items():
        for stage, released in zip(record["stages"], record["entropy_path"]):
            key = (family, stage)
            if key not in entropy:
                wrong.append(f"{family}/{stage}: absent from the raw run")
                continue
            if abs(entropy[key] - released) > 0.0015:
                wrong.append(
                    f"{family}/{stage}: released {released}, recomputed {entropy[key]:.4f}"
                )
    assert not wrong, f"the stage ladder does not follow from the run: {wrong}"


def test_seven_of_eight_transitions_fall():
    """The count the paper states, and the exception it names."""
    paths = _analysis().get("P8_paths")
    if not paths:
        pytest.skip("[repro] no P8 paths")

    transitions, falling, risen = 0, 0, []
    for family, record in paths.items():
        path = record["entropy_path"]
        stages = record["stages"]
        for i, (before, after) in enumerate(zip(path, path[1:])):
            transitions += 1
            if after < before:
                falling += 1
            else:
                risen.append(f"{family} {stages[i]}->{stages[i + 1]} "
                             f"({before:.2f}->{after:.2f})")

    assert transitions == 8, (
        f"the ladder now holds {transitions} transitions; the paper says eight"
    )
    assert falling == 7, (
        f"entropy falls at {falling} of {transitions} transitions; the paper "
        f"says seven, with the exceptions being {risen}"
    )
    assert len(risen) == 1 and risen[0].startswith("Tulu-3-8B DPO->RLVR"), (
        f"the exception the paper names is Tulu-3-8B's RLVR step; the data now "
        f"says {risen}. The caption claimed every stage sharpens until this "
        f"exception was found, so it is the sentence most likely to drift back."
    )
