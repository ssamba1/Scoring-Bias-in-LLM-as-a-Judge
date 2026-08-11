r"""The README's numbers, pinned to the results they came from.

The README is the first thing anyone reads and the last thing anyone regenerates.
It restates a dozen headline figures in its own words, maintained by hand, with
nothing connecting them to the analyses -- the same standing the paper's prose
had before check_prose.py existed. Every figure in it currently agrees with the
data; that is the reason to pin them now rather than after one has drifted.

Each case reads the claim out of the README with a pattern, reads the true value
out of the derived JSON, and compares. Nothing is typed here: the expected value
comes from the results, and the claim comes from the README, so this file cannot
turn into a third hand-maintained copy of the same numbers.

Where the README rounds harder than the source -- "+0.16" for 0.1559, "22%" for
0.216 -- the comparison rounds the source the same way. Rounding is not
disagreement; a check that failed on it would be reporting its own strictness.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
README = REPO / "README.md"


def _json(name):
    path = REPRO / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


MECH = _json("results_mechanism.json") or {}
ROB = _json("results_robustness.json") or {}


def _at(root, dotted):
    node = root
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


# (label, regex with one numeric group, source, dotted path, decimals)
CLAIMS = [
    ("entropy before tuning", r"entropy (\d\.\d\d) ->", MECH, "decisiveness.base_mean", 2),
    ("entropy after tuning", r"entropy \d\.\d\d -> (\d\.\d\d)", MECH, "decisiveness.instruct_mean", 2),
    ("mixed-effects coefficient", r"instruct coef \*\*\+(\d\.\d\d)", MECH, "lmm.instruct_coef", 2),
    ("exact permutation p", r"\*\*p=(\d\.\d+)\*\*", ROB, "F1_exact_permutation.exact_p_two_sided", 5),
    ("entropy-bias correlation", r"rho=(-\d\.\d\d) pooled", MECH, "entropy_bias_link.spearman_rho", 2),
    ("size-partialled correlation", r"pooled; (-\d\.\d\d) partialling", MECH,
     "size_confound_control.partial_rank_rho_given_log10_params", 2),
    ("within-judge correlation", r"within-judge rho=\+(\d\.\d\d)", ROB,
     "B1_within_checkpoint_responsiveness.mean_within_rho", 2),
    ("responsiveness before", r"TV (\d\.\d\d)->", MECH, "responsiveness.base_mean", 2),
    ("responsiveness after", r"TV \d\.\d\d->(\d\.\d\d)", MECH, "responsiveness.instruct_mean", 2),
    ("responsiveness effect size", r"d_z=(\d\.\d\d)", MECH, "responsiveness.dz", 2),
    ("public-item correlation", r"Dolly-15k items \(7/8 families, rho=(-\d\.\d\d)\)", ROB,
     "C5_public_items.entropy_bias_rho", 2),
    ("predictor rank correlation", r"\(rho=(\d\.\d\d)\)", MECH, "predictor.loo_spearman_rho", 2),
    ("expected-value mitigation", r"\((\d\.\d\d) -> 1\.88\)", MECH, "mitigation.expected", 2),
    ("argmax readout", r"\(1\.09 -> (\d\.\d\d)\)", MECH, "mitigation.argmax", 2),
]


def _readme():
    if not README.exists():
        pytest.skip("[readme] not present")
    return README.read_text(encoding="utf-8", errors="replace")


def _cases():
    out = []
    for label, pattern, source, dotted, places in CLAIMS:
        if source and _at(source, dotted) is not None:
            out.append(pytest.param(label, pattern, source, dotted, places, id=label.replace(" ", "-")))
    return out


CASES = _cases()


@pytest.mark.skipif(not CASES, reason="[results] derived JSON not present")
@pytest.mark.parametrize("label,pattern,source,dotted,places", CASES)
def test_readme_figure_matches_its_source(label, pattern, source, dotted, places):
    match = re.search(pattern, _readme())
    assert match, f"{label}: the README no longer states this figure (pattern {pattern!r})"
    claimed = float(match.group(1))
    actual = round(float(_at(source, dotted)), places)
    assert claimed == actual, (
        f"{label}: the README says {claimed}, the results give {actual} "
        f"(from {dotted})"
    )


def test_the_readme_family_count_matches_the_panel():
    families = len((_json("results_scaled.json") or {}).get("results", {}))
    if not families:
        pytest.skip("[panel data] results_scaled.json not present")
    match = re.search(r"\*\*(\d+) open-weight families", _readme())
    assert match, "the README no longer states a family count"
    assert int(match.group(1)) == families, (
        f"the README says {match.group(1)} families, the panel has {families}"
    )


def test_the_claim_patterns_still_find_what_they_look_for():
    """Vacuity guard: a reworded README would make every case above skip silently.

    Each pattern is specific enough to break if the sentence around it changes,
    which is deliberate -- but then it must fail rather than quietly match
    nothing, so the count of patterns that still find their figure is pinned.
    """
    readme = _readme()
    missing = [label for label, pattern, _, _, _ in CLAIMS if not re.search(pattern, readme)]
    assert not missing, (
        f"{len(missing)} README figure(s) can no longer be located: {missing}. "
        f"If the wording changed, update the pattern; do not delete the case."
    )
