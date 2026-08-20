"""Does the paper say the mixed model it quotes did not converge?

The between-judge claim rests on a family-random-intercept regression reported
as "coefficient -0.46, p < 1e-5, n = 130". That fit does not converge. Its
family variance component sits at the boundary -- about 0.0006 against a
residual scale of 0.25 -- which is exactly the degenerate case statsmodels warns
about, and the analysis captured none of it: `results_robustness.json` stored
the coefficient, the p-value and n, and nothing else.

The estimate survives the diagnosis, which is why this is a disclosure defect
rather than a numerical one. Ordinary least squares gives -0.462 and
family-clustered least squares gives -0.462 with p = 4.7e-4, so the conclusion
does not depend on the random effect at all. But a coefficient quoted from a
non-converged fit, with nothing anywhere recording that it did not converge, is
a defect this project has already had once: three item-level models in a sibling
paper were fitted under a blanket warnings filter, and the same boundary warning
was hidden by it. The rule that came out of that was to capture the warnings,
assert on a fitted instance, and write the health of the fit into the released
table.

So the released record must carry the convergence flag, the variance component
and the cluster-robust cross-check, and the paper must tell the reader -- a
referee who refits this model gets the same non-convergence warning, and should
find it already described rather than discover it.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ROBUST = REPO / "paper" / "honest" / "repro" / "results_robustness.json"
MACROS = REPO / "paper" / "honest" / "macros.tex"


def _lmm():
    if not ROBUST.exists():
        pytest.skip("[repro] results_robustness.json not present")
    blob = json.loads(ROBUST.read_text(encoding="utf-8", errors="replace"))
    entry = blob.get("B1_lmm")
    if not isinstance(entry, dict) or "entropy_coef" not in entry:
        pytest.skip("[repro] no mixed-model record")
    return entry


def test_the_released_record_carries_the_fit_health():
    entry = _lmm()
    for field in ("converged", "group_var", "se_finite",
                  "clustered_ols_coef", "clustered_ols_p", "fit_warnings"):
        assert field in entry, (
            f"the mixed-model record does not report '{field}'. The coefficient "
            f"alone cannot tell a reader whether the fit that produced it "
            f"converged, and this one does not."
        )
    assert entry["se_finite"], (
        "the mixed model's standard errors are no longer finite. A boundary fit "
        "with finite SEs is reportable with a caveat; one without them is not."
    )

    # The flag and the warnings have to agree. Flipping `converged` to true on
    # its own would otherwise retire the paper's disclosure -- the check below
    # skips when the fit converges -- while the captured warnings still say the
    # optimizer failed. A record that contradicts itself is worse than either
    # value alone, because each half looks authoritative.
    warned = " ".join(entry.get("fit_warnings") or []).lower()
    failed = "failed to converge" in warned or "optimization failed" in warned
    assert not (entry["converged"] and failed), (
        f"the record says the fit converged while its own captured warnings say "
        f"otherwise: {entry.get('fit_warnings')}. One of the two was edited."
    )


def test_the_conclusion_does_not_rest_on_the_random_effect():
    """Whatever the optimizer does, the estimate must survive dropping it."""
    entry = _lmm()
    mixed = entry["entropy_coef"]
    clustered = entry["clustered_ols_coef"]
    assert abs(mixed - clustered) < 0.02, (
        f"the mixed-effects estimate ({mixed}) and the family-clustered least "
        f"squares estimate ({clustered}) have diverged. While they agree, the "
        f"non-convergence is a curiosity; if they stop agreeing, the reported "
        f"coefficient depends on a fit that did not converge."
    )
    assert clustered < 0 and entry["clustered_ols_p"] < 0.01, (
        f"the cluster-robust cross-check no longer supports the relation "
        f"(coef {clustered}, p {entry['clustered_ols_p']}); it is the most "
        f"conservative of the three estimators and the one a sceptical reader "
        f"will run"
    )


def test_the_paper_discloses_the_boundary_fit():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    if "MECHPROSE" not in text:
        pytest.skip("[paper] no mechanism prose")
    prose = text[text.index("MECHPROSE"):]
    prose = prose[:prose.index("\n")]

    entry = _lmm()
    if entry.get("converged"):
        pytest.skip("[repro] the fit now converges; the disclosure is not required")

    for fragment, why in [
        ("boundary", "that the likelihood sits on the boundary"),
        ("non-convergence", "that the optimizer does not converge"),
        ("clustered", "the cluster-robust cross-check that does not need the random effect"),
    ]:
        assert fragment in prose, (
            f"the mechanism prose does not state {why}. A referee refitting this "
            f"model meets the warning; the paper should have said so first."
        )
