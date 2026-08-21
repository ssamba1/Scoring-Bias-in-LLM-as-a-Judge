"""Does the >3B band support the weight the paper puts on it?

The paper scopes its central relation with a contrast: strong below 3B, flat
above. Those 30 rows above 3B are 3 families x 2 checkpoints x 5 probes -- thirty
numbers from three judges -- and treating them as thirty independent
observations is what makes "flat" read as a finding rather than as an absence of
one.

Respecting family clustering, the band is consistent with correlations from
about -0.71 to +0.19. It does not resolve the relation in either direction. The
naive comparison between bands looks significant (p=0.017); the clustered
interval for the same difference includes zero. Both numbers are recorded, and
the guard holds the honest one.

This is the same shape as the registered per-probe nulls, and the same error is
available in both places: reading "we could not detect it" as "it is not there".
The one difference is that the scale claim is load-bearing for the paper's scope,
so overreading it costs more.

The clustered bootstrap was validated by simulation before use -- naive intervals
cover 72-77% at nominal 95% under clustering, clustered ones ~91% -- so the
intervals here are, if anything, slightly too narrow.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"


def _bands():
    path = REPRO / "results_bands.json"
    if not path.exists():
        pytest.skip("[repro] results_bands.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def test_the_high_band_is_three_families_not_thirty_observations():
    band = _bands()["bands"][">3B"]
    assert band["n_families"] == 3 and band["n_cells"] == 30, (
        f"the >3B band is now {band['n_families']} families / {band['n_cells']} "
        f"cells. The whole caution here rests on n=30 being 3 judges; if more "
        f"families have landed above 3B, the band may now resolve something."
    )


def test_clustering_widens_the_interval_it_is_meant_to_widen():
    """Vacuity guard: if clustering changed nothing, it was not applied."""
    band = _bands()["bands"][">3B"]
    naive = band["naive_ci95"]
    clustered = band["clustered_ci95"]
    assert (clustered[1] - clustered[0]) > (naive[1] - naive[0]), (
        f"the clustered interval {clustered} is no wider than the naive one "
        f"{naive}. With ten rows per family it has to be, so either the "
        f"resampling is not grouping by family or the bands changed shape."
    )


def test_the_high_band_does_not_resolve_the_relation():
    band = _bands()["bands"][">3B"]
    low, high = band["clustered_ci95"]
    assert low < -0.3 and high > 0.0, (
        f"the >3B clustered interval is [{low}, {high}]. The paper's caution is "
        f"that this band resolves nothing; an interval that has tightened away "
        f"from zero is a result and should be reported as one."
    )


def test_the_band_difference_is_reported_as_unresolved():
    diff = _bands()["difference"]
    # Recompute the flag from the interval it summarises rather than trusting
    # it. A stored boolean that nothing re-derives is a claim, not a check.
    low, high = diff["clustered_ci95"]
    recomputed = bool(low <= 0 <= high)
    assert recomputed == diff["clustered_ci_crosses_zero"], (
        f"the release records clustered_ci_crosses_zero="
        f"{diff['clustered_ci_crosses_zero']} while its own interval "
        f"[{low}, {high}] gives {recomputed}"
    )
    assert recomputed is True, (
        "the clustered interval for the between-band difference no longer "
        "includes zero. That would make scale-dependence a positive finding "
        "rather than an open question, which is a different paper."
    )
    assert diff["naive_p"] < 0.05, (
        "the naive between-band p is no longer significant, so the contrast "
        "between naive and clustered -- the point of recording both -- has "
        "gone. Check that the naive computation is still being done."
    )


def test_the_paper_does_not_call_the_high_band_flat():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = " ".join(MACROS.read_text(encoding="utf-8", errors="replace").split())
    if "MECHPROSE" not in text:
        pytest.skip("[paper] no mechanism prose")

    start = text.index("MECHPROSE")
    prose = text[start:start + 4000]
    marker = "$>$3B"
    if marker not in prose:
        pytest.skip("[paper] the >3B band is no longer discussed here")
    window = prose[prose.index(marker) - 120:prose.index(marker) + 200]
    assert "flat" not in window.lower(), (
        "the mechanism prose still calls the >3B band flat. Respecting family "
        "clustering it is consistent with anything from about -0.71 to +0.19, "
        "so 'flat' asserts a result the three judges there cannot support; "
        "'unresolved' is what the data say."
    )
