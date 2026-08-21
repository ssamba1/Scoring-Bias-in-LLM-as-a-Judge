"""The two summary columns a raw recomputation cannot reach.

test_the_main_table_recomputes_from_raw.py reimplements five of the seven data
columns of tab_v2_summary in stdlib and compares rendered digits. It stops at
the bootstrap interval and the Holm-corrected p, because reimplementing those
means reimplementing numpy's generator and scipy's signed-rank test, which
tests the copy rather than the claim.

That left both columns exposed to the defect the sibling file exists for: a
value rounded once when it is stored and again when it is rendered, landing on
a digit that is not the value's own. Neither column is wrong today. Both are
rendered from a store that has already been rounded, so neither was checked.

The question these two tests ask is narrower than "is the statistic right",
and deliberately so. It is: does the printed digit equal the digit the
unrounded quantity would print? Answering it needs the unrounded quantity, so
each test reproduces the exact procedure the analysis ran -- same seed, same
resample count, same order -- and then compares only the rendering. A failure
here means a digit was lost between the computation and the page, not that the
bootstrap or the correction is wrong. Those have their own guards.

Holm is the more interesting of the two, because it is computed from p-values
that analyze_peritem.py has already rounded to four decimals. Multiplying a
rounded p by its rank and rounding again is the same composition that moved
three digits elsewhere in this paper. It happens to move none here -- every
probe renders identically from the exact and the rounded route -- and pinning
that fact is worth more than asserting it, because a data change could end it
silently.
"""

import json
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
stats = pytest.importorskip("scipy.stats")

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
TABLE = REPO / "paper" / "honest" / "tables" / "tab_v2_summary.tex"

# analyze_peritem.py's constants and probe order. The bootstrap draws from one
# generator shared across probes, so the order matters to the result.
SEED = 42
N_BOOT = 10_000
PROBES = ["rubric_order", "score_id", "reference_answer", "authority", "verbosity"]
LABEL = {"rubric_order": "Rubric order", "score_id": "Score ID",
         "reference_answer": "Reference answer", "authority": "Authority",
         "verbosity": "Verbosity"}


def _peritem():
    path = REPRO / "results_peritem.json"
    if not path.exists():
        pytest.skip("[repro] results_peritem.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _diffs(per_family, probe):
    values = []
    for record in per_family.values():
        cell = record.get(probe)
        if not isinstance(cell, dict) or "base_delta_full" not in cell:
            return None
        values.append(cell["instruct_delta_full"] - cell["base_delta_full"])
    return np.array(values, float)


def _table_cells():
    if not TABLE.exists():
        pytest.skip("[repro] tab_v2_summary.tex not present")
    rows = {}
    for line in TABLE.read_text(encoding="utf-8", errors="replace").splitlines():
        for probe, label in LABEL.items():
            if line.startswith(label + " &"):
                rows[probe] = [c.strip() for c in
                               line.rstrip().removesuffix("\\\\").split("&")]
    return rows


def _holm(pvals):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running = {}, 0.0
    for position, (key, p) in enumerate(items):
        running = max(running, min((m - position) * p, 1.0))
        adjusted[key] = running
    return adjusted


def test_the_interval_endpoints_print_their_own_digits():
    """Reproduce the bootstrap, then check only the rendering.

    The stored interval is rounded to three decimals and the table prints two,
    so a bound whose third decimal is a 5 would print the wrong digit. None
    does; without this test nothing would notice if one started to.
    """
    blob = _peritem()
    per_family = blob.get("per_family")
    if not isinstance(per_family, dict):
        pytest.skip("[repro] no per-family record")
    cells = _table_cells()
    assert len(cells) == len(PROBES), f"read rows for {sorted(cells)}"

    rng = np.random.default_rng(SEED)
    wrong = []
    for probe in PROBES:
        diffs = _diffs(per_family, probe)
        if diffs is None:
            pytest.skip(f"[repro] no unrounded deltas for {probe}")
        means = np.array([rng.choice(diffs, len(diffs), replace=True).mean()
                          for _ in range(N_BOOT)])
        low, high = np.percentile(means, [2.5, 97.5])

        stored = blob["summary"][probe]["boot_ci95"]
        if abs(stored[0] - low) > 5e-4 or abs(stored[1] - high) > 5e-4:
            pytest.skip(
                f"[repro] the bootstrap no longer reproduces at seed {SEED} "
                f"({probe}: stored {stored}, reproduced "
                f"[{low:.4f}, {high:.4f}]); this test can only check the "
                f"rendering when it can reproduce the value"
            )

        shown = cells[probe][5]
        expected = f"[{low:+.2f}, {high:+.2f}]"
        if shown != expected:
            via_three = f"[{round(low, 3):+.2f}, {round(high, 3):+.2f}]"
            note = " (double-rounded)" if shown == via_three else ""
            wrong.append(
                f"{probe}: table shows {shown}, the unrounded endpoints "
                f"({low:.5f}, {high:.5f}) print as {expected}{note}"
            )
    assert not wrong, f"interval endpoints lost a digit in rendering: {wrong}"


def test_holm_prints_the_same_digits_from_unrounded_p_values():
    """Correcting rounded p-values must not change what is printed.

    analyze_peritem.py rounds each Wilcoxon p to four decimals before Holm
    multiplies it by its rank. That is a rounded input to a statistic, which
    is what manufactured a tie and moved rubric_order's p elsewhere in this
    release. Here it changes nothing -- and this is the test that would say so
    if it stopped changing nothing.
    """
    blob = _peritem()
    per_family = blob.get("per_family")
    if not isinstance(per_family, dict):
        pytest.skip("[repro] no per-family record")
    cells = _table_cells()

    exact = {}
    for probe in PROBES:
        diffs = _diffs(per_family, probe)
        if diffs is None:
            pytest.skip(f"[repro] no unrounded deltas for {probe}")
        base = np.array([per_family[f][probe]["base_delta_full"] for f in per_family])
        inst = np.array([per_family[f][probe]["instruct_delta_full"] for f in per_family])
        exact[probe] = float(stats.wilcoxon(base, inst)[1])

    from_exact = _holm(exact)
    wrong = []
    for probe in PROBES:
        shown = cells[probe][6]
        expected = f"{from_exact[probe]:.3f}"
        if shown != expected:
            stored = blob["summary"][probe].get("wilcoxon_p_holm")
            note = " (this is the value from the rounded route)" if (
                stored is not None and shown == f"{stored:.3f}") else ""
            wrong.append(
                f"{probe}: table shows {shown}, Holm over unrounded p-values "
                f"gives {from_exact[probe]:.6f}, printing as {expected}{note}"
            )
    assert not wrong, (
        f"the corrected p-values printed in the table differ from Holm applied "
        f"to unrounded inputs: {wrong}. The correction is currently computed "
        f"from p-values already rounded to four decimals; that was harmless "
        f"when this guard was written and is no longer."
    )
