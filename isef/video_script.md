# Project Video Script — Bias in LLM-as-a-Judge

## Duration: 3:00 | Target: ISEF video submission, NeurIPS HS Track, general audience

---

### Part 1: The Hook (0:00-0:30)

**Visual:** Split screen — left side shows Chatbot Arena interface, right side shows an LLM typing "Score: 4/5" 
**Narration:** 
"Every day, AI models evaluate other AI models. When you use ChatGPT, when you see rankings on Chatbot Arena, when companies test their latest AI — there's an LLM acting as judge."

**Visual:** The judge's score suddenly changes from 4 to 2 as the rubric format changes
**Narration:**
"But what if those judges are biased? We found they are — and worse, we discovered where that bias comes from."

---

### Part 2: The Problem (0:30-1:00)

**Visual:** Animated diagram showing the LLM-as-a-Judge paradigm — evaluation prompt → judge model → score
**Narration:**
"35 different types of bias have been documented in LLM judges. Position bias, verbosity bias, self-preference bias. But one question remained unanswered:"

**Visual:** Question mark appears over the judge model
**Narration:**
"Is this bias inherent to language models — something they're born with — or is it learned during training? Li et al. published this as the #1 open question in their DASFAA 2026 paper."

---

### Part 3: The Experiment (1:00-1:45)

**Visual:** 3 model families appear: Llama 3, Mistral, Gemma — each splits into "base" and "instruct"
**Narration:**
"We compared 6 model variants — the base pre-trained version and the instruction-tuned version of Llama 3 8B, Mistral 7B, and Gemma 2 2B. We tested each on 3 bias probes:"

**Visual:** Probe 1: rubric order reordering. Probe 2: score labels changing. Probe 3: reference examples appearing.
**Narration:**
"Rubric order bias — does reordering the score scale change the output? Score ID bias — do letter grades vs numbers make a difference? Reference answer bias — does showing an example sway the score?"

**Visual:** Counter ticks up: 8,100 total judgments
**Narration:**
"50 items, 3 repeats, 3 variants — 8,100 total judgments. All on a free Kaggle GPU."

---

### Part 4: The Discovery (1:45-2:30)

**Visual:** Bar chart animation — rubric order drops 44%, score ID drops 77%, reference answer rises 35%
**Narration:**
"And here's what we found. Instruction tuning has a DIFFERENTIAL effect — it makes some biases better and others worse."

**Visual:** Green arrows on rubric and score ID bars dropping. Red arrow on ref answer bar rising.
**Narration:**
"Format-related biases — rubric order and score ID — decreased by 44% and 77% respectively. But content-related bias — reference answers — increased by 35%. Instruction tuning makes models parse formats better but makes them MORE susceptible to content biasing."

**Visual:** 3 model logos with checkmarks
**Narration:**
"This pattern held across ALL three model families. It's a general property of instruction tuning."

---

### Part 5: The Implications (2:30-3:00)

**Visual:** "Two channels" diagram — left: format robustness (improved), right: content sensitivity (worsened)
**Narration:**
"The implication is clear: bias mitigation must target two separate channels. Format biases are naturally improved by instruction tuning. But content biases need specific intervention."

**Visual:** GitHub page, open source logo
**Narration:**
"Our complete code, data, and analysis are open source. The entire experiment costs ZERO dollars to replicate on a free Kaggle GPU."

**Visual:** Text: "First base-vs-instruct comparison for scoring bias"
**Narration:**
"This is the first time anyone has compared base and instruct models for scoring bias. We answered the question Li et al. left open."

**Visual:** Project title, GitHub link
**Narration:**
"Bias in LLM-as-a-Judge. The root cause. The differential effect. Now we know where it comes from — and how to fix it."

---

## Storyboard Summary

| Time | Visual | Audio | Purpose |
|------|--------|-------|---------|
| 0:00-0:30 | Chatbot Arena → judge changing score | Hook: "AI judges are biased" | Attention |
| 0:30-1:00 | Evaluation diagram → question mark | Problem: "Where does bias come from?" | Context |
| 1:00-1:45 | Model family animation → counter | Experiment: "6 models, 3 probes, 8,100 judgments" | Methodology |
| 1:45-2:30 | Bar chart animation | Discovery: "Differential effect" | Results |
| 2:30-3:00 | Two channels → GitHub | Implications: "Two channels, open source" | Impact |
