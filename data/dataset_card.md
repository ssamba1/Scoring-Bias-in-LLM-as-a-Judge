---
license: cc-by-4.0
task_categories:
- text-scoring
- text-evaluation
language:
- en
tags:
- llm-as-a-judge
- scoring-bias
- evaluation
size_categories:
- n<1K
---

# Scoring Bias in LLM-as-a-Judge — Dataset

Per-item scores from 32 model variants across 3 scoring bias probes.

## Structure

```python
{
  "model_name": {
    "rubric_order": {    # Probe 1: Rubric direction
      "normal": [...],   # 50 item scores (1-5)
      "reversed": [...], # Same items, reversed scale
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

32 variants total:
- 22 instruct-tuned models (OpenRouter)
- 6 base-instruct pairs (Kaggle T4: Qwen2.5, Llama-3.2, StableLM, Gemma-2)
- 3 base-instruct pairs (Kaggle original: Llama-3-8B, Mistral-7B, Gemma-2-2B)

## Citation

```bibtex
@article{samba2026scoring,
  title={Scoring Bias in LLM-as-a-Judge Models},
  author={Samba, Sricharan},
  year={2026}
}
```

## License

CC-BY 4.0
