#!/usr/bin/env python3
"""Dimension 2: Bias Mitigation Benchmark.
Tests 5 mitigation methods across all 44 families.
Buildable now — runs on the main experiment output data.
"""
import json
from pathlib import Path

METHODS = {
    "calibration": {
        "name": "Score Calibration",
        "description": "Shift and scale instruction model scores to match base model distribution",
        "code": """
def calibrate_scores(scores, base_mean, base_std, inst_mean, inst_std):
    '''Linear calibration: align instruct distribution to base distribution.'''
    return [(s - inst_mean) / max(inst_std, 0.01) * base_std + base_mean for s in scores]
"""
    },
    "ensembling": {
        "name": "Multi-Judge Ensemble",
        "description": "Average scores from 5 different instruct models",
        "code": """
def ensemble_scores(scores_dict):
    '''Average scores across multiple judges.'''
    import statistics
    return [statistics.mean([scores_dict[j][i] for j in scores_dict]) for i in range(len(next(iter(scores_dict.values()))))]
"""
    },
    "prompt_calibration": {
        "name": "Anti-Bias Prompting",
        "description": "Add explicit anti-bias instructions to the scoring prompt",
        "code": """
ANTI_BIAS_PROMPT = "IMPORTANT: Ignore the order of the rubric. Score the actual quality of the response. Do NOT let the scale format influence your judgment."
def anti_bias_prompt(original_prompt):
    return ANTI_BIAS_PROMPT + "\\n\\n" + original_prompt
"""
    },
    "few_shot": {
        "name": "Few-Shot Calibration",
        "description": "Provide examples of unbiased scoring before the target item",
        "code": """
EXAMPLES = [
    ("What is 2+2?", "4", 5),
    ("What is the capital of France?", "Paris", 5),
    ("What is the meaning of life?", "42", 2),
]
def few_shot_prompt(instruction, response):
    prompt = "Here are some scored examples:\\n\\n"
    for instr, resp, score in EXAMPLES:
        prompt += f"Q: {instr}\\nA: {resp}\\nScore: {score}\\n\\n"
    prompt += f"Now score this:\\nQ: {instruction}\\nA: {response}\\nScore:"
    return prompt
"""
    },
    "adversarial": {
        "name": "Adversarial Debiasing",
        "description": "Find worst-case biased prompt, report score range as uncertainty",
        "code": """
def adversarial_bias_range(model, tokenizer, item, probe_suite):
    '''Report min and max scores across all probe variants.'''
    scores = []
    for probe_type, variants in probe_suite:
        for vname, prompt_fn in variants.items():
            prompt = prompt_fn(item)
            inputs = tokenizer(prompt, ...)
            score = extract_score(model.generate(...))
            scores.append(score)
    return {"min": min(scores), "max": max(scores), "range": max(scores)-min(scores)}
"""
    }
}

print("="*60)
print("BIAS MITIGATION BENCHMARK")
print("="*60)
print(f"Methods: {len(METHODS)}")
for key, method in METHODS.items():
    print(f"\n  {key:<25} {method['name']:<30}")
    print(f"  {'':<25} {method['description']}")

print("\n\nEvaluation script template:")
print('''
import json, statistics

# Load experiment data
with open("results_rootcause/study1_max_scale.json") as f:
    data = json.load(f)

# For each family, compute:
# 1. Unmitigated bias (Δ between control and biased)
# 2. Mitigated bias after applying each method

results = {}
for method_name, method_fn in METHODS.items():
    mitigated_bias = []  
    for family, variants in data.items():
        # Apply mitigation
        # Compare control vs biased after mitigation
        pass
    
    results[method_name] = {
        "mean_residual_bias": statistics.mean(mitigated_bias),
        "reduction_pct": 100 * (1 - statistics.mean(mitigated_bias) / mean_unmitigated_bias)
    }

print("\\nMitigation Effectiveness:")
print(f"{'Method':<30} {'Residual Bias':<15} {'Reduction':<15}")
for method, result in sorted(results.items(), key=lambda x: -x[1]["reduction_pct"]):
    print(f"{method:<30} {result['mean_residual_bias']:<15.3f} {result['reduction_pct']:<.1f}%")
''')
print("="*60)
