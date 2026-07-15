# Video Abstract  Screen Recording Script

## 3-minute narrated walkthrough

---

### [0:00-0:15] Hook
**Visual:** Split screen  left side shows LLM judge awarding scores, right side shows model training stages (base → instruct)
**Narrator:** "When an AI model judges another AI model, can you trust the score? We found that the answer depends on where the model is in its training  and the effect goes in opposite directions."

### [0:15-0:45] The Problem
**Visual:** Diagram of LLM-as-a-Judge, highlight 3 bias types with arrows
**Narrator:** "Scoring bias is a known problem. Li et al. documented three types at DASFAA 2026  but nobody knew whether these biases come from pre-training or from instruction tuning."
**Visual:** Zoom into model architecture, split into "Base" and "Instruct" side by side
**Narrator:** "We tested both base and instruct versions of 30 model variants across 15 families  over 40,000 judgments in total."

### [0:45-1:30] The Finding
**Visual:** Bar chart animation  format bars drop (green), content bar rises (red)
**Narrator:** "The result was surprising and consistent across every family we tested."
**Visual:** -44%, -77%, +35% appear in sequence
**Narrator:** "Format biases  like rubric order and score label format  decreased by 44 to 77 percent after instruction tuning. But reference answer bias  a content-related bias  increased by 35 percent."

### [1:30-2:00] Why This Happens
**Visual:** Attention flow diagram  base model shows shallow attention to all tokens, instruct shows deeper attention
**Narrator:** "We call this the Instruction-Induced Attention Redistribution, or IIAR. Instruction tuning teaches models to attend more carefully to everything in the prompt."
**Visual:** Green checkmark appears over format tokens, red warning appears over content exemplars
**Narrator:** "For format features, this helps. For content features  like reference examples  it actually makes things worse."

### [2:00-2:30] What This Means
**Visual:** Split screen again  left side shows improvement in Chatbot Arena style ranking, right shows mitigation methods
**Narrator:** "The good news: instruction tuning naturally improves format robustness. The bad news: you can't stop there. We show that ensembling across models reduces bias by 52 percent, and calibration helps by 45 percent."

### [2:30-3:00] Call to Action
**Visual:** Repository page, paper landing page
**Narrator:** "Every model, every analysis, every figure is open source at github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge. If you're building with LLM judges  report your bias profile alongside your scores. The finding changes how we think about evaluation."
**Visual:** Fade to title card with citation
**Narrator:** "Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge."

---

## Technical Specs
- **Format:** MP4, 1920×1080, 30fps
- **Audio:** TTS or voiceover at moderate pace
- **Slides/tool:** Can be created with Keynote, PowerPoint, or Manim
- **Text overlay:** Keep key numbers on screen (44%, 77%, 35%)
