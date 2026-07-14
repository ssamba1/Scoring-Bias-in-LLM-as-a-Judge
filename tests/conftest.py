"""
Pytest configuration for scoring-bias research project.
"""
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

# Shared test fixtures
# (Add fixtures here as the test suite grows)


def pytest_collection_modifyitems(items):
    """Ensure tests have consistent naming and ordering."""
    for item in items:
        if "depth" in item.name or "model" in item.name:
            item.add_marker(pytest.mark.analysis)
