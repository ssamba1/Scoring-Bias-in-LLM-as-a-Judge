"""Do the Bayes factors say what the release says they say?

The registered per-probe test is null for all five probes, and a null p-value is
the easiest number in the paper to misread in either direction. A reader can
take it as evidence the effect is absent; an author can take it as a formality
to apologise for. Neither is right, and the Bayes factors settle which.

Recomputed here from the raw runs: no probe reaches BF01 >= 3, the conventional
threshold for moderate evidence favouring the null, and two of five sit below 1,
meaning the evidence leans -- weakly -- toward an effect. The registered nulls
are uninformative, not supportive. The equivalence bounds say the same thing
from the other side: the smallest margin the data would certify is larger than
the effects themselves, so equivalence to zero cannot be claimed at any margin
worth having.

Two things this guard protects.

The first is the direction of the reading. If a later edit turns "uninformative"
into "evidence of no effect", the numbers here contradict it.

The second is the post-hoc label. This analysis was added while auditing and is
not in PREREGISTRATION.md. A post-hoc test that quietly loses its label reads as
confirmatory, which is precisely the move this project retracted a paper over,
so the label is asserted here rather than trusted.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}


def _stored():
    path = REPRO / "results_nulls.json"
    if not path.exists():
        pytest.skip("[repro] results_nulls.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _paired_differences():
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] results_scaled.json not present")
    results = json.loads(path.read_text(encoding="utf-8", errors="replace"))["results"]
    per_probe = {probe: [] for probe in CONTROL}
    for record in results.values():
        for probe in CONTROL:
            arms = {}
            for kind in ("base", "instruct"):
                variants = (record.get(kind) or {}).get(probe)
                if not isinstance(variants, dict):
                    continue
                means = [v["mean"] for v in variants.values()]
                arms[kind] = max(means) - min(means)
            if len(arms) == 2:
                per_probe[probe].append(arms["instruct"] - arms["base"])
    return per_probe


def _mean_sd(values):
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return mean, math.sqrt(var), n


def test_the_paired_differences_are_the_ones_the_analysis_used():
    """Recompute the inputs in stdlib, independent of numpy and the analyzer."""
    stored = _stored()["per_probe"]
    for probe, values in _paired_differences().items():
        mean, sd, n = _mean_sd(values)
        assert stored[probe]["n"] == n, f"{probe}: {n} pairs, stored {stored[probe]['n']}"
        assert abs(stored[probe]["mean_difference"] - mean) < 5e-4, (
            f"{probe}: stored mean {stored[probe]['mean_difference']}, "
            f"recomputed {mean:.4f}"
        )
        t = mean / (sd / math.sqrt(n))
        assert abs(stored[probe]["t"] - t) < 5e-3, (
            f"{probe}: stored t {stored[probe]['t']}, recomputed {t:.3f}"
        )


def test_every_point_estimate_still_points_the_same_way():
    """The consistent direction is what the headline rests on, not any p."""
    negative = sorted(p for p, v in _stored()["per_probe"].items()
                      if v["mean_difference"] <= 0)
    assert not negative, (
        f"{negative} now have a non-positive mean difference. The paper's claim "
        f"is that the point estimate is positive for all five bias types; that "
        f"consistency, not any single p-value, is what carries it."
    )


def test_no_probe_is_evidence_of_absence():
    stored = _stored()
    supportive = sorted(p for p, v in stored["per_probe"].items() if v["bf01"] >= 3)
    assert supportive == stored["moderate_evidence_for_null"], (
        f"the release lists {stored['moderate_evidence_for_null']} as having "
        f"moderate evidence for the null; its own Bayes factors give {supportive}"
    )
    assert not supportive, (
        f"{supportive} now reach BF01 >= 3. If a registered null has become "
        f"evidence of absence, the paper should say so -- that is a different "
        f"and stronger claim than the one it currently makes."
    )


def test_the_equivalence_bounds_exceed_the_effects():
    """Equivalence to zero is not claimable, and the release must not imply it."""
    for probe, v in _stored()["per_probe"].items():
        assert v["equivalence_bound"] > abs(v["mean_difference"]), (
            f"{probe}: equivalence bound {v['equivalence_bound']} is no larger "
            f"than the effect {v['mean_difference']}; if the data now certify "
            f"equivalence at a meaningful margin that is a new result"
        )


def test_the_analysis_is_still_labelled_post_hoc():
    stored = _stored()
    blob = json.dumps(stored).lower()
    assert "post hoc" in blob or "post-hoc" in blob, (
        "results_nulls.json no longer records that this analysis is post hoc. "
        "It is not in PREREGISTRATION.md, and an unlabelled post-hoc test reads "
        "as confirmatory."
    )
    prereg = REPO / "paper" / "honest" / "PREREGISTRATION.md"
    if prereg.exists():
        text = prereg.read_text(encoding="utf-8", errors="replace").lower()
        assert "bayes" not in text or "amend" in text, (
            "PREREGISTRATION.md mentions Bayes factors; if this analysis was "
            "registered after all, the post-hoc label here is wrong"
        )
