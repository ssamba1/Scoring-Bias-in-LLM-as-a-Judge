# Experiment Run Book — Bias Interaction Study

## Purpose
Standardized protocol for running the bias interaction experiment to ensure reproducibility.

## Pre-Run Checklist

### Environment
- [ ] Python 3.9+ installed
- [ ] All dependencies installed: `pip install -r pipeline_biasinteraction/requirements.txt`
- [ ] API keys set in environment variables or .env file
- [ ] At least 10GB free disk space for results

### Data
- [ ] `data/items_all_conditions.csv` exists (3,200 rows)
- [ ] Verify: `python3 -c "import csv; rows=list(csv.DictReader(open('data/items_all_conditions.csv'))); print(f'{len(rows)} items loaded')"`
- [ ] Expected: 3200 items loaded

### API Keys
- [ ] `export ANTHROPIC_API_KEY=sk-...`
- [ ] `export OPENAI_API_KEY=sk-...`
- [ ] `export GEMINI_API_KEY=...`
- [ ] `export DEEPSEEK_API_KEY=sk-...`
- [ ] `export TOGETHER_API_KEY=...`
- [ ] Verify: `python3 pipeline_biasinteraction/api_keys.py`

## Execution Order

### Step 1: Run synthetic pilot (optional, 5 min)
```bash
python3 pipeline_biasinteraction/generate_synthetic_pilot.py
python3 pipeline_biasinteraction/analysis.py
python3 explore_results.py
```
Purpose: Verify the analysis pipeline works end-to-end.

### Step 2: Run 10-item probe (30 min)
```bash
# Edit scoring_pipeline.py to use first 10 items only
python3 pipeline_biasinteraction/scoring_pipeline.py --judge claude
```
Purpose: Verify API keys work, scores are reasonable, catch format issues.

### Step 3: Run full experiment per judge (~2-4 hours each)
```bash
# Run in order of cost (cheapest first to catch issues early)
python3 pipeline_biasinteraction/scoring_pipeline.py --judge gemini     # ~$0.50, 30 min
python3 pipeline_biasinteraction/scoring_pipeline.py --judge deepseek   # ~$1, 30 min
python3 pipeline_biasinteraction/scoring_pipeline.py --judge llama      # ~$1, 30 min
python3 pipeline_biasinteraction/scoring_pipeline.py --judge gpt4o      # ~$10, 2 hours
python3 pipeline_biasinteraction/scoring_pipeline.py --judge claude     # ~$15, 2 hours
```

### Step 4: Quality check (15 min)
```bash
python3 pipeline_biasinteraction/quality_check.py
```

### Step 5: Analysis (30 min)
```bash
python3 pipeline_biasinteraction/analysis.py
python3 pipeline_biasinteraction/generate_figures.py
python3 explore_results.py
```

### Step 6: Populate database (5 min)
```bash
python3 pipeline_biasinteraction/results_db.py
```

## Error Recovery

### API rate limit hit
- The pipeline has built-in exponential backoff
- If it fails, wait 60 seconds and retry
- Consider reducing to 2 repeats instead of 3

### Score parsing failure
- Check that the judge response contains a number
- Add debug print: `print(f"Raw response: {response}")`
- Adjust the response parsing regex

### Partial results
- Results are saved after every 50 items
- If interrupted, rerun the same judge — it skips already-scored items (when implemented)

## Data Dictionary

### Input: `data/items_all_conditions.csv`
| Column | Type | Description |
|--------|------|-------------|
| item_id | int | Unique item identifier (0-399) |
| condition | str | Experimental condition name |
| position | str | "first" or "second" |
| length | str | "short", "normal", "long" |
| sentiment | str | "negative", "neutral", "positive" |
| instruction | str | The evaluation instruction |
| response | str | The response to evaluate |

### Output: `results/results_{judge}.csv`
| Column | Type | Description |
|--------|------|-------------|
| item_id | int | Matches input item_id |
| condition | str | Experimental condition |
| score_mean | float | Mean score across repeats |
| score_median | float | Median score |
| score_std | float | Standard deviation across repeats |
| raw_scores | json | All individual scores |

## Post-Run Checklist
- [ ] All 5 judges completed
- [ ] Quality check passes (all scores 1-5, no missing data)
- [ ] Analysis produces interaction ratios
- [ ] Figures generated
- [ ] Database populated
- [ ] Results backed up
