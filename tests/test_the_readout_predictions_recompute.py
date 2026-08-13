"""Do the three readout predictions follow from the raw runs they summarise?

Addendum 4 registered three predictions about how a score is *read out* of a
model, and all three shipped an analysis file summarising a raw file:

  P16 (sampled readout)   results_sampled.json -> results_sampled_analysis.json
  P17 (scale granularity) results_gran_analysis.json
  P18 (token variants)    results_tokvar.json  -> results_tokvar_analysis.json

The other verdict guards in this suite recompute a summary from per-unit values
stored beside it. Where a raw file survives, the stronger check is available:
recompute the summary from the run itself, so that a wrong aggregation is
caught and not only a mistyped total. P16 and P18 get that treatment here --
parse rates from the 18 recorded conditions, deltas from the per-cell means,
correlations from those deltas. P17 has no raw file in the release, so its
per-unit-range figures are recomputed from the scale ranges instead.

These three carry the paper's answer to "is your effect an artifact of how you
read the score?", which is the first question a skeptical reader asks about a
logit-based bias measurement. P16 says the parse-based alternative is either
confounded or noise-dominated; P18 says the bare-token conditional tracks the
model's real high-mass preference; P17 says bias scales with the value range as
the variance theory predicts. Two are confirmations, one is a failure that
corrects the paper's own earlier framing, and none had been recomputed.
"""

import json
import statistics
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
READOUTS = ("bare", "union", "space_appended")


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text())


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


def _spearman(xs, ys):
    return _pearson(_average_ranks(xs), _average_ranks(ys))


def _sampled_cells():
    """(family, checkpoint, probe) -> the conditions recorded for that cell."""
    raw = _load("results_sampled.json")["results"]
    for family, checkpoints in raw.items():
        for checkpoint, probes in checkpoints.items():
            for probe, conditions in probes.items():
                yield family, checkpoint, probe, conditions


def test_the_sampled_parse_rates_recompute_from_the_run():
    """P16a: base 0.80 against instruct 0.83 -- the re-scoped confound claim."""
    stored = _load("results_sampled_analysis.json")["P16a_parse_rate"]
    observed = {"base": [], "instruct": []}
    for _family, checkpoint, _probe, conditions in _sampled_cells():
        observed[checkpoint].extend(c["parse_rate"] for c in conditions.values())

    for checkpoint, rates in observed.items():
        if not rates:
            pytest.skip("[repro] no recorded parse rates")
        got = statistics.mean(rates)
        assert abs(got - stored[checkpoint]) <= 0.0005, (
            f"the release reports a {checkpoint} parse rate of "
            f"{stored[checkpoint]}; its {len(rates)} recorded conditions average "
            f"{got:.4f}"
        )

    gap = abs(statistics.mean(observed["base"]) - statistics.mean(observed["instruct"]))
    assert gap < 0.10, (
        f"base and instruct parse rates now differ by {gap:.3f}; the paper's "
        f"re-scoping rests on their being nearly equal under this protocol"
    )


def test_the_sampled_estimator_still_fails_to_recover_the_ordering():
    """P16b: rho = -0.20 over 12 cells, a registered failure."""
    stored = _load("results_sampled_analysis.json")["P16b_delta_agreement"]
    expected, sampled = [], []
    for _family, _checkpoint, _probe, conditions in _sampled_cells():
        ev = [c["ev_mean"] for c in conditions.values()]
        sm = [c["sampled_mean"] for c in conditions.values()]
        expected.append(max(ev) - min(ev))
        sampled.append(max(sm) - min(sm))

    assert len(expected) == stored["n_cells"], (
        f"the release correlates {stored['n_cells']} cells; the run holds "
        f"{len(expected)}"
    )
    rho = _spearman(expected, sampled)
    assert abs(rho - stored["spearman_ev_vs_sampled_delta"]) <= 0.0015, (
        f"the release reports rho = {stored['spearman_ev_vs_sampled_delta']}; "
        f"its own cells give {rho:.4f}"
    )
    assert rho < 0.4, (
        f"the sampled estimator now recovers the expected-value ordering at "
        f"rho = {rho:.3f}; P16b is registered and reported as a failure"
    )


def test_the_granularity_growth_recomputes():
    """P17: bias grows with the scale's value range, instruct above base."""
    blob = _load("results_gran_analysis.json")
    per_scale = blob["per_scale"]
    growth = blob["P17a_growth"]

    for checkpoint in ("base", "instruct"):
        biases = [per_scale[name][f"mean_bias_{checkpoint}"] for name in per_scale]
        assert biases == growth[checkpoint]["biases_by_scale"], (
            f"the release lists {growth[checkpoint]['biases_by_scale']} for "
            f"{checkpoint}; its per-scale records give {biases}"
        )
        increasing = all(a < b for a, b in zip(biases, biases[1:]))
        assert increasing == growth[checkpoint]["monotone_increasing"], (
            f"the release calls the {checkpoint} sequence monotone="
            f"{growth[checkpoint]['monotone_increasing']}; {biases} is "
            f"monotone={increasing}"
        )
        assert increasing, (
            f"{checkpoint} bias no longer grows with the scale range: {biases}"
        )

    for name, cell in per_scale.items():
        for checkpoint in ("base", "instruct"):
            got = cell[f"mean_bias_{checkpoint}"] / cell["range"]
            assert abs(got - cell[f"bias_per_unit_range_{checkpoint}"]) <= 0.0005, (
                f"{name} stores bias per unit range "
                f"{cell[f'bias_per_unit_range_{checkpoint}']} for {checkpoint}; "
                f"{cell[f'mean_bias_{checkpoint}']} over a range of "
                f"{cell['range']} is {got:.4f}"
            )
        assert cell["mean_bias_instruct"] > cell["mean_bias_base"], (
            f"instruct no longer exceeds base at {name}; P17b is reported as "
            f"holding at every granularity"
        )


def _tokvar_deltas():
    """Per-cell max-min spread and answer mass, for each readout."""
    raw = _load("results_tokvar.json")["results"]
    deltas = {readout: [] for readout in READOUTS}
    mass = {readout: {"base": [], "instruct": []} for readout in READOUTS}
    by_family = {readout: {} for readout in READOUTS}
    for family, checkpoints in raw.items():
        for checkpoint, probes in checkpoints.items():
            if checkpoint == "digit_set_sizes":
                continue
            for probe, conditions in probes.items():
                if probe == "digit_set_sizes":
                    continue
                for readout in READOUTS:
                    means = [c[readout]["mean"] for c in conditions.values()]
                    spread = max(means) - min(means)
                    deltas[readout].append(spread)
                    mass[readout][checkpoint].extend(
                        c[readout]["mean_mass"] for c in conditions.values()
                    )
                    cell = by_family[readout].setdefault(family, {})
                    cell.setdefault(checkpoint, []).append(spread)
    return deltas, mass, by_family


def test_the_readout_variants_agree_as_reported():
    """P18a: bare == union exactly, and 0.79 against the space-appended read."""
    stored = _load("results_tokvar_analysis.json")
    deltas, mass, _ = _tokvar_deltas()

    assert len(deltas["bare"]) == stored["n_cells"], (
        f"the release reports {stored['n_cells']} cells; the run holds "
        f"{len(deltas['bare'])}"
    )
    for pair, expected in stored["P18a_pairwise_delta_corr"].items():
        left, right = pair.split("~")
        got = _spearman(deltas[left], deltas[right])
        assert abs(got - expected) <= 0.0015, (
            f"the release reports {pair} at {expected}; its own per-cell "
            f"deltas give {got:.4f}"
        )
        assert got >= 0.7, (
            f"{pair} agree at only {got:.3f}; the registered threshold is 0.7 "
            f"and the paper reports the prediction as met"
        )

    for readout, checkpoints in stored["mean_mass"].items():
        for checkpoint, expected in checkpoints.items():
            got = statistics.mean(mass[readout][checkpoint])
            assert abs(got - expected) <= 0.0005, (
                f"the release reports {readout}/{checkpoint} mass {expected}; "
                f"the run averages {got:.4f}"
            )
    assert min(
        statistics.mean(mass["space_appended"][c]) for c in ("base", "instruct")
    ) > 0.9, "the space-appended position no longer carries the dominant mass"


def test_the_union_effect_and_its_residual_recompute():
    """P18b holds 4/4; P18c's space-appended residual holds only 2/4."""
    stored = _load("results_tokvar_analysis.json")
    _deltas, _mass, by_family = _tokvar_deltas()

    for readout, expected in stored["P18c_effect_by_readout"].items():
        effects = {
            family: statistics.mean(cell["instruct"]) - statistics.mean(cell["base"])
            for family, cell in by_family[readout].items()
        }
        mean_effect = statistics.mean(effects.values())
        assert abs(mean_effect - expected["mean_effect"]) <= 0.0015, (
            f"the release reports a {readout} mean effect of "
            f"{expected['mean_effect']}; its families give {mean_effect:.4f}"
        )
        positive = sum(1 for value in effects.values() if value > 0)
        assert f"{positive}/{len(effects)}" == expected["families_positive"], (
            f"the release reports {expected['families_positive']} families "
            f"positive under {readout}; its own values give "
            f"{positive}/{len(effects)}"
        )
        if readout == "union":
            for family, value in effects.items():
                assert abs(value - stored["P18b_union_effect"]["per_family"][family]) <= 0.0015, (
                    f"the release stores {family} at "
                    f"{stored['P18b_union_effect']['per_family'][family]} under "
                    f"the union readout; the run gives {value:.4f}"
                )
            assert positive == len(effects), (
                f"the instruct>base effect holds in only {positive} of "
                f"{len(effects)} families under the union readout; the paper "
                f"reports 4/4"
            )

    residual = stored["P18c_effect_by_readout"]["space_appended"]
    assert residual["families_positive"] != stored["P18b_union_effect"]["families_positive"], (
        "the space-appended readout now matches the union readout family for "
        "family; the paper reports this gap as its honest residual"
    )
