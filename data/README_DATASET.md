# Dataset Release Package — Bias in LLM-as-a-Judge

## Study 1: Root Cause of Scoring Bias

---

## Overview
This package contains all datasets generated for Study 1. All data is released under CC-BY 4.0.

## Files

| File | Description | Format | Size |
|------|-------------|--------|------|
| `study1_canonical.csv` | Canonical synthetic results (16,000 rows, 5 judges) | CSV | ~500 KB |
| `study1_raw_scores.json` | Per-item raw scores from all 6 model variants | JSON | ~150 KB |
| `study1_summary.json` | Summary statistics (MAD, FR, Cohen's d, CIs) | JSON | ~10 KB |
| `study1_probes.txt` | Full probe prompts used in experiment | Text | ~5 KB |
| `study1_items.csv` | All 50 evaluation items with domains | CSV | ~8 KB |

## Canonical Data Schema (`study1_canonical.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `judge` | string | Model name (e.g., "claude", "gpt4o") |
| `item_id` | int | Item identifier (0-399) |
| `condition` | string | Experimental condition |
| `position` | string | Response position ("first", "second") |
| `length` | string | Response length ("short", "normal", "long") |
| `sentiment` | string | Response sentiment ("negative", "neutral", "positive") |
| `score` | int | Score assigned by the model (1-5) |
| `repeat_num` | int | Replicate number (1-3) |

## Conditions

| Condition | Position | Length | Sentiment | Description |
|-----------|----------|--------|-----------|-------------|
| baseline | first | normal | neutral | Unbiased control |
| short_response | first | short | neutral | Tests verbosity bias |
| verbose_response | first | long | neutral | Tests verbosity bias |
| positive_tone | first | normal | positive | Tests sentiment bias |
| negative_tone | first | normal | negative | Tests sentiment bias |
| disfavored_pos | second | normal | neutral | Tests position bias |
| worst_case | second | short | negative | Worst-case combination |
| best_biased | second | long | positive | Best-biased combination |

## Models

| Model ID | HuggingFace Path | Type | Size |
|----------|-----------------|------|------|
| llama3-base | meta-llama/Meta-Llama-3-8B | Base | 8B |
| llama3-inst | meta-llama/Meta-Llama-3-8B-Instruct | Instruct | 8B |
| mistral-base | mistralai/Mistral-7B-v0.3 | Base | 7B |
| mistral-inst | mistralai/Mistral-7B-Instruct-v0.3 | Instruct | 7B |
| gemma2-base | google/gemma-2-2b | Base | 2B |
| gemma2-inst | google/gemma-2-2b-it | Instruct | 2B |

## Experimental Parameters

| Parameter | Value |
|-----------|-------|
| Temperature | 0.0 |
| Decoding | Greedy (do_sample=False) |
| Max new tokens | 3 |
| Repeats per condition | 3 |
| Total items | 50 |
| Items per domain | 10 |
| Domains | 5 (science, tech, humanities, daily life, math) |
| Random seed | 42 |
| Total judgments | 8,100 |
| GPU | NVIDIA Tesla T4 (16 GB) |
| Runtime | ~6 hours |
| Cost | $0 (Kaggle free tier) |

## License
CC-BY 4.0 — Free to use, share, and adapt with attribution.

## Citation
```
@misc{student2026scoringbias,
  title={Where Does Scoring Bias Come From?},
  author={Student A and Student B},
  year={2026},
  howpublished={GitHub: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge}
}
```
