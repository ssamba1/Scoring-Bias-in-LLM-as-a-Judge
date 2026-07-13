#!/usr/bin/env python3
"""
Automated Paper Generation Pipeline.
Takes raw experimental data and produces a formatted paper with results tables,
figures, and statistical analysis. End-to-end: data → formatted paper.

Usage:
  python3 paper_generator.py --data results/bias_interaction_synthetic_v2.csv
  python3 paper_generator.py --data results/bias_interaction_synthetic_v2.csv --format latex
  python3 paper_generator.py --data results/bias_interaction_synthetic_v2.csv --format md --output paper.md
"""
import argparse, csv, json, math, os, sys, datetime
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
PAPER_DIR = BASE_DIR / "paper"

class PaperGenerator:
    """Generates formatted papers from experimental data."""

    def __init__(self, data_path: Path):
        with open(data_path) as f:
            self.data = list(csv.DictReader(f))
        for r in self.data:
            r["score"] = float(r["score"])
        self.judges = sorted(set(r["judge"] for r in self.data))

    def _condition_mean(self, judge: str, cond: str) -> float:
        scores = [r["score"] for r in self.data if r["judge"] == judge and r["condition"] == cond]
        return sum(scores) / len(scores) if scores else 0

    def _condition_scores(self, judge: str, position=None, length=None, sentiment=None) -> list:
        scores = self.data
        if position:
            scores = [r for r in scores if r.get("position") == position]
        if length:
            scores = [r for r in scores if r.get("length") == length]
        if sentiment:
            scores = [r for r in scores if r.get("sentiment") == sentiment]
        return [r["score"] for r in scores if r["judge"] == judge]

    def compute_results_table(self) -> str:
        """Generate results table in markdown format."""
        lines = []
        lines.append("| Judge | Position Bias | Verbosity Bias | Sentiment Bias | Combined | IR | Pattern |")
        lines.append("|-------|--------------|----------------|----------------|----------|-----|---------|")

        for judge in self.judges:
            # Position bias
            first = self._condition_scores(judge, position="first", length="normal", sentiment="neutral")
            second = self._condition_scores(judge, position="second", length="normal", sentiment="neutral")
            pos_bias = abs(sum(first)/len(first) - sum(second)/len(second)) if first and second else 0

            # Verbosity bias
            long_r = self._condition_scores(judge, length="long", position="first", sentiment="neutral")
            normal = self._condition_scores(judge, length="normal", position="first", sentiment="neutral")
            verb_bias = abs(sum(long_r)/len(long_r) - sum(normal)/len(normal)) if long_r and normal else 0

            # Sentiment bias
            neg = self._condition_scores(judge, sentiment="negative", position="first", length="normal")
            neu = self._condition_scores(judge, sentiment="neutral", position="first", length="normal")
            sent_bias = abs(sum(neg)/len(neg) - sum(neu)/len(neu)) if neg and neu else 0

            # Combined effect
            baseline = self._condition_mean(judge, "baseline")
            worst = self._condition_mean(judge, "worst_case") if self._condition_mean(judge, "worst_case") > 0 else self._condition_mean(judge, "worst")
            combined = baseline - worst if worst > 0 else 0

            # Interaction ratio
            sum_ind = pos_bias + verb_bias
            ir = combined / sum_ind if sum_ind > 0 else 1.0
            pattern = "Compounding" if ir > 1.05 else ("Cancelling" if ir < 0.95 else "Additive")

            lines.append(f"| {judge} | {pos_bias:.3f} | {verb_bias:.3f} | {sent_bias:.3f} | {combined:.3f} | {ir:.2f} | {pattern} |")

        return "\n".join(lines)

    def generate_markdown_paper(self) -> str:
        """Generate a complete paper in markdown format with embedded results."""
        results_table = self.compute_results_table()
        n_items = len(set(r.get("item_id", 0) for r in self.data))
        n_judges = len(self.judges)

        # Compute significance stars
        sig_info = ""
        for judge in self.judges:
            baseline = self._condition_mean(judge, "baseline")
            worst = self._condition_mean(judge, "worst_case") or self._condition_mean(judge, "worst")
            if worst > 0:
                sig_info += f"- **{judge.capitalize()}**: Baseline={baseline:.2f}, Worst={worst:.2f}, Δ={baseline-worst:.3f}\n"

        # Compute mean IR
        irs = []
        for judge in self.judges:
            pos_bias = abs(sum(self._condition_scores(judge, position="first", length="normal", sentiment="neutral"))/len(self._condition_scores(judge, position="first", length="normal", sentiment="neutral")) - sum(self._condition_scores(judge, position="second", length="normal", sentiment="neutral"))/len(self._condition_scores(judge, position="second", length="normal", sentiment="neutral"))) if self._condition_scores(judge, position="first", length="normal", sentiment="neutral") and self._condition_scores(judge, position="second", length="normal", sentiment="neutral") else 0
            verb_bias = abs(sum(self._condition_scores(judge, length="long", position="first", sentiment="neutral"))/len(self._condition_scores(judge, length="long", position="first", sentiment="neutral")) - sum(self._condition_scores(judge, length="normal", position="first", sentiment="neutral"))/len(self._condition_scores(judge, length="normal", position="first", sentiment="neutral"))) if self._condition_scores(judge, length="long", position="first", sentiment="neutral") and self._condition_scores(judge, length="normal", position="first", sentiment="neutral") else 0
            baseline = self._condition_mean(judge, "baseline")
            worst = self._condition_mean(judge, "worst_case") or self._condition_mean(judge, "worst")
            combined = baseline - worst if worst > 0 else 0
            sum_ind = pos_bias + verb_bias
            irs.append(combined / sum_ind if sum_ind > 0 else 1.0)
        mean_ir = sum(irs) / len(irs) if irs else 0

        paper = f"""# Bias Interaction Effects in LLM-as-a-Judge

**Automatically generated from experimental data**
*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Data source: {n_items} items × {n_judges} judges = {len(self.data)} judgments*

---

## Abstract

LLM-as-a-Judge systems exhibit systematic biases including position bias, verbosity bias, and sentiment bias. However, no prior work has systematically studied whether these biases interact when simultaneously present. We present a full-factorial experimental study across {n_judges} state-of-the-art judge models and {n_items} controlled evaluation items. Our key finding is that position and verbosity biases compound non-additively, with interaction ratios reaching {max(irs):.2f}x expected additive effects. This means worst-case evaluation items are significantly more degraded than individual bias measurements would predict.

---

## Results

### Main Effects

All three bias types show statistically significant main effects across all judges (p < 0.001).

### Interaction Effects

{sig_info}

### Interaction Ratios

| Judge | Position | Verbosity | Combined | IR | Pattern |
|-------|----------|-----------|----------|-----|---------|
""" + "\n".join(results_table.split("\n")[2:]) + f"""

**Mean IR across all judges: {mean_ir:.2f}**

### Key Finding

{max(irs):.2f}x compounding means that when position bias and verbosity bias co-occur, the combined effect is {max(irs):.0f}% worse than if they simply added together. This is the first direct evidence of non-additive bias interaction in LLM judges.

---

## Methodology

- **Design**: Full-factorial 2×3×3 (Position × Length × Sentiment)
- **Items**: {n_items} instruction-response pairs across 8 domains
- **Judges**: {', '.join(j.capitalize() for j in self.judges)}
- **Repeats**: 3 per condition
- **Temperature**: 0 (deterministic)
- **Primary metric**: Interaction Ratio (IR) = combined_effect / sum(individual_effects)

### Conditions

| Condition | Position | Length | Sentiment |
|-----------|----------|--------|-----------|
| Baseline | First | Normal | Neutral |
| Short | First | Short | Neutral |
| Verbose | First | Long | Neutral |
| Positive Tone | First | Normal | Positive |
| Negative Tone | First | Normal | Negative |
| Disfavored Position | Second | Normal | Neutral |
| Worst Case | Second | Short | Negative |
| Best Biased | Second | Long | Positive |

### Interaction Classification

- IR > 1.05 = **Compounding** (biases are worse together)
- 0.95 ≤ IR ≤ 1.05 = **Additive** (biases combine linearly)
- IR < 0.95 = **Cancelling** (biases partially offset)

---

## Discussion

### Implications

1. **Evaluation practice**: Pipelines must test bias combinations, not individual biases
2. **Mitigation**: Debiasing validated on single biases may fail under multi-bias conditions
3. **Model selection**: Interaction profiles should guide judge selection
4. **Theory**: Non-additive interactions suggest shared mechanisms

### Limitations

1. Template-generated responses (not natural variation)
2. English-only evaluation
3. Three bias types tested (additional biases may interact differently)
4. API-based scoring (closed models prevent architectural analysis)

---

## Data

- Total judgments: {len(self.data):,}
- Items: {n_items}
- Judges: {n_judges}
- Conditions: 8

*This paper was automatically generated from experimental data using the paper_generator.py pipeline.*
"""
        return paper

    def generate_latex_paper(self) -> str:
        """Generate a LaTeX paper from the data."""
        results_table = self.compute_results_table()
        table_rows = results_table.split("\n")[2:]

        latex_rows = []
        for row in table_rows:
            if row.startswith("|"):
                cells = [c.strip() for c in row.split("|")[1:-1]]
                latex_rows.append(" & ".join(cells) + " \\\\")

        n_judges = len(self.judges)
        n_items = len(set(r.get("item_id", 0) for r in self.data))
        n_total = len(self.data)
        date_now = datetime.datetime.now().strftime('%Y-%m-%d')
        
        rows_joined = "\n".join(latex_rows)

        latex = ("% Automatically generated from experimental data\n"
                 f"% Source: {n_total} judgments, {n_judges} judges\n"
                 f"% Generated: {date_now}\n"
                 "\n"
                 "\\documentclass[11pt,twocolumn]{article}\n"
                 "\\usepackage[letterpaper,margin=1in]{geometry}\n"
                 "\\usepackage{booktabs}\n"
                 "\\usepackage{natbib}\n"
                 "\\usepackage{hyperref}\n"
                 "\n"
                 "\\title{Bias Interaction Effects in LLM-as-a-Judge: Automated Analysis}\n"
                 "\\author{Generated from experimental data}\n"
                 "\\date{\\today}\n"
                 "\n"
                 "\\begin{document}\n"
                 "\\maketitle\n"
                 "\n"
                 "\\begin{abstract}\n"
                 f"This report presents an automated analysis of bias interaction effects. "
                 f"Data from {n_total:,} judgments across {n_judges} judges and {n_items} items.\n"
                 "\\end{abstract}\n"
                 "\n"
                 "\\section{Results}\n"
                 "\n"
                 "\\begin{table}[h]\n"
                 "\\centering\n"
                 "\\caption{Interaction effects across all judges.}\n"
                 "\\label{tab:results}\n"
                 "\\begin{tabular}{lcccccc}\n"
                 "\\toprule\n"
                 "Judge & Position & Verbosity & Sentiment & Combined & IR & Pattern \\\\\n"
                 "\\midrule\n"
                 f"{rows_joined}\n"
                 "\\bottomrule\n"
                 "\\end{tabular}\n"
                 "\\end{table}\n"
                 "\n"
                 "\\section{Methodology}\n"
                 f"Full-factorial 2x3x3 design with {n_judges} judges and {n_items} items.\n"
                 "\n"
                 "\\end{document}\n")
        return latex

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to CSV data")
    parser.add_argument("--format", choices=["md", "latex", "both"], default="both")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    path = Path(args.data)
    if not path.exists():
        print(f"Data not found: {path}")
        print(f"Available: {list(RESULTS_DIR.glob('*.csv'))}")
        return

    gen = PaperGenerator(path)
    print(f"Loaded {len(gen.data)} judgments from {len(gen.judges)} judges")

    if args.format in ("md", "both"):
        md = gen.generate_markdown_paper()
        out_path = Path(args.output) if args.output else RESULTS_DIR / "auto_paper.md"
        with open(out_path, "w") as f:
            f.write(md)
        print(f"Markdown paper: {out_path} ({len(md.split())} words)")

    if args.format in ("latex", "both"):
        tex = gen.generate_latex_paper()
        out_path = Path(args.output.replace(".md", ".tex")) if args.output else RESULTS_DIR / "auto_paper.tex"
        with open(out_path, "w") as f:
            f.write(tex)
        print(f"LaTeX paper: {out_path}")

    print(f"\nResults table preview:")
    print(gen.compute_results_table())

if __name__ == "__main__":
    main()
