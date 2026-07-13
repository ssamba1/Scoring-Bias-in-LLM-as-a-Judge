# Budget Worksheet — Bias Interaction Experiment

## Option 2: Bias Interaction (API-based, zero GPU)

### API Costs (5 judges × 3,200 items × 3 repeats)

| Judge Model | Provider | Cost per 1k calls | Total calls | Estimated cost |
|------------|----------|-------------------|-------------|----------------|
| Claude Sonnet 4 | Anthropic | $0.015 | 9,600 | $14.40 |
| GPT-4o | OpenAI | $0.010 | 9,600 | $9.60 |
| Gemini 2.0 Flash | Google | $0.0005 | 9,600 | $0.48 |
| DeepSeek V3 | DeepSeek | $0.001 | 9,600 | $0.96 |
| Llama 3 70B | Together/Groq | $0.001 | 9,600 | $0.96 |
| **Subtotal (judges)** | | | **48,000** | **$26.40** |

### Other Costs

| Item | Cost | Notes |
|------|------|-------|
| Domain name (optional) | $0 | GitHub Pages is free |
| LaTeX (Overleaf) | $0 | Free tier |
| Colab Pro (optional) | $0 | Not needed for API-based experiment |
| Internet | $0 | Already have |
| **Subtotal (other)** | **$0** | |

### Total: ~$26.40

---

## Option 1: Root Cause (GPU-based)

### Compute Costs

| Resource | Purpose | Hours | Cost |
|----------|---------|-------|------|
| Colab T4 GPU | Load 6 models, run 50 items each | ~8-10 | $10 (Colab Pro) |
| Or: Together AI API | Inference API instead of local GPU | ~8 hours | $15 |

### Model Access (all free)

| Model | HuggingFace | Access |
|-------|-------------|--------|
| Meta-Llama-3-8B | meta-llama/Meta-Llama-3-8B | Free (request access) |
| Meta-Llama-3-8B-Instruct | meta-llama/Meta-Llama-3-8B-Instruct | Free (request access) |
| Mistral-7B-v0.3 | mistralai/Mistral-7B-v0.3 | Free, no restrictions |
| Mistral-7B-Instruct-v0.3 | mistralai/Mistral-7B-Instruct-v0.3 | Free, no restrictions |
| Gemma 2 2B | google/gemma-2-2b | Free (accept terms) |
| Gemma 2 2B IT | google/gemma-2-2b-it | Free (accept terms) |

### Total: ~$10-15

---

## Comparison

| Item | Option 1 (Root Cause) | Option 2 (Bias Interaction) |
|------|----------------------|----------------------------|
| **Compute cost** | $10-15 (GPU) | $26 (API) |
| **Software** | $0 | $0 |
| **Domain** | $0 | $0 |
| **Total** | **$10-15** | **$26** |
| **Time** | 4 weeks | 3 weeks |
| **Technical skill needed** | Medium (HuggingFace, GPU) | Low (API calls) |

## Funding Sources
- School science fair budget (often covers small projects like this)
- Parental support
- Personal funds
- Request API credits from providers (some have academic credit programs)
  - Anthropic: research credits available
  - OpenAI: researcher access program
  - Google: free credits for Google Cloud
