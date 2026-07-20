"""Analyzer for the nuisance-span patching run (P13). Committed before the data.

Reads spanpatch_results.json: for each probe, delta_instruct, delta_base, and the
per-layer delta when the instruct model's nuisance-span residuals are overwritten
with the base model's. Reports the per-layer bias-reduction fraction
  reduction(L) = (delta_instruct - delta_patched(L)) / (delta_instruct - delta_base)
(1 = fully reduced to base level; 0 = no effect) and the best layer band.
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    p = HERE / name
    if p.exists():
        return json.loads(p.read_text())
    return json.loads(gzip.decompress((HERE / (name + ".gz")).read_bytes()).decode())


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "spanpatch_results.json"
    payload = load(name)
    out = {"pair": payload["pair"], "n_layers": payload["n_layers"],
           "n_items": payload["n_items"], "probes": {}}
    for pname, rec in payload["results"].items():
        di, db = rec["delta_instruct"], rec["delta_base"]
        gap = di - db
        reds = []
        for L, dp in enumerate(rec["per_layer_delta_patched"]):
            red = (di - dp) / gap if abs(gap) > 1e-6 else None
            reds.append(round(red, 3) if red is not None else None)
        best = max((r for r in reds if r is not None), default=None)
        best_layers = [i for i, r in enumerate(reds) if r is not None and best is not None
                       and r >= 0.5]
        out["probes"][pname] = {
            "delta_instruct": di, "delta_base": db,
            "per_layer_reduction": reds,
            "max_reduction": best,
            "layers_with_reduction_ge_50pct": best_layers,
            "p13_met": bool(best is not None and best >= 0.5)}
    (HERE / "spanpatch_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
