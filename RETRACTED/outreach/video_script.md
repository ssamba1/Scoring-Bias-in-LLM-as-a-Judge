# Video Script  3-Minute Explainer

**Title:** Can We Trust AI to Judge AI?
**Duration:** ~3 minutes
**Format:** YouTube Shorts / TikTok / Instagram Reel
**Tone:** Clear, engaging, fast-paced

---

| Time | Visual | Narration |
|------|--------|-----------|
| 00:00–00:15 | [Opening: Split screen  on left, a human grading a paper with a red pen; on right, a glowing AI icon grading code] | **Narrator:** "When a human grades a test, we know they can make mistakes. But when an AI judges another AIcan we trust the score?" |
| 00:15–00:25 | [Text appears: "54,000 JUDGMENTS. 31 MODELS. ONE QUESTION." with dramatic zoom] | **Narrator:** "That's the question I set out to answer. 31 model variants. 54,000 judgments. And the answer surprised me." |
| 00:25–00:50 | [Visual: Three boxes appear one by one  "RUBRIC ORDER" with arrows reversing, "SCORE ID" with 1-2-3 turning into A-B-C, "REFERENCE ANSWER" with a thumb up/down] | **Narrator:** "I tested three types of scoring bias. First: Rubric Order bias - does the model notice if you reverse the scale? Second: Score ID bias - change numbers to letters, do the scores change? Third: Reference Answer bias - show a good or bad example first, does it sway the score?" |
| 00:50–01:05 | [Visual: Two brains side by side  "BASE MODEL" on left (gray, simpler) and "INSTRUCT MODEL" on right (colorful, complex). Arrows show scores coming out] | **Narrator:** "For each model family, I compared the raw pre-trained version with the instruction-tuned version. Same brain, different training. This is how we find where bias comes from." |
| 01:05–01:30 | [Visual: Animated bar chart showing downward arrows for format bias. Numbers animate: 44%, 77%] | **Narrator:** "Good news first: instruction tuning makes models better at understanding scoring formats. Rubric order bias drops 44%. Score ID bias drops 77%. Format understanding improves across the board." |
| 01:30–01:55 | [Visual: Bar chart transitions  format bars drop, then a red content bar RISES. A model silhouette grows from small to large as the red bar climbs] | **Narrator:** "But here's the twist. For larger models - those with 3 billion parameters or more, trained with RLHF - content bias actually INCREASES. Show them a poor example before scoring, and their scores shift dramatically. One model moved 1.58 points on a 5-point scale!" |
| 01:55–02:10 | [Visual: Pie chart of attention  "Before" shows format attention as a slice at 23.7%, "After" shows it shrink to 20.8%. Text: "Format Efficiency Hypothesis"] | **Narrator:** "Why? Attention analysis reveals the Format Efficiency Hypothesis: instruction tuning makes models more efficient at parsing formats, using less brain power to understand the scoring rules. But that doesn't fix content sensitivity." |
| 02:10–02:35 | [Visual: Three quick tips appear as cards: "1. USE NUMBERS (not letters)", "2. TEST MULTIPLE FORMATS", "3. INCLUDE BOTH GOOD AND BAD EXAMPLES"] | **Narrator:** "Three practical takeaways. One: use numeric labels - they're the most reliable. Two: always test multiple scoring formats. Three: if you use examples, include both good and bad ones. And report format bias separately from content bias." |
| 02:35–02:55 | [Visual: Screen shows GitHub repo, paper, and interactive dashboard. Text: "github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge"] | **Narrator:** "The best part? All of this is open source. Code, data, interactive dashboards - everything is freely available. The whole experiment cost less than 3 dollars in API fees." |
| 02:55–03:00 | [Closing: Researcher photo with "Sricharan Samba  High School Researcher" text overlay] | **Narrator:** "I'm Sricharan, a high school researcher. If AI is going to judge AI, we need to make sure the judges are fair. The code is open, the data is free - let's fix this together." |

---

## Production Notes

- **Music:** Upbeat, electronic, building in energy through the middle section
- **Pacing:** Fast cuts (2-4 second average shot length), kinetic typography
- **Color scheme:** Blue for format bias (positive), Orange/Red for content bias (warning)
- **End screen:** Subscribe + link to GitHub + "Read the Paper"
- **Captions:** Full-screen burned-in captions for silent viewing
