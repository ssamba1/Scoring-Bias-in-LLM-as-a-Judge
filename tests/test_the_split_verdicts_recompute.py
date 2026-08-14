"""Do the split preregistered verdicts follow from their own per-unit values?

Two predictions came back split, and the paper reports both halves.

P15 (ten templates): the entropy-bias law holds pooled at rho = -0.51 over 180
points -- the paper's broadest template coverage, though probe-centred its
weakest evidence, which
tests/test_the_pooled_template_law_is_a_between_probe_contrast.py pins -- while
the instruct > base direction holds in only 6 of 10 templates at the
135M--0.5B scale. The paper's sentence is "strengthens the first clause and fails the
second, and we report both".

P19 (chat template): bias under the model's own chat template is substantial in
every cell and chat >= raw in 4 of 6, but the instruct-chat-vs-base-raw effect
is positive in only 1 of 3 families.

Each summary is a count over values stored beside it, and neither had been
recomputed. A split verdict is the easiest kind to drift, because either half
moving still leaves a sentence that reads as balanced -- 8 of 10 templates would
still be "fails the second clause", and 3 of 3 families would still be a small
sample. The counts are the whole content of the qualification.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"


def _load(name):
    path = REPRO / name
    if not path.exists():
        pytest.skip(f"[repro] {name} not present")
    return json.loads(path.read_text())


def test_the_ten_template_count_recomputes():
    blob = _load("results_t10_analysis.json")
    per_template = blob.get("P15b_per_template")
    summary = blob.get("P15b_summary")
    if not isinstance(per_template, dict) or not summary:
        pytest.skip("[repro] no per-template record")

    positive = sum(1 for value in per_template.values() if value > 0)
    assert f"{positive}/{len(per_template)}" in summary, (
        f"the release summarises {summary!r}; its own per-template values give "
        f"{positive}/{len(per_template)} with instruct above base"
    )
    assert len(per_template) == 10, (
        f"the ten-template extension holds {len(per_template)} templates"
    )


def test_the_pooled_template_law_is_still_the_strong_half():
    """The first clause is the half the paper reports as strengthened."""
    blob = _load("results_t10_analysis.json")
    pooled = blob.get("P15a_entropy_bias")
    if not isinstance(pooled, dict):
        pytest.skip("[repro] no pooled template correlation")
    assert pooled["spearman_rho"] < 0, (
        f"the pooled template correlation is {pooled['spearman_rho']}; the "
        f"strengthened clause is that it is negative"
    )
    assert pooled["n"] == 180, (
        f"the pooled correlation is over {pooled['n']} points; the paper says "
        f"180 -- three families x two checkpoints x ten templates x three "
        f"probes, which is 60 judge x template cells of three probes, not 180 "
        f"independent draws"
    )


def test_the_chat_template_counts_recompute():
    blob = _load("results_chat_analysis.json")
    third = blob.get("P19c")
    if not isinstance(third, dict) or "per_family" not in third:
        pytest.skip("[repro] no per-family chat record")

    families = third["per_family"]
    positive = sum(1 for value in families.values() if value > 0)
    assert f"{positive}/{len(families)}" == third["families_positive"], (
        f"the release stores {third['families_positive']} families positive; "
        f"its own values give {positive}/{len(families)}"
    )

    mean = sum(families.values()) / len(families)
    assert abs(mean - third["mean_chat_minus_base"]) <= 0.0015, (
        f"the release stores a mean of {third['mean_chat_minus_base']}; its "
        f"families give {mean:.4f}"
    )


def test_both_weak_halves_are_still_weak():
    """A split verdict stops being split if either half quietly strengthens."""
    templates = _load("results_t10_analysis.json").get("P15b_per_template", {})
    if templates:
        positive = sum(1 for value in templates.values() if value > 0)
        assert positive < len(templates), (
            f"instruct now exceeds base in all {len(templates)} templates; the "
            f"paper reports this clause as failing"
        )

    chat = _load("results_chat_analysis.json").get("P19c", {})
    families = chat.get("per_family", {})
    if families:
        positive = sum(1 for value in families.values() if value > 0)
        assert positive <= len(families) / 2, (
            f"the chat-vs-raw effect is now positive in {positive} of "
            f"{len(families)} families; the paper reports it as weak"
        )
