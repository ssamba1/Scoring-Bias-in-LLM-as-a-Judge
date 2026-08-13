"""Is the released raw data internally consistent?

Every number in the paper is a reduction of these arrays, and nothing checked
the arrays themselves. The reproduction gate compares derived JSON to derived
JSON: corrupt the raw data and the gate still passes, because the analyses would
faithfully re-derive the corrupted result and it would match what was committed.

So the raw files are checked here for the failures that move a mean without
looking like anything:

  * an array shorter than the run's own n_items -- items silently dropped
  * ragged lengths within one file -- a truncated write
  * NaN or infinity -- a failed forward pass recorded as a number
  * a score off the rating scale, or a negative entropy -- impossible values

None of these are hypothetical classes of defect for this project: it published
fabricated data once, and the honest release is the whole of the evidence.
"""

import gzip
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Arrays of one value per scored item.
SCORE_ARRAYS = {"per_item", "ev_per_item", "sampled_per_item"}
DERIVED_ARRAYS = {"per_item_argmax", "per_item_entropy"}
ALL_ARRAYS = SCORE_ARRAYS | DERIVED_ARRAYS

# The judges score on a 1-5 or 1-10 rubric depending on the probe; expected
# values fall between. Bounds are deliberately loose -- this catches impossible
# values, not surprising ones.
SCORE_MIN, SCORE_MAX = 0.0, 10.0


def _load(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _walk(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        yield path, obj
        for value in obj:
            if isinstance(value, (dict, list)):
                yield from _walk(value, path + "[]")


def _raw_files():
    listing = subprocess.run(
        ["git", "ls-files", "paper/honest/repro"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    paths = []
    for line in listing.stdout.splitlines():
        name = Path(line).name
        if "analysis" in name or not (name.endswith(".json") or name.endswith(".json.gz")):
            continue
        path = REPO / line
        if path.exists():
            paths.append(path)
    if not paths:
        pytest.skip("[repro data] no tracked raw result files")
    return paths


def _arrays(data):
    """(keypath, leaf, values) for every numeric per-item array in a file.

    null is a recorded outcome, not a malformed entry: the sampled harness
    writes it for an item whose k draws never parsed. Requiring every entry to
    be numeric dropped all 36 sampled_per_item arrays from the length and
    raggedness checks, and dropped them silently, because the ev_per_item
    arrays beside them kept the file out of the skip list. An array of 20 with
    two nulls is still an array of 20, and its length is exactly what these
    checks exist to compare.
    """
    for keypath, value in _walk(data):
        leaf = keypath.rsplit(".", 1)[-1]
        if leaf not in ALL_ARRAYS or not value:
            continue
        if all(
            v is None or (isinstance(v, (int, float)) and not isinstance(v, bool))
            for v in value
        ):
            yield keypath, leaf, value


def _numeric(values):
    """The recorded values, dropping items that never parsed."""
    return [v for v in values if v is not None]


@pytest.mark.parametrize("path", _raw_files(), ids=lambda p: p.name)
def test_every_value_is_finite(path):
    bad = []
    for keypath, _, values in _arrays(_load(path)):
        for i, v in enumerate(values):
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                bad.append(f"{keypath}[{i}]={v}")
    assert not bad, f"{path.name} holds non-finite values: {bad[:5]}"


@pytest.mark.parametrize("path", _raw_files(), ids=lambda p: p.name)
def test_scores_lie_on_the_rating_scale(path):
    bad = []
    for keypath, leaf, values in _arrays(_load(path)):
        if leaf not in SCORE_ARRAYS:
            continue
        out = [v for v in _numeric(values) if not (SCORE_MIN <= v <= SCORE_MAX)]
        if out:
            bad.append(f"{keypath}: {out[:3]}")
    assert not bad, (
        f"{path.name} holds scores outside [{SCORE_MIN}, {SCORE_MAX}]: {bad[:5]}. "
        f"A judge cannot return these; something upstream is writing a sentinel "
        f"or an unnormalised value into the score array."
    )


@pytest.mark.parametrize("path", _raw_files(), ids=lambda p: p.name)
def test_entropies_are_not_negative(path):
    bad = []
    for keypath, leaf, values in _arrays(_load(path)):
        if leaf != "per_item_entropy":
            continue
        neg = [v for v in _numeric(values) if v < 0]
        if neg:
            bad.append(f"{keypath}: {neg[:3]}")
    assert not bad, f"{path.name} holds negative entropy values: {bad[:5]}"


@pytest.mark.parametrize("path", _raw_files(), ids=lambda p: p.name)
def test_arrays_all_have_the_same_length(path):
    lengths = Counter(len(values) for _, _, values in _arrays(_load(path)))
    if not lengths:
        pytest.skip(f"[no per-item arrays] {path.name}")
    modal = lengths.most_common(1)[0][0]
    odd = {length: count for length, count in lengths.items() if length != modal}
    assert not odd, (
        f"{path.name} has ragged per-item arrays: most are {modal} long, but "
        f"{odd} also occur. A short array drops items from a mean without "
        f"changing anything that looks wrong."
    )


@pytest.mark.parametrize("path", _raw_files(), ids=lambda p: p.name)
def test_array_length_matches_the_declared_item_count(path):
    data = _load(path)
    if not isinstance(data, dict) or "n_items" not in data:
        pytest.skip(f"[no declared n_items] {path.name}")
    declared = data["n_items"]
    lengths = Counter(len(values) for _, _, values in _arrays(data))
    if not lengths:
        pytest.skip(f"[no per-item arrays] {path.name}")
    modal = lengths.most_common(1)[0][0]
    assert modal == declared, (
        f"{path.name} declares n_items={declared} but its per-item arrays are "
        f"{modal} long"
    )


def test_the_audit_actually_reads_arrays():
    """Vacuity guard: a key rename would leave every check above scanning nothing."""
    total = sum(len(list(_arrays(_load(path)))) for path in _raw_files())
    assert total >= 500, (
        f"only {total} per-item arrays found across the raw files; the key names "
        f"in ALL_ARRAYS no longer match the data"
    )
