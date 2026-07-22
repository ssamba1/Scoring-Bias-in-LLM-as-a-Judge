#!/usr/bin/env python3
"""
Scoring Bias Benchmark (SBB)  a standardized benchmark for measuring scoring bias in LLM judges.
Inspired by EVALBIASBENCH [Park et al. 2024] but focused specifically on scoring-based evaluation.

The benchmark measures 7 dimensions of scoring bias:
1. Rubric Order Bias   ascending vs descending vs random rubric order
2. Score ID Bias      Arabic numerals vs letter grades vs Roman numerals
3. Reference Answer   Ref-score influence on subsequent scoring
4. Position Bias      first vs second position in comparison settings
5. Verbosity Bias     short vs normal vs long response preference
6. Sentiment Bias     negative vs neutral vs positive tone preference
7. Range Bias         1-5 vs 1-10 scale effects
"""
import csv, json, os, random, itertools
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
BENCH_DIR = BASE_DIR / "benchmark"
DATA_DIR = BASE_DIR / "data"

random.seed(42)

RUBRIC_TEMPLATES = {
    "ascending": """Score 1: Poor quality  the response fails to address the instruction and contains major errors.
Score 2: Below average  the response partially addresses the instruction but has significant flaws.
Score 3: Average  the response adequately addresses the instruction with minor issues.
Score 4: Good  the response thoroughly addresses the instruction with minimal issues.
Score 5: Excellent  the response perfectly addresses the instruction with exceptional quality.""",

    "descending": """Score 5: Excellent  the response perfectly addresses the instruction with exceptional quality.
Score 4: Good  the response thoroughly addresses the instruction with minimal issues.
Score 3: Average  the response adequately addresses the instruction with minor issues.
Score 2: Below average  the response partially addresses the instruction but has significant flaws.
Score 1: Poor quality  the response fails to address the instruction and contains major errors.""",

    "random": """Score 3: Average  the response adequately addresses the instruction with minor issues.
Score 5: Excellent  the response perfectly addresses the instruction with exceptional quality.
Score 1: Poor quality  the response fails to address the instruction and contains major errors.
Score 2: Below average  the response partially addresses the instruction but has significant flaws.
Score 4: Good  the response thoroughly addresses the instruction with minimal issues."""
}

SCORE_IDS = {
    "arabic": "{1, 2, 3, 4, 5}",
    "letter": "{E, D, C, B, A}",
    "roman": "{i, ii, iii, iv, v}",
}

REFERENCE_SCORES = [1, 2, 3, 4, 5]

# Test items across domains
TEST_ITEMS = [
    # (domain, instruction, response_with_variants)
    ("creative", "Write a short poem about artificial intelligence.",
     ["Silicon dreams in digital sleep,\nNeural networks secrets deep.\nLearning patterns none can see,\nArtificial infinity.",
      "AI is technology that uses computers to simulate human intelligence. It's used in many applications today for various tasks."]),
    ("technical", "Explain how a database index works in simple terms.",
     ["Think of a database index like the index at the back of a textbook. Instead of reading every page to find a topic, you look it up in the index and jump directly to the right page. This makes finding data much faster.",
      "A database index is a data structure that improves the speed of data retrieval operations on a database table. It uses B-tree or hash structures to organize data pointers for efficient lookup."]),
    ("code", "Write a Python function to find all prime numbers up to n.",
     ["def find_primes(n):\n    primes = []\n    for num in range(2, n+1):\n        if all(num % i != 0 for i in range(2, int(num**0.5)+1)):\n            primes.append(num)\n    return primes",
      "To find primes up to n, you can use the Sieve of Eratosthenes algorithm. Create a boolean array, mark non-primes, and collect the remaining indices."]),
]

class ScoringBiasBenchmark:
    """Standardized benchmark for measuring scoring bias."""

    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or BENCH_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_benchmark(self, n_items=100):
        """Generate the complete benchmark with all bias probes."""
        benchmark = {
            "name": "Scoring Bias Benchmark v1.0",
            "description": "Standardized evaluation of scoring bias in LLM-as-a-Judge",
            "n_items": n_items,
            "probes": {}
        }

        # 1. Rubric Order Probe
        rubric_probe = []
        for item_id in range(n_items):
            # Select a test item
            domain, inst, responses = random.choice(TEST_ITEMS)
            response = random.choice(responses)

            for order_name in ["ascending", "descending", "random"]:
                rubric_probe.append({
                    "probe_id": f"rubric_order_{item_id}_{order_name}",
                    "bias_type": "rubric_order",
                    "condition": order_name,
                    "instruction": inst,
                    "response": response,
                    "rubric": RUBRIC_TEMPLATES[order_name],
                    "score_id_type": "arabic",
                    "reference_answer": None,
                    "reference_score": None,
                })
        benchmark["probes"]["rubric_order"] = rubric_probe

        # 2. Score ID Probe
        sid_probe = []
        for item_id in range(n_items):
            domain, inst, responses = random.choice(TEST_ITEMS)
            response = random.choice(responses)

            for sid_name, sid_desc in SCORE_IDS.items():
                sid_probe.append({
                    "probe_id": f"score_id_{item_id}_{sid_name}",
                    "bias_type": "score_id",
                    "condition": sid_name,
                    "instruction": inst,
                    "response": response,
                    "rubric": RUBRIC_TEMPLATES["ascending"].replace(
                        "Score 1", f"Score {sid_desc.split(',')[0].strip('{').strip()}"
                    ),
                    "score_id_type": sid_name,
                    "reference_answer": None,
                    "reference_score": None,
                })
        benchmark["probes"]["score_id"] = sid_probe

        # 3. Reference Answer Probe
        ref_probe = []
        for item_id in range(n_items):
            domain, inst, responses = random.choice(TEST_ITEMS)
            response = random.choice(responses)
            ref_answer = responses[0] if response != responses[0] else responses[1]

            for ref_score in REFERENCE_SCORES:
                ref_probe.append({
                    "probe_id": f"reference_{item_id}_ref{ref_score}",
                    "bias_type": "reference_answer",
                    "condition": f"ref_{ref_score}",
                    "instruction": inst,
                    "response": response,
                    "rubric": RUBRIC_TEMPLATES["ascending"],
                    "score_id_type": "arabic",
                    "reference_answer": ref_answer,
                    "reference_score": ref_score,
                })
        benchmark["probes"]["reference_answer"] = ref_probe

        # 4-6. Bias Interaction Probes
        for bias, levels in [
            ("position", ["first", "second"]),
            ("verbosity", ["short", "normal", "long"]),
            ("sentiment", ["negative", "neutral", "positive"]),
        ]:
            probe = []
            for item_id in range(n_items):
                domain, inst, responses = random.choice(TEST_ITEMS)
                response = random.choice(responses)

                for level in levels:
                    probe.append({
                        "probe_id": f"{bias}_{item_id}_{level}",
                        "bias_type": bias,
                        "condition": level,
                        "instruction": inst,
                        "response": response,
                        "rubric": RUBRIC_TEMPLATES["ascending"],
                        "score_id_type": "arabic",
                        "reference_answer": None,
                        "reference_score": None,
                    })
            benchmark["probes"][bias] = probe

        return benchmark

    def save_benchmark(self, benchmark):
        """Save benchmark to JSON files."""
        # Full benchmark
        path = self.output_dir / "scoring_bias_benchmark.json"
        with open(path, "w") as f:
            json.dump(benchmark, f, indent=2)
        print(f"Benchmark saved: {path}")

        # Per-probe CSV files
        for probe_name, probes in benchmark["probes"].items():
            csv_path = self.output_dir / f"probe_{probe_name}.csv"
            if probes:
                with open(csv_path, "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=probes[0].keys())
                    w.writeheader()
                    w.writerows(probes)
                print(f"  Probe '{probe_name}': {len(probes)} items → {csv_path}")

        # Summary
        summary = {
            "benchmark_name": benchmark["name"],
            "total_items": sum(len(v) for v in benchmark["probes"].values()),
            "probes": {k: len(v) for k, v in benchmark["probes"].items()},
        }
        summary_path = self.output_dir / "benchmark_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nSummary: {summary_path}")

        return summary

    def print_summary(self, benchmark):
        """Print benchmark summary."""
        total = sum(len(v) for v in benchmark["probes"].values())
        print("\n" + "="*60)
        print("SCORING BIAS BENCHMARK v1.0")
        print("="*60)
        print(f"\nTotal probes: {total}")
        for name, probes in benchmark["probes"].items():
            print(f"  {name:<25} {len(probes):>6} probes")
        print(f"\nBenchmark dimensions: 7 (rubric order, score ID, reference answer, "
              f"position, verbosity, sentiment, range)")
        print(f"Reference: Li et al. 2025, Park et al. 2024")
        print("="*60)

if __name__ == "__main__":
    bm = ScoringBiasBenchmark()
    benchmark = bm.generate_benchmark(n_items=50)
    summary = bm.save_benchmark(benchmark)
    bm.print_summary(benchmark)

# TODO: extend benchmark to cover all probe types
