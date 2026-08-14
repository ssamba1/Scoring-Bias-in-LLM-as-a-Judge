"""Is every failure a run recorded also disclosed to a reader?

The harnesses write an `errors` block. Two released runs have a non-empty one:
the ground-truth run lost both StableLM-2-1.6B checkpoints to a config quirk,
and the frontier run lost qwen-2.5-72b-instruct to a provider 404. The second
was disclosed -- it sits under `excluded` in the analysis with its reason, and
the paper discusses which frontier judges could be reached. The first was
recorded in the raw file and nowhere else.

That matters more than the missing model does. `gold_results.json` still holds a
`StableLM-2-1.6B` entry carrying only `params_b`, so anyone counting models in
that file gets six while five have data. Nothing in the paper claims six -- the
ground-truth section quotes accuracies and margins rather than a family count --
so no stated number is wrong. What was wrong is that a run failure sat in a data
file with no path to the reader, in a project whose whole premise is that the
data and the prose agree.

Two properties are checked here. A recorded failure must name its subject in
ENVIRONMENT.md, and a model that appears in a released run with no condition
data must be named there too. The second catches the shell entry directly: a
model can vanish from an analysis without ever appearing in an errors block, if
the harness simply never reached it.
"""

import gzip
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
ENVIRONMENT = REPRO / "ENVIRONMENT.md"

# Keys that describe a model rather than a measurement of it.
METADATA = {"params_b", "training", "stage", "stage_order", "family", "_meta"}


def _disclosure():
    if not ENVIRONMENT.exists():
        pytest.skip("[repro] ENVIRONMENT.md not present")
    return ENVIRONMENT.read_text(encoding="utf-8", errors="replace")


def _released_runs():
    runs = []
    for path in sorted(REPRO.glob("*.json")) + sorted(REPRO.glob("*.json.gz")):
        if path.name.endswith("_analysis.json"):
            continue
        try:
            if path.suffix == ".gz":
                with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
                    blob = json.load(fh)
            else:
                blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(blob, dict):
            runs.append((path.name, blob))
    if not runs:
        pytest.skip("[repro] no released runs")
    return runs


def _short(subject):
    """The distinctive part of a model id, e.g. stablelm-2-1_6b -> stablelm."""
    tail = subject.rsplit("/", 1)[-1].lower()
    return re.split(r"[-_.]", tail)[0]


def test_every_recorded_failure_is_disclosed():
    disclosure = _disclosure().lower()
    undisclosed = []
    for name, blob in _released_runs():
        errors = blob.get("errors")
        if not isinstance(errors, dict) or not errors:
            continue
        for subject in errors:
            if _short(subject) not in disclosure:
                undisclosed.append(f"{name}: {subject}")
    assert not undisclosed, (
        f"{undisclosed} failed during a released run and are named nowhere in "
        f"ENVIRONMENT.md. A failure recorded only in the data file has no path "
        f"to a reader."
    )


def test_no_model_is_an_empty_shell():
    """An entry with metadata and no measurements inflates an apparent panel."""
    disclosure = _disclosure().lower()
    shells = []
    for name, blob in _released_runs():
        results = blob.get("results")
        if not isinstance(results, dict):
            continue
        for model, record in results.items():
            if not isinstance(record, dict):
                continue
            measured = [k for k in record if k not in METADATA]
            if measured:
                continue
            if _short(model) not in disclosure:
                shells.append(f"{name}: {model}")
    assert not shells, (
        f"{shells} appear in a released run carrying only metadata, so counting "
        f"models in that file overstates the panel, and ENVIRONMENT.md does not "
        f"say so."
    )


def test_the_disclosure_names_the_ground_truth_loss():
    """The specific one this test was written for."""
    disclosure = _disclosure()
    assert "gold_results.json" in disclosure, (
        "ENVIRONMENT.md no longer names gold_results.json among the runs that "
        "recorded a failure"
    )
    assert "pad_token_id" in disclosure, (
        "the ground-truth run's failure is disclosed without its cause; the "
        "cause is what tells a reader it was a config quirk rather than a "
        "model that scored badly and was dropped"
    )
