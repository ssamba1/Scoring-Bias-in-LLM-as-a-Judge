"""Is every number in the paper explained by the released data?

The targeted sweeps in this repository each look for a shape: ranges, A -> B
transitions, rho values, p-values, sample sizes. Each caught defects of its own
shape, and each missed the inflated frontier call count -- "~4,500 single-token
logprob calls" against a harness whose design maximum is 3,000 -- because it is
a plain integer in a prose sentence and matches none of those patterns.

This check assumes no shape. It takes every numeric literal in the paper and
requires each to be explained, where explained means one of:

  * it appears in a derived result file at its own printed precision, or as a
    percentage of a stored fraction
  * it is named in check_prose.py, which pins it deliberately
  * it is listed below, with a reason

The allowlist is the honest part. A number that is genuinely not data -- a year,
a scale bound, a figure of the retracted version quoted in the retraction notice
-- has to be written down as such rather than silently skipped, so the set of
numbers nobody is checking stays visible and small.

**Precision.** This originally accepted a match at one, two *or* three decimals.
Against 6,708 stored values that is nearly free -- 0.437 rounded to 0.4 finds
something almost surely -- so the sweep could report that every number traces
while proving very little. Measured before tightening: 79 numbers reached the
data loosely and 77 of them at their own precision. The two that did not were
both the Zenodo DOI prefix, which is an identifier and is now stripped rather
than allowlisted as though it were a value.

**No mutation distinguishes the two rules, and that is worth stating rather than
faking.** A mutation would need a number that matches loosely but not strictly;
none can be built from this paper, because every decimal in it is either pinned
by name in check_prose.py or matches at full precision. The evidence for the
tightening is the 79/77 measurement above, not a harness entry. The registered
mutation on this file covers the sweep itself -- an unexplained number returning
to the paper -- which is the property that can be demonstrated.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
REPRO = HONEST / "repro"

# value -> why it is not a measurement
ALLOWED = {
    "2026": "publication year",
    "0.05": "conventional significance threshold",
    "0.15": "the preregistered equivalence margin",
    "95": "confidence level",
    "90": "confidence level for the TOST interval",
    "56000": (
        "a stated floor rather than a count -- the abstract says 'over 56,000 "
        "scored judgments' and the release holds 62,940. It equals no stored "
        "value by design; test_scale_claims_match_the_data checks the inequality."
    ),
}

# LaTeX machinery whose digits are not claims.
STRIP = (
    # A DOI is an identifier, not a measurement. Its prefix (10.5281) was the
    # only thing in the paper reaching the data by a loose match and nothing at
    # its own precision -- exactly the false confidence the tightened rule
    # removes, so it has to go rather than be allowlisted as if it were a value.
    r"10\.\d{4,}/[^\s}$,]+",
    r"\\(?:ref|label|cite[a-z]*|includegraphics|input|usepackage|newcommand|section"
    r"|subsection|documentclass|hbox|raise|scriptstyle|vspace|hspace|setlength"
    r"|tabcolsep|linewidth|textwidth|columnwidth)\{[^}]*\}",
    r"\[[^\]]*\]",
    r"\\[a-zA-Z]+",
    r"%.*",
)

NUMBER = re.compile(r"(?<![\w.])([+-]?\d+(?:\.\d+)?)(?![\w.])")


def _stored_values():
    """Every value in the derived data, plus the counts the data itself implies.

    Some of the paper's numbers are sizes rather than measurements -- 2,250
    frontier logprob calls, 13,000 model rows -- and a size is as much a fact
    about the release as a correlation is. Array lengths and their per-file
    totals are therefore counted as data too, so a size claim is explained when
    the release actually contains that many entries.
    """
    stored = set()
    per_file_totals = 0

    def walk(obj):
        if isinstance(obj, dict):
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            f = float(obj)
            for digits in (1, 2, 3):
                stored.add(round(f, digits))
                stored.add(round(abs(f), digits))
            if f and abs(f) < 1:
                stored.add(round(f * 100))
                stored.add(round(f * 100, 1))

    def count_entries(obj):
        total = 0
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "per_item" and isinstance(value, list):
                    total += len(value)
                else:
                    total += count_entries(value)
        elif isinstance(obj, list):
            for value in obj:
                total += count_entries(value)
        return total

    for path in sorted(REPRO.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        walk(payload)
        entries = count_entries(payload)
        if entries:
            stored.add(entries)
            per_file_totals += entries
    stored.add(per_file_totals)
    return stored


def _prose():
    parts = []
    for name in ("macros.tex", "scoring_bias_v2.tex"):
        path = HONEST / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    if not parts:
        pytest.skip("[paper] sources not present")
    text = "".join(parts)
    # LaTeX writes thousands as 2{,}250, which would otherwise be read as the
    # two numbers 2 and 250 -- and 250 is not in any result file, so the sweep
    # would report a defect that is a typesetting convention.
    text = text.replace("{,}", "")
    for pattern in STRIP:
        text = re.sub(pattern, " ", text)
    return text


def test_every_number_in_the_paper_is_explained():
    stored = _stored_values()
    if not stored:
        pytest.skip("[derived data] no result files to explain numbers with")
    checker = (REPRO / "check_prose.py").read_text(encoding="utf-8", errors="replace")
    text = _prose()

    unexplained = {}
    for match in NUMBER.finditer(text):
        raw = match.group(1)
        value = float(raw)
        # Small integers are counts, layer indices and scale points; they are
        # checked by the guards that know what they count.
        if value.is_integer() and abs(value) <= 30:
            continue
        bare = raw.lstrip("+-")
        if bare in ALLOWED or bare.replace(".", "").lstrip("0") in ALLOWED:
            continue
        # Match at the PAPER's own precision, not at whichever of one, two or
        # three decimals happens to land. With 6,708 stored values a loose match
        # is nearly free: rounding 0.437 to 0.4 finds something almost surely,
        # so the sweep would report "every number traces" while proving little.
        # Measured before tightening: 79 numbers passed loosely, 77 of them at
        # their own precision. A number printed to three decimals is a claim
        # about three decimals.
        decimals = len(bare.split(".")[1]) if "." in bare else 0
        if round(abs(value), decimals) in stored:
            continue
        if bare in checker:
            continue
        context = " ".join(text[max(0, match.start() - 90) : match.end() + 40].split())
        unexplained.setdefault(raw, context[-120:])

    assert not unexplained, (
        f"{len(unexplained)} number(s) in the paper are in no result file, pinned "
        f"by no check, and not on the allowlist:\n"
        + "\n".join(f"  {v}  ...{c}" for v, c in unexplained.items())
        + "\n\nEither the number is derived and should come from the data, or it "
        "is not a measurement and belongs in ALLOWED with a reason."
    )


def test_the_sweep_reads_a_real_paper():
    """Vacuity guard: over-eager stripping would leave nothing to check."""
    text = _prose()
    found = [m.group(1) for m in NUMBER.finditer(text)]
    assert len(found) >= 200, (
        f"only {len(found)} numeric literals found in the paper; the LaTeX "
        f"stripping is removing the prose along with the machinery"
    )


def test_the_allowlist_is_not_a_dumping_ground():
    """Every allowed value must still appear, and the list must stay small."""
    text = _prose() + (REPO / "README.md").read_text(encoding="utf-8", errors="replace")
    assert len(ALLOWED) <= 15, (
        f"{len(ALLOWED)} numbers are exempted from checking; the allowlist is "
        f"meant to hold the few that are genuinely not measurements"
    )
    stale = [v for v in ALLOWED if v not in text.replace(",", "").replace("{", "").replace("}", "")]
    assert not stale, (
        f"{stale} are exempted but no longer appear anywhere; remove them so the "
        f"list reflects what is actually unchecked"
    )
