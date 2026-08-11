"""Does the paper describe the mixed-effects model it actually fits?

The paper said "random intercepts for family and item". The analysis fits

    mixedlm("dev ~ C(kind, ...)", df, groups=df["family"], re_formula="1")

which is a random intercept for family alone. An `item` column is built and
never used as a random effect, and statsmodels needs `vc_formula` for a crossed
term, which does not appear.

The difference is not cosmetic. Item intercepts absorb item-level variance, so
claiming them describes a more conservative model than was fitted -- the usual
direction of an accidental overstatement, and one no reader can check without
reading the analysis source.

Refitting the described model settles it: the item variance component comes out
at 5e-05, the coefficient is unchanged at 0.1559, and the fit does not converge
because the covariance is singular. So the coded model is the right one and the
sentence was wrong. The sentence now says "random intercept for family" and
notes that the crossed term adds nothing.

This checks that the two stay in step. It is deliberately narrow: it reads which
grouping factors the code declares and requires the prose not to claim a random
effect the code does not fit. It does not try to parse the model formula in
general.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
ANALYSIS = HONEST / "repro" / "analyze_mechanism.py"
MACROS = HONEST / "macros.tex"


def _analysis():
    if not ANALYSIS.exists():
        pytest.skip("[analysis] analyze_mechanism.py not present")
    return ANALYSIS.read_text(encoding="utf-8", errors="replace")


def _macros():
    if not MACROS.exists():
        pytest.skip("[macros] macros.tex not present")
    return MACROS.read_text(encoding="utf-8", errors="replace")


def _fitted_random_effects():
    """The grouping factors the mixedlm call actually declares."""
    source = _analysis()
    call = re.search(r"mixedlm\((.{0,400}?)\)\.fit", source, re.S)
    assert call, "no mixedlm(...).fit(...) call found in analyze_mechanism.py"
    body = call.group(1)

    effects = set()
    groups = re.search(r"groups\s*=\s*df\[[\"'](\w+)[\"']\]", body)
    if groups:
        effects.add(groups.group(1))
    # Crossed / nested terms only exist if vc_formula names them.
    for name in re.findall(r"vc_formula\s*=\s*\{([^}]*)\}", body):
        effects |= set(re.findall(r"[\"'](\w+)[\"']\s*:", name))
    return effects


def test_the_prose_claims_no_random_effect_the_model_lacks():
    fitted = _fitted_random_effects()
    assert fitted, "could not determine the model's grouping factors"

    text = _macros()
    described = re.search(
        r"random intercepts?\s+for\s+([^;,)]+)", text, re.I
    )
    assert described, "the paper no longer describes the model's random effects"

    claimed = {
        word.strip().lower()
        for word in re.split(r"\band\b|,", described.group(1))
        if word.strip()
    }
    # "family" and "item" are the only random-effect nouns in play; ignore any
    # descriptive words that survive the split.
    claimed &= {"family", "item", "probe", "checkpoint", "judge"}

    overclaimed = sorted(claimed - fitted)
    assert not overclaimed, (
        f"the paper claims random intercepts for {sorted(claimed)}, but the "
        f"fitted model declares only {sorted(fitted)}. Claiming {overclaimed} "
        f"describes a more conservative model than was fitted."
    )


def test_the_reported_n_is_the_per_item_row_count():
    """n = 13,000 must be the model's row count, not a design multiplication.

    The retracted version's counts were design arithmetic -- an intended number
    of judgments multiplied out, never the size of a real table. This ties the
    figure in the prose to the value the fit reports.
    """
    import json

    mech = HONEST / "repro" / "results_mechanism.json"
    if not mech.exists():
        pytest.skip("[mechanism] results_mechanism.json not present")
    lmm = json.loads(mech.read_text(encoding="utf-8", errors="replace")).get("lmm", {})
    if "n_obs" not in lmm:
        pytest.skip("[lmm] the fit reported no n_obs")

    text = _macros()
    # LaTeX closes math before the noun: "$n=13{,}000$ per-item deviations".
    stated = re.search(r"n=([\d,{}\\]+)\$?\s*per-item deviations", text)
    assert stated, "the paper no longer states the model's n as per-item deviations"
    n = int(re.sub(r"[^\d]", "", stated.group(1)))
    assert n == lmm["n_obs"], (
        f"the paper reports n={n:,} for the mixed model; the fit used "
        f"{lmm['n_obs']:,} rows"
    )


def test_the_extractor_finds_the_call():
    """Vacuity guard: a refactor must not leave the checks above parsing nothing."""
    assert _fitted_random_effects(), "the mixedlm call could no longer be parsed"
