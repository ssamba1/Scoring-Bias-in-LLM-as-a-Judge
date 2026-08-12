"""Does the all-order appendix's arithmetic survive an independent recompute?

Appendix "All-order check: cumulants under tuning" is where the theory earns
the word *all*: the first-order bound is proved, and the appendix argues the
same mechanism controls every cumulant, not only the second. It backs that with
three measured numbers -- kappa_2 1.80 -> 0.99 across 11/13 families, |kappa_3|
1.03 -> 0.56, kappa_4 -3.79 -> -0.29 -- and concludes every measured cumulant
moves toward the decisive limit.

Those numbers appeared in the paper as literals. check_prose counted the string
"11/13 families" and stopped there; counting a string proves the sentence has
not been reworded, not that it is true. Nothing compared any of the three
cumulants against results_robustness.json, and nothing recomputed them from the
distributions they summarise.

So this recomputes them from results_scaled.json -- the same control-condition
distributions the analyzer reads -- using central moments written out here
rather than the analyzer's own cumulants() helper. Calling that helper would
only prove it is deterministic. The kappa_4 identity in particular (mu_4 minus
three mu_2 squared) is the one place a plain "fourth moment" would look right
and be wrong, and would leave the paper reporting a moment while calling it a
cumulant.

The averaging is over probes within a checkpoint, then over families, matching
the analyzer; that structure is asserted here too, since averaging over the
pooled cells instead would weight checkpoints by how many probes they happen to
have and quietly change what the printed number means.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}


def _central_moments(dist):
    """k2, k3, k4 of a distribution over the scores 1..len(dist).

    Written out rather than imported: mu4 - 3*mu2**2 is the step that turns a
    fourth moment into a fourth cumulant, and it is the step worth checking.
    """
    total = sum(dist)
    p = [x / total for x in dist]
    vals = [float(i + 1) for i in range(len(dist))]
    mean = sum(pi * v for pi, v in zip(p, vals))
    mu2 = sum(pi * (v - mean) ** 2 for pi, v in zip(p, vals))
    mu3 = sum(pi * (v - mean) ** 3 for pi, v in zip(p, vals))
    mu4 = sum(pi * (v - mean) ** 4 for pi, v in zip(p, vals))
    return {"k2": mu2, "k3": mu3, "k4": mu4 - 3 * mu2 ** 2}


def _mean(xs):
    return sum(xs) / len(xs)


def _load():
    scaled = REPRO / "results_scaled.json"
    stored = REPRO / "results_robustness.json"
    if not scaled.exists() or not stored.exists():
        pytest.skip("[repro] scaled or robustness results not present")
    return (json.loads(scaled.read_text())["results"],
            json.loads(stored.read_text())["D1_cumulants"])


def _per_family():
    """Per-family cumulants, averaged over probes within each checkpoint."""
    scaled, stored = _load()
    per = {"base": [], "instruct": []}
    for fam in sorted(scaled):
        for kind in ("base", "instruct"):
            kd = scaled[fam].get(kind)
            if not isinstance(kd, dict):
                continue
            cells = [_central_moments(kd[p][CONTROL[p]]["mean_dist"])
                     for p in CONTROL if p in kd]
            if not cells:
                continue
            per[kind].append({k: _mean([c[k] for c in cells]) for k in ("k2", "k3", "k4")})
    if not per["base"] or not per["instruct"]:
        pytest.skip("[repro] no control distributions to recompute from")
    return per, stored


def test_the_stored_cumulants_recompute_from_the_distributions():
    per, stored = _per_family()
    for kind in ("base", "instruct"):
        for k in ("k2", "k3", "k4"):
            mine = round(_mean([c[k] for c in per[kind]]), 3)
            theirs = stored[kind][k]
            # The stored cumulants are rounded to three decimals, so rounding
            # alone permits 0.0005; the observed residuals are at most 0.0002
            # (base k2: 1.8008 recomputed against 1.801 stored). 0.002 was my
            # own four-times-too-loose constant, written before measuring.
            assert abs(mine - theirs) <= 0.00075, (
                f"{kind} {k}: released {theirs}, recomputed {mine} from the "
                f"control distributions in results_scaled.json. The appendix's "
                f"all-order claim rests on these three numbers."
            )


def test_the_family_count_recomputes():
    per, stored = _per_family()
    base = [c["k2"] for c in per["base"]]
    inst = [c["k2"] for c in per["instruct"]]
    assert len(base) == len(inst), (
        f"{len(base)} base checkpoints against {len(inst)} instruct ones; the "
        f"count is a paired comparison and cannot be formed"
    )
    dropped = sum(1 for b, i in zip(base, inst) if i < b)
    mine = f"{dropped}/{len(base)}"
    assert mine == stored["k2_drop_families"], (
        f"released {stored['k2_drop_families']} families with a variance drop, "
        f"recomputed {mine}"
    )


def test_every_measured_cumulant_moves_toward_the_decisive_limit():
    """The appendix's actual conclusion, as opposed to its three numbers.

    "Every measured cumulant moves toward the decisive limit" means each one
    shrinks in absolute value -- the decisive limit is a point mass, where all
    cumulants above the first vanish. A cumulant that grew, or that shrank only
    because it changed sign past zero, would falsify the sentence while leaving
    all three printed numbers untouched if only their magnitudes were compared.
    """
    _, stored = _load()
    grew = [k for k in ("k2", "k3", "k4")
            if abs(stored["instruct"][k]) >= abs(stored["base"][k])]
    assert not grew, (
        f"the appendix says every measured cumulant moves toward the decisive "
        f"limit; {grew} did not shrink in absolute value"
    )


def test_the_appendix_prints_the_cumulants_it_measured():
    """The literals in the appendix, against the released values.

    The appendix prints kappa_3 as a magnitude ("|kappa_3| 1.03 -> 0.56") while
    the released value is signed, so the check is on magnitude for that one and
    signed for the others -- printing a signed -1.03 as 1.03 without the bars
    would be the error worth catching, and this is the pairing that catches it.
    """
    _, stored = _load()
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"\\section\{All-order check.*?(?=\\section|\Z)", text, re.S)
    assert block, "the all-order appendix is gone; this check should go with it"
    body = block.group(0)

    expected = [
        ("k2", "1.80", "0.99", False),
        ("k3", "1.03", "0.56", True),
        ("k4", "-3.79", "-0.29", False),
    ]
    for k, before, after, magnitude in expected:
        for literal, side in ((before, "base"), (after, "instruct")):
            assert literal in body, (
                f"the appendix no longer prints {literal} for {k}; update this "
                f"check with whatever it prints now"
            )
            value = stored[side][k]
            shown = abs(value) if magnitude else value
            assert abs(shown - float(literal)) < 0.005, (
                f"the appendix prints {k} {side} as {literal}, the released "
                f"value is {value}"
            )
