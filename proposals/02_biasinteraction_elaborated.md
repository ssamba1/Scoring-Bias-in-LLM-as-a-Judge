# Option 2: Bias Interaction Effects — Elaborated for Your Use Case

## What You're Actually Trying to Prove

**The core question:** Everyone knows LLM judges have individual biases (position bias, verbosity bias, etc.). But in real use, these biases don't occur in isolation — a response might be BOTH verbose AND in the disfavored position. Does that make the bias twice as bad? Or do the biases cancel each other out?

**Why this matters:** If biases compound, evaluation pipelines need to test combinations, not just individual biases. If they cancel, maybe we can intentionally design inputs to counteract known biases.

## What a Day Looks Like for You

### Week 1: Generate the 8-condition evaluation set

Your job is to create 400 evaluation items, each in 8 versions:

```
Item: "Explain quantum computing to a 10-year-old"

Version 1 (baseline):       Short answer, first position, positive tone  → "It's like being in two places at once!"
Version 2:                  Short answer, first position, negative tone
Version 3:                  Short answer, second position, positive tone
...
Version 8 (worst case):     Short answer, second position, negative tone
```

**How your AI models help:** Use Claude/GPT-4 to generate the 8 versions of each item. Give it one version and say "rewrite this to be more verbose while preserving content" or "create a version with a negative/positive tone." This is the bulk of Week 1.

Both students can split the 400 items: 200 each, using AI to generate all 8 variants.

### Week 2: Run the judge API calls

You have access to premier models — here's the exact API plan:

| Model | API | Cost per 1k items | Total (3,200 items × 3 repeats) |
|-------|-----|-------------------|-------------------------------|
| Claude Sonnet 4 | Anthropic | ~$0.015 | ~$15 |
| GPT-4o | OpenAI | ~$0.01 | ~$10 |
| Gemini 2.0 Flash | Google | ~$0.0005 | ~$0.50 |
| DeepSeek V3 | DeepSeek | ~$0.001 | ~$1 |
| Llama 3 70B | Together/Groq | ~$0.001 | ~$1 |

**Total cost: ~$30 — and you already have access to these models through your premier subscriptions!**

Split: Student A runs 3 models, Student B runs 2 models. Each call returns a JSON with the score.

### Week 3: Statistical analysis

This is where your AI models really shine. Here's the analysis pipeline:

**Step 1: Main effects (replicate known biases)**
```python
# Does position bias exist in our data?
position_effect = score(first_position) - score(second_position)
verbosity_effect = score(long) - score(short)
sentiment_effect = score(positive) - score(negative)
```

**Step 2: Interaction effects (NOVEL — this is the discovery)**
```python
# Does verbosity bias change depending on position?
# If verbosity_effect is 0.3 in first position but 0.5 in second position,
# that's an interaction — they compound.
interaction_pos_verb = Δ_verbosity_at_position1 - Δ_verbosity_at_position2
```

**Step 3: Visualize**
- Heatmap: 8 conditions × scores
- Interaction plot: lines for each bias crossing or diverging
- Model comparison: which models compound biases most?

Have Claude/GPT-4 write ALL the analysis code. Just describe the statistics you want, and have the AI implement it.

## Your AI Models as Research Assistants

| Task | How Claude/GPT-4 Helps |
|------|----------------------|
| Generating 8 response variants | "Create 8 versions of this response varying length, tone, and position" |
| API calling code | "Write a script to score 3,200 items using the Anthropic API and save to CSV" |
| Statistical analysis | "Perform a 3-way ANOVA with interaction terms on this data" |
| Data visualization | "Create an interaction plot showing verbosity bias at different position conditions" |
| Paper writing | "Write a results section describing these interaction effects" |
| Interpretation | "What does a significant position×verbosity interaction mean practically?" |

## Splitting the Work (2 People)

| Person | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| **Student A** | Generate 200 items × 8 variants (using AI) | Run Claude + GPT-4o API calls | Main effects analysis, interaction ANOVA | Draft intro, related work, discussion |
| **Student B** | Generate 200 items × 8 variants (using AI) | Run Gemini + DeepSeek + Llama API calls | Interaction plots, model comparison | Draft results, revise paper, create figures |

## What the Final Deliverable Looks Like

**A 6-8 page paper with:**
1. **Abstract** — "We show that LLM judge biases don't operate independently — position bias and verbosity bias compound, making the worst case 2× worse than expected..."
2. **Introduction** — LLM judges have known biases, but they've only been studied in isolation
3. **Methodology** — Full-factorial 2×2×2 design, 5 judge models, 400 items
4. **Results** — Key finding: [e.g., verbosity and position biases compound additively, but sentiment bias cancels with verbosity]
5. **Discussion** — Practical implications for evaluation pipeline design
6. **Limitations** — Only tested 3 bias types, pairwise scoring, English-only

**Target venues:**
- ICML NextGen / NeurIPS High School Projects
- arXiv preprint
- ISEF (Systems Software category)

## What Makes This Strong for ISEF

1. **Beautiful experimental design** — Full-factorial is textbook good science
2. **Practical implications** — "How to design better AI evaluation" is timely
3. **Novel finding** — Nobody has measured this before
4. **Statistical sophistication** — ANOVA, interaction effects — impresses judges
5. **Cross-platform** — Tests 5 different AI models from different companies

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| No interactions found (all biases are purely additive) | Medium | Even this is a finding — "biases in LLM judges are independent" would be surprising |
| API rate limits | Low | Spread calls across the week, use multiple API keys |
| High variance in scores | Medium | Run 3 repeats per condition, use median score |
| Someone publishes bias interactions before you | Extremely low | Multiple independent searches confirmed zero papers |
