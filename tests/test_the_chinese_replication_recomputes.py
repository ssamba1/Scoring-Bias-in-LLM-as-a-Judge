"""Does the Chinese replication replicate, in its own numbers?

P11 asks whether the effect survives a different language. The released answer
is that it does: instruction tuning raises bias in 4 of 4 Qwen families on
Chinese items, and the entropy-bias relation reproduces at rho = -0.355 over 40
cells. Both appear in the paper as evidence that the finding is not an artifact
of English prompts.

Neither was recomputed. check_prose pins the string "4/4" so the sentence cannot
drift from the release, and a separate test checks the Chinese items are
actually Chinese -- but nothing asked whether four families really come out
positive, or what the correlation is. A single family flipping sign turns 4/4
into 3/4 and leaves every existing check passing, because the pinned string and
the stored value would move together.

Recomputed from results_zh.json: per family and checkpoint, the max-min bias
spread per probe and the mean of the variants' mean_entropy; the family effect
as instruct minus base averaged over probes; then average-rank Spearman over the
40 cells. It reproduces all four effects to three decimals -- +0.598, +0.115,
+0.691, +0.323 -- and rho = -0.3553 against a stored -0.355.

Qwen2.5-1.5B is worth naming: its effect is +0.115, the smallest of the four and
the one a sign flip would reach first. The count is what the paper claims, so
the count is asserted, not just the values.
"""

import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


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


def _rebuild():
    """Cell-level entropy and bias, plus each family's instruct-minus-base effect."""
    results = _load("results_zh.json").get("results", {})
    entropy, bias, effects = [], [], {}
    for family, arms in results.items():
        if not isinstance(arms, dict):
            continue
        by_checkpoint = {}
        for checkpoint in ("base", "instruct"):
            cell = arms.get(checkpoint)
            if not isinstance(cell, dict):
                continue
            spreads = []
            for _probe, variants in cell.items():
                if not isinstance(variants, dict):
                    continue
                usable = [v for v in variants.values()
                          if isinstance(v, dict) and "mean" in v and "mean_entropy" in v]
                if len(usable) < 2:
                    continue
                means = [v["mean"] for v in usable]
                spread = max(means) - min(means)
                spreads.append(spread)
                bias.append(spread)
                entropy.append(statistics.mean(v["mean_entropy"] for v in usable))
            if spreads:
                by_checkpoint[checkpoint] = statistics.mean(spreads)
        if len(by_checkpoint) == 2:
            effects[family] = by_checkpoint["instruct"] - by_checkpoint["base"]
    if not entropy:
        pytest.skip("[repro] no Chinese cells")
    return entropy, bias, effects


def test_every_family_effect_recomputes():
    stored = _load("results_zh_analysis.json").get("per_family_effect")
    if not stored:
        pytest.skip("[repro] no per-family record")
    _entropy, _bias, effects = _rebuild()

    assert set(effects) == set(stored), (
        f"the release reports {sorted(stored)}; the raw run holds {sorted(effects)}"
    )
    wrong = [
        f"{family}: released {stored[family]}, recomputed {value:.3f}"
        for family, value in effects.items()
        if abs(value - stored[family]) > 0.0015
    ]
    assert not wrong, f"the Chinese family effects do not follow from the run: {wrong}"


def test_all_four_families_are_positive():
    """The claim is a count, so the count is what is checked."""
    _entropy, _bias, effects = _rebuild()
    negative = {f: round(v, 3) for f, v in effects.items() if v <= 0}
    assert not negative, (
        f"{negative} no longer show a positive tuning effect on Chinese items. "
        f"The paper reports 4 of 4, and that count is the replication claim; "
        f"the smallest is Qwen2.5-1.5B at about +0.12, so it moves first."
    )
    assert len(effects) == 4, (
        f"the replication now covers {len(effects)} families, not the four the "
        f"paper describes"
    )


def test_the_entropy_bias_link_recomputes():
    stored = _load("results_zh_analysis.json").get("entropy_bias_link")
    if not stored:
        pytest.skip("[repro] no entropy-bias record")
    entropy, bias, _effects = _rebuild()

    assert len(entropy) == stored["n"], (
        f"the release correlates {stored['n']} Chinese cells; the run gives "
        f"{len(entropy)}"
    )
    rho = _pearson(_average_ranks(entropy), _average_ranks(bias))
    assert abs(rho - stored["spearman_rho"]) <= 0.0015, (
        f"the release reports rho = {stored['spearman_rho']} on Chinese items; "
        f"recomputing gives {rho:.4f}"
    )
    assert rho < 0, (
        f"the entropy-bias relation is {rho:.3f} on Chinese items. The point of "
        f"this replication is that the negative relation is not an artifact of "
        f"English prompts."
    )
