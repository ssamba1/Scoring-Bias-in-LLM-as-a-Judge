# Fifty ways to strengthen this paper

Written 2026-08-20 against commit `739893b` (CI green, 1077 tests, 259
mutations). Ordered by judged value, not effort. The first ten are worth more
than the last thirty combined; the tail is real but marginal, and saying so is
part of what the list is for.

Tags: **[free]** analysis or writing on existing data - **[gpu]** local compute -
**[api]** paid API calls - **[human]** annotators, and an ethics/consent decision
before any data is collected.

## Tier 1 - the scale ceiling (the paper's biggest vulnerability)

The panel is 13 families, all 0.1-8B. The entropy-bias relation is strong below
3B (-0.51, -0.42) and flat above it (-0.02, n=30). The single point above 8B is
a **4-bit quantized** 14B run, attenuated to +0.06 against the panel's +0.26 --
so the one piece of evidence that the effect fades with scale is confounded by
the variable most likely to fade it artificially.

1. **[gpu]** Re-run the 14B extension unquantized (bf16). Disentangles
   quantization from scale. Nothing else here changes the scope claim as cheaply.
2. **[gpu]** Run `q32b_harness.py`. It is written, committed, and has never been
   run -- no results file exists. Qwen2.5-32B has base+instruct.
3. **[gpu]** Quantization control: one family at bf16 / 8-bit / 4-bit. Turns a
   confound into a measured finding, and stands alone as a caution for anyone
   benchmarking quantized judges.
4. **[gpu]** Add Llama-3.1-8B base+instruct. The most-deployed open family is
   absent from the panel entirely.
5. **[gpu]** Add Gemma-2-9B and Gemma-2-2B. Second absent major family; 9B also
   thickens the underpowered 3-8B band.
6. **[gpu]** Add Mistral-7B-v0.3 base+instruct. Third absent major family.
7. **[gpu]** Add Phi-3-mini/small -- a distinct training recipe, testing whether
   the effect is recipe-general or Qwen/OLMo-flavoured.
8. **[free]** Power analysis for the >3B band. State whether -0.02 over n=30 is
   evidence of flatness or absence of evidence. That distinction is the entire
   scope claim and is currently left ambiguous.
9. **[free]** Plot effect size against log parameters with the 14B and frontier
   points marked, so the scope limit is visible rather than buried in prose.
10. **[api]** Extend the frontier arm past three judges wherever logprobs are
    exposed (Together, Fireworks, DeepInfra host large open judges).

## Tier 2 - the registered-null problem

The preregistered per-probe test is null for every probe (smallest Holm p =
0.13). The paper says so plainly, which is right, but a referee can dismiss it in
one line and force everything else into the role of rescue argument.

11. **[free]** Bayes factors per probe. Separates evidence *for* no effect from
    absence of evidence, which the frequentist test cannot -- the cheapest way to
    make the null informative rather than embarrassing.
12. **[free]** Equivalence tests (TOST) on the null probes, so "null" carries a
    bound instead of a shrug.
13. **[free]** Refit as one hierarchical model with partial pooling across probes
    instead of five tests plus Holm. More powerful and better matched to the
    design; report it beside the registered analysis, never instead of it.
14. **[gpu]** Once items 4-7 land, re-run the registered test at n=17-20
    families. The honest fix for low power is more units.
15. **[free]** Give the null its own subsection rather than a sentence. A
    weakness you raise reads as calibration; one a referee finds reads as spin.
16. **[free]** Report ICC and the family-level variance component explicitly.
17. **[free]** Fix the mixed-model boundary/convergence warnings (reparameterize
    or change optimizer) and print convergence diagnostics in the table.
18. **[free]** Promote the 12-specification check to a full specification curve
    with inference over the multiverse.

## Tier 3 - deepen the mechanism (the most novel asset)

Patching currently covers **one family** (Qwen2.5-1.5B, with 0.5B as a partial
replicate). The stage ladder covers OLMo-2-1B/7B and Tulu-3-8B.

19. **[gpu]** Replicate the patching band on a non-Qwen family. A layer-10 result
    from one family is a Qwen fact until shown otherwise.
20. **[gpu]** Component-level patching at the band: attention vs MLP, then heads.
    Moves the claim from "where" to "what".
21. **[gpu]** Normalize band location by relative depth across families -- is it
    layer 10, or 35% of the way through?
22. **[gpu]** Cross-probe patching: do rubric-order and authority ride the same
    circuit or different ones? Currently assumed, never tested.
23. **[gpu]** Bidirectional patching (base into instruct as well as the reverse)
    to test whether the transfer is symmetric.
24. **[gpu]** Extract a responsiveness steering vector and test whether adding or
    subtracting it modulates measured bias. Turns mechanism into control, and is
    the likeliest single result to lift this into a top-tier venue.
25. **[gpu]** Patch SFT-stage activations into the RLVR checkpoint -- can the
    SFT-installed responsiveness be undone downstream?
26. **[gpu]** Tuned-lens or logit-lens at the score position, to visualize when
    the nuisance becomes score-consequential.
27. **[gpu]** Add a second stage ladder from a different lab (a Zephyr or Nous DPO
    chain). The SFT/DPO split currently rests on OLMo plus Tulu.

## Tier 4 - measurement validity

28. **[gpu]** Validate the expected-value readout against actually sampled scores
    at temperature. The readout is defended behaviorally; this defends it
    directly.
29. **[free]** Quantify the answer-token mass per family. The limitation says
    "small" without giving a number.
30. **[free]** Sensitivity to the answer-token set (space-prefixed digits and
    other tokenizer variants).
31. **[gpu]** Compare against constrained decoding as a third readout.
32. **[free]** Report test-retest across seeds wherever decoding is stochastic.
33. **[free]** Extend the chat-template check (currently three families) to the
    whole panel.

## Tier 5 - breadth of task and language

34. **[gpu/api]** A second dataset beyond MT-Bench -- AlpacaEval or Arena-Hard.
    Single-distribution is a standing referee objection and the fix is mechanical.
35. **[gpu]** **Pairwise preference judging (A/B).** The dominant deployment mode
    for LLM judges, and the paper does not test it at all. The highest-value item
    in this tier by a distance.
36. **[gpu]** Long-form judging (essays, code) where the score distribution
    behaves differently.
37. **[gpu]** Reference-free versus reference-based judging as a factor.
38. **[gpu]** A third language beyond English and Chinese, ideally not
    Indo-European and not from a natively bilingual series.
39. **[gpu]** A radically different scoring interface (words only, 1-100, stars).
    Every current template is instruction-style.

## Tier 6 - human grounding

40. **[human]** A small annotation study: do humans change their scores under
    these perturbations? Converts "bias" from a definitional claim into a
    validated construct. The most fundamental gap in the paper.
41. **[human]** Human agreement on the gold discrimination task, as a ceiling for
    the 0.98 figure.
42. **[human]** Have annotators rate whether the reversed-rubric condition is
    genuinely ambiguous. Limitation 6 raises this and cannot resolve it alone.

## Tier 7 - mitigation and practical payoff

43. **[gpu]** Broaden mitigation beyond marginalization's 59%: self-consistency,
    rubric randomization, format ensembling.
44. **[gpu]** Test whether mitigations compose. The companion study found
    combination can backfire; this design could settle it.
45. **[free]** Report the accuracy cost of each mitigation beside its bias
    reduction. A defense with no cost column is not actionable.
46. **[free]** Ship a drop-in debiased-judge recipe with measured guarantees.

## Tier 8 - theory

47. **[free]** Close the finite-entropy gap (Limitation 4): characterize bias
    beyond the decisive limit.
48. **[free]** Derive and test a functional form for bias against entropy, rather
    than only a rank correlation.
49. **[free]** Connect the decomposition to the calibration literature.
    Sharpness/calibration decompositions are the same shape, and the bridge would
    widen the audience considerably.
50. **[free]** A theory of why SFT raises responsiveness while preference tuning
    does not, in terms of what each objective does to the perturbation response.

## If you only do five

**2, 1, 35, 24, 40.** Run the 32B harness that already exists; de-confound the
14B point; test pairwise judging; build the steering vector; ground "bias" in
human judgement. The first two close the scope hole, the third covers the
dominant deployment mode, the fourth is the likeliest route to a top-tier
result, and the fifth answers the one objection a determined referee can
otherwise press indefinitely.

## What is deliberately not on this list

Another undirected pass over the existing numbers — a re-check with no
hypothesis behind it.

This section used to say something stronger and worse: that auditing the
existing numbers was *done*, and that further passes over the same 63,040
judgments would be "motion, not progress". The day after that was written is
what refuted it. Auditing on 2026-08-21 found three published digits wrong from
a value rounded once for storage and again for display; a registered Wilcoxon
p that was a rounding artefact (0.600, actually 0.588, because rounding to three
decimals manufactured a tie between two families); the asterisk in the main
table decided by a single arbitrary bootstrap seed while the prose separately
asserted the intervals were seed-stable; five derived files that CI regenerated
and never compared against what was committed; and a platform allowlist still
accepting a divergence the documentation says was fixed.

The narrower claim is the true one. Re-checking the same numbers the same way is
motion. What found things was auditing along an axis nobody had used yet — the
composition of two individually correct steps, a hand-maintained list against
what it is supposed to cover, a verdict against the precision it is stored at.
Those axes are recorded so they are not rediscovered by accident.

Everything above still adds evidence rather than re-checking it, and that is
still why it is the priority. But "done" was the wrong word, and the list should
not have claimed it.

---

# Tiers to maximum, and the gap count

The paper names nine limitations. Seven more gaps are real but unnamed. Seventeen
total -- but only four are load-bearing, and the distinction matters more than
the count.

## The seventeen

**Named in the paper (9).** L1 causal contrast stops at open weights, frontier
is three cross-sectional judges. L2 family as unit, greedy decoding,
instruction-style templates only, Chinese replication is one bilingual series.
L3 twenty predictions, family-wise error controlled only within the headline.
L4 theory characterized only in the decisive limit. L5 expected-value readout
defended behaviorally, not by mass. L6 reversed-rubric ground truth is
ambiguous. L7 verbosity's terse variant can remove information (largely defused:
99% of the effect is the padded variant). L8 the increase is a property of the
continuous readout; argmax washes out the format probes. L9 the attention null
uses one operationalization of attention.

**Unnamed (8).** U1 pairwise A/B judging is untested entirely. U2 no human
validation that the perturbations are nuisance -- "bias" is definitional. U3 one
task distribution. U4 patching rests on one family. U5 the stage ladder is
essentially one lab. U6 mitigation is one method at 59%, with no composition and
no accuracy cost. U7 the only causal point above 8B is 4-bit quantized. U8 the
registered per-probe test is null for every probe.

## The ladder

Each tier states what it closes and what it buys. Cost is order-of-magnitude.

**T0 -- where it is.** Honest, mechanistically interesting, mid-tier. Held back
by U8, L1/U7, U1.

**T1 Scope hole closed** (L1 partial, U7; ~3 GPU-weeks). Unquantized 14B, the
32B harness that already exists, plus Llama-3.1-8B / Gemma-2-9B / Mistral-7B.
Buys: the causal claim reaches the regime small judges are deployed in, and the
flat >3B band becomes a result instead of an ambiguity.

**T2 Registered analysis works** (L3, U8; free once T1 lands). n≈20 families
re-runs the registered test with real power; Bayes factors and a hierarchical
refit make the nulls informative. Buys: removes the one-line dismissal.

**T3 Mechanism general and controllable** (U4, U5, L9, L4 partial; ~4 GPU-weeks).
Patching on three-plus families, component-level within the band, a second stage
ladder, and a responsiveness steering vector. Buys: the contribution stops being
observational. **This is the tier that changes the venue.**

**T4 About real judging** (U1, U3, L2 partial; ~2 GPU-weeks + API). Pairwise A/B,
a second dataset, a non-instruction scoring interface. Buys: external validity
for how judges are actually used.

**T5 Bias validated, not defined** (U2, L6, L7; annotator budget + ethics
decision). Buys: the construct itself. Without it, a determined referee can
always say the perturbations were assumed to be nuisance rather than shown.

**T6 Actionable** (U6; ~1 GPU-week). Mitigation suite with accuracy costs and
composition. Pairs with T3: mechanism plus defense is a complete story.

**T7 Theory complete** (L4, L5, L8; free, hard). Finite-entropy characterization,
sampled-score validation, a readout theory that explains why argmax compresses.

**T8 Independently replicated** (U9). Not work you do; work someone else does.
The terminal state, and it is not purchasable.

## The four that carry weight

U8, L1/U7, U1, U2. The registered null, the scale ceiling, pairwise judging, and
human grounding. Every claim in the paper either rests on these or is scoped
around them. The other thirteen are already defused, honestly bounded, or
refinements a referee would call future work.

## The honest caveat about "nothing left"

Closing seventeen gaps is a research programme -- realistically three papers, not
one revision -- and a paper that tries to close all of them stops having a
thesis. The right target is not "nothing left" but **"nothing left that the
claims depend on."** That is T1+T2 for defensibility, plus T3 if the goal is the
top tier, plus T5 if the goal is that no referee can reopen the construct.
Everything else is a better second paper than a bigger first one.
