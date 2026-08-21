"""Recompute the main results table from raw, in stdlib, and compare digits.

tab_v2_summary is the first thing a referee reads, and until now the only check
on it was that it matched analyze_peritem.py -- which cannot detect the
generator being wrong. This reimplements every deterministic column from
results_scaled.json using nothing but the standard library, and compares the
rendered digits rather than the intermediate floats.

Comparing the rendered digits is the point. The defect that motivated this file
was invisible at every other level: analyze_peritem.py rounded each family's
flip rate to three places for the JSON, the table then formatted that value at
two, and two of the ten flip cells landed on the wrong digit.

    reference answer, instruct   0.37462 -> 0.375 -> 0.38   (0.37 at two places)
    authority,        instruct   0.41538 -> 0.415 -> 0.41   (0.42 at two places)

Both were quoted in the paper. Neither the generator nor the JSON was wrong in
isolation; only the composition was. So the assertion here is on the string the
reader sees.

The bootstrap interval and the Holm-corrected Wilcoxon p are not recomputed --
they need numpy's generator and scipy, and reimplementing them here would test
the copy, not the claim. They have their own guards.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
TABLE = REPO / "paper" / "honest" / "tables" / "tab_v2_summary.tex"

CONTROL = {"rubric_order": "control", "score_id": "numeric",
           "reference_answer": "none", "authority": "none", "verbosity": "control"}
LABEL = {"rubric_order": "Rubric order", "score_id": "Score ID",
         "reference_answer": "Reference answer", "authority": "Authority",
         "verbosity": "Verbosity"}


def _panel():
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] results_scaled.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))["results"]


def _table_rows():
    if not TABLE.exists():
        pytest.skip("[repro] tab_v2_summary.tex not present")
    rows = {}
    for line in TABLE.read_text(encoding="utf-8", errors="replace").splitlines():
        for probe, label in LABEL.items():
            if line.startswith(label + " &"):
                rows[probe] = [c.strip() for c in
                               line.rstrip().removesuffix("\\\\").split("&")]
    return rows


def _delta(record, probe):
    means = [v["mean"] for v in record[probe].values()]
    return max(means) - min(means)


def _flip(record, probe):
    """Mean over variants of the fraction of items whose argmax score moves."""
    control = record[probe][CONTROL[probe]]["per_item_argmax"]
    rates = []
    for name, variant in record[probe].items():
        if name == CONTROL[probe]:
            continue
        arg = variant["per_item_argmax"]
        rates.append(sum(1 for a, b in zip(control, arg) if a != b) / len(arg))
    return sum(rates) / len(rates)


def _stats(panel, probe):
    families = sorted(panel)
    base = [_delta(panel[f]["base"], probe) for f in families]
    inst = [_delta(panel[f]["instruct"], probe) for f in families]
    diffs = [i - b for i, b in zip(inst, base)]
    n = len(diffs)
    mean = sum(diffs) / n
    sd = math.sqrt(sum((d - mean) ** 2 for d in diffs) / (n - 1))
    return {
        "base": sum(base) / n,
        "inst": sum(inst) / n,
        "change": mean,
        "pct": 100 * mean / (sum(base) / n),
        "dz": mean / sd,
        "flip_base": sum(_flip(panel[f]["base"], probe) for f in families) / n,
        "flip_inst": sum(_flip(panel[f]["instruct"], probe) for f in families) / n,
    }


def test_every_delta_column_recomputes():
    panel, rows = _panel(), _table_rows()
    assert len(rows) == len(LABEL), f"only found rows {sorted(rows)}"

    wrong = []
    for probe, cells in rows.items():
        want = _stats(panel, probe)
        shown_base, shown_inst = cells[1], cells[2]
        shown_dz = cells[4]
        for name, got, expect in (
            ("base delta", shown_base, f"{want['base']:.2f}"),
            ("instruct delta", shown_inst, f"{want['inst']:.2f}"),
            ("cohen dz", shown_dz, f"{want['dz']:+.2f}"),
        ):
            if got != expect:
                wrong.append(f"{probe} {name}: table {got!r}, raw gives {expect!r}")
    assert not wrong, (
        "the main table disagrees with a stdlib recomputation from "
        f"results_scaled.json: {wrong}"
    )


def test_the_change_column_and_its_percentage_recompute():
    panel, rows = _panel(), _table_rows()
    wrong = []
    for probe, cells in rows.items():
        want = _stats(panel, probe)
        # "{+0.21 (+74\%)}" or "\textbf{+0.23 (+59\%)}"
        body = cells[3]
        inner = body[body.index("{") + 1:body.rindex("}")]
        change, pct = inner.split(" (")
        pct = pct.removesuffix(")").removesuffix("\\%")
        if change != f"{want['change']:+.2f}":
            wrong.append(f"{probe} change: table {change!r}, raw {want['change']:+.2f}")
        if pct != f"{want['pct']:+.0f}":
            wrong.append(f"{probe} pct: table {pct!r}, raw {want['pct']:+.0f}")
    assert not wrong, f"the change column does not recompute: {wrong}"


def test_the_flip_rates_are_rounded_once_not_twice():
    """The digits shown must be the exact mean rounded once, not via 3dp.

    Two of these ten cells were wrong for exactly that reason. A guard that
    compared floats with a tolerance would have passed on both.
    """
    panel, rows = _panel(), _table_rows()
    wrong = []
    for probe, cells in rows.items():
        want = _stats(panel, probe)
        field = cells[-1]
        nums = [tok for tok in field.replace("$", " ").replace("\\", " ").split()
                if tok[:1].isdigit()]
        assert len(nums) == 2, f"{probe}: cannot read flip cell {field!r}"
        for arm, got, exact in (("base", nums[0], want["flip_base"]),
                                ("instruct", nums[1], want["flip_inst"])):
            direct = f"{exact:.2f}"
            via_three = f"{round(round(exact, 3), 2):.2f}"
            if got != direct:
                note = " (this is the double-rounded value)" if got == via_three else ""
                wrong.append(
                    f"{probe} {arm} flip: table {got!r}, exact {exact:.5f} "
                    f"rounds to {direct!r}{note}"
                )
    assert not wrong, (
        "flip rates in the main table are not the exact means rounded once: "
        f"{wrong}. Rounding to three places before rendering at two moves a "
        f"digit whenever the third place is a 5."
    )


FAMILY_TABLE = REPO / "paper" / "honest" / "tables" / "tab_v2_family.tex"


def test_the_per_family_table_rounds_once_too():
    """Same check, one table over: 65 cells at one decimal place.

    This table renders each family's spread at 1dp, and it carried the same
    defect: SmolLM2-360M's reference-answer base spread is 0.15010, which is
    0.2 at one place but 0.1 if it passes through 0.150 first.
    """
    panel = _panel()
    if not FAMILY_TABLE.exists():
        pytest.skip("[repro] tab_v2_family.tex not present")

    probes = list(LABEL)
    rows = {}
    for line in FAMILY_TABLE.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = [c.strip() for c in line.rstrip().removesuffix("\\\\").split("&")]
        if len(cells) == 3 + 2 * len(probes) and cells[0] in panel:
            rows[cells[0]] = cells[3:]
    assert len(rows) == len(panel), (
        f"read {len(rows)} family rows for {len(panel)} families: {sorted(rows)}"
    )

    wrong = []
    for family, cells in rows.items():
        for i, probe in enumerate(probes):
            for j, arm in enumerate(("base", "instruct")):
                exact = _delta(panel[family][arm], probe)
                shown = cells[2 * i + j]
                direct = f"{exact:.1f}"
                if shown == direct:
                    continue
                via_three = f"{round(exact, 3):.1f}"
                note = " (double-rounded)" if shown == via_three else ""
                wrong.append(
                    f"{family}/{probe}/{arm}: table {shown!r}, exact "
                    f"{exact:.5f} rounds to {direct!r}{note}"
                )
    assert not wrong, f"per-family table cells do not recompute from raw: {wrong}"
