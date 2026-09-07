"""Can every registered mutation still find the text it mutates?

`mutation_check.py` proves each guard can fail by editing the thing it guards
and requiring the guard to notice. That proof is only as good as the anchor: if
the find-string is no longer in the file, the mutation cannot be applied, the
guard is never exercised, and the registration sits there looking like coverage.

The mutation pass detects this, and takes the better part of an hour to do it --
309 mutations, each running a test suite. This asks the same question by reading
the files, in about a second, so an anchor broken by an ordinary edit is caught
before a commit rather than after a full gate.

It has already earned that. Three edits in one session silently disarmed a
guard, and none of them looked like it touched a guard at all:

  * widening a table column past a bare macro made
    test_the_positioning_row_matches_the_study skip instead of run;
  * the sentence "every prediction WAS REGISTERED before its data existed"
    contains the substring "as registered", which satisfied the P4 guard's
    alternation on its own;
  * and rewrapping a Related Work sentence -- no words changed, nothing visible
    in the PDF -- split "thirteen instruction-tuned judges on answers from both
    base and instruction-tuned" across a newline, so the mutation registered
    against it could no longer be applied.

Only the third is in scope here; the first two are the reason to distrust the
assumption that guards stay armed. LaTeX reflow is invisible in the output and
routine in the source, which makes a byte anchor in prose exactly the kind of
thing that rots quietly.
"""

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "mutation_check.py"


def _mutations():
    if not CHECKER.exists():
        pytest.skip("[mutation] mutation_check.py not present")
    spec = importlib.util.spec_from_file_location("_mutation_check", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    entries = getattr(module, "MUTATIONS", None)
    if not entries:
        pytest.fail("mutation_check.py defines no MUTATIONS list to check")
    return entries


def test_every_mutation_target_file_exists():
    missing = sorted({
        f"{entry[4]!r} -> {entry[0]}"
        for entry in _mutations()
        if not (REPO / entry[0]).exists()
    })
    assert not missing, (
        "registered mutations naming a file that is not there, so they can "
        "never run: " + "; ".join(missing)
    )


def test_every_mutation_anchor_is_present_in_its_file():
    """A find-string that matches nothing is a registration, not a check."""
    absent = []
    for entry in _mutations():
        path, find, label = entry[0], entry[1], entry[4]
        target = REPO / path
        if not target.exists():
            continue  # reported by the test above
        if find not in target.read_text(encoding="utf-8", errors="replace"):
            absent.append(f"{label!r} in {path}")
    assert not absent, (
        "registered mutations whose anchor is no longer in the file. The guard "
        "they are supposed to exercise is not being exercised: "
        + "; ".join(sorted(absent))
        + ". Restore the anchored text, or re-anchor the entry deliberately -- "
        "and if the mutation is obsolete, delete it rather than leaving a "
        "registration nothing runs."
    )


def test_every_mutation_names_a_guard_that_exists():
    missing = sorted({
        f"{entry[4]!r} -> {entry[3]}"
        for entry in _mutations()
        if not (REPO / entry[3]).exists()
    })
    assert not missing, (
        "registered mutations naming a guard file that does not exist: "
        + "; ".join(missing)
    )


def test_the_registry_is_actually_being_read():
    """Vacuity guard: every assertion above passes on an empty list."""
    entries = _mutations()
    assert len(entries) >= 200, (
        f"only {len(entries)} mutations parsed from mutation_check.py; the "
        f"registry held 309 when this was written, so a count this low means "
        f"the parse broke rather than the registry shrinking"
    )
    assert all(len(entry) >= 5 for entry in entries), (
        "a mutation entry is not the (path, find, replace, guard, label) shape "
        "this guard reads"
    )
