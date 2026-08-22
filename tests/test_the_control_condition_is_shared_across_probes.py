"""All five probes share one control prompt, and the paper has to say so.

`scaled_harness.py` builds every prompt through `build_prompt(instr, resp,
scale, header, ref)`. For the control condition of each probe those arguments
coincide:

    rubric_order/control      scale=1..5 worst-to-best, header "Score", ref ""
    score_id/numeric          the same three
    reference_answer/none     the same three
    authority/none            prefix "", response transform identity
    verbosity/control         prefix "", response transform identity

so all five reduce to the identical string. A checkpoint therefore has *one*
control measurement, not five, and the released data confirms it: in every one
of the 26 checkpoints the five control cells carry the same mean and the same
entropy, to the last stored digit.

This matters where the control reading is used as a predictor. The control-only
entropy-bias link is computed over 130 rows, but those rows hold only 26
distinct entropies -- each repeated once per probe -- so a p-value computed over
130 rows is counting repeats as independent observations. The paper now states
this and quotes the collapsed reading (one row per checkpoint), which is
stronger, not weaker: rho = -0.64 at n = 26. The relation survives being counted
honestly, which is the point of saying it out loud.

Nothing else checks the coincidence. `analyze_mechanism.py` and
`test_cumulants_recompute_from_raw.py` both average "across the five probes'
control conditions" -- an average of five copies of one number, which is
arithmetically harmless and rhetorically misleading if never disclosed. If a
future prompt edit makes the controls genuinely distinct, this file fails and
the disclosure has to be revisited rather than left standing as a false caveat.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
SCALED = REPRO / "results_scaled.json"
MECH = REPRO / "results_mechanism.json"

# the control variant of each probe, as analyze_mechanism.py defines it
CONTROL = {
    "rubric_order": "control",
    "score_id": "numeric",
    "reference_answer": "none",
    "authority": "none",
    "verbosity": "control",
}


def _panel():
    if not SCALED.exists():
        pytest.skip("[repro] results_scaled.json not present")
    return json.loads(SCALED.read_text(encoding="utf-8", errors="replace"))["results"]


def _mech():
    if not MECH.exists():
        pytest.skip("[repro] results_mechanism.json not present")
    return json.loads(MECH.read_text(encoding="utf-8", errors="replace"))


def _checkpoints(panel):
    for family, rec in panel.items():
        if not isinstance(rec, dict) or "base" not in rec:
            continue
        for arm in ("base", "instruct"):
            if isinstance(rec.get(arm), dict):
                yield family, arm, rec[arm]


def test_the_five_control_cells_are_one_measurement():
    panel = _panel()
    checked, disagreeing = 0, []
    for family, arm, block in _checkpoints(panel):
        readings = {}
        for probe, variant in CONTROL.items():
            cell = block.get(probe, {}).get(variant)
            if isinstance(cell, dict):
                readings[probe] = (cell.get("mean"), cell.get("mean_entropy"))
        if len(readings) < 2:
            continue
        checked += 1
        if len(set(readings.values())) != 1:
            disagreeing.append(f"{family}/{arm}: {readings}")

    assert checked, "no checkpoints carried control cells for more than one probe"
    assert not disagreeing, (
        f"the probes' control conditions no longer coincide: {disagreeing[:3]}. "
        f"The paper states that all five share one prompt and that the "
        f"control-only reading therefore repeats each entropy; if the prompts "
        f"have genuinely diverged that disclosure is now wrong and the collapsed "
        f"statistic needs recomputing rather than leaving as-is."
    )


def test_the_repeat_count_is_what_the_paper_says():
    """130 rows, 26 distinct entropies -- the number the disclosure quotes."""
    mech = _mech()
    col = mech.get("entropy_bias_link_control_only", {})
    distinct = col.get("n_distinct_entropies")
    rows = col.get("n")
    assert distinct is not None, (
        "results_mechanism.json no longer records how many distinct entropies "
        "the control-only reading carries; the paper quotes that count"
    )
    panel = _panel()
    expected = sum(1 for _ in _checkpoints(panel))
    assert distinct == expected, (
        f"the control-only reading carries {distinct} distinct entropies but the "
        f"panel holds {expected} checkpoints; with one control prompt per "
        f"checkpoint those must be equal"
    )
    assert rows and rows > distinct, (
        f"the control-only reading reports n={rows} over {distinct} distinct "
        f"values; if they are equal the repeats are gone and the paper's caveat "
        f"no longer applies"
    )


def test_the_collapsed_reading_is_reported_and_survives():
    """The honest count must still show the relation, or the caveat is a finding."""
    col = _mech().get("entropy_bias_link_control_only", {})
    collapsed = col.get("collapsed_to_checkpoints")
    assert collapsed, (
        "the collapsed control-only statistic is not in the release; the paper "
        "quotes it as the reading without repeated predictor values"
    )
    assert collapsed["n"] == col["n_distinct_entropies"], (
        f"the collapsed reading has {collapsed['n']} rows but there are "
        f"{col['n_distinct_entropies']} distinct entropies; it should be one row "
        f"per checkpoint"
    )
    assert collapsed["spearman_rho"] < 0, (
        f"collapsing to one row per checkpoint reverses the relation "
        f"(rho={collapsed['spearman_rho']}). The paper reports the collapsed "
        f"reading as intact; if it is not, the robustness claim fails."
    )
