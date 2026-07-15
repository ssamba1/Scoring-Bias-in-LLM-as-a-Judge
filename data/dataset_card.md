---
license: cc-by-4.0
task_categories:
  - text-scoring
  - text-evaluation
  - bias-detection
language:
  - en
tags:
  - llm-as-a-judge
  - scoring-bias
  - evaluation
  - instruction-tuning
  - base-vs-instruct
  - rubric-bias
  - model-evaluation
size_categories:
  - n<1K
pretty_name: Scoring Bias in LLM-as-a-Judge Dataset
---

# Scoring Bias in LLM-as-a-Judge — Dataset Card

> **New:** A unified dataset (`data/dataset.json`) and comprehensive data dictionary
> (`data/data_dictionary.md`) have been added. See those files for the complete structured dataset.

## Dataset Description

- **Purpose:** Measure scoring bias in LLM-as-a-Judge models using perturbation probes
- **Total judgments:** 40,500+ (24,300 from base-instruct pairs + 29,700 from instruct-only models, with overlap)
- **Models:** 31 model variants (9 base + 22 instruct)
- **Probes:** 3 scoring bias types (Rubric Order, Score ID, Reference Answer)
- **Total API cost:** < $3 USD

## Dataset Statistics

| Property | Value |
|----------|-------|
| Total evaluation items | 80 |
| Domains | 5 (science, tech, humanities, daily life, math) |
| Items per domain | 10 (primary set) + 30 (secondary items, items 51–80) |
| Base models | 11 (including root cause study) |
| Instruct models | 31 (including OpenRouter and root cause study) |
| Base-instruct paired families | 11 (7 T4 + 4 root cause) |
| Probe types | 3 (rubric_order, score_id, reference_answer) |
| Probe variants per type | 3 |
| Repeats per condition | 3 (greedy, deterministic) |
| Score scale | 1–5 (integer) |

## Structure

The complete structured data is available in two formats:

1. **`data/dataset.json`** — Single unified JSON file with all scores, metrics, model metadata, and statistical analyses.
2. **`data/data_dictionary.md`** — Documents every field across all data files.

### Raw JSON Structure

```python
{
  "model_name": {
    "rubric_order": {    # Probe 1: Rubric direction
      "normal": [...],   # 50 item scores (1-5)
      "reversed": [...], # Same items, reversed scale
      "random": [...]    # Random label mapping
    },
    "score_id": {        # Probe 2: Score label format
      "numeric": [...],
      "letter": [...],   # A-E converted to 1-5
      "descriptive": [...],
    },
    "reference_answer": { # Probe 3: Exemplar bias
      "no_ref": [...],
      "good_ref": [...],
      "poor_ref": [...],
    }
  }
}
```

## Models

31 model variants total:

- **Base-instruct pairs (T4 GPU inference):** 7 families, 14 models
  - Qwen2.5 (0.5B, 1.5B, 7B), Llama-3.2 (1B, 3B), Gemma-2-2B, StableLM-2-1.6B
- **Base-instruct pairs (Kaggle root cause):** 3 families, 6 models (with 1 overlap)
  - Llama-3.1-8B, Llama-2-7B, Mistral-7B-v0.3, Gemma-2-9B, Qwen2.5-7B
- **Instruct-only (OpenRouter API):** 22 models
  - Qwen3 (8B, 14B, 32B), Qwen2.5-72B, Gemma3 (4B, 12B, 27B), Gemma4-31B, Phi-4, Mistral-Nemo-12B, Mistral-3.2-24B, DeepSeek (V3, V4-Flash), Hermes-3-70B, Zephyr-7B, MythoMax-13B, SOLAR-10.7B, Nemotron (Nano-30B, Super-120B), Hy3-295B, GPT-OSS-20B, Command-R, GLM-4.7, Gemini-2.5-Flash, Lunaris-8B
- **Excluded models:** 5 (Gemini-2.5-Pro, Inflection-3-Pi, Nemotron-Nano-30B, Command-R7B, Mistral-Small-24B) — stop-token truncation

## Recommended Uses

- **Bias measurement:** Use this dataset to evaluate scoring bias in new LLM-as-a-Judge models
- **Comparative analysis:** Compare bias profiles across model families, sizes, and training methods
- **Mitigation development:** Test debiasing strategies against the 3 scoring bias types
- **Meta-evaluation:** Use as a benchmark for LLM evaluator reliability
- **Instruction tuning studies:** Analyze how different alignment methods affect scoring behavior

## Out-of-Scope Uses

- **Human evaluation substitute:** This dataset measures model-internal bias, not human judgment quality
- **Absolute scoring benchmark:** Scores are relative measures; do not use as ground-truth quality judgments
- **Cross-lingual evaluation:** All items are in English; results do not generalize to other languages
- **Safety evaluation:** Does not measure harmful content, toxicity, or safety alignment
- **Real-time deployment:** Not designed for production scoring without calibration

## Bias Discussion

### Dataset-Level Biases

1. **English-only items:** All 80 items are in English, limiting multilingual generalizability
2. **Mid-quality responses:** Items were designed as factual, mid-quality responses (~3-4/5). Results may differ for very good or very poor responses
3. **Item domain distribution:** Science and technology items are overrepresented in the secondary set (items 51-80 include additional technical items)
4. **Model selection bias:** Open-weight models only (except Gemini-2.5-Flash). Results may not generalize to closed API models or frontier systems
5. **Scale range:** Only 1-5 scoring scale tested; other scales (1-10, 1-100, etc.) may produce different bias patterns

### Measurement Biases

1. **Greedy decoding:** Temperature 0 ensures determinism but may not reflect the full distribution of model outputs
2. **Single prompt template:** All probes use the same base template format; results may vary with different prompt structures
3. **3 repeats:** Repeats are deterministic; they verify stability but do not provide meaningful variance estimates
4. **Parse failures:** Descriptive labels had ~11% parse failures for base models; numeric and letter variants had <1%

### Known Limitations

- Only 11 families with base-instruct pairs (N=9 for primary analysis after deduplication)
- Per-domain bias analysis requires per-item score data (not currently available in aggregated form)
- No human baseline for absolute bias magnitude claims
- Single author study; independent replication pending

## Citation

```bibtex
@article{samba2026scoring,
  title={Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison},
  author={Samba, Sricharan},
  journal={arXiv preprint},
  year={2026},
  doi={10.5281/zenodo.21361920},
  url={https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge}
}
```

## License

CC-BY 4.0

## Acknowledgments

This dataset was created as part of research conducted at South Forsyth High School. All inference was performed on Kaggle T4 GPUs (free tier) and OpenRouter API (paid, < $3 total). We thank the developers of all open-weight models used in this study.
