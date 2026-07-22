# Getting Started Guide

## Prerequisites
- Python 3.9+
- API keys for judge models (Option 2) or GPU (Option 1)
- Git

## Quick Start (5 minutes)

### 1. Clone and explore
```bash
git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge.git
cd research-draft
# View the proposals
less proposals/01_rootcause_scoring_bias.md
less proposals/02_bias_interaction_effects.md
```

### 2. Run synthetic pilot (Option 2)
```bash
# Generate synthetic data and run analysis
python3 pipeline_biasinteraction/generate_synthetic_pilot.py
python3 pipeline_biasinteraction/analysis.py
# Explore results interactively
python3 explore_results.py
```

### 3. Run synthetic pilot (Option 1)
```bash
# Run placeholder pipeline
python3 pipeline_rootcause/rootcause_pipeline.py
# Explore results
python3 explore_rootcause.py
```

## Running Real Experiments

### Option 2: Bias Interaction (API-based)

**Step 1: Add API keys**
Edit `pipeline_biasinteraction/scoring_pipeline.py`:
- Replace `score_with_api()` with actual API calls
- Add your API keys

**Step 2: Run judges**
```bash
# Run each judge separately
python3 pipeline_biasinteraction/scoring_pipeline.py --judge claude
python3 pipeline_biasinteraction/scoring_pipeline.py --judge gpt4o
python3 pipeline_biasinteraction/scoring_pipeline.py --judge gemini
python3 pipeline_biasinteraction/scoring_pipeline.py --judge deepseek
python3 pipeline_biasinteraction/scoring_pipeline.py --judge llama
```

**Step 3: Analyze**
```bash
python3 pipeline_biasinteraction/analysis.py
python3 pipeline_biasinteraction/generate_figures.py
```

### Option 1: Root Cause (GPU-based)

**Step 1: Set up environment**
```bash
pip install -r pipeline_rootcause/requirements.txt
# Or use the Colab notebook
```

**Step 2: Implement model inference**
Edit `pipeline_rootcause/rootcause_pipeline.py`:
- Replace `score_with_hf_model()` with actual HuggingFace inference
- See the implementation template in the function docstring

**Step 3: Run**
```bash
# On GPU machine
python3 pipeline_rootcause/rootcause_pipeline.py
```

**Step 4: Analyze**
```bash
python3 explore_rootcause.py
```

## File Structure Quick Reference

| You Need To... | File |
|----------------|------|
| Read the proposals | `proposals/` |
| Add API keys | `pipeline_biasinteraction/scoring_pipeline.py` |
| Run synthetic data | `pipeline_biasinteraction/generate_synthetic_pilot.py` |
| Run analysis | `pipeline_biasinteraction/analysis.py` |
| Generate figures | `pipeline_biasinteraction/generate_figures.py` |
| Explore results | `explore_results.py` |
| Implement model inference | `pipeline_rootcause/rootcause_pipeline.py` |
| Use Colab | `pipeline_rootcause/colab_setup.ipynb` |
| Explore root cause | `explore_rootcause.py` |
| Read the paper draft | `paper/paper_biasinteraction.md` or `paper/paper_rootcause.md` |
| View LaTeX paper | `paper/paper_latex.tex` |
| Check references | `paper/references.bib` |
| Read literature review | `literature/literature_review.md` |
| Read paper notes | `literature/paper_notes.md` |
| View dashboard | `dashboard/index.html` (open in browser) |

## API Cost Estimates

### Option 2 (5 judges × 3,200 items × 3 repeats = 48,000 judgments)

| Provider | Model | Est. Cost |
|----------|-------|-----------|
| Anthropic | Claude Sonnet 4 | ~$15 |
| OpenAI | GPT-4o | ~$10 |
| Google | Gemini 2.0 Flash | ~$0.50 |
| DeepSeek | DeepSeek V3 | ~$1 |
| Together/Groq | Llama 3 70B | ~$1 |
| **Total** | | **~$28** |

### Option 1 (6 models × 50 items × 3 bias types × 3 repeats)

| Resource | Est. Cost |
|----------|-----------|
| Colab T4 GPU (10 hours) | ~$10 |
| Or inference API (Together AI) | ~$15 |
| **Total** | **~$10-15** |
