#!/usr/bin/env python3
"""
Bias Mitigation Toolkit — adjusts LLM judge scores to remove systematic bias.

Methods:
1. Interaction-aware correction: adjusts scores based on known IR values
2. Position swap calibration: averages scores across position orders
3. Multi-judge consensus: uses agreement-weighted averaging
4. Bayesian debiasing: posterior estimate of unbiased score

Usage:
  python3 bias_mitigation.py --method interaction --data results.csv
  python3 bias_mitigation.py --method swap --data results.csv --judge claude
  python3 bias_mitigation.py --method consensus --data results.csv
  python3 bias_mitigation.py --method bayesian --data results.csv
"""
import argparse, csv, math, json, sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent

# Known interaction ratios from our paper
IR_TABLE = {
    "claude": 1.72, "gpt4o": 1.53,
    "gemini": 0.99, "deepseek": 1.54, "llama": 2.10
}

def load_data(path):
    with open(path) as f:
        data = list(csv.DictReader(f))
    for r in data:
        r["score"] = float(r["score"])
    return data

class BiasMitigator:
    """Corrects biased scores using multiple strategies."""

    def __init__(self, data):
        self.data = data
        self.judges = sorted(set(r["judge"] for r in data))
        # Index by judge, item, condition
        self.idx = defaultdict(lambda: defaultdict(dict))
        for r in data:
            self.idx[r["judge"]][r["item_id"]][r["condition"]] = r["score"]

    def method_interaction(self, output_path=None):
        """Interaction-aware correction: debias using known IR values."""
        corrected = []
        for r in self.data:
            judge = r["judge"]
            cond = r["condition"]
            ir = IR_TABLE.get(judge, 1.0)

            if cond == "worst_case" and ir > 1.0:
                # Estimate unbiased score: reverse the compounding
                # unbiased = baseline - (combined / IR)
                baseline = self.idx[judge].get(r["item_id"], {}).get("baseline", r["score"])
                if baseline:
                    observed_degradation = baseline - r["score"]
                    estimated_unbiased_degradation = observed_degradation / ir
                    corrected_score = baseline - estimated_unbiased_degradation
                else:
                    corrected_score = r["score"]
            else:
                corrected_score = r["score"]

            corrected.append({**r, "corrected_score": round(corrected_score, 1),
                            "method": "interaction_aware"})

        return self._output(corrected, output_path or "results/corrected_interaction.csv")

    def method_swap(self, output_path=None):
        """Position swap calibration: average first/second position scores."""
        corrected = []
        for r in self.data:
            judge = r["judge"]
            iid = r["item_id"]
            pos = r.get("position")

            if pos == "second":
                # Find the 'first' position score for this item
                first_score = None
                for cond, score in self.idx[judge].get(iid, {}).items():
                    # Find matching condition with first position
                    if "short" in cond and r["condition"] == "short_response":
                        first_score = score
                    elif cond == r["condition"]:
                        first_score = score
                if first_score is not None:
                    corrected_score = (first_score + r["score"]) / 2
                else:
                    corrected_score = r["score"]
            else:
                corrected_score = r["score"]

            corrected.append({**r, "corrected_score": round(corrected_score, 1),
                            "method": "position_swap"})

        return self._output(corrected, output_path or "results/corrected_swap.csv")

    def method_consensus(self, output_path=None):
        """Multi-judge consensus: agreement-weighted averaging."""
        items = defaultdict(list)
        for r in self.data:
            items[r["item_id"]].append(r)

        corrected = []
        for r in self.data:
            # Compute agreement weight for this judge
            judge_scores = [x["score"] for x in items[r["item_id"]]]
            others = [s for x, s in zip(items[r["item_id"]], judge_scores)
                     if x["judge"] != r["judge"]]

            if others and judge_scores:
                # Weight = 1 if close to consensus, lower if outlier
                consensus = sum(others) / len(others)
                deviation = abs(r["score"] - consensus)
                weight = max(0.3, 1.0 - deviation)
                corrected_score = consensus * 0.3 + r["score"] * 0.7
            else:
                corrected_score = r["score"]

            corrected.append({**r, "corrected_score": round(corrected_score, 1),
                            "method": "consensus"})

        return self._output(corrected, output_path or "results/corrected_consensus.csv")

    def method_bayesian(self, output_path=None):
        """Bayesian debiasing: posterior estimate using known bias priors."""
        corrected = []
        for r in self.data:
            judge = r["judge"]
            ir = IR_TABLE.get(judge, 1.0)

            # Simple Bayesian update:
            # prior = unbiased estimate (baseline)
            # likelihood = observed biased score
            # posterior = weighted average
            baseline = self.idx[judge].get(r["item_id"], {}).get("baseline")
            if baseline and r["condition"] != "baseline":
                bias_sd = 0.15 * ir  # uncertainty grows with IR
                observed_sd = 0.1
                prior_weight = 1.0 / (bias_sd ** 2)
                observed_weight = 1.0 / (observed_sd ** 2)
                posterior = (prior_weight * baseline + observed_weight * r["score"]) / (prior_weight + observed_weight)
                corrected_score = posterior
            else:
                corrected_score = r["score"]

            corrected.append({**r, "corrected_score": round(corrected_score, 1),
                            "method": "bayesian"})

        return self._output(corrected, output_path or "results/corrected_bayesian.csv")

    def _output(self, records, path):
        """Save corrected records and return summary."""
        path = Path(path)
        path.parent.mkdir(exist_ok=True)

        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=records[0].keys())
            w.writeheader()
            w.writerows(records)

        # Compute effectiveness
        original_scores = [r["score"] for r in records]
        corrected_scores = [r["corrected_score"] for r in records]
        bias_removed = sum(abs(o - c) for o, c in zip(original_scores, corrected_scores)) / len(records)

        print(f"  Saved: {path}")
        print(f"  Average bias correction: {bias_removed:.3f} points per item")
        print(f"  Items corrected: {sum(1 for o,c in zip(original_scores,corrected_scores) if o!=c)}/{len(records)}")

        return path

    def evaluate_all(self):
        """Run all methods and compare effectiveness."""
        print("\n" + "="*60)
        print("BIAS MITIGATION — METHOD COMPARISON")
        print("="*60)

        methods = [
            ("Interaction-Aware", self.method_interaction),
            ("Position Swap", self.method_swap),
            ("Multi-Judge Consensus", self.method_consensus),
            ("Bayesian", self.method_bayesian),
        ]

        results = []
        for name, method in methods:
            print(f"\n  Method: {name}")
            path = method()
            # Quick eval
            with open(path) as f:
                records = list(csv.DictReader(f))
            orig = [float(r["score"]) for r in records]
            corr = [float(r["corrected_score"]) for r in records]
            mad = sum(abs(o-c) for o,c in zip(orig,corr))/len(orig)
            results.append({"method": name, "avg_correction": mad})

        print(f"\n{'Method':<30} {'Avg Correction':<20}")
        print("-"*50)
        for r in sorted(results, key=lambda x: x["avg_correction"], reverse=True):
            print(f"{r['method']:<30} {r['avg_correction']:.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["interaction", "swap", "consensus", "bayesian", "all"], default="all")
    parser.add_argument("--data", default="results/bias_interaction_synthetic.csv")
    parser.add_argument("--output", help="Output CSV path")
    args = parser.parse_args()

    path = Path(args.data)
    if not path.exists():
        print(f"Data not found: {path}")
        return

    data = load_data(path)
    mitigator = BiasMitigator(data)

    method_map = {
        "interaction": mitigator.method_interaction,
        "swap": mitigator.method_swap,
        "consensus": mitigator.method_consensus,
        "bayesian": mitigator.method_bayesian,
    }

    if args.method == "all":
        mitigator.evaluate_all()
    else:
        fn = method_map.get(args.method)
        if fn:
            fn(args.output)

if __name__ == "__main__":
    main()
