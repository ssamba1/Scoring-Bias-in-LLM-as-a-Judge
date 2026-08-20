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
    # Probed against restatements on 2026-08-14. The originals matched only
    # "reduces", and only the two nouns the offending artefacts happened to
    # use, so "instruction tuning reduces FORMAT bias" -- nearest to the
    # retracted headline -- and "lowers"/"decreases" all passed.
    #
    # The subject is required to be the tuning, not any intervention. The paper
    # legitimately reports that a mitigation reduces bias by 59%, and a pattern
    # broad enough to catch "reduces bias" would forbid saying so.
    "reduces scoring bias": (
        r"(?i)(?:instruction[-\s]tun\w+|tuning|instruct\s+models?)[^.\n]{0,40}"
        r"(?:reduc|lower|decreas|diminish)\w*\s+(?:the\s+)?"
        r"(?:scoring|evaluation|format)\s+bias",
        "Instruction tuning reduces scoring bias ($n=7$ families)",
    ),
    "reduces evaluation bias": (
        r"(?i)(?:reduc|lower|decreas|diminish)\w*\s+(?:the\s+)?evaluation\s+bias",
        "Instruction tuning generally reduces evaluation bias.",
    ),
    "rests on the T4 run": (
        r"(?i)which is the evidence the honest paper rests on",
        "run over six open-weight families, which is the evidence the honest paper rests on.",
    ),
    # From paper_biasinteraction.md, quarantined 2026-08-13. The completed
    # bias-interaction study finds the interaction is attributable to Gemini
    # 2.5 Flash alone, with the other four judges certified additive by an
    # equivalence test. The draft asserted the inverse -- Gemini near-additive,
    # Claude and Llama compounding -- so the attribution, not just the strength,
    # was backwards.
    "gemini is near-additive": (
        r"(?i)gemini\s+(?:shows|is|remains|behaves)\s+(?:as\s+)?near[-\s]additive",
        "Gemini shows near-additive behavior",
    ),
    # From paper_rootcause.md, a three-family draft that sat in paper/ until
    # 2026-08-13 while this repository's own archive README described its era
    # as overturned. It concluded that instruct models "consistently exhibit
    # 3-12x more scoring bias" -- a multiplicative claim from ratios of small
    # deltas, against a corrected paper whose pooled increase is +0.16 with no
    # probe individually significant.
    "multiplicative bias increase": (
        r"(?i)\d+\s*(?:[-–]|\s+to\s+)\s*\d+\s*(?:x|×)\s+more\s+scoring\s+bias",
        "instruct models consistently exhibit 3-12x more scoring bias than base models",
    ),
    # From paper/rebuttals.md, the pre-retraction rebuttal document that sat
    # beside the honest one until 2026-08-13. Its answer to the base-model
    # objection was that pretrained representations carry no surface-form bias
    # and that instruction tuning introduces the capability. P16 re-scoped the
    # parse-failure confound to protocol-dependent, and base checkpoints are
    # measurably biased throughout the panel, so the claim is overturned rather
    # than merely unsupported.
    "representations are bias-free": (
        r"(?i)inherently\s+bias[-\s]free",
        "pre-trained representations are inherently bias-free with respect to surface form",
    ),
    # The score-ordering fix (score_id's letter variant is stored in token
    # order, so a total-variation distance against the ascending control was
    # taken across misaligned supports) moved five published figures. The
    # macros were corrected and the prose gate pins them -- but the
    # contributions list, the README and the rebuttal FAQ each keep their own
    # copy of the same numbers, and all three kept the superseded values
    # through four commits that described the correction as complete. The
    # gate could not see them: it pins the macro, not its paraphrases.
    # Found by reading the compiled PDF, which is the only surface that shows
    # what a referee actually reads.
    "superseded sign accuracy": (
        r"(?i)75\s*\\?%\s*(?:of\s+65\s+cells|sign\s*accuracy)",
        "75% sign accuracy over 65 cells (the corrected value is 74%)",
    ),
    "superseded SFT share": (
        r"84\s*(?:--|[-\u2013])\s*99\s*\\?%",
        "SFT installs 84-99% of the responsiveness rise (corrected: 87-94%)",
    ),
    "format bias decreases": (
        r"(?i)format\s+bias\s*(?:&#8595;|↓|â)?\s*(?:decreas|drop|fall)\w*",
        "Format Bias ↓ Decreases After instruction tuning",
    ),
}

# Paths whose purpose is to hold the superseded record.
EXEMPT_PREFIXES = (
    "RETRACTED/",
    "paper/honest/superseded/",
    "paper/archive/",
    # The early root-cause pilot, whose own README opens "Superseded pilot data
    # -- the paper of record derives nothing from this directory". It is the
    # same category as the three above and was simply never listed; the
    # widened patterns found it stating the overturned direction, which is what
    # a preserved superseded record is supposed to do.
    "results_rootcause/",
)
EXEMPT_FILES = {
    "DATA_INTEGRITY_AUDIT.md",
    "paper/PROVENANCE_AUDIT.md",
    ".hermes.md",
    "mutation_check.py",
    "tests/test_superseded_claims_are_not_asserted.py",
    "RETRACTED/README.md",
    # Quotes the false figure title in order to explain which script draws it.
    # This is the third time a guard has tripped the sweep by naming the thing it
    # guards against; the exemption is by exact path so a new file cannot inherit
    # the licence quietly.
    "tests/test_superseded_scripts_stay_in_their_lane.py",
    # Fourth time. This one sweeps every live document for the overturned
    # direction, so its pattern list necessarily spells the direction out.
    "tests/test_no_document_states_the_overturned_direction.py",
    # Fifth and sixth. Both exist to record that the Zenodo deposit the paper
    # cites still contains the superseded figures, which cannot be said without
    # naming them. The checklist is the one place a reader is told the archive
    # is stale, so exempting it is the point rather than a concession.
    "tests/test_the_archived_snapshot_claim_is_current.py",
    "paper/submission_checklist.md",
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
