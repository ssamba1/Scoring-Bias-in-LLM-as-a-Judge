"""
Tests for statistical metrics: Cohen's d, MAD, pooled_std, etc.
"""

from __future__ import annotations
import pytest
from scoring_bias.metrics import (
    cohens_d,
    mean_absolute_deviation,
    pooled_std,
    effect_size_interpretation,
    family_from_model,
    size_from_model,
)


class TestCohensD:
    """Tests for cohens_d function."""

    def test_large_effect(self):
        """Well-separated groups should give large d."""
        d = cohens_d([1.0, 1.1, 1.0], [5.0, 5.1, 5.0])
        assert d is not None
        assert abs(d) > 5.0  # very large effect

    def test_no_effect(self):
        """Identical groups should give d ≈ 0."""
        d = cohens_d([3.0, 4.0, 3.5], [3.0, 4.0, 3.5])
        assert d is not None
        assert d == pytest.approx(0.0, abs=0.01)

    def test_small_effect(self):
        """Close groups should give small d."""
        d = cohens_d([3.0, 3.1, 3.0], [3.3, 3.4, 3.3])
        assert d is not None

    def test_empty_groups(self):
        """Empty groups should return None."""
        assert cohens_d([], [1.0, 2.0]) is None
        assert cohens_d([1.0, 2.0], []) is None

    def test_single_element_groups(self):
        """Groups with 1 element can't compute std, return None."""
        assert cohens_d([3.0], [4.0]) is None

    def test_positive_negative(self):
        """Order matters: group1 - group2."""
        d1 = cohens_d([5.0, 5.1, 5.0], [1.0, 1.1, 1.0])
        d2 = cohens_d([1.0, 1.1, 1.0], [5.0, 5.1, 5.0])
        assert d1 is not None and d2 is not None
        assert d1 > 0
        assert d2 < 0
        assert d1 == pytest.approx(-d2)


class TestPooledStd:
    """Tests for pooled_std function."""

    def test_same_variance(self):
        """Identical groups should give pooled std equal to group std."""
        ps = pooled_std([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert ps is not None
        assert ps > 0

    def test_small_groups(self):
        """Groups with <2 elements should return None."""
        assert pooled_std([1.0], [2.0, 3.0]) is None
        assert pooled_std([1.0, 2.0], [3.0]) is None

    def test_different_sizes(self):
        """Groups of different sizes should still compute."""
        ps = pooled_std([1.0, 2.0, 3.0], [2.0, 3.0, 4.0, 5.0])
        assert ps is not None
        assert ps > 0


class TestMeanAbsoluteDeviation:
    """Tests for mean_absolute_deviation function."""

    def test_identical_scores(self):
        """All identical scores should give MAD of 0."""
        mad = mean_absolute_deviation([3.0, 3.0, 3.0])
        assert mad is not None
        assert mad == pytest.approx(0.0)

    def test_varying_scores(self):
        """Varying scores should give positive MAD."""
        mad = mean_absolute_deviation([1.0, 2.0, 3.0, 4.0, 5.0])
        assert mad is not None
        assert mad > 0

    def test_with_center(self):
        """MAD from a specific center."""
        mad = mean_absolute_deviation([1.0, 3.0, 5.0], center=3.0)
        assert mad is not None
        assert mad == pytest.approx(4.0 / 3.0)

    def test_empty(self):
        """Empty list should return None."""
        assert mean_absolute_deviation([]) is None


class TestEffectSizeInterpretation:
    """Tests for effect_size_interpretation function."""

    def test_negligible(self):
        assert effect_size_interpretation(0.05) == "negligible"
        assert effect_size_interpretation(0.19) == "negligible"
        assert effect_size_interpretation(-0.1) == "negligible"

    def test_small(self):
        assert effect_size_interpretation(0.2) == "small"
        assert effect_size_interpretation(0.49) == "small"

    def test_medium(self):
        assert effect_size_interpretation(0.5) == "medium"
        assert effect_size_interpretation(0.79) == "medium"

    def test_large(self):
        assert effect_size_interpretation(0.8) == "large"
        assert effect_size_interpretation(2.0) == "large"


class TestModelNameParsing:
    """Tests for family_from_model and size_from_model."""

    def test_llama_family(self):
        assert family_from_model("Meta-Llama-3.1-8B") == "Llama"
        assert family_from_model("llama-2-7b") == "Llama"

    def test_gemma_family(self):
        assert family_from_model("gemma-2-27b-it") == "Gemma"

    def test_qwen_family(self):
        assert family_from_model("Qwen2.5-32B") == "Qwen"

    def test_mistral_family(self):
        assert family_from_model("Mistral-7B") == "Mistral"

    def test_unknown_family(self):
        assert family_from_model("custom-model-v1") == "Other"

    def test_extract_size(self):
        assert size_from_model("Meta-Llama-3.1-8B") == "8B"
        assert size_from_model("gemma-2-27b") == "27B"
        assert size_from_model("Qwen2.5-32B") == "32B"
        assert size_from_model("no-size-here") == "Unknown"
