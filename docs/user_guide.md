# User Guide — Scoring Bias in LLM-as-a-Judge

> **Complete guide to understanding and using the codebase for the paper
> "Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison"**

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Project Structure](#project-structure)
4. [Configuration](#configuration)
5. [Running Analyses](#running-analyses)
6. [The CLI Tool](#the-cli-tool)
7. [Generating Figures](#generating-figures)
8. [Interpreting Results](#interpreting-results)
9. [Working with the API](#working-with-the-api)
10. [Reproducing the Paper](#reproducing-the-paper)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Usage](#advanced-usage)

---

## Overview

This project investigates **scoring bias in LLM-as-a-Judge models** — systematic score changes caused by superficial prompt features rather than response quality. We compare **base** (pre-trained only) and **instruct** (instruction-tuned) variants across 31 model variants from 16 families, using 3 scoring bias probes on 80 evaluation items (40,500+ judgments).

### Key Findings

| Bias Type | Δ Before | Δ After | Change |
|-----------|----------|---------|--------|
| 🔢 Rubric Order | 2.85 | 1.59 | **−44%** |
| 🏷️ Score ID | 0.67 | 0.15 | **−77%** |
| 📋 Reference Answer | 0.88 | 1.19 | **+35%** |

**The differential effect**: Instruction tuning reduces format biases (rubric order, score ID) but increases content biases (reference answer).

---

## Installation

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- Optional: GPU with CUDA support for local model inference

### Quick Install

```bash
# 1. Clone the repository
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install the package in development mode
pip install -e ".[dev,api,dashboard,notebook]"

# 4. Verify installation
python tests/test_all.py
```

### Platform-Specific Notes

- **Windows**: Use git-bash (MSYS2) or WSL. See the [Setup Guide](setup_guide.md) for details.
- **macOS/Linux**: The standard install above works directly.
- **Kaggle/Colab**: See the [Setup Guide](setup_guide.md) for notebook-specific instructions.

### Dependency Groups

The project uses optional dependency groups via `pyproject.toml`:

| Group | Packages | Install Command |
|-------|----------|-----------------|
| `dev` | pytest, flake8, black | `pip install -e ".[dev]"` |
| `api` | FastAPI, uvicorn | `pip install -e ".[api]"` |
| `dashboard` | Streamlit | `pip install -e ".[dashboard]"` |
| `notebook` | Jupyter, jupytext | `pip install -e ".[notebook]"` |
| `all` | Everything above | `pip install -e ".[all]"` |

### Conda Environment

```bash
conda env create -f environment.yml
conda activate scoring-bias
```

---

## Project Structure

```
Scoring-Bias-in-LLM-as-a-Judge/
├── src/scoring_bias/           # Core Python package
│   ├── __init__.py            # Package exports
│   ├── models.py              # Data structures (dataclasses, enums)
│   ├── analysis.py            # Core analysis functions
│   ├── metrics.py             # Statistical metrics
│   └── visualization.py       # Plotting and figures
├── cli.py                     # Command-line interface
├── tests/                     # Test suite
│   ├── test_all.py            # Integration tests
│   ├── test_models.py         # Model tests
│   ├── test_analysis.py       # Analysis tests
│   ├── test_metrics.py        # Metrics tests
│   └── conftest.py            # Shared fixtures
├── paper/                     # LaTeX paper and figures
├── data/                      # Evaluation items and model cards
├── results_rootcause/         # Pre-computed experiment results
├── dashboard/                 # Interactive HTML dashboards
├── notebooks/                 # Jupyter notebooks
├── api/                       # FastAPI REST backend
├── infrastructure/            # Docker, CI config
├── Dockerfile                 # Container build
├── docker-compose.yml         # Multi-service setup
├── Makefile                   # Build automation
└── requirements.txt           # Python dependencies
```

---

## Configuration

### Environment Variables

Copy the template and add your API keys:

```bash
cp .env.template .env
# Edit .env with your API keys
```

The `.env.template` expects keys for:
- `ANTHROPIC_API_KEY` — for Claude models
- `OPENAI_API_KEY` — for GPT models
- `GEMINI_API_KEY` — for Gemini models
- `DEEPSEEK_API_KEY` — for DeepSeek models
- `TOGETHER_API_KEY` — for Together AI models

### Test Configuration

Test settings are in `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --no-header
```

### Code Style Configuration

- **Black**: line-length=100 (in `pyproject.toml`)
- **Flake8**: max-line-length=100 (in `pyproject.toml`)
- **Pre-commit**: auto-checks trailing whitespace, YAML/JSON validity, large files

Install pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

---

## Running Analyses

### Using the CLI

The `scoring-bias` CLI provides four main commands:

```bash
# Run the full pipeline
scoring-bias run-all --input data/raw/items_all_conditions.csv --output output/

# Or run steps individually:
scoring-bias compute-deltas --input data.csv --output output/
scoring-bias compute-flip-rates --input data.csv --output output/
scoring-bias bootstrap-ci --input data.csv --output output/ --n-resamples 10000
scoring-bias generate-figures --input data.csv --output output/figures/ --format png
```

### Using Python Directly

```python
from scoring_bias.analysis import compute_delta, bootstrap_ci, compute_flip_rate

# Compute bias delta
delta = compute_delta(control_scores, treatment_scores)
print(f"Bias delta (Δ): {delta:.4f}")

# Bootstrap confidence interval
delta, ci_lower, ci_upper = bootstrap_ci(
    control_scores, treatment_scores,
    n_resamples=10000, seed=42
)
print(f"Δ = {delta:.4f} [{ci_lower:.4f}, {ci_upper:.4f}]")

# Compute flip rate
flip_rate = compute_flip_rate(control_scores, treatment_scores, threshold=0.5)
print(f"Flip rate: {flip_rate:.1%}")
```

### Using the FastAPI Server

```bash
# Start the API
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

# Then query
curl http://localhost:8000/delta?model=llama-3.1-8b&probe=rubric_order
```

### Using the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

---

## The CLI Tool

### Commands

| Command | Description |
|---------|-------------|
| `compute-deltas` | Compute bias deltas (Δ = treatment − control) for all model-probe pairs |
| `compute-flip-rates` | Compute score flip rates (fraction of items where scores differ by ≥ threshold) |
| `bootstrap-ci` | Bootstrap confidence intervals for bias deltas |
| `generate-figures` | Generate publication-quality figures (PNG, PDF, SVG) |
| `run-all` | Run the full analysis pipeline sequentially |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--input FILE` | `data/raw/items_all_conditions.csv` | Input CSV data file |
| `--output DIR` | `output/` | Output directory |
| `--n-resamples N` | 10000 | Number of bootstrap resamples |
| `--format fmt` | `png` | Figure format (png, pdf, svg) |

### Examples

```bash
# Custom input and output
scoring-bias compute-deltas --input my_data.csv --output results/deltas/

# High-precision bootstrap
scoring-bias bootstrap-ci --n-resamples 50000 --output results/ci/

# Generate SVG figures
scoring-bias generate-figures --format svg --output results/figures/

# Full pipeline with custom paths
scoring-bias run-all --input data/experiment_results.csv --output experiment_output/
```

---

## Generating Figures

### Available Plot Types

| Function | Description |
|----------|-------------|
| `plot_bias_landscape()` | All models sorted by average delta with grouped bars per probe |
| `plot_model_comparison()` | Side-by-side comparison of two models |
| `plot_probe_breakdown()` | Per-probe score distributions for a single model |
| `plot_flip_rate_chart()` | Flip rates across all models and probes |
| `plot_base_instruct_comparison()` | Base vs instruct delta-of-deltas comparison |

### Python API

```python
from scoring_bias.visualization import plot_bias_landscape
from scoring_bias.analysis import load_scores_from_csv

results = load_scores_from_csv("data/raw/items_all_conditions.csv")
fig = plot_bias_landscape(results, save_path="figures/bias_landscape.png")
```

### CLI Generation

```bash
scoring-bias generate-figures --format pdf --output paper/figures/
```

### Figure Format Options

- **PNG**: Best for web and quick viewing (default, 150 DPI)
- **PDF**: Best for publication (vector format)
- **SVG**: Best for web with scaling (vector format)

---

## Interpreting Results

### Understanding Δ (Delta)

**Δ = mean(treatment scores) − mean(control scores)**

- **Positive Δ** → Treatment increases scores (leniency bias)
- **Negative Δ** → Treatment decreases scores (strictness bias)
- **Δ ≈ 0** → No bias detected

### Understanding Confidence Intervals

The bootstrap CI gives a range of plausible values for Δ:

- **Narrow CI** → High confidence in the estimate
- **CI crosses zero** → Bias may not be statistically significant
- **Wide CI** → More data needed for precise estimate

### Understanding Flip Rate

**Flip Rate = fraction of items where |treatment − control| ≥ threshold**

- **0%** → No items changed score (perfect consistency)
- **50%** → Half of items changed score
- **100%** → Every item changed score

### Understanding Cohen's d

**Cohen's d** = standardized effect size:

| d (abs) | Interpretation |
|---------|---------------|
| < 0.2 | Negligible |
| 0.2–0.5 | Small |
| 0.5–0.8 | Medium |
| > 0.8 | Large |

### Output File Structure

After running `run-all`, the output directory contains:

```
output/
├── deltas.json            # All bias deltas
├── flip_rates.json        # All flip rates
├── bootstrap_ci.json      # Bootstrap confidence intervals
└── figures/
    ├── bias_landscape.png   # Main bias landscape figure
    ├── flip_rates.png       # Flip rate chart
    ├── probe_breakdown_*.png # Per-model breakdowns
```

### Key Results Table

| Metric | Instruct Models | Base Models |
|--------|-----------------|-------------|
| Mean Δ (Rubric Order) | 0.68 | 2.85 |
| Mean Δ (Score ID) | 0.15 | 0.67 |
| Mean Δ (Reference Answer) | 1.19 | 0.88 |
| Avg Flip Rate (all probes) | ~25% | ~40% |

---

## Working with the API

### FastAPI Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/delta` | GET | Compute bias delta for a model-probe pair |
| `/models` | GET | List all available models |
| `/probes` | GET | List all probe types |
| `/results` | GET | Get full analysis results |

### API Example

```python
import requests

# Compute delta
resp = requests.get(
    "http://localhost:8000/delta",
    params={"model": "llama-3.1-8b", "probe": "rubric_order"}
)
print(resp.json())
```

---

## Reproducing the Paper

### Full End-to-End Reproduction

```bash
# 1. Set up environment
make setup

# 2. Run all tests
make test

# 3. Reproduce analyses
python results_rootcause/run_all_analyses.py

# 4. Generate figures
make figures

# 5. Compile paper
make paper

# 6. Generate arXiv submission
make archive
```

### Using Pre-computed Results

The `results_rootcause/` directory contains all experiment results:

| File | Contents |
|------|----------|
| `study1_results.json` | 22 instruct models (OpenRouter) |
| `t4fam_results.json` | 7 base-instruct families (T4) |
| `rootcause_analysis.json` | 3 original families (Kaggle) |
| `analysis_output/t4fam_deltas.json` | Computed deltas |
| `analysis_output/bootstrapped_cis.json` | Bootstrap CIs |
| `analysis_output/wilcoxon_results.json` | Statistical tests |
| `analysis_output/cohens_d.json` | Effect sizes |
| `analysis_output/bayesian_results.json` | Bayesian analysis |

### Verification

```bash
python tests/test_all.py  # 11+ tests should pass
pytest tests/ -v          # Or use pytest directly
```

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `ModuleNotFoundError: scoring_bias` | Package not installed | Run `pip install -e .` |
| Import errors in tests | Wrong Python version | Use Python 3.11+ |
| Tests fail on Windows | Path separator issues | Use git-bash, not cmd |
| Bootstrap is slow | Too many resamples | Reduce `--n-resamples` (default: 10000) |
| Figures not rendering | Missing matplotlib backend | Ensure `matplotlib.use("Agg")` is set |
| Docker build fails | Missing build dependencies | Check Dockerfile prerequisites |

For more detailed help, see:
- [Setup Guide](setup_guide.md) — platform-specific instructions
- [Troubleshooting Guide](troubleshooting.md) — common issues
- [FAQ](faq.md) — frequently asked questions

---

## Advanced Usage

### Custom Data Analysis

```python
from scoring_bias.analysis import load_scores_from_csv
from scoring_bias.metrics import cohens_d, effect_size_interpretation

results = load_scores_from_csv("my_data.csv")

# Compute Cohen's d for a specific model and probe
model = results.get_model("llama-3.1-8b")
pr = model.probe_results.get(ProbeType.RUBRIC_ORDER)
if pr and pr.delta:
    control = pr.condition_scores.get("normal", [])
    treatment = pr.condition_scores.get("reversed", [])
    d = cohens_d(control, treatment)
    print(f"Cohen's d: {d:.4f} ({effect_size_interpretation(d)})")
```

### Base vs Instruct Comparison

```python
from scoring_bias.analysis import compute_base_instruct_comparison
from scoring_bias.models import BiasResult

results = load_scores_from_csv("all_scores.csv")
comparison = compute_base_instruct_comparison(
    "llama-3.1-8b",  # base
    "llama-3.1-8b-instruct",  # instruct
    results
)
if comparison:
    print(f"Family: {comparison.family}")
    print(f"Delta of deltas: {comparison.avg_delta_of_deltas}")
```

### Adding New Models

1. Add inference code to `results_rootcause/`
2. Run the 3 probes × 3 conditions × 50 items
3. Save as structured JSON
4. Update model cards in `data/model_cards/`

---

## Support

- **GitHub Issues**: https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/issues
- **Email**: srisamba09@gmail.com
- **License**: MIT (code), CC-BY 4.0 (data, paper)
