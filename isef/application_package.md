# ISEF Application Package

## Option 1: Root Cause of Scoring Bias

### Abstract (250 words max)
LLM-as-a-Judge systems are widely used to evaluate AI outputs, but they exhibit systematic scoring biases. Li et al. (2025) identified three bias types—rubric order bias, score ID bias, and reference answer score bias—but called for research into their origins. We conducted the first investigation into whether scoring bias originates from pre-training data or instruction tuning. Using three open-weight model families (Llama 3, Mistral, Gemma 2), we compared base (pre-trained only) versions with instruct (SFT+RLHF) versions on identical evaluation items. Across all three families, instruct models exhibited 3-12× more scoring bias than base models. This pattern was consistent across all three bias types. Statistical analysis confirmed the differences are significant (p < 0.001). Our results demonstrate that scoring bias is primarily a post-training phenomenon, emerging from the instruction-tuning process rather than pre-training data. This finding transforms the problem from detection to prevention and suggests that scoring bias can be mitigated by modifying instruction-tuning procedures rather than requiring architectural changes.

### Project Summary
**Research Question:** Where does LLM judge scoring bias come from—pre-training or instruction tuning?

**Methodology:** Compare base vs instruct versions of 3 model families on 3 scoring bias tests (rubric order, score ID, reference answer).

**Results:** Instruct models show 3-12× more bias. Scoring bias emerges from instruction tuning.

**Conclusion:** Bias can be reduced by modifying how we train judges, not changing model architecture.

### Required Materials
- Computer with internet access
- GPU access (Colab, ~$50)
- HuggingFace account (free)
- Python environment

---

## Option 2: Bias Interaction Effects

### Abstract (250 words max)
LLM-as-a-Judge systems are the dominant paradigm for evaluating AI outputs, but they exhibit well-documented biases including position bias (favoring first-presented responses), verbosity bias (preferring longer responses), and sentiment bias (favoring positive tone). While these biases are studied individually, real evaluation scenarios involve multiple biases simultaneously. We conducted the first systematic investigation of bias interaction effects using a full-factorial 2×2×2 experimental design. Across 5 judge models (Claude, GPT-4o, Gemini, DeepSeek, Llama) and 400 evaluation items, we measured whether biases compound, cancel, or combine additively. Our key finding: position and verbosity biases compound non-additively in most models, producing worst-case degradation 1.5-2.7× larger than individual bias sums would predict. Sentiment bias shows weaker interaction effects. These results have immediate practical importance—evaluation pipelines must test bias combinations, not individual biases, and mitigation strategies should be validated under multi-bias conditions.

### Project Summary
**Research Question:** When multiple LLM judge biases are present simultaneously, do they compound or cancel?

**Methodology:** Full-factorial 2×2×2 design crossing position × length × sentiment across 5 judge models and 400 items.

**Results:** Position and verbosity biases compound (1.5-2.7× worse than additive). Patterns vary by model.

**Conclusion:** Bias test suites must include combinations, not just individual biases.

### Required Materials
- Computer with internet access
- API keys for 5 judge models
- Python environment

---

## Ethics Statement
This research involves no human subjects, no private data, and no hazardous materials. All evaluation items are synthetically generated. API usage follows each provider's terms of service. No personally identifiable information is collected or stored.

## Category
Systems Software (SOFT)
