#!/usr/bin/env python3
"""
Honest analysis pipeline for "Where Does Scoring Bias Come From?"

Single source of truth. Reads ONLY the real, provenance-verified dataset
(results_rootcause/t4fam_results.json: per-variant mean scores hand-transcribed
from Kaggle T4 terminal output, 7 open-weight families <=7B, base + instruct).

No synthetic, simulated, or unverifiable data is used. Every number in the paper
and every figure is produced from this script.

Because only per-variant *means* were retained (not per-item scores), the unit of
analysis is the model family. All inferential statistics are family-level paired
comparisons (n = 7). Item-level quantities (flip rate, per-item discrimination,
domain breakdowns) are NOT computable from this data and are therefore not reported.

Outputs (written next to this file, under ../ ):
  repro/results.json         all computed statistics
  tables/tab_summary.tex     main base-vs-instruct summary table
  tables/tab_family.tex      per-family delta table

Deterministic: seed 42 for the bootstrap.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

SEED = 42
N_BOOT = 10_000
ROOT = Path(__file__).resolve().parents[3]        # research-draft/
DATA = ROOT / "results_rootcause" / "t4fam_results.json"
OUT_DIR = Path(__file__).resolve().parent
TAB_DIR = OUT_DIR.parent / "tables"

FAMILIES = [
    "Qwen2.5-0.5B", "Qwen2.5-1.5B", "Llama-3.2-1B", "Llama-3.2-3B",
    "Gemma-2-2B", "StableLM-2-1.6B", "Qwen2.5-7B",
]
# Display metadata (params in billions; training type of the *instruct* variant).
FAMILY_META = {
    "Qwen2.5-0.5B":    (0.5,  "RLHF"),
    "Qwen2.5-1.5B":    (1.5,  "RLHF"),
    "Llama-3.2-1B":    (1.0,  "RLHF"),
    "Llama-3.2-3B":    (3.0,  "RLHF"),
    "Gemma-2-2B":      (2.0,  "RLHF"),
    "StableLM-2-1.6B": (1.6,  "SFT"),
    "Qwen2.5-7B":      (7.0,  "RLHF"),
}
PROBES = ["rubric_order", "score_id", "reference_answer"]
PROBE_LABEL = {
    "rubric_order": "Rubric order",
    "score_id": "Score ID",
    "reference_answer": "Reference answer",
}


def delta(variants: dict[str, float]) -> float:
    """Bias magnitude = max inter-variant spread in mean score (Li et al., 2025)."""
    v = list(variants.values())
    return round(max(v) - min(v), 3)


def cohen_dz(diffs: np.ndarray) -> float:
    """Paired standardized effect size (mean / sd of the differences)."""
    sd = diffs.std(ddof=1)
    return float(diffs.mean() / sd) if sd > 0 else float("nan")


def bootstrap_ci(diffs: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    """Percentile bootstrap 95% CI of the mean paired difference."""
    n = len(diffs)
    means = np.array([rng.choice(diffs, size=n, replace=True).mean()
                      for _ in range(N_BOOT)])
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def main() -> None:
    rng = np.random.default_rng(SEED)
    data = json.loads(DATA.read_text())

    # ---- per-family deltas -------------------------------------------------
    per_family: dict[str, dict] = {}
    base_arr = {p: [] for p in PROBES}
    inst_arr = {p: [] for p in PROBES}
    for fam in FAMILIES:
        b, i = data[fam], data[f"{fam}-IT"]
        row = {"params_b": FAMILY_META[fam][0], "training": FAMILY_META[fam][1]}
        for p in PROBES:
            db, di = delta(b[p]), delta(i[p])
            row[p] = {"base": db, "instruct": di, "change": round(di - db, 3)}
            base_arr[p].append(db)
            inst_arr[p].append(di)
        per_family[fam] = row

    # ---- family-level paired inference -------------------------------------
    summary: dict[str, dict] = {}
    for p in PROBES:
        base = np.array(base_arr[p], float)
        inst = np.array(inst_arr[p], float)
        diffs = inst - base
        lo, hi = bootstrap_ci(diffs, rng)
        # Wilcoxon signed-rank (exact, two-sided); guard the all-zero edge case.
        try:
            w_stat, w_p = stats.wilcoxon(base, inst)
            w_stat, w_p = float(w_stat), float(w_p)
        except ValueError:
            w_stat, w_p = float("nan"), float("nan")
        n_dec = int((diffs < 0).sum())
        n_nonzero = int((diffs != 0).sum())
        summary[p] = {
            "label": PROBE_LABEL[p],
            "base_mean": round(float(base.mean()), 3),
            "base_median": round(float(np.median(base)), 3),
            "instruct_mean": round(float(inst.mean()), 3),
            "instruct_median": round(float(np.median(inst)), 3),
            "mean_change": round(float(diffs.mean()), 3),
            "pct_change": round(100 * diffs.mean() / base.mean(), 1) if base.mean() else None,
            "cohen_dz": round(cohen_dz(diffs), 3),
            "boot_ci95": [round(lo, 3), round(hi, 3)],
            "ci_excludes_zero": bool(hi < 0 or lo > 0),
            "wilcoxon_stat": round(w_stat, 3) if not math.isnan(w_stat) else None,
            "wilcoxon_p": round(w_p, 4) if not math.isnan(w_p) else None,
            "n_families_decreased": n_dec,
            "n_families_nonzero": n_nonzero,
            "n_families": len(FAMILIES),
        }

    results = {
        "dataset": str(DATA.relative_to(ROOT)),
        "provenance": "Per-variant mean scores from Kaggle T4 greedy-decode runs; "
                      "hand-transcribed via build_t4fam_from_output.py. Family-level only.",
        "n_families": len(FAMILIES),
        "seed": SEED,
        "n_bootstrap": N_BOOT,
        "per_family": per_family,
        "summary": summary,
    }
    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2))

    # ---- LaTeX table fragments --------------------------------------------
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    _write_summary_table(summary)
    _write_family_table(per_family)

    # ---- console report ----------------------------------------------------
    print(f"Dataset: {results['dataset']}  (n = {len(FAMILIES)} families)\n")
    hdr = f"{'Probe':16s} {'base':>6} {'instr':>6} {'chg':>7} {'dz':>6} {'dec':>5} {'boot95CI':>16} {'wilcox p':>9}"
    print(hdr); print("-" * len(hdr))
    for p in PROBES:
        s = summary[p]
        ci = f"[{s['boot_ci95'][0]:+.2f},{s['boot_ci95'][1]:+.2f}]"
        star = "*" if s["ci_excludes_zero"] else " "
        print(f"{s['label']:16s} {s['base_mean']:6.2f} {s['instruct_mean']:6.2f} "
              f"{s['mean_change']:+7.2f} {s['cohen_dz']:+6.2f} "
              f"{s['n_families_decreased']:d}/{s['n_families']:d}  {ci:>15}{star} "
              f"{s['wilcoxon_p']!s:>9}")
    print("\n* = bootstrap 95% CI excludes zero (robust reduction).")
    print(f"Wrote {OUT_DIR/'results.json'}, {TAB_DIR/'tab_summary.tex'}, {TAB_DIR/'tab_family.tex'}")


def _write_summary_table(summary: dict) -> None:
    lines = [
        r"% AUTO-GENERATED by repro/analyze.py -- do not edit by hand.",
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"\textbf{Probe} & \textbf{Base} & \textbf{Instruct} & \textbf{Change} & "
        r"\textbf{$d_z$} & \textbf{95\% CI} \\",
        r" & mean $\Delta$ & mean $\Delta$ & (\%) & & (bootstrap) \\",
        r"\midrule",
    ]
    for p in PROBES:
        s = summary[p]
        ci = f"[{s['boot_ci95'][0]:+.2f}, {s['boot_ci95'][1]:+.2f}]"
        bold = r"\textbf" if s["ci_excludes_zero"] else ""
        lines.append(
            f"{s['label']} & {s['base_mean']:.2f} & {s['instruct_mean']:.2f} & "
            f"{bold}{{{s['mean_change']:+.2f} ({s['pct_change']:+.0f}\\%)}} & "
            f"{s['cohen_dz']:+.2f} & {ci} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    (TAB_DIR / "tab_summary.tex").write_text("\n".join(lines))


def _write_family_table(per_family: dict) -> None:
    lines = [
        r"% AUTO-GENERATED by repro/analyze.py -- do not edit by hand.",
        r"\begin{tabular}{lcc" + "cc" * len(PROBES) + "}",
        r"\toprule",
        r"\multirow{2}{*}{\textbf{Family}} & \multirow{2}{*}{\textbf{B}} & "
        r"\multirow{2}{*}{\textbf{Train}} & "
        + " & ".join(rf"\multicolumn{{2}}{{c}}{{\textbf{{{PROBE_LABEL[p]}}}}}" for p in PROBES)
        + r" \\",
        " & & & " + " & ".join("base & inst" for _ in PROBES) + r" \\",
        r"\midrule",
    ]
    for fam, row in per_family.items():
        cells = " & ".join(f"{row[p]['base']:.1f} & {row[p]['instruct']:.1f}" for p in PROBES)
        lines.append(f"{fam} & {row['params_b']:g} & {row['training']} & {cells} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (TAB_DIR / "tab_family.tex").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
