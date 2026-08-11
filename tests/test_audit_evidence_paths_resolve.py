"""Do the audit documents' file references still point at the evidence?

DATA_INTEGRITY_AUDIT.md and PROVENANCE_AUDIT.md are how a sceptical reader
checks the fabrication findings: each claim names the file it was established
from. That only works while the paths resolve.

Two had gone stale. The audit cited `results_rootcause/study1_results.json` and
`results_rootcause/full_metrics.json`, and both had since been quarantined into
`RETRACTED/data/`. The findings were unaffected -- the files still exist and
still say what the audit reports -- but the trail from claim to evidence was
broken, and a reader following it would conclude the evidence was gone. For a
document whose entire purpose is to be checkable, that is the failure mode that
matters.

Only repo-relative paths are checked. Bare filenames are mentioned throughout as
names rather than locations, and a document is allowed to say "study1_results.json"
without promising a file sits at the repository root.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

DOCS = [
    "DATA_INTEGRITY_AUDIT.md",
    "paper/PROVENANCE_AUDIT.md",
    "RETRACTED/README.md",
]

# A backticked token that names a directory as well as a file: it is a location,
# not just a name, so it is a promise the reader can follow.
PATH_IN_TICKS = re.compile(
    r"`([\w.-]+(?:/[\w.-]+)+\.(?:py|json|tex|md|yml|yaml|sh|cff|txt|bib|html|gz))`"
)


def _docs():
    present = [(d, REPO / d) for d in DOCS if (REPO / d).exists()]
    if not present:
        pytest.skip("[audit docs] none present")
    return present


def _resolves(doc, cited):
    """A citation may be repo-relative or relative to the document itself.

    RETRACTED/README.md describes its own contents, so it writes `paper/...`
    meaning RETRACTED/paper/..., and `../DATA_INTEGRITY_AUDIT.md` for the file a
    level up. Both readings are what a reader would try.
    """
    here = (REPO / doc).parent
    for candidate in ((REPO / cited), (here / cited)):
        try:
            if candidate.resolve().exists():
                return True
        except OSError:
            continue
    return False


@pytest.mark.parametrize("doc", [d for d, _ in _docs()])
def test_every_cited_path_exists(doc):
    text = (REPO / doc).read_text(encoding="utf-8", errors="replace")
    cited = sorted({m.group(1) for m in PATH_IN_TICKS.finditer(text)})
    missing = [p for p in cited if not _resolves(doc, p)]
    assert not missing, (
        f"{doc} cites {len(missing)} path(s) that no longer exist: {missing}. "
        f"If the material moved, update the reference -- the audit is only "
        f"usable while a reader can follow it to the evidence."
    )


def test_the_documents_cite_something():
    """Vacuity guard: a reformat that drops the backticks would empty this.

    Checked over the corpus rather than per document. PROVENANCE_AUDIT.md refers
    to its sources by bare filename -- `study1_results.json` rather than a
    location -- which is a legitimate style and would fail a per-document floor
    for a reason that is not a defect.
    """
    total = set()
    for doc, path in _docs():
        text = path.read_text(encoding="utf-8", errors="replace")
        total |= {m.group(1) for m in PATH_IN_TICKS.finditer(text)}
    assert len(total) >= 8, (
        f"the audit documents cite only {len(total)} locations between them; the "
        f"check above is passing because it has almost nothing to check"
    )
