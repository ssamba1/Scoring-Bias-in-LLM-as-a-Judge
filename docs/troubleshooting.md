# Troubleshooting Guide

> **Common issues and solutions for the Scoring Bias project.**

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Python & Import Issues](#python--import-issues)
3. [4-Bit Loading Issues](#4-bit-loading-issues)
4. [Stop Tokens & Prompt Issues](#stop-tokens--prompt-issues)
5. [API Key Issues](#api-key-issues)
6. [Path & Platform Issues](#path--platform-issues)
7. [GPU & CUDA Issues](#gpu--cuda-issues)
8. [Test Failures](#test-failures)
9. [Docker Issues](#docker-issues)
10. [Analysis Issues](#analysis-issues)
11. [Visualization Issues](#visualization-issues)

---

## Installation Issues

### `pip install -r requirements.txt` Fails

**Symptom**: Error messages about failed package installation.

**Causes and Solutions**:

| Error | Cause | Solution |
|-------|-------|----------|
| `ERROR: Could not find a version that satisfies the requirement torch` | No CUDA | Install CPU-only torch: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| `ERROR: No matching distribution found for scipy==1.13.1` | Python version too old | Use Python 3.11+: `python --version` |
| `ERROR: Could not build wheels for pyyaml` | Missing build tools | Install build tools: `pip install wheel setuptools` first |
| `ERROR: scipy requires Python >=3.10` | Python too old | Upgrade to Python 3.11+ |
| `pip._vendor.urllib3.exceptions.ReadTimeoutError` | Slow network | Use `pip install --default-timeout=120 -r requirements.txt` |

### `pip install -e .` Fails

**Symptom**: Error installing the package in development mode.

**Solution**:
```bash
# Ensure you're in the project root (has pyproject.toml)
cd Scoring-Bias-in-LLM-as-a-Judge

# Try with verbose output
pip install -e . -v

# If using outdated pip
pip install --upgrade pip
pip install -e .
```

### Conda Environment Fails

**Symptom**: `conda env create -f environment.yml` fails.

**Solutions**:
```bash
# Try with verbose logging
conda env create -f environment.yml --verbose

# Update conda first
conda update -n base conda

# Create environment manually instead
conda create -n scoring-bias python=3.11
conda activate scoring-bias
pip install -r requirements.txt
pip install -e .
```

---

## Python & Import Issues

### `ModuleNotFoundError: No module named 'scoring_bias'`

**Symptom**: Python can't find the `scoring_bias` package.

**Solutions**:

```bash
# 1. Make sure you're in the project root
cd /path/to/Scoring-Bias-in-LLM-as-a-Judge

# 2. Install the package (dev mode)
pip install -e .

# 3. Verify import works
python -c "from scoring_bias import compute_delta; print('OK')"

# 4. Check Python path
python -c "import sys; print('\n'.join(sys.path))"
# The project root should be in the list
```

### `ImportError: cannot import name 'compute_delta' from 'scoring_bias'`

**Symptom**: Specific function can't be imported.

**Solutions**:
```bash
# 1. Check if the function exists in the module
python -c "from scoring_bias.analysis import compute_delta; print('OK')"

# 2. Reinstall in dev mode (picks up changes)
pip install -e .

# 3. Check for circular imports or syntax errors
python -c "import scoring_bias.analysis; print('OK')"
```

### `RuntimeWarning: invalid value encountered in scalar divide`

**Symptom**: Warnings during analysis but no error.

**Cause**: Division by zero or NaN values in data.

**Solution**: Check input data for NaN or zero-variance groups.

```python
import numpy as np
scores = [1.0, 2.0, 3.0]
if np.std(scores) == 0:
    print("Warning: zero variance in scores")
```

---

## 4-Bit Loading Issues

### `torch.cuda.OutOfMemoryError` When Loading Models

**Symptom**: GPU runs out of memory when loading large models (34B+, 70B+).

**Solutions**:

```python
# 1. Use 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16,
)

# 2. Use CPU offloading for very large models
model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    load_in_4bit=True,
    device_map="sequential",  # or "auto" with offload
    offload_folder="offload",
    torch_dtype=torch.float16,
)

# 3. Clear cache between models
import torch
torch.cuda.empty_cache()
del model

# 4. Reduce batch size
# Instead of batch_size=8, use batch_size=2 or 1
```

### `bitsandbytes` Not Installed

**Symptom**: `ImportError: No module named 'bitsandbytes'` when using 4-bit.

**Solution**:
```bash
# Install bitsandbytes
pip install bitsandbytes

# Windows: Install from pre-compiled wheel
pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.0-py3-none-win_amd64.whl
```

### `AttributeError: 'NoneType' object has no attribute 'quantize'`

**Symptom**: Error when trying to quantize a model.

**Cause**: Model not loaded on GPU or wrong quantization configuration.

**Solution**:
```python
from transformers import BitsAndBytesConfig

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    quantization_config=quant_config,
    device_map="auto",
)
```

---

## Stop Tokens & Prompt Issues

### Model Generates Past Expected Length

**Symptom**: Model produces very long output instead of a short score.

**Causes and Solutions**:

```python
# 1. Set proper stopping criteria
from transformers import StoppingCriteria, StoppingCriteriaList

class StopOnNewline(StoppingCriteria):
    def __call__(self, input_ids, scores, **kwargs):
        return input_ids[0, -1] == tokenizer.encode("\n")[0]

model.generate(
    ...,
    stopping_criteria=StoppingCriteriaList([StopOnNewline()]),
    max_new_tokens=10,  # Short output expected
)
```

```python
# 2. Use specific stop tokens for API models
# OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    max_tokens=10,
    stop=["\n", "###"],
)

# Anthropic
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=10,
    stop_sequences=["\n", "\n\n"],
    messages=[...],
)
```

### Model Returns 0 or 6 Instead of 1-5

**Symptom**: Scores outside the expected 1-5 range.

**Solutions**:

```python
# 1. Post-process scores
def clamp_score(score: float) -> float:
    """Clamp score to valid range 1-5."""
    return max(1.0, min(5.0, score))

# 2. Use extract functions that handle edge cases
def extract_score(text: str) -> float:
    """Extract numeric score from model output."""
    import re
    # Look for numbers 1-5
    matches = re.findall(r'\b([1-5])\b', text)
    if matches:
        return float(matches[0])
    return 3.0  # Default to middle score
```

### Empty or Gibberish Responses

**Symptom**: Model returns empty string, repeated characters, or gibberish.

**Solutions**:
```bash
# 1. Check prompt formatting
# Ensure prompts end with a clear signal to produce a score
prompt = f"""{rubric}

Item: {item}
Response: {response}

Score:"""  # Model should complete this

# 2. Use temperature=0 for deterministic output
model.generate(..., temperature=0.0, do_sample=False)

# 3. For API models, use system message
```

---

## API Key Issues

### `AuthenticationError` or `401 Unauthorized`

**Symptom**: API calls fail with authentication error.

**Solutions**:

```bash
# 1. Check your .env file is properly formatted
cat .env
# Should look like:
# OPENAI_API_KEY=sk-proj-abc123...
# No quotes around the value

# 2. Verify the key is being loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI Key:', os.getenv('OPENAI_API_KEY', 'NOT SET')[:10]+'...')"
```

### `RateLimitError` or `429 Too Many Requests`

**Symptom**: API calls are rate-limited.

**Solutions**:

```python
# 1. Add delays between calls
import time
for item in items:
    response = call_api(item)
    time.sleep(1)  # Wait 1 second

# 2. Use exponential backoff
import time
import random

def call_with_retry(api_func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return api_func()
        except RateLimitError:
            wait = (2 ** attempt) + random.random()
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### `InsufficientQuotaError` or `402 Payment Required`

**Symptom**: API key has run out of credits.

**Solutions**:
```bash
# 1. Check API usage
# OpenAI: https://platform.openai.com/usage
# Anthropic: https://console.anthropic.com/settings/billing
# Google: https://console.cloud.google.com/apis/credentials

# 2. Use smaller/cheaper models for initial testing
# 3. Set spending limits
# 4. Use free tiers when available
```

---

## Path & Platform Issues

### Windows: Path Separator Issues

**Symptom**: Scripts fail with path-related errors on Windows.

**Solutions**:

```bash
# Use POSIX-style paths in git-bash
/c/Users/Admin/Research/research-draft

# Use raw strings in Python
path = r"C:\Users\Admin\Research\research-draft"

# Use pathlib (cross-platform)
from pathlib import Path
path = Path("C:/Users/Admin/Research/research-draft")  # Forward slash works
```

### Windows: `venv/bin/activate` Not Found

**Symptom**: Virtual environment activation fails.

**Solution**: On Windows, the activation script is in `Scripts/`, not `bin/`:

```bash
# git-bash
source venv/Scripts/activate

# PowerShell
.\venv\Scripts\Activate.ps1

# cmd
venv\Scripts\activate.bat
```

### Windows: `make: command not found`

**Symptom**: `make` commands fail.

**Solutions**:
```bash
# Option 1: Install make via Chocolatey
choco install make

# Option 2: Use the commands directly
# Instead of `make test`, run:
python -m pytest tests/ -v

# Instead of `make install`, run:
pip install -r requirements.txt
pip install -e .
pre-commit install

# Option 3: Use git-bash which may include make
```

### Windows: UnicodeEncodeError

**Symptom**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution**:
```bash
# Set UTF-8 mode
set PYTHONUTF8=1
# Then run Python
python script.py
```

### Linux: `ModuleNotFoundError: No module named '_tkinter'`

**Symptom**: matplotlib fails to render.

**Solution**:
```bash
# Install tkinter
sudo apt-get install python3-tk
# Or use the Agg backend (already set in visualization.py)
```

---

## GPU & CUDA Issues

### `CUDA out of memory`

**Symptom**: GPU runs out of memory.

**Solutions**:
```python
# 1. Use smaller batch size
model.generate(..., batch_size=1)

# 2. Use 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(..., load_in_4bit=True)

# 3. Clear memory between models
import torch
torch.cuda.empty_cache()
del model

# 4. Use CPU offloading
model = AutoModelForCausalLM.from_pretrained(
    ...,
    device_map="auto",
    offload_folder="./offload",
)

# 5. Check GPU memory usage
!nvidia-smi
```

### `CUDA not available`

**Symptom**: PyTorch can't find CUDA.

**Solutions**:
```bash
# 1. Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# 2. Install correct PyTorch version
# For CUDA 12.x:
pip install torch --index-url https://download.pytorch.org/whl/cu121

# For CPU only:
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 3. Update NVIDIA drivers
# https://www.nvidia.com/download/index.aspx
```

---

## Test Failures

### Tests Fail with `ModuleNotFoundError`

**Symptom**: Tests can't find the `scoring_bias` package.

**Solution**:
```bash
pip install -e .
python -c "from scoring_bias import compute_delta; print('OK')"
```

### Tests Fail on Windows

**Symptom**: Tests that pass on Linux fail on Windows.

**Common Causes**:
1. **Path separators**: Use `Path` from `pathlib` instead of hardcoded paths
2. **Line endings**: Use `\n` instead of `os.linesep` or configure `.gitattributes`
3. **Encoding**: Set `PYTHONUTF8=1`

### Specific Test Failures

| Test | Likely Cause | Solution |
|------|-------------|----------|
| `test_extract_score` | Regex pattern issue | Check that score extraction handles edge cases |
| `test_delta_computation` | Data mismatch | Check input data format |
| `test_base_instruct_comparison` | Missing models | Ensure both base and instruct models are in data |
| `test_interactive_paper_exists` | File not found | Run figure generation first: `make figures` |

---

## Docker Issues

### Docker Build Fails

**Symptom**: `docker build` exits with errors.

**Solutions**:
```bash
# 1. Check Dockerfile syntax
docker build --no-cache -t scoring-bias . 2>&1

# 2. Ensure requirements.txt exists
ls requirements.txt

# 3. Build with verbose output
DOCKER_BUILDKIT=0 docker build --no-cache -t scoring-bias .

# 4. Common issues:
# - Network timeout: Use a different DNS or proxy
# - Missing build tools: Use full python:3.11 instead of python:3.11-slim
```

### Docker Run Fails

**Symptom**: Container exits immediately or fails to start.

**Solutions**:
```bash
# 1. Check logs
docker logs bias-test

# 2. Run with interactive shell to debug
docker run --rm -it scoring-bias /bin/bash
# Then run commands manually

# 3. Check for missing files
docker run --rm scoring-bias ls -la /app/

# 4. Common issues:
# - Missing .env file: Use --env-file
# - Volume mount path doesn't exist: Create it first
```

---

## Analysis Issues

### Bootstrap Never Finishes

**Symptom**: `bootstrap_ci()` takes too long.

**Solutions**:
```python
# 1. Reduce number of resamples
delta, lo, hi = bootstrap_ci(
    control, treatment,
    n_resamples=1000,  # Default is 10000
    seed=42,
)

# 2. Reduce number of items (for testing)
# Use a subset of data first

# 3. Use vectorized operations if possible
```

### All Deltas Are Zero

**Symptom**: All computed deltas are 0.0.

**Cause**: Treatment and control conditions might be identical or mislabeled.

**Solution**:
```python
# Check condition labels
print("Condition keys:", condition_scores.keys())
# Expected: "normal", "reversed" (or similar)

# Verify scores differ
print("Control:", control_scores[:5])
print("Treatment:", treatment_scores[:5])
```

### Delta Values Seem Too Large/Small

**Symptom**: Computed deltas don't match expectations.

**Solution**:
```python
# 1. Check score ranges
print(f"Score range: {min(scores)}-{max(scores)}")
# Scores should be 1-5 scale

# 2. Check for outliers
import numpy as np
scores = np.array(scores)
print(f"Mean: {scores.mean():.3f}, Std: {scores.std():.3f}")

# 3. Verify condition assignment
# Are you comparing the right conditions?
```

---

## Visualization Issues

### `plt.show()` Shows Nothing

**Symptom**: No figure window appears.

**Cause**: Non-interactive backend (Agg) is set.

**Solution**:
```python
# Option 1: Use save() instead of show()
fig.savefig("output.png", dpi=150, bbox_inches="tight")

# Option 2: Switch to interactive backend
import matplotlib
matplotlib.use("TkAgg")  # or "Qt5Agg", "QtAgg"
import matplotlib.pyplot as plt
```

### Chinese or Special Characters in Labels

**Symptom**: Box characters or Chinese text in figure labels.

**Cause**: Model names contain special characters that matplotlib can't render.

**Solution**:
```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Replace with available font
```

### Figures Are Blurry

**Symptom**: Saved figures look pixelated.

**Solution**:
```python
# Increase DPI
fig.savefig("output.png", dpi=300, bbox_inches="tight")

# Or use vector format
fig.savefig("output.pdf", bbox_inches="tight")
fig.savefig("output.svg", bbox_inches="tight")
```

---

## Still Stuck?

If none of these solutions work:

1. **Search existing issues**: https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge/issues
2. **Open a new issue** with:
   - Full error message and traceback
   - Your operating system and Python version
   - Steps to reproduce the problem
   - What you've already tried
3. **Email**: srisamba09@gmail.com
4. **Check documentation**: Review the [User Guide](user_guide.md), [Setup Guide](setup_guide.md), and [FAQ](faq.md)
