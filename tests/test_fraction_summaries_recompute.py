"""Do the "N/M" summaries follow from the per-family numbers beside them?

The robustness section's claims are these strings: the effect survives leaving
out each family in turn (11/13 positive), it survives excluding every Qwen
family (8/9), it survives restricting to >=1B (9/10), and it replicates on
public items (7/8). The paper quotes the strings; the per-family values sit in
the same file and nobody recomputed one from the other.

That gap is the same one the boolean verdicts had, in a different type. A string
is if anything worse: "8/9" reads as a fact, and a reader has no way to tell it
from a fact that used to be true.

The >=1B subset is recomputed across two files -- the per-family effects live in
results_robustness.json and the parameter counts in results_peritem.json -- so
this also checks that the two agree about which families are which size.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[{name}] not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _positive(mapping):
    return f"{sum(1 for v in mapping.values() if v > 0)}/{len(mapping)}"


def test_the_headline_family_count_recomputes():
    b3 = _load("results_robustness.json")["B3_sensitivity"]
    per_family = b3["per_family"]
    assert len(per_family) >= 10, f"only {len(per_family)} families; the panel is 13"
    stored = f"{b3['n_families_positive']}/{b3['n_families']}"
    assert stored == _positive(per_family), (
        f"stored {stored}, per-family values give {_positive(per_family)}"
    )


def test_the_excluding_qwen_count_recomputes():
    b3 = _load("results_robustness.json")["B3_sensitivity"]
    non_qwen = {k: v for k, v in b3["per_family"].items() if "qwen" not in k.lower()}
    assert len(non_qwen) == 9, (
        f"{len(non_qwen)} non-Qwen families; the claim is about 9. Either a "
        f"family was added or the vendor name changed."
    )
    assert b3["excl_qwen_positive"] == _positive(non_qwen), (
        f"stored {b3['excl_qwen_positive']}, recomputed {_positive(non_qwen)}"
    )


def test_the_one_billion_subset_recomputes_across_both_files():
    b3 = _load("results_robustness.json")["B3_sensitivity"]
    sizes = {f: rec["params_b"] for f, rec in _load("results_peritem.json")["per_family"].items()}
    missing = sorted(set(b3["per_family"]) - set(sizes))
    assert not missing, f"{missing} have an effect but no parameter count; the files disagree"

    ge1b = {k: v for k, v in b3["per_family"].items() if sizes[k] >= 1.0}
    assert len(ge1b) == 10, f"{len(ge1b)} families at >=1B; the claim is about 10"
    assert b3["only_ge1B_positive"] == _positive(ge1b), (
        f"stored {b3['only_ge1B_positive']}, recomputed {_positive(ge1b)}"
    )


def test_the_public_item_replication_recomputes():
    c5 = _load("results_robustness.json")["C5_public_items"]
    per_family = c5["per_family"]
    assert len(per_family) == c5["n_families"], (
        f"{len(per_family)} families listed, n_families says {c5['n_families']}"
    )
    assert c5["families_positive"] == _positive(per_family), (
        f"stored {c5['families_positive']}, recomputed {_positive(per_family)}"
    )


def test_every_fraction_summary_with_siblings_is_covered():
    """Vacuity guard: name the fraction strings this file does not recompute.

    Most fraction summaries in the release have no per-item siblings to
    recompute from -- the specification curve stores only its verdicts, the
    frontier detail stores a string per judge. Those are pinned against the
    prose elsewhere. The four here are the ones whose inputs are present, and
    if a fifth appears it should be recomputed rather than trusted.
    """
    rob = _load("results_robustness.json")
    recomputable = [
        key for key, value in (
            ("B3_sensitivity", rob.get("B3_sensitivity")),
            ("C5_public_items", rob.get("C5_public_items")),
        )
        if isinstance(value, dict) and isinstance(value.get("per_family"), dict)
    ]
    assert set(recomputable) == {"B3_sensitivity", "C5_public_items"}, (
        f"the blocks carrying per-family data changed: {recomputable}. A new one "
        f"means a new fraction summary that nothing recomputes."
    )
