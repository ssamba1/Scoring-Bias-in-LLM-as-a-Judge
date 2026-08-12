"""Does the mixed-model coefficient reproduce from the per-item scores?

The paper's answer to "does this rest on one probe?" is a per-item mixed-effects
model pooling all five: instruct coefficient +0.16, p < 10^-3, n = 13,000. It is
the sentence that carries the aggregate claim, and until now every check on it
read the number statsmodels produced -- the paper matches the JSON, the JSON
regenerates by rerunning the same fit. Rerunning a computation is not checking
it.

The design is balanced: every family contributes both arms, every arm all five
probes, every probe two non-control variants, every variant fifty items. On a
balanced design the fixed effect of a two-level factor equals the unweighted
difference of the group means, so the coefficient can be recomputed with
arithmetic that shares no code with the model -- no statsmodels, no formula, no
random effects.

It agrees to four decimals. What this cannot reproduce is the standard error or
the p-value, which are exactly what the random effects exist to get right; the
test says so rather than implying the significance claim has been verified.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

CONTROL = {
    "rubric_order": "control",
    "score_id": "numeric",
    "reference_answer": "none",
    "authority": "none",
    "verbosity": "control",
}


def _deviations():
    """Per-item |score - control score|, split by arm -- the model's outcome."""
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] scaled results not present")
    results = json.loads(path.read_text())["results"]

    rows = {"base": [], "instruct": []}
    for family, arms in results.items():
        for arm in ("base", "instruct"):
            cell = arms.get(arm)
            if not isinstance(cell, dict):
                continue
            for probe, control_name in CONTROL.items():
                variants = cell.get(probe)
                if not isinstance(variants, dict):
                    continue
                control = variants.get(control_name, {})
                baseline = control.get("per_item") if isinstance(control, dict) else None
                if not baseline:
                    continue
                for name, record in variants.items():
                    if name == control_name or not isinstance(record, dict):
                        continue
                    scores = record.get("per_item")
                    if not scores or len(scores) != len(baseline):
                        continue
                    rows[arm].extend(abs(a - b) for a, b in zip(scores, baseline))
    return rows


def _stored():
    path = REPRO / "results_mechanism.json"
    if not path.exists():
        pytest.skip("[repro] mechanism results not present")
    lmm = json.loads(path.read_text()).get("lmm")
    if not isinstance(lmm, dict):
        pytest.skip("[repro] no mixed-model record")
    return lmm


def test_the_instruct_coefficient_is_the_difference_of_the_arm_means():
    rows, lmm = _deviations(), _stored()
    assert rows["base"] and rows["instruct"], "no per-item deviations could be formed"

    base = sum(rows["base"]) / len(rows["base"])
    instruct = sum(rows["instruct"]) / len(rows["instruct"])
    contrast = instruct - base

    assert abs(contrast - lmm["instruct_coef"]) <= 0.0006, (
        f"the release stores an instruct coefficient of {lmm['instruct_coef']}; "
        f"the per-item deviations give {contrast:.4f} "
        f"(base {base:.4f}, instruct {instruct:.4f}). On this balanced design "
        f"the fixed effect is the difference of the arm means."
    )


def test_the_model_was_fitted_on_the_rows_the_data_holds():
    rows, lmm = _deviations(), _stored()
    total = len(rows["base"]) + len(rows["instruct"])
    assert total == lmm["n_obs"], (
        f"the model reports n = {lmm['n_obs']}; the released per-item scores "
        f"yield {total} deviations"
    )
    assert len(rows["base"]) == len(rows["instruct"]), (
        f"the design is unbalanced -- {len(rows['base'])} base rows against "
        f"{len(rows['instruct'])} instruct -- so the coefficient is no longer "
        f"the unweighted contrast and this reproduction does not apply"
    )


def test_the_outcome_is_the_one_the_release_documents():
    """The note beside the coefficient defines the outcome; it has to match."""
    lmm = _stored()
    note = lmm.get("note", "")
    assert "score - control score" in note or "control" in note, (
        f"the mixed-model record no longer documents its outcome variable: "
        f"{note!r}. This reproduction assumes |score - control score|."
    )
    assert lmm["instruct_coef"] > 0, (
        "the stored coefficient is not positive; the note says a negative "
        "coefficient would mean instruct is LESS biased, which is the opposite "
        "of the paper's finding"
    )
