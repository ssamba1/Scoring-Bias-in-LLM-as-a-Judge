# Newsletter Blurbs

---

## TLDR AI (50 words)

**Scoring bias in LLM judges: where does it come from?** New research tests 31 model variants (54K judgments) comparing base vs instruct versions. Key finding: instruction tuning reduces format bias (−44% to −77%) but increases content bias in larger (3B+) RLHF models. Code/data open-source. github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

---

## The Batch  DeepLearning.AI (100 words)

**Where Does AI Judge Bias Come From?**

LLMs used as automated judges have known scoring biases, but the origin has been unclear. New research by high school researcher Sricharan Samba provides the first systematic answer.

Testing 31 model variants (54,000 judgments)  including Llama, Mistral, Qwen, and Gemma families  the study compared base models against their instruction-tuned counterparts. The findings: instruction tuning consistently reduces format-related biases (rubric order down 44%, score ID down 77%), but increases content-related bias in larger (3B+) RLHF-trained models. The training method matters too: RLHF, SFT+DPO, and SFT-only families show distinct bias profiles.

The author proposes the Format Efficiency Hypothesis  attention evidence shows format parsing becomes more efficient after instruction tuning (23.7% → 20.8%). All code and data are open-source.

📄 github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge

---

## import AI (150 words)

**The Origin of Scoring Bias in LLM-as-a-Judge**

A fundamental question in AI evaluation has been: where does scoring bias come from? Is it inherent to pre-trained language models, or does it emerge during instruction tuning? A new paper by high school researcher Sricharan Samba provides the first experimental answer.

The study compares base and instruct variants across 9 model families (Llama 3.1/3.2, Mistral 7B, Qwen2.5, Gemma 2, StableLM 2) spanning 0.5B to 671B parameters, plus 22 additional instruct-tuned models  totaling 31 model variants and 54,000 judgments. Using three perturbation probes from Li et al. (DASFAA 2026), the author measures rubric order, score ID, and reference answer bias before and after instruction tuning.

The central finding: instruction tuning has a **differential effect** on scoring bias. Format-related bias decreases consistently across families (rubric order −44%, score ID −77%). Content-related bias increases in larger (3B+) RLHF-trained models (e.g., Llama-3.1-8B shows +1.58 point shift). The SFT+DPO family (Mistral 7B) shows a different pattern. Bayesian analysis confirms Bayes factors > 10,000 for all bias types.

The author proposes the Format Efficiency Hypothesis: attention-weight analysis shows format token attention drops from 23.7% to 20.8% after instruction tuning. Five testable predictions are offered.

**Implication:** Scoring bias is modulated by instruction tuning  mitigation should target alignment, and must treat format robustness and content sensitivity as separate channels.

🔗 Paper, code, data: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
💾 Archived: doi.org/10.5281/zenodo.21361920
