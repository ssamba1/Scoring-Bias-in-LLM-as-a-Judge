"""Could any test in this suite pass no matter what?

mutation_check proves that 130 specific guards fail when the thing they protect
breaks. It says nothing about the other several hundred assertions. A test that
cannot fail is worse than no test, because the count includes it and the count
is what gets quoted -- this suite's size is cited in commit messages and in
comparisons against the companion projects.

Two shapes are checked:

  * a test function with no assertion and no call that raises on failure
  * an assertion that is true by construction -- `assert True`,
    `assert isinstance(x, list)` on a list that was just built, `assert x or True`

The second found a real one. `test_superseded_outputs_are_not_shared_with_the_paper`
ended in `assert isinstance(clashes, list)`, left behind when I replaced its
logic and reasoned that the property was covered elsewhere. It was not covered;
it was simply not checked. Rewriting it to compare the drawn text of the live
and superseded copies immediately found two figures in the paper's directory
that belonged to the superseded draft.
"""

import ast
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Tests whose failure mode is an exception rather than an assertion, with the
# reason. Anything here is exempt from the "no assertion" rule only.
RAISES_INSTEAD = {
    "test_it_validates_against_the_real_schema_when_that_is_possible":
        "cffconvert's validate() raises on an invalid record",
}


def _test_files():
    listing = subprocess.run(
        ["git", "ls-files", "tests/*.py"], cwd=REPO, capture_output=True, text=True, timeout=300
    ).stdout.split()
    files = [(rel, REPO / rel) for rel in listing if Path(rel).name.startswith("test_")]
    if not files:
        pytest.skip("[tests] none found")
    return files


def _functions(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test")]


def test_every_test_can_fail():
    """No test may be free of both assertions and raising calls."""
    bare = []
    for rel, path in _test_files():
        for func in _functions(path):
            if func.name in RAISES_INSTEAD:
                continue
            has_assert = any(isinstance(n, ast.Assert) for n in ast.walk(func))
            has_raises = any(
                isinstance(n, ast.Call) and getattr(n.func, "attr", "") in ("raises", "warns")
                for n in ast.walk(func)
            )
            if not has_assert and not has_raises:
                bare.append(f"{rel}::{func.name}")
    assert not bare, (
        f"{len(bare)} test(s) contain no assertion and nothing that raises, so "
        f"they pass regardless: {bare}. Add the check, or record why the call "
        f"itself is the check in RAISES_INSTEAD."
    )


def test_no_assertion_is_true_by_construction():
    trivial = []
    for rel, path in _test_files():
        for func in _functions(path):
            for node in ast.walk(func):
                if not isinstance(node, ast.Assert):
                    continue
                test = node.test
                if isinstance(test, ast.Constant):
                    trivial.append(f"{rel}::{func.name}: assert {test.value!r}")
                elif (isinstance(test, ast.Call) and isinstance(test.func, ast.Name)
                      and test.func.id == "isinstance"):
                    trivial.append(f"{rel}::{func.name}: assert isinstance(...)")
                elif (isinstance(test, ast.BoolOp) and isinstance(test.op, ast.Or)
                      and any(isinstance(v, ast.Constant) and v.value for v in test.values)):
                    trivial.append(f"{rel}::{func.name}: assert ... or True")
    assert not trivial, (
        f"{len(trivial)} assertion(s) are true by construction and cannot fail: "
        f"{trivial}"
    )


def test_the_sweep_sees_the_whole_suite():
    """Vacuity guard for the vacuity guard."""
    total = sum(len(_functions(path)) for _, path in _test_files())
    assert total >= 100, (
        f"only {total} test functions parsed across {len(_test_files())} files; "
        f"the sweep is looking at far less than the suite"
    )
