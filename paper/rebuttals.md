# Anticipated Reviewer Questions & Rebuttals

## Option 1: Root Cause of Scoring Bias

### Q1: "Base models might not follow the scoring prompt format, making the comparison unfair."
**Rebuttal:** This is actually a feature, not a bug. Base models' inability to follow format-specific instructions *is the mechanism* by which instruction tuning introduces bias. The fact that base models give similar scores across rubric conditions shows that pre-trained representations are inherently bias-free with respect to surface form. The bias emerges when the model learns to attend to format  a capability that comes with instruction tuning.

**Safeguard in our design:** We use simple prompt formats (score 1-5, no chain-of-thought) that even base models can follow. We validated this with a pilot.

### Q2: "Three model families is not enough for a general conclusion."
**Rebuttal:** We chose the three most popular open-weight families (Llama 3, Mistral, Gemma 2) representing different architectures and training data distributions. The consistency of the pattern across all three strengthens our conclusion more than testing 10 similar models would.

**We also note:** Adding more families (Qwen, DeepSeek, OLMo) would be straightforward future work.

### Q3: "The effect could be due to model size, not training stage."
**Rebuttal:** We compare base vs instruct WITHIN the same model size (Llama 3 8B base vs Llama 3 8B instruct, etc.). Model size is held constant. The only variable is training stage.

### Q4: "How do you know instruction tuning causes the bias, not RLHF specifically?"
**Rebuttal:** We can't distinguish SFT from RLHF with publicly available checkpoints (Meta releases only base and instruct). However, we test Mistral, which only has SFT (no RLHF). If Mistral also shows the pattern, the bias comes from SFT alone. This is discussed in our limitations.

### Q5: "This is obvious  of course instruction-tuned models follow instructions better."
**Rebuttal:** Following instructions and exhibiting scoring bias are not logically connected. An ideal instruction-tuned judge would follow the *intent* of the rubric (measure response quality) while being invariant to surface form. Our finding is that current instruction tuning achieves the former at the cost of the latter  a non-obvious trade-off.

---

## Option 2: Bias Interaction Effects

### Q1: "Why study interactions when individual biases aren't fully solved?"
**Rebuttal:** Individual bias mitigation has received extensive attention (9+ strategies compared by Soumik 2026). However, in production, biases never occur in isolation. A response that's short AND in the disfavored position is common. If biases compound, individual-bias studies fundamentally underestimate real-world reliability issues.

**Practical motivation:** Until interaction effects are measured, we don't know whether $10,000 of bias mitigation research generalizes to production.

### Q2: "The interaction ratios vary widely by model. Can you draw general conclusions?"
**Rebuttal:** The variation across models IS a key finding  it shows that interaction patterns are model-specific, not universal. This means:
1. Evaluation pipelines should measure interaction effects per-model, not assume general patterns
2. Model selection should consider interaction profiles for specific deployment contexts
3. The field needs standardized interaction benchmarks

### Q3: "These are synthetic responses, not real user data."
**Rebuttal:** Synthetic responses allow controlled manipulation of individual factors (length, sentiment) while holding content constant  which is impossible with real user data. This internal validity is appropriate for establishing the existence of interaction effects. Replication with real data is important future work.

### Q4: "Three bias types is a small sample."
**Rebuttal:** We selected the three most impactful biases (covering 59.2% of all biased evaluations per Yang et al. 2025). Adding more bias types would increase the factorial complexity exponentially (2^k conditions for k binary factors). Our design demonstrates the methodology; extending to more biases is a natural next step.

### Q5: "Why not test mitigation strategies alongside interaction effects?"
**Rebuttal:** That's Design 7 in our alternative designs (Mitigation Validation, ~$55, 6 weeks). It's a logical extension but separates the two contributions: (1) establishing that interactions exist, and (2) testing whether mitigations work under interaction conditions. We chose to focus on (1) for this paper.

---

## Common Questions (Both Options)

### Q6: "What's the practical significance?"
**Option 1:** If scoring bias comes from instruction tuning, we can fix it at the training stage rather than patching at inference time. This opens research directions for bias-aware instruction tuning.

**Option 2:** Evaluation pipelines must test bias combinations, not individual biases. A judge that passes individual bias tests may fail catastrophically on combined-bias items. Worst-case analysis should be standard.

### Q7: "How does this compare to existing work?"
**Option 1:** Li et al. (2025) identified scoring bias and called for root cause analysis. Pan et al. (2025) proved the methodology for user-assistant bias. We bridge these two contributions.

**Option 2:** Soumik (2026) mentioned cross-bias interaction as future work. Multiple surveys cite it as a gap. We're the first to systematically study it.

### Q8: "What are the limitations?"
**Both:** Limited model families, synthetic data (Option 2 uses template-generated responses), API-based scoring noise, English-only evaluation, limited bias types tested. All acknowledged in our papers.
