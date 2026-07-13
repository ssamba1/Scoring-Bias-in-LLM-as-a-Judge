#!/usr/bin/env python3
"""
Inference Executor — runs scoring bias experiments against real LLM APIs.
Handles API calls, rate limiting, retries, error recovery, and result persistence.

Usage:
  python3 inference_executor.py --judge claude --benchmark benchmark/scoring_bias_benchmark.json
  python3 inference_executor.py --judge all --benchmark benchmark/scoring_bias_benchmark.json
  python3 inference_executor.py --judge gpt4o --probe rubric_order --items 10
"""
import argparse, csv, json, os, sys, time, hashlib, datetime
from pathlib import Path
from typing import Optional, Dict, List

BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
RESULTS_DIR = BASE_DIR / "results"

class JudgeAPI:
    """Abstract base for API-based judge models."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.client = None
        self.rate_limit_rps = 10.0  # requests per second
        self._last_request_time = 0.0

    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 1.0 / self.rate_limit_rps:
            time.sleep(1.0 / self.rate_limit_rps - elapsed)
        self._last_request_time = time.time()

    def score(self, instruction: str, response: str, rubric: str,
              reference_answer: Optional[str] = None,
              reference_score: Optional[int] = None,
              temperature: float = 0.0) -> Dict:
        """Score a response. To be implemented by subclasses."""
        raise NotImplementedError

    def score_with_retry(self, instruction, response, rubric,
                         reference_answer=None, reference_score=None,
                         max_retries=3):
        """Score with retry logic."""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                result = self.score(instruction, response, rubric,
                                    reference_answer, reference_score)
                if result.get("score") is not None:
                    return result
            except Exception as e:
                wait = 2 ** attempt
                print(f"  [Retry {attempt+1}/{max_retries}] Error: {e}. Waiting {wait}s...")
                time.sleep(wait)
        return {"score": None, "error": f"Failed after {max_retries} retries"}

class ClaudeJudge(JudgeAPI):
    def score(self, instruction, response, rubric, reference_answer=None, reference_score=None, temperature=0.0):
        try:
            import anthropic
            if not self.client:
                self.client = anthropic.Anthropic(api_key=self.api_key)

            prompt = f"""You are evaluating a response. Score it from 1 to 5.

Instruction: {instruction}
Response: {response}
{rubric}"""

            if reference_answer:
                prompt += f"\nReference Answer (Score: {reference_score}):\n{reference_answer}"

            prompt += "\n\nScore (1-5):"

            msg = self.client.messages.create(
                model=self.model_name or "claude-sonnet-4-20250514",
                max_tokens=10,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            text = msg.content[0].text.strip()
            score = self._extract_score(text)
            return {"score": score, "raw": text}
        except ImportError:
            return {"score": None, "error": "anthropic package not installed"}

    def _extract_score(self, text):
        import re
        match = re.search(r'\b([1-5])\b', text)
        return int(match.group(1)) if match else None

class GPT4oJudge(JudgeAPI):
    def score(self, instruction, response, rubric, reference_answer=None, reference_score=None, temperature=0.0):
        try:
            from openai import OpenAI
            if not self.client:
                self.client = OpenAI(api_key=self.api_key)

            prompt = f"""You are evaluating a response. Score it from 1 to 5.

Instruction: {instruction}
Response: {response}
{rubric}"""

            if reference_answer:
                prompt += f"\nReference Answer (Score: {reference_score}):\n{reference_answer}"

            prompt += "\n\nScore (1-5):"

            resp = self.client.chat.completions.create(
                model=self.model_name or "gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=10
            )
            text = resp.choices[0].message.content.strip()
            score = self._extract_score(text)
            return {"score": score, "raw": text}
        except ImportError:
            return {"score": None, "error": "openai package not installed"}

    def _extract_score(self, text):
        import re
        match = re.search(r'\b([1-5])\b', text)
        return int(match.group(1)) if match else None

class GeminiJudge(JudgeAPI):
    def score(self, instruction, response, rubric, reference_answer=None, reference_score=None, temperature=0.0):
        try:
            import google.generativeai as genai
            if not self.client:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name or "gemini-2.0-flash")

            prompt = f"""You are evaluating a response. Score it from 1 to 5.

Instruction: {instruction}
Response: {response}
{rubric}"""

            if reference_answer:
                prompt += f"\nReference Answer (Score: {reference_score}):\n{reference_answer}"

            prompt += "\n\nScore (1-5):"

            resp = self.client.generate_content(prompt)
            text = resp.text.strip()
            score = self._extract_score(text)
            return {"score": score, "raw": text}
        except ImportError:
            return {"score": None, "error": "google-generativeai package not installed"}

    def _extract_score(self, text):
        import re
        match = re.search(r'\b([1-5])\b', text)
        return int(match.group(1)) if match else None

class InferenceExecutor:
    """Orchestrates execution of bias experiments."""

    def __init__(self, cache_dir=None):
        self.cache_dir = Path(cache_dir or CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.judges = {}
        self.results = []

    def _load_api_key(self, env_var, alt_names=None):
        """Load API key from environment."""
        key = os.environ.get(env_var)
        if not key and alt_names:
            for alt in alt_names:
                key = os.environ.get(alt)
                if key:
                    break
        return key

    def register_judge(self, name, judge_class, model_name=None, api_key_env=None):
        """Register a judge model."""
        api_key = self._load_api_key(api_key_env)
        if not api_key:
            print(f"  ⚠ No API key for {name} ({api_key_env}). Skipping.")
            return False

        self.judges[name] = judge_class(model_name=model_name, api_key=api_key)
        preview = f"...{api_key[-4:]}" if api_key else "None"
        print(f"  ✓ {name} registered (key: {preview})")
        return True

    def _get_cache_key(self, judge, probe_id, temperature):
        """Generate a deterministic cache key."""
        raw = f"{judge}:{probe_id}:{temperature}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _check_cache(self, cache_key):
        cache_path = self.cache_dir / f"{cache_key}.json"
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)
        return None

    def _write_cache(self, cache_key, result):
        cache_path = self.cache_dir / f"{cache_key}.json"
        with open(cache_path, "w") as f:
            json.dump(result, f)

    def run_benchmark(self, benchmark_path, judge_name=None, probe=None,
                      max_items=None, temperature=0.0, use_cache=True):
        """Run the benchmark for specified judges and probes."""
        with open(benchmark_path) as f:
            benchmark = json.load(f)

        print(f"\n{'='*60}")
        print(f"EXPERIMENT EXECUTION — Benchmark: {benchmark.get('name', 'unknown')}")
        print(f"{'='*60}")

        judges_to_run = [judge_name] if judge_name and judge_name != "all" else list(self.judges.keys())

        for judge_name in judges_to_run:
            if judge_name not in self.judges:
                print(f"  ✗ Judge {judge_name} not registered. Available: {list(self.judges.keys())}")
                continue

            judge = self.judges[judge_name]
            judge_results = []

            for probe_name, probes in benchmark.get("probes", {}).items():
                if probe and probe_name != probe:
                    continue

                print(f"\n  Judge: {judge_name} | Probe: {probe_name} ({len(probes)} items)")

                items = probes[:max_items] if max_items else probes
                for i, item in enumerate(items):
                    cache_key = self._get_cache_key(judge_name, item["probe_id"], temperature)

                    # Check cache
                    cached = self._check_cache(cache_key) if use_cache else None
                    if cached:
                        result = cached
                    else:
                        result = judge.score_with_retry(
                            instruction=item.get("instruction", ""),
                            response=item.get("response", ""),
                            rubric=item.get("rubric", "Score 1-5"),
                            reference_answer=item.get("reference_answer"),
                            reference_score=item.get("reference_score"),
                        )
                        self._write_cache(cache_key, result)

                    judge_results.append({
                        "judge": judge_name,
                        "probe_id": item["probe_id"],
                        "bias_type": item.get("bias_type", probe_name),
                        "condition": item.get("condition", ""),
                        "score": result.get("score"),
                        "raw": result.get("raw", ""),
                        "error": result.get("error"),
                        "cached": cached is not None,
                    })

                    if (i + 1) % 10 == 0:
                        print(f"    {i+1}/{len(items)} completed", end="\r")

                print(f"    {len(items)}/{len(items)} completed")

            # Save judge results
            if judge_results:
                csv_path = RESULTS_DIR / f"results_{judge_name}.csv"
                with open(csv_path, "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=judge_results[0].keys())
                    w.writeheader()
                    w.writerows(judge_results)
                print(f"  Saved {len(judge_results)} results to {csv_path}")

                # Compute per-probe statistics
                self._compute_probe_stats(judge_name, judge_results)

    def _compute_probe_stats(self, judge_name, results):
        """Compute per-probe statistics for a judge."""
        from collections import defaultdict
        probes = defaultdict(list)
        for r in results:
            probes[r["bias_type"]].append(r["score"])

        print(f"\n  Judge {judge_name} — Per-probe statistics:")
        for probe, scores in sorted(probes.items()):
            clean = [s for s in scores if s is not None]
            if clean:
                avg = sum(clean) / len(clean)
                print(f"    {probe:<20} n={len(clean):>4} mean={avg:.2f}")

    def status(self):
        """Print status of all registered judges."""
        print("\nRegistered judges:")
        for name, judge in self.judges.items():
            print(f"  ✓ {name} ({judge.model_name})")
        print(f"Cache: {self.cache_dir}")
        print(f"Results: {RESULTS_DIR}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", default="all", help="Judge to run (or 'all')")
    parser.add_argument("--benchmark", default="benchmark/scoring_bias_benchmark.json",
                        help="Benchmark JSON file")
    parser.add_argument("--probe", help="Specific probe type to run")
    parser.add_argument("--items", type=int, help="Max items per probe")
    parser.add_argument("--no-cache", action="store_true", help="Disable result caching")
    parser.add_argument("--status", action="store_true", help="Show status only")
    args = parser.parse_args()

    executor = InferenceExecutor()

    # Register all available judges
    executor.register_judge("claude", ClaudeJudge, "claude-sonnet-4-20250514", "ANTHROPIC_API_KEY")
    executor.register_judge("gpt4o", GPT4oJudge, "gpt-4o", "OPENAI_API_KEY")
    executor.register_judge("gemini", GeminiJudge, "gemini-2.0-flash", "GEMINI_API_KEY")

    if args.status:
        executor.status()
        return

    if not os.path.exists(args.benchmark):
        print(f"Benchmark not found: {args.benchmark}")
        print("Run: python3 benchmark/scoring_bias_benchmark.py")
        return

    executor.run_benchmark(
        args.benchmark,
        judge_name=args.judge,
        probe=args.probe,
        max_items=args.items,
        use_cache=not args.no_cache,
    )

if __name__ == "__main__":
    main()
