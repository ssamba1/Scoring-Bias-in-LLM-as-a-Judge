r"""Does the ethics statement describe the experiments that were actually run?

An ethics section is a summary, and summaries drift toward the cleaner claim.
This one said:

    "All models are public open-weight checkpoints used under their licenses.
     Compute is a free tier at zero monetary cost (Appendix C)."

Both halves were falsified by the paper's own frontier-judge run, which queries
GPT-4o and GPT-4o-mini -- proprietary models, no public weights -- through a
commercial API. The second half contradicted the very appendix it cited, which
discloses the API spend as "under US$2 total". The appendix was right the whole
time; the summary of it was not.

Nothing could have caught this by reading the paper against itself in the usual
direction, because the claim is about the *set of models*, and that set lives in
the data. So this checks the statement against the released judge roster rather
than against a remembered phrase: whenever the frontier results contain a judge
from a vendor that publishes no weights, the ethics section has to say so.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
PAPER = HONEST / "scoring_bias_v2.tex"
FRONTIER = HONEST / "repro" / "results_closed_analysis.json"

# Vendors that serve judges by API and publish no weights. Matched against the
# judge identifiers in the released results, so adding a closed judge to the
# study forces the statement to be revisited.
CLOSED_VENDOR = re.compile(r"^(gpt-|o[13]-|chatgpt|claude|gemini|grok|command-r)", re.I)


def _paper():
    if not PAPER.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    return PAPER.read_text(encoding="utf-8", errors="replace")


def _section(title):
    """Text of one section, up to the next \\section."""
    text = _paper()
    start = text.find(title)
    if start == -1:
        pytest.skip(f"[paper] section {title!r} not found")
    nxt = text.find("\\section", start + len(title))
    return " ".join(text[start : nxt if nxt != -1 else len(text)].split())


def _frontier_judges():
    if not FRONTIER.exists():
        pytest.skip("[frontier data] results_closed_analysis.json not present")
    return list(json.loads(FRONTIER.read_text(encoding="utf-8", errors="replace"))["judges"])


def test_closed_weight_judges_are_disclosed_in_the_ethics_section():
    closed = [j for j in _frontier_judges() if CLOSED_VENDOR.match(j)]
    if not closed:
        pytest.skip("[frontier data] no closed-weight judge in the released results")
    ethics = _section("Ethics and Broader Impact")
    assert "proprietary" in ethics.lower(), (
        f"the study judges {closed}, which publish no weights, but the ethics "
        f"section does not say so"
    )
    named = [j for j in closed if j.split("-")[0].lower() in ethics.lower()]
    assert named, f"none of the closed-weight judges {closed} is named in the ethics section"


def test_the_ethics_section_does_not_claim_every_model_is_open_weight():
    ethics = _section("Ethics and Broader Impact")
    flat = ethics.lower()
    for claim in ("all models are public open-weight", "all models are open-weight"):
        assert claim not in flat, (
            f"the ethics section claims {claim!r}; the frontier-judge run uses "
            f"proprietary API models"
        )


def test_the_cost_claim_matches_the_compute_appendix():
    """A summary saying "zero monetary cost" must not contradict its own appendix."""
    compute = _section("Compute disclosure")
    spend = re.search(r"US\\\$(\d+)", compute)
    if not spend:
        pytest.skip("[paper] the compute appendix reports no monetary spend")
    ethics = _section("Ethics and Broader Impact")
    assert "US\\$" in ethics, (
        f"the compute appendix discloses spend (US${spend.group(1)}) but the ethics "
        f"section summarises compute without it -- it cites that appendix while "
        f"contradicting it"
    )


def test_the_roster_is_actually_being_read():
    """Vacuity guard: the checks above pass trivially on an empty roster."""
    judges = _frontier_judges()
    assert len(judges) >= 3, f"only {len(judges)} frontier judges parsed: {judges}"
    assert any(CLOSED_VENDOR.match(j) for j in judges), (
        f"no judge in {judges} matches the closed-vendor pattern; if the frontier "
        f"arm really is all-open now, this guard is vacuous and should be revisited"
    )
