"""
Tests for core analysis functions: delta, flip rate, bootstrap CI.
"""

from __future__ import annotations
import pytest
from statistics import mean
from scoring_bias.analysis import (
    compute_delta,
    compute_flip_rate,
    bootstrap_ci,
    compute_model_summary,
    compute_base_instruct_comparison,
)
from scoring_bias.models import (
    ProbeType,
    BiasResult,
    ModelProfile,
)


class TestComputeDelta:
    """Tests for compute_delta function."""

    def test_positive_delta(self, sample_scores_normal, sample_scores_reversed):
        """Treatment > control should give positive delta."""
        delta = compute_delta(sample_scores_normal, sample_scores_reversed)
        assert delta is not None
        assert delta > 0

    def test_negative_delta(self):
        """Control > treatment should give negative delta."""
        delta = compute_delta([4.0, 5.0, 4.5], [3.0, 2.5, 3.0])
        assert delta is not None
        assert delta < 0

    def test_zero_delta(self):
        """Identical lists should give zero delta."""
        delta = compute_delta([3.0, 4.0, 3.5], [3.0, 4.0, 3.5])
        assert delta is not None
        assert delta == pytest.approx(0.0)

    def test_empty_control(self):
        """Empty control list should return None."""
        assert compute_delta([], [1.0, 2.0]) is None

    def test_empty_treatment(self):
        """Empty treatment list should return None."""
        assert compute_delta([1.0, 2.0], []) is None

    def test_single_element(self):
        """Single-element lists should still compute."""
        delta = compute_delta([3.0], [4.0])
        assert delta is not None
        assert delta == 1.0

    def test_exact_values(self):
        """Verify exact delta computation."""
        delta = compute_delta([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert delta is not None
        assert delta == pytest.approx(3.0)


class TestComputeFlipRate:
    """Tests for compute_flip_rate function."""

    def test_no_flips(self, sample_scores_equal):
        """Identical scores should give 0 flip rate."""
        rate = compute_flip_rate(sample_scores_equal, sample_scores_equal)
        assert rate is not None
        assert rate == pytest.approx(0.0)

    def test_all_flips(self):
        """Every pair flips by >= threshold."""
        control = [1.0, 2.0, 3.0]
        treatment = [4.0, 5.0, 6.0]
        rate = compute_flip_rate(control, treatment, threshold=0.5)
        assert rate is not None
        assert rate == pytest.approx(1.0)

    def test_partial_flips(self):
        """Some flips, some not."""
        control = [3.0, 4.0, 3.0, 4.0]
        treatment = [4.0, 4.5, 3.0, 4.0]
        rate = compute_flip_rate(control, treatment, threshold=0.5)
        assert rate is not None
        assert rate == pytest.approx(0.5)

    def test_mismatched_lengths(self):
        """Different length lists should return None."""
        assert compute_flip_rate([1.0], [1.0, 2.0]) is None

    def test_empty(self):
        """Empty lists should return None."""
        assert compute_flip_rate([], []) is None

    def test_custom_threshold(self):
        """Higher threshold should reduce flip count."""
        control = [3.0, 3.0]
        treatment = [3.5, 4.0]
        rate_strict = compute_flip_rate(control, treatment, threshold=0.8)
        rate_loose = compute_flip_rate(control, treatment, threshold=0.3)
        # With threshold 0.8: |3.5-3.0| = 0.5 < 0.8, |4.0-3.0| = 1.0 >= 0.8 => 1/2
        # With threshold 0.3: both qualify => 2/2
        assert rate_strict == pytest.approx(0.5)
        assert rate_loose == pytest.approx(1.0)


class TestBootstrapCI:
    """Tests for bootstrap_ci function."""

    def test_bootstrap_returns_three_values(self, sample_scores_normal, sample_scores_reversed):
        """bootstrap_ci should return (delta, ci_lower, ci_upper)."""
        delta, ci_l, ci_u = bootstrap_ci(
            sample_scores_normal, sample_scores_reversed,
            n_resamples=1000, seed=42,
        )
        assert delta is not None
        assert ci_l is not None
        assert ci_u is not None
        assert ci_l <= ci_u  # CI should be valid

    def test_bootstrap_ci_contains_delta(self, sample_scores_normal, sample_scores_reversed):
        """The observed delta should be within the bootstrap CI."""
        delta, ci_l, ci_u = bootstrap_ci(
            sample_scores_normal, sample_scores_reversed,
            n_resamples=1000, seed=42,
        )
        assert ci_l <= delta <= ci_u

    def test_zero_delta_ci(self):
        """CI for zero-delta case should be tight around zero."""
        scores = [3.0, 4.0, 3.5, 4.0]
        delta, ci_l, ci_u = bootstrap_ci(scores, scores, n_resamples=1000, seed=42)
        assert delta == pytest.approx(0.0)
        assert ci_l <= 0.0 <= ci_u

    def test_mismatched_lengths(self):
        """Mismatched lists should return all Nones."""
        d, l, u = bootstrap_ci([1.0], [1.0, 2.0])
        assert d is None and l is None and u is None

    def test_empty(self):
        """Empty lists should return all Nones."""
        d, l, u = bootstrap_ci([], [])
        assert d is None and l is None and u is None

    def test_reproducibility(self):
        """Same seed should give same CI."""
        control = [3.0, 4.0, 3.5, 4.0, 3.5]
        treatment = [3.5, 4.5, 4.0, 4.5, 4.0]
        d1, l1, u1 = bootstrap_ci(control, treatment, n_resamples=1000, seed=123)
        d2, l2, u2 = bootstrap_ci(control, treatment, n_resamples=1000, seed=123)
        assert d1 == d2
        assert l1 == l2
        assert u1 == u2


class TestComputeModelSummary:
    """Tests for compute_model_summary function."""

    def test_returns_model_profile(self, sample_small_data):
        """Should return a ModelProfile with correct structure."""
        scores = sample_small_data["model_1"]
        profile = compute_model_summary(
            "test-model",
            {ProbeType(k): v for k, v in scores.items()},
        )
        assert isinstance(profile, ModelProfile)
        assert profile.name == "test-model"

    def test_populates_probe_results(self, sample_small_data):
        """Should create ProbeResult entries for each probe."""
        scores = sample_small_data["model_1"]
        profile = compute_model_summary(
            "test-model",
            {ProbeType(k): v for k, v in scores.items()},
        )
        assert len(profile.probe_results) == 2  # rubric_order and score_id

    def test_delta_values(self, sample_small_data):
        """Should compute sensible delta values."""
        scores = sample_small_data["model_1"]
        profile = compute_model_summary(
            "test-model",
            {ProbeType(k): v for k, v in scores.items()},
        )
        for pr in profile.probe_results.values():
            assert pr.delta is not None


class TestBaseInstructComparison:
    """Tests for compute_base_instruct_comparison."""

    def test_missing_model_returns_none(self):
        """If either model is missing, should return None."""
        results = BiasResult()
        comp = compute_base_instruct_comparison("base", "instruct", results)
        assert comp is None


class TestLargeDatasetPerformance:
    """Performance/sanity tests with larger data."""

    def test_many_scores_delta(self):
        """Delta computation on 1000 scores should be fast."""
        import random
        random.seed(42)
        control = [random.uniform(1, 5) for _ in range(1000)]
        treatment = [s + random.gauss(0.5, 0.2) for s in control]
        delta = compute_delta(control, treatment)
        assert delta is not None
        assert delta > 0  # treatment systematically higher

    def test_many_scores_flip_rate(self):
        """Flip rate on 1000 items should be reasonable."""
        import random
        random.seed(42)
        control = [random.uniform(1, 5) for _ in range(1000)]
        treatment = [s + random.gauss(0.3, 0.1) for s in control]
        rate = compute_flip_rate(control, treatment, threshold=0.5)
        assert rate is not None
        assert 0.0 <= rate <= 1.0

    def test_bootstrap_ci_narrow_with_many_samples(self):
        """More data should give narrower CI."""
        import random
        random.seed(42)
        control = [random.uniform(1, 5) for _ in range(200)]
        treatment = [s + 0.2 for s in control]
        _, l, u = bootstrap_ci(control, treatment, n_resamples=500, seed=42)
        ci_width = u - l
        assert ci_width < 1.0  # reasonable CI width for n=200
