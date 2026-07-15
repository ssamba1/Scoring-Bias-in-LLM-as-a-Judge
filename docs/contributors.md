# Contributors Guide

> **How to contribute to the Scoring Bias in LLM-as-a-Judge project.**
>
> We welcome contributions from researchers, students, and practitioners!

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Types of Contributions](#types-of-contributions)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Pull Request Process](#pull-request-process)
7. [Adding New Models](#adding-new-models)
8. [Adding New Probes](#adding-new-probes)
9. [Documentation](#documentation)
10. [Research Integrity](#research-integrity)

---

## Code of Conduct

This project is committed to providing a welcoming, inclusive, and harassment-free experience for everyone. By participating, you agree to:

- **Be respectful** of differing viewpoints and experiences
- **Give constructive** feedback
- **Accept responsibility** for mistakes and learn from them
- **Focus on what's best** for the research community

---

## Types of Contributions

### 🧪 Adding New Models
The most impactful contribution is evaluating new models using the existing probe framework. See [Adding New Models](#adding-new-models) below.

### 🔬 Adding New Probe Types
If you identify a new scoring bias type, define probes and implement inference. See [Adding New Probes](#adding-new-probes).

### 📊 New Analyses
- Domain-specific bias analysis
- Cross-lingual evaluation
- Human baseline studies
- Mitigation strategies (calibration, ensembling)
- Time-series analysis of bias over model versions

### 🐛 Bug Fixes & Improvements
- Code optimization
- Documentation fixes
- Test additions
- Reproducibility enhancements
- Performance improvements

### 📝 Documentation
- Fix typos, clarify explanations
- Add examples and tutorials
- Translate documentation

---

## Development Setup

### Prerequisites

- **Python 3.11+**
- **Git**
- **Optional**: GPU for local model inference

### Step 1: Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge
git remote add upstream https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev,api,dashboard,notebook]"
```

### Step 3: Install Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

This ensures code quality checks run automatically before every commit.

### Step 4: Verify Setup

```bash
python tests/test_all.py
# Expected: ALL TESTS PASS
```

---

## Coding Standards

### Python Style

We follow **PEP 8** with these project-specific rules:

| Rule | Standard |
|------|----------|
| **Line length** | 100 characters max |
| **Indentation** | 4 spaces (no tabs) |
| **Quotes** | Double quotes (`"`) for docstrings, single quotes (`'`) for strings |
| **Type hints** | Required for all function signatures |
| **Docstrings** | NumPy/Google style preferred |

### Formatting

We use **Black** for automatic formatting:

```bash
# Format all Python files
black src/scoring_bias/ cli.py tests/ api/ scripts/

# Check formatting without changes
black --check --diff src/scoring_bias/ cli.py tests/
```

### Linting

We use **Flake8** for linting:

```bash
flake8 src/scoring_bias/ cli.py tests/ \
    --max-line-length=100 --count --statistics
```

### Pre-commit Configuration

Our `.pre-commit-config.yaml` enforces:
- `trailing-whitespace` — No trailing spaces
- `end-of-file-fixer` — Files end with newline
- `check-yaml` — Valid YAML syntax
- `check-json` — Valid JSON syntax
- `check-added-large-files` — No files >500KB
- `black` — Automatic formatting
- `flake8` — Linting

### Import Order

Standard library → Third-party → Local imports:

```python
# Standard library
from __future__ import annotations
import random
from typing import Dict, List, Optional

# Third-party
import numpy as np
import matplotlib.pyplot as plt

# Local
from scoring_bias.models import ProbeType, ProbeResult
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Variables | `snake_case` | `control_scores` |
| Functions | `snake_case` | `compute_delta()` |
| Classes | `PascalCase` | `ModelProfile` |
| Constants | `UPPER_SNAKE_CASE` | `COLORS` |
| Private | Prefix `_` | `_save_or_show()` |
| Type params | `PascalCase` | `ProbeType` |

---

## Testing

### Running Tests

```bash
# Run all tests
python tests/test_all.py

# Or with pytest (more detailed output)
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_analysis.py -v

# Run specific test class
pytest tests/test_analysis.py::TestComputeDelta -v
```

### Writing Tests

We use **pytest** with descriptive class names. Tests are organized by module:

```
tests/
├── test_models.py         # Tests for data structures
├── test_analysis.py       # Tests for analysis functions
├── test_metrics.py        # Tests for statistical metrics
├── test_all.py            # Integration tests
└── conftest.py            # Shared fixtures
```

### Test Requirements

Every new function or method should have tests that cover:
1. **Normal case** — Known expected output
2. **Edge cases** — Empty inputs, single elements, boundary values
3. **Error cases** — Invalid inputs return appropriate values (usually `None`)

### Fixtures

Shared fixtures live in `conftest.py`:

```python
@pytest.fixture
def sample_scores_normal() -> List[float]:
    """Scores under normal (control) condition."""
    return [3.0, 4.0, 3.5, 4.0, 3.0, 3.5, 4.0, 3.0, 2.5, 3.5]

@pytest.fixture
def sample_scores_reversed() -> List[float]:
    """Scores under reversed (treatment) condition."""
    return [4.0, 4.5, 4.0, 3.5, 3.5, 4.0, 4.5, 3.5, 3.0, 4.0]
```

### Test Example

```python
class TestComputeDelta:
    """Tests for compute_delta function."""

    def test_positive_delta(self, sample_scores_normal, sample_scores_reversed):
        """Treatment > control should give positive delta."""
        delta = compute_delta(sample_scores_normal, sample_scores_reversed)
        assert delta is not None
        assert delta > 0

    def test_empty_control(self):
        """Empty control list should return None."""
        assert compute_delta([], [1.0, 2.0]) is None
```

---

## Pull Request Process

### Step-by-Step

1. **Fork** the repository on GitHub
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run all tests** to ensure nothing breaks:
   ```bash
   pytest tests/ -v
   ```
6. **Run linting**:
   ```bash
   flake8 src/scoring_bias/ cli.py tests/
   black --check --diff src/scoring_bias/ cli.py tests/
   ```
7. **Commit** with a clear message:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```
8. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Open a Pull Request** on GitHub

### PR Checklist

- [ ] Code follows project style guidelines (Black, Flake8)
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Docstrings updated
- [ ] Type hints added
- [ ] New models have corresponding model cards
- [ ] References have complete DOIs/URLs
- [ ] Documentation updated if relevant
- [ ] All analysis results are reproducible

### What Happens Next

1. A maintainer reviews your PR
2. CI checks run automatically (GitHub Actions)
3. Any issues are discussed in the PR
4. Once approved, a maintainer merges your changes

---

## Adding New Models

This is the most valuable way to contribute to our research.

### Requirements

1. **Base-instruct pair preferred**: Having both variants maximizes scientific value
2. **3 probes**: Rubric Order, Score ID, Reference Answer
3. **50+ items**: Per the standard protocol
4. **3 condition variants**: Normal + perturbed conditions

### Steps

1. **Add inference code** to `results_rootcause/`
   - Follow the pattern in existing inference scripts
   - Support HuggingFace models, API models, or both
2. **Run the protocol**:
   ```python
   # For each model:
   for probe in [rubric_order, score_id, reference_answer]:
       for condition in [normal, perturbed]:
           for item in items:
               score = model.judge(item, probe, condition)
   ```
3. **Save results** as structured JSON in `results_rootcause/`
4. **Update model cards** in `data/model_cards/all_models.md`
5. **Run analysis** to verify results fit expected patterns

### Model Card Template

Add an entry to `data/model_cards/all_models.md`:

```markdown
## [Model Name]

| Field | Value |
|-------|-------|
| **Family** | [Family] |
| **Size** | [Size] |
| **Variant** | Base / Instruct |
| **Source** | [HuggingFace / API provider] |
| **License** | [License] |
| **Access** | [Open weight / API only] |
```

---

## Adding New Probes

If you identify a new scoring bias type, here's how to add it.

### Steps

1. **Add to enum** in `src/scoring_bias/models.py`:
   ```python
   class ProbeType(str, Enum):
       RUBRIC_ORDER = "rubric_order"
       SCORE_ID = "score_id"
       REFERENCE_ANSWER = "reference_answer"
       YOUR_NEW_PROBE = "your_new_probe"  # Add here
   ```

2. **Define prompt variants**:
   - Create normal and perturbed conditions
   - Document the prompt templates

3. **Implement inference** for the new probe

4. **Update analysis pipeline**:
   - The analysis code automatically handles new probe types (it iterates over `ProbeType`)
   - Verify delta, flip rate, and CI computations work correctly

5. **Add visualization** support:
   - Add color and label in `visualization.py`
   - Verify all plot functions handle the new probe

6. **Document** the new probe in appendices

7. **Add tests** for the new probe type

---

## Documentation

### Documenting Functions

Use NumPy-style docstrings:

```python
def compute_delta(
    control_scores: List[float],
    treatment_scores: List[float],
) -> Optional[float]:
    """Compute the bias delta: mean(treatment) - mean(control).

    A positive delta means the treatment condition increases scores
    (leniency bias). A negative delta means it decreases scores
    (strictness bias).

    Parameters
    ----------
    control_scores : List[float]
        Scores under the control (normal) condition.
    treatment_scores : List[float]
        Scores under the treatment (biased) condition.

    Returns
    -------
    Optional[float]
        The mean difference (treatment - control), or None if
        either list is empty.

    Examples
    --------
    >>> compute_delta([3.0, 4.0], [4.0, 5.0])
    1.0
    """
```

### Documentation Files

The `docs/` directory contains:

| File | Audience |
|------|----------|
| `user_guide.md` | Users of the codebase |
| `educational_explainer.md` | Students, general audience |
| `methodology_tutorial.md` | Researchers, developers |
| `api_documentation.md` | Developers |
| `faq.md` | Everyone |
| `contributors.md` | Contributors |
| `setup_guide.md` | Users across platforms |
| `docker_guide.md` | Docker users |
| `troubleshooting.md` | Users with issues |
| `citation_guide.md` | Academics |
| `research_notebook.md` | Researchers |
| `glossary.md` | Everyone |

---

## Research Integrity

All contributions must adhere to:

### Transparency
- Report all methods and results honestly
- Document any deviations from the planned analysis
- Report negative results as well as positive ones

### Disclosure
- Disclose any API costs or computational resources used
- Report any conflicts of interest

### Reproducibility
- Provide complete code and data for all experiments
- Document random seeds and parameters
- Pre-register analyses where possible

### Open Data
- Share data in open formats (JSON, CSV)
- Use open licenses (MIT for code, CC-BY for data)
- Archive on Zenodo or similar platforms

---

## Getting Help

- **GitHub Issues**: For bugs, feature requests, and questions
- **Email**: srisamba09@gmail.com
- **Documentation**: Check `docs/` first
- **Existing issues**: Search before creating new ones

---

## License

By contributing, you agree that your contributions will be licensed under the same licenses as the project:
- **Code**: MIT License
- **Data**: CC-BY 4.0
- **Paper text**: CC-BY 4.0
