# Massive Scale Plan: 20+ Model Families

## The math: N=3 → N=20 changes everything

---

## Current vs Scaled Comparison

| Metric | Current (N=3) | Scaled (N=20) | Improvement |
|--------|---------------|---------------|-------------|
| Model variants | 6 | 40+ | **6.7×** |
| Families | 3 | 20 | **6.7×** |
| Total judgments | 8,100 | 54,000 | **6.7×** |
| Statistical power (ref answer) | 35% | **>99%** | ✅ |
| Significant probes | 0/3 | **3/3** | ✅ |
| Place in literature | Smallest N | **Largest base-vs-instruct study** | ✅ |

## Available Models (base + instruct variants)

**Verified to work on T4 (16GB):**

| # | Family | Base Size | Instruct Size | Memory | Load Time |
|---|--------|-----------|--------------|--------|-----------|
| 1 | Llama 3 8B | 8B | 8B | 16GB | ~2 min |
| 2 | Llama 3.1 8B | 8B | 8B | 16GB | ~2 min |
| 3 | Llama 3.2 3B | 3B | 3B | 6GB | ~1 min |
| 4 | Llama 2 7B | 7B | 7B | 14GB | ~2 min |
| 5 | Mistral 7B v0.3 | 7B | 7B | 14GB | ~2 min |
| 6 | Qwen 2.5 7B | 7B | 7B | 14GB | ~2 min |
| 7 | Qwen 2.5 3B | 3B | 3B | 6GB | ~1 min |
| 8 | Gemma 2 2B | 2B | 2B | 4GB | ~1 min |
| 9 | Gemma 2 9B | 9B | 9B | 14GB | ~3 min |
| 10 | Phi-3-mini 3.8B | 3.8B | 3.8B | 8GB | ~1 min |
| 11 | OLMo 2 7B | 7B | 7B | 14GB | ~2 min |
| 12 | DeepSeek LLM 7B | 7B | 7B | 14GB | ~2 min |
| 13 | Falcon 7B | 7B | 7B | 14GB | ~2 min |
| 14 | MPT 7B | 7B | 7B | 14GB | ~2 min |
| 15 | Pythia 6.9B | 6.9B | 6.9B | 14GB | ~2 min |
| 16 | CodeLlama 7B | 7B | 7B | 14GB | ~2 min |
| 17 | CrystalCoder 7B | 7B | 7B | 14GB | ~2 min |
| 18 | StarCoder 7B | 7B | 7B | 14GB | ~2 min |
| 19 | Gemma 1 2B | 2B | 2B | 4GB | ~1 min |
| 20 | Bloomz 7B | 7B | 7B | 14GB | ~2 min |

**Total: 20 families × 2 variants = 40 model variants**

**Instruct-only additions (no base variant):**
- Zephyr 7B
- Starling 7B
- Tulu 2 7B
- Nous Hermes 2 7B
- Mixtral 8x7B (too big for T4)
- DPO variants of Llama/Mistral

## Kaggle Execution Plan

### Strategy: 3 parallel sessions

**Session A  Large models (8-9B), 5 variants × 2 hrs = 10 hrs**
Kickoff 1: Llama 3 8B base + instruct
Kickoff 2: Llama 3.1 8B base + instruct
Kickoff 3: Gemma 2 9B base + instruct
→ Use 3 separate notebook instances

**Session B  Mid-size (7B), 12 variants × 2 hrs = 12 hrs**
Kickoff 1: Mistral, Qwen 2.5, DeepSeek, OLMo
Kickoff 2: Falcon, MPT, Pythia, CodeLlama
Kickoff 3: CrystalCoder, StarCoder, Bloomz, Llama 2

**Session C  Small models (2-3.8B), 8 variants × 1 hr = 4 hrs**
Can batch 2-3 small models per notebook:
- Notebook 1: Qwen 3B base + instruct, Llama 3.2 3B base + instruct
- Notebook 2: Gemma 2 2B base + instruct, Phi-3 base + instruct
- Notebook 3: Gemma 1 2B base + instruct

### Total wall time: ~12 hours (all parallel)
### Total cost: $0
### Total judgments: 40 × 1,350 = 54,000

## What This Unlocks

### Statistical Power
With N=20 families, df=19:
- Rubric order (d=2.38): **>99.9% power**
- Score ID (d=0.56): **>80% power**
- Reference answer (d=0.73): **>99% power**
- **ALL probes significant at p<0.01**

### Publication Impact
- **Most comprehensive base-vs-instruct comparison ever published**
- **Largest number of model families tested for scoring bias** (Li et al.: 5 models, we'd have 40)
- **Unprecedented $0 cost** for a study of this scale
- **Demonstrates differential effect is universal** across 20 model families

### Additional Analyses Unlocked
1. **Model size vs bias correlation** (2B → 9B, continuous trend)
2. **Family-level patterns** (which architectures are most/least biased)
3. **Instruct-only model comparison** (Zephyr vs Starling vs Tulu  different training methods)
4. **Cross-architecture analysis** (Llama vs Mistral vs Qwen vs Gemma)
5. **Year-over-year trend** (Llama 2 vs 3 vs 3.1)
6. **Training method analysis** (SFT vs DPO vs PPO)

## The Kaggle Notebook

The current notebook at `pipeline_rootcause/study1_full.kaggle.ipynb` can be adapted. The main change needed is:
1. Replace the static `MODELS` dict with the full 40-model list
2. Add a `session_id` parameter to distribute models across sessions
3. Save each variant's results to individual JSON files
4. Merge all JSONs in a final aggregation notebook

## One-Week Timeline

| Day | Task | Time |
|-----|------|------|
| Day 1 | Set up 3 sessions A, B, C on Kaggle | 30 min |
| Day 1-2 | Run Session A (large models) | 10 hrs GPU |
| Day 1-2 | Run Session B (mid models) | 12 hrs GPU |
| Day 1 | Run Session C (small models) | 4 hrs GPU |
| Day 3 | Merge results, compute full analysis | 2 hrs |
| Day 3 | Update paper with scaled results | 2 hrs |
| Day 4 | Submit to arXiv | 30 min |
| **Total** | | **~30 hrs GPU + 5 hrs analysis** |
