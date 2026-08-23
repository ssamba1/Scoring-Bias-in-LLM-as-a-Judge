"""Do any of the analysis scripts round values before aggregating them?

`analyze_robustness.py` used to build the leave-one-family-out effects like this:

    loo_eff = {f: round(float(np.mean(...)), 3) for f in fam_effect}
    ...
    "loo_range": [min(loo_eff.values()), max(loo_eff.values())]

The maximum is 0.28464. Rounded to three decimals first it becomes 0.285, and
the paper then rounded that to 0.29 -- a digit the exact value never reaches
under any convention. Aggregating over already-rounded values is how a stored
number acquires precision it does not have, and it is the only mechanism found
in this repository that manufactured a wrong digit *inside* a released file
rather than between the file and the page.

The check is structural rather than numeric: find every name bound to a
comprehension whose element is a `round(...)` call, then look for that name
inside a call to min, max, sum, mean, median, sorted, or a correlation. The
correct order is the reverse -- aggregate exactly, round once for storage --
and `round(np.mean(xs), 3)` is not flagged, because the mean is taken first.

Run against the commit before the fix, this reports the two `loo_eff` uses. It
reports nothing now, and `test_the_detector_finds_the_pattern_it_looks_for`
keeps that zero from becoming vacuous.
"""

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

AGGREGATORS = {
    "min", "max", "sum", "sorted", "mean", "median", "std", "var",
    "percentile", "spearmanr", "pearsonr", "wilcoxon", "argmax", "argmin",
}


def _element_is_round(node):
    """True when the comprehension's element expression is a round() call."""
    for attr in ("elt", "value"):
        element = getattr(node, attr, None)
        if isinstance(element, ast.Call) and getattr(element.func, "id", "") == "round":
            return True
    return False


def _offenders(source):
    """(name, definition line, use line, aggregator) for each bad ordering."""
    tree = ast.parse(source)
    rounded = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(
            node.value, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)
        ):
            if _element_is_round(node.value):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        rounded[target.id] = node.lineno

    hits = []
    if not rounded:
        return hits
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name not in AGGREGATORS:
            continue
        for argument in node.args:
            for sub in ast.walk(argument):
                if isinstance(sub, ast.Name) and sub.id in rounded:
                    hits.append((sub.id, rounded[sub.id], node.lineno, name))
    return hits


def test_no_analysis_script_aggregates_over_rounded_values():
    if not REPRO.exists():
        pytest.skip("[repro] analysis directory not present")
    scripts = sorted(REPRO.glob("*.py"))
    assert scripts, "no analysis scripts found to check"

    problems = []
    for path in scripts:
        try:
            hits = _offenders(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for name, defined, used, aggregator in hits:
            problems.append(
                f"{path.name}: '{name}' is built with round() at line {defined} "
                f"and aggregated by {aggregator}() at line {used}"
            )

    assert not problems, (
        "these aggregate over already-rounded values, which is how 0.28464 "
        "became a stored 0.285 and then a printed 0.29:\n  "
        + "\n  ".join(problems)
        + "\nAggregate exactly and round once for storage."
    )


def test_the_detector_finds_the_pattern_it_looks_for():
    """Vacuity guard: a checker that cannot fail proves nothing by passing."""
    bad = (
        "vals = {k: round(mean(v), 3) for k, v in data.items()}\n"
        "out = [min(vals.values()), max(vals.values())]\n"
    )
    assert _offenders(bad), "the detector no longer finds the ordering it exists to find"

    good = (
        "vals = {k: mean(v) for k, v in data.items()}\n"
        "out = [round(min(vals.values()), 3), round(max(vals.values()), 3)]\n"
    )
    assert not _offenders(good), (
        "the detector flags the correct ordering -- aggregate first, round once -- "
        "which would make it noise rather than a check"
    )
