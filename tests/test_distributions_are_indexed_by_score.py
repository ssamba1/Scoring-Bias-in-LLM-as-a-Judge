"""Is every stored distribution indexed the way the code that reads it assumes?

The harness stores each variant's answer distribution in TOKEN order and its
expected score under the token->score map. For every variant those two orders
coincide, except one: score_id's "letter" variant offers the tokens A..E, which
map to scores 5..1. Its `mean_dist` is therefore descending where every other
variant's is ascending.

Nothing recorded that. Three analyses took a total-variation distance between a
control distribution and each perturbed one by zipping the two lists, which for
score_id measured the distance between P(score 1) and P(score 5). It inflated
score_id's responsiveness by about a sixth and moved five published numbers.

The check that finds it is one line of arithmetic: expected score is linear in
the distribution, so sum(p_i * score_i) must equal the stored mean for every
variant. Under the wrong index assumption the letter variants miss by up to
3.2 on a 1-5 scale -- not a subtle disagreement, just one nobody had asked for.

This is the check that breaks the circle. Two independent reimplementations
agreed with the analysis and with each other, because all three shared the
assumption; agreement between implementations tests the code, and only an
appeal to something outside them -- here, the identity between a distribution
and its own mean -- tests the assumption.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Variants whose distribution is stored in descending score order, because the
# tokens they offer run from best to worst.
DESCENDING = {("score_id", "letter")}

# Files holding a family -> arm -> probe -> variant tree of scored cells, with
# whether the run is required to carry distributions at all. Only the main panel
# is: the others store means and entropies without the full vectors, and a run
# that never stored a distribution cannot have misindexed one.
RUNS = [("results_scaled.json", True),
        ("results_multitemplate.json", False),
        ("results_zh.json", False)]


def _cells(node, probe=None, depth=0):
    """Yield (probe, variant, record) for every variant record in a run."""
    if depth > 4 or not isinstance(node, dict):
        return
    for key, value in node.items():
        if not isinstance(value, dict):
            continue
        if "mean_dist" in value and "mean" in value:
            yield probe, key, value
        else:
            yield from _cells(value, key, depth + 1)


def _scores(distribution, probe, variant):
    n = len(distribution)
    if (probe, variant) in DESCENDING:
        return list(range(n, 0, -1))
    return list(range(1, n + 1))


@pytest.mark.parametrize("filename,required", RUNS)
def test_each_distribution_reproduces_its_own_mean(filename, required):
    path = REPRO / filename
    if not path.exists():
        pytest.skip(f"[repro] {filename} not present")
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    results = payload.get("results")
    if not isinstance(results, dict):
        pytest.skip(f"[repro] {filename} has no results tree")

    checked, wrong = 0, []
    for probe, variant, record in _cells(results):
        distribution = record["mean_dist"]
        if not distribution or abs(sum(distribution) - 1.0) > 0.01:
            continue
        scores = _scores(distribution, probe, variant)
        expected = sum(p * s for p, s in zip(distribution, scores))
        checked += 1
        # Distributions are rounded to four decimals and the mean is a mean of
        # per-item expectations, so allow a little slack -- but only a little,
        # because the failure this guards against is off by whole points.
        if abs(expected - record["mean"]) > 0.02:
            wrong.append(
                f"{probe}/{variant}: distribution implies {expected:.3f}, "
                f"stored mean is {record['mean']:.3f}"
            )

    if not checked:
        if required:
            pytest.fail(
                f"{filename} carries no answer distributions. The main panel's "
                f"responsiveness term is computed from them, so their absence "
                f"means this check silently covers nothing"
            )
        pytest.skip(f"[repro] {filename} stores no distributions")
    assert not wrong, (
        f"{len(wrong)} of {checked} distributions in {filename} disagree with "
        f"their own stored mean, so they are not indexed by the score order "
        f"assumed here: {wrong[:6]}. Any comparison between two variants' "
        f"distributions -- total variation, and so every responsiveness "
        f"figure -- is measuring across misaligned supports."
    )


def test_the_descending_variant_is_actually_descending():
    """The exemption must stay earned, not become folklore."""
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] results_scaled.json not present")
    results = json.loads(path.read_text(encoding="utf-8", errors="replace"))["results"]

    ascending_fits, descending_fits = 0, 0
    for probe, variant, record in _cells(results):
        if (probe, variant) not in DESCENDING:
            continue
        distribution = record["mean_dist"]
        n = len(distribution)
        up = sum(p * s for p, s in zip(distribution, range(1, n + 1)))
        down = sum(p * s for p, s in zip(distribution, range(n, 0, -1)))
        ascending_fits += abs(up - record["mean"]) <= 0.02
        descending_fits += abs(down - record["mean"]) <= 0.02

    assert descending_fits and not ascending_fits, (
        f"the letter variant is listed as descending, but {ascending_fits} of "
        f"its cells fit an ascending reading and {descending_fits} fit a "
        f"descending one. If the harness changed to store score order "
        f"directly, this exemption now reverses a distribution that was "
        f"already correct"
    )
