"""Is the Chinese replication actually in Chinese, and scoped as the paper says?

The paper calls it "a fully Chinese version of the 5-probe suite" and limits it
in the same breath: it "covers one (natively bilingual) model series". Both are
claims about what ran, and both were unchecked.

A partially translated suite is the failure that matters here. A prompt whose
scaffolding stayed English while the items were translated would still be
described as a Chinese replication, would still produce a full set of numbers,
and would be testing something between two languages that nobody had named. It
is invisible to every other check in this suite, because every one of them
reads the outputs rather than the prompts.

The scope claim is checked too. "One model series" is the sentence that keeps a
four-family Chinese run from being read as broad evidence, and it stops being
true the moment a second series is added -- which is a good change to make and a
bad one to make silently.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"
HARNESS = REPRO / "zh_harness.py"


def _harness():
    if not HARNESS.exists():
        pytest.skip("[repro] the Chinese harness is not present")
    return HARNESS.read_text(encoding="utf-8", errors="replace")


def _results():
    path = REPRO / "results_zh.json"
    if not path.exists():
        pytest.skip("[repro] Chinese results not present")
    return json.loads(path.read_text(encoding="utf-8"))["results"]


def _has_han(text):
    return any("一" <= ch <= "鿿" for ch in text)


def test_the_prompt_scaffolding_is_translated():
    """Not just the items -- the instruction, the field labels, the header."""
    source = _harness()
    built = re.search(r"def build_prompt\([^)]*\):\s*\n((?:\s+.*\n)+)", source)
    assert built, "build_prompt is no longer in the Chinese harness"
    template = built.group(1)
    assert _has_han(template), (
        f"the Chinese harness builds an English prompt: {template.strip()[:120]!r}"
    )
    english = re.findall(r"\b(?:Evaluate|Instruction|Response|Score|Rating|Grade)\b", template)
    assert not english, (
        f"the prompt keeps English scaffolding {sorted(set(english))} around "
        f"translated content; that is a bilingual prompt, not a Chinese one"
    )


def test_every_scale_instruction_is_translated():
    """One untranslated variant makes its probe a different experiment."""
    source = _harness()
    scales = re.findall(r'"(?:control|reversed|random|numeric|letter|descriptive)":\s*\("([^"]*)"',
                        source)
    assert scales, "no scale instructions found in the Chinese harness"
    untranslated = [s for s in scales if s.strip() and not _has_han(s)]
    assert not untranslated, (
        f"these scale instructions are still English: {untranslated}"
    )


def test_the_letter_scale_says_A_is_best_in_chinese_too():
    """The instruction and the A=5 mapping have to agree in both languages."""
    source = _harness()
    letter = re.search(r'"letter":\s*\("([^"]+)"', source)
    if not letter:
        pytest.skip("[repro] no letter variant in the Chinese harness")
    wording = letter.group(1)
    assert "A" in wording and "最好" in wording, (
        f"the Chinese letter instruction is {wording!r}; it must say A is best, "
        f"since the scoring maps A to 5"
    )


def test_the_replication_covers_the_probes_it_claims():
    results = _results()
    probes = set()
    for family in results.values():
        for arm in family.values():
            if isinstance(arm, dict):
                probes |= {k for k, v in arm.items() if isinstance(v, dict)}
    assert len(probes) == 5, (
        f"the paper calls it a 5-probe suite; the released run holds "
        f"{len(probes)}: {sorted(probes)}"
    )


def test_the_one_series_limitation_is_true():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    paper = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    if "model series" not in paper:
        pytest.skip("[paper] the scope limitation is not stated")
    families = sorted(_results())
    series = {re.split(r"[-\d]", name)[0] for name in families}
    assert len(series) == 1, (
        f"the limitations say the Chinese replication covers one model series; "
        f"the run covers {sorted(series)} across {families}"
    )
