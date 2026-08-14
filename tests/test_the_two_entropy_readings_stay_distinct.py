"""Does each entropy claim use the reading it says it uses?

The mechanism section uses entropy twice, and not the same way both times. The
decisiveness *shift* -- 2.04 to 1.45 bits -- is the control variant's entropy,
the judge's answer distribution when nothing has been injected. The entropy-bias
*correlation* is the mean over a probe's variants, because a correlation with a
probe's bias should use that probe's own conditions. The paper states the
distinction inline: "here the mean over a probe's variants, not the control
variant used for the shift above".

Reimplementing this without reading that parenthetical gives 2.04 to 1.505 for
the shift -- base matches, instruct is off by 0.055 -- which looks like a
rounding disagreement rather than the wrong estimator. That is how this kind of
error survives review: the number is close enough to argue about and wrong
enough to matter.

Both readings are correct as used, and both are checked here, along with the
gap between them. Pinning them separately is the point. If someone later
"fixes" the shift to use the same estimator as the correlation, every sentence
still reads sensibly and 1.45 quietly becomes 1.51.

The responsiveness half of the decomposition is checked the same way: its
correlation with bias pooled and within each arm, and -- the claim the
corollary's division of labour actually rests on -- that responsiveness ranks
probes *within* a checkpoint where entropy does not.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# The unperturbed variant of each probe, as analyze_robustness.py defines it.
# These are not guessable: score_id's control is "numeric", not "control".
CONTROL = {
    "rubric_order": "control",
    "score_id": "numeric",
    "reference_answer": "none",
    "authority": "none",
    "verbosity": "control",
}


def _results():
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] results_scaled.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))["results"]


def _average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = shared
        i = j + 1
    return ranks


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return 0.0 if dx == 0 or dy == 0 else num / (dx * dy)


def _spearman(xs, ys):
    return _pearson(_average_ranks(xs), _average_ranks(ys))


def _total_variation(p, q):
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def _cells():
    """One record per (family, checkpoint, probe) with both entropy readings."""
    rows = []
    for family, record in _results().items():
        for kind in ("base", "instruct"):
            for probe, variants in (record.get(kind) or {}).items():
                if probe not in CONTROL or not isinstance(variants, dict):
                    continue
                control = variants.get(CONTROL[probe])
                if not control or "mean_dist" not in control:
                    continue
                means = [v["mean"] for v in variants.values()]
                perturbed = [v for name, v in variants.items() if name != CONTROL[probe]]
                rows.append({
                    "family": family,
                    "kind": kind,
                    "probe": probe,
                    "control_entropy": control["mean_entropy"],
                    "variant_entropy": (sum(v["mean_entropy"] for v in variants.values())
                                        / len(variants)),
                    "bias": max(means) - min(means),
                    "responsiveness": (sum(_total_variation(control["mean_dist"],
                                                            v["mean_dist"])
                                           for v in perturbed) / len(perturbed)),
                })
    return rows


def _arm_mean(rows, kind, field):
    sel = [r[field] for r in rows if r["kind"] == kind]
    return sum(sel) / len(sel)


def test_the_control_variants_are_the_ones_the_analysis_uses():
    """This file restates CONTROL; it must not drift from the definition.

    Restating rather than importing is deliberate -- a test that imports the
    number it checks verifies nothing. But a restatement that silently
    disagrees with the analysis is worse than either, so the two are compared
    directly. Reading the literal out of the source rather than importing the
    module also keeps this test free of the analysis's dependencies.
    """
    import ast

    source = REPRO / "analyze_robustness.py"
    if not source.exists():
        pytest.skip("[repro] analyze_robustness.py not present")

    declared = None
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8", errors="replace"))):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CONTROL" for t in node.targets):
            declared = ast.literal_eval(node.value)
            break

    assert declared == CONTROL, (
        f"the analysis treats {declared} as each probe's unperturbed variant; "
        f"this file assumes {CONTROL}. Every responsiveness number here is a "
        f"shift measured *from* that variant, so a disagreement means the "
        f"tests and the paper are describing different baselines"
    )


def test_the_decisiveness_shift_is_the_control_variant():
    rows = _cells()
    assert len(rows) == 130, f"{len(rows)} cells, not 130"

    base = _arm_mean(rows, "base", "control_entropy")
    instruct = _arm_mean(rows, "instruct", "control_entropy")
    assert abs(base - 2.04) < 0.005, f"base control entropy is {base:.3f}, not 2.04"
    assert abs(instruct - 1.45) < 0.005, (
        f"instruct control entropy is {instruct:.3f}, not 1.45"
    )

    families = sorted({r["family"] for r in rows})
    fell = 0
    for family in families:
        arms = {}
        for kind in ("base", "instruct"):
            sel = [r["control_entropy"] for r in rows
                   if r["family"] == family and r["kind"] == kind]
            arms[kind] = sum(sel) / len(sel)
        fell += arms["instruct"] < arms["base"]
    assert (fell, len(families)) == (11, 13), (
        f"control entropy falls in {fell}/{len(families)} families; the paper "
        f"reports 11/13, and the two exceptions are why it is not 'all'"
    )


def test_the_other_reading_would_give_a_different_shift():
    """The two readings must not be silently interchangeable."""
    rows = _cells()
    wrong = _arm_mean(rows, "instruct", "variant_entropy")
    right = _arm_mean(rows, "instruct", "control_entropy")
    assert abs(wrong - right) > 0.03, (
        f"the mean-over-variants reading now gives {wrong:.3f} against the "
        f"control variant's {right:.3f}. The paper distinguishes them "
        f"explicitly; if they have converged, the parenthetical that tells a "
        f"reader which is which no longer marks a real difference"
    )
    assert abs(wrong - 1.505) < 0.01, (
        f"the mean-over-variants instruct entropy is {wrong:.3f}; using it for "
        f"the shift would print 1.51 where the paper says 1.45"
    )


def test_both_entropy_correlations_recompute():
    rows = _cells()
    bias = [r["bias"] for r in rows]

    variant = _spearman([r["variant_entropy"] for r in rows], bias)
    assert abs(variant - (-0.41)) < 0.01, (
        f"the mean-over-variants entropy-bias correlation is {variant:.3f}; "
        f"the paper's headline is -0.41"
    )

    control = _spearman([r["control_entropy"] for r in rows], bias)
    assert abs(control - (-0.34)) < 0.01, (
        f"the control-variant entropy-bias correlation is {control:.3f}; the "
        f"paper reports -0.34 and uses it to show the relation does not depend "
        f"on which entropy reading is taken"
    )


def test_responsiveness_tracks_bias_in_both_arms():
    rows = _cells()
    pooled = _spearman([r["responsiveness"] for r in rows], [r["bias"] for r in rows])
    assert abs(pooled - 0.82) < 0.01, (
        f"the responsiveness-bias correlation is {pooled:.3f}; the paper "
        f"reports +0.82, far tighter than decisiveness's -0.41, which is the "
        f"decomposition's main empirical claim"
    )
    for kind, expected in (("base", 0.80), ("instruct", 0.81)):
        sel = [r for r in rows if r["kind"] == kind]
        rho = _spearman([r["responsiveness"] for r in sel], [r["bias"] for r in sel])
        assert abs(rho - expected) < 0.015, (
            f"within {kind} judges the responsiveness-bias correlation is "
            f"{rho:.3f}; the paper reports {expected}, and the point is that it "
            f"is a continuous property rather than a base/instruct difference"
        )

    base = _arm_mean(rows, "base", "responsiveness")
    instruct = _arm_mean(rows, "instruct", "responsiveness")
    assert abs(base - 0.14) < 0.006 and abs(instruct - 0.26) < 0.006, (
        f"mean responsiveness is {base:.3f} then {instruct:.3f}; the paper "
        f"reports 0.14 to 0.26"
    )


def test_responsiveness_ranks_probes_within_a_checkpoint():
    """Where entropy is null, responsiveness is not -- the corollary's claim."""
    rows = _cells()
    per_checkpoint = []
    for family in sorted({r["family"] for r in rows}):
        for kind in ("base", "instruct"):
            sel = [r for r in rows if r["family"] == family and r["kind"] == kind]
            if len(sel) < 3:
                continue
            per_checkpoint.append(
                _spearman([r["responsiveness"] for r in sel], [r["bias"] for r in sel])
            )

    assert len(per_checkpoint) == 26, f"{len(per_checkpoint)} checkpoints, not 26"
    mean = sum(per_checkpoint) / len(per_checkpoint)
    positive = sum(1 for v in per_checkpoint if v > 0)
    assert abs(mean - 0.64) < 0.02, (
        f"the mean within-checkpoint responsiveness-bias correlation is "
        f"{mean:.3f}; the paper reports +0.64"
    )
    assert positive == 24, (
        f"responsiveness ranks probes correctly in {positive}/26 checkpoints; "
        f"the paper reports 24/26. This is the half of the decomposition that "
        f"is *not* null within a judge, which is what assigns responsiveness to "
        f"the judge x perturbation level"
    )
