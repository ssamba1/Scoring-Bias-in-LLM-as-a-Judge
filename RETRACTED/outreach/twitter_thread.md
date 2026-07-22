# Twitter/X Thread  Scoring Bias in LLM-as-a-Judge

> 10-tweet thread summarizing the paper. Each tweet ≤280 chars with thread numbering.

---

**Tweet 1/10  Hook**
When AI judges AI, can we trust the score? 🎲
I tested 31 models (54,000 judgments) to find out where scoring bias really comes from. The answer surprised me. 🧵👇

[Suggested image: Fig 1  bias landscape across 22 models, showing Score ID as the tallest bar]

**Tweet 2/10  The Problem**
Scoring bias: when the same answer gets different ratings just because you changed the rubric format, swapped numbers for letters, or showed an example first. Prior work found 35+ bias types  but nobody asked WHERE they come from. 🧐

[Suggested image: Animated GIF showing the same answer with three different scores depending on format]

**Tweet 3/10  What We Did**
54,000 judgments × 31 model variants × 3 bias probes.
9 model families with BASE + INSTRUCT pairs (same model, before & after instruction tuning).
22 additional instruct models for breadth.
All open-weight, all reproducible, all for <$3 in API costs. 🧪

[Suggested image: Fig 7  base vs instruct paired comparison lines]

**Tweet 4/10  Key Finding 1: Format Bias ↓**
Good news first: instruction tuning makes models better at understanding scoring formats.
📉 Rubric order bias: −44%
📉 Score ID bias: −77%
Instruct models consistently outperform their base counterparts on format robustness.

[Suggested image: Fig 2  format vs content scatter plot]

**Tweet 5/10  Key Finding 2: Content Bias ↑ (in larger models)**
Here's the twist. In larger models (3B+ parameters, RLHF-trained), content bias INCREASES.
Show a Llama-3.1-8B model a poor example before scoring → the score shifts +1.58 points.
The base model? Almost no shift. 😬

[Suggested image: Fig 3  scale-dependent differential effect bar chart]

**Tweet 6/10  The Scale-Dependent Differential Effect**
Instruction tuning creates a split personality:
- SMALL models (≤1.5B): both format AND content bias decrease ✅
- LARGE models (3B+ RLHF): format ↓ but content ↑ ⚠️
This scale-dependence is itself a major finding.

[Suggested image: Fig 3 with annotations highlighting the crossover]

**Tweet 7/10  Bayesian Evidence**
Bayes factors > 10,000 for all three bias types across 22 models. That's overwhelming evidence scoring bias exists.
For the differential effect: P(content Δ decrease in ≤7B models) = 0.986, BF₁₀ = 6.76.
The data speaks clearly. 📊

[Suggested image: Fig 5  Bayesian posterior distributions]

**Tweet 8/10  Format Efficiency Hypothesis**
Why does this happen? Attention analysis reveals:
Format token attention drops: 23.7% → 20.8% after instruction tuning.
Models become MORE efficient at parsing formats, making fewer format errors. Content attention stays flat.
We call this the Format Efficiency Hypothesis. 🧠

[Suggested image: Attention weight heatmaps showing format attention change]

**Tweet 9/10  Practical Implications**
Three actionable takeaways:
1️⃣ Use NUMERIC labels (not letters/words)  lowest bias across all probes
2️⃣ Test multiple scoring formats before trusting any single result
3️⃣ If you use exemplars in prompts, include BOTH good and poor examples
Report format bias and content bias separately!

[Suggested image: Fig 4  model ranking heatmap, or a practical infographic]

**Tweet 10/10  Resources**
📄 Full paper + code + data: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
💾 Archived data: doi.org/10.5281/zenodo.21361920
🖥️ Interactive dashboard (coming soon)
🏆 Model leaderboard included

Retweet if you believe AI evaluation needs better standards! 🔁

[Suggested image: QR code or graphical abstract]
