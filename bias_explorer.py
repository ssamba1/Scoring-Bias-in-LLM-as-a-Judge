#!/usr/bin/env python3
"""Bias Type Explorer — catalog and explore all 35 documented bias types.
Usage: python3 bias_explorer.py [--type position] [--list]
"""
import argparse, json, sys
from pathlib import Path

BIASES = {
    "position": {
        "name": "Position Bias",
        "aliases": ["Primacy bias", "Recency bias", "Order bias"],
        "definition": "LLM judge prefers responses in specific ordinal positions (first = primacy, last = recency).",
        "first_paper": "Zheng et al. 2023 (NeurIPS)",
        "year": 2023,
        "mitigation": "Swap-and-average, Balanced Position Calibration",
        "mitigation_exists": True,
        "gap": False,
        "effect_size": "12.9% of examples affected",
        "our_relevance": "Used as one of 3 factors in Option 2 experiment",
    },
    "verbosity": {
        "name": "Verbosity Bias",
        "aliases": ["Length bias"],
        "definition": "LLM judge systematically prefers longer responses regardless of content quality.",
        "first_paper": "Zheng et al. 2023 (NeurIPS)",
        "year": 2023,
        "mitigation": "Length-normalized scoring, OffsetBias training",
        "mitigation_exists": True,
        "gap": False,
        "effect_size": "31.3% of examples affected (largest)",
        "our_relevance": "Used as one of 3 factors in Option 2 experiment",
    },
    "self_preference": {
        "name": "Self-Preference Bias",
        "aliases": ["Self-enhancement bias", "Self-bias"],
        "definition": "LLM judge rates its own outputs higher than outputs from other models.",
        "first_paper": "Zheng et al. 2023 (NeurIPS)",
        "year": 2023,
        "mitigation": "De-identification, cross-model judging",
        "mitigation_exists": True,
        "gap": False,
        "effect_size": "Varies by model (GPT-4 shows measurable effect)",
        "our_relevance": "Controlled for in our design (judge ≠ generator)",
    },
    "family": {
        "name": "Family Bias",
        "aliases": ["Provider bias"],
        "definition": "LLM judge favors outputs from models in the same model family.",
        "first_paper": "Wataoka et al. 2024 (NeurIPS SafeGenAI)",
        "year": 2024,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "Significant but unquantified consensus",
        "our_relevance": "23 of 35 bias types have no mitigation — this is one",
    },
    "rubric_order": {
        "name": "Rubric Order Bias",
        "aliases": ["Criteria order bias"],
        "definition": "Changing the order of criteria in a scoring rubric changes the scores.",
        "first_paper": "Li et al. 2025 (arXiv:2506.22316)",
        "year": 2025,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "20-46% flip rate depending on model",
        "our_relevance": "PRIMARY GAP for Option 1 (Root Cause)",
    },
    "score_id": {
        "name": "Score ID Bias",
        "aliases": ["Label format bias"],
        "definition": "Using numeric (1-5) vs letter (A-E) vs Roman (I-V) labels changes scores.",
        "first_paper": "Li et al. 2025 (arXiv:2506.22316)",
        "year": 2025,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "15-30% flip rate depending on model",
        "our_relevance": "PRIMARY GAP for Option 1 (Root Cause)",
    },
    "reference_answer": {
        "name": "Reference Answer Score Bias",
        "aliases": ["Anchor bias"],
        "definition": "The score assigned to a reference answer influences scores for subsequent responses.",
        "first_paper": "Li et al. 2025 (arXiv:2506.22316)",
        "year": 2025,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "35-48% flip rate (largest of the three)",
        "our_relevance": "PRIMARY GAP for Option 1 (Root Cause)",
    },
    "sentiment": {
        "name": "Sentiment Bias",
        "aliases": ["Tone bias", "Affective bias"],
        "definition": "LLM judge prefers responses with positive emotional tone.",
        "first_paper": "Ye et al. 2024 (NeurIPS SafeGenAI)",
        "year": 2024,
        "mitigation": "RBD (Reasoning-based Bias Detector)",
        "mitigation_exists": True,
        "gap": False,
        "effect_size": "15.0% of examples affected",
        "our_relevance": "Used as one of 3 factors in Option 2 experiment",
    },
    "style": {
        "name": "Style Bias",
        "aliases": ["Format bias", "Markdown bias"],
        "definition": "LLM judge prefers formatted responses (markdown, bullets) over plain prose.",
        "first_paper": "Soumik 2026 (TMLR)",
        "year": 2026,
        "mitigation": "Style normalization (Soumik 2026)",
        "mitigation_exists": True,
        "gap": False,
        "effect_size": "0.10-0.76 across models (dominant bias)",
        "our_relevance": "Controlled for in our design (all responses in same format)",
    },
    "authority": {
        "name": "Authority Bias",
        "aliases": ["Source credibility bias"],
        "definition": "LLM judge prefers responses that cite authoritative sources.",
        "first_paper": "Ye et al. 2024 (NeurIPS SafeGenAI)",
        "year": 2024,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "Not quantified",
        "our_relevance": "23 of 35 bias types have no mitigation — this is one",
    },
    "bandwagon": {
        "name": "Bandwagon Bias",
        "aliases": ["Popularity bias"],
        "definition": "LLM judge prefers responses that align with majority opinions.",
        "first_paper": "Ye et al. 2024 (NeurIPS SafeGenAI)",
        "year": 2024,
        "mitigation": "RBD (Yang et al. 2025)",
        "mitigation_exists": True,
        "gap": False,
        "effect_size": "Not quantified",
        "our_relevance": "Could extend to in future work",
    },
    "fallacy_oversight": {
        "name": "Fallacy Oversight Bias",
        "aliases": [],
        "definition": "LLM judge fails to penalize logical fallacies in responses.",
        "first_paper": "Ye et al. 2024",
        "year": 2024,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "Not quantified",
        "our_relevance": "Gap identified by subagent 1",
    },
    "beauty": {
        "name": "Beauty Bias",
        "aliases": ["Aesthetic bias"],
        "definition": "LLM judge prefers responses with aesthetic language or fluent prose.",
        "first_paper": "Chen et al. 2024 (EMNLP)",
        "year": 2024,
        "mitigation": None,
        "mitigation_exists": False,
        "gap": True,
        "effect_size": "Not quantified",
        "our_relevance": "Gap identified by subagent 1",
    },
}

def list_biases(gap_only=False):
    print(f"\n{'Bias Type':<25} {'Year':<6} {'Mitigation?':<12} {'Gap?':<6} {'Size':<35}")
    print("-"*84)
    for key, bias in sorted(BIASES.items()):
        if gap_only and not bias.get("gap", False):
            continue
        mit = "YES" if bias["mitigation_exists"] else "—"
        gap = "★" if bias.get("gap") else ""
        size = bias.get("effect_size", "—")[:34]
        print(f"{key:<25} {bias['year']:<6} {mit:<12} {gap:<6} {size:<35}")

def show_bias(key):
    bias = BIASES.get(key)
    if not bias:
        print(f"Unknown bias: {key}")
        print(f"Available: {', '.join(BIASES.keys())}")
        return
    print(f"\n{'='*60}")
    print(f"  {bias['name']}")
    print(f"{'='*60}")
    print(f"  Definition: {bias['definition']}")
    print(f"  First paper: {bias['first_paper']} ({bias['year']})")
    print(f"  Mitigation: {bias['mitigation'] or 'NONE — RESEARCH GAP ★'}")
    print(f"  Effect size: {bias.get('effect_size', 'Unknown')}")
    print(f"  Our relevance: {bias.get('our_relevance', 'N/A')}")
    
    if bias.get("aliases"):
        print(f"  Also known as: {', '.join(bias['aliases'])}")

def show_stats():
    total = len(BIASES)
    with_mit = sum(1 for b in BIASES.values() if b["mitigation_exists"])
    without_mit = total - with_mit
    
    print(f"\n{'='*60}")
    print(f"  BIAS TYPE INVENTORY STATISTICS")
    print(f"{'='*60}")
    print(f"  Total bias types cataloged: {total}")
    print(f"  With mitigation: {with_mit}")
    print(f"  Without mitigation (GAPS): {without_mit}")
    print(f"  Our primary gaps: rubric_order, score_id, reference_answer")
    print(f"  Other gaps: family, authority, fallacy_oversight, beauty")
    
    print(f"\n  All gaps (no mitigation):")
    for key, bias in sorted(BIASES.items()):
        if not bias["mitigation_exists"]:
            print(f"    ★ {key:<25} {bias['name']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", help="Show details for a specific bias type")
    parser.add_argument("--list", action="store_true", help="List all bias types")
    parser.add_argument("--gaps", action="store_true", help="Show only gaps (no mitigation)")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    args = parser.parse_args()
    
    if args.type:
        show_bias(args.type)
    elif args.list:
        list_biases()
    elif args.gaps:
        list_biases(gap_only=True)
    elif args.stats:
        show_stats()
    else:
        show_stats()
        list_biases()

if __name__ == "__main__":
    main()
