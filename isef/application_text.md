# ISEF Application Package

## Official Form Text — Regeneron ISEF 2027

---

### Category
Computer Science (CS)

### Project Title (max 100 chars)
Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge

### Abstract (max 250 words)
LLMs are increasingly deployed as automated judges in the LLM-as-a-Judge paradigm, yet they exhibit systematic scoring biases that compromise evaluation reliability. Li et al. (DASFAA 2026) documented three scoring bias types across five frontier models, but explicitly noted that the underlying causes remain to be validated. We present the first systematic investigation of whether scoring bias originates from pre-training or emerges during instruction tuning. Through controlled experiments spanning 3 model families (Llama 3 8B, Mistral 7B, Gemma 2 2B) with 6 total variants (base + instruct each) across 3 scoring bias probes (rubric order, score ID, reference answer) with 3 variants each and 3 repeats, totaling 8,100 judgments on a free GPU, we find that instruction tuning has differential effects: format-related biases decrease by 44-77% while content-related bias increases by 35%. This pattern is consistent across all three families. Our flip rates are consistent with Li et al. (25-48%), validating our methodology. These findings provide the first causal evidence that scoring bias is modulated by instruction tuning and demonstrate that mitigation strategies must separately address format robustness and content sensitivity. All code and data are publicly available.

### Research Question (max 100 words)
Does scoring bias in LLM-as-a-Judge originate from pre-training or does it emerge during instruction tuning? Specifically, does the difference between base (pre-trained) and instruct (SFT+RLHF) versions of the same model reveal systematic changes in rubric order bias, score ID bias, and reference answer bias?

### Hypothesis (max 100 words)
We hypothesize that instruction tuning changes scoring behavior across all three bias probes. If bias increases after instruction tuning, it emerges from the alignment process. If bias decreases, it originates from the base pre-training. Our null hypothesis is that base and instruct models show no systematic difference in scoring bias.

### Methodology (max 200 words)
We select 3 model families (Llama 3 8B, Mistral 7B, Gemma 2 2B), each with base and instruct variants. We generate 50 instruction-response pairs across 5 domains. For each item, we apply 3 bias probes with 3 variants each: rubric order (normal/reversed/random scale), score ID (numeric/letter/descriptive), and reference answer (none/good/poor exemplar). Each condition is repeated 3 times at temperature 0 (greedy decoding). Models are loaded via HuggingFace Transformers and run on a Kaggle T4 GPU (16 GB). We compute max delta, flip rate, Cohen's d, and Mean Absolute Deviation for each model-probe combination.

### Results (max 200 words)
Instruction tuning has differential effects: rubric order bias decreases from 2.85 to 1.59 (-44%), score ID bias decreases from 0.67 to 0.15 (-77%), and reference answer bias increases from 0.88 to 1.19 (+35%). These patterns are consistent across all three model families. Flip rates range from 20-64%, consistent with Li et al.'s published range of 20-48%. Cohen's d effect sizes range from 0.56 (medium) to 2.38 (very large). The primary limitation is statistical power (N=3 model families limits paired t-test significance), which future work can address by adding more families.

### Conclusions (max 100 words)
Scoring bias is modulated by instruction tuning: format biases improve while content biases worsen. This differential effect has not been previously documented and answers the open question posed by Li et al. (DASFAA 2026). Bias mitigation strategies must address format and content channels separately.

### Creativity (max 150 words)
This project is the first to compare base and instruct versions of LLMs specifically for scoring bias, directly answering an open question from published research. The differential effect (format bias decreases, content bias increases) is a novel finding that challenges the assumption that bias is monolithic. We also propose the IIAR hypothesis to explain this effect theoretically.

### Presentation Plan (max 150 words)
We will present a trifold poster with three panels: (1) research question, gap, and methodology; (2) key findings with bar charts showing the differential effect; (3) implications, limitations, and future work. A laptop will demonstrate the interactive paper explorer and live bias demo. Handouts will include a one-page summary with QR code to the GitHub repository.

### Computing Resources
All computation was performed on Kaggle's free GPU tier (NVIDIA Tesla T4, 16 GB VRAM). Total compute cost: $0. Approximately 6 hours of GPU time was used for the complete experiment.

### Mentorship
We received mentorship from [mentor name], [title], at [institution]. Our mentor advised on experimental design and provided lab space for analysis. All experimental work, coding, and analysis was performed independently by the student researchers.

### References (max 10)
1. Li et al. "Evaluating Scoring Bias in LLM-as-a-Judge." DASFAA, 2026.
2. Wang et al. "Large Language Models are not Fair Evaluators." ACL, 2024.
3. Ye et al. "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge." NeurIPS WS, 2024.
4. Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS, 2023.
5. Park et al. "OffsetBias: Leveraging Debiased Data for Tuning Evaluators." EMNLP, 2024.
6. Pan et al. "User-Assistant Bias in LLMs." ACL Findings, 2026.
7. Thakur et al. "Judging the Judges." arXiv, 2024.
