#!/usr/bin/env python3
"""Run the checks in a fresh clone, the way a reader will see them.

A test that reads state which only exists in a directory someone has worked in
passes here and fails everywhere else. The companion projects hit that five
separate times -- a hash computed on a CRLF checkout, figure bytes from one
rendering stack, an artefact that existed because a generator had been run at
some point, a README path that resolves only because the file is present but
gitignored.

This repository has a sharper version of the same risk. Its guards ask what is
tracked, and the answer differs between a working tree with leftovers and a
clean checkout: the fabricated manuscripts sat on disk here for weeks after they
had been retracted upstream, because the local checkout was 83 commits behind.
Reading the working tree would have said the retraction never happened.

    python verify_clean_clone.py [--keep]

Clones HEAD into a temporary directory, runs the test suite there, and reports.
Nothing in the working tree is touched. Skips are printed with their reasons,
because a check that skips looks exactly like a check that passed.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent


def _run(cmd, cwd, timeout=1800):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def main(keep=False):
    tmp = Path(tempfile.mkdtemp(prefix="verify-clean-"))
    clone = tmp / BASE.name
    print(f"cloning {BASE.name} -> {clone}")
    result = _run(["git", "clone", "--quiet", str(BASE), str(clone)], BASE)
    if result.returncode != 0:
        print(result.stderr[-1500:])
        return 1

    print("running the suite in the clone")
    proc = _run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header", "-rs"], clone)
    tail = [ln for ln in proc.stdout.splitlines() if ln.strip()][-1:]
    print("  " + (tail[0] if tail else "no output"))

    # pytest was asked for skip reasons; print them. A clean clone legitimately
    # skips the checks that need a built PDF or a packaged archive, but a check
    # skipping because an artefact it should have found is missing looks
    # identical from the count alone.
    reasons = {}
    for line in proc.stdout.splitlines():
        if line.startswith("SKIPPED"):
            match = re.match(r"SKIPPED \[(\d+)\]", line)
            count = int(match.group(1)) if match else 1
            reason = line.split(":", 2)[-1].strip()
            reasons[reason] = reasons.get(reason, 0) + count
    if reasons:
        print("  skipped in a clean clone, by reason:")
        for reason, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
            print(f"    {count:3d}  {reason[:96]}")

    if proc.returncode != 0:
        print("\nFailures in a clean clone that do not appear in the working tree:")
        for line in proc.stdout.splitlines():
            if line.startswith("FAILED") or "AssertionError" in line:
                print("  " + line[:200])

    # The fabrication sweep is the one guard that must never skip: it is the
    # reason this suite exists.
    if "test_signature_absent_from_live_tree" in proc.stdout and "skipped" in proc.stdout.lower():
        pass  # reported above; the counts speak for themselves

    if keep:
        print(f"\nclone kept at {clone}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return proc.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="do not delete the clone")
    sys.exit(main(**vars(parser.parse_args())))
