# Conference Talk Abstract

## Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison

**Sricharan Samba** — South Forsyth High School
srisamba09@gmail.com

---

### Abstract (250 words)

LLMs deployed as automated judges exhibit systematic scoring biases, but the origin of these biases—whether from pre-training or instruction tuning—remains unknown. We present the first large-scale investigation of this question, comparing base and instruct variants across 9 model families (24,300 paired judgments) alongside 22 additional instruct-tuned models (29,700 judgments), totaling 31 model variants spanning dense and MoE architectures from 0.5B to 671B parameters.

Using three perturbation probes (rubric order reversal, score ID relabeling, and reference answer exemplar priming), we measure scoring bias before and after instruction tuning. We find a robust differential effect: instruction tuning consistently reduces format-related bias (rubric order −44%, score ID −77% on average) while increasing content-related bias in larger (3B+) RLHF-trained models (e.g., Llama-3.1-8B: Δ = +1.58 on a 5-point scale). The SFT+DPO family (Mistral 7B) and SFT-only family (StableLM 2) show distinct patterns, suggesting training method modulates the effect. Bayesian analysis confirms Bayes factors > 10,000 for all three bias types across the 22-model landscape.

We propose the Format Efficiency Hypothesis as a mechanistic explanation: attention-weight analysis reveals instruction tuning reduces format token attention from 23.7% to 20.8%, making format parsing more efficient without proportionally increasing content attention. Five testable predictions are offered for future validation.

Our central implication is that scoring bias is modulated by instruction tuning—not inherent to pre-training—meaning mitigation strategies should target the alignment stage and address format robustness and content sensitivity as separate channels. All code, data, and analyses are publicly released for full reproducibility.

---

**Keywords:** LLM-as-a-Judge, scoring bias, instruction tuning, bias measurement, evaluation, AI safety

**Suggested venues:** NeurIPS High School Track, ACL Student Research Workshop, ICML AI Safety Workshop
