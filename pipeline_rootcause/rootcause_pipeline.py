#!/usr/bin/env python3
"""Root Cause of Scoring Bias  HuggingFace inference pipeline.
Compares base vs instruct models on rubric order, score ID, and reference answer bias.

Usage: python3 rootcause_pipeline.py
"""
import csv, json, os, sys, random, itertools
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results_rootcause"

# Model configs: (name, hf_path, type)
MODELS = [
    # Llama 3 family
    ("llama3-8b-base", "meta-llama/Meta-Llama-3-8B", "base"),
    ("llama3-8b-instruct", "meta-llama/Meta-Llama-3-8B-Instruct", "instruct"),
    # Mistral family
    ("mistral-7b-base", "mistralai/Mistral-7B-v0.3", "base"),
    ("mistral-7b-instruct", "mistralai/Mistral-7B-Instruct-v0.3", "instruct"),
    # Gemma 2 family
    ("gemma2-2b-base", "google/gemma-2-2b", "base"),
    ("gemma2-2b-instruct", "google/gemma-2-2b-it", "instruct"),
]

# Prompt templates for the 3 scoring bias types
# BIAS 1: Rubric Order Bias
RUBRIC_A = """Score the following response on a scale of 1-5.

Criteria (in order of importance):
1. Accuracy: Is the information factually correct?
2. Clarity: Is the response easy to understand?
3. Completeness: Does it fully address the question?

Instruction: {instruction}
Response: {response}

Score (1-5):"""

RUBRIC_B = """Score the following response on a scale of 1-5.

Criteria (in order of importance):
1. Completeness: Does it fully address the question?
2. Clarity: Is the response easy to understand?
3. Accuracy: Is the information factually correct?

Instruction: {instruction}
Response: {response}

Score (1-5):"""

# BIAS 2: Score ID Bias
SCORE_NUMERIC = """Score the following response on a scale of 1-5 where:
1 = Poor, 2 = Below Average, 3 = Average, 4 = Good, 5 = Excellent

Instruction: {instruction}
Response: {response}

Score (1-5):"""

SCORE_LETTER = """Score the following response where:
E = Poor, D = Below Average, C = Average, B = Good, A = Excellent

Instruction: {instruction}
Response: {response}

Score (A-E):"""

SCORE_ROMAN = """Score the following response where:
I = Poor, II = Below Average, III = Average, IV = Good, V = Excellent

Instruction: {instruction}
Response: {response}

Score (I-V):"""

# BIAS 3: Reference Answer Score Bias
REF_HIGH = """Below is a reference answer that scored 5/5 (Excellent).

Reference: {reference}

Now score the following response on a scale of 1-5:

Instruction: {instruction}
Response: {response}

Score (1-5):"""

REF_LOW = """Below is a reference answer that scored 2/5 (Below Average).

Reference: {reference}

Now score the following response on a scale of 1-5:

Instruction: {instruction}
Response: {response}

Score (1-5):"""

REF_ABSENT = """Score the following response on a scale of 1-5:

Instruction: {instruction}
Response: {response}

Score (1-5):"""

# Load some evaluation items
def load_items(n=50):
    """Load items for evaluation."""
    path = DATA_DIR / "items_base.csv"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            items = list(csv.DictReader(f))
        return items[:n]
    
    # Fallback: generate minimal items
    items = []
    domains = ["science", "tech", "writing", "reasoning", "business"]
    for i in range(n):
        items.append({
            "item_id": i,
            "domain": domains[i % len(domains)],
            "instruction": f"Explain concept number {i}",
            "base_response": f"This is response number {i} with some content to evaluate.",
        })
    return items

GENERIC_REFERENCES = [
    "The water cycle involves evaporation, condensation, and precipitation working together to distribute fresh water across the planet.",
    "Machine learning algorithms learn patterns from data through training processes that optimize for accuracy on specific tasks.",
    "Photosynthesis converts sunlight into chemical energy, producing glucose and oxygen from carbon dioxide and water.",
    "The Internet uses TCP/IP protocols to route data packets between connected devices across global networks.",
    "DNA contains genetic instructions stored in a double helix structure of nucleotide base pairs.",
]

def score_with_hf_model(model_name, model_path, model_type, prompt):
    """Score using a HuggingFace model.
    
    YOU NEED TO: pip install transformers torch accelerate
    
    Implementation template:
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs, 
        max_new_tokens=5, 
        temperature=0,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    
    # Extract score from response
    import re
    match = re.search(r'[1-5]', response.strip())
    return int(match.group()) if match else 3
    """
    # PLACEHOLDER: Simulate base vs instruct behavior
    # Base models: less sensitive to prompt perturbations
    # Instruct models: more sensitive (they follow instructions better)
    random.seed(hash(prompt) % 10000)
    if model_type == "base":
        # Base models show less bias (less instruction-following)
        base_score = 3.0 + random.uniform(-0.3, 0.3)
    else:
        # Instruct models show more bias (they pay attention to rubric format)
        base_score = 3.0 + random.uniform(-0.6, 0.6)
    return max(1, min(5, round(base_score)))

def run_bias_test(items, bias_type, model_name, model_path, model_type):
    """Run a single bias type test on a model."""
    results = []
    
    for item in items:
        inst = item["instruction"]
        resp = item["base_response"]
        
        if bias_type == "rubric_order":
            s1 = score_with_hf_model(model_name, model_path, model_type, RUBRIC_A.format(instruction=inst, response=resp))
            s2 = score_with_hf_model(model_name, model_path, model_type, RUBRIC_B.format(instruction=inst, response=resp))
            results.append({"item_id": item["item_id"], "score_a": s1, "score_b": s2, "delta": abs(s1 - s2)})
        
        elif bias_type == "score_id":
            s_num = score_with_hf_model(model_name, model_path, model_type, SCORE_NUMERIC.format(instruction=inst, response=resp))
            s_let = score_with_hf_model(model_name, model_path, model_type, SCORE_LETTER.format(instruction=inst, response=resp))
            s_rom = score_with_hf_model(model_name, model_path, model_type, SCORE_ROMAN.format(instruction=inst, response=resp))
            results.append({"item_id": item["item_id"], "score_numeric": s_num, "score_letter": s_let, "score_roman": s_rom})
        
        elif bias_type == "reference_answer":
            ref = random.choice(GENERIC_REFERENCES)
            s_high = score_with_hf_model(model_name, model_path, model_type, REF_HIGH.format(reference=ref, instruction=inst, response=resp))
            s_low = score_with_hf_model(model_name, model_path, model_type, REF_LOW.format(reference=ref, instruction=inst, response=resp))
            s_abs = score_with_hf_model(model_name, model_path, model_type, REF_ABSENT.format(instruction=inst, response=resp))
            results.append({"item_id": item["item_id"], "score_high_ref": s_high, "score_low_ref": s_low, "score_no_ref": s_abs})
    
    return results

def analyze_results(all_results, model_type):
    """Analyze base vs instruct results."""
    analysis = {
        "model_type": model_type,
        "rubric_order": {"mean_delta": 0, "max_delta": 0, "pct_affected": 0},
        "score_id": {"variance": 0, "max_gap": 0},
        "reference_answer": {"high_minus_low": 0, "high_minus_none": 0},
    }
    
    # Rubric order
    deltas = [r["delta"] for r in all_results.get("rubric_order", [])]
    if deltas:
        analysis["rubric_order"]["mean_delta"] = round(sum(deltas)/len(deltas), 3)
        analysis["rubric_order"]["max_delta"] = max(deltas)
        analysis["rubric_order"]["pct_affected"] = round(sum(1 for d in deltas if d > 0)/len(deltas)*100, 1)
    
    # Score ID
    sid = all_results.get("score_id", [])
    if sid:
        gaps = []
        for r in sid:
            vals = [r["score_numeric"], r["score_letter"], r["score_roman"]]
            gaps.append(max(vals) - min(vals))
        analysis["score_id"]["mean_max_gap"] = round(sum(gaps)/len(gaps), 3)
        analysis["score_id"]["max_gap"] = max(gaps)
    
    # Reference answer
    ref = all_results.get("reference_answer", [])
    if ref:
        diffs = [r["score_high_ref"] - r["score_low_ref"] for r in ref]
        diffs_none = [r["score_high_ref"] - r["score_no_ref"] for r in ref]
        analysis["reference_answer"]["high_minus_low"] = round(sum(diffs)/len(diffs), 3)
        analysis["reference_answer"]["high_minus_none"] = round(sum(diffs_none)/len(diffs_none), 3)
    
    return analysis

if __name__ == "__main__":
    print("="*70)
    print("ROOT CAUSE OF SCORING BIAS  PIPELINE")
    print("="*70)
    
    items = load_items(30)
    print(f"Loaded {len(items)} evaluation items")
    
    all_results = {}
    
    for name, path, mtype in MODELS:
        print(f"\n--- {name} ({mtype}) ---")
        
        model_results = {}
        for bias in ["rubric_order", "score_id", "reference_answer"]:
            print(f"  Testing {bias}...")
            model_results[bias] = run_bias_test(items, bias, name, path, mtype)
        
        analysis = analyze_results(model_results, mtype)
        all_results[name] = analysis
        
        print(f"  Rubric order bias: mean Δ={analysis['rubric_order']['mean_delta']}, {analysis['rubric_order']['pct_affected']}% of items affected")
        print(f"  Score ID bias: mean max gap={analysis['score_id'].get('mean_max_gap', 'N/A')}")
        print(f"  Reference bias: high-low Δ={analysis['reference_answer'].get('high_minus_low', 'N/A')}")
    
    # Compare base vs instruct
    print("\n" + "="*70)
    print("BASE vs INSTRUCT COMPARISON")
    print("="*70)
    
    for family in ["llama3", "mistral", "gemma2"]:
        base_name = f"{family}-8b-base" if family != "gemma2" else f"{family}-2b-base"
        inst_name = f"{family}-8b-instruct" if family != "gemma2" else f"{family}-2b-instruct"
        
        if base_name in all_results and inst_name in all_results:
            base = all_results[base_name]
            inst = all_results[inst_name]
            
            print(f"\n{family.upper()}:")
            print(f"  Rubric order (base vs instruct): {base['rubric_order']['mean_delta']} vs {inst['rubric_order']['mean_delta']}")
            print(f"  Score ID gap (base vs instruct): {base['score_id'].get('mean_max_gap','?')} vs {inst['score_id'].get('mean_max_gap','?')}")
            print(f"  Ref answer bias (base vs instruct): {base['reference_answer'].get('high_minus_low','?')} vs {inst['reference_answer'].get('high_minus_low','?')}")
    
    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "rootcause_analysis.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR}/rootcause_analysis.json")
    print("\nNOTE: This is a placeholder pipeline. To run with real models:")
    print("1. pip install transformers torch accelerate")
    print("2. Implement score_with_hf_model() with actual HuggingFace inference")
    print("3. python3 rootcause_pipeline.py")
