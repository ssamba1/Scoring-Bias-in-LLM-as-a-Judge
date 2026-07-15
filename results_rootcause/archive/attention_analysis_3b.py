#!/usr/bin/env python3
"""
ATTENTION ANALYSIS AT 3B  Tests IIAR at scale where content ↑ effect appears.
Compares: Llama-3.2-3B base vs instruct attention patterns.

Run on Kaggle T4 (free). Needs HF_TOKEN for gated Llama models.
"""
# !pip install -q --upgrade transformers

import torch, json, os, numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM

os.environ["HF_TOKEN"] = "hf_your_token"  # ← CHANGE THIS

MODELS = [
    ("meta-llama/Llama-3.2-3B", "Llama-3.2-3B-base"),
    ("meta-llama/Llama-3.2-3B-Instruct", "Llama-3.2-3B-instruct"),
]

PROMPT = """Evaluate the following response.
### Instruction: Explain how photosynthesis works.
### Response: Photosynthesis happens in plants where they use sunlight to make food.
### Score from 1-5 (where 1 is worst, 5 is best)
### Score:"""

# Token classification  expanded for better coverage
FORMAT_PATTERNS = ["###", "Instruction", "Response", "Score", "1", "2", "3", "4", "5", 
                   "from", "where", "is", "the", "worst", "best", ":", "\n", " ", "."]
CONTENT_PATTERNS = ["photosynthesis", "explain", "happens", "plants", "sunlight", 
                    "food", "make", "use", "they", "how", "works"]

def classify(token_ids, tokenizer):
    labels = []
    for tid in token_ids:
        t = tokenizer.decode(tid).strip().lower()
        if any(f in t for f in FORMAT_PATTERNS):
            labels.append("FORMAT")
        elif any(c in t for c in CONTENT_PATTERNS):
            labels.append("CONTENT")
        else:
            labels.append("OTHER")
    return labels

results = {}

for model_id, name in MODELS:
    print(f"\n=== Loading {name} ===")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.environ["HF_TOKEN"])
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto",
        output_attentions=True, token=os.environ["HF_TOKEN"]
    )
    model.eval()
    
    inputs = tokenizer(PROMPT, return_tensors="pt").to(model.device)
    labels = classify(inputs["input_ids"][0].tolist(), tokenizer)
    
    # Print token classification for debugging
    n_format = labels.count("FORMAT")
    n_content = labels.count("CONTENT")
    print(f"  Tokens: {len(labels)} total, {n_format} format, {n_content} content")
    
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    
    attentions = outputs.attentions  # tuple of (batch, heads, seq, seq)
    
    format_attn = []
    content_attn = []
    
    for layer_idx, attn in enumerate(attentions):
        avg_attn = attn[0].mean(dim=0)  # average over heads -> (seq, seq)
        
        # Attention from LAST token to each other token
        last_token_attn = avg_attn[-1, :] * 100  # percentage
        
        f_attn = sum(last_token_attn[i].item() for i in range(len(labels)) if labels[i] == "FORMAT")
        c_attn = sum(last_token_attn[i].item() for i in range(len(labels)) if labels[i] == "CONTENT")
        
        format_attn.append(f_attn)
        content_attn.append(c_attn)
    
    results[name] = {
        "format_attn_per_layer": format_attn,
        "content_attn_per_layer": content_attn,
        "mean_format_attn": np.mean(format_attn),
        "mean_content_attn": np.mean(content_attn),
    }
    print(f"  Mean format attention: {results[name]['mean_format_attn']:.2f}%")
    print(f"  Mean content attention: {results[name]['mean_content_attn']:.2f}%")

# Compare base vs instruct
base = results.get("Llama-3.2-3B-base")
instruct = results.get("Llama-3.2-3B-instruct")

if base and instruct:
    k_format = instruct["mean_format_attn"] / max(base["mean_format_attn"], 0.01)
    k_content = instruct["mean_content_attn"] / max(base["mean_content_attn"], 0.01)
    
    print(f"\n{'='*50}")
    print(f"IIAR TEST AT 3B SCALE")
    print(f"{'='*50}")
    print(f"Format κ = {k_format:.3f}x {'✅' if k_format > 1.05 else '❌'} (IIAR predicts > 1.0)")
    print(f"Content κ = {k_content:.3f}x {'✅' if k_content > 1.05 else '❌'} (IIAR predicts > 1.0)")
    print(f"\nComparison with 0.5B (from earlier run):")
    print(f"  0.5B: Format κ=1.003, Content κ=0.870 (IIAR NOT supported)")
    if k_format > 1.05 and k_content > 1.05:
        print(f"\n  3B: Both κ > 1.0 → IIAR SUPPORTED at 3B scale!")
        print(f"  Implication: IIAR has a scale threshold between 0.5B and 3B")
    elif k_format > 1.05:
        print(f"\n  3B: Only format κ > 1.0 → partial IIAR")
    else:
        print(f"\n  3B: Neither κ > 1.0 → IIAR not supported at any tested scale")
        print(f"  Alternative mechanism needed")

# Save
with open("attention_results_3b.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved attention_results_3b.json")
print("DONE.")
