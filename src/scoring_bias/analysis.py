"""
Core analysis functions for scoring-bias research.

Provides delta computation, flip-rate analysis, bootstrap confidence
intervals, and summary statistics for LLM-as-a-Judge bias assessment.
"""

from __future__ import annotations
import random
from typing import Dict, List, Optional, Tuple, Callable
from statistics import mean, stdev
import math

from scoring_bias.models import (
    ProbeType,
    ScoreRecord,
    ProbeResult,
    ModelProfile,
    BiasResult,
    ComparisonResult,
)


def compute_delta(
    control_scores: List[float],
    treatment_scores: List[float],
) -> Optional[float]:
    """Compute the bias delta: mean(treatment) - mean(control).

    A positive delta means the treatment condition increases scores
    (leniency bias). A negative delta means it decreases scores
    (strictness bias).

    Args:
        control_scores: Scores under the control (normal) condition.
        treatment_scores: Scores under the biased condition.

    Returns:
        The mean difference, or None if either list is empty.
    """
    if not control_scores or not treatment_scores:
        return None
    return mean(treatment_scores) - mean(control_scores)


def compute_flip_rate(
    control_scores: List[float],
    treatment_scores: List[float],
    threshold: float = 0.5,
) -> Optional[float]:
    """Compute the flip rate between two conditions.

    For paired items, the flip rate is the fraction of items where
    the score direction changes (i.e. one condition preferred the
    response more than the other).

    Args:
        control_scores: Scores under control condition (per item).
        treatment_scores: Scores under treatment condition (per item).
        threshold: Minimum absolute difference to count as a flip.

    Returns:
        Fraction of items that flipped, or None if lists are empty/mismatched.
    """
    if len(control_scores) != len(treatment_scores):
        return None
    if not control_scores:
        return None

    flips = sum(
        1 for c, t in zip(control_scores, treatment_scores)
        if abs(c - t) >= threshold
    )
    return flips / len(control_scores)


def bootstrap_ci(
    control_scores: List[float],
    treatment_scores: List[float],
    n_resamples: int = 10_000,
    ci: float = 0.95,
    seed: Optional[int] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Bootstrap confidence interval for the bias delta.

    Resamples paired deltas with replacement and computes the
    percentile confidence interval.

    Args:
        control_scores: Scores under control condition.
        treatment_scores: Scores under treatment condition.
        n_resamples: Number of bootstrap resamples.
        ci: Confidence level (e.g., 0.95).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (delta, ci_lower, ci_upper). All None if inputs are invalid.
    """
    if len(control_scores) != len(treatment_scores):
        return None, None, None
    if not control_scores:
        return None, None, None

    n = len(control_scores)
    paired_deltas = [t - c for c, t in zip(control_scores, treatment_scores)]
    observed_delta = mean(paired_deltas)

    if seed is not None:
        random.seed(seed)

    # Bootstrap resampling
    boot_deltas: List[float] = []
    for _ in range(n_resamples):
        resample = [random.choice(paired_deltas) for _ in range(n)]
        boot_deltas.append(mean(resample))

    # Percentile CI
    alpha = 1.0 - ci
    lower_pct = (alpha / 2) * 100
    upper_pct = (1.0 - alpha / 2) * 100

    boot_deltas.sort()
    lower_idx = int(n_resamples * alpha / 2)
    upper_idx = int(n_resamples * (1.0 - alpha / 2))

    ci_lower = boot_deltas[lower_idx] if lower_idx < n_resamples else None
    ci_upper = boot_deltas[upper_idx] if upper_idx < n_resamples else None

    return observed_delta, ci_lower, ci_upper


def compute_model_summary(
    model_name: str,
    scores_by_probe: Dict[ProbeType, Dict[str, List[float]]],
    is_base: bool = False,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ModelProfile:
    """Build a ModelProfile from per-probe score dictionaries.

    Args:
        model_name: Name of the model.
        scores_by_probe: Dict mapping ProbeType -> condition -> scores.
        is_base: Whether this is a base (vs instruct) variant.
        n_bootstrap: Bootstrap resamples for CI.
        seed: Random seed.

    Returns:
        Populated ModelProfile.
    """
    from scoring_bias.metrics import (
        family_from_model,
        size_from_model,
    )

    profile = ModelProfile(
        name=model_name,
        family=family_from_model(model_name),
        size=size_from_model(model_name),
        is_base=is_base,
    )

    for probe, conditions in scores_by_probe.items():
        # Determine which conditions are control vs treatment
        control_conditions = [k for k in conditions if "normal" in k.lower()
                              or "control" in k.lower() or "present" in k.lower()]
        treatment_conditions = [k for k in conditions if k not in control_conditions]

        # Flatten scores from control and treatment conditions
        control_scores: List[float] = []
        treatment_scores: List[float] = []
        for ctrl_key in control_conditions:
            control_scores.extend(conditions.get(ctrl_key, []))
        for trt_key in treatment_conditions:
            treatment_scores.extend(conditions.get(trt_key, []))

        delta, ci_l, ci_u = bootstrap_ci(
            control_scores, treatment_scores,
            n_resamples=n_bootstrap, seed=seed,
        )
        flip_rate = compute_flip_rate(control_scores, treatment_scores)

        result = ProbeResult(
            model_name=model_name,
            probe=probe,
            condition_scores=conditions,
            delta=delta,
            ci_lower=ci_l,
            ci_upper=ci_u,
            flip_rate=flip_rate,
            is_base=is_base,
        )
        profile.probe_results[probe] = result

    return profile


def compute_base_instruct_comparison(
    base_name: str,
    instruct_name: str,
    results: BiasResult,
) -> Optional[ComparisonResult]:
    """Compare base vs instruct variants of the same model family.

    Args:
        base_name: Name of the base model.
        instruct_name: Name of the instruct model.
        results: Full BiasResult containing both profiles.

    Returns:
        ComparisonResult with delta-of-deltas, or None if either missing.
    """
    base = results.get_model(base_name)
    instr = results.get_model(instruct_name)
    if base is None or instr is None:
        return None

    family = base.family
    comp = ComparisonResult(
        family=family,
        base_name=base_name,
        instruct_name=instruct_name,
    )

    for probe in ProbeType:
        base_pr = base.probe_results.get(probe)
        instr_pr = instr.probe_results.get(probe)

        if base_pr is not None and base_pr.delta is not None:
            comp.base_deltas[probe] = base_pr.delta
        if instr_pr is not None and instr_pr.delta is not None:
            comp.instruct_deltas[probe] = instr_pr.delta

        if (base_pr is not None and base_pr.delta is not None
                and instr_pr is not None and instr_pr.delta is not None):
            comp.delta_of_deltas[probe] = abs(base_pr.delta) - abs(instr_pr.delta)

    return comp


def load_scores_from_csv(
    csv_path: str,
) -> BiasResult:
    """Load analysis results from a CSV file.

    CSV must have columns: model_name, probe, condition, score, item_id
    and optionally: is_base, raw_response.

    Args:
        csv_path: Path to CSV file.

    Returns:
        Populated BiasResult.
    """
    import csv

    # Collect raw records
    records: List[ScoreRecord] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            probe = ProbeType(row["probe"])
            records.append(ScoreRecord(
                model_name=row["model_name"],
                probe=probe,
                item_id=row.get("item_id", ""),
                condition=row["condition"],
                score=float(row["score"]),
                raw_response=row.get("raw_response"),
                is_base=row.get("is_base", "false").lower() == "true",
            ))

    # Aggregate into probes
    by_model_probe: Dict[tuple, Dict[str, List[float]]] = {}
    for rec in records:
        key = (rec.model_name, rec.probe.value)
        if key not in by_model_probe:
            by_model_probe[key] = {}
        if rec.condition not in by_model_probe[key]:
            by_model_probe[key][rec.condition] = []
        by_model_probe[key][rec.condition].append(rec.score)

    result = BiasResult()
    seen_models: Dict[str, bool] = {}

    # Determine is_base from records
    model_is_base: Dict[str, bool] = {}
    for rec in records:
        if rec.model_name not in model_is_base:
            model_is_base[rec.model_name] = rec.is_base

    for (mname, probe_str), conditions in by_model_probe.items():
        if mname not in result.model_profiles:
            is_base = model_is_base.get(mname, False)
            profile = ModelProfile(
                name=mname,
                family=family_from_model(mname),
                size=size_from_model(mname),
                is_base=is_base,
            )
            result.model_profiles[mname] = profile

        probe = ProbeType(probe_str)
        delta, ci_l, ci_u = bootstrap_ci(
            conditions.get("normal", []),
            conditions.get("reversed", conditions.get("treatment", [])),
        )
        flip_rate = compute_flip_rate(
            conditions.get("normal", []),
            conditions.get("reversed", conditions.get("treatment", [])),
        )
        pr = ProbeResult(
            model_name=mname,
            probe=probe,
            condition_scores=conditions,
            delta=delta,
            ci_lower=ci_l,
            ci_upper=ci_u,
            flip_rate=flip_rate,
            is_base=model_is_base.get(mname, False),
        )
        result.model_profiles[mname].probe_results[probe] = pr

    return result
