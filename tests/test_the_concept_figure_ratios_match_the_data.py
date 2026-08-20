"""Do the schematic's three ratios still match the run they summarise?

Figure 1 is a schematic, and its three bars are hardcoded constants in
`make_concept_figure.py`:

    inst_v = [0.71, 1.72, 1.59]   # entropy, responsiveness, bias -- instruct/base

Every other figure is drawn from a released JSON, so `check_figures.py` can
compare what is drawn against what the data says. It cannot do that here: there
is no JSON behind these numbers to compare against, only a comment. So the one
figure whose values are maintained by hand is the one figure the figure checker
cannot verify, and the caption in the paper repeats the same three numbers a
second time by hand.

Both went stale. The score-ordering correction moved responsiveness from
0.1446->0.2584 to 0.1387->0.2387, so the ratio moved 1.79 -> 1.72, and the
figure and its caption both kept 1.73 -- a value that was already rounded from
the pre-correction numbers. It survived the prose gate (which pins macros, and
this is not one), the figure check (no data source), and a full read of the
compiled PDF that caught two other stale numbers in the same pass.

So the constants are recomputed here from the released runs. Entropy and bias
were correct throughout; only responsiveness had drifted, which is exactly why
a check is needed rather than a re-read: two of the three numbers looked right.
"""

import ast
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
GENERATOR = REPRO / "make_concept_figure.py"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _drawn():
    """The three ratios the generator hardcodes."""
    if not GENERATOR.exists():
        pytest.skip("[repro] make_concept_figure.py not present")
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8", errors="replace"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "inst_v" for t in node.targets):
            return list(ast.literal_eval(node.value))
    pytest.skip("[repro] inst_v no longer defined")


def _measured():
    mech = _load("results_mechanism.json")
    resp = mech["responsiveness"]
    per_family = mech["decisiveness_per_family"]
    base_H = sum(v["base"] for v in per_family.values()) / len(per_family)
    inst_H = sum(v["instruct"] for v in per_family.values()) / len(per_family)

    scaled = _load("results_scaled.json")["results"]
    arms = {"base": [], "instruct": []}
    for record in scaled.values():
        for kind in ("base", "instruct"):
            for probe, variants in (record.get(kind) or {}).items():
                if probe not in CONTROL:
                    continue
                means = [v["mean"] for v in variants.values()]
                arms[kind].append(max(means) - min(means))
    base_b = sum(arms["base"]) / len(arms["base"])
    inst_b = sum(arms["instruct"]) / len(arms["instruct"])

    return [inst_H / base_H,
            resp["instruct_mean"] / resp["base_mean"],
            inst_b / base_b]


def test_the_three_bars_are_the_ratios_the_data_gives():
    drawn = _drawn()
    measured = _measured()
    assert len(drawn) == 3, f"the schematic now draws {len(drawn)} bars, not 3"

    labels = ("entropy", "responsiveness", "bias")
    wrong = [
        f"{label}: figure draws {d}, data gives {m:.4f}"
        for label, d, m in zip(labels, drawn, measured)
        if abs(d - m) > 0.005
    ]
    assert not wrong, (
        f"the schematic's hardcoded ratios no longer match the runs they "
        f"summarise: {wrong}. check_figures cannot catch this -- these are "
        f"constants in the generator, not values read from a released file."
    )


def test_the_caption_repeats_the_same_numbers():
    """The caption is a second hand-maintained copy of the same three values."""
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    flat = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    if "fig:concept" not in flat:
        pytest.skip("[paper] no concept figure")

    for value in _drawn():
        token = "$\\times %g$" % value
        assert token in flat, (
            f"the figure draws {value} but the caption does not state it "
            f"({token!r} absent). The caption is the number a reader quotes."
        )
