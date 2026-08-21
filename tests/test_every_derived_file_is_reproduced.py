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

# Derived files whose names do not end in _analysis.json. There is no way to
# tell them from raw inputs by name alone, so they were listed by hand -- and
# the list went stale exactly the way this file's docstring warns a list does.
# Five analyses added after it was written (nulls, bands, readout,
# quantization, speccurve) write outputs that end in neither _analysis.json nor
# any name here, so they fell out of the guard, and out of the workflow's diff
# list with nothing to notice.
#
# The set is still written down, because a reader should be able to see it. But
# it is no longer trusted: _analyzer_outputs() below reads the write targets off
# the analyses themselves, and a test requires the two to agree. Adding a
# nineteenth analysis now fails here until its output is covered.
DERIVED_WITHOUT_SUFFIX = {
    "results_peritem.json",
    "results_mechanism.json",
    "results_gold.json",
    "results_robustness.json",
    "spanpatch_analysis.json",
    "results_nulls.json",
    "results_bands.json",
    "results_readout.json",
    "results_quantization.json",
    "results_speccurve.json",
}

# `p = HERE / "x.json"` followed by `p.write_text(...)`, and the direct form.
_ASSIGNED = re.compile(r'^\s*(\w+)\s*=\s*HERE\s*/\s*"([A-Za-z0-9_]+\.json)"', re.M)
_LITERAL = re.compile(r'"([A-Za-z0-9_]+\.json)"')


def _analyzer_outputs():
    """Every file an analyze_*.py writes, read from the analyses themselves.

    Templated targets are deliberately not resolved. analyze_newprobes.py
    writes f"{stem}_analysis.json" for three different inputs, and those are
    covered by the _analysis.json suffix rule rather than by name.
    """
    outputs = set()
    for source in sorted(REPRO.glob("analyze_*.py")):
        text = source.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if "write_text" in line or "write_bytes" in line:
                outputs |= set(_LITERAL.findall(line))
        for variable, name in _ASSIGNED.findall(text):
            if re.search(rf"\b{variable}\.write_(?:text|bytes)", text):
                outputs.add(name)
    return outputs


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
        produced = {f"{s[:-5]}.json" for s in invoked} | invoked
        if source and (REPRO / source).exists() and source in produced:
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


def test_the_derived_list_is_what_the_analyses_actually_write():
    """The hand-written set must equal what the analyses produce.

    This is the check that was missing. The previous list was correct when it
    was written and wrong five analyses later, with nothing to say so -- the
    same shape as the omission it was created to prevent, one level up.
    """
    written = _analyzer_outputs()
    if not written:
        pytest.skip("[repro] no analyses found to read write targets from")

    covered = {name for name in written if name.endswith("_analysis.json")}
    needing_entry = written - covered

    missing = sorted(needing_entry - DERIVED_WITHOUT_SUFFIX)
    assert not missing, (
        f"{missing} are written by an analysis but named nowhere in "
        f"DERIVED_WITHOUT_SUFFIX, so the coverage checks in this file skip "
        f"them entirely -- which is how five outputs came to be regenerated in "
        f"CI and never diffed."
    )

    stale = sorted(
        name for name in DERIVED_WITHOUT_SUFFIX
        if name not in written and not name.endswith("_analysis.json")
    )
    assert not stale, (
        f"{stale} are listed as derived but no analysis writes them. Either the "
        f"analysis was removed and the entry outlived it, or the write target "
        f"was renamed and this list still names the old one."
    )
