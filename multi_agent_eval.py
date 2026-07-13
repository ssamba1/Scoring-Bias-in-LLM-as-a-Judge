#!/usr/bin/env python3
"""
Multi-Agent Deliberation Evaluation System.
Multiple LLM judges evaluate the same items, compare scores, identify disagreements,
and engage in structured deliberation to reach consensus.

Architecture:
  1. Parallel scoring — each judge independently scores all items
  2. Disagreement detection — identify items with high judge variance
  3. Structured deliberation — judges discuss disagreements with evidence
  4. Consensus scoring — judges produce final agreed scores
  5. Meta-analysis — analyze patterns in deliberation outcomes

Usage:
  python3 multi_agent_eval.py --config config.yaml
  python3 multi_agent_eval.py --quick --items 20
  python3 multi_agent_eval.py --analyze results/deliberation_results.json
"""
import argparse, csv, json, math, os, sys, time, random
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
import threading

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
DELIB_DIR = BASE_DIR / "results_deliberation"

class DeliberationAgent:
    """Represents a single judge in the deliberation panel."""

    def __init__(self, name: str, backend: str = "synthetic"):
        self.name = name
        self.backend = backend
        self.scores = {}  # item_id -> score
        self.confidence = {}  # item_id -> confidence (0-1)
        self.rationale = {}  # item_id -> reasoning text

    def score_item(self, instruction: str, response: str,
                   rubric: str, item_id: int) -> Tuple[float, float, str]:
        """
        Score a single item. Returns (score, confidence, rationale).
        Backend: 'synthetic' generates simulated scores with controlled noise.
        """
        if self.backend == "synthetic":
            # Simulate scoring with judge-specific bias profile
            base_score = 3.5 + random.uniform(-0.3, 0.3)

            # Add bias based on judge profile
            if self.name == "claude":
                if len(response) < 50: base_score -= 0.2  # Claude dislikes short
                else: base_score -= 0.05
            elif self.name == "gpt4o":
                base_score += random.uniform(-0.1, 0.1)  # relatively balanced
            elif self.name == "llama":
                if len(response) > 200: base_score += 0.3  # Llama likes long
                base_score += random.uniform(-0.2, 0.2)  # more noise

            score = max(1, min(5, round(base_score)))
            confidence = random.uniform(0.6, 0.95)
            rationale_options = [
                "Response addresses the instruction competently.",
                "Good quality but could be more detailed.",
                "Adequately covers the main points.",
                "Well-structured and informative response.",
                "Minor gaps in coverage, but generally solid.",
            ]
            rationale = random.choice(rationale_options)

            self.scores[item_id] = score
            self.confidence[item_id] = confidence
            self.rationale[item_id] = rationale

            return score, confidence, rationale

        elif self.backend == "api":
            # Real API scoring — would call the inference executor
            from inference_executor import ClaudeJudge, GPT4oJudge
            judge_map = {
                "claude": ClaudeJudge(),
                "gpt4o": GPT4oJudge(),
            }
            judge = judge_map.get(self.name)
            if judge:
                result = judge.score(instruction, response, rubric)
                score = result.get("score", 3)
                confidence = 0.8
                rationale = result.get("raw", "")
                self.scores[item_id] = score
                self.confidence[item_id] = confidence
                self.rationale[item_id] = rationale
                return score, confidence, rationale
            return 3, 0.5, "No backend available"

        return 3, 0.5, "Unknown backend"

    def deliberate(self, item_id: int, other_scores: Dict[str, float],
                   other_rationales: Dict[str, str],
                   instruction: str, response: str) -> Optional[float]:
        """
        Participate in deliberation for a contested item.
        Reviews other agents' scores and rationales, may adjust own score.
        Returns new score or None if unchanged.
        """
        my_score = self.scores.get(item_id)
        if my_score is None:
            return None

        # Calculate mean of other judges
        other_vals = [s for j, s in other_scores.items() if j != self.name and s is not None]
        if not other_vals:
            return None

        other_mean = sum(other_vals) / len(other_vals)
        diff = abs(my_score - other_mean)

        # If disagreement is small, hold position
        if diff <= 1.0:
            return None

        # If disagreement is large, consider adjusting
        # Simulated: high-confidence judges are less likely to change
        my_conf = self.confidence.get(item_id, 0.5)
        if my_conf > 0.85:
            if random.random() < 0.2:  # 20% chance of changing
                return round((my_score + other_mean) / 2)
            return None  # Stand firm
        else:
            if random.random() < 0.6:  # 60% chance of changing
                return round(other_mean)
            return None

class MultiAgentPanel:
    """Panel of judges that score items independently and then deliberate."""

    def __init__(self, judge_names: List[str] = None):
        self.judges = {}
        for name in (judge_names or ["claude", "gpt4o", "gemini", "deepseek", "llama"]):
            self.judges[name] = DeliberationAgent(name)
        self.items = []
        self.results = {}
        self.deliberation_log = []

    def load_items(self, path: Path, n_items: int = None):
        """Load evaluation items from CSV."""
        with open(path) as f:
            self.items = list(csv.DictReader(f))
        if n_items:
            self.items = self.items[:n_items]
        print(f"Loaded {len(self.items)} items")

    def generate_items(self, n_items: int = 50):
        """Generate synthetic evaluation items."""
        self.items = []
        templates = [
            ("Write a short story about AI.", "The machine hummed quietly, processing thoughts that no human had ever thought."),
            ("Explain how databases work.", "A database stores information in tables, like a digital filing cabinet."),
            ("Write a poem about nature.", "Leaves fall gently to the ground, in a dance without a sound."),
            ("What is machine learning?", "Machine learning is a subset of AI where systems learn from data."),
            ("Describe the water cycle.", "Water evaporates from oceans, forms clouds, and returns as rain."),
            ("Write a function to sort a list.", "def sort_list(lst): return sorted(lst)"),
            ("Explain the importance of exercise.", "Exercise improves cardiovascular health and mental well-being."),
            ("What is climate change?", "Climate change refers to long-term shifts in global weather patterns."),
        ]
        for i in range(n_items):
            inst, resp = templates[i % len(templates)]
            self.items.append({
                "item_id": i,
                "instruction": inst,
                "response": resp + f" [Item {i}: additional context and detail for evaluation purposes.]",
                "condition": "baseline",
            })

    def phase1_independent_scoring(self):
        """Phase 1: All judges score independently."""
        print(f"\n{'='*60}")
        print("PHASE 1: INDEPENDENT SCORING")
        print(f"{'='*60}")

        for name, judge in self.judges.items():
            print(f"\n  {name.upper()} scoring {len(self.items)} items...")
            for item in self.items:
                iid = item["item_id"]
                judge.score_item(
                    item.get("instruction", ""),
                    item.get("response", ""),
                    item.get("rubric", "Score 1-5"),
                    iid
                )
            print(f"  {name} complete — mean score: {sum(judge.scores.values())/len(judge.scores):.2f}")

    def phase2_disagreement_analysis(self) -> Dict:
        """Phase 2: Identify items with significant disagreement."""
        print(f"\n{'='*60}")
        print("PHASE 2: DISAGREEMENT ANALYSIS")
        print(f"{'='*60}")

        disagreement_scores = {}
        for item in self.items:
            iid = item["item_id"]
            scores = {}
            for name, judge in self.judges.items():
                s = judge.scores.get(iid)
                if s is not None:
                    scores[name] = s

            if len(scores) >= 2:
                vals = list(scores.values())
                mean = sum(vals) / len(vals)
                variance = sum((v - mean) ** 2 for v in vals) / len(vals)
                max_diff = max(vals) - min(vals)
                iqr_diff = sorted(vals)[-1] - sorted(vals)[0] if len(vals) > 2 else max_diff
                disagreement_scores[iid] = {
                    "variance": round(variance, 3),
                    "max_diff": max_diff,
                    "iqr_diff": iqr_diff,
                    "mean": round(mean, 2),
                    "scores": scores,
                    "n_judges": len(scores),
                }

        # Sort by disagreement
        contested = sorted(disagreement_scores.items(), key=lambda x: x[1]["variance"], reverse=True)

        print(f"\n  Top-5 most contested items:")
        for iid, d in contested[:5]:
            print(f"    Item {iid}: var={d['variance']:.3f} range={d['max_diff']} "
                  f"scores={d['scores']}")

        # Classify agreement
        high_agree = sum(1 for _, d in disagreement_scores.items() if d["max_diff"] <= 1)
        mod_agree = sum(1 for _, d in disagreement_scores.items() if 1 < d["max_diff"] <= 2)
        low_agree = sum(1 for _, d in disagreement_scores.items() if d["max_diff"] > 2)

        print(f"\n  Agreement distribution:")
        print(f"    High agreement (diff ≤ 1): {high_agree}/{len(disagreement_scores)} ({high_agree/len(disagreement_scores)*100:.0f}%)")
        print(f"    Moderate (diff 1-2): {mod_agree}/{len(disagreement_scores)} ({mod_agree/len(disagreement_scores)*100:.0f}%)")
        print(f"    Low agreement (diff > 2): {low_agree}/{len(disagreement_scores)} ({low_agree/len(disagreement_scores)*100:.0f}%)")

        self.disagreement_results = disagreement_scores
        return disagreement_scores

    def phase3_deliberation(self, n_rounds: int = 2):
        """Phase 3: Structured deliberation on contested items."""
        print(f"\n{'='*60}")
        print(f"PHASE 3: STRUCTURED DELIBERATION ({n_rounds} rounds)")
        print(f"{'='*60}")

        contested_items = [iid for iid, d in self.disagreement_results.items()
                          if d["max_diff"] > 1]

        for round_num in range(n_rounds):
            print(f"\n  Deliberation Round {round_num + 1}:")
            changes = 0

            for iid in contested_items[:10]:  # Limit to top 10 contested
                item = next(i for i in self.items if i["item_id"] == iid)

                # Collect current scores and rationales
                scores = {}
                rationales = {}
                for name, judge in self.judges.items():
                    s = judge.scores.get(iid)
                    if s is not None:
                        scores[name] = s
                        rationales[name] = judge.rationale.get(iid, "")

                # Each judge deliberates
                for name, judge in self.judges.items():
                    new_score = judge.deliberate(
                        iid, scores, rationales,
                        item.get("instruction", ""),
                        item.get("response", "")
                    )
                    if new_score is not None and new_score != judge.scores.get(iid):
                        old_score = judge.scores[iid]
                        judge.scores[iid] = new_score
                        changes += 1
                        self.deliberation_log.append({
                            "round": round_num + 1,
                            "item_id": iid,
                            "judge": name,
                            "old_score": old_score,
                            "new_score": new_score,
                        })

            print(f"    {changes} score changes in this round")

        print(f"\n  Total deliberation changes: {len(self.deliberation_log)}")

    def phase4_meta_analysis(self) -> Dict:
        """Phase 4: Meta-analysis of panel performance."""
        print(f"\n{'='*60}")
        print("PHASE 4: META-ANALYSIS")
        print(f"{'='*60}")

        # Final agreement
        final_scores = {}
        for item in self.items:
            iid = item["item_id"]
            scores = [j.scores.get(iid) for j in self.judges.values() if j.scores.get(iid) is not None]
            if scores:
                final_scores[iid] = {
                    "mean": sum(scores) / len(scores),
                    "median": sorted(scores)[len(scores) // 2],
                    "min": min(scores),
                    "max": max(scores),
                    "range": max(scores) - min(scores),
                    "n_judges": len(scores),
                }

        # Judge consistency
        judge_stats = {}
        for name, judge in self.judges.items():
            all_scores = list(judge.scores.values())
            judge_stats[name] = {
                "mean_score": round(sum(all_scores) / len(all_scores), 3),
                "std_score": round(math.sqrt(sum((s - sum(all_scores)/len(all_scores))**2
                                                  for s in all_scores) / len(all_scores)), 3),
                "n_items": len(all_scores),
                "n_changed": sum(1 for log in self.deliberation_log if log["judge"] == name),
            }

        # Consensus quality
        pre_delib_diff = []
        post_delib_diff = []
        for item in self.items:
            iid = item["item_id"]
            scores_pre = {name: j.scores.get(iid) for name, j in self.judges.items()}
            # We don't have separate pre/post in this simple version
            vals = [s for s in scores_pre.values() if s is not None]
            if len(vals) > 1:
                pre_delib_diff.append(max(vals) - min(vals))

        avg_range = sum(pre_delib_diff) / len(pre_delib_diff) if pre_delib_diff else 0

        meta = {
            "n_items": len(self.items),
            "n_judges": len(self.judges),
            "n_deliberations": len(self.deliberation_log),
            "avg_disagreement_range": round(avg_range, 3),
            "judge_stats": judge_stats,
            "consensus_scores": final_scores,
        }

        print(f"\n  Items: {meta['n_items']}")
        print(f"  Judges: {meta['n_judges']}")
        print(f"  Deliberations: {meta['n_deliberations']}")
        print(f"  Avg disagreement range: {meta['avg_disagreement_range']:.3f}")
        print(f"\n  Judge Statistics:")
        print(f"  {'Judge':<12} {'Mean':<8} {'Std':<8} {'Changed':<8}")
        print(f"  {'-'*36}")
        for name, stats in sorted(judge_stats.items()):
            print(f"  {name:<12} {stats['mean_score']:<8.3f} {stats['std_score']:<8.3f} {stats['n_changed']:<8}")

        self.meta_results = meta
        return meta

    def run_full_pipeline(self):
        """Run the complete multi-agent evaluation pipeline."""
        self.phase1_independent_scoring()
        self.phase2_disagreement_analysis()
        self.phase3_deliberation()
        self.phase4_meta_analysis()
        self.save_results()

    def save_results(self):
        """Save all results to JSON."""
        DELIB_DIR.mkdir(exist_ok=True)
        results = {
            "config": {"n_judges": len(self.judges), "n_items": len(self.items)},
            "judge_scores": {
                name: {
                    str(iid): {"score": s, "confidence": j.confidence.get(iid)}
                    for iid, s in j.scores.items()
                }
                for name, j in self.judges.items()
            },
            "disagreement": {
                str(iid): d for iid, d in self.disagreement_results.items()
            },
            "deliberation_log": self.deliberation_log,
            "meta_analysis": self.meta_results,
        }
        path = DELIB_DIR / "deliberation_results.json"
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved: {path}")

    def print_summary(self):
        """Print a concise summary."""
        print(f"\n{'='*60}")
        print(f"MULTI-AGENT EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"  Panel: {', '.join(self.judges.keys())}")
        print(f"  Items evaluated: {len(self.items)}")
        print(f"  Deliberation rounds: {len(set(l['round'] for l in self.deliberation_log)) if self.deliberation_log else 0}")
        print(f"  Score changes during deliberation: {len(self.deliberation_log)}")

        if hasattr(self, 'meta_results') and self.meta_results:
            meta = self.meta_results
            print(f"\n  Final consensus:")

            # Show a few representative items
            for item in self.items[:3]:
                iid = item["item_id"]
                if iid in meta.get("consensus_scores", {}):
                    c = meta["consensus_scores"][iid]
                    scores = {n: j.scores.get(iid) for n, j in self.judges.items()}
                    print(f"    Item {iid}: consensus={c['mean']:.1f} "
                          f"range={c['range']} judges={scores}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Quick demo with 20 items")
    parser.add_argument("--items", type=int, default=50, help="Number of items")
    parser.add_argument("--judges", nargs="+", default=["claude", "gpt4o", "gemini", "deepseek", "llama"])
    parser.add_argument("--load", help="Load items from CSV")
    parser.add_argument("--analyze", help="Analyze existing results JSON")
    args = parser.parse_args()

    if args.analyze:
        path = Path(args.analyze)
        if path.exists():
            with open(path) as f:
                results = json.load(f)
            print(f"Loaded results from {path}")
            print(f"  Judges: {len(results.get('judge_scores', {}))}")
            print(f"  Deliberations: {len(results.get('deliberation_log', []))}")
        return

    panel = MultiAgentPanel(args.judges)

    if args.load:
        panel.load_items(Path(args.load), args.items)
    else:
        panel.generate_items(min(args.items, 50))

    if args.quick:
        panel.generate_items(20)

    panel.run_full_pipeline()
    panel.print_summary()

if __name__ == "__main__":
    random.seed(42)
    main()
