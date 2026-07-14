# Bias Glossary

| Term | Definition |
|------|-----------|
| **LLM-as-a-Judge** | Using a language model to evaluate the quality of another model's response |
| **Scoring bias** | Systematic score changes due to superficial prompt features, not response quality |
| **Rubric order bias** | Score changes when the rubric scale is reversed (1=best vs 1=worst) |
| **Score ID bias** | Score changes when labels change (numbers vs letters vs words) |
| **Reference answer bias** | Score changes when an example answer is shown before scoring |
| **Base model** | Pre-trained language model, no instruction tuning |
| **Instruct model** | Base model further trained with SFT + RLHF to follow instructions |
| **Instruction tuning** | Training process (SFT + RLHF) that teaches models to follow instructions |
| **SFT** | Supervised Fine-Tuning — training on human demonstrations |
| **RLHF** | Reinforcement Learning from Human Feedback |
| **Flip Rate (FR)** | Proportion of items where biased score differs from control |
| **Mean Absolute Deviation (MAD)** | Average absolute difference between scores |
| **Cohen's d** | Standardized effect size measure |
| **Spearman's ρ** | Rank correlation between scores |
| **IIAR hypothesis** | Instruction-Induced Attention Redistribution — our theory for the differential effect |
| **Differential effect** | Format biases ↓, content biases ↑ after instruction tuning |

# FAQ

**Q: Why does this matter?**
A: LLMs are used to evaluate other AI systems in benchmarks like Chatbot Arena, MT-Bench, and AlpacaEval. If the judges are biased, model rankings are unreliable. Understanding where the bias comes from is the first step to fixing it.

**Q: How is this different from prior work?**
A: Prior work (Li et al., DASFAA 2026) documented scoring biases but didn't investigate their origin. We're the first to compare base and instruct models for scoring bias, showing it's learned during instruction tuning.

**Q: What's the main finding?**
A: Instruction tuning has a DIFFERENTIAL effect: format-related biases (rubric order, score ID) decrease by 44-77%, while content-related bias (reference answer) increases by 35%. This has never been shown before.

**Q: How many models did you test?**
A: 44 model families with both base and instruct variants = 88 total model variants. This is the largest study of its kind.

**Q: How much did this cost?**
A: $0. Everything ran on Kaggle's free GPU tier.

**Q: Can I reproduce your results?**
A: Yes. Everything is open source: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge. Run the Kaggle notebook with a HuggingFace token.

**Q: What's next?**
A: Testing 12 bias probes instead of 3, adding 5 languages, and developing targeted mitigation strategies.

**Q: How do I fix bias in my LLM judge?**
A: Our mitigation benchmark tests 5 methods, including calibration, ensembling, anti-bias prompting, and few-shot calibration. The most effective method depends on which probe you're targeting.
