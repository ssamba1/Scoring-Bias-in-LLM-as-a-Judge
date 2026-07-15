# Press FAQ

## Scoring Bias in LLM-as-a-Judge Models — Journalist Q&A

---

### Q1: What is scoring bias?

**A:** Scoring bias is when an AI judge gives different scores to the same answer simply because of how the scoring format is presented — not because of the content being evaluated. For example, if you change the score labels from "1=worst, 5=best" to "1=best, 5=worst," a biased AI might not notice the switch and score incorrectly. Or if you change from numbers (1–5) to letters (A–E), the scores can shift. Or if you show a good example before asking for a score, the AI might score more leniently than if you showed a poor example.

### Q2: Why does it matter?

**A:** AI models are increasingly used to evaluate other AI systems — this is called "LLM-as-a-Judge." These evaluations power popular AI leaderboards (like Chatbot Arena), benchmark rankings (like MT-Bench), and even help train AI systems through reinforcement learning. If the judges themselves are systematically biased, then every evaluation that relies on them inherits that bias. This means AI safety assessments could be unreliable, benchmark rankings could be misleading, and AI training could inadvertently amplify biases.

### Q3: What did you find?

**A:** Three main findings: (1) Format-related bias — like confusion about scoring scale direction or label formats — **decreases** after instruction tuning (models get better at understanding formats). (2) Content-related bias — like being swayed by seeing an example answer before scoring — **increases** after instruction tuning, but only in larger models (3 billion+ parameters) trained with RLHF. (3) The specific training method used (RLHF vs. SFT+DPO vs. SFT-only) produces different bias profiles. We also found that label format bias (numbers vs. letters vs. words) is the most common problem overall.

### Q4: How is this different from prior work?

**A:** Prior research identified and measured scoring bias in frontier models (Li et al., DASFAA 2026) but explicitly left the origin question open: does this bias come from pre-training or instruction tuning? Our study is the first to answer this by comparing base models (before instruction tuning) with their instruct-tuned counterparts across multiple model families. Previous work only tested instruct-tuned models, making it impossible to determine where the bias originates.

### Q5: What are the practical implications?

**A:** Three immediate takeaways: (1) If you're using AI judges, use numeric labels (1–5) rather than letters or descriptive words — they produce the most consistent scores. (2) Always test multiple scoring formats to detect bias — don't assume a single format gives the "right" answer. (3) If you include example answers in your evaluation prompts, include both good and poor examples to calibrate the judge. For AI developers, the key implication is that bias mitigation should target the instruction-tuning stage, not the base model.

### Q6: How many models did you test?

**A:** 31 model variants in total: 9 base-instruct family pairs (18 models) for the primary comparison, plus 22 additional instruct-tuned models for breadth (some models overlap between groups). Families include Llama, Mistral, Qwen, Gemma, StableLM, DeepSeek, Microsoft Phi-4, Cohere Command-R, and others ranging from 0.5B to 671B parameters.

### Q7: Is this a problem with all AI judges?

**A:** Every model we tested showed at least some scoring bias. However, the magnitude varies enormously — from models with nearly zero bias (Qwen3-14B had a Score ID bias of 0.00) to models with very large bias (Hermes-3-70B had Score ID bias of 1.80 on a 5-point scale). So while bias is universal, it's not uniform — some models are dramatically better than others.

### Q8: What should be done about it?

**A:** Three things: First, the AI community needs standardized bias evaluation — every LLM-as-a-Judge system should report its bias profile alongside its accuracy metrics. Second, instruction-tuning methods should be designed to improve format robustness without increasing content sensitivity. Our Format Efficiency Hypothesis suggests this is achievable. Third, practitioners should use bias-aware evaluation protocols: multiple scoring formats, diverse exemplar sets, and separate reporting of format vs. content bias.

### Q9: What are the limitations?

**A:** The primary comparison (base vs. instruct) is based on 9 model families — real but modest in size. The content bias finding (increase in larger models) needs replication with more large-model families. The study uses English-only prompts and a single scoring template. We didn't test commercial API models (GPT-4, Claude) due to cost. Finally, there's no human baseline for comparison. All limitations are transparently documented in the paper.

### Q10: What's next?

**A:** The Format Efficiency Hypothesis makes five testable predictions that we're eager to see tested independently. We'd love to see replication on commercial models (GPT, Claude, Gemini) and larger open-weight models. We're also interested in developing bias mitigation strategies that specifically target the instruction-tuning stage — since that's where we now know the bias emerges. And we hope the open-source release encourages other researchers, especially students, to contribute to this important area of AI safety.
