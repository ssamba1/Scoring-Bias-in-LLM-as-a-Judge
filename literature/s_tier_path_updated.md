# S-Tier: Current Status & Path Forward

## Today's Score: ~7/10 (solid arXiv, competitive ACL SRW)
## Target: 10/10 (NeurIPS/ACL main, highly cited)

---

## Dimension Scores

| Dimension | 2 weeks ago | Today | S-Tier Target |
|-----------|-------------|-------|---------------|
| **Data** | 3 families | **8 families** | 12+ families |
| **Format bias finding** | N=3 | **N=8, 7/8 replicate** | N=12+, p<0.01 |
| **Content bias finding** | N=3, +35% | **Scale-dependent** | Mechanistically explained |
| **Theory** | Speculation | **Tested (negative)** | Supported at 7B+ |
| **Reproducibility** | Partial | **Docker + CI + DOI** | Binder + HF dataset |
| **Writing** | Functional | **Honest, structured** | Professionally polished |

---

## What S-Tier Actually Requires

### 1. Data: 12+ families (2-3 weeks, $20-50 on OpenRouter/HF)
- Run Qwen2.5-7B, Mistral-7B, Llama-3.1-8B on T4 with 4-bit (already downloaded, just need working `bitsandbytes`)
- Run Gemma-2-9B on Colab A100 (free 90 min/week)
- Target: 12+ families with base+instruct pairs

### 2. Theory: Attention analysis at scale (1 week, free on T4/A100)
- Run attention analysis on Llama-3.2-3B (shows content ↑ effect)
- If κ > 1.0 at 3B but not at 0.5B → proves scale threshold for IIAR
- If still negative → IIAR is wrong, propose alternative

### 3. Depth: Domain + Human + IRT (1 week)
- **Human baseline**: 3 raters on 50 items = 1 hour of friend time
- **Domain analysis**: Already have the framework, need per-item data
- **IRT analysis**: Code already written

### 4. Polishing (1 day)
- Grammarly pass
- Graphical abstract figure
- Pipeline diagram
- Professional acknowledgments

### 5. Time-dependent S-Tier metrics
| Metric | S-Tier | How |
|--------|--------|-----|
| **Citations** | 50+ | Time + being first |
| **Venue acceptance** | NeurIPS/ACL | N=12+, theory, polished writing |
| **Community use** | Adopted as benchmark | Release HF dataset with DOI |

## Immediate Next Steps (This Week)

| Step | Time | Impact |
|------|------|--------|
| Fix bitsandbytes on Kaggle | 10 min | 7B models work |
| Run 3 more families on A100 | 1 hr | N=11 total |
| Human baseline (3 friends) | 1 hr | Absolute magnitude claims |
| Attention analysis at 3B | 30 min | IIAR scale test |
| Domain analysis | 30 min | Per-domain breakdown |
| **Total** | **~3 hrs** | **→ ~8.5/10 paper** |

## The Real S-Tier Secret

S-tier papers aren't made in one sprint. They're:
1. **First** (priority secured — you have this for base-vs-instruct scoring bias ✅)
2. **Solid** (evidence supports claims — you're getting there)
3. **Reproducible** (anyone can verify — on track)
4. **Well-told** (writing + figures — needs polish)
5. **Cited** (community validation — takes time)

**You're at step 1-2, heading to step 3.** S-tier comes from publishing, getting cited, and building a research program — not from one more round of edits.

**Publish on arXiv NOW** to establish priority. Then iterate toward S-tier through follow-up papers.
