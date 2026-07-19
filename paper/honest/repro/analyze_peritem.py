#!/usr/bin/env python3
"""
Per-item analysis for the FIXED harness output (results_full.json).

Unlike the means-only t4fam data, the fixed harness (repro/full_harness.py, run on
Kaggle) logs per-item expected scores AND per-item discrete (argmax) scores AND a
domain tag per item. That unlocks the quantities the retracted paper could only
fabricate: real flip rates and real per-domain bias — all computed here from one
data file. Deterministic (seed 42).

Usage:  python analyze_peritem.py [path/to/results_full.json]
Outputs: results_peritem.json  (+ prints a summary)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats

SEED = 42
N_BOOT = 10_000
HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "results_full.json"

# master maps over all probe families (3 scoring + 2 content-perturbation)
CONTROL = {"rubric_order": "control", "score_id": "numeric", "reference_answer": "none",
           "authority": "none", "verbosity": "control"}
LABEL = {"rubric_order": "Rubric order", "score_id": "Score ID", "reference_answer": "Reference answer",
         "authority": "Authority", "verbosity": "Verbosity"}
FORMAT_PROBES = ["rubric_order", "score_id"]
CONTENT_PROBES = ["reference_answer", "authority", "verbosity"]
PROBES = ["rubric_order", "score_id", "reference_answer"]  # reset in main() from data
INSTRUCT_SUFFIXES = ("-Instruct", "-instruct", "-IT", "-it", "-chat", "-Chat")


def family_of(model: str):
    for s in INSTRUCT_SUFFIXES:
        if model.endswith(s):
            return model[: -len(s)], "instruct"
    return model, "base"


def delta(variant_means: dict) -> float:
    v = list(variant_means.values())
    return max(v) - min(v)


def cohen_dz(diffs: np.ndarray) -> float:
    sd = diffs.std(ddof=1)
    return float(diffs.mean() / sd) if sd > 0 else float("nan")


def boot_ci(diffs: np.ndarray, rng) -> tuple[float, float]:
    n = len(diffs)
    m = np.array([rng.choice(diffs, n, replace=True).mean() for _ in range(N_BOOT)])
    return tuple(np.percentile(m, [2.5, 97.5]))


def main() -> None:
    rng = np.random.default_rng(SEED)
    payload = json.loads(SRC.read_text())
    results = payload["results"]
    domains = payload.get("domains")

    # Accept two output layouts:
    #  (A) family-keyed: results[fam] = {"base": <probes>, "instruct": <probes>, ...}
    #  (B) model-keyed:  results[model] = <probes>  (pair up by name suffix)
    def is_probes(d):
        return isinstance(d, dict) and "rubric_order" in d
    fams: dict[str, dict] = {}
    meta: dict[str, dict] = {}
    layout_a = any(isinstance(v, dict) and ("params_b" in v or "base" in v or "instruct" in v)
                   and not is_probes(v) for v in results.values())
    if results and layout_a:
        for fam, rec in results.items():                       # layout A
            fams[fam] = {k: rec[k] for k in ("base", "instruct") if k in rec}
            meta[fam] = {"params_b": rec.get("params_b"), "training": rec.get("training")}
    else:
        fmeta = payload.get("family_meta", {})
        for model, data in results.items():                    # layout B
            fam, kind = family_of(model)
            fams.setdefault(fam, {})[kind] = data
            if fam in fmeta:
                meta[fam] = {"params_b": fmeta[fam][0], "training": fmeta[fam][1]}
    pairs = {f: d for f, d in fams.items() if "base" in d and "instruct" in d}

    # detect which probe families are present in the data (keep master order)
    global PROBES
    sample = next(iter(pairs.values()))["base"]
    PROBES = [p for p in CONTROL if p in sample]

    per_family = {}
    for fam, d in pairs.items():
        row = {"params_b": meta.get(fam, {}).get("params_b"),
               "training": meta.get(fam, {}).get("training")}
        for probe in PROBES:
            b_means = {v: d["base"][probe][v]["mean"] for v in d["base"][probe]}
            i_means = {v: d["instruct"][probe][v]["mean"] for v in d["instruct"][probe]}
            row[probe] = {
                "base_delta": round(delta(b_means), 3),
                "instruct_delta": round(delta(i_means), 3),
                "base_flip": round(flip_rate(d["base"][probe], probe), 3),
                "instruct_flip": round(flip_rate(d["instruct"][probe], probe), 3),
            }
        per_family[fam] = row

    # family-level paired inference on delta (base vs instruct)
    summary = {}
    for probe in PROBES:
        base = np.array([per_family[f][probe]["base_delta"] for f in per_family], float)
        inst = np.array([per_family[f][probe]["instruct_delta"] for f in per_family], float)
        diffs = inst - base
        lo, hi = boot_ci(diffs, rng)
        try:
            _, wp = stats.wilcoxon(base, inst); wp = float(wp)
        except ValueError:
            wp = float("nan")
        summary[probe] = {
            "label": LABEL[probe], "n_families": len(per_family),
            "base_mean_delta": round(float(base.mean()), 3),
            "instruct_mean_delta": round(float(inst.mean()), 3),
            "mean_change": round(float(diffs.mean()), 3),
            "cohen_dz": round(cohen_dz(diffs), 3),
            "boot_ci95": [round(lo, 3), round(hi, 3)],
            "ci_excludes_zero": bool(hi < 0 or lo > 0),
            "wilcoxon_p": None if np.isnan(wp) else round(wp, 4),
            "n_decreased": int((diffs < 0).sum()),
            "base_mean_flip": round(float(np.mean([per_family[f][probe]["base_flip"] for f in per_family])), 3),
            "instruct_mean_flip": round(float(np.mean([per_family[f][probe]["instruct_flip"] for f in per_family])), 3),
        }

    # Holm-Bonferroni across the 3 probes (family-level Wilcoxon)
    holm = holm_bonferroni({p: summary[p]["wilcoxon_p"] for p in PROBES
                            if summary[p]["wilcoxon_p"] is not None})
    for p in PROBES:
        summary[p]["wilcoxon_p_holm"] = holm.get(p)

    # size dependence: does the base->instruct bias change scale with model size?
    size_effect = size_regression(per_family)

    # per-domain mean bias (base vs instruct), if domain tags present
    domain_summary = domain_analysis(pairs, domains) if domains else None

    out = {"source": str(SRC.name), "seed": SEED, "n_bootstrap": N_BOOT,
           "n_families": len(per_family), "families": list(per_family),
           "per_family": per_family, "summary": summary,
           "size_effect": size_effect, "domain": domain_summary}
    (HERE / "results_peritem.json").write_text(json.dumps(out, indent=2))
    write_tables(out)

    print(f"Source: {SRC.name}   families with base+instruct pairs: {len(per_family)}")
    print(f"{'Probe':16s} {'base d':>7} {'inst d':>7} {'chg':>7} {'dz':>6} {'dec':>4} "
          f"{'CI95':>16} {'wilc p':>7} | {'baseFR':>6} {'instFR':>6}")
    for probe in PROBES:
        s = summary[probe]
        ci = f"[{s['boot_ci95'][0]:+.2f},{s['boot_ci95'][1]:+.2f}]"
        star = "*" if s["ci_excludes_zero"] else " "
        print(f"{s['label']:16s} {s['base_mean_delta']:7.2f} {s['instruct_mean_delta']:7.2f} "
              f"{s['mean_change']:+7.2f} {s['cohen_dz']:+6.2f} {s['n_decreased']:d}/{s['n_families']:d} "
              f"{ci:>15}{star} {str(s['wilcoxon_p']):>7} | {s['base_mean_flip']:6.2f} {s['instruct_mean_flip']:6.2f}")
    print("* = bootstrap 95% CI excludes zero.  FR = flip rate (discrete argmax vs control).")
    if domain_summary:
        print("\nPer-domain mean bias (avg |delta| across families & probes):")
        for dom, v in domain_summary.items():
            print(f"  {dom:12s} base={v['base']:.2f}  instruct={v['instruct']:.2f}")


def flip_rate(probe_data: dict, probe: str) -> float:
    """Fraction of (item, biased-variant) pairs whose discrete score differs from
    the control variant's score. Uses per_item_argmax."""
    def discrete(v):  # prefer argmax; fall back to rounded expected score
        return v.get("per_item_argmax") or [int(round(x)) for x in v["per_item"]]
    ctrl = discrete(probe_data[CONTROL[probe]])
    flips = tot = 0
    for variant, d in probe_data.items():
        if variant == CONTROL[probe]:
            continue
        for a, b in zip(ctrl, discrete(d)):
            tot += 1
            flips += (a != b)
    return flips / tot if tot else 0.0


def write_tables(out: dict) -> None:
    """Emit LaTeX table fragments consumed by the paper (paper/honest/tables/)."""
    tdir = HERE.parent / "tables"; tdir.mkdir(parents=True, exist_ok=True)
    s = out["summary"]; pf = out["per_family"]

    # main summary: delta base/instruct + change + dz + CI + Holm p + flip rates
    L = [r"% AUTO-GENERATED by repro/analyze_peritem.py", r"\begin{tabular}{lccccccc}", r"\toprule",
         r"\textbf{Probe} & \textbf{Base} & \textbf{Instr.} & \textbf{Change} & \textbf{$d_z$} & "
         r"\textbf{95\% CI} & \textbf{$p_{\text{Holm}}$} & \textbf{Flip $\downarrow$} \\",
         r" & $\bar\Delta$ & $\bar\Delta$ & (\%) & & & & base$\to$inst \\", r"\midrule"]
    for p in PROBES:
        x = s[p]; ci = f"[{x['boot_ci95'][0]:+.2f}, {x['boot_ci95'][1]:+.2f}]"
        bold = r"\textbf" if x["ci_excludes_zero"] else ""
        pct = f"{100*x['mean_change']/x['base_mean_delta']:+.0f}" if x["base_mean_delta"] else "--"
        ph = x.get("wilcoxon_p_holm"); phs = f"{ph:.3f}" if ph is not None else "--"
        L.append(f"{x['label']} & {x['base_mean_delta']:.2f} & {x['instruct_mean_delta']:.2f} & "
                 f"{bold}{{{x['mean_change']:+.2f} ({pct}\\%)}} & {x['cohen_dz']:+.2f} & {ci} & {phs} & "
                 f"{x['base_mean_flip']:.2f}$\\to${x['instruct_mean_flip']:.2f} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (tdir / "tab_v2_summary.tex").write_text("\n".join(L))

    # per-family delta table
    L = [r"% AUTO-GENERATED", r"\begin{tabular}{lcc" + "cc" * len(PROBES) + "}", r"\toprule",
         r"\multirow{2}{*}{\textbf{Family}} & \multirow{2}{*}{\textbf{B}} & \multirow{2}{*}{\textbf{Train}} & "
         + " & ".join(rf"\multicolumn{{2}}{{c}}{{\textbf{{{LABEL[p]}}}}}" for p in PROBES) + r" \\",
         r" & & & " + " & ".join("b & i" for _ in PROBES) + r" \\", r"\midrule"]
    for fam in sorted(pf, key=lambda f: (pf[f].get("params_b") or 0)):
        r = pf[fam]; pb = r.get("params_b"); tr = r.get("training") or "--"
        cells = " & ".join(f"{r[p]['base_delta']:.1f} & {r[p]['instruct_delta']:.1f}" for p in PROBES)
        L.append(f"{fam} & {pb:g} & {tr} & {cells} \\\\" if pb else f"{fam} & -- & {tr} & {cells} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (tdir / "tab_v2_family.tex").write_text("\n".join(L))

    # domain table (if present)
    if out.get("domain"):
        L = [r"% AUTO-GENERATED", r"\begin{tabular}{lcc}", r"\toprule",
             r"\textbf{Domain} & \textbf{Base $\bar\Delta$} & \textbf{Instruct $\bar\Delta$} \\", r"\midrule"]
        for dom, v in out["domain"].items():
            L.append(f"{dom.replace('_',' ').title()} & {v['base']:.2f} & {v['instruct']:.2f} \\\\")
        L += [r"\bottomrule", r"\end{tabular}"]
        (tdir / "tab_v2_domain.tex").write_text("\n".join(L))


def holm_bonferroni(pvals: dict) -> dict:
    """Holm step-down adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items); adj = {}; running = 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min((m - i) * p, 1.0))
        adj[k] = round(running, 4)
    return adj


def size_regression(per_family: dict) -> dict:
    """Regress the base->instruct bias change on log10(params) per probe.
    Tests whether the effect is scale-dependent (Spearman + OLS slope)."""
    out = {}
    fams = [f for f in per_family if per_family[f].get("params_b")]
    if len(fams) < 4:
        return {"note": "need >=4 sized families", "n": len(fams)}
    x = np.log10(np.array([per_family[f]["params_b"] for f in fams], float))
    for probe in PROBES:
        chg = np.array([per_family[f][probe]["instruct_delta"]
                        - per_family[f][probe]["base_delta"] for f in fams], float)
        rho, p = stats.spearmanr(x, chg)
        slope = float(np.polyfit(x, chg, 1)[0])
        out[probe] = {"spearman_rho": round(float(rho), 3), "spearman_p": round(float(p), 4),
                      "ols_slope_per_decade": round(slope, 3), "n": len(fams)}
    return out


def domain_analysis(pairs: dict, domains: list) -> dict:
    doms = sorted(set(domains))
    idx = {dom: [i for i, d in enumerate(domains) if d == dom] for dom in doms}
    out = {}
    for dom in doms:
        ii = idx[dom]
        base_deltas, inst_deltas = [], []
        for fam, d in pairs.items():
            for probe in PROBES:
                for kind, acc in (("base", base_deltas), ("instruct", inst_deltas)):
                    means = []
                    for v in d[kind][probe]:
                        pi = d[kind][probe][v]["per_item"]
                        means.append(float(np.mean([pi[i] for i in ii])))
                    acc.append(max(means) - min(means))
        out[dom] = {"base": round(float(np.mean(base_deltas)), 3),
                    "instruct": round(float(np.mean(inst_deltas)), 3)}
    return out


if __name__ == "__main__":
    main()
