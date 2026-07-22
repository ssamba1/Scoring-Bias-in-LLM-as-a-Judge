"""
Tests for data models: ModelProfile, ProbeResult, ScoreRecord, etc.
"""

from __future__ import annotations
import pytest
from scoring_bias.models import (
    ProbeType,
    ScoreRecord,
    ProbeResult,
    ModelProfile,
    BiasResult,
    ComparisonResult,
)


class TestScoreRecord:
    """Tests for ScoreRecord dataclass."""

    def test_create_basic(self):
        """Create a basic ScoreRecord with required fields."""
        rec = ScoreRecord(
            model_name="llama-3.1-8b",
            probe=ProbeType.RUBRIC_ORDER,
            item_id="item_001",
            condition="normal",
            score=4.0,
        )
        assert rec.model_name == "llama-3.1-8b"
        assert rec.probe == ProbeType.RUBRIC_ORDER
        assert rec.score == 4.0

    def test_default_fields(self):
        """Default fields should be populated correctly."""
        rec = ScoreRecord(
            model_name="test",
            probe=ProbeType.SCORE_ID,
            item_id="i1",
            condition="reversed",
            score=3.5,
        )
        assert rec.raw_response is None
        assert rec.is_base is False

    def test_is_base_flag(self):
        """The is_base flag should work for base models."""
        rec = ScoreRecord(
            model_name="llama-3.1-8b",
            probe=ProbeType.REFERENCE_ANSWER,
            item_id="i1",
            condition="present",
            score=3.0,
            is_base=True,
        )
        assert rec.is_base is True


class TestProbeResult:
    """Tests for ProbeResult dataclass."""

    def test_create_empty(self):
        """ProbeResult should initialize with empty condition_scores."""
        pr = ProbeResult(model_name="test", probe=ProbeType.RUBRIC_ORDER)
        assert pr.condition_scores == {}
        assert pr.delta is None

    def test_mean_abs_bias_without_delta(self):
        """Without delta, mean_abs_bias should be None."""
        pr = ProbeResult(model_name="test", probe=ProbeType.RUBRIC_ORDER)
        assert pr.mean_abs_bias is None

    def test_mean_abs_bias_with_delta(self):
        """With delta, mean_abs_bias should be abs(delta)."""
        pr = ProbeResult(
            model_name="test",
            probe=ProbeType.RUBRIC_ORDER,
            delta=0.5,
        )
        assert pr.mean_abs_bias == 0.5

    def test_negative_delta_abs(self):
        """mean_abs_bias should always be positive."""
        pr = ProbeResult(
            model_name="test",
            probe=ProbeType.RUBRIC_ORDER,
            delta=-0.3,
        )
        assert pr.mean_abs_bias == 0.3


class TestModelProfile:
    """Tests for ModelProfile dataclass."""

    @pytest.fixture
    def profile_with_results(self):
        """Create a profile with partial probe results."""
        return ModelProfile(
            name="test-model",
            family="Llama",
            size="8B",
            is_base=False,
            probe_results={
                ProbeType.RUBRIC_ORDER: ProbeResult(
                    model_name="test-model",
                    probe=ProbeType.RUBRIC_ORDER,
                    delta=0.5,
                    flip_rate=0.3,
                ),
                ProbeType.SCORE_ID: ProbeResult(
                    model_name="test-model",
                    probe=ProbeType.SCORE_ID,
                    delta=-0.2,
                    flip_rate=0.1,
                ),
            },
        )

    def test_avg_delta(self, profile_with_results):
        """avg_delta should be mean of all probe deltas."""
        avg = profile_with_results.avg_delta
        assert avg is not None
        assert avg == pytest.approx(0.15)  # (0.5 + (-0.2)) / 2

    def test_avg_flip_rate(self, profile_with_results):
        """avg_flip_rate should be mean of all flip rates."""
        avg = profile_with_results.avg_flip_rate
        assert avg is not None
        assert avg == pytest.approx(0.2)  # (0.3 + 0.1) / 2

    def test_profile_without_results(self):
        """Profile without probe_results should have None averages."""
        profile = ModelProfile(name="empty", family="Other", size="Unknown")
        assert profile.avg_delta is None
        assert profile.avg_flip_rate is None

    def test_empty_probe_results(self):
        """Profile with empty probe_results dict should have None averages."""
        profile = ModelProfile(
            name="empty",
            family="Other",
            size="Unknown",
            probe_results={},
        )
        assert profile.avg_delta is None
        assert profile.avg_flip_rate is None


class TestBiasResult:
    """Tests for BiasResult container."""

    def test_empty_result(self):
        """Empty BiasResult should have no models."""
        result = BiasResult()
        assert result.num_models == 0
        assert result.model_names == []

    def test_add_model(self):
        """Adding models should update counts."""
        result = BiasResult()
        result.model_profiles["llama-8b"] = ModelProfile(
            name="llama-8b", family="Llama", size="8B"
        )
        result.model_profiles["gemma-27b"] = ModelProfile(
            name="gemma-27b", family="Gemma", size="27B"
        )
        assert result.num_models == 2
        assert "llama-8b" in result.model_names

    def test_get_model(self):
        """get_model should return correct profile or None."""
        result = BiasResult()
        result.model_profiles["test"] = ModelProfile(
            name="test", family="Test", size="1B"
        )
        assert result.get_model("test") is not None
        assert result.get_model("nonexistent") is None


class TestComparisonResult:
    """Tests for ComparisonResult dataclass."""

    def test_create_comparison(self):
        """Create a basic comparison result."""
        comp = ComparisonResult(
            family="Llama",
            base_name="llama-8b",
            instruct_name="llama-8b-it",
        )
        assert comp.family == "Llama"
        assert comp.base_deltas == {}
        assert comp.delta_of_deltas == {}

    def test_delta_of_deltas_positive(self):
        """Delta of deltas should be positive when base is more biased."""
        comp = ComparisonResult(
            family="Llama",
            base_name="llama-8b",
            instruct_name="llama-8b-it",
            base_deltas={ProbeType.RUBRIC_ORDER: 0.8},
            instruct_deltas={ProbeType.RUBRIC_ORDER: 0.3},
            delta_of_deltas={ProbeType.RUBRIC_ORDER: 0.5},
        )
        assert comp.delta_of_deltas[ProbeType.RUBRIC_ORDER] == 0.5

    def test_avg_delta_of_deltas(self):
        """Average delta-of-deltas across probes."""
        comp = ComparisonResult(
            family="Llama",
            base_name="llama-8b",
            instruct_name="llama-8b-it",
            delta_of_deltas={
                ProbeType.RUBRIC_ORDER: 0.5,
                ProbeType.SCORE_ID: -0.2,
            },
        )
        assert comp.avg_delta_of_deltas == pytest.approx(0.15)

    def test_empty_delta_of_deltas(self):
        """No delta_of_deltas should yield None average."""
        comp = ComparisonResult(
            family="Llama",
            base_name="llama-8b",
            instruct_name="llama-8b-it",
        )
        assert comp.avg_delta_of_deltas is None


class TestProbeTypeEnum:
    """Tests for ProbeType enum."""

    def test_values(self):
        assert ProbeType.RUBRIC_ORDER.value == "rubric_order"
        assert ProbeType.SCORE_ID.value == "score_id"
        assert ProbeType.REFERENCE_ANSWER.value == "reference_answer"

    def test_membership(self):
        assert "rubric_order" in [p.value for p in ProbeType]
        assert "score_id" in [p.value for p in ProbeType]
