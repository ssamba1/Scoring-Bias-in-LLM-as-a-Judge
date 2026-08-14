"""Do the mechanism section's subgroup correlations come from the data?

The headline entropy-bias correlation is recomputed elsewhere. The sentences
around it are not, and they carry most of the argument's weight: the relation
holds within base-only judges and within instruct-only judges separately (so it
is not the base/instruct split in disguise), it is strong below 3B and flat
above (so the paper says where it is least resolved), and it does *not* rank
probes inside a single checkpoint (so decisiveness is a judge-level trait, not
a judge x probe one).

Every one of those is a subgroup of the same 130 cells, and a subgroup is the
easiest place for an analysis to go wrong without looking wrong: change a band
boundary and the number moves, drop a checkpoint and the mean moves, and the
sentence still reads as a robustness check that passed.

They were checked here for the first time and all seven reproduced. That is the
reason to pin them rather than a reason not to -- an unverified number that
happens to be right is still unverified, and the ten-template correction in
tests/test_the_pooled_template_law_is_a_between_probe_contrast.py came from
exactly this shape: a subgroup structure nobody had recomputed.

The band boundaries are part of what is being pinned. Seven families sit in
1--3B and three above it, which is what makes the >3B subsample n=30; the paper
calls that subsample small and its correlation unresolved, and both halves of
that description have to keep matching the data.
"""

import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
MACROS = REPO / "paper" / "honest" / "macros.tex"


def _results():
    path = REPRO / "results_scaled.json"
    if not path.exists():
        pytest.skip("[repro] results_scaled.json not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))["results"]


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


def _cells():
    """(family, kind, probe, mean entropy, max-min bias) for all 130 cells."""
    rows = []
    for family, record in _results().items():
        for kind in ("base", "instruct"):
            for probe, variants in (record.get(kind) or {}).items():
                if not isinstance(variants, dict):
                    continue
                vals = [v for v in variants.values()
                        if isinstance(v, dict) and "mean" in v and "mean_entropy" in v]
                if len(vals) < 2:
                    continue
                means = [v["mean"] for v in vals]
                entropy = sum(v["mean_entropy"] for v in vals) / len(vals)
                rows.append((family, kind, probe, entropy, max(means) - min(means)))
    return rows


def _rho(rows):
    return _spearman([r[3] for r in rows], [r[4] for r in rows])


def test_the_relation_holds_inside_each_checkpoint_kind():
    """Not a two-group difference dressed up as a correlation."""
    rows = _cells()
    assert len(rows) == 130, f"the panel holds {len(rows)} cells, not 130"

    for kind, expected in (("base", -0.25), ("instruct", -0.33)):
        sel = [r for r in rows if r[1] == kind]
        assert len(sel) == 65, f"{kind} holds {len(sel)} cells, not 65"
        rho = _rho(sel)
        assert abs(rho - expected) < 0.01, (
            f"within {kind}-only judges the entropy-bias relation recomputes to "
            f"{rho:.3f}; the paper reports {expected}. This split is the "
            f"paper's answer to 'the correlation is just base vs instruct'"
        )


def test_the_relation_is_flat_in_the_largest_judges():
    """The paper says where its own relation is least resolved."""
    results = _results()
    sizes = {family: float(record["params_b"]) for family, record in results.items()}
    rows = _cells()

    bands = {
        "<1B": [r for r in rows if sizes[r[0]] < 1.0],
        "1-3B": [r for r in rows if 1.0 <= sizes[r[0]] <= 3.0],
        ">3B": [r for r in rows if sizes[r[0]] > 3.0],
    }
    assert [len(bands[b]) for b in ("<1B", "1-3B", ">3B")] == [30, 70, 30], (
        f"the size bands hold {[(b, len(rows_)) for b, rows_ in bands.items()]}; "
        f"the paper's >3B subsample is n=30, which is what makes it small"
    )

    for band, expected in (("<1B", -0.51), ("1-3B", -0.42)):
        rho = _rho(bands[band])
        assert abs(rho - expected) < 0.01, (
            f"the {band} band recomputes to {rho:.3f}; the paper reports {expected}"
        )

    large = _rho(bands[">3B"])
    assert abs(large) < 0.1, (
        f"the >3B band recomputes to {large:.3f}; the paper reports -0.02 and "
        f"describes the largest judges as where the relation is least resolved. "
        f"If this band has become strong, that sentence understates the result"
    )


def test_entropy_does_not_rank_probes_within_one_judge():
    """The within-checkpoint null the paper reports against itself."""
    rows = _cells()
    per_checkpoint = []
    for family in sorted({r[0] for r in rows}):
        for kind in ("base", "instruct"):
            sel = [r for r in rows if r[0] == family and r[1] == kind]
            if len(sel) < 3:
                continue
            per_checkpoint.append(_rho(sel))

    assert len(per_checkpoint) == 26, (
        f"{len(per_checkpoint)} checkpoints contributed; the paper says 26 "
        f"(13 families x base and instruct)"
    )
    mean = sum(per_checkpoint) / len(per_checkpoint)
    assert abs(mean - (-0.05)) < 0.02, (
        f"the mean within-checkpoint entropy-bias correlation recomputes to "
        f"{mean:.3f}; the paper reports -0.05 and builds on it, assigning "
        f"decisiveness to the judge level and responsiveness to the "
        f"judge x perturbation level"
    )
    assert abs(mean) < 0.15, (
        f"the within-checkpoint relation is now {mean:.3f}; the paper reports "
        f"it as not significant, and the decomposition's division of labour "
        f"depends on it staying that way"
    )


def test_the_prose_still_carries_these_numbers():
    if not MACROS.exists():
        pytest.skip("[paper] macros.tex not present")
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    if "MECHPROSE" not in text:
        pytest.skip("[paper] no mechanism prose")
    start = text.index("MECHPROSE")
    prose = text[start:text.index("\n", start)]

    for fragment, why in [
        ("$\\rho=-0.25$", "the base-only correlation"),
        ("$\\rho=-0.33$", "the instruct-only correlation"),
        ("$-0.42$", "the 1--3B band"),
        ("$n=30$", "the >3B subsample size, which is why it is called small"),
    ]:
        assert fragment in prose, (
            f"the mechanism prose no longer states {why}; this test recomputes "
            f"it from the raw runs, so dropping it from the paper leaves the "
            f"check pinned to nothing a reader can see"
        )
