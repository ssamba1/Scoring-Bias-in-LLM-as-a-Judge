# FINAL SYNTHESIS — Exhaustive Research Gap Audit

## Sources
- **My research:** ~60 papers read, 30+ search dimensions
- **Subagent 1:** 35 bias types cataloged, 25+ searches
- **Subagent 2:** 12 activation steering challenges audited, 40 papers checked
- **Subagent 3:** 10 untouched niche angles, 40+ searches

---

## Part A: Activation Steering — VERDICT: Do NOT pursue

| Finding | Source |
|---|---|
| 0 of 12 challenges fully solved | Subagent 2 |
| But 9 of 12 have partial solutions | Subagent 2 |
| New problems discovered (safety deterioration, non-identifiability) | Subagent 2 |
| Requires GPU, complex setup, fast-moving field | My research |
| **Recommendation:** Skip. Too competitive, too much compute needed, too fast-moving for HS timeline. | Consensus |

---

## Part B: LLM-as-a-Judge — Verified Untouched Niches

### Inventory of ALL documented bias types (35 total)
- 12 have at least one mitigation paper
- **23 have ZERO peer-reviewed mitigation** — confirmed research gaps
- Source: Subagent 1's complete inventory at `C:\Users\Admin\Hermes\llm-as-a-judge-bias-inventory.md`

### Verified Untouched Niche Rankings

| Rank | Niche | Confirmed By | ISEF Potential | Cost | Risk |
|------|-------|-------------|----------------|------|------|
| **1** | **Root Cause of Scoring Bias** (base→instruct→RLHF comparison) | Me + Li et al. 2025 call | HIGH | ~$50 GPU | Low |
| **2** | **Bias Interaction Effects** (do biases compound or cancel?) | Subagent 3 | HIGH | $0 GPU (API only) | Low |
| **3** | **Practical Cost of Bias (Rank Reversal)** | Me | MED-HIGH | $0 GPU | Low |
| **4** | **Judge Fatigue Over Long Sessions** | Subagent 3 | HIGH | $0 GPU | Medium |
| **5** | **Cross-Domain Scoring Bias Comparison** | Me | MED | $0 GPU | Low |
| **6** | **Multi-turn vs Single-turn Bias** | Subagent 3 | HIGH | $0 GPU | Medium |
| **7** | **Family Bias Mitigation** | Subagent 1 | MED | $0 GPU | Low |

---

## Part C: The Two Best Options — Detailed Comparison

### Option 1: Root Cause of Scoring Bias
**Ask:** Does LLM judge scoring bias (rubric order, score ID, reference answer score) originate from pre-training, instruction tuning, or RLHF?

**How:** Compare Llama 3 8B (base) → Instruct → RLHF on the same scoring bias tests

**Evidence gap is real:**
- Li et al. 2025: *"underlying causes of scoring bias remain to be validated"*
- Pan et al. 2025 proved methodology works for a different bias
- Zero papers have applied this to scoring bias

**Pros:** Causal design, directly answers published open question
**Cons:** Needs ~$50 GPU, 3 model checkpoints to load

### Option 2: Bias Interaction Effects
**Ask:** When multiple biases are present simultaneously (e.g., position bias + verbosity bias), do they compound, cancel, or interact non-linearly?

**How:** Full-factorial 2×2 experiment: [long/short response] × [first/second position], measure which bias dominates

**Evidence gap is real:**
- Blog posts note "biases interact" but zero systematic studies (Subagent 3)
- Soumik 2026 mentions cross-bias analysis but doesn't deeply study it
- Clean experimental design

**Pros:** Pure API calls, zero GPU, elegant statistics
**Cons:** Descriptive rather than causal; less "deep" story

---

## Final Recommendation

**If you want the strongest causal science story → Option 1 (Root Cause)**
- Better for ISEF: "I discovered WHERE LLM bias comes from"
- Directly responds to Li et al. 2025's explicit call
- Proven methodology (Pan et al. 2025)
- Slightly more compute needed

**If you want the cleanest, cheapest, fastest path → Option 2 (Bias Interaction)**
- Zero GPU, just API calls
- Full-factorial experimental design is statistically rigorous
- Nobody has done this systematically
- Faster execution (2-3 weeks)

Both are **confirmed untouched** with zero dedicated papers.
