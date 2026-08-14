"""Does the answer to the size-confound objection come from the data?

"The entropy-bias correlation is a capability/size confound" is among the first
objections a reader raises, and the paper's answer is a rank partial correlation
of -0.38 given log10 parameters, plus the observation that size correlates
*positively* with bias, which is the opposite direction the confound requires.
The rebuttal FAQ leads with the same two numbers.

Both were pinned as strings: README against the stored JSON, and the JSON
against nothing. A pin proves the sentence was not reworded. It cannot tell you
the partialling was done, done on the right variable, or done at all -- and
"controls for size" is the kind of claim that is either true or fatal to the
paper's central relation, with no useful middle.

So this reimplements it from the raw runs: mean answer-distribution entropy and
the max-min bias spread per cell from results_scaled.json, parameter counts from
each family's own record, all three rank-transformed, then entropy and bias each
residualised on rank(log10 params) and correlated. It reproduces -0.3816 against
a stored -0.382, and the size-bias correlation 0.1842 against a stored 0.184.

The sign of that second number matters as much as the first. A confound that
explained the relation would need size to correlate *negatively* with bias, in
the direction that would manufacture the entropy-bias link; it goes the other
way, which is why the paper can say the confound would have to work against the
observed effect.
"""

import json
import math
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PROBES = ["rubric_order", "score_id", "authority", "verbosity", "reference_answer"]


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


def _residuals(y, x):
    """y with its linear dependence on x removed."""
    mx, my = statistics.mean(x), statistics.mean(y)
    denom = sum((xi - mx) ** 2 for xi in x)
    if denom == 0:
        pytest.skip("[repro] no variation in the covariate")
    slope = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / denom
    intercept = my - slope * mx
    return [yi - (intercept + slope * xi) for xi, yi in zip(x, y)]


def _cells():
    """Per cell: mean entropy, bias spread, and the family's parameter count."""
    scaled = _load("results_scaled.json")["results"]
    entropy, bias, size = [], [], []
    for _family, arms in scaled.items():
        params = arms.get("params_b")
        for checkpoint in ("base", "instruct"):
            cell = arms.get(checkpoint)
            if not isinstance(cell, dict):
                continue
            for probe in PROBES:
                variants = cell.get(probe)
                if not isinstance(variants, dict):
                    continue
                if not all(isinstance(v, dict) and "per_item" in v
                           and "per_item_entropy" in v for v in variants.values()):
                    continue
                means = {n: statistics.mean(r["per_item"]) for n, r in variants.items()}
                bias.append(max(means.values()) - min(means.values()))
                entropy.append(statistics.mean(
                    statistics.mean(r["per_item_entropy"]) for r in variants.values()
                ))
                size.append(params)
    if not entropy:
        pytest.skip("[repro] no cells with entropy and per-item scores")
    if any(s is None for s in size):
        pytest.skip("[repro] some families declare no parameter count")
    return entropy, bias, size


def test_the_partial_correlation_recomputes():
    stored = _load("results_mechanism.json").get("size_confound_control")
    if not stored:
        pytest.skip("[repro] no size-confound record")
    entropy, bias, size = _cells()

    rank_e = _average_ranks(entropy)
    rank_b = _average_ranks(bias)
    rank_s = _average_ranks([math.log10(s) for s in size])
    partial = _pearson(_residuals(rank_e, rank_s), _residuals(rank_b, rank_s))

    expected = stored["partial_rank_rho_given_log10_params"]
    assert abs(partial - expected) <= 0.0015, (
        f"the release reports a size-partialled correlation of {expected}; "
        f"recomputing it from the raw runs gives {partial:.4f}"
    )
    assert partial < 0, (
        f"the entropy-bias relation is {partial:.3f} after partialling out "
        f"size; the paper's answer to the capability-confound objection is "
        f"that it stays negative"
    )


def test_size_correlates_positively_with_bias():
    """The direction that makes the confound story implausible."""
    stored = _load("results_mechanism.json").get("size_confound_control")
    if not stored:
        pytest.skip("[repro] no size-confound record")
    _entropy, bias, size = _cells()

    rho = _pearson(
        _average_ranks([math.log10(s) for s in size]), _average_ranks(bias)
    )
    expected = stored["size_bias_spearman_rho"]
    assert abs(rho - expected) <= 0.0015, (
        f"the release reports a size-bias correlation of {expected}; the raw "
        f"runs give {rho:.4f}"
    )
    assert rho > 0, (
        f"size now correlates {rho:.3f} with bias. The paper argues a size "
        f"confound would have to run the other way to manufacture the "
        f"entropy-bias link; a negative value here removes that argument."
    )
