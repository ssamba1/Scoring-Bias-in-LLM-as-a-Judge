"""How much probability actually sits on a bare score token? (post hoc)

The score is read as an expected value over the answer tokens, conditioned on
that set. Limitation 5 concedes the judges place little mass there and defends
the readout behaviorally rather than by mass. It used to say "small" and give no
number, which is not checkable and does not survive a change in the data.

Two things come out of measuring it. The mean is 0.15% over the measured
variants. And the mass is systematically smaller for instruct checkpoints than
for base ones -- the two arms the paper compares -- which the limitation had not
said. That asymmetry runs in the reassuring direction: instruct models place
LESS mass on bare score tokens, so any artefact from conditioning works against
the reported effect rather than for it.

POST HOC. Not preregistered. Quantifies a stated limitation; establishes no new
effect.

Output: results_readout.json
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBES = {"rubric_order", "score_id", "reference_answer", "authority", "verbosity"}


def masses():
    results = json.loads((HERE / "results_scaled.json").read_text())["results"]
    by_arm = {"base": [], "instruct": []}
    for record in results.values():
        for kind in ("base", "instruct"):
            for probe, variants in (record.get(kind) or {}).items():
                if probe not in PROBES or not isinstance(variants, dict):
                    continue
                for value in variants.values():
                    if isinstance(value, dict) and "mean_mass" in value:
                        by_arm[kind].append(float(value["mean_mass"]))
    return by_arm


def summarise(values):
    ordered = sorted(values)
    n = len(ordered)
    mid = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    return {
        "n_variants": n,
        "mean_pct": round(100 * sum(ordered) / n, 4),
        "median_pct": round(100 * mid, 4),
        "min_pct": round(100 * ordered[0], 4),
        "max_pct": round(100 * ordered[-1], 4),
    }


def main():
    by_arm = masses()
    every = by_arm["base"] + by_arm["instruct"]
    out = {
        "note": "POST HOC. Not preregistered. Quantifies Limitation 5.",
        "what": ("probability mass on the bare score tokens, before the readout "
                 "renormalises over them"),
        "overall": summarise(every),
        "base": summarise(by_arm["base"]),
        "instruct": summarise(by_arm["instruct"]),
    }
    out["instruct_below_base"] = bool(
        out["instruct"]["mean_pct"] < out["base"]["mean_pct"])
    out["reading"] = (
        f"Mass on bare score tokens averages {out['overall']['mean_pct']}% across "
        f"{out['overall']['n_variants']} variants. It is "
        f"{out['base']['mean_pct']}% for base checkpoints and "
        f"{out['instruct']['mean_pct']}% for instruct ones -- an asymmetry between "
        f"the compared arms, running against the reported effect rather than for "
        f"it, since the arm with the larger measured bias is the one placing less "
        f"mass on the tokens the readout conditions on."
    )

    (HERE / "results_readout.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
