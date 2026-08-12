"""Is every scoring arm deterministic, as the paper says?

Limitation 2: "Family as unit; greedy decoding. Powered for large effects;
deterministic scores give no within-model variance." That claim is what lets the
paper treat a family's Δ as a fixed quantity rather than one draw from a
distribution, and it is a claim about code: the harnesses read the next-token
logits under no_grad and never sample.

One harness does sample, on purpose. sampled_harness.py exists to show that the
lenient sampled protocol drowns the signal in noise (Appendix A), and it sets
temperature 1.0, do_sample=True and seed 42 because that is the protocol it is
measuring.

If any other harness gained a `.generate()` call, the released scores would
carry sampling noise while the paper still described them as deterministic --
and nothing else would notice, because a noisy score is still a number in range.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
PAPER = REPO / "paper" / "honest" / "scoring_bias_v2.tex"

# The arm whose subject IS the sampled protocol.
SAMPLING_IS_THE_POINT = {"sampled_harness.py"}


def _harnesses():
    found = sorted(REPRO.glob("*harness*.py"))
    if not found:
        pytest.skip("[repro] no harnesses present")
    return found


def test_no_scoring_harness_samples():
    offenders = []
    for path in _harnesses():
        if path.name in SAMPLING_IS_THE_POINT:
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        code = "\n".join(line.split("#", 1)[0] for line in body.splitlines())
        if ".generate(" in code:
            offenders.append(f"{path.name}: calls .generate()")
        if re.search(r"do_sample\s*=\s*True", code):
            offenders.append(f"{path.name}: sets do_sample=True")
        if re.search(r"temperature\s*=\s*(?!0\b)[\d.]+", code):
            offenders.append(f"{path.name}: sets a non-zero temperature")
    assert not offenders, (
        f"the paper says scores are deterministic; these arms sample: "
        f"{offenders}"
    )


def test_the_sampled_arm_still_samples():
    """Vacuity guard: if it stopped, the exemption above is hiding nothing and
    the appendix's protocol comparison has lost its other half."""
    path = REPRO / "sampled_harness.py"
    if not path.exists():
        pytest.skip("[repro] the sampled-protocol harness is not present")
    body = path.read_text(encoding="utf-8", errors="replace")
    assert ".generate(" in body and re.search(r"do_sample\s*=\s*True", body), (
        "sampled_harness.py no longer samples, so the exemption is vacuous and "
        "the parse-failure appendix compares one protocol with itself"
    )


def test_the_scoring_arms_read_logits_without_gradients():
    """no_grad is not correctness, but its absence means the loop was rewritten."""
    missing = []
    for path in _harnesses():
        body = path.read_text(encoding="utf-8", errors="replace")
        if "torch" not in body:
            continue  # the frontier arm is an API client
        if "no_grad" not in body and "inference_mode" not in body:
            missing.append(path.name)
    assert not missing, (
        f"these torch harnesses no longer read logits under no_grad: {missing}"
    )


def test_the_paper_still_claims_determinism():
    if not PAPER.exists():
        pytest.skip("[paper] source not present")
    text = " ".join(PAPER.read_text(encoding="utf-8", errors="replace").split())
    assert "deterministic" in text, (
        "the paper no longer claims deterministic scoring; this guard exists to "
        "hold it to that claim and should be revisited with the sentence"
    )
