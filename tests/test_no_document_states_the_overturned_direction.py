"""Does any live document still say instruction tuning makes judges more robust?

That was the earliest version's conclusion, and it was overturned twice: first by
the integrity audit, then by the 13-family GPU run, which found the opposite
sign. The paper of record says tuning makes judges sharper AND more biased.

Documents outlive the claims they were written to carry. Two artifacts asserting
the reversed direction have already been found in this repository -- a graphical
abstract announcing "Format Bias DECREASES After instruction tuning", and
`paper/video_script.md`, a narration saying "instruction tuning naturally
improves format robustness" and quoting mitigation figures (52%, 45%) that appear
in no released analysis. Both were public-facing. Neither was reachable from any
test, because they are prose.

The existing signature sweep looks for fabricated model names and invented
values. This looks for the overturned *direction*, which those artifacts state in
plain English while containing no fabricated signature at all.

The superseded material under RETRACTED/ and paper/honest/superseded/ is exempt:
recording what was claimed is the point of keeping it.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

EXEMPT_PREFIXES = ("RETRACTED/", "paper/honest/superseded/", "paper/archive/")
EXEMPT_FILES = {
    "DATA_INTEGRITY_AUDIT.md",
    "paper/PROVENANCE_AUDIT.md",
    "tests/fabricated_signatures.py",
    "tests/test_no_document_states_the_overturned_direction.py",
    "tests/test_superseded_claims_are_not_asserted.py",
    "paper/honest/PREREGISTRATION.md",  # states the hypothesis in both directions
}

# Phrasings of the overturned direction. Each is a claim, not a hypothesis: the
# preregistrations above pose both directions and are exempt by name.
# Probed against restatements on 2026-08-14. Every pattern here was
# case-sensitive, so "Instruction tuning improves robustness" -- the sentence
# with a capital at the start of it, which is how anyone would actually write
# it -- passed the whole set. That is the third pattern set in this repository
# found narrowed to the exact casing and wording of the artefact that prompted
# it. The verbs and the agent are alternated for the same reason.
REVERSED = (
    r"(?i)instruction tuning (?:naturally )?(?:improves|enhances|increases) (?:format )?robustness",
    r"(?i)tuning makes (?:the )?judges? more robust",
    r"(?i)format bias (?:decreases|declines|drops|falls) after",
    r"(?i)bias (?:is )?reduced by (?:instruction )?tuning",
    r"(?i)more robust after (?:instruction )?tuning",
)


def _documents():
    listing = subprocess.run(["git", "ls-files"], cwd=REPO,
                             capture_output=True, text=True, timeout=300).stdout
    paths = []
    for line in listing.splitlines():
        if not line.endswith((".md", ".tex", ".html", ".txt", ".svg")):
            continue
        if line.startswith(EXEMPT_PREFIXES) or line in EXEMPT_FILES:
            continue
        paths.append(line)
    if not paths:
        pytest.skip("[repo] no documents to check")
    return paths


def test_no_live_document_asserts_the_overturned_direction():
    offenders = []
    for rel in _documents():
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        flat = " ".join(text.split())
        for pattern in REVERSED:
            match = re.search(pattern, flat, re.I)
            if match:
                offenders.append(f"{rel}: ...{flat[max(0, match.start()-50):match.end()+50]}...")
                break
    assert not offenders, (
        f"these live documents state the direction the data overturned: "
        f"{offenders}. The paper of record finds tuning makes judges sharper "
        f"and MORE biased."
    )


def test_the_patterns_still_match_the_material_they_were_written_for():
    """Vacuity guard: the quarantined script is what these patterns were built from."""
    quarantined = REPO / "RETRACTED" / "outreach" / "video_script_screen_recording.md"
    if not quarantined.exists():
        pytest.skip("[retracted] the script this was written for is gone")
    flat = " ".join(quarantined.read_text(encoding="utf-8", errors="replace").split())
    assert any(re.search(p, flat, re.I) for p in REVERSED), (
        "none of the patterns matches the document they were written from, so "
        "the sweep above would pass on anything"
    )


def test_the_sweep_reads_the_documents_it_claims_to():
    documents = _documents()
    assert len(documents) >= 20, (
        f"only {len(documents)} documents swept; the listing has stopped "
        f"matching the repository"
    )
