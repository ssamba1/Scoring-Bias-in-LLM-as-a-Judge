"""Does any live file still assert the conclusion the data overturned?

There are two ways to be wrong in this repository, and only one of them was
guarded. The fabrication sweep catches invented models and invented values. It
cannot catch a real number, honestly measured on a smaller slice, presented as
the finding -- and that is what kept turning up:

  * `graphical_abstract.svg` led with "Format Bias DECREASES After instruction
    tuning" over real counts from the superseded analysis.
  * `paper/interactive/index.html` told readers the 7-family Kaggle T4 run "is
    the evidence the honest paper rests on".
  * `paper/interactive/base_vs_instruct.html` -- the one dashboard the index
    described as unaffected -- said "Instruction tuning generally reduces
    evaluation bias".
  * `repro/make_figures.py` drew Figure 1 titled "Instruction tuning reduces
    scoring bias (n=7 families)". The paper shipped the correct figure only
    because a second generator sorted later and overwrote it.

The early t4fam-only result really did point that way. The 13-family panel
reversed it, so every one of these sentences is now false, and each was written
by someone describing their evidence accurately at the time. That is why they
survived three sweeps: nothing about them looks fabricated.

Directories that exist to preserve the superseded record are exempt. Preserving
it is the point; asserting it in the live tree is the defect.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# label -> (regex, a string it must match)
#
# Narrow by design. These are assertions of the overturned direction, not any
# mention of it: a sentence explaining that the direction was overturned has to
# be able to say so.
CLAIMS = {
    "reduces scoring bias": (
        r"(?i)reduces\s+scoring\s+bias",
        "Instruction tuning reduces scoring bias ($n=7$ families)",
    ),
    "reduces evaluation bias": (
        r"(?i)reduces\s+evaluation\s+bias",
        "Instruction tuning generally reduces evaluation bias.",
    ),
    "rests on the T4 run": (
        r"(?i)which is the evidence the honest paper rests on",
        "run over six open-weight families, which is the evidence the honest paper rests on.",
    ),
    "format bias decreases": (
        r"(?i)format\s+bias\s*(?:&#8595;|↓|â)?\s*decreases",
        "Format Bias ↓ Decreases After instruction tuning",
    ),
}

# Paths whose purpose is to hold the superseded record.
EXEMPT_PREFIXES = (
    "RETRACTED/",
    "paper/honest/superseded/",
    "paper/archive/",
)
EXEMPT_FILES = {
    "DATA_INTEGRITY_AUDIT.md",
    "paper/PROVENANCE_AUDIT.md",
    ".hermes.md",
    "mutation_check.py",
    "tests/test_superseded_claims_are_not_asserted.py",
    "RETRACTED/README.md",
}

BINARY = {".png", ".pdf", ".gz", ".jpg", ".jpeg", ".ico", ".pyc", ".zip"}


def _tracked():
    listing = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, timeout=300
    )
    return listing.stdout.splitlines()


def _live_files():
    files = []
    for rel in _tracked():
        if rel.startswith(EXEMPT_PREFIXES) or rel in EXEMPT_FILES:
            continue
        path = REPO / rel
        if not path.is_file() or path.suffix.lower() in BINARY:
            continue
        files.append((rel, path))
    return files


@pytest.mark.parametrize("label", sorted(CLAIMS))
def test_superseded_claim_absent_from_live_tree(label):
    pattern = CLAIMS[label][0]
    guilty = []
    for rel, path in _live_files():
        body = path.read_text(encoding="utf-8", errors="replace")
        if re.search(pattern, body):
            guilty.append(rel)
    assert not guilty, (
        f"the superseded claim '{label}' is asserted in {guilty}. The 13-family "
        f"panel reversed this direction; it may be described as superseded but "
        f"not stated as a finding. See paper/honest/superseded/README.md."
    )


@pytest.mark.parametrize("label", sorted(CLAIMS))
def test_the_pattern_can_actually_match(label):
    """Each pattern must match the text it was written for.

    Without this the guard is one bad edit away from matching nothing and
    passing forever -- which is how a sweep reports a clean tree that is not.
    """
    pattern, sample = CLAIMS[label]
    assert re.search(pattern, sample), f"pattern for '{label}' no longer matches its own sample"


def test_the_sweep_actually_reads_files():
    """Vacuity guard: the exemptions must not swallow the whole tree."""
    files = _live_files()
    assert len(files) > 100, f"only {len(files)} live files scanned; exemptions are too broad"
