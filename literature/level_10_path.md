# Level 10: How to Open a New Subfield

## What Level 10 Actually Means

Level 10 means your work changes how an entire field thinks and operates. 
Examples: "Attention is All You Need" (transformer architecture), 
BERT (pre-training changes everything), AlexNet (deep learning works).

These papers didn't just find something new — they made everything before them obsolete.

---

## What That Would Look Like for Our Work

A level-10 contribution in LLM bias research would mean:

1. **Everyone uses your method** to evaluate/audit their models
2. **Your finding changes how models are trained** (not just evaluated)
3. **Your framework becomes the standard** — people say "run the Smith bias audit" like they say "run ImageNet"

---

## The Specific Path

| Level | What It Looks Like | Impact |
|-------|-------------------|--------|
| **8** | Definitive study of scoring bias origins | The paper people cite |
| **9** | + A widely used bias audit tool | The API people call |
| **10** | + A training method that eliminates the bias | The technique people adopt |

---

## To Reach Level 10

You need to ADD three things on top of the definitive study:

### 1. A Deployable Bias Audit Tool (Already 60% Built)

`bias_api.py` exists but needs to be:
- Deployed as a live web service (Render, Railway, or similar — free tier)
- Accept any HuggingFace model ID → return a bias report card PDF
- Get used by real researchers (share on Twitter, Reddit, LinkedIn)

**Impact:** Anyone can audit their model in 30 seconds.

### 2. A New Evaluation Protocol That Becomes Standard

Right now, people evaluate LLMs with MT-Bench, Chatbot Arena, etc. — all of which have biased judges. Your protocol:
- "Score reports should include a bias profile alongside the score"
- Show that it changes model RANKINGS (not just scores)
- Get adopted by Chatbot Arena or MT-Bench maintainers

**Impact:** Changes how every LLM evaluation is done.

### 3. A Training Method That Fixes Content Bias

The differential effect says: format bias improves, content bias worsens.
A level-10 paper would also show how to fix content bias:
- Calibrate instruct models to reduce exemplar sensitivity
- Train a "bias-resistant" judge model (fine-tune on adversarial examples)
- Show that the fix preserves scoring accuracy while eliminating the differential effect

**Impact:** Your method becomes the default way to train LLM judges.

---

## The Comparison

| Dimension | Level 8 (Definitive Study) | Level 10 (New Subfield) |
|-----------|---------------------------|----------------------|
| Contribution | Found the differential effect | **Created the bias audit paradigm** |
| Tooling | Open source code | **Deployed web service used by others** |
| Standard | Paper is cited | **Protocol is adopted by benchmarks** |
| Solution | Identified the problem | **Delivered a working fix** |
| Recognition | Peer-reviewed publication | **Industry adoption + media coverage** |

---

## Is Level 10 Achievable for This Project?

| Prerequisite | Status | Path |
|-------------|--------|------|
| Novel finding | ✅ Have it | — |
| Clean experiment | ✅ Have it | — |
| Deployable tool | ⚠️ Built but not deployed | Deploy bias_api.py to Render |
| New protocol | ❌ Not proposed | Write a position paper/brief |
| Training fix | ❌ Not done | Fine-tune a bias-resistant judge |
| Community adoption | ❌ Not started | Share on social media, engage with benchmark orgs |

**Level 10 is achievable, but it's a different type of work.**
You stop writing papers and start building tools, engaging with the community, and getting things adopted.

---

## The Decision

| Path | Time | Impact |
|------|------|--------|
| **Level 8** (definitive paper) | 30 hrs writing + OpenRouter run | Respected paper, good for college |
| **Level 10** (new subfield) | 3 months: deploy + engage + fix | Recognition, industry attention, legacy |

**Level 8 takes a month. Level 10 takes a year of sustained effort.**

Which do you want? Both are achievable.
