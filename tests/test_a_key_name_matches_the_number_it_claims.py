"""A key whose name states a parameter must have been computed with it.

Three keys in the release encode a threshold in their own name:

    all_cells_gt_0p1      every chat-template cell exceeds 0.1
    probes_delta_gt_0.1   how many probes exceed 0.1
    within_pm_0p15        the TOST interval falls inside +/- 0.15

The name is a claim about how the value was produced, and nothing checked it.
Change 0.1 to 0.2 in the comparison and the key keeps asserting 0.1; the JSON
stays internally consistent, every existing test passes, and a reader
recomputing from the stated threshold gets a different answer than the release.
This repository has the same defect class on record from the other direction --
a model named in the paper asserting a version its recorded route does not pin.

The check is deliberately not a hand-written list of the three. Such a list
goes stale exactly when someone adds a fourth key, which is the moment it
matters. Instead every released key is scanned for an embedded number, and each
one found must appear as a literal on the line of the analysis that assigns it.
A key nobody assigns fails too: a parameter-bearing name with no computation
behind it is a hand-written assertion sitting in a results file.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# "gt_0p1", "pm_0p15", "gt_0.1" -- a comparison word is optional, the number is not.
KEY_PARAMETER = re.compile(r"(?:^|_)(?:pm_|gt_|lt_|ge_|le_)?(\d+p\d+|0\.\d+)(?:$|_)")
LITERAL = re.compile(r"\d+\.\d+")


def _as_float(token):
    return float(token.replace("p", ".")) if "p" in token else float(token)


def _parameter_bearing_keys():
    """Every released key whose name embeds a numeric parameter."""
    found = {}
    for path in sorted(REPRO.glob("results_*.json")):
        try:
            blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        stack = [blob]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if isinstance(key, str):
                        match = KEY_PARAMETER.search(key)
                        if match:
                            found.setdefault(key, (_as_float(match.group(1)), set()))
                            found[key][1].add(path.name)
                    stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)
    return found


def _assigning_lines(key):
    """Lines in the analyses that assign this key, with their numeric literals."""
    out = []
    for source in sorted(REPRO.glob("*.py")):
        try:
            text = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if f'"{key}"' in line and ":" in line:
                out.append((source.name, number, {float(x) for x in LITERAL.findall(line)}))
    return out


def test_every_parameter_in_a_key_name_is_the_one_that_was_used():
    keys = _parameter_bearing_keys()
    if not keys:
        pytest.skip("[repro] no released results to scan")

    problems = []
    for key, (parameter, files) in sorted(keys.items()):
        assignments = _assigning_lines(key)
        if not assignments:
            problems.append(
                f"{key} (in {sorted(files)}) names the parameter {parameter} but "
                f"no analysis assigns it -- the name is asserting a computation "
                f"that is not in the repository"
            )
            continue
        for source, line, literals in assignments:
            if parameter not in literals:
                problems.append(
                    f"{key} names {parameter}, but {source}:{line} computes it "
                    f"with {sorted(literals) or 'no literal threshold'}. The key "
                    f"is telling a reader which threshold produced the value and "
                    f"it is not that one."
                )
    assert not problems, f"a key name disagrees with its own computation: {problems}"


def test_the_scan_finds_the_keys_it_is_meant_to_cover():
    """Guard the guard: a regex that stops matching would pass everything.

    These three are in the release today. If one is renamed the assertion
    should be updated deliberately, which is the point -- silently matching
    nothing is how this kind of sweep dies.
    """
    keys = _parameter_bearing_keys()
    if not keys:
        pytest.skip("[repro] no released results to scan")
    expected = {"all_cells_gt_0p1", "probes_delta_gt_0.1", "within_pm_0p15"}
    missing = sorted(expected - set(keys))
    assert not missing, (
        f"{missing} no longer match the parameter-bearing key pattern. Either "
        f"they were renamed, or the pattern stopped working and this sweep is "
        f"now checking nothing."
    )


def test_the_tost_verdict_follows_from_the_interval_it_names():
    """within_pm_0p15 is recomputable from the interval stored beside it."""
    path = REPRO / "results_robustness.json"
    if not path.exists():
        pytest.skip("[repro] results_robustness.json not present")
    blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    record = blob.get("H3_anchoring_equivalence")
    if not record or "within_pm_0p15" not in record:
        pytest.skip("[repro] equivalence record absent")

    margin = _as_float(KEY_PARAMETER.search("within_pm_0p15").group(1))
    low, high = record["ci90"]
    expected = low > -margin and high < margin
    assert record["within_pm_0p15"] == expected, (
        f"the interval [{low}, {high}] falls inside +/-{margin}: {expected}, "
        f"but the flag says {record['within_pm_0p15']}"
    )
