"""The reproduction gate's allowlist must not accept more than it documents.

`verify_like_ci.py` reruns every analysis and compares the result to what is
committed. A handful of values genuinely differ between Linux and Windows in
the fourth decimal, so the gate carries an allowlist read from
`repro/ENVIRONMENT.md`. An allowlist on a reproduction check is the one place
where being slightly too generous costs the whole guarantee: whatever it
accepts, nobody ever sees.

It used to be built by scraping every number in the document, which accepted
two things it should not.

**Any file.** A value was accepted wherever it appeared, so a real regression
in one file passed as long as some unrelated file was documented as differing
by that amount. The table records which file each value belongs to; matching
without it discards the only thing that made the entry specific.

**Differences the document says are fixed.** ENVIRONMENT.md discusses, in the
past tense, a divergence in `results_stages_analysis.json` -- 0.839 on Linux
against 0.840 on Windows, and an SFT share that is now 0.871 on both. Those
numbers are still in the prose, so scraping them re-armed exactly the
divergence the document says no longer exists. A regression back to it would
have been reported as documented.

The gate now reads the table and matches on (file, value). These tests hold it
there, because the loose version passed every check in this repository for as
long as it existed.
"""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "verify_like_ci.py"
ENVDOC = REPO / "paper" / "honest" / "repro" / "ENVIRONMENT.md"


def _gate():
    if not GATE.exists():
        pytest.skip("[gate] verify_like_ci.py not present")
    spec = importlib.util.spec_from_file_location("_gate_under_test", GATE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_gate_under_test"] = module
    spec.loader.exec_module(module)
    return module


def test_the_allowlist_records_which_file_each_value_belongs_to():
    entries = _gate().documented_platform_differences()
    assert entries, (
        "the allowlist is empty, so every reproduction difference would be "
        "reported as undocumented -- or ENVIRONMENT.md's table stopped parsing"
    )
    bare = [e for e in entries if not (isinstance(e, tuple) and len(e) == 2)]
    assert not bare, (
        f"{bare[:4]} are not (file, value) pairs. A bare number accepts a "
        f"difference in any file, which is how a regression in one file passes "
        f"because an unrelated file is documented as differing by that amount."
    )
    for name, value in entries:
        assert isinstance(name, str) and name.endswith(".json"), (
            f"{name!r} is not a results file name"
        )
        assert isinstance(value, float), f"{value!r} is not a number"


def test_every_allowlisted_file_exists():
    """An entry naming a file nobody ships can never be exercised."""
    entries = _gate().documented_platform_differences()
    repro = REPO / "paper" / "honest" / "repro"
    missing = sorted({name for name, _v in entries if not (repro / name).exists()})
    assert not missing, (
        f"{missing} are allowlisted as differing between platforms but are not "
        f"in repro/. The entry cannot match anything, so it documents nothing."
    )


def test_differences_the_document_calls_fixed_are_not_allowlisted():
    """Prose describing a resolved divergence must not re-arm it.

    The document explains that correcting the score-ordering bug moved the
    responsiveness values off the rounding boundary they had been sitting on,
    and that the gate now regenerates the stage file identically on both
    platforms. The numbers from that resolved case are still written down, as
    they should be -- it is the history. They must not be accepted as live.
    """
    if not ENVDOC.exists():
        pytest.skip("[gate] ENVIRONMENT.md not present")
    # Collapse the wrapping: the document is hard-wrapped, so the phrase this
    # looks for is split across a newline in the file. Searching the raw text
    # made this test skip, which is the same as not having written it.
    doc = " ".join(ENVDOC.read_text(encoding="utf-8", errors="replace").split())
    assert "used to include" in doc, (
        "ENVIRONMENT.md no longer describes the resolved divergence this test "
        "checks is not re-armed. If that passage was deliberately removed, "
        "remove this test with it rather than letting it skip."
    )

    entries = _gate().documented_platform_differences()
    allowed_values = {value for _name, value in entries}
    allowed_files = {name for name, _v in entries}

    # The paragraph that describes the resolved case, and the numbers in it.
    start = doc.index("used to include")
    passage = doc[max(0, start - 200):start + 600]
    resolved = {float(v) for v in re.findall(r"\b\d\.\d{3,4}\b", passage)}
    resolved_files = set(re.findall(r"`(results_[a-z0-9_]+\.json)`", passage))

    leaked = sorted(v for v in resolved if v in allowed_values)
    assert not leaked, (
        f"{leaked} come from a divergence ENVIRONMENT.md describes in the past "
        f"tense, but the allowlist still accepts them. A regression back to "
        f"exactly the difference the document says was fixed would be reported "
        f"as documented."
    )
    still_live = sorted(f for f in resolved_files if f in allowed_files)
    assert not still_live, (
        f"{still_live} is described as reproducing identically on both "
        f"platforms and is also allowlisted as differing. One of the two is "
        f"wrong, and the allowlist is the half that silently wins."
    )
