#!/usr/bin/env python3
"""
ATTENTION HEAD ANALYSIS — tests the IIAR hypothesis
by comparing attention redistribution in base vs instruct models.

Run on Kaggle T4 (free). Requires model pairs:
  - meta-llama/Llama-3.2-3B (base)
  - meta-llama/Llama-3.2-3B-Instruct (instruct)

Measures: attention to format tokens vs content tokens per layer per head.
"""
import torch, json, re, sys
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import numpy as np

MODELS = [
    ("meta-llama/Llama-3.2-3B", "Llama-3.2-3B-base"),
    ("meta-llama/Llama-3.2-3B-Instruct", "Llama-3.2-3B-instruct"),
]

# Test scoring prompt
PROMPT = """Evaluate the following response to the instruction on a scale of 1--5, where 1 is worst and 5 is best.
### Instruction: Explain how photosynthesis works.
### Response: Photosynthesis happens in plants where they use sunlight to make food.
### Score:"""

def classify_tokens(tokens, tokenizer):
    """Classify each token as FORMAT, CONTENT, or OTHER."""
    labels = []
    for tid in tokens:
        t = tokenizer.decode(tid)
        if t in ["###", "Instruction", "Response", "Score", ":", "1", "2", "3", "4", "5", 
                 "--", "worst", "best", "scale", "where", "of", "on", "a", "the", "to"]:
            labels.append("FORMAT")
        elif t in ["Photosynthesis", "happens", "plants", "sunlight", "food", "Explain", 
                   "how", "photosynthesis", "works", "make", "use", "in", "they"]:
            labels.append("CONTENT")
        else:
            labels.append("OTHER")
    return labels

results = {}

for model_id, name in MODELS:
    print(f"\nLoading {name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto",
        output_attentions=True
    )
    
    inputs = tokenizer(PROMPT, return_tensors="pt").to(model.device)
    labels = classify_tokens(inputs["input_ids"][0].tolist(), tokenizer)
    
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    
    # Extract attention per layer
    attentions = outputs.attentions  # tuple of (batch, heads, seq, seq)
    n_layers = len(attentions)
    n_heads = attentions[0].shape[1]
    
    # For each layer, compute attention to FORMAT vs CONTENT tokens
    format_attn = []
    content_attn = []
    
    for layer_idx, attn in enumerate(attentions):
        # Average over heads
        avg_attn = attn[0].mean(dim=0)  # (seq, seq)
        
        # For each token, how much attention does it pay to FORMAT vs CONTENT?
        f_attn = 0
        c_attn = 0
        total = 0
        for i in range(len(labels)):
            if labels[i] == "FORMAT":
                f_attn += avg_attn[-1, i].item() * 100  # last token attention to format tokens
            elif labels[i] == "CONTENT":
                c_attn += avg_attn[-1, i].item() * 100
        format_attn.append(f_attn)
        content_attn.append(c_attn)
    
    results[name] = {
        "format_attn_per_layer": format_attn,
        "content_attn_per_layer": content_attn,
        "mean_format_attn": np.mean(format_attn),
        "mean_content_attn": np.mean(content_attn),
        "kappa_format": 1.0,  # will compute ratio
        "kappa_content": 1.0,
    }
    print(f"  Format attention: {results[name]['mean_format_attn']:.2f}%")
    print(f"  Content attention: {results[name]['mean_content_attn']:.2f}%")

# Compare base vs instruct
base = results.get("Llama-3.2-3B-base")
instruct = results.get("Llama-3.2-3B-instruct")
if base and instruct:
    k_format = instruct["mean_format_attn"] / max(base["mean_format_attn"], 0.01)
    k_content = instruct["mean_content_attn"] / max(base["mean_content_attn"], 0.01)
    print(f"\n=== IIAR TEST RESULTS ===")
    print(f"Format attention ratio (kappa_format): {k_format:.2f}x")
    print(f"  {'SUPPORTS IIAR' if k_format > 1.05 else 'INCONCLUSIVE'} (expected > 1.0)")
    print(f"Content attention ratio (kappa_content): {k_content:.2f}x")
    print(f"  {'SUPPORTS IIAR' if k_content > 1.05 else 'INCONCLUSIVE'} (expected > 1.0)")

# Save
OUT = Path("attention_results.json")
with open(OUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}")

print("\nDONE.")
print("If kappa > 1.0 for BOTH format AND content, IIAR is supported.")
print("If only format attention increases, alternative mechanism is needed.")
