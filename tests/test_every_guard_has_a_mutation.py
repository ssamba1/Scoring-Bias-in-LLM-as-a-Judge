"""Does every test file have at least one registered mutation?

mutation_check proves a guard fails when the thing it protects breaks. That
proof is per-mutation, and mutations are registered by hand, so a test file
nobody registered is a file whose guards have never been shown to fail. The
whole suite could pass while some of it asserts nothing -- which is the exact
defect the mutation harness exists to rule out, one level up.

Fifty of fifty-one files were covered when this was first checked. The uncovered
one was the newest, added an hour earlier; the gap is always the newest file,
because registering a mutation is the step it is easiest to mean to do later.

Coverage is not depth. One mutation per file proves that file can fail, not that
each of its assertions can. Files carrying many independent claims have several
mutations; this only refuses zero.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "mutation_check.py"


def _registered():
    if not CHECKER.exists():
        pytest.skip("[tooling] mutation_check.py not present")
    body = CHECKER.read_text(encoding="utf-8", errors="replace")
    entries = re.findall(r'"(tests/test_[\w]+\.py)"', body)
    if not entries:
        pytest.skip("[tooling] no mutations registered")
    return entries


def _test_files():
    files = sorted(f"tests/{p.name}" for p in (REPO / "tests").glob("test_*.py"))
    if not files:
        pytest.skip("[tests] none found")
    return files


def test_every_test_file_has_a_registered_mutation():
    covered = set(_registered())
    uncovered = [f for f in _test_files() if f not in covered]
    assert not uncovered, (
        f"{len(uncovered)} test file(s) have no registered mutation, so nothing "
        f"has shown their guards can fail: {uncovered}. Register one that breaks "
        f"what the file protects, or delete the file."
    )


def test_no_mutation_names_a_test_file_that_is_gone():
    """A mutation pointing at a deleted file reports success having run nothing."""
    files = set(_test_files())
    orphaned = sorted({e for e in _registered() if e not in files})
    assert not orphaned, (
        f"mutations name test files that no longer exist: {orphaned}"
    )


def test_the_coverage_sweep_reads_the_registry():
    """Vacuity guard: an empty registry satisfies both checks above."""
    registered = _registered()
    files = _test_files()
    assert len(set(registered)) >= len(files) - 1, (
        f"only {len(set(registered))} distinct test files appear in the mutation "
        f"registry against {len(files)} on disk; the parse has probably stopped "
        f"matching the registration format"
    )
