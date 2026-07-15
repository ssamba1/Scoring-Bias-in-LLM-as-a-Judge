# Option 1: Root Cause of Scoring Bias  Elaborated for Your Use Case

## What You're Actually Trying to Prove

**The core question:** When an LLM judge changes its score based on trivial things like rubric order or score labels  does that bug come from the model's pre-training (its "raw knowledge") or from instruction tuning (learning to follow formats)?

**Why this matters:** If scoring bias comes from pre-training, it's practically baked in and hard to fix. If it comes from instruction tuning, we can fix it by changing how we train judges. This distinction is valuable to every company using LLM-as-a-Judge in production.

## What a Day Looks Like for You

### Week 1-2: Setup and pipeline (parallel work)

**Student 1  Dataset & Infrastructure**
- Download Li et al.'s public dataset from github.com/KMdsy/scoring_bias/ (400 evaluation items already made)
- Set up inference pipeline with HuggingFace Transformers
- You have premier AI models  use Claude/GPT-4 to write the evaluation scripts and debug them
- Set up 3 models: `meta-llama/Meta-Llama-3-8B`, `google/gemma-2-2b`, `mistralai/Mistral-7B-v0.3` (base versions)

**Student 2  Prompt Templates**
- Use your AI access (Claude/GPT-4) to generate the 3 scoring bias prompt templates:
  1. **Rubric order:** Same rubric, criteria order swapped (A→B→C vs C→B→A)
  2. **Score ID:** Same rubric, labels as "1-5" vs "A-E" vs "I-V"
  3. **Reference answer:** Same rubric, reference answer scored as "5" vs "3"
- Have Claude/GPT-4 help design the exact prompt wording (they're great at this)
- Validate: run the prompts through a frontier model to check they're working

### Week 2-3: Data collection (can parallelize)

Each student runs half the inferences:
```
2 students × 
2 model versions (base + instruct) × 
3 model families (Llama, Mistral, Gemma) × 
3 bias types × 
400 items × 
3 repeats = 21,600 total inferences
```
Split: ~10,800 inferences each. At ~1-2 seconds per inference on Colba T4, that's ~3-6 hours per student.

### Week 3-4: Analysis

**Together:**
- For each bias type, compute Δ_score between rubric variants
- Compare: is Δ_score larger in base models or instruct models?
- Plot: bar charts per model family × per bias type
- Use Claude/GPT-4 to help write the analysis code and interpret results

## Your AI Models as Research Assistants

| Task | How Claude/GPT-4 Helps |
|------|----------------------|
| Writing inference code | "Write a Python script that loads Llama 3 8B and generates scores for 400 items with 3 rubric variants" |
| Prompt engineering | "Design 3 rubric variants that test order bias while keeping content identical" |
| Statistical analysis | "Run a paired t-test comparing base vs instruct model scores" |
| Literature review | "Summarize the Li et al. 2025 paper's methodology" |
| Paper writing | "Draft the methods section for our experiment" |
| Debugging | "Why is my HuggingFace pipeline giving different logits for the same input?" |

## Splitting the Work (2 People)

| Person | Week 1-2 | Week 3-4 | Week 5-6 | Week 7-8 |
|--------|----------|----------|----------|----------|
| **Student A** | Set up inference pipeline, run base models | Analyze Llama & Mistral results | Draft intro, related work, methods | Write results, make plots |
| **Student B** | Design prompt templates, run instruct models | Analyze Gemma results, cross-model comparison | Draft results, discussion | Final paper revisions, abstract |

## What the Final Deliverable Looks Like

**A 6-8 page paper with:**
1. **Abstract**  "We show that LLM judge scoring bias originates from instruction tuning, not pre-training..."
2. **Introduction**  LLM-as-a-Judge is widely used but exhibits unexplained scoring biases
3. **Methodology**  Model selection, perturbation design, statistical tests
4. **Results**  3 plots (one per bias type) showing base vs instruct Δ_score
5. **Discussion**  Implications for training bias-robust judges
6. **Related Work & References**

**Target venues:** 
- ICML NextGen / NeurIPS High School Projects track (if they run it again)
- arXiv preprint + blog post
- Local/regional science fairs → ISEF

## What Makes This Strong for ISEF

1. **Hypothesis-driven**  You're testing a specific causal theory
2. **Controlled experiment**  Compare base vs instruct (clear independent variable)
3. **Societal impact**  "Understanding where AI bias comes from" is compelling
4. **Rigor**  3 model families, 3 bias types, statistical tests
5. **Story**  "We discovered that teaching AI to follow instructions also makes it biased"

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Results are inconclusive (both models show same bias) | Low (Pan et al. found clear differences for user-assistant bias) | Still publishable as "scoring bias is equally present in all training stages" |
| GPU access issues | Medium | Use Together AI / Groq inference APIs instead (~$30, no GPU needed) |
| Someone publishes before you | Very low (Pan et al. proved the methodology, nobody has applied it) | Submit to arXiv as soon as results are ready |
