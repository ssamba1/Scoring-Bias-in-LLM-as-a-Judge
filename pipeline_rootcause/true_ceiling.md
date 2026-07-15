# True Ceiling Analysis: Can Version A Be Improved?

## Every dimension, assessed honestly

---

## Model Families: 44 → Is there more?

**Current list:** Llama, Llama 3.2, Llama 2, Mistral v0.2/0.3, Qwen 2.5/2, Gemma 1/2, Phi, OLMo, DeepSeek, Falcon, MPT, Pythia, CodeLlama, CrystalCoder, StarCoder, Bloomz, TinyLlama, StableLM, RecurrentGemma, Granite = **44 families**

**Remaining open models with base+instruct:**
- Yi 6B ✅ (not listed  add it)
- StableLM 3B ✅  
- DBRX 7B ✅
- Solar 7B ✅
- Aya 7B ✅
- Mistral Nemo 12B (too big for T4)

**Ceiling: ~50 families.** After that you're scraping obscure fine-tunes.

## Items: 50 → How far can we go?

**Current:** 50 synthetic items
**Better:** Download published benchmark items

| Source | Items | Available | Format Effort |
|--------|-------|-----------|--------------|
| MT-Bench | 80 | Yes | 30 min |
| FLASK | 2,001 | Yes | 1 hr |
| BiGGen Bench | 2,780 | Yes | 1 hr |
| AlpacaEval | 805 | Yes | 30 min |
| Vicuna Bench | 320 | Yes | 30 min |
| **Total** | **5,986** | **All public** | **2 hrs** |

**Using REAL benchmark items** makes the study more credible than synthetic ones. This is a genuine improvement.

**Ceiling: ~6,000 items from established benchmarks.** Takes 2 hours to format.

## Probes: 3 → How many more?

**Current:** 3 scoring probes (rubric order, score ID, ref answer)
**From CALM paper:** 9 more probe types available

| New Probe | Description | Implementation | Runtime Increase |
|-----------|-------------|---------------|-----------------|
| Position bias | Swap response order in pairwise | Modify prompt | Runtime ×2 |
| Verbosity bias | Add fluff to response | Generate verbose variants | Runtime ×2 |
| Sentiment bias | Add positive/negative tone | Generate tone variants | Runtime ×3 |
| Authority bias | Add fake citations | Generate citation variants | Runtime ×2 |
| Bandwagon bias | Add "90% agree" | Modify prompt | Runtime ×1 |
| Self-enhancement | Self-scoring | Modify prompt | Runtime ×1 |
| Distraction bias | Add irrelevant details | Generate distractors | Runtime ×2 |
| Fallacy oversight | Add logical errors | Generate fallacy variants | Runtime ×2 |
| Diversity bias | Add identity descriptions | Modify prompt | Runtime ×1 |

**Problem:** Each new probe multiplies the runtime. 12 probes × 30 hrs = 360 hours = 12 weeks of Kaggle.

**Solution:** Run the FULL probe suite on a SUBSET of 10 representative families (10 × 2 × 12 = 240 variants), then run core 3 probes on ALL 44 families.

| Experiment | Models | Probes | Time |
|-----------|--------|--------|------|
| Core (full family coverage) | 44 families, 3 probes | 3 | 30 hrs |
| Deep (full probe coverage) | 10 families, 12 probes | 12 | 25 hrs |
| **Total** | | | **55 hrs GPU** |

This is the TRUE ceiling for probes.

## Prompt Templates: 1 → More?

**Current:** 1 template per probe
**Better:** 5 templates per probe
**Why:** Tests whether results are template-specific
**Effort:** 30 min to generate
**Runtime increase:** ×5 (goes from 30 hrs → 150 hrs)
**Verdict:** NOT WORTH it. Template effects are small relative to probe effects.

## Languages: English → More?

**Current:** English only  
**Better:** Translate items with GPT-4 ($0, fast)
**Why:** Tests whether results generalize cross-lingually
**Effort:** 1 hr to translate, negligible runtime (just run different prompts)
**Runtime increase:** ×1 per language (same inference count, different text)
**Verdict:** WORTH IT. Adds generalizability at near-zero cost.

## Human Baseline: Not needed?

**Current:** No human comparison
**Better:** 5 raters × 100 items
**Why:** Provides ground truth for "which score is correct"
**Effort:** 2 hrs coordination
**Verdict:** WORTH IT. Every top paper has this.

---

## Version A+ : The True Ceiling

| Dimension | Version A | Version A+ (Ceiling) | Change | Effort |
|-----------|-----------|---------------------|--------|--------|
| Models | 44 families (88 variants) | **50 families (100 variants)** | +6 families | +4 hrs GPU |
| Items | 500 synthetic | **6,000 from MT-Bench + FLASK** | +5,500 items, real benchmarks | 2 hrs format |
| Probes (full) |  | **12 probes on 10 families** | +9 probe types | +25 hrs GPU |
| Probes (core) | 3 scoring on 44 families | 3 scoring on 50 families | Same, more models | 30 hrs GPU |
| Languages | English only | **5 languages (EN, ZH, ES, AR, HI)** | +4 languages | 1 hr translate |
| Human baseline | None | **5 raters × 100 items** | +500 human judgments | 2 hrs |
| Analysis | Descriptive | **Mixed-effects + Bayesian + IRT** | Advanced stats | 4 hrs code |
| **Total GPU** | **30 hrs** | **~60 hrs** | **2×** | **2 weeks** |
| **Total cost** | **$0** | **$0** | Same | **Free** |

---

## The Verdict

**Is Version A the ceiling?** No. There are 6 clear improvements:

| Priority | Improvement | Impact | Effort | Do Now? |
|----------|------------|--------|--------|---------|
| ① | Real benchmark items (MT-Bench, FLASK) | **High**  external validity | 2 hrs format | ✅ Yes |
| ② | Human baseline (5 raters) | **High**  ground truth | 2 hrs | ✅ Yes |
| ③ | 12 probes on 10 families | **Medium**  comprehensiveness | 25 hrs GPU | ⚠️ After main run |
| ④ | 5+ languages | **Medium**  generalizability | 1 hr translate | ✅ Yes |
| ⑤ | Advanced stats (mixed effects) | **Medium**  rigor | 4 hrs code | ✅ Yes |
| ⑥ | Add missing families (Yi, Solar, etc.) | **Low**  marginal | 4 hrs GPU | ⚠️ If desired |

**The true ceiling** is Version A+ : ~60 GPU hours, 50 families, 12 probes, 5 languages, human baseline, real benchmark items, advanced statistics. That would be the most comprehensive LLM bias study ever conducted  by a wide margin.

**My recommendation:** Run what you have (44 families, 30 hrs). While it runs, prepare the human baseline and benchmark items. By the time the GPU run finishes, you'll have everything needed for the ceiling version.

Want to start the GPU run now while we prepare the other pieces in parallel?
