"""Does 4-bit quantization change the measured tuning effect? (post hoc)

The paper's only causal point above 8B is a 4-bit Qwen2.5-14B run, attenuated to
+0.06 against the panel's +0.26. Nothing said how much of that was quantization
rather than scale, and nothing could: the 14B has no fp16 counterpart and cannot
get one on the 16 GB card this project has access to, since fp16 weights are
~29.6 GB.

Qwen2.5-7B does have one. It sits in the main panel at fp16, scored on these
exact items by this exact harness, so running it at nf4 measures the
quantization effect by difference instead of assuming it.

The answer is that nf4 does not attenuate the tuning delta. It moves it from
+0.5436 to +0.5757, about +6%, and in the direction of inflation. So the 14B
attenuation is not a quantization artefact, and the scale reading of it is the
one left standing.

Two honest limits. This is one family and one quantization scheme, so it is not
a general claim about quantization; and the comparison is at 7B, so it does not
prove nf4 behaves identically at 14B. What it does rule out is the specific
worry that made the 14B point uninterpretable -- a ~6% inflation cannot produce
a ~77% attenuation.

Worth recording separately: quantization is not innocuous cell by cell. Several
individual probes move sharply (rubric_order base 0.113 -> 0.474, authority
instruct 0.063 -> 0.214). It is the base-versus-instruct contrast that is
stable, not the individual biases, which is the quantity the paper actually
uses.

POST HOC. Not preregistered.

Output: results_quantization.json
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBES = ["rubric_order", "score_id", "reference_answer", "authority", "verbosity"]
FAMILY = "Qwen2.5-7B"


def bias(record, probe):
    means = [v["mean"] for v in record[probe].values()]
    return max(means) - min(means)


def arm_means(record):
    return {kind: sum(bias(record[kind], p) for p in PROBES) / len(PROBES)
            for kind in ("base", "instruct")}


def main():
    panel_path = HERE / "results_scaled.json"
    nf4_path = HERE / "results_7b_nf4.json"
    if not (panel_path.exists() and nf4_path.exists()):
        raise SystemExit("need results_scaled.json and results_7b_nf4.json")

    panel = json.loads(panel_path.read_text())["results"][FAMILY]
    nf4 = json.loads(nf4_path.read_text())["results"][FAMILY]

    fp16_means = arm_means(panel)
    nf4_means = arm_means(nf4)
    fp16_delta = fp16_means["instruct"] - fp16_means["base"]
    nf4_delta = nf4_means["instruct"] - nf4_means["base"]

    per_probe = {}
    for probe in PROBES:
        per_probe[probe] = {
            kind: {"fp16": round(bias(panel[kind], probe), 4),
                   "nf4": round(bias(nf4[kind], probe), 4)}
            for kind in ("base", "instruct")
        }

    out = {
        "note": "POST HOC. Not preregistered. One family, one scheme.",
        "family": FAMILY,
        "reference": "fp16 arm is the committed main panel; nf4 arm is results_7b_nf4.json",
        "fp16": {k: round(v, 4) for k, v in fp16_means.items()},
        "nf4": {k: round(v, 4) for k, v in nf4_means.items()},
        "fp16_tuning_delta": round(fp16_delta, 4),
        "nf4_tuning_delta": round(nf4_delta, 4),
        "delta_change_pct": round(100 * (nf4_delta - fp16_delta) / abs(fp16_delta), 2),
        "quantization_attenuates_delta": bool(abs(nf4_delta) < abs(fp16_delta)),
        "per_probe": per_probe,
        "reading": (
            f"nf4 moves the base-to-instruct bias delta from {fp16_delta:.4f} to "
            f"{nf4_delta:.4f}, an inflation of about "
            f"{100 * (nf4_delta - fp16_delta) / abs(fp16_delta):.0f}%. Quantization "
            f"therefore does not attenuate the tuning effect, so the 14B run's "
            f"attenuation is not explained by its being 4-bit. Individual probes "
            f"do move sharply under quantization; the base-versus-instruct "
            f"contrast is what survives."
        ),
    }

    (HERE / "results_quantization.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
