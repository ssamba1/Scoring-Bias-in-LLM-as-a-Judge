# S-Tier Path: No Human Experiments

## Current: ~7.5/10
## Target: 10/10 (NeurIPS/ACL quality)
## Constraint: No human baselines, no raters

---

## Phase 1: Data Max-Out (1 week, $10-30)

### Fix the 4-bit loading → add 3 more families (30 min)
Install updated transformers + bitsandbytes on Kaggle:
```
!pip install -q --upgrade transformers bitsandbytes accelerate
```
Rerun T4 script. This adds:
- **Qwen2.5-7B** (7B, open, shows content ↑?)
- **Mistral-7B-v0.3** (7B, open, Apache 2.0)
- **Llama-3.2-3B** is already done ✅

**N = 9 → 12 families**

### Run on Colab A100 (free, 90 min/week) → 5 more families
Colab gives you a free A100 for 90 min/week. Each model takes ~5 min:
- **Gemma-2-9B** + IT (9B, gated, needs HF_TOKEN)
- **Llama-3.1-8B** + IT (8B, gated  this is the one that showed content ↑ in original Kaggle)
- **Qwen2.5-14B** + IT (14B, open)
- **Mistral-7B-v0.3** (if not done above)
- **DeepSeek-7B** + IT (7B, open)

**N = 12 → 17 families**

### OpenRouter  5 more instruct-only models ($2)
Add 5 more instruct models from the earlier list that failed (Gemini-2.5-Pro, etc.) with the fixed stop tokens.

**N = 17 families + 27 instruct models**

## Phase 2: Statistical Rigor (1 day, $0)

### Replace t-tests with Bayesian hierarchical model
Current issue: N=3-9 families, t-tests are underpowered. Fix:
```python
import pymc as pm
# Hierarchical model: each family has base/instruct delta
# Pooled estimate with partial pooling
```
This properly handles N=9-17. Gives you posterior distributions instead of p-values. NeurIPS papers use this.

### Compute Bayes factors
Instead of "p < 0.05" (which needs N=12+), compute:
- BF > 10 = strong evidence for the differential effect
- Works with any N

### Equivalence test for small models
Test whether small models (≤1.5B) truly show NO content bias increase (not just "not significant").

## Phase 3: Theory Experiments (1 week, $0)

### Attention analysis at 7B  1 hour on Colab A100
Run attention analysis on Llama-3.1-8B (shows content ↑). This tests:
- Format Efficiency Hypothesis: does format attention decrease more at 8B?
- Does content attention finally increase at 8B?

### Ablation: prompt format variations
Currently: single prompt template. Test 5 variations:
- Different rubric wording
- Different separator tokens
- Different item lengths
- This tells you: is the effect robust to prompt changes?

### Token-level bias analysis
Which specific tokens cause the bias? (e.g., does "best" vs "worst" trigger it?)
Use integrated gradients or attention rollout.

## Phase 4: Paper Polish (1 week, $0)

### Write the NeurIPS version
- Add formal problem definition section
- Add experimental pipeline diagram (Mermaid or draw.io)
- Professional figures via seaborn (better defaults)
- Related work table with all 35+ bias types
- 15-page limit (single column)

### Release assets
- **HuggingFace dataset**: ssamba1/scoring-bias (per-item scores, MIT)
- **Binder notebook**: one-click reproduction
- **Twitter/X thread**: 8 tweets with figures

## Phase 5: Submission (Feb deadline)

| Venue | Deadline | Tier | Your edge |
|-------|----------|------|-----------|
| **ACL SRW** | Feb | Student workshop | ✅ Solo HS + open question |
| **NeurIPS HS Track** | May | HS track | ✅ Novel finding |
| **EMNLP main** | May | Top venue | Need 17+ families |
| **ACL main** | Feb | Top venue | Need more theory |

---

## Cost Summary (no humans)

| Item | Cost | Time |
|------|------|------|
| Fix 4-bit + 3 families | $0 | 30 min |
| Colab A100 (5 families) | $0 | 90 min |
| OpenRouter (5 models) | $2 | 2 hrs |
| Bayesian analysis | $0 | 1 day |
| Attention at 7B | $0 | 1 hr |
| Prompt ablation | $0 | 2 hrs |
| Paper polish | $0 | 1 week |
| **Total** | **~$2** | **~2 weeks** |

## Timeline

```
Week 1: Fix 4-bit, run Colab for 5+ families, Bayesian analysis
Week 2: Attention at 7B, prompt ablation, paper polish
Week 3: Release HF dataset, write thread, submit to venue
```

**After Phase 1-5: ~8.5-9.0/10.** Still need citations and venue acceptance for true S-tier, but the paper itself is at competitive level.
