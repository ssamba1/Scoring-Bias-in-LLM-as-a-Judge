"""Does the continuous readout agree with the discrete one, as claimed?

The paper measures bias from the answer distribution rather than from the
argmax, which is the choice a skeptical reader questions first: it is not how a
deployed judge behaves. The answer is a concordance -- across all 130 cells, the
expected-value bias correlates rho = 0.557 with the flip rate, the fraction of
items whose argmax actually moves between variants. It appears in the release's
behavioural-validity block for exactly that purpose.

Only its n was checked. A test confirmed the correlation ran over the full panel
of 130 cells and said nothing about the value, so a concordance of 0.05 would
have passed while the claim it supports collapsed.

Recomputed here from the raw runs. The flip rate is rebuilt from per_item_argmax
-- the fraction of items whose argmax differs from the control variant's,
averaged over the non-control variants -- and the bias spread from the variant
means, then correlated by average-rank Spearman. It reproduces 0.5567 against a
stored 0.557, and 0.5564 when the variant means are themselves recomputed from
per_item rather than read from the stored mean.

Getting there needed the control variant of each probe, and guessing them was
wrong for two: score_id's control is "numeric" and verbosity's is "control",
not the "control"/"none" pattern the other three follow. Guessing produced a
concordance of 0.46 over 78 cells -- a plausible-looking number from silently
skipping two fifths of the panel, which is the failure mode this file is
otherwise about.
"""

import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Each probe's unperturbed variant. Not a uniform name -- see the docstring.
CONTROL = {
    "rubric_order": "control",
    "score_id": "numeric",
    "reference_answer": "none",
    "authority": "none",
    "verbosity": "control",
}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = shared
        i = j + 1
    return ranks


def _pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    if den == 0:
        pytest.skip("[repro] degenerate spread")
    return num / den


def _bias_and_flip(from_per_item):
    scaled = _load("results_scaled.json")["results"]
    bias, flip = [], []
    for _family, arms in scaled.items():
        for checkpoint in ("base", "instruct"):
            cell = arms.get(checkpoint)
            if not isinstance(cell, dict):
                continue
            for probe, control in CONTROL.items():
                variants = cell.get(probe)
                if not isinstance(variants, dict) or control not in variants:
                    continue
                if not all("per_item_argmax" in v for v in variants.values()):
                    continue
                if from_per_item:
                    means = {n: statistics.mean(v["per_item"]) for n, v in variants.items()}
                else:
                    means = {n: v["mean"] for n, v in variants.items()}
                bias.append(max(means.values()) - min(means.values()))

                reference = variants[control]["per_item_argmax"]
                moved = [
                    statistics.mean(
                        [1 if a != b else 0
                         for a, b in zip(reference, v["per_item_argmax"])]
                    )
                    for name, v in variants.items() if name != control
                ]
                flip.append(statistics.mean(moved))
    if not bias:
        pytest.skip("[repro] no cells with argmax vectors")
    return bias, flip


def test_the_panel_is_whole():
    """78 cells instead of 130 is what a wrong control name looks like."""
    stored = _load("results_robustness.json").get("B4_readout_concordance")
    if not stored:
        pytest.skip("[repro] no concordance record")
    bias, _flip = _bias_and_flip(from_per_item=False)
    assert len(bias) == stored["n"], (
        f"the release correlates {stored['n']} cells; this reconstruction "
        f"found {len(bias)}. A control variant that does not resolve drops its "
        f"probe silently and the correlation still returns a plausible number."
    )


@pytest.mark.parametrize("from_per_item", [False, True], ids=["stored-mean", "per-item-mean"])
def test_the_concordance_recomputes(from_per_item):
    stored = _load("results_robustness.json").get("B4_readout_concordance")
    if not stored:
        pytest.skip("[repro] no concordance record")
    bias, flip = _bias_and_flip(from_per_item)
    rho = _pearson(_average_ranks(bias), _average_ranks(flip))

    assert abs(rho - stored["spearman_evbias_fliprate"]) <= 0.0015, (
        f"the release reports a concordance of "
        f"{stored['spearman_evbias_fliprate']}; recomputing it from the raw "
        f"runs gives {rho:.4f}"
    )
    assert rho > 0.3, (
        f"the expected-value readout and the discrete flip rate agree at only "
        f"{rho:.3f}. The paper measures bias from the distribution rather than "
        f"the argmax, and this concordance is what answers the objection that "
        f"it therefore measures something a deployed judge would not do."
    )
