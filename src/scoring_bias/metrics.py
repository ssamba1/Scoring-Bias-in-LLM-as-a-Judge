"""
Statistical metrics for scoring-bias analysis.

Provides Cohen's d, pooled standard deviation, mean absolute deviation,
and effect size interpretation utilities.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from statistics import mean, stdev
import math


def pooled_std(
    group1: List[float],
    group2: List[float],
) -> Optional[float]:
    """Compute pooled standard deviation for two independent groups.

    Args:
        group1: First group of scores.
        group2: Second group of scores.

    Returns:
        Pooled standard deviation, or None if either group has < 2 elements.
    """
    if len(group1) < 2 or len(group2) < 2:
        return None

    n1, n2 = len(group1), len(group2)
    var1 = stdev(group1) ** 2
    var2 = stdev(group2) ** 2

    pooled_num = (n1 - 1) * var1 + (n2 - 1) * var2
    pooled = math.sqrt(pooled_num / (n1 + n2 - 2))
    return pooled if pooled > 0 else None


def cohens_d(
    group1: List[float],
    group2: List[float],
) -> Optional[float]:
    """Compute Cohen's d effect size between two groups.

    A measure of the standardized mean difference.
    Interpretation: 0.2 = small, 0.5 = medium, 0.8 = large.

    Args:
        group1: First group of scores.
        group2: Second group of scores.

    Returns:
        Cohen's d value, or None if cannot compute.
    """
    if not group1 or not group2:
        return None
    if len(group1) < 2 or len(group2) < 2:
        return None

    pooled = pooled_std(group1, group2)
    if pooled is None or pooled == 0.0:
        return None

    diff = mean(group1) - mean(group2)
    return diff / pooled


def mean_absolute_deviation(
    scores: List[float],
    center: Optional[float] = None,
) -> Optional[float]:
    """Compute mean absolute deviation from a center point.

    If center is None, the mean of the scores is used.

    Args:
        scores: List of score values.
        center: Center point to measure deviation from (default: mean).

    Returns:
        Mean absolute deviation, or None if list is empty.
    """
    if not scores:
        return None

    if center is None:
        center = mean(scores)

    return sum(abs(s - center) for s in scores) / len(scores)


def effect_size_interpretation(d: float) -> str:
    """Interpret Cohen's d effect size qualitatively.

    Args:
        d: Cohen's d value.

    Returns:
        Qualitative description: "negligible", "small", "medium", or "large".
    """
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    else:
        return "large"


def family_from_model(model_name: str) -> str:
    """Extract model family from a model name string.

    Args:
        model_name: e.g. "Meta-Llama-3.1-8B", "gemma-2-27b-it"

    Returns:
        Family name: "Llama", "Gemma", "Qwen", "Mistral", or "Other".
    """
    lower = model_name.lower()
    if "llama" in lower:
        return "Llama"
    elif "gemma" in lower:
        return "Gemma"
    elif "qwen" in lower:
        return "Qwen"
    elif "mistral" in lower:
        return "Mistral"
    elif "deepseek" in lower:
        return "DeepSeek"
    elif "mixtral" in lower:
        return "Mixtral"
    elif "falcon" in lower:
        return "Falcon"
    elif "gpt" in lower or "openai" in lower:
        return "OpenAI"
    else:
        return "Other"


def size_from_model(model_name: str) -> str:
    """Extract model size (parameter count) from a model name.

    Args:
        model_name: e.g. "Meta-Llama-3.1-8B" or "gemma-2-27b"

    Returns:
        Size string e.g. "8B", "27B", "70B", or "Unknown".
    """
    import re
    match = re.search(r'(\d+)\s*[Bb]', model_name)
    if match:
        return match.group(1) + "B"
    return "Unknown"
