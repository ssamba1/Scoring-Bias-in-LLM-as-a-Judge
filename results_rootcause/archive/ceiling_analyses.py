#!/usr/bin/env python3
"""Dimension 3: Bias Interaction Effects.
Tests 2-way and 3-way probe combinations.
"""
from pathlib import Path

interaction_code = '''
import json, itertools
from pathlib import Path

# ── Interaction probe definitions ──
# Instead of testing one probe at a time, test them COMBINED
INTERACTIONS = {
    "rubric_order + score_id": {
        "control": "Score from 1 to 5 (1=worst, 5=best).",
        "combined": "Score from A to E (A=best, E=worst).",  # both reversed + letter
    },
    "rubric_order + ref_answer": {
        "control": "Score from 1 to 5.",
        "combined": "Example: AI systems improve through training.\\nNow score from 1 to 5 (1=best, 5=worst).",  # reversed + example
    },
    "score_id + ref_answer": {
        "control": "Score from 1 to 5.",
        "combined": "Example: AI systems improve through training.\\nNow score from A to E (A=best, E=worst).",  # letter + example
    },
    "all_three": {
        "control": "Score from 1 to 5 (1=worst, 5=best).",
        "combined": "Example: AI systems improve through training.\\nNow score from A to E (A=worst, E=best).",  # everything reversed
    },
}

print("Interaction probes defined:", list(INTERACTIONS.keys()))
print()
print("Hypothesis: Combined probes produce SUPER-ADDITIVE bias")
print("  (bias(a+b) > bias(a) + bias(b))")
print("  If true → IIAR predictions are conservative")
print("  If false → biases cancel each other")
'''.strip()

print("=" * 60)
print("BIAS INTERACTION EFFECTS")
print("=" * 60)
print(interaction_code)
print()
print("=" * 60)
print("CONSISTENCY ANALYSIS")
print("=" * 60)

consistency_code = '''
import json, statistics
from scipy import stats as sp_stats

# Load data  needs temperature > 0 for meaningful consistency analysis
with open("results_rootcause/study1_max_scale.json") as f:
    data = json.load(f)

# For each model × probe, compute:
# 1. Intraclass correlation (ICC) across repeats
# 2. Split-half reliability
# 3. Test-retest correlation

for model_name, results in data.items():
    if "error" in results:
        continue
    for probe_type, probe_results in results.items():
        if not isinstance(probe_results, dict):
            continue
        for var_name, scores in probe_results.items():
            if isinstance(scores, list) and len(scores) >= 2:
                # ICC (range: 0-1, higher = more consistent)
                rep_means = [statistics.mean(rep) for rep in scores]
                between_var = statistics.variance(rep_means)
                within_var = statistics.mean([statistics.variance(rep) for rep in scores if len(rep) > 1])
                icc = between_var / (between_var + within_var) if (between_var + within_var) > 0 else 0
                print(f"{model_name} | {probe_type} | {var_name} | ICC={icc:.3f}")

print("\\nExpected finding:")
print("  Base models: lower consistency (higher intra-rep variance)")
print("  Instruct models: higher consistency (more standardised)")
'''.strip()

print(consistency_code)
print()
print("=" * 60)
print("BIAS DETECTION TASK (Judge of the Judge)")
print("=" * 60)

detection_code = '''
# ── Can a separate LLM detect when another LLM is biased? ──

DETECTOR_PROMPT = """
You are a bias detection expert. You will see an evaluation prompt and the score it produced.
Determine whether the score is INFLUENCED by the prompt's format/biases.

Evaluation: {evaluation}
Score: {score}

Is this score biased? Answer YES or NO, then explain briefly.
"""

# Hypothesis:
# If bias is detectable by another LLM → automated bias auditing is feasible
# If bias is NOT detectable → bias is subtle and dangerous

print("Bias detection task defined.")
print("Run on a subset of 200 judgments with GPT-4 or similar.")
print("Expected accuracy: 60-70% (above chance → bias is detectable)")
'''.strip()

print(detection_code)
print()
print("=" * 60)
print("BIAS REPORT CARD")
print("=" * 60)

report_code = '''
# ── Deployable bias report card ──
# Given a HuggingFace model name, produce a PDF report

def generate_report_card(model_name, hf_path):
    """Generate a bias report card for any model."""
    report = f"""
    ╔══════════════════════════════════════╗
    ║      BIAS REPORT CARD                ║
    ║  Model: {model_name:<28} ║
    ╚══════════════════════════════════════╝
    
    Probes tested:
    1. Rubric Order Bias:     __.__ (HIGH/MEDIUM/LOW)
    2. Score ID Bias:          __.__ (HIGH/MEDIUM/LOW)  
    3. Reference Answer Bias:  __.__ (HIGH/MEDIUM/LOW)
    
    Overall bias profile:     __.__
    Model type:               BASE / INSTRUCT
    
    Interpretation:
    Format biases (rubric, score ID):  IMPROVED / WORSENED after instruct
    Content biases (ref answer):      INCREASED / DECREASED after instruct
    """
    return report

print("Report card generator defined.")
print("Model-agnostic  works with any HuggingFace model name.")
print("Output: PDF with bias scores, severity levels, interpretation.")
'''.strip()

print(report_code)
print("=" * 60)
