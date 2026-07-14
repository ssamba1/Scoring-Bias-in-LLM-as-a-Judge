# Upgrade Plan: 6.5 → 9.0 Paper

## Current: 6.5/10 (arXiv, ACL SRW)
## Target: 9.0/10 (NeurIPS, ACL main)

---

## 1. Statistical Power: 4 → 9 (Hard, 3-6 months)

**Problem:** N=3 families for base-instruct. Directional only.

**Plan:**
| Step | Cost | Impact |
|------|------|--------|
| Run 12+ open-weight families with base+instruct pairs through OpenRouter | $5-15 | N=3 → N=15. Now you have proper statistical power |
| Include Llama 3, Qwen 2.5, Gemma 3, Mistral, DeepSeek, Phi, OLMo, Solar, Falcon, Yi, DBRX, StableLM | $10-20 for all | Maximum breadth |
| Bayesian hierarchical model (instead of t-tests) | $0 | Proper uncertainty quantification |
| Preregister the replication on OSF | $0 | Addresses the prereg gap |

**Target:** 12+ families, formal significance, Bayesian posteriors.

## 2. Theory: 4 → 9 (Hard, 2-4 months)

**Problem:** IIAR is speculation with no mechanistic evidence.

**Plan:**
| Step | Cost | Impact |
|------|------|--------|
| **Attention head analysis:** Extract attention weights from base vs instruct models on scoring prompts. Compute attention allocated to format vs content tokens | Requires GPU + coding (Kaggle T4, free) | **Core experiment. Turns IIAR from speculation to tested theory.** |
| **Ablation:** Patch instruct attention heads into base models; measure if bias profile shifts | Same as above | Causal evidence |
| **Prediction 1 test:** Correlate attention redistribution ratio κ with bias change Δ | Same as above | Quantitative test of IIAR |
| **Control experiment:** Random token baselines to ensure effects are format/content specific | Same as above | Strengthens claim |

**Target:** IIAR goes from "hypothesis" to "empirically supported mechanism" with attention heatmaps.

## 3. Depth: 5 → 9 (Medium, 1-2 months)

**Problem:** No domain analysis, no per-item stats, no human baseline.

**Plan:**
| Step | Cost | Impact |
|------|------|--------|
| **Domain analysis:** Compute bias per domain (science, math, humanities, tech, daily) to see if bias is domain-specific | $0 (already have per-item scores) | **High-impact finding** |
| **Item-level IRT:** Item difficulty, discrimination, DIF across models | $0 (code written in item_analysis_framework.py) | **Strength of evidence** |
| **Human baseline:** 3 raters on 50 items, 3 probes = 450 judgments | Free (friends/classmates) | **Absolute magnitude claims** |
| **Bayesian item-response model:** Uncertainty per item per model | $0 | Richer analysis |

**Target:** Domain effects, human comparison, IRT metrics.

## 4. Writing & Presentation: 6 → 9 (Easy, 1 week)

**Problem:** Solo HS author writing, functional but not polished.

**Plan:**
| Step | Cost | Impact |
|------|------|--------|
| Pass through Grammarly or similar | Free | Typos, awkward phrasing |
| Add graphical abstract figure | 2 hrs in draw.io | First impression |
| Add experimental pipeline diagram (models → probes → scores → analysis) | 2 hrs | Clarity |
| Write stronger "So what?" in intro and conclusion | 1 hr | Reader retention |
| Add a one-paragraph "Related Work" summary at end of intro to position the paper | 30 min | Context |

## 5. Reproducibility & Data: 7 → 10 (Easy, 1 day)

**Plan:**
| Step | Cost | Impact |
|------|------|--------|
| Upload per-item scores to HuggingFace dataset hub | Free | Community reuse |
| Binder-ready notebook for interactive reproduction | Free (mybinder.org) | Instant reproducibility |
| Zenodo v2 with final dataset | Free | Permanent DOI for data |

## Timeline

```
Week 1-2:   Human baseline (3 raters, 450 judgments)
Week 3-4:   Domain analysis + IRT (code already written)
Week 5-8:   Attention head experiments (Kaggle T4, free)
Week 9-10:  Run 12+ base-instruct families on OpenRouter ($15)
Week 11:    Bayesian reanalysis + preregistration
Week 12:    Writing polish, figures, submission
```

**Total cost:** $15-35 (OpenRouter inference)
**Total time:** 12 weeks

## After This Plan

| Dimension | Current | Target | Key Change |
|-----------|---------|--------|------------|
| Statistical power | 4/10 | 9/10 | N=3 → N=15+ families |
| Theory | 4/10 | 9/10 | IIAR tested via attention analysis |
| Depth | 5/10 | 9/10 | Domain, IRT, human baseline |
| Writing | 6/10 | 9/10 | Polish, figures, structure |
| Reproducibility | 9/10 | 10/10 | HF dataset, Binder |
| Venue fit | 3/10 | 8/10 | Now viable for NeurIPS main |

**Final score:** 6.5/10 → ~8.5-9.0/10 — competitive at NeurIPS/ACL main track.
