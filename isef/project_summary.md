# Project Summary — Scoring Bias in LLM-as-a-Judge

## For ISEF Judges (Non-Technical Audience)

---

### Research Question

**Where does scoring bias in AI judges come from — is it learned during training, or is it there from the start?**

AI models like ChatGPT, Claude, and Gemini are now used to evaluate other AI systems — a process called "LLM-as-a-Judge." But these AI judges have known biases: they give different scores depending on how you format the rubric, what labels you use (numbers vs. letters), and whether you show an example answer first. Prior research identified over 35 types of bias but never answered the most basic question: are these biases baked into the model from the very beginning, or do they emerge when the model is fine-tuned to follow instructions?

---

### Methodology

I compared **9 pairs of AI models** where each pair has a "base" version (raw pre-trained model) and an "instruct" version (same model, fine-tuned to follow instructions). Across 9 model families — including Llama, Mistral, Qwen, Gemma, and StableLM — I tested each model's scoring behavior using three experiments:

1. **Rubric Order Test:** I reversed the scoring scale (1=best instead of 1=worst) to see if the model notices.
2. **Score ID Test:** I changed score labels from numbers (1–5) to letters (A–E) or descriptive words (Poor–Excellent).
3. **Reference Answer Test:** I showed a good or poor example answer before asking the model to score.

In total, I collected **54,000 judgments** across **31 model variants**, running experiments on Kaggle GPUs and through the OpenRouter API.

---

### Results

The results reveal a clear pattern:

- **Format-related bias decreases after instruction tuning.** Instruct models are better at understanding scoring formats — rubric order bias dropped by 44% and score ID bias dropped by 77% on average.
- **Content-related bias increases after instruction tuning in larger models.** When shown a poor example answer before scoring, larger instruction-tuned models (3 billion+ parameters) became more biased, with the worst case showing a 1.58-point shift on a 5-point scale.
- **Score ID bias (label format)** is the most common problem overall, affecting models by an average of 0.68 points on a 5-point scale.
- **One family (Mistral 7B), trained with a different method called SFT+DPO, showed a different pattern**, suggesting the training method matters.

---

### Conclusions

Scoring bias is **not** inherent to pre-trained language models — it emerges during instruction tuning. This is good news because it means we can fix the problem by improving how we fine-tune models, rather than redesigning them from scratch. However, the fix must be careful: improving format understanding can inadvertently make models more sensitive to content-based priming.

---

### Real-World Applications

- **AI Safety:** If AI judges are biased, safety evaluations of new AI systems may be unreliable.
- **Benchmark Rankings:** Popular AI leaderboards may contain systematic scoring errors.
- **Practical Guidance:** For the most reliable scores, use numeric labels (not letters or words) and always test multiple scoring formats.
- **Model Development:** Future instruction tuning should include diverse rubric formats without amplifying content sensitivity.

All code and data are open-source at **github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge**.
