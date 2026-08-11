r"""Does the paper quote and describe its sources accurately?

A prior version of this project fabricated data. The companion project turned up
the neighbouring defect: a sentence in quotation marks, attributed to a real
paper, that did not appear in it. Neither a compiler nor a reproduction gate can
see either problem -- the citation resolves, the build is clean, and the claim
is about a document the repository does not contain.

Two classes are pinned here, both found by checking this paper against its
sources.

1. INEXACT QUOTATION. The paper quoted Li et al. (2506.22316) as "the underlying
   causes of these scoring biases remain to be validated". The sentence in their
   Limitations section reads "the underlying causes of scoring bias remain to be
   validated" -- singular, no "these". The meaning survives, which is exactly why
   it would never be noticed; a direct quotation still has to be what the source
   says. Verified against two independent renderers (arxiv.org/html and ar5iv).

2. MISCHARACTERISED DESIGN. The paper said Thakur et al. (2406.12624) "found
   base and instruct judges differ". All thirteen of their judges are
   instruction-tuned; the base/instruct split is on the *exam-taker* models whose
   answers are being judged. That distinction is load-bearing here, because a
   base-vs-instruct comparison of *judges* is this paper's own design.

Each retired sentence is named explicitly. No general "quotations must be
accurate" check is writable -- the source text is not in the repository -- so
what a guard can do is refuse to let a corrected sentence quietly return.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
SOURCES = ("scoring_bias_v2.tex", "macros.tex")

# Verified verbatim against the source, and what it replaced.
VERIFIED_QUOTATIONS = [
    (
        "li2025scoring / 2506.22316 Limitations",
        "the underlying causes of scoring bias remain to be validated",
    ),
]

RETIRED = [
    (
        "inexact quotation of Li et al.: the source says 'scoring bias', not "
        "'these scoring biases'",
        "underlying causes of these scoring biases",
    ),
    (
        "mischaracterised design: Thakur et al.'s judges are all instruction-tuned; "
        "the base/instruct split is on the exam-taker models",
        # Keyed on the claim, not the verb that introduced it. The first version
        # of this entry included "found", and a mutation that reworded the verb
        # walked straight past it -- the guard has to survive rephrasing.
        "base and instruct judges differ",
    ),
]


def _text():
    out = ""
    for name in SOURCES:
        path = HONEST / name
        if path.exists():
            out += path.read_text(encoding="utf-8", errors="replace")
    if not out:
        pytest.skip("[paper] no LaTeX sources present")
    # Quotations wrap across lines; compare on collapsed whitespace or the
    # assertion turns on where the paragraph happens to break.
    return " ".join(out.split())


def test_verified_quotations_are_still_verbatim():
    text = _text()
    missing = [f"{who}: {quote!r}" for who, quote in VERIFIED_QUOTATIONS if quote not in text]
    assert not missing, (
        "a quotation checked word-for-word against its source is no longer in the "
        f"paper as verified: {missing}. If the sentence was reworded, re-verify "
        f"against the source rather than editing this list."
    )


def test_retired_sentences_have_not_returned():
    text = _text()
    back = [f"{why} -- {frag!r}" for why, frag in RETIRED if frag in text]
    assert not back, "a corrected claim has reappeared: " + "; ".join(back)


def test_quoted_spans_are_accounted_for():
    """Any NEW externally-attributed quotation must be verified, not assumed.

    Most quoted spans in this paper are its own scare-quotes, prompt text or
    table-legend abbreviations, which need no external check. A quotation
    sitting next to a \\citet is a claim about someone else's document. If one
    appears that is not in the verified list, this fails so it gets checked
    rather than shipped.
    """
    raw = ""
    for name in SOURCES:
        path = HONEST / name
        if path.exists():
            raw += path.read_text(encoding="utf-8", errors="replace")
    flat = " ".join(raw.split())

    verified = {q for _, q in VERIFIED_QUOTATIONS}
    unverified = []
    for m in re.finditer(r"``(.+?)''", flat):
        span = m.group(1).strip().rstrip(".")
        # Short spans are single words used as scare-quotes ("better", "expert").
        if len(span.split()) < 5:
            continue
        if any(v in span or span in v for v in verified):
            continue
        # A citation within the preceding clause makes it an external attribution.
        before = flat[max(0, m.start() - 200) : m.start()]
        if re.search(r"\\cite[tp]?\*?\{", before) and "``" not in before[-60:]:
            unverified.append(span[:80])
    assert not unverified, (
        "quotation(s) attributed near a citation but not in the verified list: "
        f"{unverified}. Check each against the source text (two renderers), then "
        f"add it to VERIFIED_QUOTATIONS."
    )


def test_the_guard_reads_a_paper_that_contains_quotations():
    """Vacuity guard: every check above passes trivially on an empty read."""
    raw = " ".join(
        (HONEST / n).read_text(encoding="utf-8", errors="replace")
        for n in SOURCES
        if (HONEST / n).exists()
    )
    quoted = re.findall(r"``(.+?)''", " ".join(raw.split()))
    assert len(quoted) >= 10, f"only {len(quoted)} quoted spans found; the sweep is near-vacuous"
