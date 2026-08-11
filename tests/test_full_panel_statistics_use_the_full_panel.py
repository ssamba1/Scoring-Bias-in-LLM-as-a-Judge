"""Do the statistics the paper says span the whole panel actually span it?

Two sentences quote a cell count: the bound's slack runs "0.37--0.57 across all
130 cells", and the decisiveness-bias link is fit "across all families, five
bias types, and both checkpoints (n=130)". Both were literals. The released
statistics each record their own n, and nothing compared the two, nor either
against the panel.

The number that matters is not 130 but the product of the panel: families times
checkpoint kinds times probes. So it is derived from results_scaled.json here
rather than written down, and the paper's literal is checked against the
derivation.

The failure this is aimed at is quiet. Every one of these statistics drops
cells it cannot use -- a degenerate variance, a missing checkpoint, a fit that
does not converge -- and dropping some would leave the range, the correlation
and the p-value all still correct for the cells that survived, while the word
"all" in front of "130 cells" became false. Nothing else in the suite would
notice, because nothing else reads n.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

CONTROL_PROBES = ("rubric_order", "score_id", "reference_answer", "authority", "verbosity")

# Statistics the paper describes as covering the whole panel, and where they live.
FULL_PANEL = [
    ("results_robustness.json", ("F5_bound_tightness", "n"), "the bound-slack range"),
    ("results_robustness.json", ("B1_lmm", "n"), "the mixed model"),
    ("results_robustness.json", ("B4_readout_concordance", "n"), "the readout concordance"),
    ("results_mechanism.json", ("entropy_bias_link", "n"), "the decisiveness-bias link"),
    ("results_mechanism.json", ("entropy_bias_link_control_only", "n"),
     "the control-only decisiveness-bias link"),
    ("results_mechanism.json", ("var_bias_link", "n"), "the variance-term correlation"),
    ("results_mechanism.json", ("responsiveness_bias_link", "n"),
     "the responsiveness-bias correlation"),
]


def _panel_cells():
    """families x kinds x probes, counted from the released panel."""
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] scaled results not present")
    results = json.loads(path.read_text())["results"]
    cells = 0
    for family in results.values():
        for kind in ("base", "instruct"):
            checkpoint = family.get(kind)
            if not isinstance(checkpoint, dict):
                continue
            cells += sum(1 for probe in CONTROL_PROBES if probe in checkpoint)
    if not cells:
        pytest.skip("[repro] the panel holds no cells")
    return cells


def _dig(blob, keys):
    for key in keys:
        if not isinstance(blob, dict) or key not in blob:
            return None
        blob = blob[key]
    return blob


@pytest.mark.parametrize("filename,keys,label", FULL_PANEL,
                         ids=[k[0] for _, k, _ in FULL_PANEL])
def test_the_statistic_covers_every_cell(filename, keys, label):
    path = REPRO / filename
    if not path.exists():
        pytest.skip(f"[repro] {filename} not present")
    stored = _dig(json.loads(path.read_text()), keys)
    assert isinstance(stored, int), (
        f"{label} records no n at {'/'.join(keys)}, so whether it covers the "
        f"panel cannot be told from the release"
    )
    cells = _panel_cells()
    assert stored == cells, (
        f"{label} is fit on {stored} cells; the panel holds {cells}. The paper "
        f"describes it as covering all of them, and a statistic that silently "
        f"drops cells stays correct for the cells it kept while the word 'all' "
        f"stops being true."
    )


def test_the_paper_quotes_the_panel_it_has():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    cells = _panel_cells()
    for phrase in (f"across all {cells} cells", f"$n={cells}$"):
        assert phrase in text, (
            f"the paper does not state {phrase!r}, but the panel holds {cells} "
            f"cells -- either the count drifted or the sentence was reworded, "
            f"and both need this check updated deliberately"
        )
