#!/usr/bin/env python3
"""
PROMPT ABLATION — tests whether differential effect is robust to prompt changes.
Runs rubric order probe with 5 different prompt templates.

Run on Kaggle T4 with a single model pair (e.g., Llama-3.2-3B).
"""
import json, os, time, re, gc, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL = "meta-llama/Llama-3.2-3B"
MODEL_IT = "meta-llama/Llama-3.2-3B-Instruct"

# 5 prompt templates
TEMPLATES = {
    "default": "Evaluate the following response.\n### Instruction: {inst}\n### Response: {resp}\n### Score from 1-5 (where 1 is worst, 5 is best)\n### Score:",
    "formal": "Please assess the provided response to the given instruction.\nInstruction: {inst}\nResponse: {resp}\nRating (1=worst, 5=best):",
    "minimal": "Score this: {inst} → {resp}\n1-5:",
    "verbose": "You are an expert evaluator. Your task is to score the following response on a scale of 1 to 5, where 1 is terrible and 5 is perfect.\n\nInstruction: {inst}\n\nResponse: {resp}\n\nScore:",
    "numbered": "Q: {inst}\nA: {resp}\nRate (1=poor, 5=excellent):",
}

REVERSED = {
    "default": "Evaluate the following response.\n### Instruction: {inst}\n### Response: {resp}\n### Score from 1-5 (where 1 is best, 5 is worst)\n### Score:",
    "formal": "Please assess the provided response.\nInstruction: {inst}\nResponse: {resp}\nRating (1=best, 5=worst):",
    "minimal": "Score this: {inst} → {resp}\n5-1 (reversed):",
    "verbose": "Score from 1 to 5, where 1 is perfect and 5 is terrible.\nInstruction: {inst}\nResponse: {resp}\nScore:",
    "numbered": "Rate (1=excellent, 5=poor): {inst} → {resp}",
}

ITEMS = [
    ("Explain photosynthesis.", "Photosynthesis happens in plants where they use sunlight to make food."),
    ("Describe an atom.", "An atom has a nucleus with protons and neutrons, and electrons orbit in shells."),
]

results = {}
for model_id, name in [(MODEL, "base"), (MODEL_IT, "instruct")]:
    print(f"\n=== {name} ===")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=HF_TOKEN)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto", token=HF_TOKEN)
    model.eval()
    
    for tmpl_name in TEMPLATES:
        normal_scores = []
        reversed_scores = []
        for inst, resp in ITEMS:
            for prompt_template, variant_scores, is_reversed in [
                (TEMPLATES[tmpl_name], normal_scores, False),
                (REVERSED[tmpl_name], reversed_scores, True)
            ]:
                prompt = prompt_template.format(inst=inst, resp=resp)
                inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=3, temperature=0.0, do_sample=False)
                new_tokens = out[0][inputs.input_ids.shape[1]:]
                text = tokenizer.decode(new_tokens, skip_special_tokens=True)
                nums = re.findall(r'[1-5]', text)
                variant_scores.append(int(nums[0]) if nums else 3)
        
        delta = abs(statistics.mean(normal_scores) - statistics.mean(reversed_scores)) if normal_scores and reversed_scores else 0
        results.setdefault(tmpl_name, {})[name] = delta
        print(f"  {tmpl_name:<12} Δ = {delta:.2f}")
    
    del model, tokenizer; gc.collect(); torch.cuda.empty_cache()

print("\n=== ABLATION RESULTS ===")
print(f"{'Template':<12} {'Base Δ':<8} {'Instruct Δ':<8} {'Direction':<10}")
print("-"*38)
for tmpl in TEMPLATES:
    b = results.get(tmpl, {}).get("base", 0)
    i = results.get(tmpl, {}).get("instruct", 0)
    d = "DOWN" if i < b else "UP"
    print(f"{tmpl:<12} {b:<8.2f} {i:<8.2f} {d:<10}")

print("\nDONE.")
