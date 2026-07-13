#!/usr/bin/env python3
"""Scoring pipeline for Bias Interaction Effects experiment.
Usage: python3 scoring_pipeline.py --judge claude --input data/items_all_conditions.csv --output results/
"""
import csv, json, os, sys, argparse, time, random
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator. Score the following response on a scale of 1-5 based on these criteria:

1. Relevance: How well does the response address the instruction?
2. Quality: How clear, accurate, and well-written is the response?
3. Completeness: Does the response fully answer the question?

Respond with ONLY a single integer score (1-5). No explanation.

Instruction: {instruction}
Response: {response}

Score:"""

def score_with_api(instruction, response, judge_name, api_key=None):
    """Score a single item using the specified judge model.
    
    YOU MUST IMPLEMENT this function with your actual API keys.
    
    Template implementations for each judge:
    
    ## Claude (Anthropic)
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return int(msg.content[0].text.strip())
    
    ## GPT-4o (OpenAI)
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )
    return int(resp.choices[0].message.content.strip())
    
    ## Gemini (Google)
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)
    return int(resp.text.strip())
    
    ## DeepSeek
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    resp = client.chat.completions.create(
        model="deepseek-chat", temperature=0, max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )
    return int(resp.choices[0].message.content.strip())
    """
    prompt = JUDGE_PROMPT_TEMPLATE.format(instruction=instruction, response=response)
    
    # PLACEHOLDER: Returns random score for testing
    # Replace with actual API call using your keys
    score = random.randint(2, 5)
    time.sleep(0.05)
    return score

def run_pipeline(judge_name, input_file, output_dir, repeats=3, api_key=None):
    """Run the full scoring pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Load items
    with open(input_file, "r", encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    
    print(f"Loaded {len(items)} items. Scoring with {judge_name} ({repeats}x repeats)...")
    
    results = []
    for i, item in enumerate(items):
        scores = []
        for r in range(repeats):
            score = score_with_api(item["instruction"], item["response"], judge_name, api_key)
            scores.append(score)
        
        results.append({
            "item_id": item["item_id"],
            "condition": item["condition"],
            "position": item["position"],
            "length": item["length"],
            "sentiment": item["sentiment"],
            "instruction": item["instruction"],
            "response_preview": item["response"][:80],
            "score_mean": sum(scores) / len(scores),
            "score_median": sorted(scores)[len(scores)//2],
            "score_min": min(scores),
            "score_max": max(scores),
            "score_std": (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5,
            "raw_scores": json.dumps(scores),
        })
        
        if (i+1) % 50 == 0:
            print(f"  Scored {i+1}/{len(items)}...")
    
    # Save results
    out_path = os.path.join(output_dir, f"results_{judge_name}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)
    
    print(f"Saved {len(results)} results to {out_path}")
    return out_path

def run_all_judges(input_file, output_dir, api_keys=None):
    """Run all 5 judges."""
    judges = ["claude", "gpt4o", "gemini", "deepseek", "llama"]
    api_keys = api_keys or {}
    
    for judge in judges:
        print(f"\n{'='*50}")
        print(f"Running {judge}...")
        run_pipeline(judge, input_file, output_dir, api_key=api_keys.get(judge))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", default="claude", help="Judge model name")
    parser.add_argument("--input", default=str(DATA_DIR / "items_all_conditions.csv"))
    parser.add_argument("--output", default=str(RESULTS_DIR))
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    
    run_pipeline(args.judge, args.input, args.output, args.repeats)
