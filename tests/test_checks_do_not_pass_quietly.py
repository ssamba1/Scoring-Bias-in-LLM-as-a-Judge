"""Can any checker report a problem and still exit zero?

The recurring defect in this repository's own verification is not a wrong
assertion. It is a check that notices it cannot verify something, says so, and
returns success. Four instances turned up in this session:

  * two build-log assertions skipped whenever the paper had not been compiled,
    which is every CI run, and a skipped test reports green
  * a mutation whose anchor stopped matching was listed as stale, after which
    mutation_check printed "every guard caught its mutation" with a quietly
    smaller count and exited 0
  * check_figures reported figures it could not check beneath a passing line
  * check_figures exited 0 when pdftotext was absent, so on any machine without
    poppler the figure check silently succeeded

Each was individually small and collectively the same thing: the apparatus is
worth exactly what it refuses to pass. This test looks for the shape rather than
the instances -- a print whose text admits an inability, followed by a success
exit in the same breath.

What it does *not* catch, stated so the coverage is not overread: an admission
on the success path of a script that exits non-zero somewhere else. Injecting
`print("cannot verify")` just above check_prose's final success line is invisible
here, because check_prose does call sys.exit(1) -- inside `if FAILS:`. Deciding
that requires following which exit each path reaches, which this does not do. A
mutation for that case was registered, found to be uncaught, and removed rather
than left as a failing entry or a passing illusion.
"""

import ast
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Words that mean "I did not check this".
ADMISSIONS = (
    "cannot", "could not", "unable", "not available", "unavailable",
    "no generator", "unverifiable", "not installed", "stale",
)

# Scripts whose job is to check something. Excludes tests/ (pytest decides the
# exit code) and RETRACTED/ (not part of the release's verification).
def _checkers():
    listing = subprocess.run(
        ["git", "ls-files", "*.py"], cwd=REPO, capture_output=True, text=True, timeout=300
    ).stdout.splitlines()
    out = []
    for rel in listing:
        if rel.startswith(("RETRACTED/", "tests/", "paper/honest/superseded/")):
            continue
        path = REPO / rel
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        if "check" not in rel and "verify" not in rel and "scan" not in rel and "mutation" not in rel:
            continue
        out.append((rel, path, body))
    if not out:
        pytest.skip("[checkers] none found")
    return out


@pytest.mark.parametrize("rel", [r for r, _, _ in _checkers()])
def test_no_admission_is_followed_by_a_success_exit(rel):
    body = dict((r, b) for r, _, b in _checkers())[rel]
    try:
        tree = ast.parse(body)
    except SyntaxError:
        pytest.skip(f"[{rel}] does not parse")

    def admission(statement):
        """Does this statement print something that admits an inability?"""
        for node in ast.walk(statement):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "print"):
                continue
            text = " ".join(
                a.value.lower()
                for a in node.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            )
            if any(word in text for word in ADMISSIONS):
                return text
        return None

    def outcome(statement):
        for node in ast.walk(statement):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
                return node.value.value
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "exit" and node.args
                    and isinstance(node.args[0], ast.Constant)):
                return node.args[0].value
            if isinstance(node, ast.Raise):
                return "raise"
        return None

    # Walk *blocks*, not lines. The admission and the exit are often separated
    # by a multi-line print, so a fixed line window misses the pairing entirely
    # -- the first version of this test did, and passed against the very defect
    # it was written for.
    offenders = []
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            block = getattr(node, field, None)
            if not isinstance(block, list):
                continue
            said = None
            for statement in block:
                # A def is one statement in its parent's block, so pairing an
                # admission inside it with "the first return found anywhere in
                # the function" is meaningless -- it flagged main() itself.
                # Function bodies are visited as their own blocks.
                if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    said = None
                    continue
                said = said or admission(statement)
                if said is None:
                    continue
                result = outcome(statement)
                if result in (1, "raise") or (isinstance(result, int) and result != 0):
                    said = None  # handled: this block fails
                elif result == 0:
                    offenders.append(f"{rel}:{statement.lineno}: {said[:80]}")
                    said = None

    # Falling off the end of a module is an implicit exit 0, and the block walk
    # above only sees explicit ones. A script that prints "cannot verify" and
    # then simply finishes is the same defect wearing no return statement -- a
    # registered mutation proved this guard missed exactly that.
    module_admissions = []
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        said = admission(statement)
        if said:
            module_admissions.append((statement.lineno, said))
    if module_admissions:
        exits_nonzero = any(
            (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "exit" and n.args
             and isinstance(n.args[0], ast.Constant) and n.args[0].value not in (0, None))
            or isinstance(n, ast.Raise)
            for statement in tree.body
            for n in ast.walk(statement)
            if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        )
        if not exits_nonzero:
            line, said = module_admissions[0]
            offenders.append(f"{rel}:{line}: {said[:80]} (module ends without a non-zero exit)")

    assert not offenders, (
        "a check says it could not verify something and then reports success: "
        + "; ".join(offenders)
        + ". Exit non-zero, or defer explicitly to a check that does cover it."
    )


def test_the_sweep_reads_the_checkers_it_should():
    """Vacuity guard: the filename filter must still match the real checkers."""
    names = {r for r, _, _ in _checkers()}
    for expected in ("mutation_check.py", "paper/honest/repro/check_prose.py",
                     "paper/honest/repro/check_figures.py", "scan_secrets.py"):
        assert expected in names, f"{expected} is no longer being swept"
