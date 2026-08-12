"""Does the paper's central correlation recompute from the points beside it?

"Confidence Is Not Robustness" rests on one number: across 130 model x probe
cells, entropy correlates negatively with bias, rho = -0.41. The released data
carries both that number and the 130 (entropy, delta) pairs it came from, and
nothing had ever computed one from the other. Every check read the stored
rho -- the paper matches the JSON, the JSON regenerates from the raw runs, the
raw runs are well formed -- which is a closed circle: an analysis that is
consistently wrong satisfies all of it.

So this ranks the pairs and correlates them here, with average ranks for ties
and Pearson on the ranks, importing nothing from the analyzer. The same is done
for the responsiveness link (+0.82), which the paper leans on just as hard when
it argues responsiveness rather than decisiveness is what bias tracks, and for
the variance-term link (-0.25).

Ties are the reason to write the ranking out rather than reach for a library
call: entropies repeat across cells, and a naive ordinal rank silently reports a
different statistic from the average-rank Spearman the analyzer uses.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# (points key, x field, y field, stored statistic key) -- each is a claim the
# paper makes in its own sentence.
LINKS = (
    ("link_points", "entropy", "delta", "entropy_bias_link"),
    ("responsiveness_link_points", "resp", "delta", "responsiveness_bias_link"),
)

TOLERANCE = 0.0006  # the stored rho is rounded to three decimals


def _mechanism():
    path = REPRO / "results_mechanism.json"
    if not path.exists():
        pytest.skip("[repro] results_mechanism.json not present")
    return json.loads(path.read_text())


def _average_ranks(values):
    """Ranks with ties averaged -- the definition Spearman's rho assumes."""
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
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx ** 0.5 * syy ** 0.5)


def _spearman(xs, ys):
    return _pearson(_average_ranks(xs), _average_ranks(ys))


@pytest.mark.parametrize("points_key,x_field,y_field,stat_key", LINKS,
                         ids=[link[3] for link in LINKS])
def test_the_correlation_recomputes_from_its_own_points(points_key, x_field, y_field, stat_key):
    mech = _mechanism()
    points = mech.get(points_key)
    stored = mech.get(stat_key)
    if not isinstance(points, dict) or not isinstance(stored, dict):
        pytest.skip(f"[repro] {points_key} or {stat_key} is not in the release")

    xs, ys = points.get(x_field), points.get(y_field)
    assert isinstance(xs, list) and isinstance(ys, list), (
        f"{points_key} does not carry {x_field} and {y_field} as lists"
    )
    assert len(xs) == len(ys) == stored["n"], (
        f"{stat_key} reports n={stored['n']} over {len(xs)} and {len(ys)} points"
    )

    mine = _spearman(xs, ys)
    assert mine is not None, f"{points_key}: a coordinate has no variance"
    assert abs(mine - stored["spearman_rho"]) <= TOLERANCE, (
        f"{stat_key}: the release stores rho = {stored['spearman_rho']}, the "
        f"points beside it give {mine:.4f}. This is the number the paper's "
        f"title rests on."
    )


def test_the_ranking_handles_ties_the_way_spearman_does():
    """Vacuity guard for the helper: on a tied vector, ordinal ranking and
    average ranking give different answers, and only one of them is Spearman."""
    tied = [1.0, 2.0, 2.0, 3.0]
    assert _average_ranks(tied) == [1.0, 2.5, 2.5, 4.0], _average_ranks(tied)
    # A perfectly monotone relation with a tie is not rho = 1.
    assert abs(_spearman(tied, [1.0, 2.0, 3.0, 4.0]) - 0.9486832980505138) < 1e-9


def test_the_out_of_sample_r2_recomputes_from_its_predictions():
    """P5's claim -- entropy predicts a held-out judge's bias -- from its points.

    The release stores the leave-one-family-out R^2 beside the 26 (actual,
    predicted) pairs it summarises, and nothing recomputed one from the other.

    The check also separates R^2 from r^2, which is the error that would be
    easiest to make and hardest to see: the squared correlation here is 0.301,
    the variance-explained R^2 is 0.272, and both are plausible numbers to find
    printed beside "R^2". They are different claims -- r^2 ignores whether the
    predictions are on the right scale, R^2 does not -- and only one of them
    supports "predictable out-of-sample".
    """
    mech = _mechanism()
    predictor = mech.get("predictor")
    if not isinstance(predictor, dict) or "points" not in predictor:
        pytest.skip("[repro] the predictor points are not in the release")
    points = predictor["points"]
    actual, predicted = points.get("actual"), points.get("predicted")
    assert isinstance(actual, list) and isinstance(predicted, list), (
        "the predictor does not carry actual and predicted as lists"
    )
    assert len(actual) == len(predicted) == predictor["n_models"], (
        f"the predictor reports {predictor['n_models']} models over "
        f"{len(actual)} actual and {len(predicted)} predicted values"
    )

    n = len(actual)
    mean_actual = sum(actual) / n
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)
    assert ss_tot > 0, "the held-out biases have no variance to explain"
    r2 = 1 - ss_res / ss_tot
    assert abs(r2 - predictor["loo_r2"]) <= 0.0006, (
        f"the release stores LOO R^2 = {predictor['loo_r2']}, its own "
        f"predictions give {r2:.4f}"
    )

    r = _pearson(actual, predicted)
    assert abs(r - predictor["loo_pearson_r"]) <= 0.0006, (
        f"the release stores r = {predictor['loo_pearson_r']}, its points give {r:.4f}"
    )
    assert abs(r ** 2 - predictor["loo_r2"]) > 0.006, (
        f"the stored R^2 ({predictor['loo_r2']}) is indistinguishable from the "
        f"squared correlation ({r ** 2:.4f}); these are different claims and the "
        f"paper makes the stronger one"
    )

    rho = _spearman(actual, predicted)
    assert abs(rho - predictor["loo_spearman_rho"]) <= 0.0006, (
        f"the release stores rank correlation {predictor['loo_spearman_rho']}, "
        f"its points give {rho:.4f}"
    )


def test_the_headline_relation_is_still_negative():
    """The sign is the claim; the magnitude is the evidence for it."""
    mech = _mechanism()
    link = mech.get("entropy_bias_link")
    if not isinstance(link, dict):
        pytest.skip("[repro] the entropy-bias link is not in the release")
    assert link["spearman_rho"] < 0, (
        f"the entropy-bias correlation is {link['spearman_rho']}; the paper's "
        f"whole argument is that it is negative"
    )
