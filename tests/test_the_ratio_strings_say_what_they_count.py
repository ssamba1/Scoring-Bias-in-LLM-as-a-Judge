"""Forty-four counts in the release are strings, and nothing parsed them.

Fields like "11/13", "4/6" and "12/20" carry a count and its denominator inside
one string. They are read by humans and by nothing else: no test splits them,
so a numerator that outgrows its denominator, a denominator that drifts from
the panel it restates, or a ratio left behind by a data change all survive.
The spec-curve entries are the load-bearing ones -- the paper's
"9--11/13 families positive" comes straight from them.

Two checks, in increasing strength.

The first is arithmetic and covers all of them: a numerator cannot exceed its
denominator, a denominator cannot be zero, and where the same object stores a
matching count the two must agree. This is cheap and catches nonsense, which is
worth having for the two dozen ratios no other test reads.

The second recomputes the twelve specification-curve ratios from the panel in
stdlib. That is the one place where the ratio is quoted in the paper, and
recomputing it is the only check that can tell a stale string from a live one:
`mean_effect` beside it is already recomputed elsewhere, but a count of
positive families is a different statistic and could drift on its own.

Three denominators deliberately do not match any sibling count, and that is
correct rather than a bug: they describe subsets -- nine families after
excluding Qwen, ten at or above 1B, twenty cells where bias fell out of
sixty-five. The check only requires agreement when a sibling count is present
with the same name, so a subset ratio is not forced to match the whole.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

RATIO = re.compile(r"^(\d+)\s*/\s*(\d+)$")

FORMAT = ["rubric_order", "score_id"]
CONTENT = ["reference_answer", "authority", "verbosity"]
PROBE_SETS = {"all": FORMAT + CONTENT, "format": FORMAT, "content": CONTENT}
CONTROL = {"rubric_order": "control", "score_id": "numeric",
           "reference_answer": "none", "authority": "none", "verbosity": "control"}


def _ratios():
    """Every "n/m" string in the release, with its path and its container."""
    found = []
    for path in sorted(REPRO.glob("results_*.json")):
        try:
            blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue

        def walk(node, trail, parent):
            if isinstance(node, dict):
                for key, value in node.items():
                    walk(value, trail + [key], node)
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, trail + [str(index)], parent)
            elif isinstance(node, str):
                match = RATIO.match(node.strip())
                if match:
                    found.append((path.name, ".".join(trail),
                                  int(match.group(1)), int(match.group(2)),
                                  parent or {}))

        walk(blob, [], None)
    return found


def test_no_ratio_counts_more_than_it_measures():
    ratios = _ratios()
    if not ratios:
        pytest.skip("[repro] no released results to scan")

    problems = []
    for source, path, numerator, denominator, _parent in ratios:
        if denominator == 0:
            problems.append(f"{source}:{path} = {numerator}/0")
        elif numerator > denominator:
            problems.append(
                f"{source}:{path} = {numerator}/{denominator}, which counts more "
                f"cases than it measured"
            )
    assert not problems, f"a released ratio is not arithmetically possible: {problems}"


def test_a_ratio_agrees_with_a_count_stored_under_the_same_name():
    """Where the object also stores the denominator as a number, they must match.

    Only when the names line up. Three ratios describe subsets (Qwen excluded,
    >=1B only, the cells where bias fell) and correctly disagree with the
    whole-panel counts beside them, so a blanket rule would be wrong.
    """
    ratios = _ratios()
    if not ratios:
        pytest.skip("[repro] no released results to scan")

    problems = []
    for source, path, numerator, denominator, parent in ratios:
        leaf = path.rsplit(".", 1)[-1]
        stem = leaf.replace("_positive", "").replace("_cells", "").replace("_families", "")
        for candidate in (f"n_{stem}", f"n_{leaf}", "n_families", "n_cells"):
            value = parent.get(candidate)
            if not isinstance(value, int) or candidate.endswith(stem) is False:
                continue
            if value != denominator:
                problems.append(
                    f"{source}:{path} = {numerator}/{denominator} beside "
                    f"{candidate}={value}"
                )
    assert not problems, f"a ratio disagrees with its own stored count: {problems}"


def _cell(record, probe, readout, metric):
    variants = record[probe]
    if readout == "ev":
        means = {name: v["mean"] for name, v in variants.items()}
    else:
        means = {name: sum(v["per_item_argmax"]) / len(v["per_item_argmax"])
                 for name, v in variants.items()}
    if metric == "maxmin":
        return max(means.values()) - min(means.values())
    control = CONTROL[probe]
    others = [abs(means[name] - means[control]) for name in means if name != control]
    return sum(others) / len(others)


def test_the_specification_curve_ratios_recompute_from_the_panel():
    """The twelve "families positive" counts the paper quotes."""
    panel_path = REPRO / "results_scaled.json"
    robustness_path = REPRO / "results_robustness.json"
    if not panel_path.exists() or not robustness_path.exists():
        pytest.skip("[repro] panel or robustness results not present")
    panel = json.loads(panel_path.read_text(encoding="utf-8", errors="replace"))["results"]
    specs = json.loads(robustness_path.read_text(encoding="utf-8", errors="replace")) \
        .get("F3_specification_curve", {}).get("specs")
    if not specs:
        pytest.skip("[repro] specification curve absent")

    families = sorted(panel)
    problems = []
    for name, record in specs.items():
        readout, metric, probe_set = name.split("|")
        positive = 0
        counted = 0
        for family in families:
            arms = {}
            for arm in ("base", "instruct"):
                cells = [_cell(panel[family][arm], probe, readout, metric)
                         for probe in PROBE_SETS[probe_set]]
                arms[arm] = sum(cells) / len(cells)
            counted += 1
            positive += (arms["instruct"] - arms["base"]) > 0
        shown = record.get("families_positive")
        expected = f"{positive}/{counted}"
        if shown != expected:
            problems.append(f"{name}: release says {shown}, the panel gives {expected}")
    assert not problems, (
        f"the specification curve's family counts do not recompute: {problems}. "
        f"These are the numbers the paper quotes as '9--11/13 families positive'."
    )
