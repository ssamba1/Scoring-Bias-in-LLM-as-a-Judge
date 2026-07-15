# Press Release

## Solo High School Researcher Publishes Landmark Study on AI Judge Bias

**54,000 judgments across 31 AI models reveals where scoring bias comes from  and how to fix it**

---

**FOR IMMEDIATE RELEASE** | July 14, 2026

**Contact:**
Sricharan Samba
Email: srisamba09@gmail.com
GitHub: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
Zenodo: doi.org/10.5281/zenodo.21361920

---

**FORSYTH COUNTY, GA**  A high school researcher at South Forsyth High School has published a landmark study investigating the origins of scoring bias in AI systems used to evaluate other AI  a finding with direct implications for AI safety, benchmarking, and model development.

Sricharan Samba's paper, "Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison," answers a fundamental question that has eluded the AI research community: does scoring bias come from pre-training, or does it emerge during instruction tuning?

The answer: **it depends on the type of bias.**

### Key Findings

- **Format-related bias decreases after instruction tuning.** Models fine-tuned to follow instructions are significantly better at understanding scoring formats. Rubric order bias dropped by 44% on average, and score ID bias (changing numbers to letters) dropped by 77% across 9 model families.

- **Content-related bias increases  but only in larger RLHF-trained models.** When shown a poor example answer before scoring, larger instruction-tuned models (3 billion+ parameters) became more biased. One model (Llama-3.1-8B) showed a 1.58-point shift on a 5-point scale after instruction tuning.

- **Training method matters.** Seven RLHF-trained families showed the differential effect, while the SFT+DPO family (Mistral 7B) and SFT-only (StableLM 2) showed different patterns.

- **Score ID bias is the most pervasive problem.** Across all models tested, changing score labels from numbers to letters to descriptive words caused an average shift of 0.68 points on a 5-point scale, with some models showing shifts as large as 1.80 points.

- **Bayesian analysis confirms overwhelming evidence.** Bayes factors exceeding 10,000 confirm that scoring bias exists across instruct-tuned models.

The study tested 31 model variants  including Meta Llama, Mistral, Qwen, Google Gemma, DeepSeek, Microsoft Phi-4, and others  collecting 54,000 judgments. Remarkably, the entire experiment cost less than $3 in API fees and is fully reproducible using free Kaggle GPUs.

### The Format Efficiency Hypothesis

Beyond documenting the phenomenon, Samba proposes a mechanistic explanation called the Format Efficiency Hypothesis. Attention-weight analysis reveals that instruction tuning makes models more efficient at parsing scoring formats  format token attention drops from 23.7% to 20.8%  reducing format-related errors without proportionally increasing content attention.

### Practical Implications

- **For AI developers:** Use numeric labels (1–5) for scoring rubrics  they show the lowest bias
- **For benchmark designers:** Always test multiple scoring formats and report format and content bias separately
- **For AI safety:** The finding that bias is modulated by instruction tuning (not inherent to pre-training) means mitigation strategies should target the alignment stage

### About the Researcher

Sricharan Samba is a high school student at South Forsyth High School in Forsyth County, Georgia. His research focuses on AI alignment and evaluation, with particular emphasis on understanding and mitigating bias in LLM-based evaluation systems. This work was conducted independently using publicly available models and tools.

### Availability

The full paper, code, data, and interactive dashboards are publicly available under CC-BY 4.0 license at:
- **GitHub:** https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
- **Zenodo:** https://doi.org/10.5281/zenodo.21361920
- **arXiv:** Coming soon

### Quote from the Researcher

> "When I started this project, I wanted to answer a deceptively simple question: when an AI judges another AI, can we trust the score? The answer isn't a simple yes or no  it depends on what kind of bias you're looking at and how the model was trained. What excites me most is that because scoring bias emerges during instruction tuning rather than being baked into pre-training, we have a clear path forward: we can fix this by improving how we align models. I hope this work encourages more researchers  especially students  to dig into AI safety questions that don't require massive budgets, just clear thinking and rigorous methods."

###

*Note to editors: Figures, interactive dashboards, and interview availability upon request.*
