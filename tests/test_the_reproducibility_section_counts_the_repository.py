"""The Reproducibility section states three counts, and nothing checked them.

    "Every statistic and figure is produced by the nineteen repro/analyze_*.py
     scripts and eight repro/make_*.py figure generators, from the twenty
     committed raw run files in repro/"

Three assertions about the repository, in a section a replicator reads first,
and all three were unverified. They are correct today -- nineteen, eight,
twenty -- but they are exactly the kind of claim that goes wrong by addition
rather than by editing: nobody adding a twentieth analysis thinks to reread the
Reproducibility paragraph, and no test looks at it.

This repository already has the same failure on record from a related angle: a
derived file that was committed, cited by the paper, and compared against
nothing, because a hand-maintained list in the CI workflow had not kept up with
the analyses. A sentence is a hand-maintained list too.

**Defining "raw" is the whole difficulty**, and it is defined here the only way
that does not require a second hand-maintained list: a raw run file is a
committed data file in repro/ that no analysis writes. results_closed.json
counts as raw even though a script produces it, because that script is
closed_harness.py -- a harness collecting model output, which is what the
sentence means by "collected by the matching repro/*_harness.py". Outputs of
analyze_newprobes.py are templated rather than literal (it writes
f"{stem}_analysis.json" for three different inputs), so the _analysis.json
suffix is what excludes those.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
}

_ASSIGNED = re.compile(r'^\s*(\w+)\s*=\s*HERE\s*/\s*"([A-Za-z0-9_]+\.json)"', re.M)
_LITERAL = re.compile(r'"([A-Za-z0-9_]+\.json)"')


def _claimed():
    """The three counts, read out of the sentence itself."""
    if not PAPER.exists():
        pytest.skip("[paper] main tex not present")
    body = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    pattern = re.compile(
        r"produced by the ([a-z-]+)\s+\\path\{repro/analyze_\*\.py\}\s+scripts and "
        r"([a-z-]+)\s+\\path\{repro/make_\*\.py\}\s+figure generators,\s+from the "
        r"([a-z-]+)\s+committed raw run files"
    )
    match = pattern.search(body)
    if not match:
        pytest.fail(
            "the Reproducibility sentence no longer has the shape this test "
            "reads. It states how many analyses, figure generators and raw run "
            "files the repository has; if the wording changed, update the "
            "pattern deliberately rather than letting the counts go unchecked."
        )
    return [WORDS.get(word) for word in match.groups()], match.groups()


def _analysis_outputs():
    """Files written by an analyze_*.py, by literal name."""
    outputs = set()
    for source in sorted(REPRO.glob("analyze_*.py")):
        text = source.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if "write_text" in line or "write_bytes" in line:
                outputs |= set(_LITERAL.findall(line))
        for variable, name in _ASSIGNED.findall(text):
            if re.search(rf"\b{variable}\.write_(?:text|bytes)", text):
                outputs.add(name)
    return outputs


def _tracked(pattern):
    listing = subprocess.run(
        ["git", "ls-files", "paper/honest/repro"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    if listing.returncode != 0:
        pytest.skip("[git] cannot list tracked files")
    return [Path(line) for line in listing.stdout.splitlines()
            if re.search(pattern, line)]


def test_the_three_counts_are_words_this_test_understands():
    """A number word it cannot read would make every count below vacuous."""
    values, words = _claimed()
    unknown = [w for v, w in zip(values, words) if v is None]
    assert not unknown, (
        f"{unknown} are not number words this test knows, so the counts would "
        f"be compared against None and pass regardless of the repository."
    )


def test_the_analysis_and_generator_counts_match_the_repository():
    (analyses, generators, _raw), _ = _claimed()

    found_analyses = _tracked(r"/analyze_[^/]+\.py$")
    found_generators = _tracked(r"/make_[^/]+\.py$")

    assert len(found_analyses) == analyses, (
        f"the paper says {analyses} analysis scripts; the repository has "
        f"{len(found_analyses)}: {sorted(p.name for p in found_analyses)}"
    )
    assert len(found_generators) == generators, (
        f"the paper says {generators} figure generators; the repository has "
        f"{len(found_generators)}: {sorted(p.name for p in found_generators)}"
    )


def test_the_raw_run_file_count_matches_the_repository():
    """Raw means: committed data in repro/ that no analysis writes."""
    (_a, _g, raw_claimed), _ = _claimed()

    data = _tracked(r"\.json(\.gz)?$")
    produced = _analysis_outputs()
    raw = sorted(
        p.name for p in data
        if p.name not in produced and not p.name.endswith("_analysis.json")
    )

    assert len(raw) == raw_claimed, (
        f"the paper says {raw_claimed} committed raw run files; this counts "
        f"{len(raw)}. Raw here means a committed .json or .json.gz in repro/ "
        f"that no analyze_*.py writes and whose name does not carry the "
        f"_analysis suffix that analyze_newprobes.py appends. Found: {raw}"
    )


def test_every_analysis_output_is_a_file_that_exists():
    """Guard the definition: a write target nobody committed makes raw wrong.

    The raw count is the data files minus the analysis outputs, so an output
    name that matches nothing on disk would silently inflate it.
    """
    produced = _analysis_outputs()
    if not produced:
        pytest.skip("[repro] no analyses found")
    missing = sorted(name for name in produced if not (REPRO / name).exists())
    assert not missing, (
        f"{missing} are written by an analysis but are not on disk, so the raw "
        f"run file count is subtracting names that do not correspond to files"
    )


def test_the_generator_count_is_stated_the_same_way_everywhere():
    """The paragraph stated it twice and disagreed with itself.

    "eight repro/make_*.py figure generators" opened the Reproducibility
    section; eleven lines later the same paragraph said "the seven make_*.py
    generators are run by hand". There are eight. The second was written before
    make_scale_figure.py existed and nothing looked at it again -- and the
    check above reads only the first sentence, so it passed while the paper
    contradicted itself in the same breath.

    This finds every number word attached to make_*.py anywhere in the paper
    and requires them all to be the real count. A count stated twice is a
    quantity defined in two places, which is the shape that put three wrong
    digits in this paper's tables.
    """
    if not PAPER.exists():
        pytest.skip("[paper] main tex not present")
    body = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    generators = len(_tracked(r"/make_[^/]+\.py$"))

    # "eight \path{repro/make_*.py} figure generators", "the seven \path{make_*.py} generators"
    pattern = re.compile(
        r"\b([a-z-]+)\s+(?:\\path\{(?:repro/)?make_\*\.py\}|make_\*\.py)")
    stated = [(word, WORDS.get(word)) for word in pattern.findall(body)]
    assert stated, (
        "no number word is attached to make_*.py anywhere in the paper. The "
        "Reproducibility section states this count; if the wording changed, "
        "update this pattern rather than letting the check find nothing."
    )

    wrong = [
        f"{word!r} ({value}) where the repository has {generators}"
        for word, value in stated if value != generators
    ]
    assert not wrong, (
        f"the paper states the number of figure generators inconsistently or "
        f"incorrectly: {wrong}. Every mention has to be the same number, and "
        f"that number has to be the one on disk."
    )
