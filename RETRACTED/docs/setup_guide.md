# Setup Guide

> **Step-by-step setup instructions for all platforms.**
>
> Windows, Linux, macOS, Kaggle, and Colab.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Linux Setup](#linux-setup)
3. [macOS Setup](#macos-setup)
4. [Windows Setup (git-bash)](#windows-setup-git-bash)
5. [Windows Setup (WSL)](#windows-setup-wsl)
6. [Windows Setup (PowerShell)](#windows-setup-powershell)
7. [Kaggle Setup](#kaggle-setup)
8. [Google Colab Setup](#google-colab-setup)
9. [Conda Environment](#conda-environment)
10. [Verification](#verification)

---

## Prerequisites

### For All Platforms

- **Git** ([download](https://git-scm.com/downloads))
- **Python 3.11+** ([download](https://python.org))
- **pip** (included with Python 3.11+)
- ~500 MB disk space for the repository and dependencies

### For Model Inference (Optional)

- **GPU with CUDA** (for running local models)
- **API keys** (for cloud models):
  - Anthropic, OpenAI, Google, DeepSeek, Together AI
- **HuggingFace account** (for accessing gated models)

---

## Linux Setup

### Ubuntu/Debian

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and Git
sudo apt install -y python3.11 python3.11-venv python3.11-dev git

# 3. Clone the repository
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge

# 4. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev,api,dashboard,notebook]"

# 6. Install pre-commit hooks
pre-commit install

# 7. Verify
python tests/test_all.py
```

### Fedora/RHEL

```bash
sudo dnf install python3.11 python3.11-devel git
# Then follow steps 3-7 from Ubuntu instructions above
```

---

## macOS Setup

### Using Homebrew

```bash
# 1. Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Python and Git
brew install python@3.11 git

# 3. Clone the repository
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge

# 4. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev,api,dashboard,notebook]"

# 6. Install pre-commit hooks
pre-commit install

# 7. Verify
python tests/test_all.py
```

### Apple Silicon (M1/M2/M3) Notes

If you encounter issues installing PyTorch or other native libraries:

```bash
# Install PyTorch for Apple Silicon
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Or use conda which handles ARM dependencies better
conda env create -f environment.yml
conda activate scoring-bias
```

---

## Windows Setup (git-bash  Recommended)

Git-bash provides a POSIX-compatible environment on Windows. This is our recommended approach.

### Step 1: Install Prerequisites

1. **Python 3.11+**: Download from [python.org](https://python.org). **Important**: Check "Add Python to PATH" during installation.
2. **Git for Windows**: Download from [git-scm.com](https://git-scm.com/download/win). Includes git-bash.
3. **Git LFS** (optional, for large files): `git lfs install`

### Step 2: Configure git-bash

Open **git-bash** (not PowerShell, not CMD).

```bash
# Verify Python
python --version
# Expected: Python 3.11.x

# Verify pip
pip --version
```

### Step 3: Clone and Install

```bash
# Navigate to where you want the project
cd /c/Users/YourName/Projects

# Clone
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge

# Create virtual environment
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev,api,dashboard,notebook]"

# Install pre-commit hooks
pre-commit install

# Verify
python tests/test_all.py
```

### Path Notes for Windows

In git-bash:
- **Use POSIX paths**: `/c/Users/Admin/...` instead of `C:\Users\Admin\...`
- **Use forward slashes**: `/` works fine
- **Virtual environment**: `venv/Scripts/activate` (not `venv/bin/activate`)

---

## Windows Setup (WSL  Alternative)

Windows Subsystem for Linux provides a full Linux environment on Windows.

### Step 1: Install WSL

Open **PowerShell as Administrator**:

```powershell
wsl --install -d Ubuntu-22.04
```

Restart your computer when prompted.

### Step 2: Set Up in WSL

Open the installed Ubuntu terminal:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install -y python3.11 python3.11-venv python3.11-dev git

# Clone (use Windows filesystem for persistence)
cd /mnt/c/Users/YourName/Projects
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge

# Follow Linux setup instructions from here
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev,api,dashboard,notebook]"
```

---

## Windows Setup (PowerShell  Alternative)

If you must use PowerShell, here are the adjustments:

### Step 1: Install Prerequisites

Same as git-bash: Python 3.11+, Git for Windows.

### Step 2: Clone and Install

```powershell
# Navigate to project directory
cd C:\Users\YourName\Projects

# Clone
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd Scoring-Bias-in-LLM-as-a-Judge

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev,api,dashboard,notebook]"

# Install pre-commit hooks
pre-commit install

# Note: You may need to enable script execution first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PowerShell-Specific Issues

1. **Activation error**: If `venv\Scripts\Activate.ps1` won't run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Path separator issues**: Use `\` or `/`  PowerShell accepts both.

3. **Makefile**: The `make` command is not available in PowerShell. Use one of:
   - Install `make` via Chocolatey: `choco install make`
   - Use git-bash instead
   - Run individual commands manually

---

## Kaggle Setup

Kaggle provides free GPU (T4, 16GB VRAM) for running experiments.

### Option A: Using Kaggle Notebook

1. Go to [kaggle.com](https://kaggle.com) and sign in
2. Create a new notebook:
   - **File** → **New Notebook**
   - Or use the provided notebook at `notebooks/kaggle_setup.ipynb`
3. Add GPU accelerator:
   - **Settings** → **Accelerator** → **GPU T4 x2**
4. Add Internet access:
   - **Settings** → **Internet** → **On**

### Option B: Use Kaggle API Locally

```bash
# Install Kaggle CLI
pip install kaggle

# Upload API token (kaggle.json) to ~/.kaggle/
# Download from: kaggle.com → Account → Create API Token

# Download a notebook
kaggle kernels pull username/kernel-name

# Push to Kaggle
kaggle kernels push
```

### Required Kaggle Notebook Setup

```python
# Install dependencies in a Kaggle notebook cell
!pip install -r /kaggle/input/scoring-bias/requirements.txt

# Set up HuggingFace token (from Kaggle Secrets)
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HF_TOKEN")

# Clone repo (if not already in input)
!git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
%cd Scoring-Bias-in-LLM-as-a-Judge
!pip install -e .
```

---

## Google Colab Setup

Colab provides free GPU (T4, occasionally A100) for running experiments.

### Notebook Setup

1. Open [colab.research.google.com](https://colab.research.google.com)
2. **File** → **Open notebook** → **GitHub** → Paste repository URL
3. Select the notebook at `notebooks/colab_setup.ipynb`
4. **Runtime** → **Change runtime type** → **T4 GPU**

### Required Colab Setup

```python
# In the first cell:
from google.colab import drive
drive.mount('/content/drive')

# Clone the repository
!git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
%cd Scoring-Bias-in-LLM-as-a-Judge

# Install dependencies
!pip install -r requirements.txt
!pip install -e ".[dev,api,dashboard,notebook]"

# Set up HuggingFace token
import os
os.environ["HF_TOKEN"] = "your_token_here"  # Or use Colab Secrets
```

### Colab GPU Memory Tips

- Use **4-bit quantization** for large models: `model = AutoModelForCausalLM.from_pretrained(..., load_in_4bit=True)`
- Use **flash attention** if available: `model = AutoModelForCausalLM.from_pretrained(..., attn_implementation="flash_attention_2")`
- Clear CUDA cache between models: `torch.cuda.empty_cache()`
- Use `del model` to free memory when switching models

---

## Conda Environment

For users who prefer conda over pip:

```bash
# Create conda environment
conda env create -f environment.yml
conda activate scoring-bias

# (Optional) Install extras
pip install -e ".[dev,api,dashboard,notebook]"
```

The `environment.yml` file:
```yaml
name: scoring-bias
channels:
  - conda-forge
  - defaults
dependencies:
  - python>=3.11
  - pip
  - pip:
    - -r file:requirements.txt
```

---

## Verification

After installation, verify everything works:

```bash
# 1. Check Python version
python --version
# Expected: Python 3.11.x

# 2. Check package import
python -c "from scoring_bias import __version__; print(f'scoring_bias v{__version__}')"
# Expected: scoring_bias v1.0.0

# 3. Run all tests
python tests/test_all.py
# Expected: ALL TESTS PASS (11+ tests)

# 4. Or with pytest
pytest tests/ -v

# 5. Check CLI works
scoring-bias --help

# 6. Quick analysis
scoring-bias run-all --help
```

---

## Environment Variables

After setup, configure API keys (if using cloud models):

```bash
# Copy template
cp .env.template .env

# Edit .env with your keys
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-proj-...
# GEMINI_API_KEY=AIza...
# DEEPSEEK_API_KEY=sk-...
# TOGETHER_API_KEY=...
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Python not found` | Ensure Python is installed and in PATH |
| `pip: command not found` | On Windows: use `python -m pip` instead |
| `ModuleNotFoundError: scoring_bias` | Run `pip install -e .` from project root |
| `No module named 'scipy'` | Run `pip install -r requirements.txt` |
| `git: command not found` | Install Git from git-scm.com |
| `make: command not found` | Install make or use direct commands |
| `pre-commit: command not found` | `pip install pre-commit` |

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).
