"""Do the outcomes recorded in the preregistration match the released data?

The preregistration now records a verdict for every registered prediction, and
those verdicts carry numbers: entropies, correlations, p-values, per-family
counts. Numbers in a markdown file drift exactly as readily as numbers in a
paper, and this file is the one a sceptical reader checks first, because it is
the only document that says what was promised before the data arrived.

So the same discipline the paper's prose is held to applies here: every figure
quoted in an outcome is recomputed from the committed analyses. A verdict that
no longer matches its evidence fails, and so does a verdict whose evidence was
reworded out of the file.

The rounding is checked at the precision quoted, not to machine precision -- a
number written to three decimals is a claim about three decimals.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PREREG = REPO / "paper" / "honest" / "PREREGISTRATION.md"


def _text():
    if not PREREG.exists():
        pytest.skip("[preregistration] PREREGISTRATION.md not present")
    return PREREG.read_text(encoding="utf-8", errors="replace")


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text())


def _states(text, literal, what):
    assert literal in text, (
        f"the preregistration no longer states {literal!r} for {what}; either "
        f"the outcome was reworded or its evidence moved, and both need this "
        f"check updated deliberately rather than left pointing at nothing"
    )


def test_the_sharpening_outcome_matches_the_measurement():
    text = _text()
    dec = _load("results_mechanism.json")["decisiveness"]
    _states(text, f"{dec['base_mean']:.3f} → {dec['instruct_mean']:.3f}", "P1's entropy fall")
    _states(text, f"{dec['n_decreased']} of {dec['n']} families", "P1's family count")
    _states(text, f"p = {dec['wilcoxon_p']}", "P1's Wilcoxon p")


def test_the_refuted_link_outcome_matches_the_measurement():
    text = _text()
    mech = _load("results_mechanism.json")
    rho = mech["entropy_bias_link"]["spearman_rho"]
    control_only = mech["entropy_bias_link_control_only"]["spearman_rho"]
    assert rho < 0, (
        f"the preregistration records P2 as refuted in sign, but the measured "
        f"correlation is {rho}, which is the registered direction"
    )
    _states(text, f"ρ = {rho}".replace("-", "−"), "P2's measured correlation")
    _states(text, f"n = {mech['entropy_bias_link']['n']}", "P2's cell count")
    _states(text, f"{control_only}".replace("-", "−"), "P2's control-only reading")


def test_the_generality_outcome_matches_the_measurement():
    text = _text()
    gen = _load("results_mechanism.json")["generality"]
    registered = gen["content_as_registered_P4"]
    _states(text, f"ρ = {registered['spearman_rho']}".replace("-", "−"),
            "P4 on the registered grouping")
    _states(text, f"p = {registered['spearman_p']}", "P4's p-value")
    _states(text, f"n = {registered['n']}", "P4's cell count")
    for key, label in (("content", "the wider content group"), ("format", "the format group")):
        _states(text, f"{gen[key]['spearman_rho']}".replace("-", "−"), label)


def test_the_predictor_outcome_matches_the_measurement():
    text = _text()
    pred = _load("results_mechanism.json")["predictor"]
    boot = _load("results_robustness.json")["B2_predictor_bootstrap"]
    _states(text, f"R² = {pred['loo_r2']}", "P5's out-of-sample R^2")
    _states(text, f"r = {pred['loo_pearson_r']}", "P5's correlation")
    _states(text, f"p = {pred['loo_p']}", "P5's p-value")
    _states(text, f"{pred['n_models']} checkpoints", "P5's checkpoint count")
    lo, hi = boot["r2_ci95"]
    _states(text, f"[{lo}, {hi}]".replace("-", "−"), "P5's bootstrap interval")
    assert lo <= 0 <= hi, (
        f"the preregistration calls P5 unstable because its interval includes "
        f"zero; the released interval is [{lo}, {hi}]"
    )


def test_the_validity_outcome_matches_the_measurement():
    text = _text()
    gold = _load("results_gold.json")
    rev = gold["degradation"]["reversed"]
    verb = gold["degradation"]["verbose"]
    nov = gold["degradation"]["novice"]

    assert rev["instruct"]["margin_drop"] > rev["base"]["margin_drop"], (
        "the preregistration records P6's second clause as failed in the "
        "opposite direction; under reversed the instruct margin drop is no "
        "longer the larger one"
    )
    _states(text, f"({rev['instruct']['margin_drop']} vs {rev['base']['margin_drop']})",
            "P6's reversed margin drops")
    _states(text, f"({verb['instruct']['margin_drop']} vs {verb['base']['margin_drop']})",
            "P6's verbose margin drops")
    _states(text, f"p = {rev['instruct_more_robust_p']}", "P6's reversed p-value")
    _states(text, f"p = {nov['instruct_more_robust_p']}", "P6's novice p-value")

    control = gold["control"]
    for kind in ("base", "instruct"):
        under = rev[kind]["accuracy_under_bias"]
        _states(text, f"{control[kind]['mean_accuracy']:.2f} → {under:.2f}",
                f"P6's {kind} accuracy collapse")


def test_the_panel_outcome_matches_the_measurement():
    text = _text()
    summary = _load("results_peritem.json")["summary"]
    sens = _load("results_robustness.json")["B3_sensitivity"]

    changes = [probe["mean_change"] for probe in summary.values()]
    assert all(change > 0 for change in changes), (
        f"the preregistration records H0 as directionally confirmed on all five "
        f"probes; the released mean changes are {changes}"
    )
    _states(text, f"+{min(changes):.3f} to +{max(changes):.3f}", "H0's spread of mean changes")
    _states(text, f"+{sens['full_mean_effect']}", "H0's panel mean effect")
    _states(text, f"{sens['n_families_positive']}/{sens['n_families']} families positive",
            "H0's family count")

    holm = min(probe["wilcoxon_p_holm"] for probe in summary.values())
    _states(text, f"Holm-adjusted p is {holm}", "H0's smallest corrected p")
    assert holm > 0.05, (
        f"the preregistration records that no probe survives Holm correction; "
        f"the smallest adjusted p is now {holm}"
    )

    excludes = sorted(
        probe["label"] for probe in summary.values() if probe["ci_excludes_zero"]
    )
    assert len(excludes) == 3, (
        f"the preregistration names three probes whose uncorrected interval "
        f"excludes zero; the data now give {excludes}"
    )
