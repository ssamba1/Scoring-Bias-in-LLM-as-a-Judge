"""Does the submission checklist describe the paper that exists?

The previous version of `paper/submission_checklist.md` described the retracted
paper: 20 figures, 10 tables, 286 references, "All results data in repository
(47 models, 41 complete)", and six quantified limitations. The corrected paper
has 10 figures, 5 tables, 28 references, 13 families, and 16 limitation items.
Every box was ticked, including "All author information complete" against a
CITATION.cff with no ORCID, and "DOI archived at Zenodo" for a deposit that
predates the correction.

A checklist is a claim about readiness, and a ticked box nobody re-derives is
the same failure shape as a reported number nobody recomputes -- with the extra
property that it is read by whoever is deciding whether to submit.

So the counts are recomputed from the paper here, and the boxes that depend on
an action only the author can take must stay unticked. That second rule is the
one that matters: the way this file went wrong was not arithmetic, it was
ticking things that were never done.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
PAPER = HONEST / "scoring_bias_v2.tex"
CHECKLIST = REPO / "paper" / "submission_checklist.md"

# Actions that are the author's own. Each must appear as an unticked box.
AUTHOR_ONLY = (
    "ORCID",
    "Zenodo DOI",
    "Withdraw or replace the on-hold submission",
    "arXiv identifier",
    "green run on GitHub's own runners",
)


def _checklist():
    if not CHECKLIST.exists():
        pytest.skip("[paper] submission_checklist.md not present")
    return CHECKLIST.read_text(encoding="utf-8", errors="replace")


def _paper():
    if not PAPER.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    return PAPER.read_text(encoding="utf-8", errors="replace")


def _stated(pattern):
    """The number the checklist states for a claim, or None."""
    match = re.search(pattern, _checklist())
    return int(match.group(1)) if match else None


def test_the_figure_and_table_counts_recompute():
    paper = _paper()
    figures = len(re.findall(r"\\includegraphics", paper))
    tables = len(re.findall(r"\\begin\{table", paper))

    stated_figures = _stated(r"Results:\s*(\d+)\s*figures")
    stated_tables = _stated(r"figures and\s*(\d+)\s*tables")
    if stated_figures is None or stated_tables is None:
        raise AssertionError(
            "the checklist no longer states a figure and table count; the "
            "retracted version's counts were wrong precisely because nothing "
            "recomputed them"
        )
    assert stated_figures == figures, (
        f"the checklist claims {stated_figures} figures; the paper includes "
        f"{figures}"
    )
    assert stated_tables == tables, (
        f"the checklist claims {stated_tables} tables; the paper has {tables} "
        f"table environments"
    )


def test_the_limitation_count_recomputes():
    paper = _paper()
    section = re.search(
        r"\\section\{Limitations\}(.*?)\\section\{", paper, re.S
    )
    if not section:
        pytest.skip("[paper] no Limitations section")
    items = len(re.findall(r"\\item", section.group(1)))
    stated = _stated(r"Limitations:\s*(\d+)\s*items")
    assert stated == items, (
        f"the checklist claims {stated} limitation items; §Limitations holds "
        f"{items}"
    )


def test_the_reference_count_recomputes():
    bib = HONEST / "honest.bib"
    if not bib.exists():
        pytest.skip("[paper] honest.bib not present")
    entries = len(re.findall(r"^@", bib.read_text(encoding="utf-8", errors="replace"), re.M))
    stated = _stated(r"References:\s*(\d+)\s*entries")
    assert stated == entries, (
        f"the checklist claims {stated} references; honest.bib holds {entries}"
    )


@pytest.mark.parametrize("action", AUTHOR_ONLY)
def test_author_only_actions_are_not_ticked(action):
    text = _checklist()
    line = next((ln for ln in text.splitlines() if action in ln), None)
    assert line is not None, (
        f"the checklist no longer mentions {action!r}; an action nobody can "
        f"take on the author's behalf has to stay visible, not disappear"
    )
    assert not line.lstrip().startswith("- [x]"), (
        f"{action!r} is ticked: {line.strip()!r}. Nobody working in this "
        f"repository can complete it, so a tick here can only be wrong."
    )


def test_the_checklist_does_not_describe_the_retracted_paper():
    """The counts that identified the old checklist, as a backstop.

    Only the checklist items are read. The header quotes the retracted counts
    in order to say they were wrong, and a sweep over the whole file would
    trip on that -- the same self-reference that has caught guards in this
    repository before. A ticked box is an assertion; a sentence explaining
    what the old file claimed is not.
    """
    text = "\n".join(
        line for line in _checklist().splitlines() if line.lstrip().startswith("- [")
    )
    retracted = {
        "47 models": r"47\s+models",
        "286 references": r"286\s+entries|\(286",
        "20 figures": r"all\s+20\s+figures",
    }
    found = [label for label, pattern in retracted.items()
             if re.search(pattern, text, re.I)]
    assert not found, (
        f"the checklist states {found}, which described the retracted paper "
        f"and not this one"
    )
