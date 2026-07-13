# Paper Reading Notes — Extracted from Full-Text Reading

## Paper 1: Li et al. 2025 — Full Methodology (Extended)

### Exact Metrics
1. **Flip Rate (FP):** % of scores that change when rubric is perturbed
2. **Mean Absolute Deviation (MAD):** Average |score_original - score_perturbed|
3. **Spearman's ρ and Pearson's r:** Correlation with golden (human/advanced LLM) scores
4. **Scoring Tendency:** Distribution of scores across the 1-5 scale

### Exact Prompt Template
```
Task Description...
### Reference Answer (Score 5): {reference}
### Score Rubrics: [{criteria}]
Score 1: {desc1} Score 2: {desc2} ... Score 5: {desc5}
### The instruction to evaluate: {instruction}
### Response to evaluate: {response}
### Feedback:
```

### Perturbations (Exact)
1. **Rubric order:** Ascending-Numeric (1→5), Descending-Numeric (5→1), Random-Numeric
2. **Score ID:** Arabic numerals {1,2,3,4,5}, Letter-Grades {E,D,C,B,A}, Roman-Numerals {i,ii,iii,iv,v}
3. **Reference answer:** Ref-5 (reference scored 5), Ref-3 (reference scored 3), No reference

### Models tested (ALL instruct/chat — NO base models):
- GPT-4o (closed-source, large)
- DeepSeek-V3-671B (open-weight, large)
- Qwen3-32B, Qwen3-8B (open-weight, mid/small)
- Mistral-Small-24B-Instruct-2501 (open-weight, mid)

### Key numeric results:
- Descending rubric order causes 20-46% of scores to flip (FP)
- Letter-Grades and Roman-Numerals cause 15-30% flip rates
- Ref-5 causes 35-48% flip rates — the largest effect
- Smaller models (Qwen3-8B) show MORE scoring bias than larger ones
- **Implication:** Model size affects bias susceptibility

### Key Methodological Details
- **Models tested:** GPT-4o, DeepSeek-V3-671B, Qwen3-32B, Qwen3-8B, Mistral-Small-24B-Instruct-2501
- **All models are INSTRUCT/CHAT versions** — no base models tested
- **Dataset:** 4 benchmarks (MT-Bench n=80, Vicuna Bench n=80, FLASK n=100, BigGen Bench n=100)
- **Metrics:** Stability (CON, SC), Accuracy (TA, BS), Scoring Tendency (MS, VarS)
- **3 bias types defined:**
  1. Rubric order bias: criteria order A→B→C vs C→B→A
  2. Score ID bias: numeric "1-5" vs letter "A-E" vs Roman "I-V"
  3. Reference answer score bias: reference scored "5" vs "3"
- **Key finding (Fig 5):** Score rubric order bias and score ID bias significantly impact scoring tendencies. Models show systematic shifts.
- **Key finding (Fig 6):** Reference answer score bias exerts substantial impact on score distribution.
- **Key finding (Table 2):** Even advanced LLMs suffer from all three biases.
- **Authors explicitly state:** "the underlying causes of scoring bias remain to be validated" (§5)
- **Authors explicitly state:** "there are no dedicated methods for addressing scoring bias" (§5)
- **Recommendations:** descending rubric order, letter/Roman numeral IDs, full-mark reference answers

### Key Quotes for Paper
> *"the underlying causes of scoring bias remain to be validated. Approaches such as training data analysis and information flow observation may help identify the reasons for scoring bias, whether it originates from within the model or from external factors."*

> *"There are no dedicated methods for addressing scoring bias, intuitive and straightforward approaches, such as scoring multiple times followed by majority voting or averaging the scores, require empirical validation for their effectiveness"*

---

## Paper 2: Pan et al. 2025 — "User-Assistant Bias in LLMs"
**arXiv:2508.15815 · ACL 2026 Findings · ~30 citations**

### Key Methodological Details
- **Models tested:** 52 frontier models (26 commercial + 26 open-weight)
- **Key comparison:** base models vs instruction-tuned models vs reasoning models
- **Dataset:** UserAssist benchmark (8k multi-turn conversations)
- **Key findings:**
  1. "instruction-tuned models exhibit strong user bias, whereas base and reasoning models are close to neutral"
  2. "human-preference alignment amplifies user bias, while reasoning fine-tuning reduces it"
  3. User-assistant bias can be bidirectionally controlled via DPO
- **Methodology:** Controlled fine-tuning experiments isolate which post-training recipes drive bias
- **This is the template for our Option 1 experiment**

### Key Quote
> *"Most of the instruction-tuned models exhibit strong user bias, whereas base and reasoning models are close to neutral. Using controlled fine-tuning experiments, we isolate which post-training recipes drive the observed user-assistant bias."*

---

## Paper 3: Gu et al. 2024 — "A Survey on LLM-as-a-Judge"
**arXiv:2411.15594 · Nov 2024 · cited 1661+**

### Structure
- 6 sections: Functionality, Methodology, Applications, Meta-evaluation, Limitations
- Proposes reliability taxonomy with 3 dimensions: consistency, bias mitigation, scenario adaptation
- **Key gap identified:** No consensus benchmark for judge reliability
- **Key gap identified:** Cross-domain generalization of judges is understudied
- **Key gap identified:** Bias interaction effects are not addressed

---

## Paper 4: Zheng et al. 2023 — "Judging LLM-as-a-Judge with MT-Bench"
**NeurIPS 2023 · cited 2000+**

### Key Details
- Introduced MT-Bench: 80 multi-turn questions across 8 categories
- First to document position bias (LLMs prefer first answer)
- First to document self-enhancement bias (LLMs prefer own outputs)
- Found GPT-4 agrees with humans 80% of the time
- Proposed swap-and-average mitigation for position bias
- **Key quote:** "LLMs exhibit substantial bias in evaluation, favoring their own outputs and responses in certain positions"

---

## Paper 6: Soumik 2026 — "Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies"
**arXiv:2604.23178 · TMLR 2026 · single author**

### Key Details
- **Models:** 5 judges (Google, Anthropic, OpenAI, Meta) × 4 provider families
- **Benchmarks:** MT-Bench n=400, LLMBar n=200, custom n=375
- **9 debiasing strategies** systematically compared
- **Key findings:**
  1. Style bias is dominant (0.10-0.76) — far exceeds position bias (≤0.04)
  2. Verbosity bias is heterogeneous: Pro/Flash/Llama prefer longer (+0.24 to +0.44), Claude prefers concise (-0.12), GPT-4o neutral (-0.04)
  3. Gemini 2.5 Flash + Combined Budget = 71.0% agreement (kappa=0.549) at ~$0.001/eval
  4. Debiasing helps: Claude +11.5pp, Flash +7.5pp
- **Key gap:** "Cross-bias interaction analysis" mentioned as future work — does NOT study bias interactions
- **Does NOT cover:** scoring bias (rubric order, score ID, reference answer), bias interactions
- **Key quote:** "Style bias is the dominant bias... far exceeding position bias, yet is rarely studied"

## Paper 7: Xu et al. 2026 — "Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge"
**arXiv:2602.02219 · Feb 2026**

### Key Details
- Shows rubric-based evaluation has position bias in score OPTIONS (where "1" vs "5" appears)
- "When a prompt scores several criteria simultaneously, the ordering of the criteria itself shifts the resulting scores"
- Proposes random permutations of rubric options as mitigation
- **Key distinction:** Studies position bias in score OPTIONS, NOT rubric ORDER bias (criteria ordering)
- Mitigation only helps models with strong bias
- **Relevance to our work:** Confirms that rubric structure matters, but does NOT address rubric order bias as defined by Li et al.

## Paper 9: Feuer et al. 2026 — "Towards Provably Unbiased LLM Judges via Bias-Bounded Evaluation"
**arXiv:2603.05485 · Mar 2026**

### Key Details
- Proposes average bias-boundedness (A-BB), an algorithmic framework
- Achieves (tau=0.5, delta=0.01) bias-bounded guarantees
- Retains 61-99% correlation with original rankings
- Evaluated on Arena-Hard-Auto with 4 LLM judges
- **Key distinction:** Theoretical framework for bias guarantees, NOT specific to scoring bias
- **Relevance:** General approach, doesn't address our specific gap

## Paper 10: Dev et al. 2026 — "Judge Reliability Harness" (RAND Corporation)
**arXiv:2603.05399 · ICLR 2026 Workshop · Mar 2026**

### Key Details
- Open-source library for stress-testing LLM judge reliability
- Evaluated 4 judges across 4 benchmarks (safety, persuasion, misuse, agentic)
- **Key finding:** "No judge that we evaluated is uniformly reliable across benchmarks"
- Simple formatting changes disrupt consistency
- **Key quote:** "No judge we evaluated is uniformly reliable across benchmarks"
- **Relevance:** Confirms the unreliability problem we're addressing

## Paper 11: Doğruöz et al. 2026 — "LLMs-as-a-Judge in Multilingual Settings"
**arXiv:2607.02235 · Jul 2026**

### Key Details
- Out of 650 papers mentioning LLM-as-a-judge, only 33 focus on multilingual
- "Inconsistent evaluation outcomes, a tendency to overtrust LLM judgments in multilingual settings"
- Widespread reliance on a single judge model per study
- **Relevance:** Documents cross-cultural bias gap — underexplored area

## Paper 12: Yang et al. 2025 — "Any Large Language Model Can Be a Reliable Judge"
**NeurIPS 2025**

### Key Details
- Verbosity bias: 31.3% of examples affected (largest effect)
- Sentiment bias: 15.0% of examples affected
- Position bias: 12.9% of examples affected
- **Key numbers:** Used in our synthetic data parameterization
- **Relevance:** Provides the effect sizes we use for our experiment design

### Key Details
- Three-stage framework: locked task specification → structured execution → post-hoc calibration
- Three failure modes identified: rubric execution drift, unverifiable score attribution, human-scale misalignment
- "Improves stability under semantically equivalent rubric perturbations"
- **Key distinction:** Proposes a general framework for rubric reliability, NOT a dedicated study of scoring bias
- The rubric stability improvement is a side effect of the locked-rubric approach, not a dedicated mitigation for the biases Li et al. identified
- **Relevance:** Partially adjacent but does NOT address our gap
