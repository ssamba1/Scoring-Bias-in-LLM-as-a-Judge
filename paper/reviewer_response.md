# Reviewer Response Template

## Anticipated Criticisms and Prepared Responses for Study 1

---

### Criticism 1: Small Sample Size (50 items)

**Likely from:** Any reviewer
**Severity:** Medium

**Response:**
We acknowledge that 50 items is smaller than the largest benchmarks (Li et al. used 2,780--5,421 items). However, our design uses 3 repeats per item and 3 variants per probe, yielding 8,100 total judgments. Each condition has 150 observations (50 items × 3 repeats), providing sufficient statistical power for effect size estimation (Cohen's $d$ up to 2.38). Furthermore, our results are consistent with Li et al.'s published flip rates, validating our methodology. We report effect sizes and bootstrap confidence intervals rather than relying solely on $p$-values, following best practices for studies with limited sample sizes.

**Planned fix before resubmission:** Add 50 more items (100 total) in next Kaggle run.

---

### Criticism 2: Not Statistically Significant

**Likely from:** Methodological reviewer
**Severity:** High

**Response:**
We acknowledge that paired $t$-tests with $N=3$ model families (df=2) are underpowered. However, we emphasize:
1. **Effect sizes are large:** Cohen's $d$ ranges from 0.56 to 2.38
2. **Pattern is consistent across all 3 families:** The differential effect (format bias ↓, content bias ↑) holds uniformly
3. **We report full transparency:** All raw scores are available for meta-analysis
4. **We provide power analysis:** $N=5\text{--}6$ families would reach $\alpha=0.05$, $\beta=0.80$

We follow the American Statistical Association's guidelines on $p$-values (Wasserstein et al., 2019): reporting effect sizes and confidence intervals alongside $p$-values.

**Planned fix before resubmission:** Add 2--3 more model families (Qwen 2.5, Phi-3, OLMo) to reach $N=5\text{--}6$.

---

### Criticism 3: Only 2B--8B Models (No 70B+)

**Likely from:** Model-scale reviewer
**Severity:** Medium

**Response:**
We tested the largest models that fit on a single T4 GPU (16 GB VRAM). 70B models require multi-GPU setups (A100/H100). We provide our complete codebase so that researchers with access to larger hardware can replicate and extend our findings. Furthermore, Li et al. found that larger models show less scoring bias, so our results for 2B--8B models likely represent an upper bound on bias magnitude.

**Planned fix before resubmission:** Test one 70B model (Llama 3 70B) via API on a subset of items (~$5 cost).

---

### Criticism 4: No Human Baseline

**Likely from:** Human-evaluation reviewer
**Severity:** Medium

**Response:**
We did not collect human scores because our focus is on the *relative difference* between base and instruct models, not absolute bias magnitude. The consistent differential effect across all 3 families does not require human comparison to validate. However, we acknowledge that human scores would help determine which scoring direction is "correct." We provide a human evaluation protocol for future work (Appendix).

**Planned fix before resubmission:** Collect 5 human raters × 20 items (~1 hour).

---

### Criticism 5: Descriptive Score ID Probe Excluded

**Likely from:** Detail-oriented reviewer
**Severity:** Low

**Response:**
The descriptive probe variant (score as "Poor, Fair, Good, Very Good, Excellent") used a parser that failed to extract scores correctly for some models. We excluded this variant from the Score ID analysis and report results using only the numeric and letter variants, which provide a valid comparison. The rubric order and reference answer probes were unaffected.

**Planned fix before resubmission:** Already fixed in pipeline. Will regenerate in next Kaggle run.

---

### Criticism 6: Single Seed (42) — Results May Not Generalize

**Likely from:** Reproducibility reviewer
**Severity:** Low

**Response:**
We use temperature 0 (deterministic decoding) and a fixed seed for reproducibility. With temperature 0, the model output is deterministic for a given input, so seed variation does not affect results. However, item ordering could affect results in principle.

**Planned fix before resubmission:** Run with 3 different item orderings (seeds 42, 123, 456).

---

### Criticism 7: Single Prompt Template

**Likely from:** Prompt-engineering reviewer
**Severity:** Low

**Response:**
We use the standard scoring prompt format from Prometheus 2 (Kim et al., 2024), following Li et al. Our results are comparable to Li et al.'s published flip rates, suggesting the prompting format is not driving our findings.

**Planned fix before resubmission:** Test with 2 additional prompt templates.

---

### Criticism 8: Novelty — Thakur et al. (2024) Already Compared Base vs Instruct

**Likely from:** Literature-review reviewer
**Severity:** High

**Response:**
Thakur et al. compared base and instruct versions of Llama-2 as *exam-takers* (models being judged) in a fact-checking task. They did not study *scoring bias* — the systematic score shifts caused by prompt perturbations. Our work is the first to compare base vs instruct models as *judges* in a scoring bias context. Furthermore, Thakur et al. did not test the three scoring bias probes (rubric order, score ID, reference answer) that we study. Pan et al. compared base vs instruct for user-assistant bias, not scoring bias. Li et al. explicitly call for root cause analysis of scoring bias, which we provide.

---

### Summary of Planned Fixes

| Fix | Effort | Impact | Timeline |
|-----|--------|--------|----------|
| Add 50 more items | 2 hrs GPU | High | Before submission |
| Add 2 more model families | 4 hrs GPU | High | Before submission |
| Add human baseline | 1 hr | Medium | Before submission |
| Multi-seed analysis | 3× GPU time | Low | Optional |
| 70B model (API) | $5 | Low | Optional |
