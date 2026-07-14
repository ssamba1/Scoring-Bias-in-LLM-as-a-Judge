# Understanding AI Bias — An Educational Module

## For High School Students and Teachers

This module explains the key concepts behind our research project in an accessible way. It's designed for classroom use, science fairs, and general audiences.

---

## Module 1: What Is LLM-as-a-Judge?

### Key Idea
AI models are now used to grade other AI models. This is called "LLM-as-a-Judge."

### Real-World Examples
- **Chatbot Arena**: Users chat with two AI models side-by-side, and an AI judge decides which response is better
- **MT-Bench**: A benchmark that uses GPT-4 to score how well other models follow instructions
- **AlpacaEval**: An automated evaluation system for instruction-following models

### Why This Matters
If the judges are biased, the rankings and scores they produce are unreliable. A model that ranks #1 might just be good at exploiting the judge's biases, not at actually being helpful.

### Discussion Questions
1. Can you think of other situations where "judges" might be biased?
2. What happens if an AI judge is used to evaluate safety-critical AI systems?

---

## Module 2: What Is Bias in AI Judges?

### Key Idea
Bias is when an AI judge's score changes based on things that shouldn't matter — like the order of responses, how long they are, or what tone they use.

### The Three Main Biases We Studied
| Bias Type | What It Means | How Much It Affects Scores |
|-----------|--------------|--------------------------|
| **Position Bias** | Prefers responses in first or last position | 12.9% of evaluations |
| **Verbosity Bias** | Prefers longer (or shorter) responses | 31.3% of evaluations |
| **Sentiment Bias** | Prefers positive or negative tone | 15.0% of evaluations |

### Real Example
If you ask an AI judge to evaluate a short, negative-toned response that's placed second, its score might be much lower than the response actually deserves — simply because of the combination of biases.

### Activity
Grab 3-5 friends. Have each person rate the same answer on a 1-5 scale. Compare the scores. Are they different? Why? This is exactly what happens with AI judges — different models have different "opinions."

---

## Module 3: Where Does Bias Come From?

### Key Finding
We discovered that scoring bias is **learned during instruction tuning** — it's not inherent to language models.

### The Analogy
Think of a base model like a newborn baby — it has raw intelligence but doesn't know how to follow instructions. Instruction tuning is like going to school — you learn to follow instructions, but you also pick up some bad habits (biases).

### What This Means
- **Good news**: We can fix bias by changing how we teach AI, not by completely retraining them
- **Challenge**: There's a trade-off between following instructions well and being unbiased

### Discussion Questions
1. Can you think of real-world examples where teaching someone something also gives them biases?
2. How would you design a training program for AI that minimizes bias while still teaching instruction-following?

---

## Module 4: How Do Biases Interact?

### Key Finding
When multiple biases happen at once, they're **compounding** — the combined effect is worse than just adding them up.

### The Math Made Simple
- Individual biases predict: 0.5 points of score change
- Actual combined effect: 0.71 points — that's **42% worse** than expected

### Why This Matters
In the real world, biases never happen in isolation. A response that's short, negative, AND placed in a bad position is common. Our research shows this worst-case scenario is significantly more biased than people realize.

### Analogy
It's like getting rained on while walking to school. If it's raining AND you forgot your umbrella AND you're wearing new shoes that hurt — the total discomfort is worse than just adding up each problem individually.

---

## Module 5: How Can We Fix Bias?

### Our Mitigation Methods

| Method | How It Works | Effectiveness |
|--------|-------------|--------------|
| **Multi-Judge Consensus** | Average scores from multiple judges | Best (0.15 pts correction) |
| **Bayesian Correction** | Use known bias patterns to adjust scores | Good (0.07 pts correction) |
| **Interaction-Aware** | Use interaction ratios to undo compounding | Moderate (0.03 pts correction) |

### Practical Recommendations
1. **Always use multiple judges** — never rely on a single AI judge
2. **Test bias combinations** — don't just test one bias at a time
3. **Include base models as controls** — compare instruction-tuned vs base models
4. **Document bias profiles** — know your judge's strengths and weaknesses

---

## Module 6: Your Turn — Design a Bias Experiment

### Challenge
Design your own experiment to measure bias in an AI judge. We've provided all the code and tools you need.

### Starter Questions
1. Which bias do you want to study? (position, verbosity, sentiment, or all three?)
2. How many items will you test? (50 is enough for a pilot)
3. Which judge model will you use? (Claude, GPT-4o, Gemini, or all of them?)
4. How will you measure bias? (interaction ratio, flip rate, score difference?)

### Resources
- **Our code**: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
- **Interactive demo**: Open `dashboard/live_demo.html` in your browser
- **Full paper**: `paper/camera_ready_paper.tex`
- **Test suite**: `python3 tests/run_all.py`

---

## Glossary

| Term | Definition |
|------|-----------|
| **LLM** | Large Language Model — an AI that processes and generates text |
| **LLM-as-a-Judge** | Using an LLM to evaluate other AI systems |
| **Bias** | Systematic deviation from fair, accurate evaluation |
| **Position Bias** | Tendency to prefer responses in certain positions |
| **Verbosity Bias** | Tendency to prefer responses of certain lengths |
| **Sentiment Bias** | Tendency to prefer certain emotional tones |
| **Interaction Ratio** | How much worse (or better) combined biases are than additive |
| **Compounding** | When combined bias effects are worse than additive |
| **Instruction Tuning** | Training an AI to follow instructions (SFT + RLHF) |
| **Base Model** | A pre-trained model without instruction tuning |

---

## Additional Resources

- **Paper**: Li et al. (2025) — "Evaluating Scoring Bias in LLM-as-a-Judge"
- **Paper**: Yang et al. (2025) — "Any Large Language Model Can Be a Reliable Judge"
- **Paper**: Pan et al. (2025) — "User-Assistant Bias in LLMs"
- **Interactive**: Open `dashboard/live_demo.html` to explore bias yourself
- **Code**: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge — all our code and data

---

*This educational module was created by Student A and Student B as part of their ISEF research project on bias in LLM-as-a-Judge. All materials are open source and freely available.*
