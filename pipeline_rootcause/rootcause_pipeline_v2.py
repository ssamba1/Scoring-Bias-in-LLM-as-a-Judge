#!/usr/bin/env python3
"""
Root Cause of Scoring Bias — Production GPU Pipeline.
Loads base and instruct models from HuggingFace, runs scoring bias probes,
and compares bias susceptibility across training stages.

Supports:
- Llama 3 8B (base + instruct)
- Mistral 7B v0.3 (base + instruct)
- Gemma 2 2B (base + instruct)
- Automatic device mapping (CUDA, MPS, or CPU)
- Batch inference for efficiency
- Result caching to avoid recomputation
"""
import argparse, csv, json, os, sys, time, math
from pathlib import Path
from typing import List, Dict, Optional

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results_rootcause"
CACHE_DIR = BASE_DIR / "cache"

MODEL_REGISTRY = {
    "llama3-8b": {
        "base": "meta-llama/Meta-Llama-3-8B",
        "instruct": "meta-llama/Meta-Llama-3-8B-Instruct",
        "family": "llama",
        "size_b": 8,
        "requires_auth": True,
    },
    "mistral-7b": {
        "base": "mistralai/Mistral-7B-v0.3",
        "instruct": "mistralai/Mistral-7B-Instruct-v0.3",
        "family": "mistral",
        "size_b": 7,
        "requires_auth": False,
    },
    "gemma2-2b": {
        "base": "google/gemma-2-2b",
        "instruct": "google/gemma-2-2b-it",
        "family": "gemma",
        "size_b": 2,
        "requires_auth": True,
    },
}

# Scoring bias probes (Li et al. 2025 methodology)
RUBRIC_ORDER_PROBES = {
    "ascending": ["1", "2", "3", "4", "5"],
    "descending": ["5", "4", "3", "2", "1"],
    "random": ["3", "5", "1", "2", "4"],
}

SCORE_ID_PROBES = {
    "arabic": ["1", "2", "3", "4", "5"],
    "letter": ["E", "D", "C", "B", "A"],
    "roman": ["i", "ii", "iii", "iv", "v"],
}

class RootCausePipeline:
    """Production pipeline for Root Cause of Scoring Bias experiment."""

    def __init__(self, model_family: str = "all", use_cache: bool = True,
                 device: str = "auto", batch_size: int = 4):
        self.model_family = model_family
        self.use_cache = use_cache
        self.device = device
        self.batch_size = batch_size
        self.models = {}  # name -> (model, tokenizer)

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _detect_device(self) -> str:
        """Detect available device."""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    def load_model(self, model_key: str, variant: str):
        """Load a model and tokenizer from HuggingFace."""
        if model_key not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(MODEL_REGISTRY.keys())}")

        hf_id = MODEL_REGISTRY[model_key][variant]
        model_name = f"{model_key}-{variant}"
        cache_path = CACHE_DIR / f"{model_name}_loaded.flag"

        # Check cache
        if self.use_cache and cache_path.exists():
            print(f"  [Cache hit] {model_name}")
            return

        print(f"  Loading {model_name} ({hf_id})...", end=" ", flush=True)
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            device = self._detect_device() if self.device == "auto" else self.device
            torch_dtype = torch.float16 if device == "cuda" else torch.float32

            tokenizer = AutoTokenizer.from_pretrained(hf_id, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelForCausalLM.from_pretrained(
                hf_id,
                torch_dtype=torch_dtype,
                device_map=device if device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )

            if device != "cuda":
                model = model.to(device)

            self.models[model_name] = (model, tokenizer)

            # Mark cache
            cache_path.write_text(f"loaded at {time.time()}")
            print(f"OK ({sum(p.numel() for p in model.parameters())/1e6:.0f}M params)")

        except ImportError:
            print("SKIP (transformers/torch not installed)")
        except Exception as e:
            print(f"FAILED: {e}")

    def score_response(self, model_name: str, instruction: str, response: str,
                       rubric: str, score_ids: List[str],
                       reference_answer: Optional[str] = None,
                       reference_score: Optional[int] = None) -> Optional[int]:
        """Score a response using the given model."""
        if model_name not in self.models:
            print(f"  Model {model_name} not loaded")
            return None

        model, tokenizer = self.models[model_name]

        # Build prompt following Li et al. 2025 template
        prompt = f"""You are evaluating a response. Score it from 1 to 5.

### Score Rubrics:
{rubric}

### The instruction to evaluate:
{instruction}

### Response to evaluate:
{response}

### Feedback:
Score: """

        if reference_answer:
            prompt = prompt.replace("Score: ", f"\n### Reference Answer (Score {reference_score}):\n{reference_answer}\n\nScore: ")

        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Generate
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=5,
                    temperature=0.0,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                )
            response_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

            # Extract score
            import re
            match = re.search(r'\b([1-5])\b', response_text)
            if match:
                return int(match.group(1))
            # Try finding a number
            nums = re.findall(r'\b(\d+)\b', response_text)
            if nums:
                n = int(nums[0])
                if 1 <= n <= 5:
                    return n

            print(f"  Could not parse score from: '{response_text[:50]}'")
            return None
        except Exception as e:
            print(f"  Generation error: {e}")
            return None

    def run_bias_probe(self, model_name: str, probe_type: str,
                       items: List[Dict]) -> List[Dict]:
        """Run a single bias probe for a model."""
        results = []

        for item in items:
            # Baseline score (ascending rubric, arabic IDs, no reference)
            baseline_rubric = "\n".join(
                f"Score {s}: Level {s} quality." for s in RUBRIC_ORDER_PROBES["ascending"]
            )
            base_score = self.score_response(
                model_name, item["instruction"], item["response"],
                baseline_rubric, SCORE_ID_PROBES["arabic"]
            )

            if probe_type == "rubric_order":
                # Test different rubric orders
                for order_name, scores in RUBRIC_ORDER_PROBES.items():
                    rubric = "\n".join(f"Score {s}: Level {self._score_idx(s)} quality." for s in scores)
                    probe_score = self.score_response(
                        model_name, item["instruction"], item["response"],
                        rubric, SCORE_ID_PROBES["arabic"]
                    )
                    results.append({
                        "model": model_name, "probe": probe_type,
                        "condition": order_name, "item_id": item["item_id"],
                        "score": probe_score, "baseline": base_score,
                    })

            elif probe_type == "score_id":
                for sid_name, ids in SCORE_ID_PROBES.items():
                    rubric = "\n".join(
                        f"Score {ids[i]}: {desc}"
                        for i, desc in enumerate(["Poor", "Below avg", "Average", "Good", "Excellent"])
                    )
                    probe_score = self.score_response(
                        model_name, item["instruction"], item["response"],
                        rubric, ids
                    )
                    results.append({
                        "model": model_name, "probe": probe_type,
                        "condition": sid_name, "item_id": item["item_id"],
                        "score": probe_score, "baseline": base_score,
                    })

            elif probe_type == "reference_answer":
                for ref_score in range(1, 6):
                    ref_answer = f"Reference response with score {ref_score}."
                    probe_score = self.score_response(
                        model_name, item["instruction"], item["response"],
                        baseline_rubric, SCORE_ID_PROBES["arabic"],
                        reference_answer=ref_answer,
                        reference_score=ref_score,
                    )
                    results.append({
                        "model": model_name, "probe": probe_type,
                        "condition": f"ref_{ref_score}", "item_id": item["item_id"],
                        "score": probe_score, "baseline": base_score,
                    })

            if len(results) % 10 == 0 and results:
                print(f"    {len(results)} probes completed", end="\r")

        return results

    def _score_idx(self, s: str) -> int:
        mapping = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
        return mapping.get(s, 3)

    def load_evaluation_items(self, n_items: int = 50) -> List[Dict]:
        """Load evaluation items from generated data."""
        path = DATA_DIR / "items_base.csv"
        if not path.exists():
            print(f"Items not found at {path}")
            return []

        import csv
        with open(path) as f:
            items = list(csv.DictReader(f))
            items = items[:n_items]

        # Create instruction-response pairs
        result = []
        for item in items:
            result.append({
                "item_id": int(item["item_id"]),
                "instruction": item.get("instruction", "Respond to the following prompt."),
                "response": item.get("base_response", "Response content."),
            })
        return result

    def compare_base_vs_instruct(self, model_key: str, n_items: int = 50):
        """Compare base vs instruct for a given model family."""
        print(f"\n{'='*60}")
        print(f"Model Family: {model_key}")
        print(f"{'='*60}")

        # Load both variants
        for variant in ["base", "instruct"]:
            self.load_model(model_key, variant)

        # Load evaluation items
        items = self.load_evaluation_items(n_items)
        if not items:
            print("No items to evaluate")
            return None

        print(f"Loaded {len(items)} evaluation items")

        # Run all probes
        all_results = []
        for variant in ["base", "instruct"]:
            model_name = f"{model_key}-{variant}"
            print(f"\n  --- {model_name} ---")

            for probe_type in ["rubric_order", "score_id", "reference_answer"]:
                print(f"  Probe: {probe_type}")
                results = self.run_bias_probe(model_name, probe_type, items)
                all_results.extend(results)

        # Save results
        if all_results:
            csv_path = RESULTS_DIR / f"rootcause_{model_key}.csv"
            with open(csv_path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=all_results[0].keys())
                w.writeheader()
                w.writerows(all_results)
            print(f"\nResults saved: {csv_path} ({len(all_results)} probes)")

        # Compute comparison statistics
        self._compute_comparison(all_results, model_key)

        return all_results

    def _compute_comparison(self, results, model_key):
        """Compute base vs instruct comparison statistics."""
        base_results = [r for r in results if "base" in r["model"]]
        inst_results = [r for r in results if "instruct" in r["model"]]

        print(f"\n  BASE vs INSTRUCT COMPARISON — {model_key}")
        print(f"  {'Probe':<25} {'Base Score':<12} {'Instruct Score':<16} {'Delta':<10}")
        print(f"  {'-'*63}")

        for probe_type in ["rubric_order", "score_id", "reference_answer"]:
            base_probe = [r for r in base_results if r["probe"] == probe_type]
            inst_probe = [r for r in inst_results if r["probe"] == probe_type]

            base_scores = [r["score"] for r in base_probe if r["score"] is not None]
            inst_scores = [r["score"] for r in inst_probe if r["score"] is not None]

            if base_scores and inst_scores:
                bm = sum(base_scores) / len(base_scores)
                im = sum(inst_scores) / len(inst_scores)
                delta = im - bm
                print(f"  {probe_type:<25} {bm:<12.3f} {im:<16.3f} {delta:<+10.3f}")

    def run_all_families(self, n_items=50):
        """Run comparison for all model families."""
        families = list(MODEL_REGISTRY.keys())
        for family in families:
            self.compare_base_vs_instruct(family, n_items)

        # Generate summary
        self._generate_summary()

    def _generate_summary(self):
        """Generate cross-family summary."""
        print(f"\n{'='*60}")
        print("CROSS-FAMILY SUMMARY")
        print(f"{'='*60}")
        print(f"{'Model':<20} {'Rubric Δ':<12} {'Score ID Δ':<12} {'Ref Answer Δ':<12}")
        print(f"{'-'*56}")

        for family in MODEL_REGISTRY:
            path = RESULTS_DIR / f"rootcause_{family}.csv"
            if not path.exists():
                continue
            import csv
            with open(path) as f:
                results = list(csv.DictReader(f))

            base_r = [r for r in results if "base" in r["model"]]
            inst_r = [r for r in results if "instruct" in r["model"]]

            deltas = {}
            for probe in ["rubric_order", "score_id", "reference_answer"]:
                bs = [float(r["score"]) for r in base_r if r["probe"] == probe and r["score"]]
                is_ = [float(r["score"]) for r in inst_r if r["probe"] == probe and r["score"]]
                if bs and is_:
                    deltas[probe] = sum(is_)/len(is_) - sum(bs)/len(bs)

            print(f"{family:<20} {deltas.get('rubric_order', 0):<12.3f} "
                  f"{deltas.get('score_id', 0):<12.3f} "
                  f"{deltas.get('reference_answer', 0):<12.3f}")

    def show_available_models(self):
        """Show which models can be loaded."""
        print("\nAvailable models in registry:")
        print(f"{'Key':<20} {'Base ID':<45} {'Instruct ID':<45} {'Size':<8} {'Auth?':<6}")
        print("-"*124)
        for key, info in MODEL_REGISTRY.items():
            print(f"{key:<20} {info['base']:<45} {info['instruct']:<45} "
                  f"{info['size_b']}B{'':<6} {'Y' if info['requires_auth'] else 'N':<6}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="all", help="Model family to test")
    parser.add_argument("--items", type=int, default=50, help="Number of evaluation items")
    parser.add_argument("--device", default="auto", help="Device override: cuda, cpu, mps")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--no-cache", action="store_true", help="Disable model loading cache")
    args = parser.parse_args()

    pipeline = RootCausePipeline(
        model_family=args.model,
        use_cache=not args.no_cache,
        device=args.device,
    )

    if args.list_models:
        pipeline.show_available_models()
        return

    try:
        import torch
        print(f"Device: {pipeline._detect_device()}")
        print(f"PyTorch version: {torch.__version__}")
    except ImportError:
        print("PyTorch not installed. Run: pip install torch transformers accelerate")
        return

    if args.model == "all":
        pipeline.run_all_families(n_items=args.items)
    elif args.model in MODEL_REGISTRY:
        pipeline.compare_base_vs_instruct(args.model, args.items)
    else:
        print(f"Unknown model: {args.model}")
        pipeline.show_available_models()

if __name__ == "__main__":
    main()
