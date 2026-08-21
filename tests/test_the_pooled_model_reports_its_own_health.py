"""Is the abstract's pooled model sound enough to quote a p-value from?

The abstract cites a pooled per-item model for the headline increase. Until this
was checked, that fit reported a coefficient and a p-value and nothing else --
no convergence flag, no variance component, no cluster-robust cross-check --
while analyze_robustness.py's B1_lmm had carried all three since it was found
not to converge. The argument for them applies here with more force, because
this coefficient is the one in the abstract.

Checking it found the fit degenerate. The family variance component is exactly
zero, the random-effects covariance is singular, the Hessian is not positive
definite, and the standard errors are not all finite. A p-value read off that
fit is not trustworthy, and it was being read off it.

The conclusion survives intact, which is why this is a reporting fix rather than
a retraction: a family-clustered OLS gives the identical coefficient (0.1559)
with p = 4e-06 under assumptions that hold. The paper now quotes that, and says
why.

The zero variance component is worth reporting rather than hiding. It says the
per-item deviations carry no between-family variance -- the increase is not a
family-level artefact -- which is also the reason the random intercept collapses.

So this guard requires three things: that the diagnosis is present, that the two
estimates still agree, and that the paper is not quoting a p-value from a fit
whose standard errors are not finite.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"


def _lmm():
    path = REPRO / "results_mechanism.json"
    if not path.exists():
        pytest.skip("[repro] results_mechanism.json not present")
    lmm = json.loads(path.read_text(encoding="utf-8", errors="replace")).get("lmm")
    if not lmm or "instruct_coef" not in lmm:
        pytest.skip("[repro] pooled model not fitted")
    return lmm


def test_the_fit_records_its_own_diagnosis():
    lmm = _lmm()
    for field in ("converged", "group_var", "resid_scale", "icc", "se_finite",
                  "clustered_ols_coef", "clustered_ols_p", "fit_warnings"):
        assert field in lmm, (
            f"the pooled model no longer records {field!r}. A coefficient "
            f"reported from a fit with nothing recording its health is the "
            f"shape of defect this project has already had once."
        )


def test_the_two_estimates_still_agree():
    """The claim rests on the coefficient, which must not depend on the fit."""
    lmm = _lmm()
    mixed = lmm["instruct_coef"]
    clustered = lmm["clustered_ols_coef"]
    assert abs(mixed - clustered) < 0.005, (
        f"the mixed-effects coefficient ({mixed}) and the family-clustered OLS "
        f"({clustered}) have diverged. While they agree, the degenerate random "
        f"effect does not matter; if they stop agreeing, it does."
    )
    assert mixed > 0, (
        f"the pooled instruct coefficient is {mixed}; the paper's aggregate "
        f"claim is that tuning increases bias"
    )


def test_the_icc_matches_the_variance_components():
    lmm = _lmm()
    group, resid = lmm["group_var"], lmm["resid_scale"]
    expected = group / (group + resid) if (group + resid) else 0.0
    assert abs(lmm["icc"] - expected) < 1e-6, (
        f"stored ICC {lmm['icc']} does not follow from its own components "
        f"({group}, {resid} give {expected})"
    )


def test_the_paper_does_not_quote_a_p_from_the_degenerate_fit():
    """If the SEs are not finite, the reported p must come from elsewhere."""
    lmm = _lmm()
    if lmm.get("se_finite", True):
        pytest.skip("[repro] the mixed fit's standard errors are finite again")

    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = " ".join(MACROS.read_text(encoding="utf-8", errors="replace").split())
    if "RESULTSPROSE" not in text:
        pytest.skip("[paper] no results prose")
    prose = text[text.index("RESULTSPROSE"):][:2400]

    assert "family-clustered OLS" in prose, (
        "the mixed fit's standard errors are not all finite, so its p-value is "
        "not trustworthy, and the prose no longer says the reported p comes "
        "from the family-clustered OLS instead."
    )
    assert "not all finite" in prose or "not trustworthy" in prose, (
        "the prose reports a p-value for this model without disclosing that the "
        "mixed-effects fit is degenerate. The coefficient is fine; the fit's "
        "standard errors are not."
    )
