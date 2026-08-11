"""Is every committed derived result actually regenerated and diffed in CI?

The reproduction gate is a hand-maintained list: repro.yml names each analysis
to run and each output to diff. A list like that is only as complete as the last
person to edit it, and it silently omitted `results_14b_analysis.json` -- the
14B extension the paper cites for "positive for 3/5 probes". That file sat in
the tree deriving from nothing anyone checked, which is the same standing as a
number typed by hand.

The failure is not that one entry was forgotten. It is that forgetting had no
consequence. This reads the derived files off disk and requires the workflow to
cover each one, so the next omission fails instead of going quiet.

Coverage means two distinct things, and both are required:

  regenerated -- some step recomputes it from raw data
  diffed      -- the final `git diff --exit-code` names it

Regenerating without diffing proves nothing (the run recomputes the file and
throws the result away); diffing without regenerating compares a file to itself
and always passes. Only the pair is a reproduction check.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
WORKFLOW = REPO / ".github" / "workflows" / "repro.yml"

# Derived files whose names do not end in _analysis.json. Listed explicitly
# because there is no way to tell them from raw inputs by name alone; the test
# below asserts each still exists, so a rename cannot quietly empty this set.
DERIVED_WITHOUT_SUFFIX = {
    "results_peritem.json",
    "results_mechanism.json",
    "results_gold.json",
    "results_robustness.json",
    "spanpatch_analysis.json",
}


def _workflow():
    if not WORKFLOW.exists():
        pytest.skip("[workflow] repro.yml not present")
    return WORKFLOW.read_text(encoding="utf-8", errors="replace")


def _tracked_repro_json():
    listing = subprocess.run(
        ["git", "ls-files", "paper/honest/repro"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return [Path(line).name for line in listing.stdout.splitlines() if line.endswith(".json")]


def _derived_files():
    names = _tracked_repro_json()
    if not names:
        pytest.skip("[repro data] no tracked result files")
    derived = {n for n in names if n.endswith("_analysis.json")}
    derived |= {n for n in DERIVED_WITHOUT_SUFFIX if n in names}
    return sorted(derived)


def _diff_list(workflow):
    """The filenames named by the final `git diff --exit-code` step."""
    start = workflow.find("git diff --exit-code")
    assert start != -1, "repro.yml no longer runs `git diff --exit-code`"
    return set(re.findall(r"([\w.-]+\.json)", workflow[start:]))


def test_every_derived_file_is_diffed():
    workflow = _workflow()
    diffed = _diff_list(workflow)
    missing = [name for name in _derived_files() if name not in diffed]
    assert not missing, (
        f"{len(missing)} derived file(s) are committed but never compared against "
        f"a fresh run: {missing}. Add them to the `git diff --exit-code` step in "
        f"repro.yml, or delete them if they are no longer cited."
    )


def test_every_derived_file_is_regenerated():
    """Each derived file must be recomputed, not merely diffed against itself.

    Most analyses write a fixed output name, so the presence of the script is
    enough. `analyze_newprobes.py` is the exception: it takes the raw file as an
    argument and writes `<stem>_analysis.json`, so covering one input says
    nothing about another -- which is exactly how the 14B run was missed.
    """
    workflow = _workflow()
    run_section = workflow[: workflow.find("git diff --exit-code")]
    invoked = set(re.findall(r"analyze_newprobes\.py\s+([\w.-]+\.json)", run_section))

    uncovered = []
    for name in _derived_files():
        stem = name[: -len("_analysis.json")] if name.endswith("_analysis.json") else None
        source = f"{stem}.json" if stem else None
        # Only decidable for the newprobes family: its output is named after its
        # input. A source file that exists but is never passed to the script is
        # a derived file nothing recomputes.
        if source and (REPRO / source).exists() and source in {f"{s[:-5]}.json" for s in invoked} | invoked:
            continue
        if source and (REPRO / source).exists() and source not in invoked:
            # Distinguish "written by newprobes" from "written by its own script".
            script = REPRO / f"analyze_{stem.replace('results_', '')}.py"
            if not script.exists():
                uncovered.append(f"{name} (nothing in repro.yml recomputes it from {source})")
    assert not uncovered, (
        "derived file(s) diffed but never regenerated, so the diff compares them "
        f"to themselves and always passes: {uncovered}"
    )


def test_the_derived_list_is_not_empty_or_stale():
    """Vacuity guard: renames must not silently empty the set being checked."""
    derived = _derived_files()
    assert len(derived) >= 12, f"only {len(derived)} derived files found: {derived}"
    tracked = set(_tracked_repro_json())
    gone = sorted(DERIVED_WITHOUT_SUFFIX - tracked)
    assert not gone, (
        f"{gone} is named as a derived file but is no longer tracked; update "
        f"DERIVED_WITHOUT_SUFFIX rather than leaving a name that matches nothing"
    )
