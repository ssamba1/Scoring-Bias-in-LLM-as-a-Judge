# Conference Poster Abstract

## Scoring Bias in LLM-as-a-Judge Models: Visual Evidence from a 31-Model Study

**Sricharan Samba**  South Forsyth High School
srisamba09@gmail.com

---

### Abstract (250 words)

LLMs serving as automated judges exhibit systematic scoring biases that undermine the reliability of AI evaluation. While prior work has identified these biases, the question of their originwhether from pre-training or instruction tuninghas remained unanswered. We present a large-scale visual analysis of scoring bias across 31 model variants (54,000 judgments) comparing base and instruct-tuned models.

**Method:** Using three perturbation probes (rubric order reversal, score ID relabeling from numbers to letters to descriptive words, and reference answer exemplar priming), we measure bias magnitude (Δ) across 9 base-instruct family pairs and 22 additional instruct models.

**Visual Results:**
1. **Bias Landscape** (Fig. 1): Score ID bias dominates (mean Δ = 0.68, range 0.00–1.80) across 22 instruct models. Rubric order shows the widest model-to-model variation (0.10–1.50).
2. **Format-Content Scatter** (Fig. 2): 7/9 model families show a clear patternformat bias decreases while content bias changes variably by scale. Models in the differential-effect quadrant cluster separately.
3. **Scale-Dependent Effect** (Fig. 3): Format bias decreases across all scales (≤1.5B to 8B+). Content bias only increases in 3B+ RLHF models, producing a crossover pattern.
4. **Base-Instruct Paired Comparison** (Fig. 7): Spider-line visualization shows every family's bias trajectory from base to instruct, revealing consistent format improvement and divergent content outcomes.
5. **Attention Evidence** (Fig. 8): Format token attention drops from 23.7% to 20.8% after instruction tuningsupporting the Format Efficiency Hypothesis.

**Conclusion:** Scoring bias is modulated by instruction tuning, not pre-training. Mitigation must target alignment and treat format robustness and content sensitivity as separate channels. All data and visualizations are publicly available.

---

**Poster highlights:** Large-format bias landscape heatmap, interactive QR code linking to the full interactive dashboard, and an annotated attention-weight visualization wall.

**Interactive demo:** https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
