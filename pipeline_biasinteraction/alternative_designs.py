#!/usr/bin/env python3
"""Alternative experimental designs for the bias interaction study.
Provides multiple design options depending on resources and goals.
"""
import json
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class ExperimentalDesign:
    name: str
    description: str
    biases_tested: List[str]
    items_needed: int
    judges_needed: int
    conditions_per_item: int
    total_api_calls: int
    estimated_cost: float  # USD
    timeline_weeks: int
    difficulty: str  # Easy/Medium/Hard
    notes: str

def design1_quick_sweep():
    """
    Design 1: Quick sweep (3 biases, 2 models, 100 items)
    Fastest path to publication-quality results.
    """
    return ExperimentalDesign(
        name="Quick Sweep",
        description="Test 3 bias interactions with 2 judges and 100 items. Fastest path to results.",
        biases_tested=["position", "verbosity", "sentiment"],
        items_needed=100,
        judges_needed=2,
        conditions_per_item=8,
        total_api_calls=100 * 8 * 2 * 3,  # 4,800
        estimated_cost=5.0,
        timeline_weeks=2,
        difficulty="Easy",
        notes="Minimum viable experiment. Good for pilot data or tight deadlines."
    )

def design2_standard():
    """
    Design 2: Standard (3 biases, 5 judges, 400 items)
    The main proposal  comprehensive enough for publication.
    """
    return ExperimentalDesign(
        name="Standard (Recommended)",
        description="Full design: 3 bias types × 5 judges × 400 items. Publication-ready.",
        biases_tested=["position", "verbosity", "sentiment"],
        items_needed=400,
        judges_needed=5,
        conditions_per_item=8,
        total_api_calls=400 * 8 * 5 * 3,  # 48,000
        estimated_cost=28.0,
        timeline_weeks=4,
        difficulty="Medium",
        notes="Balances comprehensiveness with cost. Our main proposal."
    )

def design3_comprehensive():
    """
    Design 3: Comprehensive (5 biases, 7 judges, 1000 items)
    Maximum coverage. Adds authority bias and bandwagon bias.
    """
    return ExperimentalDesign(
        name="Comprehensive",
        description="5 bias types (adds authority, bandwagon) × 7 judges × 1000 items.",
        biases_tested=["position", "verbosity", "sentiment", "authority", "bandwagon"],
        items_needed=1000,
        judges_needed=7,
        conditions_per_item=32,  # 2×2×2×2×2
        total_api_calls=1000 * 32 * 7 * 3,  # 672,000
        estimated_cost=350.0,
        timeline_weeks=8,
        difficulty="Hard",
        notes="Full factorial with 5 binary factors. High cost but most comprehensive."
    )

def design4_budget():
    """
    Design 4: Budget (2 biases, 3 judges, 200 items)
    For limited API budget.
    """
    return ExperimentalDesign(
        name="Budget",
        description="2 bias types (position, verbosity) × 3 judges × 200 items.",
        biases_tested=["position", "verbosity"],
        items_needed=200,
        judges_needed=3,
        conditions_per_item=4,  # 2×2
        total_api_calls=200 * 4 * 3 * 3,  # 7,200
        estimated_cost=4.0,
        timeline_weeks=2,
        difficulty="Easy",
        notes="Only tests position × verbosity interaction. Loses sentiment analysis."
    )

def design5_cross_domain():
    """
    Design 5: Cross-domain (3 biases, 3 judges, 5 domain comparisons)
    Tests whether bias interactions differ across domains (code, creative, medical, etc.)
    """
    return ExperimentalDesign(
        name="Cross-Domain",
        description="3 biases × 3 judges × 5 domains (code, creative, technical, reasoning, business).",
        biases_tested=["position", "verbosity", "sentiment"],
        items_needed=500,  # 100 per domain
        judges_needed=3,
        conditions_per_item=8,
        total_api_calls=500 * 8 * 3 * 3,  # 36,000
        estimated_cost=18.0,
        timeline_weeks=5,
        difficulty="Medium",
        notes="Adds domain as a factor. Tests whether bias interactions generalize across domains."
    )

def design6_model_size():
    """
    Design 6: Model size scaling (3 biases, same-family models at different sizes)
    Tests whether bias interactions scale with model parameters.
    """
    return ExperimentalDesign(
        name="Model Size Scaling",
        description="3 biases × same-family models at 3 sizes (e.g., Llama 3 8B, 70B, 405B).",
        biases_tested=["position", "verbosity", "sentiment"],
        items_needed=200,
        judges_needed=3,  # same family, different sizes
        conditions_per_item=8,
        total_api_calls=200 * 8 * 3 * 3,  # 14,400
        estimated_cost=15.0,
        timeline_weeks=4,
        difficulty="Medium",
        notes="Tests whether bias interaction patterns change with model scale."
    )

def design7_mitigation():
    """
    Design 7: Mitigation comparison (3 biases, 5 judges, with/without debiasing)
    Tests whether existing debiasing methods work under multi-bias conditions.
    """
    return ExperimentalDesign(
        name="Mitigation Validation",
        description="3 biases × 5 judges × 2 conditions (with/without debiasing).",
        biases_tested=["position", "verbosity", "sentiment"],
        items_needed=400,
        judges_needed=5,
        conditions_per_item=16,  # 8 conditions × 2 debiasing conditions
        total_api_calls=400 * 16 * 5 * 3,  # 96,000
        estimated_cost=55.0,
        timeline_weeks=6,
        difficulty="Hard",
        notes="Tests whether standard debiasing (swap-and-average, etc.) works when multiple biases co-occur."
    )

def print_comparison():
    designs = [
        design1_quick_sweep(),
        design2_standard(),
        design3_comprehensive(),
        design4_budget(),
        design5_cross_domain(),
        design6_model_size(),
        design7_mitigation(),
    ]
    
    print("="*100)
    print("BIAS INTERACTION EXPERIMENT  ALTERNATIVE DESIGNS")
    print("="*100)
    print(f"{'Design':<25} {'Items':<8} {'Judges':<8} {'Calls':<10} {'Cost':<8} {'Weeks':<8} {'Difficulty':<10}")
    print("-"*100)
    for d in designs:
        calls = f"{d.total_api_calls/1000:.0f}K"
        cost = f"${d.estimated_cost:.0f}"
        print(f"{d.name:<25} {d.items_needed:<8} {d.judges_needed:<8} {calls:<10} {cost:<8} {d.timeline_weeks:<8} {d.difficulty:<10}")
    
    print("\n" + "="*100)
    print("RECOMMENDATION")
    print("="*100)
    print("""
    For a first paper: Design 2 (Standard)  balances rigor and cost.
    For a pilot/exploratory: Design 1 (Quick Sweep)  get results in 2 weeks.
    For maximum impact: Design 3 (Comprehensive)  most complete, but costly.
    For ISEF: Design 2 or 5  thorough enough for competition, feasible timeline.
    """)

if __name__ == "__main__":
    print_comparison()
    
    # Save designs to JSON
    designs = [
        design1_quick_sweep(),
        design2_standard(),
        design3_comprehensive(),
        design4_budget(),
        design5_cross_domain(),
        design6_model_size(),
        design7_mitigation(),
    ]
    
    with open(__file__ + ".json", "w") as f:
        json.dump([asdict(d) for d in designs], f, indent=2)
    print(f"Designs saved to alternative_designs.py.json")
