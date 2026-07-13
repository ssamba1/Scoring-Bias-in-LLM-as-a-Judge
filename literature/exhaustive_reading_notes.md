# Exhaustive Paper Reading Notes — Full Text Extraction

## Li et al. 2025: "Evaluating Scoring Bias in LLM-as-a-Judge"
**arXiv:2506.22316v4 · DASFAA 2026 · Read in full (78K chars)**

### Exact Numbers
| Metric | Value |
|--------|-------|
| BiGGen Bench items | 2,780 responses for 695 instances |
| FLASK items | 2,001 responses for 200 prompts |
| MT Bench items | 320 responses |
| Vicuna Bench items | 320 responses |
| Models tested | GPT-4o, DeepSeek-V3-671B, Qwen3-32B, Qwen3-8B, Mistral-Small-24B-Instruct-2501 |
| Temperature | 0 (deterministic) |
| Reference score used | 5 (for Ref-5 condition) |

### Flip Rates by Model (Table 3)

**GPT-4o:**
| Perturbation | BiGGen FR | FLASK FR | MT Bench FR | Vicuna FR |
|---|---|---|---|---|
| Descending rubric | 23.63% | 23.44% | 23.13% | 20.00% |
| Random rubric | 22.55% | 24.94% | 28.44% | 19.38% |
| Letter grades | 18.17% | 18.24% | 19.69% | 19.38% |
| Roman numerals | 16.51% | 15.94% | 23.13% | 15.63% |
| Ref-5 | **45.54%** | **45.58%** | — | — |

**DeepSeek-V3-671B:**
| Descending rubric | 24.21% | 21.89% | 25.00% | 27.50% |
| Random rubric | 30.86% | 32.83% | 32.19% | 39.06% |
| Letter grades | 19.86% | 18.14% | 17.81% | 26.25% |
| Roman numerals | 19.53% | 17.89% | 20.00% | 25.00% |
| Ref-5 | 38.99% | 45.13% | — | — |

**Qwen3-8B (smallest model, most biased):**
| Descending rubric | 46.22% | 32.23% | 40.31% | 44.06% |
| Random rubric | 34.93% | 36.83% | 35.31% | 34.38% |
| Letter grades | 30.54% | 28.39% | 36.88% | 28.44% |
| Roman numerals | 32.99% | 34.38% | 40.31% | 30.94% |
| Ref-5 | 36.48% | 40.53% | — | — |

### Key Findings
1. "Even the most advanced LLMs suffer from substantial scoring biases" (GPT-4o exhibits 45% flip rate)
2. Ref-5 causes the LARGEST effect (35-48% across models)
3. Smaller models (Qwen3-8B) show MORE scoring bias
4. Model size negatively correlates with bias susceptibility
5. "The underlying causes of scoring bias remain to be validated" (Section 5 — our gap)

## Yang et al. 2025: "Any Large Language Model Can Be a Reliable Judge"
**arXiv:2505.17100v2 · NeurIPS 2025 · Read in full (33K chars)**

### Exact Numbers
| Bias Type | % Affected | Base Dataset |
|-----------|-----------|--------------|
| Verbosity | **31.3%** | GSM8K |
| Sentiment | **15.0%** | ScienceQA |
| Position | **12.9%** | Arena |
| Bandwagon | **12.5%** | Arena |

### RBD Performance
| Metric | Improvement |
|--------|-------------|
| RBD-8B accuracy improvement | **18.5%** |
| RBD-8B consistency improvement | **10.9%** |
| vs prompting baselines | +12.8% |
| vs fine-tuned judges | +17.2% |
| RBD training size | 1.67K reasoning traces |
| Test set | 0.5K examples |
| RBD models trained | 1.5B, 7B, 8B, 14B |

### Models Evaluated
8 evaluators: GPT-4o, GPT-4o-mini, Claude-3.5-Sonnet, Claude-3.5-Haiku, DeepSeek-V3, Llama 3.1 (8B, 70B, 405B)

### Key Insights
1. "Even state-of-the-art models GPT-4o and Claude-3.5-Sonnet consistently exhibit detectable biases"
2. Verbosity bias is the LARGEST individual bias
3. Claude prefers concise responses (reverse direction!)
4. RBD generalizes across biases and domains

## Pan et al. 2025: "User-Assistant Bias in LLMs"
**arXiv:2508.15815v3 · ACL 2026 Findings · Read in full**

### Key Findings
1. Tested 52 frontier models — largest comparison
2. "Most instruction-tuned models exhibit strong user bias"
3. "Base and reasoning models are close to neutral"
4. Human-preference alignment amplifies user bias
5. Reasoning fine-tuning REDUCES user bias
6. DPO can bidirectionally control the bias

### Relevance to Our Work
- Validates the base-vs-instruct comparison methodology
- Same finding: instruction tuning introduces bias
- Different bias type (user-assistant vs scoring)
- Our work extends this to scoring bias for the first time

## Shi et al. 2025: "Judging the Judges: A Systematic Study of Position Bias"
**arXiv:2406.07791v9 · AACL-IJCNLP 2025**

### Key Numbers
- 15 judges × ~150,000 evaluation instances
- 22 tasks, 40 solution-generating models
- 3 metrics: repetition stability (RS), position consistency (PC), preference fairness (PF)
- Judge-Level, Candidate-Level, and Task-Level factors
- Position bias NOT random — varies significantly across judges/tasks
- Weakly influenced by prompt length
- Strongly affected by quality gap between solutions
