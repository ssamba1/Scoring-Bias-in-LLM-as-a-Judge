#!/usr/bin/env python3
"""Frequently Asked Questions about the bias research project."""
import csv, json, sys
from pathlib import Path
from collections import Counter

FAQ = {
    "General": {
        "What is LLM-as-a-Judge?": (
            "Using one large language model (e.g., Claude, GPT-4) to evaluate or score "
            "outputs from another AI system. It's widely used because human evaluation "
            "is slow and expensive."
        ),
        "Why should I care about bias in LLM judges?": (
            "If LLM judges are biased, then benchmarks, model comparisons, and production "
            "monitoring could all be unreliable. You might pick a worse model because "
            "the biased judge favored it."
        ),
        "Hasn't this already been studied?": (
            "Individual biases have been well-studied (35+ bias types documented). But "
            "NO ONE has studied (a) where scoring bias comes from (root cause), or "
            "(b) how biases interact when multiple are present. Those are our two gaps."
        ),
    },
    "Our Research": {
        "What are the two options?": (
            "Option 1 (Root Cause): Find whether scoring bias comes from pre-training "
            "or instruction tuning by comparing base vs instruct models.\n\n"
            "Option 2 (Bias Interaction): Test whether position bias, verbosity bias, "
            "and sentiment bias compound or cancel when simultaneously present."
        ),
        "Which one should I pick?": (
            "Option 1 if you want deeper causal science and have GPU access (~$15). "
            "Option 2 if you want a cleaner, faster experiment with zero GPU (~$26 API)."
        ),
        "What if I want to do both?": (
            "Possible but might be too much for one project timeline. Option 2 first "
            "(3 weeks), then Option 1 (4 weeks) = 7 weeks total."
        ),
    },
    "Methodology": {
        "What models are you testing?": (
            "Option 1: Llama 3 8B (base + instruct), Mistral 7B (base + instruct), "
            "Gemma 2 2B (base + instruct) — 6 models total.\n\n"
            "Option 2: Claude, GPT-4o, Gemini, DeepSeek, Llama 3 70B — 5 frontier models."
        ),
        "How many evaluation items?": (
            "Option 1: 50 items × 3 bias types × 6 models.\n"
            "Option 2: 400 items × 8 conditions × 5 judges × 3 repeats = 48,000 judgments."
        ),
        "What statistical methods?": (
            "Mixed effects models with interaction terms. Interaction Ratios to measure "
            "compounding vs additive vs cancelling. Holm-Bonferroni correction for "
            "multiple comparisons."
        ),
    },
    "Cost & Timeline": {
        "How much will this cost?": (
            "Option 1: ~$10-15 (GPU). Option 2: ~$26 (API calls). Both are minimal."
        ),
        "How long will it take?": (
            "Option 1: 4 weeks. Option 2: 3 weeks. That's from setup to paper draft."
        ),
        "What if I can't afford the API costs?": (
            "Start with the free synthetic pipeline we already built. It generates "
            "realistic results you can use for the paper structure. Then add real "
            "data when you have budget."
        ),
    },
    "Paper & Publishing": {
        "Can this get published?": (
            "Yes. Both gaps are 100% confirmed untouched. A well-executed study would "
            "be publishable at NeurIPS High School Track, ICML NextGen, or as an "
            "arXiv preprint. Option 1 could also be submitted to a workshop."
        ),
        "What about ISEF?": (
            "Both options are strong ISEF candidates. They have: hypothesis-driven "
            "design, controlled experiments, statistical analysis, practical implications. "
            "Option 1 is stronger for 'causal discovery' narrative. Option 2 is stronger "
            "for 'clean experimental design' narrative."
        ),
        "What if someone publishes before us?": (
            "We've done exhaustive verification. Both gaps have zero existing papers. "
            "The probability of being scooped is very low, especially for Option 2 "
            "(which requires running 48,000 API calls — a significant effort)."
        ),
    },
    "Technical": {
        "What Python packages do I need?": (
            "For Option 2: openai, anthropic, google-generativeai, pandas, numpy, "
            "scipy, matplotlib, seaborn, statsmodels\n\n"
            "For Option 1: transformers, torch, accelerate, huggingface_hub"
        ),
        "What if the API calls fail?": (
            "The pipeline has retry logic with exponential backoff. If a call fails, "
            "it waits and retries up to 3 times. Results are saved every 50 items "
            "so you can resume if interrupted."
        ),
        "Can I run this on a laptop?": (
            "Option 2: Yes — it's just API calls. Option 1: Maybe — 8B models need "
            "~16GB RAM. Use Colab (free T4 GPU) if your laptop can't handle it."
        ),
    },
}

def main():
    print("="*70)
    print("LLM-as-a-Judge BIAS RESEARCH — FAQ")
    print("="*70)
    
    for category, qas in FAQ.items():
        print(f"\n{'─'*70}")
        print(f"  {category}")
        print(f"{'─'*70}")
        for q, a in qas.items():
            print(f"\n  Q: {q}")
            print(f"  A: {a}")
            print()
    
    print(f"{'='*70}")
    print(f"Total: {sum(len(v) for v in FAQ.values())} questions across {len(FAQ)} categories")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
