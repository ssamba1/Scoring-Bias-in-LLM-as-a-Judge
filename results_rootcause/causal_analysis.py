#!/usr/bin/env python3
"""Dimension 1: Causal / Mechanistic Analysis.
Compares hidden states between base and instruct models under biased probes.
Tests the IIAR hypothesis at the embedding level.
"""
import json, torch, numpy as np
from pathlib import Path

def kaggle_cell():
    return '''
# ── CAUSAL ANALYSIS CELL ──
# Add to Kaggle notebook after main experiment
# Runs embedding comparison on a SUBSET of families (5 representative)

CAUSAL_FAMILIES = ["Mistral-v0.3-7B", "Qwen2.5-7B", "Llama3-8B", "Gemma2-9B", "Phi3-mini-3.8B"]

def extract_hidden_states(model, tokenizer, prompt):
    """Extract last-token hidden state for a prompt."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    # Get last token's hidden state from the last layer
    hidden = outputs.hidden_states[-1][0, -1, :].cpu().numpy()
    return hidden

def compute_embedding_shift(model_name, base_id, inst_id, items, probes):
    """Compute cosine similarity between base and instruct for each probe."""
    results = {}
    for probe_type, variants in probes:
        for variant_name in variants:
            base_states = []
            inst_states = []
            for item in items:
                prompt = build_prompt(probe_type, variant_name, item)
                # Would need to run twice — once with base model, once with instruct
                # This is a template — actual execution requires two model loads
                pass
    return results

print("Causal analysis cell ready — 5 families, embedding extraction")
print("Runtime: ~30 min per family (extra forward passes)")
print(""
'''.strip()

# Template for the main causal analysis
ANALYSIS_TEMPLATE = '''
import json, numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load embeddings from causal run output
with open("results_rootcause/causal_embeddings.json") as f:
    data = json.load(f)

# For each family, compute embedding shift magnitude
print("\\nCausal Analysis Results")
print("="*50)
for family, probes in data.items():
    print(f"\\n{family}:")
    for probe, variants in probes.items():
        if "base" in variants and "instruct" in variants:
            base_vec = np.array(variants["base"])
            inst_vec = np.array(variants["instruct"])
            sim = cosine_similarity([base_vec], [inst_vec])[0][0]
            shift = 1 - sim
            print(f"  {probe}: embedding shift = {shift:.4f} (cosine={sim:.4f})")
            
print("\\nIIAR Hypothesis Test:")
print("If shift > 0 for content probes > format probes → IIAR confirmed")
'''

print("=== CAUSAL ANALYSIS ===")
print(kaggle_cell())
print()
print("Template for after data collection:")
print(ANALYSIS_TEMPLATE)
print()
print("Saves to results_rootcause/causal_analysis/")
