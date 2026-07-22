"""
Shared test fixtures and configuration for scoring-bias tests.
"""

from __future__ import annotations
import sys
import pytest
import random
from pathlib import Path
from typing import Dict, List

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_scores_normal() -> List[float]:
    """Scores under normal (control) condition: 10 items."""
    return [3.0, 4.0, 3.5, 4.0, 3.0, 3.5, 4.0, 3.0, 2.5, 3.5]


@pytest.fixture
def sample_scores_reversed() -> List[float]:
    """Scores under reversed (treatment) condition: 10 items."""
    return [4.0, 4.5, 4.0, 3.5, 3.5, 4.0, 4.5, 3.5, 3.0, 4.0]


@pytest.fixture
def sample_scores_equal() -> List[float]:
    """Scores where control and treatment are identical (no bias)."""
    return [3.0, 4.0, 3.5, 4.0, 3.0, 3.5, 4.0, 3.0, 2.5, 3.5]


@pytest.fixture
def sample_deltas_positive() -> List[float]:
    """Paired deltas where treatment > control (leniency bias)."""
    return [1.0, 0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]


@pytest.fixture
def sample_small_data() -> Dict:
    """Small synthetic dataset for model profile tests."""
    return {
        "model_1": {
            "rubric_order": {
                "normal": [3.0, 4.0, 3.5],
                "reversed": [4.0, 4.5, 4.0],
            },
            "score_id": {
                "normal": [3.0, 3.5, 4.0],
                "reversed": [3.5, 4.0, 4.5],
            },
        },
        "model_2": {
            "rubric_order": {
                "normal": [2.5, 3.0, 3.5],
                "reversed": [2.0, 2.5, 3.0],
            },
        },
    }


def pytest_collection_modifyitems(items):
    """Ensure tests have consistent naming and ordering."""
    for item in items:
        if "model" in item.name or "delta" in item.name:
            item.add_marker(pytest.mark.analysis)
