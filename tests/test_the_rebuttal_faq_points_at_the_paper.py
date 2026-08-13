"""Does the reviewer-facing FAQ still describe the paper it answers for?

REBUTTAL_FAQ.md is the document prepared for submission and defense: an
anticipated objection, then where the paper answers it. Every other artifact
here is checked against the data -- check_prose pins the paper's numbers,
test_every_number_is_accounted_for sweeps the ones it misses -- and this file
was checked by nothing at all, which is how it accumulated three kinds of drift
at once.

*Section numbers.* Nine of its cross-references pointed at the wrong section.
They were right when written and were never renumbered as sections were added,
so the predictor claim cited the attention section, the public-item replication
cited dose--response, and the stage ablation cited the five-bias-types section.
Every one still resolved to a real heading, so nothing looked broken; a reviewer
following the pointer would simply have landed somewhere else.

*A stale count.* It said ten of sixteen predictions were preregistered where the
paper says twenty were.

*An overstated claim.* It answered "Only 3/5 probes individually significant"
with "stated verbatim in 5.1". The paper states the opposite: the registered
per-probe test is null for *every* probe, and three of five bootstrap intervals
excluding zero is not the same property. That is the failure mode this project
was retracted for -- a document claiming more support than the analysis gives --
in the one artifact written to be read adversarially.

So each reference is pinned to the *title* of the section it must point at,
resolved from the paper's own heading order. A renumbering now fails here
instead of silently redirecting the reader.

This does not check that the FAQ's numbers are right. Membership in the paper's
text is too weak to assert: the FAQ's partial correlation of -0.38 matches the
paper's score-ID bias of +0.38 by coincidence, and a check that accepts that
would read as stronger than it is. The numbers were verified by hand against
the release when this was written; what is mechanised is the pointing.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
FAQ = HONEST / "REBUTTAL_FAQ.md"
PAPER = HONEST / "scoring_bias_v2.tex"

# Every section number the FAQ cites, and the heading it has to land on.
EXPECTED = {
    "3.2": "Expected-value scoring",
    "3.3": "Statistics",
    "5.1": "Instruction tuning increases scoring bias",
    "5.2": "Robustness of the headline",
    "5.3": "Mechanism: sharper, but more biased",
    "5.4": "The decomposition predicts cell-by-cell",
    "5.5": "Causal test: patching localizes the fix",
    "5.6": "Where responsiveness comes from",
    "5.10": "Dose--response: a preregistered failure",
    "5.12": "Bias is predictable from decisiveness",
    "5.15": "Robustness to prompt template",
    "5.16": "Which alignment stage installs the bias?",
    "5.17": "Replication on public-dataset items",
    "5.22": "Frontier judges",
    "7": "Limitations",
}


def _headings():
    """Section number -> title, numbered the way LaTeX numbers them."""
    if not PAPER.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    if r"\begin{document}" not in text:
        pytest.skip("[paper] no document body")
    body = text.split(r"\begin{document}", 1)[1].split(r"\appendix", 1)[0]

    numbers = {}
    section = subsection = 0
    for match in re.finditer(r"\\(section|subsection)\*?\{([^}]*)\}", body):
        if match.group(1) == "section":
            section += 1
            subsection = 0
            numbers[str(section)] = match.group(2)
        else:
            subsection += 1
            numbers[f"{section}.{subsection}"] = match.group(2)
    return numbers


def _faq():
    if not FAQ.exists():
        pytest.skip("[paper] REBUTTAL_FAQ.md not present")
    return FAQ.read_text(encoding="utf-8", errors="replace")


def _cited():
    """Every section the FAQ points at, including both ends of a range.

    "§5.3--5.4" cites two sections and only the first carries the marker, so a
    pattern anchored on § alone silently drops the second -- the same shape of
    miss as a detector that matches one spelling of a key.
    """
    faq = _faq()
    refs = set()
    for match in re.finditer(
        r"§\s*([0-9]+(?:\.[0-9]+)?)(?:\s*[-–—]+\s*([0-9]+(?:\.[0-9]+)?))?", faq
    ):
        refs.add(match.group(1))
        if match.group(2):
            refs.add(match.group(2))
    return sorted(refs, key=lambda s: [int(part) for part in s.split(".")])


def test_every_cited_section_lands_on_the_expected_one():
    numbers = _headings()
    wrong = []
    for ref in _cited():
        if ref not in EXPECTED:
            continue
        title = numbers.get(ref)
        if title is None:
            wrong.append(f"§{ref} does not exist in the paper")
        elif not title.startswith(EXPECTED[ref]):
            wrong.append(f"§{ref} is {title!r}, expected {EXPECTED[ref]!r}")
    assert not wrong, (
        f"the FAQ points reviewers at the wrong section(s): {wrong}. The paper "
        f"was renumbered; update the reference to the section that now holds "
        f"the claim, not the expectation."
    )


def test_no_reference_is_undeclared():
    """A new pointer has to say where it means to land."""
    undeclared = sorted(set(_cited()) - set(EXPECTED))
    assert not undeclared, (
        f"the FAQ cites {undeclared} with no expected heading recorded, so a "
        f"renumbering would move them silently; add each to EXPECTED"
    )


def test_no_expectation_is_stale():
    cited = set(_cited())
    unused = sorted(set(EXPECTED) - cited)
    assert not unused, (
        f"EXPECTED pins {unused}, which the FAQ no longer cites; an expectation "
        f"guarding nothing hides the next one"
    )


def test_the_prediction_count_matches_the_paper():
    faq = _faq()
    paper = PAPER.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"preregistered (\w+) predictions", paper)
    if not match:
        pytest.skip("[paper] states no prediction count")
    count = match.group(1)
    assert re.search(rf"\b{count.capitalize()}|\b{count}\b", faq), (
        f"the paper says it preregistered {count} predictions; the FAQ does not "
        f"say so, and a reviewer reading both sees two different projects"
    )


def test_the_faq_does_not_claim_a_probe_is_individually_significant():
    """The registered per-probe test is null for every probe."""
    faq = _faq()
    overstated = re.search(
        r"([0-9]+\s*/\s*5|three|Three)\s+(of\s+(the\s+)?five\s+)?probes?[^.\n]{0,40}"
        r"individually significant",
        faq,
    )
    assert not overstated, (
        f"the FAQ says {overstated.group(0)!r}; the registered per-probe test "
        f"(paired Wilcoxon, Holm-corrected) is null for every probe, and "
        f"bootstrap intervals excluding zero are a different and weaker property"
    )
    assert "null for *every* probe" in faq or "null for every probe" in faq, (
        "the FAQ no longer states that the registered per-probe test is null "
        "for every probe, which is the honest answer to the objection it raises"
    )
