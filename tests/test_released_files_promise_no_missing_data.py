"""Does a released file carry an empty container a reader would misread?

`patch_results.json` ships `"raw": []` and `"per_layer_gap_closed": {}`. Both
are empty because the harness initialised them and never wrote to them. Nothing
reads either one, and the causal claim rests on `frac_toward_instruct`,
`median_recovery`, `n_items_used` and `best_layer`, all of which are there.

But a reader auditing a retracted-and-rewritten project opens the patching data,
sees an empty `raw`, and has to decide whether the per-item records were
withheld, lost, or never collected. Only the third is true. In this repository
that ambiguity costs more than the key is worth: the audit it is answering found
invented numbers, so absent data invites the worst reading.

The harness no longer emits either key, ENVIRONMENT.md records why the existing
files still do, and this refuses new ones. The released files themselves are
left exactly as produced -- they are the record of what ran, and editing raw
outputs to look tidier is the habit this project is furthest from.
"""

import ast
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Empty containers already in the release, each documented in ENVIRONMENT.md.
KNOWN = {
    ("patch_results.json", "raw"),
    ("patch_results.json", "per_layer_gap_closed"),
    ("patch_results_qwen05.json", "raw"),
    ("patch_results_qwen05.json", "per_layer_gap_closed"),
}


def _released():
    listing = subprocess.run(
        ["git", "ls-files", "paper/honest/repro/*.json"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    ).stdout.split()
    files = [REPO / rel for rel in listing if (REPO / rel).exists()]
    if not files:
        pytest.skip("[repro] no released JSON files")
    return files


def test_no_new_released_file_carries_an_empty_container():
    """An empty container is only suspicious if it is never filled anywhere.

    `"errors": {}` is a positive statement -- that run had no failures -- and
    gold_results.json carries a non-empty one recording the StableLM crashes. So
    the rule is derived from the release rather than from a list of blessed key
    names: a key that appears populated somewhere is a register that happens to
    be empty here; a key that is empty everywhere it appears was never written.
    My first version flagged twelve `errors: {}` and would have been deleted for
    firing on correct data.
    """
    blobs = {}
    for path in _released():
        try:
            blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        if isinstance(blob, dict):
            blobs[path.name] = blob

    populated_somewhere = {
        key
        for blob in blobs.values()
        for key, value in blob.items()
        if isinstance(value, (list, dict)) and len(value) > 0
    }

    offenders = []
    for name, blob in sorted(blobs.items()):
        for key, value in blob.items():
            if not (isinstance(value, (list, dict)) and len(value) == 0):
                continue
            if key in populated_somewhere or (name, key) in KNOWN:
                continue
            offenders.append(f"{name}: {key!r} is empty in every file that has it")
    assert not offenders, (
        f"these released files carry empty containers a reader cannot tell from "
        f"withheld data: {offenders}. Either fill them, remove them from the "
        f"writer, or document them in ENVIRONMENT.md and list them here."
    )


def test_the_known_empties_are_documented():
    doc = REPRO / "ENVIRONMENT.md"
    if not doc.exists():
        pytest.skip("[repro] ENVIRONMENT.md not present")
    text = doc.read_text(encoding="utf-8", errors="replace")
    missing = sorted({key for _, key in KNOWN if key not in text})
    assert not missing, (
        f"these empty keys are exempted here but explained nowhere: {missing}"
    )


def test_the_harness_no_longer_writes_the_unused_keys():
    """The exemption covers files already produced, not new runs."""
    harness = REPRO / "patch_harness.py"
    if not harness.exists():
        pytest.skip("[repro] the patching harness is not present")
    source = harness.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source)

    written = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "report" for t in node.targets):
            continue
        if isinstance(node.value, ast.Dict):
            for key in node.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    written.add(key.value)

    reintroduced = sorted(written & {"raw", "per_layer_gap_closed"})
    assert not reintroduced, (
        f"the patching harness initialises {reintroduced} again; a future run "
        f"would ship empty containers that read as missing data"
    )


def test_the_patching_measurements_are_present():
    """Vacuity guard: the point is that the real measurements ARE released."""
    path = REPRO / "patch_results.json"
    if not path.exists():
        pytest.skip("[repro] patch results not present")
    blob = json.loads(path.read_text())
    for key in ("frac_toward_instruct", "median_recovery", "n_items_used"):
        assert blob.get(key), (
            f"patch_results.json no longer carries {key}, which is what the "
            f"causal claim is computed from"
        )
