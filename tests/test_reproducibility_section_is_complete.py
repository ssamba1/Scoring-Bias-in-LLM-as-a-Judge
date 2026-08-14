"""Does the Reproducibility section describe the pipeline that exists?

It said every statistic and figure is produced by six named scripts from nine
named raw files. The repository holds fourteen analyzers, seven figure
generators and nineteen raw run files. The scripts behind whole sections were
missing from the list -- the frontier judges, the stage ablation, the two new
probes -- so a reader following the section would have reproduced part of the
paper and had no way to know which part.

The failure is the same one that put an unreproduced file in the release: a
hand-written list of what matters, written once and never re-derived. It cannot
be fixed by lengthening the list. The section now states counts, and the counts
are checked against the directory, so adding an analysis fails this until the
sentence is updated.

Every file the section does name must also exist, since a named file that has
been renamed sends the reader looking for something that is not there.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

WORDS = {
    3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
    9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen", 20: "twenty", 21: "twenty-one",
    22: "twenty-two", 23: "twenty-three", 24: "twenty-four",
}


def _section():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = PAPER.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\section\*\{Reproducibility\}(.*?)\\section\*", text, re.S)
    if not match:
        pytest.skip("[paper] no Reproducibility section")
    return " ".join(match.group(1).split())


def _derived_names():
    """Files written by an analyzer or figure generator -- not raw inputs."""
    produced = set()
    for path in list(REPRO.glob("analyze_*.py")) + list(REPRO.glob("make_*.py")):
        body = path.read_text(encoding="utf-8", errors="replace")
        produced |= set(re.findall(
            r'\(\s*HERE\s*/\s*["\']([\w.]+\.json)["\']\s*\)\.write_text', body))
        produced |= set(re.findall(r'_write\w*\(\s*["\']([\w.]+\.json)["\']', body))
    return produced


def _raw_files():
    derived = _derived_names()
    return sorted(
        p.name for p in list(REPRO.glob("*.json")) + list(REPRO.glob("*.json.gz"))
        if p.name not in derived and "_analysis" not in p.name
    )


def test_the_analyzer_count_is_right():
    section = _section()
    analyzers = sorted(p.name for p in REPRO.glob("analyze_*.py"))
    if not analyzers:
        pytest.skip("[repro] no analysis scripts present")
    word = WORDS.get(len(analyzers), str(len(analyzers)))
    assert f"{word} \\path{{repro/analyze_*.py}}" in section, (
        f"the section does not say there are {word} analysis scripts; the "
        f"directory holds {len(analyzers)}: {analyzers}"
    )


def test_the_figure_generator_count_is_right():
    section = _section()
    makers = sorted(p.name for p in REPRO.glob("make_*.py"))
    if not makers:
        pytest.skip("[repro] no figure generators present")
    word = WORDS.get(len(makers), str(len(makers)))
    assert f"{word} \\path{{repro/make_*.py}}" in section, (
        f"the section does not say there are {word} figure generators; the "
        f"directory holds {len(makers)}: {makers}"
    )


def test_the_raw_file_count_is_right():
    section = _section()
    raw = _raw_files()
    if not raw:
        pytest.skip("[repro] no raw run files present")
    word = WORDS.get(len(raw), str(len(raw)))
    assert f"{word} committed raw run files" in section, (
        f"the section does not say there are {word} raw run files; excluding "
        f"everything an analyzer writes, the directory holds {len(raw)}: {raw}"
    )


def test_every_file_the_section_names_exists():
    section = _section()
    named = [n for n in re.findall(r"\\path\{([^}]+)\}", section)
             if "*" not in n and n.endswith((".json", ".json.gz", ".py", ".sh"))]
    assert named, "the section names no files at all"
    missing = []
    for name in named:
        candidates = [REPO / name, REPRO / name, REPO / "paper" / "honest" / name]
        if not any(c.exists() for c in candidates):
            missing.append(name)
    assert not missing, (
        f"the section points the reader at files that do not exist: {missing}"
    )


def test_the_named_examples_are_raw_not_derived():
    """The examples illustrate the raw inputs; a derived file among them misleads."""
    section = _section()
    paths = re.findall(r"\\path\{([^}]+)\}", section)
    named = {n for n in paths if n.endswith((".json", ".json.gz"))}
    derived = _derived_names()
    wrong = sorted(named & derived)
    assert not wrong, (
        f"the section offers {wrong} as examples of raw run files, but they are "
        f"written by an analyzer -- reproducing from them would be circular"
    )
