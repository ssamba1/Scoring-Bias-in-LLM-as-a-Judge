"""Is the ten-template correlation a law within probes, or a gap between them?

P15 pools 180 points into rho = -0.51 and the paper used to call it "the
broadest template-robustness evidence in the paper". Two things were wrong with
reading it that way, and neither is visible in the stored summary.

The 180 points are 60 judge x template cells of three probes each. Entropy does
vary by probe, so they are not literal duplicates, but three probes scored by
one judge under one template are not three independent draws, and the nominal
p (< 1e-6) is computed as though they were.

Worse, the pooled figure is mostly a level difference *between* probes. Hold
probe identity fixed and it falls to r = -0.19; of the three probes this run
carries, only score_id shows the relation individually (-0.67), while authority
(+0.03) and rubric_order (+0.07) point the other way. A reader told that ten
templates give -0.51 would conclude the law survived a breadth test. What
survived is one probe of three.

This matters because the run is an *extension* -- it is supposed to corroborate
the three-template result. Probe-centred it is the weakest of the three panels,
not the strongest, which is the reverse of how the pooled numbers rank them.

So this recomputes the probe-centred correlation from raw for all three panels
and requires the ordering to be what the paper now says: the main panel and the
three-template run hold up when probe identity is removed, the ten-template
pooled figure does not, and the prose says so rather than claiming breadth as
strength.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = shared
        i = j + 1
    return ranks


def _pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def _spearman(xs, ys):
    return _pearson(_average_ranks(xs), _average_ranks(ys))


def _cell(variants):
    """(mean entropy over variants, max-min spread of variant means)."""
    vals = [v for v in variants.values()
            if isinstance(v, dict) and "mean" in v and "mean_entropy" in v]
    if len(vals) < 2:
        return None
    means = [v["mean"] for v in vals]
    entropy = sum(v["mean_entropy"] for v in vals) / len(vals)
    return entropy, max(means) - min(means)


def _rows_flat(results):
    """(probe, entropy, bias) for a family -> kind -> probe -> variant layout."""
    rows = []
    for rec in results.values():
        for kind in ("base", "instruct"):
            for probe, variants in (rec.get(kind) or {}).items():
                if not isinstance(variants, dict):
                    continue
                cell = _cell(variants)
                if cell:
                    rows.append((probe, *cell))
    return rows


def _rows_nested(results):
    """Same, for the extra family -> kind -> template -> probe level."""
    rows = []
    for rec in results.values():
        for kind in ("base", "instruct"):
            for probes in (rec.get(kind) or {}).values():
                if not isinstance(probes, dict):
                    continue
                for probe, variants in probes.items():
                    if not isinstance(variants, dict):
                        continue
                    cell = _cell(variants)
                    if cell:
                        rows.append((probe, *cell))
    return rows


def _probe_centred(rows):
    """Correlation with each probe's own level removed from both variables.

    Ranking inside a probe and then centring leaves only the within-probe
    covariation, so a pure between-probe level difference contributes nothing.
    """
    xs, ys = [], []
    for probe in sorted({r[0] for r in rows}):
        sel = [r for r in rows if r[0] == probe]
        if len(sel) < 5:
            continue
        rx = _average_ranks([s[1] for s in sel])
        ry = _average_ranks([s[2] for s in sel])
        mx = sum(rx) / len(rx)
        my = sum(ry) / len(ry)
        xs.extend(r - mx for r in rx)
        ys.extend(r - my for r in ry)
    if not xs:
        return None
    return _pearson(xs, ys)


def _t10_rows():
    return _rows_nested(_load("results_t10.json")["results"])


def test_the_pooled_ten_template_figure_survives_only_between_probes():
    rows = _t10_rows()
    pooled = _spearman([r[1] for r in rows], [r[2] for r in rows])
    centred = _probe_centred(rows)

    assert len(rows) == 180, f"the ten-template run holds {len(rows)} cells, not 180"
    assert abs(pooled - (-0.511)) < 0.01, (
        f"the pooled ten-template correlation recomputes to {pooled:.3f}; the "
        f"paper reports -0.51"
    )
    assert abs(centred - (-0.187)) < 0.01, (
        f"probe-centred, the ten-template relation recomputes to {centred:.3f}; "
        f"the paper reports -0.19"
    )
    assert centred > pooled + 0.2, (
        f"the qualification exists because removing the between-probe contrast "
        f"weakens this relation substantially ({pooled:.3f} -> {centred:.3f}); "
        f"if it no longer does, the prose overstates the caveat instead"
    )


def test_only_one_of_the_three_probes_carries_it():
    rows = _t10_rows()
    per_probe = {}
    for probe in sorted({r[0] for r in rows}):
        sel = [r for r in rows if r[0] == probe]
        per_probe[probe] = _spearman([s[1] for s in sel], [s[2] for s in sel])

    assert len(per_probe) == 3, (
        f"the ten-template run carries probes {sorted(per_probe)}; the paper "
        f"says three of the five, which is half the reason its pooled figure "
        f"behaves differently from the main panel"
    )
    negative = sorted(p for p, r in per_probe.items() if r < -0.2)
    shown = ", ".join(f"{p}={r:+.3f}" for p, r in sorted(per_probe.items()))
    assert negative == ["score_id"], (
        f"the paper says score_id alone shows the relation within probe, with "
        f"authority and rubric_order pointing the other way; recomputed, the "
        f"probes showing it are {negative} ({shown})"
    )


def test_the_panels_the_law_rests_on_survive_probe_centring():
    """The two panels the paper leans on must hold with probe level removed."""
    main = _probe_centred(_rows_flat(_load("results_scaled.json")["results"]))
    assert main is not None and main < -0.3, (
        f"probe-centred, the main panel's entropy-bias relation is {main}; the "
        f"paper rests the law on this holding within probes, not merely across "
        f"them, and reports -0.38"
    )

    multi = _load("results_multitemplate.json")["results"]
    by_template = {}
    for key, rec in multi.items():
        template = key.split("__")[-1]
        by_template.setdefault(template, {})[key] = rec
    assert len(by_template) == 3, (
        f"the three-template run holds {sorted(by_template)}"
    )
    for template, subset in sorted(by_template.items()):
        centred = _probe_centred(_rows_flat(subset))
        assert centred is not None and centred < -0.3, (
            f"template {template} gives a probe-centred relation of {centred}; "
            f"the paper reports all three between -0.38 and -0.54, and this is "
            f"the run the ten-template extension is supposed to extend"
        )


def test_the_prose_does_not_sell_breadth_as_strength():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    if "MTPROSE" not in text:
        pytest.skip("[paper] no template prose")
    start = text.index("MTPROSE")
    prose = text[start:text.index("\n", start)]

    assert "broadest template-robustness evidence" not in prose, (
        "the ten-template run is the paper's broadest template coverage but, "
        "probe-centred, its weakest evidence; calling it the broadest evidence "
        "invites the reader to weight it most"
    )
    for fragment, why in [
        ("not 180 independent", "the 180 points are 60 cells of three probes"),
        ("-0.19", "the probe-centred value belongs beside the pooled one"),
        # LaTeX escapes the underscore inside \texttt.
        ("score\\_id", "the one probe that carries it should be named"),
    ]:
        assert fragment in prose, (
            f"the template prose no longer states that {why}; the pooled "
            f"-0.51 reads as a breadth test passed without it"
        )
