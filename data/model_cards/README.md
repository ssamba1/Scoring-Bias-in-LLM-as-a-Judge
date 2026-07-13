# Model Cards — 44 Families

## Standardized documentation for all models tested (NeurIPS Datasheet compliance)

Each card follows the [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) framework.

---

### Template

```markdown
## Model: {Family Name} {Size}

**Model Details**
- Developer: {Organization}
- Variants tested: Base {size}, Instruct {size}
- Architecture: {LLaMA, Mistral, Qwen, Gemma, Phi, etc.}
- Parameters: {size}
- License: {MIT, Apache 2.0, Llama Community, etc.}
- HuggingFace: {model_id}

**Intended Use**
- Used as an LLM judge in our experiments
- Evaluates response quality on a 1-5 scale

**Training Data**
- Pre-training: {source data, e.g., "Web corpus, books"}
- Instruction tuning: {method, e.g., SFT + RLHF}

**Bias Profile (from our experiments)**
| Probe | Base Delta | Instruct Delta | Change |
|-------|-----------|---------------|--------|
| Rubric Order | ... | ... | ...% |
| Score ID | ... | ... | ...% |
| Reference Answer | ... | ... | ...% |

**Known Limitations**
- English-only evaluation
- 1-5 scale only
- Temperature 0 evaluation only
```
