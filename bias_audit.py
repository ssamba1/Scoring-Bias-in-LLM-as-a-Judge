#!/usr/bin/env python3
"""
Bias Auditing Framework — comprehensive CLI for testing any LLM for all bias types.
Analyzes a judge model across 7 bias dimensions and produces a standardized report.

Usage:
  python3 bias_audit.py --judge claude --mode quick
  python3 bias_audit.py --judge gpt4o --mode full --output audit_report.html
  python3 bias_audit.py --list-models
  python3 bias_audit.py --report --input results/results_claude.csv
"""
import argparse, csv, json, os, sys, math
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

# Standardized bias score categories
BIAS_CATEGORIES = {
    "rubric_order": {
        "name": "Rubric Order Bias",
        "description": "Score changes when rubric descriptions are reordered",
        "severity_thresholds": {"low": 0.15, "medium": 0.30, "high": 0.45},
        "interpretation": "Higher = judge is sensitive to rubric format",
    },
    "score_id": {
        "name": "Score ID Bias",
        "description": "Score changes when using different labeling schemes",
        "severity_thresholds": {"low": 0.10, "medium": 0.20, "high": 0.30},
        "interpretation": "Higher = judge uses label format as proxy for quality",
    },
    "reference_answer": {
        "name": "Reference Answer Bias",
        "description": "Score anchored by reference answer's assigned score",
        "severity_thresholds": {"low": 0.20, "medium": 0.40, "high": 0.50},
        "interpretation": "Higher = judge is susceptible to anchoring effects",
    },
    "position": {
        "name": "Position Bias",
        "description": "Preference for responses in specific ordinal positions",
        "severity_thresholds": {"low": 0.05, "medium": 0.15, "high": 0.25},
        "interpretation": "Higher = position in prompt affects judgment",
    },
    "verbosity": {
        "name": "Verbosity Bias",
        "description": "Preference for responses of specific lengths",
        "severity_thresholds": {"low": 0.10, "medium": 0.25, "high": 0.40},
        "interpretation": "Higher = response length used as quality proxy",
    },
    "sentiment": {
        "name": "Sentiment Bias",
        "description": "Penalizing or rewarding emotional tone in responses",
        "severity_thresholds": {"low": 0.08, "medium": 0.18, "high": 0.30},
        "interpretation": "Higher = emotional tone overrides content evaluation",
    },
    "interaction": {
        "name": "Bias Interaction Effect",
        "description": "Non-additive effects when multiple biases co-occur",
        "severity_thresholds": {"low": 0.95, "medium": 1.50, "high": 2.00},
        "interpretation": "IR>1.05 = compounding; IR<0.95 = cancelling",
    },
}

class BiasAuditor:
    """Comprehensive bias auditor for LLM judges."""

    def __init__(self):
        self.scores = {}
        self.report = {}

    def load_results(self, csv_path: Path) -> Dict:
        """Load and parse results from a CSV file."""
        if not csv_path.exists():
            print(f"File not found: {csv_path}")
            return {}

        with open(csv_path) as f:
            data = list(csv.DictReader(f))

        # Parse scores
        parsed = []
        for row in data:
            try:
                score = float(row.get("score", row.get("score_mean", 0)))
                parsed.append({
                    "judge": row.get("judge", csv_path.stem.replace("results_", "")),
                    "item_id": int(row.get("item_id", 0)),
                    "condition": row.get("condition", "baseline"),
                    "score": score,
                    "probe": row.get("bias_type", row.get("probe", "unknown")),
                })
            except (ValueError, TypeError):
                continue

        self.scores = parsed
        print(f"Loaded {len(parsed)} scores from {csv_path}")
        return self.scores

    def compute_severity(self, metric_value: float, category: str) -> str:
        """Classify severity based on metric value."""
        if category not in BIAS_CATEGORIES:
            return "unknown"
        thresholds = BIAS_CATEGORIES[category]["severity_thresholds"]
        if metric_value >= thresholds["high"]:
            return "HIGH"
        elif metric_value >= thresholds["medium"]:
            return "MEDIUM"
        elif metric_value >= thresholds["low"]:
            return "LOW"
        return "NEGLIGIBLE"

    def audit_rubric_order(self) -> Dict:
        """Compute rubric order bias metrics."""
        scores = self.scores
        baseline = [s for s in scores if s.get("condition") == "baseline" or s.get("probe") == "rubric_order_ascending"]
        descending = [s for s in scores if "descending" in s.get("condition", "")]
        random_order = [s for s in scores if "random" in s.get("condition", "")]
        ascending = [s for s in scores if "ascending" in s.get("condition", "")]

        def mean(seq):
            return sum(s["score"] for s in seq) / len(seq) if seq else 0

        def flip_rate(seq, base):
            """Fraction of scores that differ from baseline."""
            if not seq or not base:
                return 0
            base_means = {s["item_id"]: s["score"] for s in base}
            flips = sum(1 for s in seq if s["item_id"] in base_means and s["score"] != base_means[s["item_id"]])
            return flips / len(seq)

        base_mean = mean(baseline) if baseline else (mean(ascending) if ascending else 0)
        desc_mean = mean(descending)
        rand_mean = mean(random_order)

        max_delta = max(
            abs(desc_mean - base_mean) if descending else 0,
            abs(rand_mean - base_mean) if random_order else 0,
        )

        fr_desc = flip_rate(descending, baseline or ascending)
        fr_rand = flip_rate(random_order, baseline or ascending)
        avg_fr = (fr_desc + fr_rand) / 2 if (descending and random_order) else (fr_desc or fr_rand)

        return {
            "baseline_score": round(base_mean, 3),
            "descending_score": round(desc_mean, 3) if descending else None,
            "random_score": round(rand_mean, 3) if random_order else None,
            "max_delta": round(max_delta, 3),
            "flip_rate_descending": round(fr_desc, 3),
            "flip_rate_random": round(fr_rand, 3),
            "avg_flip_rate": round(avg_fr, 3),
            "severity": self.compute_severity(avg_fr, "rubric_order"),
            "interpretation": BIAS_CATEGORIES["rubric_order"]["interpretation"],
        }

    def audit_position(self) -> Dict:
        """Compute position bias metrics."""
        first = [s for s in self.scores if s.get("position") == "first"]
        second = [s for s in self.scores if s.get("position") == "second"]
        baseline = [s for s in self.scores if "baseline" in s.get("condition", "")]

        def mean(seq):
            return sum(s["score"] for s in seq) / len(seq) if seq else 0

        base_mean = mean(baseline) if baseline else mean(first)
        first_mean = mean(first)
        second_mean = mean(second)
        pos_bias = abs(first_mean - second_mean)

        return {
            "first_position_score": round(first_mean, 3),
            "second_position_score": round(second_mean, 3),
            "position_bias_magnitude": round(pos_bias, 3),
            "baseline_score": round(base_mean, 3),
            "preferred_position": "first" if first_mean > second_mean else "second" if second_mean > first_mean else "none",
            "severity": self.compute_severity(pos_bias, "position"),
            "interpretation": BIAS_CATEGORIES["position"]["interpretation"],
        }

    def audit_verbosity(self) -> Dict:
        """Compute verbosity bias metrics."""
        short_r = [s for s in self.scores if s.get("length") == "short"]
        normal = [s for s in self.scores if s.get("length") == "normal"]
        long_r = [s for s in self.scores if s.get("length") == "long"]

        def mean(seq):
            return sum(s["score"] for s in seq) / len(seq) if seq else 0

        short_mean = mean(short_r)
        normal_mean = mean(normal)
        long_mean = mean(long_r)

        short_bias = abs(normal_mean - short_mean) if short_r else 0
        long_bias = abs(long_mean - normal_mean) if long_r else 0
        max_verb_bias = max(short_bias, long_bias)

        return {
            "short_score": round(short_mean, 3) if short_r else None,
            "normal_score": round(normal_mean, 3),
            "long_score": round(long_mean, 3) if long_r else None,
            "short_penalty": round(short_bias, 3),
            "long_bonus": round(long_bias, 3),
            "max_verbosity_bias": round(max_verb_bias, 3),
            "preferred_length": "long" if long_bias > short_bias else "short" if short_bias > long_bias else "normal",
            "severity": self.compute_severity(max_verb_bias, "verbosity"),
            "interpretation": BIAS_CATEGORIES["verbosity"]["interpretation"],
        }

    def audit_interactions(self) -> Dict:
        """Compute bias interaction effects (position × verbosity)."""
        baseline = [s for s in self.scores if s.get("condition") == "baseline"]
        pos_affected = [s for s in self.scores if s.get("position") == "second" and s.get("length") == "normal"]
        verb_affected = [s for s in self.scores if s.get("length") == "long" and s.get("position") == "first"]
        both_affected = [s for s in self.scores if s.get("position") == "second" and s.get("length") == "short"]

        def mean(seq):
            return sum(s["score"] for s in seq) / len(seq) if seq else 0

        base_mean = mean(baseline)
        pos_effect = base_mean - mean(pos_affected) if pos_affected else 0
        verb_effect = base_mean - mean(verb_affected) if verb_affected else 0
        both_effect = base_mean - mean(both_affected) if both_affected else 0

        sum_ind = abs(pos_effect) + abs(verb_effect)
        ir = both_effect / sum_ind if sum_ind > 0 else 1.0

        return {
            "baseline_score": round(base_mean, 3),
            "position_alone_effect": round(pos_effect, 3),
            "verbosity_alone_effect": round(verb_effect, 3),
            "combined_effect": round(both_effect, 3),
            "interaction_ratio": round(ir, 3),
            "classification": "compounding" if ir > 1.05 else "cancelling" if ir < 0.95 else "additive",
            "severity": self.compute_severity(ir, "interaction"),
            "interpretation": BIAS_CATEGORIES["interaction"]["interpretation"],
        }

    def generate_report(self) -> Dict:
        """Generate comprehensive audit report."""
        if not self.scores:
            return {"error": "No data loaded"}

        report = {
            "judge": self.scores[0]["judge"],
            "total_scores": len(self.scores),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

        # Run all audits
        report["rubric_order"] = self.audit_rubric_order()
        report["position"] = self.audit_position()
        report["verbosity"] = self.audit_verbosity()
        report["interactions"] = self.audit_interactions()

        # Overall bias score
        severity_scores = []
        for key in ["rubric_order", "position", "verbosity"]:
            sev = report.get(key, {}).get("severity", "NEGLIGIBLE")
            severity_scores.append({"NEGLIGIBLE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(sev, 0))

        ir = report.get("interactions", {}).get("interaction_ratio", 1.0)
        ir_score = 2 if abs(ir - 1.0) > 0.5 else (1 if abs(ir - 1.0) > 0.05 else 0)

        avg_severity = sum(severity_scores + [ir_score]) / 4

        if avg_severity >= 2.5:
            overall = "HIGH BIAS"
        elif avg_severity >= 1.5:
            overall = "MODERATE BIAS"
        elif avg_severity >= 0.5:
            overall = "LOW BIAS"
        else:
            overall = "NEGLIGIBLE BIAS"

        report["overall_bias_rating"] = overall
        report["bias_score"] = round(avg_severity, 2)

        self.report = report
        return report

    def print_report(self):
        """Print the audit report to stdout."""
        if not self.report:
            self.generate_report()

        r = self.report
        print("\n" + "="*65)
        print(f"  BIAS AUDIT REPORT — {r.get('judge', 'Unknown').upper()}")
        print(f"  Overall: {r.get('overall_bias_rating', 'UNKNOWN')} (score: {r.get('bias_score', '?')}/3.0)")
        print("="*65)

        categories = [
            ("Rubric Order", "rubric_order"),
            ("Position Bias", "position"),
            ("Verbosity Bias", "verbosity"),
            ("Bias Interactions", "interactions"),
        ]

        for name, key in categories:
            data = r.get(key, {})
            severity = data.get("severity", "N/A")
            sev_color = "\033[91m" if severity == "HIGH" else "\033[93m" if severity == "MEDIUM" else "\033[92m"
            reset = "\033[0m"
            print(f"\n  {sev_color}{severity:<12}{reset} {name}")

            for k, v in data.items():
                if k in ("severity", "interpretation"):
                    continue
                print(f"    {k:<30} {v}")

        print("\n" + "="*65)
        print(f"  INTERPRETATION: {r.get('judge', 'Model').upper()} demonstrates {r.get('overall_bias_rating', 'unknown bias').lower()}")
        print("="*65)

    def export_html(self, output_path: Path):
        """Export audit report as HTML."""
        if not self.report:
            self.generate_report()

        r = self.report
        html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<title>Bias Audit Report — {r.get('judge', 'Unknown')}</title>
<style>
body {{font-family:sans-serif;max-width:800px;margin:auto;padding:20px;background:#f5f5f5}}
.header {{background:#333;color:#fff;padding:20px;border-radius:10px;margin-bottom:20px}}
.badge {{display:inline-block;padding:5px 15px;border-radius:20px;font-weight:bold}}
.badge-HIGH {{background:#ff4444;color:#fff}}
.badge-MEDIUM {{background:#ffaa00;color:#000}}
.badge-LOW {{background:#88cc44;color:#000}}
.badge-NEGLIGIBLE {{background:#44aa88;color:#fff}}
.card {{background:#fff;padding:15px;margin:10px 0;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}
table {{width:100%;border-collapse:collapse}}
td {{padding:8px;border-bottom:1px solid #ddd}}
.key {{color:#666;font-size:0.9em}}
</style></head><body>
<div class='header'>
  <h1>Bias Audit Report</h1>
  <p>Judge: <strong>{r.get('judge', 'Unknown')}</strong></p>
  <p>Overall: <span class='badge badge-{r.get('overall_bias_rating','NEGLIGIBLE').split()[0]}'>{r.get('overall_bias_rating', 'UNKNOWN')}</span>
  (score: {r.get('bias_score', '?')}/3.0)</p>
  <p>Scores analyzed: {r.get('total_scores', 0)}</p>
</div>"""

        for name, key in [("Rubric Order Bias", "rubric_order"), ("Position Bias", "position"),
                          ("Verbosity Bias", "verbosity"), ("Bias Interactions", "interactions")]:
            data = r.get(key, {})
            severity = data.get("severity", "NEGLIGIBLE")
            html += f"""
<div class='card'>
  <h2>{name} <span class='badge badge-{severity}'>{severity}</span></h2>
  <table>"""
            for k, v in data.items():
                if k in ("severity", "interpretation"):
                    continue
                html += f"<tr><td class='key'>{k}</td><td>{v}</td></tr>"
            html += f"</table><p style='color:#888;font-size:0.9em'>{data.get('interpretation', '')}</p></div>"

        html += "</body></html>"

        with open(output_path, "w") as f:
            f.write(html)
        print(f"HTML report: {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", help="Judge name to analyze")
    parser.add_argument("--input", help="Input CSV file path")
    parser.add_argument("--output", help="Output HTML report path")
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--quick", action="store_true", help="Quick analysis (first 100 items)")
    args = parser.parse_args()

    auditor = BiasAuditor()

    if args.list_models:
        print("\nAvailable bias audit categories:")
        for key, cat in BIAS_CATEGORIES.items():
            print(f"  {key:<20} {cat['name']:<30} thresholds: {cat['severity_thresholds']}")
        return

    if args.input:
        path = Path(args.input)
    elif args.judge:
        path = RESULTS_DIR / f"results_{args.judge}.csv"
        if not path.exists():
            path = RESULTS_DIR / f"results_{args.judge}.csv"
    else:
        print("Need --judge or --input")
        parser.print_help()
        return

    auditor.load_results(path)
    auditor.generate_report()
    auditor.print_report()

    if args.output:
        auditor.export_html(Path(args.output))

if __name__ == "__main__":
    main()
