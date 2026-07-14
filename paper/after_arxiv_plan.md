# After arXiv: Path to S-Tier (NeurIPS/ACL Level)

## Phase 1: v2.0 — Strengthen Core (1-2 weeks, $0-5)

### 1. Fix the 4-bit loading issue → Qwen2.5-7B + Mistral-7B (30 min)
Run the T4 script with `!pip install -q --upgrade transformers bitsandbytes accelerate` first. Gets you 2 more families (Qwen2.5-7B, Mistral-7B). N=9 → N=11 families.

### 2. Human baseline (1 hour, free)
3 friends rate the 50 items (from `data/human_baseline_sheet.md`). Each takes 15 min.
- Tells you: do humans show the same bias patterns?
- Tells you: what's the "correct" score for each item?
- Lets you compute: model vs human agreement, bias magnitude vs human

### 3. Attention analysis at 3B (30 min on Kaggle)
Run `attention_analysis_kaggle.py` on Llama-3.2-3B (shows content ↑). If κ > 1.0 at 3B but not at 0.5B → proves IIAR has a scale threshold. This is the key experiment.

### 4. Domain analysis (30 min)
Already have the code + per-item data from the T4 run. Run `domain_analysis.py` — tells you if science items show different bias than humanities.

**After Phase 1: ~8.0-8.5/10. Paper has N=11, human baseline, attention evidence, per-domain breakdown.**

## Phase 2: v3.0 — The NeurIPS Push (1-2 months, $20-100)

### 5. More families via A100 (free on Colab)
Run 7B+ models on Colab's free A100 (90 min/week):
- Llama-3.1-8B + Instruct (8B, shows differential effect)
- Qwen2.5-14B + Instruct (14B, the bigger Qwen)
- DeepSeek-7B + Instruct
- Gemma-2-9B + Instruct
Target: N=15+ families.

### 6. Bayesian analysis (1 day)
Instead of paired t-tests (which need N=12+), use Bayesian hierarchical model that handles N=9-15 properly. This is what NeurIPS papers use.

### 7. Write the NeurIPS version (1 week)
- Add related work section for ICLR 2026, ICML 2026 papers
- Add formal problem definition
- Add experimental diagram figure
- Professional figures (not matplotlib defaults)
- Have a senior researcher read and critique

**After Phase 2: ~8.5-9.0/10. Paper has N=15+, Bayesian stats, attention evidence, human baseline, professional figures.**

## Phase 3: S-Tier (3-6 months, variable)

### 8. Submit to a venue
| Venue | Deadline ~ | Acceptance | Fit |
|-------|-----------|------------|-----|
| **ACL SRW** (Student Research Workshop) | Feb-April | ~35% | ✅ Great fit for solo HS |
| **NeurIPS HS Track** | May-June | ~25% | ✅ Good fit |
| **ACL main** | Feb | ~20% | ⚠️ Need more data |
| **EMNLP** | May | ~20% | ⚠️ Strong paper needed |

### 9. Release dataset on HuggingFace (free)
Upload the per-item scores as `ssamba1/scoring-bias-llm-as-a-judge`. This drives citations and community use.

### 10. Write a blog post / tweet thread
- Thread summarizing the finding (8 tweets)
- Links to arXiv, HuggingFace, GitHub
- This drives early citations

## Phase 4: True S-Tier (1-2 years)

| Milestone | What it looks like |
|-----------|-------------------|
| 50+ citations | People are building on your work |
| Used as benchmark | Other papers cite your bias measurement |
| Follow-up paper | "Scoring Bias in GPT-4, Claude, Gemini"
| Invited talk | Someone asks you to present |
| Industry adoption | Bias measurement used in production |

---

## Summary: What matters most for S-Tier

| Move | Impact | Time | Cost |
|------|--------|------|------|
| **Publish on arXiv** (done) | Priority + timestamp | ✅ Done | $0 |
| **Human baseline** | Absolute magnitude claims | 1 hr | $0 |
| **Attention at 3B** | IIAR test at scale | 30 min | $0 |
| **Bayesian analysis** | Proper statistics | 1 day | $0 |
| **Submit to ACL SRW** | Venue acceptance | 1 week prep | $0 |
| **Time + citations** | Community recognition | 1-3 years | $0 |

**The biggest ROI for your time right now:** human baseline (1 hr) + attention at 3B (30 min). Those two experiments double the paper's evidence depth for 90 minutes of work.
