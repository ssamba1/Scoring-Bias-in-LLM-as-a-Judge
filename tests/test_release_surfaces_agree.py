r"""Do the release's several front doors say the same thing?

A repository states the same facts in several places -- LICENSE, CITATION.cff, a
README badge, the paper -- maintained separately and read by different people.
They drift, and always in the direction of whoever edited last. Two had drifted
here.

LICENCE. The README badge advertised CC BY 4.0 while linking to a LICENSE file
containing the MIT text, and CITATION.cff also said MIT. A reader who trusts the
badge and a reader who opens the file come away with different rights. Whichever
was intended, three surfaces disagreeing is the defect.

SCALE. The README described the panel as "13,000 per-item scores". That is the
mixed model's row count -- perturbed conditions only, control rows dropped --
not a count of scores. The panel holds 19,500, and the paper's abstract says
over 56,000 across all datasets, so a reader comparing the two could not
reconcile them.

Both are checked against something authoritative rather than against a
remembered string: the licence against the LICENSE file itself, the scale
against the released data.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
LICENSE = REPO / "LICENSE"
CFF = REPO / "CITATION.cff"
PANEL = REPO / "paper" / "honest" / "repro" / "results_scaled.json"

# Text that identifies a licence family inside the LICENSE file itself.
LICENCE_SIGNATURES = {
    "MIT": "MIT License",
    "Apache-2.0": "Apache License",
    "CC BY 4.0": "Creative Commons Attribution 4.0",
    "CC BY-SA 4.0": "Creative Commons Attribution-ShareAlike 4.0",
    "BSD-3-Clause": "BSD 3-Clause",
}


def _declared_licence():
    if not LICENSE.exists():
        pytest.skip("[licence] no LICENSE file")
    head = LICENSE.read_text(encoding="utf-8", errors="replace")[:400]
    for name, signature in LICENCE_SIGNATURES.items():
        if signature.lower() in head.lower():
            return name
    pytest.skip(f"[licence] LICENSE text not recognised: {head.splitlines()[:1]}")


def _readme():
    if not README.exists():
        pytest.skip("[readme] not present")
    return README.read_text(encoding="utf-8", errors="replace")


def test_the_readme_badge_matches_the_licence_file():
    licence = _declared_licence()
    badge = re.search(r"img\.shields\.io/badge/License-([^-?]+)", _readme())
    if not badge:
        pytest.skip("[readme] no licence badge")
    shown = badge.group(1).replace("_", " ").strip()
    assert shown.lower() == licence.lower(), (
        f"the README badge advertises {shown!r} but LICENSE contains the "
        f"{licence} text. A reader who trusts the badge and one who opens the "
        f"file get different answers."
    )


def test_the_citation_record_matches_the_licence_file():
    licence = _declared_licence()
    if not CFF.exists():
        pytest.skip("[metadata] no CITATION.cff")
    cff_text = CFF.read_text(encoding="utf-8", errors="replace")
    declared = re.search(r"^license:\s*(.+)$", cff_text, re.M)
    if not declared:
        pytest.skip("[metadata] CITATION.cff declares no licence")
    value = declared.group(1).strip().strip("\"'")
    assert value.lower() == licence.lower(), (
        f"CITATION.cff says {value!r} but LICENSE contains the {licence} text; "
        f"this record is what Zenodo reads when minting a DOI"
    )


def _panel_scores():
    if not PANEL.exists():
        pytest.skip("[panel data] results_scaled.json not present")
    data = json.loads(PANEL.read_text(encoding="utf-8", errors="replace"))["results"]
    total = 0
    for arms in data.values():
        for arm in ("base", "instruct"):
            for cell in arms[arm].values():
                if not isinstance(cell, dict):
                    continue
                for condition in cell.values():
                    if isinstance(condition, dict) and condition.get("per_item"):
                        total += len(condition["per_item"])
    return total


def test_the_readme_panel_scale_matches_the_released_panel():
    """Any per-item-score count in the README's headline must be the real one."""
    readme = " ".join(_readme().split())
    m = re.search(r"([\d,]+)\s+per-item scores", readme)
    if not m:
        pytest.skip("[readme] no per-item score count stated")
    claimed = int(m.group(1).replace(",", ""))
    actual = _panel_scores()
    assert claimed == actual, (
        f"the README says {claimed:,} per-item scores in the main panel; the "
        f"released panel holds {actual:,}. (13,000 is the mixed model's row "
        f"count, which drops control rows -- not a count of scores.)"
    )


def test_the_panel_is_actually_being_counted():
    """Vacuity guard: an empty parse would make the comparison meaningless."""
    assert _panel_scores() >= 19500, f"only {_panel_scores()} per-item scores found in the panel"
