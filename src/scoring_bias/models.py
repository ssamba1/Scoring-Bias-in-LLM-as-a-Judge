"""
Data models for scoring-bias analysis.

Defines the core data structures used throughout the analysis pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ProbeType(str, Enum):
    """The three bias probes used in the study."""

    RUBRIC_ORDER = "rubric_order"
    SCORE_ID = "score_id"
    REFERENCE_ANSWER = "reference_answer"


@dataclass
class ScoreRecord:
    """A single score from a model-judge on one probe-item."""

    model_name: str
    probe: ProbeType
    item_id: str
    condition: str  # e.g. "normal", "reversed", "low_id", "high_id", "present", "absent"
    score: float  # 1-5 scale
    raw_response: Optional[str] = None
    is_base: bool = False  # True = base variant, False = instruct variant


@dataclass
class ProbeResult:
    """Aggregated results for one probe on one model."""

    model_name: str
    probe: ProbeType
    condition_scores: Dict[str, List[float]] = field(default_factory=dict)
    delta: Optional[float] = None  # mean bias delta
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    flip_rate: Optional[float] = None  # fraction of items where order flips preference
    is_base: bool = False

    @property
    def mean_abs_bias(self) -> Optional[float]:
        """Mean absolute delta across all conditions."""
        if self.delta is not None:
            return abs(self.delta)
        return None


@dataclass
class ModelProfile:
    """Full profile of a single judge model."""

    name: str
    family: str  # e.g. "Llama", "Gemma", "Qwen", "Mistral"
    size: str  # e.g. "8B", "70B", "7B"
    is_base: bool = False
    probe_results: Dict[ProbeType, ProbeResult] = field(default_factory=dict)

    @property
    def avg_delta(self) -> Optional[float]:
        """Average delta across all probes."""
        deltas = [
            pr.delta
            for pr in self.probe_results.values()
            if pr.delta is not None
        ]
        if not deltas:
            return None
        return sum(deltas) / len(deltas)

    @property
    def avg_flip_rate(self) -> Optional[float]:
        """Average flip rate across all probes."""
        rates = [
            pr.flip_rate
            for pr in self.probe_results.values()
            if pr.flip_rate is not None
        ]
        if not rates:
            return None
        return sum(rates) / len(rates)


@dataclass
class BiasResult:
    """Top-level container for all bias analysis results."""

    model_profiles: Dict[str, ModelProfile] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_model(self, name: str) -> Optional[ModelProfile]:
        return self.model_profiles.get(name)

    @property
    def model_names(self) -> List[str]:
        return list(self.model_profiles.keys())

    @property
    def num_models(self) -> int:
        return len(self.model_profiles)


@dataclass
class ComparisonResult:
    """Result of comparing base vs instruct variants of a model family."""

    family: str  # e.g. "Llama"
    base_name: str
    instruct_name: str
    base_deltas: Dict[ProbeType, float] = field(default_factory=dict)
    instruct_deltas: Dict[ProbeType, float] = field(default_factory=dict)
    delta_of_deltas: Dict[ProbeType, float] = field(default_factory=dict)
    # Positive means base is more biased than instruct

    @property
    def avg_delta_of_deltas(self) -> Optional[float]:
        vals = list(self.delta_of_deltas.values())
        if not vals:
            return None
        return sum(vals) / len(vals)
