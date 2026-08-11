r"""Pin the derived values that sit on a rounding tie to CI's output.

The committed derived JSON is a build output, and the reproduction gate
regenerates it in CI and fails on any difference. Four entries of
responsiveness_link_points land within a whisker of a rounding tie: `round(x, 4)`
where x is just either side of ...5 in the fifth decimal. Which way it rounds
depends on the last bits of x, so it differs between environments. CI computes
0.6995 where this machine computes 0.6996.

The obvious explanation was package drift -- scipy 1.18.0 against a 1.17.1 pin.
It was wrong, and worth recording as wrong: installing the pinned stack exactly
(numpy 2.4.4, scipy 1.17.1, statsmodels 0.14.6, pandas 3.0.3) still produces
0.6996 here. The difference lives below the package layer -- OS, Python build,
or the BLAS numpy links against -- and no requirements file can pin that.

It cost five consecutive red CI runs, all on commits whose actual content was
fine. The paper is unaffected: these four numbers feed a figure, and the figure
is compared by drawn content, not by these values.

Two designs were tried and rejected before this one. "Fail if this environment
differs from CI" is red on every maintainer machine forever, which is how a gate
stops being read. "Fail if a derived file is modified outside CI" blocks the
ordinary workflow of changing an analysis and regenerating. What is left is
narrow and correct: pin the known-fragile values to what CI produces, so a local
regeneration that flips them fails here instead of three commits later in CI.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MECH = REPRO / "results_mechanism.json"
PINS = REPRO / "requirements-repro.txt"

# Values known to differ between environments, with what CI produces for each.
#
# The first four came from the reproduction gate's own diff after it went red.
# The rest were found before CI saw them, by regenerating every analysis into a
# scratch copy under the pinned stack and diffing against the committed files:
# they are correct in the repository right now, and are recorded here so that a
# local regeneration which flips them fails immediately rather than three
# commits later.
#
# (file, dotted path, value CI produces)
CI_VALUES = [
    ("results_mechanism.json", "responsiveness_link_points.resp[6]", 0.6995),
    ("results_mechanism.json", "responsiveness_link_points.resp[18]", 0.1083),
    ("results_mechanism.json", "responsiveness_link_points.resp[91]", 0.3871),
    ("results_mechanism.json", "responsiveness_link_points.resp[92]", 0.2231),
    ("results_stages_analysis.json", "per_cell[16].resp", 0.4863),
    ("results_stages_analysis.json", "trajectories.OLMo-2-1B.RLVR.resp", 0.1967),
    ("results_stages_analysis.json", "P8_paths.OLMo-2-1B.resp_path[3]", 0.1967),
    ("results_stages_analysis.json", "P7.sft_share_of_total_rise[0]", 0.839),
]

NUMERIC = ("numpy", "scipy", "statsmodels", "pandas")


def _resolve(data, dotted):
    """Follow a path like 'a.b[3].c' through parsed JSON."""
    node = data
    for part in dotted.split("."):
        m = re.match(r"([^\[]*)((?:\[\d+\])*)$", part)
        key, indices = m.group(1), re.findall(r"\[(\d+)\]", m.group(2))
        if key:
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        for i in indices:
            if not isinstance(node, list) or int(i) >= len(node):
                return None
            node = node[int(i)]
    return node


def _resp():
    if not MECH.exists():
        pytest.skip("[derived data] results_mechanism.json not present")
    data = json.loads(MECH.read_text(encoding="utf-8", errors="replace"))
    points = data.get("responsiveness_link_points", {}).get("resp")
    if not points:
        pytest.skip("[derived data] responsiveness_link_points absent")
    return points


def test_tie_prone_values_match_what_ci_produces():
    wrong, unchecked = [], []
    for filename, dotted, expected in CI_VALUES:
        path = REPRO / filename
        if not path.exists():
            unchecked.append(f"{filename} absent")
            continue
        got = _resolve(json.loads(path.read_text(encoding="utf-8", errors="replace")), dotted)
        if got is None:
            unchecked.append(f"{filename}:{dotted} no longer resolves")
        elif got != expected:
            wrong.append(f"{filename}:{dotted} = {got}, CI produces {expected}")
    assert not wrong, (
        "committed values differ from what the reproduction gate computes: "
        + "; ".join(wrong)
        + ". These sit on a rounding tie and flip between environments, so a local "
        "regeneration has overwritten CI's values. Restore them before committing, "
        "or the gate goes red on every later commit."
    )
    assert not unchecked, (
        "pinned path(s) no longer resolve, so they are silently unchecked: "
        + "; ".join(unchecked)
    )


def test_the_pinned_indices_still_point_at_the_same_quantity():
    """Vacuity guard: if the array is rebuilt, fixed indices stop meaning anything.

    A shorter or reordered array would make the check above compare unrelated
    numbers, or skip. Length is part of what is pinned.
    """
    resp = _resp()
    assert len(resp) == 130, (
        f"responsiveness_link_points has {len(resp)} entries, expected 130 "
        f"(13 families x 5 probes x 2 arms). The pinned indices no longer identify "
        f"the values they were recorded for."
    )


def test_the_numeric_stack_is_pinned_at_all():
    """Version pins do not explain this drift, but an unpinned stack is a second source."""
    if not PINS.exists():
        pytest.skip("[pins] requirements-repro.txt not present")
    text = PINS.read_text(encoding="utf-8", errors="replace")
    pinned = {
        m.group(1).lower()
        for m in re.finditer(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*[0-9]", text, re.M)
    }
    missing = [name for name in ("numpy", "scipy") if name not in pinned]
    assert not missing, f"{missing} not pinned in requirements-repro.txt"
