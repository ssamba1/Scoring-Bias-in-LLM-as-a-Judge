# Complete Literature Matrix  LLM-as-a-Judge Bias Research

## All Papers Read in Full

| # | Paper | Venue | Year | Models Tested | Bias Types | Items | Base vs Instruct? | Key Finding |
|---|-------|-------|------|-------------|-----------|-------|-----------------|-------------|
| 1 | Li et al. | DASFAA | 2026 | GPT-4o, DeepSeek-V3-671B, Qwen3-32B/8B, Mistral-24B | 3 scoring (rubric, score ID, ref answer) | 5,421 | ❌ | Scoring bias exists (20-48% FR). Larger models more robust. |
| 2 | Wang et al. | ACL | 2024 | GPT-4, ChatGPT | Position bias | 80 | ❌ | Position bias causes 46-82% conflict rate. |
| 3 | Ye et al. (CALM) | NeurIPS WS | 2024 | GPT-4, Gemini, Llama-2, Mistral, Claude | 12 biases (position, verbosity, authority, etc.) | ~500 | ❌ | Advanced models still have significant biases. |
| 4 | Thakur et al. | arXiv | 2024 | 9 judges (Llama-2/3, Mistral, Gemma, GPT-4) × 9 exam-takers | Leniency, instruction following | 400 | ✅ **YES** (base vs instruct as exam-takers) | Only GPT-4 Turbo and Llama-3 70B show high human alignment. |
| 5 | Park et al. (OffsetBias) | EMNLP | 2024 | GPT-4, GPT-3.5, Llama-2 | 6 biases | ~1,000 | ❌ | Debiased data improves judge robustness. |
| 6 | Pan et al. | ACL Findings | 2026 | 52 models (Llama, Mistral, Gemma, etc.) | User-assistant bias | ~1,000 | ✅ **YES** | Instruction-tuned models show strong user bias. Base models neutral. |
| 7 | Xu et al. | arXiv | 2026 | GPT-OSS, Qwen3.5, Gemma-3 | Rubric position bias | 2,816 | ❌ | Position bias is model-specific (some first-biased, some last-biased). |
| 8 | **This work (Study 1)** | *Target* | 2026 | Llama 3 8B, Mistral 7B, Gemma 2 2B (base+instruct) | 3 scoring (rubric, score ID, ref answer) | 50 × 3 = 8,100 | ✅ **YES  FIRST for scoring bias** | **DIFFERENTIAL effect: format bias ↓, content bias ↑** |

## Key Methodological Comparison

| Aspect | Li et al. | Xu et al. | Thakur et al. | **This work** |
|--------|----------|----------|--------------|-------------|
| Framework | Perturb scoring prompt | Permute rubric order | Compare judge scores to humans | Perturb scoring prompt |
| Items | 5,421 | 2,816 | 400 | 50 × 3 = 8,100 |
| Models | 5 | 6 | 9 judges × 9 exam-takers | 6 (3 families × 2 variants) |
| Base vs Instruct | ❌ | ❌ | ⚠️ (as exam-takers only) | **✅ (first for scoring bias)** |
| Metrics | FR, MAD, Spearman ρ, Pearson r | χ², Friedman, Pearson r | Cohen's κ, % agreement | Δ, FR, Cohen's d, MAD |
| Open source | ✅ Partial | ❌ | ✅ | **✅ Complete** |
| Human evaluation | ✅ GPT-4.1 scores | ❌ | ✅ 3 human annotators | ❌ |
| Statistical tests | ✅ | ✅ | ✅ Cohen's κ | **⚠️ Underpowered (N=3)** |
| GPU cost | $$$$ (API calls) | $$$ (H100, 50 hrs) | $$$ (API calls) | **$0 (Kaggle free tier)** |

## Bias Types Coverage Matrix

| Bias Type | Wang '23 | Ye '24 | Park '24 | Li '25 | Xu '26 | **This work** |
|-----------|---------|-------|---------|-------|-------|-------------|
| Position | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ (scoring focus) |
| Verbosity/Length | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Rubric Order | ❌ | ❌ | ❌ | ✅ | ✅ | **✅** |
| Score ID | ❌ | ❌ | ❌ | ✅ | ❌ | **✅** |
| Reference Answer | ❌ | ❌ | ❌ | ✅ | ❌ | **✅** |
| Self-enhancement | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Sentiment | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Authority | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Bandwagon | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Diversity | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Fallacy Oversight | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Base vs Instruct** | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ UNIQUE** |

## Our Position in the Literature

```
        Foundational
        (Wang 2023, Zheng 2023)
              |
              v
    Bias Cataloguing
    (Ye 2024 CALM - 12 biases)
    (Park 2024 OffsetBias - 6 biases)
              |
              v
    Scoring Bias Discovery
    (Li 2025 - 3 scoring biases)
              |
              v
    ------------------------------------------
    |  THIS WORK                          |
    |  Root cause: Base vs Instruct       |
    |  Finding: DIFFERENTIAL effect        |
    |  (**NOBODY HAS DONE THIS**)          |
    ------------------------------------------
              |
              v
    Future: Mitigation strategies
    targeting specific bias channels
```
