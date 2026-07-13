#!/usr/bin/env python3
"""
Statistical Analysis Notebook — comprehensive R-style statistical analysis for
bias interaction experiments. Generates publication-ready tables and figures.

Usage:
  python3 statistical_analysis.py --data results/bias_interaction_synthetic_v2.csv
  python3 statistical_analysis.py --data results/bias_interaction_synthetic_v2.csv --anova
  python3 statistical_analysis.py --data results/bias_interaction_synthetic_v2.csv --report
"""
import argparse, csv, json, math, os, sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"

class StatisticalAnalysis:
    """Comprehensive statistical analysis for bias experiments."""

    def __init__(self, data_path: Path):
        self.data = []
        self.judges = []
        with open(data_path) as f:
            self.data = list(csv.DictReader(f))
        for r in self.data:
            r["score"] = float(r["score"])
        self.judges = sorted(set(r["judge"] for r in self.data))
        print(f"Loaded {len(self.data)} data points from {len(self.judges)} judges")

    def descriptive_stats(self) -> Dict:
        """Compute descriptive statistics per judge per condition."""
        stats = {}
        for judge in self.judges:
            jd = [r for r in self.data if r["judge"] == judge]
            by_condition = defaultdict(list)
            for r in jd:
                by_condition[r.get("condition", "unknown")].append(r["score"])

            cond_stats = {}
            for cond, scores in sorted(by_condition.items()):
                n = len(scores)
                mean = sum(scores) / n
                variance = sum((s - mean) ** 2 for s in scores) / (n - 1) if n > 1 else 0
                std = math.sqrt(variance)
                se = std / math.sqrt(n)
                cond_stats[cond] = {
                    "n": n, "mean": round(mean, 3), "median": round(sorted(scores)[n // 2], 3),
                    "std": round(std, 3), "se": round(se, 3),
                    "min": round(min(scores), 1), "max": round(max(scores), 1),
                    "ci_95": [
                        round(mean - 1.96 * se, 3),
                        round(mean + 1.96 * se, 3),
                    ],
                }
            stats[judge] = cond_stats
        return stats

    def anova(self) -> Dict:
        """Two-way ANOVA for interaction effects per judge."""
        results = {}
        for judge in self.judges:
            jd = [r for r in self.data if r["judge"] == judge]

            # Extract factors
            factors = defaultdict(list)
            for r in jd:
                pos = r.get("position", "unknown")
                leng = r.get("length", "unknown")
                sent = r.get("sentiment", "unknown")
                factors["position"].append(pos)
                factors["length"].append(leng)
                factors["sentiment"].append(sent)
                factors["score"].append(r["score"])

            n = len(factors["score"])
            grand_mean = sum(factors["score"]) / n

            # Compute SS for each factor and interaction
            def ss_by_factor(factor_name):
                levels = set(factors[factor_name])
                ss = 0
                for level in levels:
                    idx = [i for i, v in enumerate(factors[factor_name]) if v == level]
                    group_mean = sum(factors["score"][i] for i in idx) / len(idx)
                    ss += len(idx) * (group_mean - grand_mean) ** 2
                return ss, len(levels) - 1

            ss_pos, df_pos = ss_by_factor("position")
            ss_len, df_len = ss_by_factor("length")
            ss_sent, df_sent = ss_by_factor("sentiment")

            # Compute interaction SS
            cells = defaultdict(list)
            for i in range(n):
                key = (factors["position"][i], factors["length"][i], factors["sentiment"][i])
                cells[key].append(factors["score"][i])

            ss_within = 0
            for key, scores in cells.items():
                cell_mean = sum(scores) / len(scores)
                ss_within += sum((s - cell_mean) ** 2 for s in scores)

            # Total SS
            ss_total = sum((s - grand_mean) ** 2 for s in factors["score"])

            ss_interaction = ss_total - ss_pos - ss_len - ss_sent - ss_within
            df_interaction = (len(set(factors["position"])) - 1) * \
                             (len(set(factors["length"])) - 1) * \
                             (len(set(factors["sentiment"])) - 1)

            # Compute F-statistics
            def f_stat(ss_effect, df_effect, ss_error, df_error):
                if df_error <= 0 or ss_error <= 0:
                    return 0, 1.0
                ms_effect = ss_effect / df_effect
                ms_error = ss_error / df_error
                f_value = ms_effect / ms_error
                # Approximate p-value using F-distribution
                from scipy import stats as sp_stats
                try:
                    p_value = 1 - sp_stats.f.cdf(f_value, df_effect, df_error)
                except:
                    p_value = 1.0
                return f_value, p_value

            df_error = n - df_pos - df_len - df_sent - df_interaction - 1
            f_pos, p_pos = f_stat(ss_pos, df_pos, ss_within, df_error)
            f_len, p_len = f_stat(ss_len, df_len, ss_within, df_error)
            f_sent, p_sent = f_stat(ss_sent, df_sent, ss_within, df_error)
            f_int, p_int = f_stat(ss_interaction, df_interaction, ss_within, df_error)

            results[judge] = {
                "grand_mean": round(grand_mean, 3),
                "ss_total": round(ss_total, 3),
                "anova": {
                    "position": {"f": round(f_pos, 3), "p": round(p_pos, 4), "sig": p_pos < 0.05},
                    "length": {"f": round(f_len, 3), "p": round(p_len, 4), "sig": p_len < 0.05},
                    "sentiment": {"f": round(f_sent, 3), "p": round(p_sent, 4), "sig": p_sent < 0.05},
                    "interaction": {"f": round(f_int, 3), "p": round(p_int, 4), "sig": p_int < 0.05},
                },
                "n": n,
            }
        return results

    def cohens_d(self, group1_scores, group2_scores) -> float:
        """Compute Cohen's d effect size."""
        if not group1_scores or not group2_scores:
            return 0
        n1, n2 = len(group1_scores), len(group2_scores)
        m1, m2 = sum(group1_scores) / n1, sum(group2_scores) / n2
        var1 = sum((s - m1) ** 2 for s in group1_scores) / (n1 - 1) if n1 > 1 else 0
        var2 = sum((s - m2) ** 2 for s in group2_scores) / (n2 - 1) if n2 > 1 else 0
        pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        return (m1 - m2) / pooled_std if pooled_std > 0 else 0

    def effect_sizes_table(self) -> Dict:
        """Compute Cohen's d for each bias contrast per judge."""
        table = {}
        for judge in self.judges:
            jd = [r for r in self.data if r["judge"] == judge]

            # Position effect
            first = [r["score"] for r in jd if r.get("position") == "first" and 
                     r.get("length") == "normal" and r.get("sentiment") == "neutral"]
            second = [r["score"] for r in jd if r.get("position") == "second" and
                      r.get("length") == "normal" and r.get("sentiment") == "neutral"]

            # Verbosity effect  
            normal_len = [r["score"] for r in jd if r.get("length") == "normal" and
                          r.get("position") == "first" and r.get("sentiment") == "neutral"]
            long_len = [r["score"] for r in jd if r.get("length") == "long" and
                        r.get("position") == "first" and r.get("sentiment") == "neutral"]

            # Sentiment effect
            neutral = [r["score"] for r in jd if r.get("sentiment") == "neutral" and
                       r.get("position") == "first" and r.get("length") == "normal"]
            negative = [r["score"] for r in jd if r.get("sentiment") == "negative" and
                        r.get("position") == "first" and r.get("length") == "normal"]

            table[judge] = {
                "position_bias_d": round(self.cohens_d(first, second), 3),
                "verbosity_bias_d": round(self.cohens_d(normal_len, long_len), 3),
                "sentiment_bias_d": round(self.cohens_d(neutral, negative), 3),
            }
        return table

    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive statistical report."""
        desc = self.descriptive_stats()
        anova_results = self.anova()
        effects = self.effect_sizes_table()

        lines = []
        lines.append("# Comprehensive Statistical Analysis Report")
        lines.append("")

        # Judge summary
        lines.append("## Judge Overview")
        lines.append("")
        lines.append(f"| Judge | Total Scores | Conditions | Mean Score | Std Dev |")
        lines.append(f"|-------|-------------|-----------|-----------|---------|")
        for judge in self.judges:
            conds = desc[judge]
            all_scores = [r["score"] for r in self.data if r["judge"] == judge]
            mean_s = sum(all_scores) / len(all_scores)
            std_s = math.sqrt(sum((s - mean_s) ** 2 for s in all_scores) / (len(all_scores) - 1))
            lines.append(f"| {judge} | {len(all_scores)} | {len(conds)} | {mean_s:.3f} | {std_s:.3f} |")

        # Effect sizes
        lines.append("\n## Effect Sizes (Cohen's d)")
        lines.append("")
        lines.append(f"| Judge | Position | Verbosity | Sentiment |")
        lines.append(f"|-------|----------|-----------|-----------|")
        for judge in self.judges:
            e = effects[judge]
            lines.append(f"| {judge} | {e['position_bias_d']} | {e['verbosity_bias_d']} | {e['sentiment_bias_d']} |")

        # ANOVA
        lines.append("\n## ANOVA Results")
        lines.append("")

        for judge in self.judges:
            a = anova_results[judge]["anova"]
            lines.append(f"\n### {judge.upper()} ANOVA")
            lines.append("")
            lines.append(f"| Factor | F | p | Significant? |")
            lines.append(f"|--------|---|--|-------------|")
            lines.append(f"| Position | {a['position']['f']} | {a['position']['p']} | {'✅' if a['position']['sig'] else '❌'} |")
            lines.append(f"| Length | {a['length']['f']} | {a['length']['p']} | {'✅' if a['length']['sig'] else '❌'} |")
            lines.append(f"| Sentiment | {a['sentiment']['f']} | {a['sentiment']['p']} | {'✅' if a['sentiment']['sig'] else '❌'} |")
            lines.append(f"| Interaction | {a['interaction']['f']} | {a['interaction']['p']} | {'✅' if a['interaction']['sig'] else '❌'} |")

        return "\n".join(lines)

    def print_summary(self):
        """Print a concise summary."""
        effects = self.effect_sizes_table()

        print(f"\n{'Judge':<12} {'Pos d':<8} {'Verb d':<8} {'Sent d':<8}")
        print("-"*36)
        for judge in self.judges:
            e = effects[judge]
            print(f"{judge:<12} {e['position_bias_d']:<8.3f} {e['verbosity_bias_d']:<8.3f} {e['sentiment_bias_d']:<8.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to CSV data")
    parser.add_argument("--anova", action="store_true", help="Run ANOVA")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    args = parser.parse_args()

    path = Path(args.data)
    if not path.exists():
        print(f"Data not found: {path}")
        sys.exit(1)

    sa = StatisticalAnalysis(path)

    if args.anova:
        results = sa.anova()
        for judge, r in results.items():
            print(f"\n{judge}:")
            for factor, stats in r["anova"].items():
                print(f"  {factor:<15} F={stats['f']:.3f} p={stats['p']:.4f} {'*' if stats['sig'] else ''}")

    if args.report:
        report = sa.generate_comprehensive_report()
        report_path = RESULTS_DIR / "statistical_report.md"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"Report saved: {report_path}")

    sa.print_summary()
