"""Does the readout limitation state the mass it depends on?

Limitation 5 concedes that these judges place little probability on a bare score
token, which is why the score is read as a conditional expectation over the
valid-token subset. It used to say only "small". "Small" is not checkable, and
it is the kind of word that survives a change in the data underneath it.

Recomputed from the release: a mean of 0.15% over the 390 measured variants,
median 0.03%.

The recomputation also surfaced something the limitation had not said. The mass
is systematically smaller for instruct checkpoints than for base ones -- 0.03%
against 0.26%, about eightfold -- and those are the two arms the paper compares.
It does not invalidate the readout, which conditions on the valid tokens and is
defended behaviorally (near-perfect gold discrimination, 0.99 split-half), but a
referee who computes it would find an asymmetry between the compared arms that
the paper had not mentioned. Now it does.

The direction is also the reassuring one to have to explain: instruct models put
LESS mass on bare score tokens, so any artefact from conditioning would be
working against the paper's finding, not for it.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"
PROBES = {"rubric_order", "score_id", "reference_answer", "authority", "verbosity"}


def _masses():
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] results_scaled.json not present")
    results = json.loads(path.read_text(encoding="utf-8", errors="replace"))["results"]
    by_arm = {"base": [], "instruct": []}
    for record in results.values():
        for kind in ("base", "instruct"):
            for probe, variants in (record.get(kind) or {}).items():
                if probe not in PROBES or not isinstance(variants, dict):
                    continue
                for value in variants.values():
                    if isinstance(value, dict) and "mean_mass" in value:
                        by_arm[kind].append(value["mean_mass"])
    if not by_arm["base"]:
        pytest.skip("[repro] no mean_mass recorded")
    return by_arm


def _mean(values):
    return sum(values) / len(values)


def test_the_stated_mass_matches_the_release():
    by_arm = _masses()
    every = by_arm["base"] + by_arm["instruct"]
    assert len(every) == 390, (
        f"{len(every)} variants carry a mass value, not 390; the percentages in "
        f"Limitation 5 were computed over 390"
    )

    overall = _mean(every) * 100
    assert abs(overall - 0.15) < 0.02, (
        f"mean answer-token mass recomputes to {overall:.3f}%, not the 0.15% the "
        f"limitation states"
    )


def test_the_arms_differ_and_the_paper_says_so():
    by_arm = _masses()
    base = _mean(by_arm["base"]) * 100
    instruct = _mean(by_arm["instruct"]) * 100
    overall = _mean(by_arm["base"] + by_arm["instruct"]) * 100

    assert instruct < base, (
        f"instruct mass ({instruct:.3f}%) is no longer below base ({base:.3f}%). "
        f"The limitation explains the asymmetry in that direction, and that "
        f"direction is what makes it work against the paper's finding rather "
        f"than for it."
    )
    assert abs(base - 0.26) < 0.03 and abs(instruct - 0.03) < 0.02, (
        f"the arms now read base {base:.3f}% / instruct {instruct:.3f}%; the "
        f"limitation states 0.26% and 0.03%"
    )

    released = REPRO / "results_readout.json"
    if released.exists():
        stored = json.loads(released.read_text(encoding="utf-8", errors="replace"))
        # Re-derive the flag from the two means it summarises rather than
        # reading it: a stored verdict nothing recomputes is a claim.
        expected = stored["instruct"]["mean_pct"] < stored["base"]["mean_pct"]
        assert stored["instruct_below_base"] == expected, (
            f"the release records instruct_below_base="
            f"{stored['instruct_below_base']} while its own means "
            f"({stored['instruct']['mean_pct']} vs {stored['base']['mean_pct']}) "
            f"give {expected}"
        )
        assert abs(stored["overall"]["mean_pct"] - overall) < 0.02, (
            f"results_readout.json stores {stored['overall']['mean_pct']}% but "
            f"the raw runs give {overall:.4f}%"
        )

    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    flat = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    assert re.search(r"0\.15\\%", flat), (
        "Limitation 5 no longer states the mean answer-token mass. 'Small' is "
        "not checkable and does not survive a change in the data."
    )
    assert re.search(r"0\.03\\%.*0\.26\\%", flat) or re.search(r"0\.26\\%.*0\.03\\%", flat), (
        "Limitation 5 no longer states the base/instruct asymmetry in "
        "answer-token mass, which is a difference between the two arms the "
        "paper compares"
    )
