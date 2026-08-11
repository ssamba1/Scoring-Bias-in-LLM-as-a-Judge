r"""Does the released data contain as much as the paper says it does?

The audit that retracted the previous version of this project found inflated
scale among its defects: the paper described more evidence than existed. That is
the single easiest defect to introduce by accident -- a number written into prose
early, an experiment later trimmed, and nothing connects the two -- and the
hardest for a reader to detect, because verifying it means counting the raw data
by hand.

The abstract's scale sentence is checked here against the raw result files:

    Across 13 open-weight families (0.1--8B; 26 checkpoints; over 56,000 scored
    judgments across all datasets) and five distinct bias types ...

Two of those five numbers come from macros (\NFAM, \MAXB), so at least they are
written once; the macro values themselves are still unverified against data. The
other three -- 26 checkpoints, 56,000 judgments, five bias types -- are literals
typed into the prose and connected to nothing at all. All five are checked.

A scored judgment is one entry of a `per_item` array: one item scored once by one
checkpoint under one condition. The `per_item_argmax` and `per_item_entropy`
arrays alongside it are *derived from the same judgment* -- the argmax and the
entropy of the same answer distribution -- so counting them would inflate the
total roughly threefold. Only the score arrays count.
"""

import gzip
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
REPRO = HONEST / "repro"
PAPER = HONEST / "scoring_bias_v2.tex"
MACROS = HONEST / "macros.tex"

# The panel run: the 13-family, base-vs-instruct sweep the scale claims describe.
PANEL = REPRO / "results_scaled.json"

# Keys holding one number per scored item. Deliberately does not include
# per_item_argmax / per_item_entropy -- see the module docstring.
SCORE_ARRAYS = {"per_item", "ev_per_item", "sampled_per_item"}

# Metadata stored beside the arms inside each family entry.
NOT_AN_ARM = {"params_b", "training"}


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


def _tracked_raw_files():
    """Raw result files as git knows them, so an untracked stray cannot pad the count."""
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
        if not (name.endswith(".json") or name.endswith(".json.gz")):
            continue
        if "analysis" in name:  # derived, not raw
            continue
        paths.append(REPO / line)
    return [p for p in paths if p.exists()]


def _count_judgments():
    total, per_file = 0, {}
    for path in _tracked_raw_files():
        try:
            data = _load(path)
        except (json.JSONDecodeError, OSError, gzip.BadGzipFile):
            continue
        count = 0
        for keypath, value in _walk(data):
            leaf = keypath.rsplit(".", 1)[-1]
            if leaf not in SCORE_ARRAYS:
                continue
            if value and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value):
                count += len(value)
        if count:
            per_file[path.name] = count
            total += count
    return total, per_file


def _panel():
    if not PANEL.exists():
        pytest.skip(f"[panel data] {PANEL.name} not present")
    return _load(PANEL)["results"]


def _macro(name):
    text = MACROS.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\newcommand\{\\" + name + r"\}\{([^}]*)\}", text)
    assert match, f"macro \\{name} is not defined in macros.tex"
    return match.group(1)


def _paper_text():
    if not PAPER.exists():
        pytest.skip("[paper] scoring_bias_v2.tex not present")
    return PAPER.read_text(encoding="utf-8", errors="replace")


def test_family_count_macro_matches_the_panel():
    """\\NFAM is the number of families actually in the panel run."""
    families = _panel()
    assert _macro("NFAM") == str(len(families)), (
        f"the paper says \\NFAM={_macro('NFAM')} families, the panel data has "
        f"{len(families)}: {sorted(families)}"
    )


def test_checkpoint_count_matches_the_panel():
    """The literal '26 checkpoints' equals families x arms, counted from the data."""
    families = _panel()
    checkpoints = sum(
        len([arm for arm in arms if arm not in NOT_AN_ARM])
        for arms in families.values()
        if isinstance(arms, dict)
    )
    # Every statement of the count, in the body and in the prose macros -- not
    # just the first. The number is written in three places; checking one would
    # let the other two drift.
    text = _paper_text() + MACROS.read_text(encoding="utf-8", errors="replace")
    claims = re.findall(r"(\d+)\s+checkpoints", text)
    assert claims, "the paper no longer states a checkpoint count"
    wrong = sorted({c for c in claims if int(c) != checkpoints})
    assert not wrong, (
        f"the paper claims {wrong} checkpoints in {len(claims)} place(s); the "
        f"panel data has {checkpoints} ({len(families)} families x arms)"
    )


def test_parameter_range_matches_the_panel():
    """'0.1--8B' brackets the sizes actually run."""
    families = _panel()
    sizes = [f["params_b"] for f in families.values() if isinstance(f, dict) and "params_b" in f]
    assert sizes, "no parameter counts in the panel data"
    assert float(_macro("MAXB")) >= max(sizes), (
        f"the paper's upper bound \\MAXB={_macro('MAXB')}B is below the largest "
        f"model actually run ({max(sizes)}B)"
    )
    # The lower bound is written as 0.1 and the smallest model is 0.135B: the
    # claim rounds down, which is the safe direction. Reject only overstatement.
    assert min(sizes) < 1.0, f"the paper implies a sub-1B judge; the smallest run is {min(sizes)}B"


def test_bias_type_count_matches_the_panel():
    """'five distinct bias types' equals the probes each checkpoint actually ran."""
    families = _panel()
    probe_sets = {
        frozenset(arms["base"])
        for arms in families.values()
        if isinstance(arms, dict) and isinstance(arms.get("base"), dict)
    }
    assert len(probe_sets) == 1, f"families disagree on which probes were run: {probe_sets}"
    probes = next(iter(probe_sets))
    # The claim appears in the body and inside the prose macros, sometimes with
    # markup between the word and the noun ("\emph{five} bias types").
    text = _paper_text() + MACROS.read_text(encoding="utf-8", errors="replace")
    assert re.search(r"five\}?\s*bias types", text), (
        "the paper no longer says 'five bias types'; update this guard to match "
        "the new wording rather than deleting it"
    )
    assert len(probes) == 5, f"the paper claims five bias types; the data has {len(probes)}: {sorted(probes)}"


def test_the_released_data_holds_the_judgments_the_paper_claims():
    """'over 56,000 scored judgments' is a floor the raw data actually clears."""
    text = _paper_text()
    claimed = re.search(r"over\s+(\d[\d,\s]*(?:\{,\})?[\d,\s]*)\s+scored judgments", text)
    assert claimed, "the paper no longer states a judgment count"
    floor = int(re.sub(r"[^\d]", "", claimed.group(1)))

    total, per_file = _count_judgments()
    assert total, "no scored judgments found in any tracked raw result file"
    assert total >= floor, (
        f"the paper claims over {floor:,} scored judgments; the released data "
        f"contains {total:,}. Per file: {per_file}"
    )


def test_the_counter_finds_the_files_it_is_meant_to_count():
    """The count must not be satisfied by one file, or a deletion would go unseen.

    Without this, dropping every raw file but the largest would still clear the
    56,000 floor and every assertion above would stay green -- the vacuity shape
    that makes a passing suite meaningless.
    """
    total, per_file = _count_judgments()
    assert len(per_file) >= 8, (
        f"only {len(per_file)} raw file(s) contributed scored judgments "
        f"({sorted(per_file)}); the paper describes judgments across many datasets"
    )
    largest = max(per_file.values())
    assert largest < total, "a single file supplies the entire judgment count"
