# Reddit Post  r/MachineLearning

---

## Title Suggestion

**[R] Scoring Bias in LLM-as-a-Judge: I tested 31 models (54K judgments) and found instruction tuning reduces format bias but increases content bias in larger RLHF models**

---

## Post Body

I just published a study investigating where scoring bias comes from in LLM-as-a-Judge models. Prior work (Li et al., DASFAA 2026) defined three scoring bias types but left the origin question open. I tried to answer it.

**What I did:**
- Compared base vs instruct variants across 9 model families (Llama, Mistral, Qwen, Gemma, StableLM)  that's 24,300 paired judgments
- Added 22 additional instruct-only models for breadth (29,700 more judgments)
- Total: 31 model variants, 54,000 judgments
- Three perturbation probes: Rubric Order (scale reversal), Score ID (numbers vs letters vs words), Reference Answer (good/poor exemplar priming)
- All experiments reproducible, total API cost under $3

**Key findings:**
1. **Format bias decreases after instruction tuning**  rubric order −44%, score ID −77% on average across 9 families
2. **Content bias increases in larger (3B+) RLHF models**  e.g., Llama-3.1-8B shows +1.58 point shift on a 5-point scale after instruction tuning when primed with a poor exemplar
3. **The training method matters**  7 RLHF families show the differential effect; the SFT+DPO family (Mistral 7B) and SFT-only (StableLM 2) show different patterns
4. **Score ID bias has the largest average effect** (Δ=0.68, range 0.00–1.80) across 22 instruct models
5. **Bayes factors > 10,000** for all three bias types  overwhelming evidence
6. **Attention analysis** supports the Format Efficiency Hypothesis: format token attention drops 23.7% → 20.8% after instruction tuning

**Implications:**
- Scoring bias is modulated by instruction tuning, not inherent to pre-training  mitigation should target alignment
- Use numeric labels (lowest bias), test multiple formats, report format and content bias separately
- The format/content differential effect means bias isn't a single number

**Links:**
- GitHub (code + data + paper): https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
- Zenodo archive: https://doi.org/10.5281/zenodo.21361920
- arXiv: Coming soon

Happy to answer questions in the comments!

---

## Q&A Prep  5 Anticipated Questions

### Q1: How did you control for model family quality differences? Maybe base models just score everything randomly.
**A:** We measure bias as the *difference* between control and perturbed conditions within each model, so absolute scoring ability doesn't affect the result. Additionally, we examine four alternative explanations (global scoring shift, single-family dominance, probe ordering, parser artifacts) and find evidence against all four.

### Q2: N=9 families for the base-instruct comparison seems small. How robust are the conclusions?
**A:** We're transparent about this  the paper explicitly calls it exploratory with N=9. The format bias reduction is consistent across 7/9 families (including both small and large models). The content bias finding is scale-dependent and needs replication with more larger model families. Power analysis shows N≥12 families needed for 80% power at α=0.05. Bayesian analysis confirms the directional evidence.

### Q3: Is this just an artifact of using 50 items from synthetic datasets?
**A:** The 50 items span 5 domains (science, technology, humanities, daily life, mathematics) and were sampled from established evaluation sets (AlpacaEval, MT-Bench) rewritten to be mid-quality (~3-4/5). The perturbations are within-model comparisons, so item selection affects absolute scores but not the bias *difference* we report.

### Q4: What about models trained after your paper? Would these findings generalize to GPT-5, Claude 4, etc.?
**A:** The study uses only open-weight models available at the time of experimentation. Commercial API models (GPT-4, Claude) were not tested due to cost constraints. The Format Efficiency Hypothesis makes specific predictions that can be tested on any model  and we'd love to see replications on frontier models!

### Q5: Is the Format Efficiency Hypothesis just a post-hoc explanation?
**A:** The hypothesis was developed after observing the pattern, yes. But it makes five specific, testable predictions (detailed in the paper's discussion section): (1) format improvements should increase with model size, (2) content sensitivity should also increase with size, (3) the effect should be independent of prompt length, (4) SFT-only models should show weaker effects, (5) embedding similarity between base and instruct should correlate with bias change. These can be confirmed or refuted in future work.
