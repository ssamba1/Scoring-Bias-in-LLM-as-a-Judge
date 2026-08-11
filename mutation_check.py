#!/usr/bin/env python3
"""Do the guards fail when the thing they protect breaks?

A suite reports "all passed" whether or not its assertions could ever fail. This
repository has a specific reason to care: it published fabricated data, and the
tests added afterwards are the only thing standing between that and a repeat. A
guard that cannot fail is worse than no guard, because it is believed.

For each entry below: break the protected thing, run the named test file, and
require it to FAIL. A mutation that leaves the test green is a guard to rewrite.

Every mutation also runs against the unmutated tree first (the BASE column). A
test that was already failing would otherwise look like a successful catch.

Nothing is left modified. The original bytes are written to `.mutation_stash/`
before the file is touched, so an out-of-band kill is recoverable, and restored
in a `finally`.

    python mutation_check.py [-v]
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
STASH = BASE / ".mutation_stash"
MANIFEST = STASH / "manifest.json"

# (file, find, replace, test file, label)
MUTATIONS = [
    (
        # A fabricated model name reappears in a live file. This is the exact
        # regression that mattered: ranking_table.html sat in the live tree for
        # two weeks listing Qwen3-14B, a model that does not exist.
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct (GLM-4.7)</h2>",
        "tests/test_no_fabricated_artefacts.py",
        "fabricated model name returns to a live page",
    ),
    (
        # The fabricated per-domain values return, by value rather than by name.
        # Written literally: the first attempt inserted "1.52 &amp; 0.98" and the
        # sweep correctly did not match it, because the entity puts "amp;"
        # between the number and the ampersand. The mutation was wrong, not the
        # guard -- which is the whole reason to run mutations against a baseline.
        "paper/interactive/index.html",
        '<span class="tag chart">paired chart</span>',
        '<span class="tag chart">paired chart 1.52 & 0.98</span>',
        "tests/test_no_fabricated_artefacts.py",
        "fabricated domain values return",
    ),
    (
        # The quarantine loses its explanation. Moving files without saying why
        # is not a retraction.
        "RETRACTED/README.md",
        "do not use or cite",
        "archived materials",
        "tests/test_no_fabricated_artefacts.py",
        "retraction notice loses its warning",
    ),
    (
        # A whole quarantined group stops being described. This one needs every
        # occurrence replaced: the path appears three times, and the guard only
        # asks whether it appears at all, so mutating the first left the test
        # satisfied by the other two and the guard looked broken when it was not.
        "RETRACTED/README.md",
        "paper/interactive/",
        "paper/elsewhere/",
        "tests/test_no_fabricated_artefacts.py",
        "quarantined group undocumented",
        True,
    ),
    (
        # The paper is edited without repackaging: the archive is now stale and
        # would ship the previous text.
        "paper/honest/scoring_bias_v2.tex",
        "\\section*{Reproducibility}",
        "\\section*{Reproducibility and Data}",
        "tests/test_submission_is_buildable.py",
        "paper edited without repackaging",
    ),
]


def _read(path: Path):
    try:
        return path.read_text(encoding="utf-8"), True
    except UnicodeDecodeError:
        return path.read_bytes(), False


def _write(path: Path, data, is_text: bool):
    if is_text:
        path.write_text(data, encoding="utf-8", newline="")
    else:
        path.write_bytes(data)


def _stash(rel: str, data, is_text: bool):
    STASH.mkdir(exist_ok=True)
    target = STASH / rel.replace("/", "__")
    _write(target, data, is_text)
    MANIFEST.write_text(json.dumps({"file": rel, "stash": target.name}), encoding="utf-8")


def _clear_stash():
    shutil.rmtree(STASH, ignore_errors=True)


def _run(test_file: str):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-q", "--no-header", "-x"],
        cwd=BASE,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return result.returncode


def main(verbose=False):
    if not (BASE / "tests").is_dir():
        raise SystemExit("no tests/ directory")

    print(f"{'mutation':46s} {'BASE':>5} {'MUT':>5}  verdict")
    print("-" * 72)

    misses, stale = [], []
    for entry in MUTATIONS:
        rel, find, replace, test_file, label = entry[:5]
        replace_all = len(entry) > 5 and entry[5]
        path = BASE / rel
        if not path.exists():
            stale.append(f"{label}: {rel} absent")
            continue
        original, is_text = _read(path)
        if not is_text or find not in original:
            stale.append(f"{label}: anchor not found in {rel}")
            print(f"{label:46s} {'-':>5} {'-':>5}  ** STALE ANCHOR **")
            continue
        if original.count(find) > 1 and not replace_all:
            print(f"  (note: {label} anchor occurs {original.count(find)}x; first is mutated)")

        base_rc = _run(test_file)
        _stash(rel, original, is_text)
        try:
            mutated = original.replace(find, replace) if replace_all else original.replace(find, replace, 1)
            _write(path, mutated, is_text)
            mutated_rc = _run(test_file)
        finally:
            _write(path, original, is_text)
            _clear_stash()

        caught = base_rc == 0 and mutated_rc != 0
        verdict = "ok" if caught else ("BASE ALREADY RED" if base_rc != 0 else "NOT CAUGHT")
        if not caught:
            misses.append(label)
        print(f"{label:46s} {base_rc:>5} {mutated_rc:>5}  {verdict}")

    print()
    if stale:
        print("mutations whose anchor no longer matches:", stale)
    if misses:
        print("guards that did NOT catch their mutation:", misses)
        return 1
    checked = len(MUTATIONS) - len(stale)
    print(f"every guard caught its mutation ({checked} checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main("-v" in sys.argv))
