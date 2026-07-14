# Honest Depth Assessment

## Can this be a solid research paper?

---

## The Good

**The core finding is genuinely novel and interesting.** Nobody has shown the differential effect before. That alone is a publishable contribution.

**The experimental design is clean.** Base vs instruct comparison is the right way to isolate where bias comes from. Three complementary probes. Consistent across models.

**The reproducibility is best-in-class.** $0 cost, open source, Docker, CI/CD, complete pipeline. Very few papers at any level have this.

---

## The Depth Problem

**What this paper currently is:**
- "We tested 3/15/44 models and found that format bias decreases and content bias increases."
- That's a *finding*, not a *depth piece*.

**What a deep research paper has on top of the finding:**

| Depth Element | Our Paper | A Deep Paper Would Have |
|-------------|-----------|----------------------|
| **Causal mechanism** | IIAR hypothesis (verbal only) | Attention head analysis, ablation studies showing *which* specific heads cause the effect |
| **Formal theory** | One equation | Full theorem + proof framework, bounds, predictions |
| **Robustness checks** | None | Cross-validation, different split methods, bootstrap across items, leave-one-out analysis |
| **Alternative explanations** | Not discussed | Explicitly test and rule out 3+ alternative hypotheses |
| **Failure cases** | Not discussed | Show *where* the effect breaks down — which models/items don't follow the pattern |
| **Quantitative prediction** | None | "The model predicts that a 13B model with DPO training will have X% less format bias and Y% more content bias" — then verify |
| **Practical mitigation** | Suggested verbally | Implemented and tested 5 methods, measured effectiveness |
| **Literature synthesis** | Listed papers | Formal meta-analysis showing effect sizes across all prior work |
| **Limitations** | Listed (brief) | Quantified impact of each limitation ("with N=44, our power is 99% for rubric order but only 55% for score ID") |

---

## What It Would Take to Have Real Depth

| Work | Time | What It Unlocks |
|------|------|----------------|
| **Implement the IIAR hypothesis** — show embedding shifts between base and instruct under biased probes | 2 hrs | Causal evidence for the theory |
| **Ablation: test on SFT-only vs DPO-only models** (not just combined instruct) | 4 hrs GPU | Which training stage causes which effect? |
| **Write and test 3 alternative hypotheses** (e.g., "bias is from data distribution, not instruction tuning") | 2 hrs | Rules out other explanations |
| **Quantify limitation impact** on every conclusion | 1 hr | Honest bounds on claims |
| **Implement + test 2 mitigation methods** (calibration, ensemble) | 3 hrs | Practical contribution |
| **Full formal framework** with bounds, predictions, verification | 4 hrs | Theoretical depth |

**Total additional work: ~18 hours.** That transforms it from "a finding" to "a deep paper."

---

## The Verdict

**Is it publishable now?** Yes. The differential effect is novel and the experiment is clean.

**Is it a DEEP paper?** Not yet. It's a solid empirical paper with one strong finding. It lacks causal mechanism, robustness checks, alternative explanations, failure analysis, and practical mitigation.

**Does it need to be deep to get published?** No. Many conference papers are "finding + clean experiment + discussion." Look at Li et al. (DASFAA 2026) — they identified the biases but had no base vs instruct comparison, no causal theory, no mitigation, and they got published.

**Should you add depth?** Only if you want to target higher-tier venues. For arXiv + ACL Student Workshop, what you have is enough. For NeurIPS main track, you'd need more.

**My recommendation:** Publish the current version on arXiv this week. Then add depth over the next month for ACL Student Workshop submission.
