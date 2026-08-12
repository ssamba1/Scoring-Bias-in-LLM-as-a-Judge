"""Does the paper describe its own retraction in the audit's words?

The paper referred to its predecessor seven times. Four called it *fabricated*.
Three called it *unreliable* -- and those three were the abstract, the
introduction's contribution list, and the discussion. The accurate word appeared
in the reproducibility statement, an appendix, and the attention-null paragraph.

Nobody chose that. It is what happens when the visible sentences get rewritten
for flow more often than the buried ones. But the pattern reads as softening
exactly where the most readers are, in the one paper that cannot afford it: the
audit's verdict on the attention "mechanism" is FABRICATED -- a hardcoded print
statement, never computed from activations -- and on the per-domain table
FABRICATED, a split invented because the pipeline could not produce it.
"Unreliable" describes a study with a methods problem. This was not that.

The guard is one-directional on purpose: it refuses words weaker than the
audit's, and says nothing about stronger ones.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
AUDITS = (REPO / "DATA_INTEGRITY_AUDIT.md", REPO / "paper" / "PROVENANCE_AUDIT.md")

# Words that describe the predecessor as merely flawed. They are not wrong about
# it; they are weaker than what its own audit concluded.
SOFTENERS = ("unreliable", "preliminary", "flawed", "early", "imperfect", "draft")


def _sources():
    files = [HONEST / "scoring_bias_v2.tex", HONEST / "macros.tex"]
    present = [f for f in files if f.exists()]
    if not present:
        pytest.skip("[paper] no LaTeX sources present")
    return present


def test_the_audit_still_says_fabricated():
    """The guard's premise. If the audit softened, this check is arguing from nothing."""
    found = [a for a in AUDITS if a.exists()]
    if not found:
        pytest.skip("[audit] no audit document present")
    verdicts = "\n".join(a.read_text(encoding="utf-8", errors="replace") for a in found)
    assert "FABRICATED" in verdicts, (
        "no audit document records a FABRICATED verdict any more; this guard "
        "requires the paper to match a conclusion that no longer exists"
    )


@pytest.mark.parametrize("softener", SOFTENERS)
def test_the_predecessor_is_not_described_more_gently_than_the_audit(softener):
    offenders = []
    for path in _sources():
        text = " ".join(path.read_text(encoding="utf-8", errors="replace").split())
        for match in re.finditer(
            rf"\b(?:prior|earlier|previous|first|original)[,\s]+{softener}\b", text
        ):
            offenders.append(f"{path.name}: ...{text[max(0, match.start() - 60):match.end() + 40]}...")
    assert not offenders, (
        f"the paper calls its predecessor {softener!r}, which is weaker than the "
        f"audit's own verdict on it: {offenders}"
    )


def test_the_sweep_finds_the_descriptions_it_is_meant_to_check():
    """Vacuity guard: if no description matches, every check above is empty."""
    described = 0
    for path in _sources():
        text = " ".join(path.read_text(encoding="utf-8", errors="replace").split())
        described += len(re.findall(
            r"\b(?:prior|earlier|previous)[,\s]+\w+\s+version of this project", text))
    assert described >= 4, (
        f"only {described} description(s) of the predecessor found; the phrasing "
        f"has changed and this sweep is no longer reading them"
    )
