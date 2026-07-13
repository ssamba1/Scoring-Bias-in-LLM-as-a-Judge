# ISEF Booth & Presentation Guide

## Booth Setup

### Physical Layout (8 ft table)

```
┌─────────────────────────────────────────────────────┐
│  [TRIFOLD POSTER BOARD - 48" x 36"]                │
│  Left panel:         Center panel:        Right:   │
│  - Research question  - Key findings      - Methods │
│  - Related work       - Figures 2-4       - Results │
│  - Gap identified     - Conclusion        - Future  │
├─────────────────────────────────────────────────────┤
│  [LAPTOP/ TABLET]     [HANDOUTS]    [NOTEBOOK]      │
│  Showing interactive  - One-pager    - Lab notebook  │
│  dashboard/demo       - Paper summary - Data logs    │
└─────────────────────────────────────────────────────┘
```

### What Judges Look For (in order of importance)

1. **Student's understanding** — Can you explain WHY your results matter?
2. **Creativity** — Did you come up with the idea yourself?
3. **Independence** — How much of the work did you do?
4. **Rigor** — Is the methodology sound?
5. **Impact** — Does this matter?

### Your Opening Statement (15 seconds)

"Hi, I'm [Name]. Our project investigates where AI judge bias comes from. We discovered that instruction tuning — the process that teaches AI to follow instructions — has opposite effects on different types of bias. Format biases improve, but content biases get worse. This has never been shown before."

### Common Questions and Your Answers

**Q: What is LLM-as-a-Judge?**
A: "It's when an AI model evaluates another AI model's output. Used everywhere — Chatbot Arena, MT-Bench, and in industry to evaluate customer service bots."

**Q: Why does this matter?**
A: "If the judges are biased, the rankings are unreliable. A model that ranks #1 might just be good at exploiting the judge's biases."

**Q: How is this different from existing research?**
A: "Li et al. published a paper in DASFAA 2026 that identified scoring biases but explicitly said they didn't know where the bias came from. We answered that question."

**Q: What was the hardest part?**
A: "Getting the models to run on a single GPU — Llama 3 8B uses 16GB of memory, and a Kaggle T4 only has 16GB. We had to optimize the loading carefully."

**Q: What would you do next?**
A: "Test more model families to strengthen the statistics, and develop specific mitigation strategies for content-based biases."

### The Notebook (reviewed BEFORE interview)

ISEF judges review your lab notebook before they talk to you. Include:
- **Dated entries** showing when you did each experiment
- **Data tables** with raw scores
- **Error analysis** — what went wrong and how you fixed it
- **Literature notes** — summaries of papers you read (we have these in `literature/`)
- ALL in a physical bound notebook

### The Poster

Print your poster from `isef/poster.html` as a 48"×36" trifold. Key design principles:
- **Large font** — readable from 3 feet away
- **One main message** per panel
- **Figures over text** — the bar charts tell the story
- **Your finding first** — don't bury the differential effect

### Handouts

Print 30 copies of `isef/one_pager.md` formatted as a single page (front and back). Include:
- Title and abstract
- Key finding with the 3-number table
- QR code to GitHub repo
- Your contact info
