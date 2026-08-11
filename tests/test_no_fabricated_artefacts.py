"""Nothing fabricated may live outside RETRACTED/.

This project published a paper containing invented data. A 2026-07 audit
(`DATA_INTEGRITY_AUDIT.md`) traced every numerical claim and found a fabricated
per-domain table, model names for models that do not exist, and inflated counts.
The manuscripts were retracted into `RETRACTED/`.

The retraction moved the manuscripts and the fabricated data files. It did not
move what was built from them, and 44 artefacts stayed in the live tree for two
weeks -- among them a public dashboard ranking a model that has never existed,
with precise per-probe scores. A reader browsing the repository would have taken
them for current results.

This is the guard that makes a repeat detectable. It sweeps every tracked file
outside `RETRACTED/` for the signatures the audit identified, and fails if one
reappears. It is deliberately the first test in this suite: for this repository,
"is anything fabricated still on display" outranks every other question.

The strings themselves live in `fabricated_signatures.py`, because a guard that
spells them out trips the sweep that looks for them -- which happened twice while
these tests were being written.
"""

import re
import subprocess
from pathlib import Path

import pytest

from fabricated_signatures import PATTERNS, SAMPLES, SWEEP_EXEMPT

ROOT = Path(__file__).resolve().parents[1]


def _tracked_files():
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, "git ls-files failed; is this a checkout?"
    return result.stdout.splitlines()


@pytest.fixture(scope="module")
def live_files():
    files = [
        f
        for f in _tracked_files()
        if not f.startswith("RETRACTED/") and f not in SWEEP_EXEMPT
    ]
    assert files, "no live files found -- the sweep would pass vacuously"
    return files


@pytest.mark.parametrize("label", sorted(PATTERNS))
def test_signature_absent_from_live_tree(label, live_files):
    pattern = re.compile(PATTERNS[label])
    offenders = []
    for rel in live_files:
        path = ROOT / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if pattern.search(text):
            offenders.append(rel)
    assert not offenders, (
        f"fabricated signature {label!r} is live again in {offenders}. "
        f"It belongs under RETRACTED/ with an entry in RETRACTED/README.md. "
        f"See DATA_INTEGRITY_AUDIT.md for why this content is not usable."
    )


def test_the_exemptions_still_exist():
    """An exemption for a deleted file would silently widen the sweep.

    Presence on disk, not tracking: a newly added exempt file is untracked until
    it is committed, and failing on that would make the suite unrunnable exactly
    when someone is adding a guard.
    """
    for rel in sorted(SWEEP_EXEMPT):
        assert (ROOT / rel).exists(), (
            f"{rel} is exempt from the fabrication sweep but does not exist; "
            f"remove the exemption or restore the file"
        )


def test_the_sweep_can_actually_fail():
    """A pattern that matches nothing would pass for the wrong reason."""
    assert set(SAMPLES) == set(PATTERNS), "every signature needs a sample"
    for label, sample in SAMPLES.items():
        assert re.search(PATTERNS[label], sample), (
            f"pattern for {label!r} no longer matches its own example; the sweep "
            f"is not checking what it claims to check"
        )


def test_retracted_material_is_documented():
    """Quarantine without explanation is just a move."""
    readme = ROOT / "RETRACTED" / "README.md"
    assert readme.exists(), "RETRACTED/ has no README"
    text = readme.read_text(encoding="utf-8", errors="ignore")
    assert "do not use or cite" in text.lower()
    assert "DATA_INTEGRITY_AUDIT.md" in text, "point the reader at the evidence"
    for group in ("paper/tables/", "paper/interactive/", "results_rootcause/"):
        assert group in text, (
            f"{group} was quarantined but is not described in RETRACTED/README.md"
        )
