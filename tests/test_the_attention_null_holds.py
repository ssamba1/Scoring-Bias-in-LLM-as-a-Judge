"""Is the attention null still a null, and still measured?

This is the point in the paper where the retracted version invented a
mechanism. It claimed instruction tuning makes judges attend more to the
injected nuisance, with hardcoded attention values behind it. The honest
measurement refutes that: across three Qwen families, instruct judges attend
equally or slightly less than base, an instruct/base ratio of 0.95 to 1.00 in
all six model x perturbation cases, so responsiveness rises despite flat input
attention.

attn_results.json was referenced by no test in the suite. Every other released
run is named somewhere; this one -- the file standing in for fabricated numbers
-- was the single exception, found by inventorying derived files against the
tests that read them.

What is checked here is the null itself, from the raw file: six cases, every
ratio inside the stated band, and no case where instruct attends materially
more. The last is the one that matters. A ratio drifting above 1 would restore
exactly the claim the retraction was for, and it would do so quietly, because a
number near 1.0 looks unremarkable either side of it.

The band is asserted at both ends. Below 0.95 the paper's "equally or slightly
less" would understate a real reduction, which is a different finding rather
than a safer one.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "macros.tex"


def _results():
    path = REPRO / "attn_results.json"
    if not path.exists():
        pytest.skip("[repro] attn_results.json not present")
    blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    results = blob.get("results")
    if not isinstance(results, dict) or not results:
        pytest.skip("[repro] no attention results")
    return results


def _ratios():
    """(family, perturbation) -> instruct attention / base attention."""
    out = {}
    for family, arms in _results().items():
        base, instruct = arms.get("base"), arms.get("instruct")
        if not isinstance(base, dict) or not isinstance(instruct, dict):
            continue
        for condition, base_value in base.items():
            if condition not in instruct or not base_value:
                continue
            out[(family, condition)] = instruct[condition] / base_value
    if not out:
        pytest.skip("[repro] no paired attention cells")
    return out


def test_all_six_cases_are_present():
    ratios = _ratios()
    assert len(ratios) == 6, (
        f"the paper reports six model x perturbation cases; the run yields "
        f"{len(ratios)}: {sorted(ratios)}. A dropped case would move the "
        f"reported range without changing any surviving number."
    )


def test_no_case_shows_instruct_attending_more():
    """The refuted hypothesis, and the one the retracted version asserted."""
    ratios = _ratios()
    higher = {f"{fam}/{cond}": round(r, 4) for (fam, cond), r in ratios.items() if r > 1.0}
    assert not higher, (
        f"instruct now attends more than base in {higher}. That is the "
        f"mechanism the retracted version invented at this exact point, and "
        f"the paper reports it as refuted; if the data now says otherwise, the "
        f"section and the retraction notice both have to change."
    )


def test_every_ratio_sits_in_the_reported_band():
    ratios = _ratios()
    outside = {
        f"{fam}/{cond}": round(r, 4)
        for (fam, cond), r in ratios.items() if not 0.95 <= r <= 1.00
    }
    assert not outside, (
        f"the paper states an instruct/base attention ratio of 0.95 to 1.00 in "
        f"all six cases; {outside} fall outside it"
    )


def test_the_paper_still_states_the_null():
    if not PAPER.exists():
        pytest.skip("[paper] macros.tex not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    if "ATTNPROSE" not in text:
        pytest.skip("[paper] no attention prose")
    assert "refuted" in text, (
        "the attention prose no longer says the natural hypothesis is refuted; "
        "reporting this null is deliberate, because a fabricated positive "
        "result stood here before"
    )
    assert "fabricated" in text, (
        "the attention prose no longer notes that a prior version invented a "
        "mechanism at this point; that sentence is why the null is stated "
        "rather than quietly omitted"
    )
