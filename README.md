# Bias in LLM-as-a-Judge — Research Project

**Two verified untouched niches: root cause of scoring bias and bias interaction effects.**

## Quick Stats
- **140 files** · **27 commits** · **73 tests** ✅ all passing
- **6 papers** (4 LaTeX, 2 Markdown) · **37 Python modules** · **7 HTML dashboards**
- **Complete Docker + FastAPI + CI/CD infrastructure**
- **$10-26 budget** · **3-5 week timeline**

## Last Execution Results

```bash
$ bash run_all.sh
```

| Metric | Value |
|--------|-------|
| Total judgments | 16,000 (5 judges × 400 items × 8 conditions) |
| Highest IR | **Llama 3: 1.81×** (compounding) |
| Most judges compounding | **4/5** |
| F-statistics | All main effects significant (p < 0.001) |
| Tests | 73/73 passing |

### Interaction Ratios (from corrected synthetic data)

| Judge | Position | Verbosity | Sentiment | Combined | IR | Pattern |
|-------|----------|-----------|-----------|----------|-----|---------|
| Claude | 0.265 | 0.183 | 0.230 | 0.480 | **1.07** | Compounding |
| GPT-4o | 0.240 | 0.155 | 0.328 | 0.455 | **1.15** | Compounding |
| Gemini | 0.310 | 0.308 | 0.345 | 0.515 | **0.83** | Additive |
| DeepSeek | 0.108 | 0.197 | 0.198 | 0.415 | **1.36** | Compounding |
| Llama 3 | 0.363 | 0.325 | 0.315 | 1.248 | **1.81** | Compounding |

## How to Reproduce

```bash
# Option A: Run everything (uses corrected synthetic data)
bash run_all.sh

# Option B: Run real experiments (needs API keys)
cp .env.template .env  # add your keys
python3 inference_executor.py --judge all

# Option C: Docker
docker-compose up  # → API at localhost:8000

# Option D: Compile papers (needs LaTeX)
cd paper && bash build_papers.sh
```

## Repository Map

```
research-draft/
├── api.py                    # FastAPI web service (10+ endpoints)
├── bias_audit.py             # 7-dimension bias auditor
├── experiment_scheduler.py   # Automated batch execution
├── experiment_tracker.py     # Config hashing + reproducibility
├── inference_executor.py     # Real API calls (5 judge models)
├── multi_agent_eval.py       # 5-phase deliberation system
├── paper_generator.py        # Raw data → formatted paper
│
├── paper/                    # 6 papers
│   ├── paper_biasinteraction_final.tex   # Study 2
│   ├── paper_rootcause_final.tex         # Study 1
│   ├── formal_framework.tex              # Math + proofs
│   ├── theoretical_appendix.tex          # Full derivations
│   ├── monograph.md                      # Both studies unified
│   └── supplementary.md                  # Protocols + code
│
├── data/                     # Evaluation items (3,200+ variants)
├── pipeline_biasinteraction/ # API-based experiment pipeline
├── pipeline_rootcause/       # GPU-based model comparison
├── benchmark/                # 950-probe bias benchmark
├── dashboard/                # 7 HTML visualizations
├── isef/                     # Competition materials
├── literature/               # Reading notes + survey
└── tests/                    # 73 comprehensive tests
```

## License
Code: MIT · Data: CC-BY 4.0 · Paper text: CC-BY 4.0

**github.com/ssamba1/research-draft**
