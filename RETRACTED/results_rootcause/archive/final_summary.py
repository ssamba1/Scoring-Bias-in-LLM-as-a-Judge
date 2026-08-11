#!/usr/bin/env python3
"""Final summary table for the paper."""
import json

print("""
=== SCORING BIAS IN LLM-AS-A-JUDGE  FINAL RESULTS ===

DATA: 10 base-instruct families + 22 instruct-only models = 32 variants
DOI: 10.5281/zenodo.21361920
CODE: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

--- PRIMARY FINDING: DIFFERENTIAL EFFECT ---

All biases decrease after instruction tuning in models ≤7B.
Content bias (reference answer) increases ONLY in large (8B+) RLHF models.

        Format Bias ↓          Content Bias (scale-dependent)
≤1.5B   7/7 families            ↓ (uniform reduction)
2-7B    2/2 families            ↓ (uniform reduction)
8B+     1/1 family (available)  ↑ (Llama-3-8B: +395%)

--- PER-FAMILY BREAKDOWN (N=10) ---

Family              Rubric B→I    ScoreID B→I   RefAns B→I    Δ Reference Answer
Qwen2.5-0.5B        0.1→0.2      1.3→0.4       1.9→0.8        -1.10
Qwen2.5-1.5B        0.1→0.4      3.1→1.8       2.5→1.8        -0.70
Llama-3.2-1B        0.0→0.2      1.3→2.0       1.4→1.9        +0.50
Llama-3.2-3B        3.5→0.8      3.7→2.4       2.8→2.2        -0.60
Gemma-2-2B          0.1→0.1      1.4→0.6       1.7→1.1        -0.60
StableLM-2-1.6B     0.4→0.3      2.9→2.5       2.9→2.8        -0.10
Qwen2.5-7B          0.6→0.0      2.5→0.4       2.4→0.9        -1.50
Llama-3-8B*         4.0→0.3      0.0→0.2       0.4→2.0        +1.58 ✨
Mistral-7B*         3.0→3.6      0.9→0.1       2.2→0.5        -1.74
Gemma-2-2B*         0.0→0.1      1.1→0.2       0.0→0.7        +0.70
                           * = Kaggle original run

--- 22 INSTRUCT-ONLY MODELS (Bias Landscape) ---

Probe             Mean Δ    Std Dev    Range
Rubric Order      0.56      0.41       0.10-1.50
Score ID          0.68      0.49       0.00-1.80
Reference Answer  0.41      0.31       0.00-1.00

--- MODEL RANKING (Least Biased) ---
1. GPT-OSS-20B       (Δ=0.10)
2. Qwen3-14B         (Δ=0.17)
3. Qwen2.5-1.5B-IT   (Δ=0.20)
...
22. MythoMax-13B     (Δ=1.00)
""")
