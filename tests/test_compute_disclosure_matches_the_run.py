"""Does the stated API call count match the data those calls produced?

The retracted version of this project inflated exactly this kind of number:
"72,900 / 24,300 / 29,700 judgments" were multiplications of an intended design,
against a raw pilot of eight items. The audit's verdict was INFLATED AND
INCONSISTENT, and it is the easiest number in a paper to write from a plan
rather than from a run.

The honest paper states 2,250 single-token logprob calls and shows the
factorisation -- three judges, five probes, three variants, fifty items. Every
factor of that is checkable against results_closed.json, which is what those
calls produced, and none of it was checked: the count was listed as a design
size and accepted as self-explaining.

So the product is recomputed from the released cells, each factor is checked
separately -- a wrong pair of factors can multiply to the right total -- and the
cost claim is required to stay an upper bound rather than a point estimate.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"


def _paper():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    return " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())


def _frontier():
    path = REPRO / "results_closed.json"
    if not path.exists():
        pytest.skip("[repro] frontier results not present")
    return json.loads(path.read_text())["results"]


def _cells():
    """(judge, probe, variant, n_items) for every released frontier cell."""
    cells = []
    for judge, arms in _frontier().items():
        for arm in arms.values():
            if not isinstance(arm, dict):
                continue
            for probe, variants in arm.items():
                if not isinstance(variants, dict):
                    continue
                for variant, record in variants.items():
                    if isinstance(record, dict) and isinstance(record.get("per_item"), list):
                        cells.append((judge, probe, variant, len(record["per_item"])))
    if not cells:
        pytest.skip("[repro] no frontier per-item cells")
    return cells


def test_the_stated_call_count_is_the_released_call_count():
    cells = _cells()
    calls = sum(n for _, _, _, n in cells)
    stated = re.search(r"\$(\d)\{,\}(\d{3})\$\s*\\?\s*single-token logprob calls", _paper())
    assert stated, "the compute appendix no longer states a single-token call count"
    quoted = int(stated.group(1) + stated.group(2))
    assert quoted == calls, (
        f"the paper states {quoted} logprob calls; the released frontier data "
        f"holds {calls} scored items across {len(cells)} cells. This is the "
        f"number the retracted version inflated."
    )


def test_each_factor_of_the_product_is_right():
    """A wrong pair of factors can multiply to the right total."""
    cells = _cells()
    judges = {c[0] for c in cells}
    probes = {c[1] for c in cells}
    variants = {(c[1], c[2]) for c in cells}
    items = {c[3] for c in cells}

    paper = _paper()
    match = re.search(
        r"\(([a-z]+) judges \$\\times\$\s*([a-z]+) probes \$\\times\$\s*([a-z]+) "
        r"variants \$\\times\$\s*(\d+) items\)", paper)
    assert match, "the compute appendix no longer shows the factorisation"

    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    stated_judges = words.get(match.group(1))
    stated_probes = words.get(match.group(2))
    stated_variants = words.get(match.group(3))
    stated_items = int(match.group(4))

    assert stated_judges == len(judges), (
        f"the paper says {match.group(1)} judges; the data hold {sorted(judges)}"
    )
    assert stated_probes == len(probes), (
        f"the paper says {match.group(2)} probes; the data hold {sorted(probes)}"
    )
    per_probe = len(variants) / len(probes)
    assert per_probe == stated_variants, (
        f"the paper says {match.group(3)} variants per probe; the data average "
        f"{per_probe}"
    )
    assert items == {stated_items}, (
        f"the paper says {stated_items} items per cell; the data hold {sorted(items)}"
    )


def test_the_excluded_judge_is_still_excluded():
    """"plus a fourth judge that served no logprobs" -- it must not be in the data."""
    paper = _paper()
    if "fourth judge" not in paper:
        pytest.skip("[paper] the excluded judge is not mentioned")
    analysis = REPRO / "results_closed_analysis.json"
    if not analysis.exists():
        pytest.skip("[repro] frontier analysis not present")
    excluded = json.loads(analysis.read_text()).get("excluded", [])
    assert len(excluded) == 1, (
        f"the paper describes exactly one excluded judge; the analysis records "
        f"{len(excluded)}"
    )
    assert excluded[0].get("cells") == 0, (
        f"the excluded judge contributed {excluded[0].get('cells')} cells, so it "
        f"is not excluded from the numbers that were reported"
    )


def test_the_cost_is_stated_as_a_bound():
    """A point estimate of spend cannot be verified from here; a bound can."""
    paper = _paper()
    assert re.search(r"under US\\\$\d", paper), (
        "the compute appendix no longer states API spend as an upper bound; an "
        "exact figure would be unverifiable from the release"
    )
