#!/usr/bin/env python3
"""Generate a comprehensive analysis report from experiment results.
Outputs: results/report.md, results/report.html
"""
import csv, json, os, datetime
from pathlib import Path
from collections import Counter
import statistics

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"

def load_synthetic():
    path = RESULTS_DIR / "bias_interaction_synthetic.csv"
    if not path.exists():
        return None
    with open(path) as f:
        data = list(csv.DictReader(f))
    for r in data:
        r["score"] = float(r["score"])
    return data

def compute_judge_stats(data):
    """Compute comprehensive statistics per judge."""
    judges = sorted(set(r["judge"] for r in data))
    stats = {}

    for judge in judges:
        jd = [r for r in data if r["judge"] == judge]
        scores = [r["score"] for r in jd]

        s = {
            "n": len(jd),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "stdev": statistics.stdev(scores) if len(scores) > 1 else 0,
            "min": min(scores),
            "max": max(scores),
            "distribution": dict(Counter(int(round(s)) for s in scores)),
        }

        # Bias calculations
        baseline = [r for r in jd if r["condition"] == "baseline"]
        worst = [r for r in jd if r["condition"] == "worst"]

        if baseline and worst:
            s["baseline_mean"] = statistics.mean(r["score"] for r in baseline)
            s["worst_mean"] = statistics.mean(r["score"] for r in worst)
            s["degradation"] = s["baseline_mean"] - s["worst_mean"]

        # Position bias
        pf = [r for r in jd if r["position"]=="first" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        ps = [r for r in jd if r["position"]=="second" and r["length"]=="normal" and r["sentiment"]=="neutral"]
        if pf and ps:
            s["position_bias"] = statistics.mean(r["score"] for r in pf) - statistics.mean(r["score"] for r in ps)

        # Verbosity bias
        vl = [r for r in jd if r["length"]=="long" and r["position"]=="first" and r["sentiment"]=="neutral"]
        vn = [r for r in jd if r["length"]=="normal" and r["position"]=="first" and r["sentiment"]=="neutral"]
        if vl and vn:
            s["verbosity_bias"] = statistics.mean(r["score"] for r in vl) - statistics.mean(r["score"] for r in vn)

        # Interaction ratio
        both = [r for r in jd if r["condition"] == "worst"]
        baseline_cond = [r for r in jd if r["condition"] == "baseline"]
        if both and baseline_cond:
            s["combined_effect"] = (statistics.mean(r["score"] for r in baseline_cond) -
                                    statistics.mean(r["score"] for r in both))
        # Also compute condition-based
        both_short_second = [r for r in jd if r["position"]=="second" and r["length"]=="short" and r["sentiment"]=="neutral"]
        if both and baseline and pf and ps and vl and vn:
            pos_bias = s.get("position_bias", 0)
            verb_bias = s.get("verbosity_bias", 0)
            combined = s.get("baseline_mean", 0) - statistics.mean(r["score"] for r in both)
            s["combined_effect"] = combined
            pa, va = abs(pos_bias), abs(verb_bias)
            s["interaction_ratio"] = combined / (pa + va) if (pa + va) > 0 else 0

        stats[judge] = s

    return stats

def generate_markdown_report(stats):
    """Generate a markdown report."""
    lines = []
    lines.append("# Bias Interaction Experiment  Analysis Report")
    lines.append(f"*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Overview table
    lines.append("## Overview\n")
    lines.append("| Judge | N | Mean | StDev | Baseline | Worst | Degradation |")
    lines.append("|-------|---|------|-------|----------|-------|-------------|")
    for judge, s in sorted(stats.items()):
        lines.append(f"| {judge} | {s['n']} | {s['mean']:.2f} | {s['stdev']:.2f} | "
                     f"{s.get('baseline_mean',0):.2f} | {s.get('worst_mean',0):.2f} | "
                     f"{s.get('degradation',0):.3f} |")

    # Bias effects
    lines.append("\n## Bias Effects\n")
    lines.append("| Judge | Position Bias | Verbosity Bias | Combined | Interaction Ratio | Effect |")
    lines.append("|-------|--------------|----------------|----------|-------------------|--------|")
    for judge, s in sorted(stats.items()):
        pa = abs(s.get("position_bias", 0))
        va = abs(s.get("verbosity_bias", 0))
        ir = s.get("interaction_ratio", 0)
        effect = "compounding" if ir > 1.05 else ("cancelling" if ir < 0.95 else "additive")
        lines.append(f"| {judge} | {pa:.3f} | {va:.3f} | {s.get('combined_effect',0):.3f} | "
                     f"{ir:.2f} | {effect} |")

    # Distribution
    lines.append("\n## Score Distribution\n")
    lines.append("| Judge | 1 | 2 | 3 | 4 | 5 |")
    lines.append("|-------|---|---|---|---|---|")
    for judge, s in sorted(stats.items()):
        d = s["distribution"]
        lines.append(f"| {judge} | {d.get(1,0)} | {d.get(2,0)} | {d.get(3,0)} | {d.get(4,0)} | {d.get(5,0)} |")

    # Key findings
    lines.append("\n## Key Findings\n")

    compounding = [j for j, s in stats.items() if s.get("interaction_ratio", 0) > 1.05]
    if compounding:
        lines.append(f"- **Compounding biases detected**: {', '.join(compounding)}  "
                     f"biases are worse together than individually")

    additive = [j for j, s in stats.items() if 0.95 <= s.get("interaction_ratio", 0) <= 1.05]
    if additive:
        lines.append(f"- **Additive biases**: {', '.join(additive)}  biases combine linearly")

    cancelling = [j for j, s in stats.items() if s.get("interaction_ratio", 0) < 0.95]
    if cancelling:
        lines.append(f"- **Cancelling biases**: {', '.join(cancelling)}  biases partially offset")

    lines.append(f"- **Average degradation across judges**: "
                 f"{statistics.mean(s.get('degradation',0) for s in stats.values()):.3f}")

    return "\n".join(lines)

def generate_html_report(md_content):
    """Convert markdown to simple HTML."""
    import re
    html = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
            "<title>Analysis Report</title>",
            "<style>body{font-family:sans-serif;max-width:900px;margin:auto;padding:20px;}",
            "table{border-collapse:collapse;width:100%;margin:10px 0}",
            "th,td{border:1px solid #ddd;padding:8px;text-align:left}",
            "th{background:#f5f5f5}",
            "h2{color:#333;border-bottom:2px solid #4CAF50;padding-bottom:5px}",
            "</style></head><body>"]

    for line in md_content.split("\n"):
        if line.startswith("# "):
            html.append(f"<h1>{line[2:].replace('*','').replace('_','')}</h1>")
        elif line.startswith("## "):
            html.append(f"<h2>{line[3:].replace('*','').replace('_','')}</h2>")
        elif line.startswith("|"):
            if "---" not in line:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                html.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            else:
                html.append("</table><table>")
                html[-1] = html[-1].replace("<tr>", "<thead><tr>")
                html.append("</thead><tbody>")
        elif line.startswith("- "):
            html.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "":
            html.append("<br>")

    html.append("</tbody></table></body></html>")
    return "\n".join(html)

def main():
    data = load_synthetic()
    if not data:
        print("No synthetic data found. Run generate_synthetic_pilot.py first.")
        return

    stats = compute_judge_stats(data)

    # Generate markdown
    md = generate_markdown_report(stats)
    md_path = RESULTS_DIR / "analysis_report.md"
    with open(md_path, "w") as f:
        f.write(md)
    print(f"Markdown report: {md_path}")

    # Generate HTML
    html = generate_html_report(md)
    html_path = RESULTS_DIR / "analysis_report.html"
    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML report: {html_path}")

    print(f"\nReport preview (first 20 lines):")
    for line in md.split("\n")[:20]:
        print(f"  {line}")

if __name__ == "__main__":
    main()
