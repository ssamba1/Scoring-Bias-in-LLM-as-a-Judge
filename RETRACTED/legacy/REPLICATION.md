# Replication Package  Bias in LLM-as-a-Judge

## Repository: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

This package contains everything needed to reproduce our experiments and analyses.

## Contents

```
replication_package/
├── README.md                    ← This file
├── setup.sh                     ← One-click environment setup
├── requirements.txt             ← Python dependencies
│
├── data/                        ← Evaluation items
│   ├── items_base.csv           ← 400 base evaluation items
│   └── items_all_conditions.csv ← 3,200 condition variants
│
├── experiments/                 ← Experiment definitions
│   ├── experiment_rootcause.json  ← Root cause experiment config
│   └── experiment_interaction.json ← Bias interaction experiment config
│
├── code/                        ← Analysis code
│   ├── analysis.R               ← R analysis script (optional)
│   └── analysis.py              ← Python analysis script
│
├── results/                     ← Pre-computed results (from synthetic data)
│   └── synthetic_results.csv    ← 48,000 synthetic judgments
│
└── paper/                       ← Manuscript
    └── paper.pdf                ← Compiled PDF
```

## Reproducing the Experiments

### Option 1: Run with Pre-computed Synthetic Data (5 minutes)

```bash
# 1. Set up environment
bash setup.sh

# 2. Run analysis
python3 pipeline_biasinteraction/analysis.py

# 3. Generate figures
python3 pipeline_biasinteraction/generate_figures.py

# 4. Generate report
python3 pipeline_biasinteraction/generate_report.py

# 5. Explore results interactively
python3 explore_results.py
```

### Option 2: Run Real API Experiments ($26 budget)

```bash
# 1. Set up environment and API keys
bash setup.sh
cp .env.template .env
# Edit .env with your API keys

# 2. Register and run experiments
python3 experiment_tracker.py register --name "Full Experiment" --config '{...}'
python3 inference_executor.py --judge all --benchmark benchmark/scoring_bias_benchmark.json

# 3. Analyze results
python3 pipeline_biasinteraction/analysis.py
python3 pipeline_biasinteraction/generate_figures.py
python3 bias_audit.py --judge claude
```

### Option 3: Run GPU-based Root Cause Experiment ($15 GPU)

```bash
# 1. Set up environment
pip install torch transformers accelerate huggingface_hub

# 2. Run on Colab
# Open pipeline_rootcause/colab_setup.ipynb and run all cells

# 3. Or run locally
python3 pipeline_rootcause/rootcause_pipeline_v2.py --model all --items 50
```

## Expected Results

| Experiment | Expected Output | Time |
|-----------|----------------|------|
| Synthetic pilot | Interaction ratios, bar charts, heatmap | 2 min |
| Real API (5 judges) | 48,000 scores, ANOVA results, bias audit | 3-4 hours |
| GPU (3 families) | 11,250 scores, base vs instruct comparison | 4-5 hours |
| Multi-agent | Deliberation log, consensus analysis | 30 min |
| Bias audit | HTML report, severity ratings | 1 min |

## Software Requirements

- Python 3.10+
- Packages: pandas, numpy, scipy, matplotlib, seaborn, statsmodels
- Optional: torch, transformers (for GPU experiments)
- Optional: anthropic, openai, google-generativeai (for API experiments)

## Docker (Optional)

```bash
docker build -t bias-research .
docker run -v $(pwd)/.env:/app/.env bias-research python3 inference_executor.py --judge all
```

## Verification

Run `python3 tests/run_tests.py` to verify the analysis pipeline works correctly.
All 13 unit tests should pass.

## Citation

If you use this package, please cite:

```
@article{student2026bias,
  title={Bias Interaction Effects in LLM-as-a-Judge: A Full-Factorial Study},
  author={Student, A. and Student, B.},
  journal={arXiv preprint},
  year={2026}
}
```

## License

Code: MIT License
Data: CC-BY 4.0
Paper text: CC-BY 4.0
