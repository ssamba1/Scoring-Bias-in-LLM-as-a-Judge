"""Can two mutation runs, or one killed run, leave a mutation in the tree?

mutation_check edits a source file, runs one test against it, and restores the
original. The restore sits in a `finally`, which covers an exception and does
not cover a kill or a second run.

Both happened. verify_like_ci.py invokes the checker, so running it beside a
direct invocation is enough for two runs to share one working tree: the second
reads an already-mutated file as its "original" and writes that back as its
restore, at which point the mutation is permanent and the tree looks clean. That
left macros.tex carrying an invented preregistration id (P4x) and a wrong pooled
n (155 for 145) -- a deliberately broken paper source, indistinguishable from an
honest edit in a later diff.

A kill leaves the same thing behind by a shorter route: the process dies between
writing the mutation and restoring it.

So the checker now takes an exclusive lock and recovers on the way in. This
tests both, which needs care: naively "test the mutation checker" means running
it, and a full run takes ten minutes and mutates the tree this suite is reading.
The refusal path exits immediately, and recovery is exercised against a
temporary directory rather than the repository.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "mutation_check.py"


def _module():
    if not CHECKER.exists():
        pytest.skip("[tooling] mutation_check.py not present")
    spec = importlib.util.spec_from_file_location("mutation_check_under_test", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_second_run_is_refused_while_one_holds_the_lock(tmp_path):
    module = _module()
    stash = REPO / module.STASH.name
    assert stash == module.STASH, "the stash is expected in the repository root"
    if stash.exists():
        pytest.skip("[tooling] a mutation run is in progress")

    stash.mkdir()
    try:
        (stash / module.LOCK.name).write_text(json.dumps({"pid": 1}), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CHECKER)], cwd=REPO,
            capture_output=True, text=True, timeout=300,
        )
        assert result.returncode != 0, (
            "a second run started while the lock was held; it would read a "
            "mutated file as its original and make the mutation permanent"
        )
        assert "lock" in (result.stdout + result.stderr).lower(), (
            f"the refusal does not say why: {result.stdout[-300:]!r}"
        )
        # The refused run must leave the holder's stash alone. Releasing
        # unconditionally would delete the only copy of the file the active run
        # is holding mutated -- the refusal causing the damage it prevents.
        assert (stash / module.LOCK.name).exists(), (
            "the refused run deleted the lock it was refused by; whatever the "
            "active run had stashed is gone with it"
        )
    finally:
        if stash.exists():
            for path in stash.glob("*"):
                path.unlink()
            stash.rmdir()


def test_an_interrupted_run_is_recovered(tmp_path, monkeypatch):
    """A file left mutated by a killed run is restored on the next start."""
    module = _module()
    victim = tmp_path / "paper" / "source.tex"
    victim.parent.mkdir(parents=True)
    original = b"the pooled relation holds at n=145\r\n"
    victim.write_bytes(original)

    stash = tmp_path / ".mutation_stash"
    stash.mkdir()
    (stash / "paper__source.tex").write_bytes(original)
    (stash / "manifest.json").write_text(
        json.dumps({"file": "paper/source.tex", "stash": "paper__source.tex"}),
        encoding="utf-8",
    )
    # what a killed run leaves behind
    victim.write_bytes(original.replace(b"145", b"155"))

    monkeypatch.setattr(module, "BASE", tmp_path)
    monkeypatch.setattr(module, "STASH", stash)
    monkeypatch.setattr(module, "MANIFEST", stash / "manifest.json")

    recovered = module._recover()
    assert recovered == "paper/source.tex", (
        f"the interrupted mutation was not recovered (got {recovered!r}); it "
        f"would stay in the tree as a deliberately wrong number"
    )
    assert victim.read_bytes() == original, "recovery did not restore the bytes"


def test_recovery_is_silent_when_there_is_nothing_to_recover(tmp_path, monkeypatch):
    """A clean stash must not be reported as a recovery, or the message lies."""
    module = _module()
    victim = tmp_path / "paper" / "source.tex"
    victim.parent.mkdir(parents=True)
    victim.write_bytes(b"unchanged\r\n")
    stash = tmp_path / ".mutation_stash"
    stash.mkdir()
    (stash / "paper__source.tex").write_bytes(b"unchanged\r\n")
    (stash / "manifest.json").write_text(
        json.dumps({"file": "paper/source.tex", "stash": "paper__source.tex"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "BASE", tmp_path)
    monkeypatch.setattr(module, "STASH", stash)
    monkeypatch.setattr(module, "MANIFEST", stash / "manifest.json")

    assert module._recover() is None


def test_the_lock_lives_where_it_is_ignored():
    """A lock file outside the ignored stash would show up as untracked."""
    module = _module()
    assert module.LOCK.parent == module.STASH, (
        "the lock sits outside the stash directory, so it is not covered by "
        "the .gitignore entry that keeps run state out of commits"
    )
