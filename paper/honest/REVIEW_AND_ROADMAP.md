# Peer Review + Roadmap: "Confidence Is Not Robustness" (v2)

Reviewed 2026-07-19 against the standard of a strong ML-venue submission.
Verdict up front: **the paper is sound, internally consistent (after today's fixes), and
honest. Its ceiling is set by external validity (≤8B open models) and by inference on
n=13 families. Everything below is ordered by how much it raises that ceiling.**

---

## Part 0 — Section-by-section peer review (what a referee would say)

| Section | Verdict | Main criticism |
|---|---|---|
| Abstract | Strong | Dense but accurate. Add scale of evidence (26 checkpoints, 13,000 per-item scores). |
| Intro | Strong | Deployment stakes well made. The confound paragraph is a highlight. |
| Related work | Good | Positioning table effective. Add scale-range column; a referee will check each row's claims. |
| Method | Good | Expected-value scoring well defended. Items are author-written — referee will ask for a public-dataset item set (see C6). |
| Theory §4 | Good | Math is correct but elementary (softmax Jacobian + Cauchy–Schwarz + CGF tilt). Its value is the *decomposition framing*, not depth. Cor. 2 now carries the fixed-responsiveness caveat. Referee will ask for the exact finite-perturbation expression (D1). |
| §5.1 main result | Strong | Now states 3/5 CIs exclude zero + pooled LMM. Honest. |
| §5.2 mechanism | Strongest section | ρ=+0.82 responsiveness→bias with both terms measured is the core contribution. Weakness: 130 pooled points from 26 checkpoints — needs clustered inference (B1). |
| §5.3 patching | Strong | Real intervention, sharp layer-10 localization. n=35 items, one family + a small replication — referee will want a third family. |
| §5.attn | Good (honest null) | Coarse metric; limitation now stated. Positive circuit identification (C7) would upgrade it. |
| §5.5 predictor | Adequate | R²=0.27, n=13 — fragile. Needs bootstrap CI (B2) and the 9-family instability already disclosed is good practice. |
| §5.6 gold | Good | n=20 author-written pairs; needs human validation (C3). Reversed-rubric ambiguity properly disclosed. |
| §5.template | Good | 3 templates × 3 families. Enough to blunt the "one prompt" attack. |
| §5.8 mitigation | Adequate | Only tested on score-ID. Extend to all five probes (C8). |
| Discussion | Strong | "Inverted screen" is the memorable practical claim. |
| Limitations | Strong | Now 7 items, unusually candid. This is a feature — keep it. |
| Reproducibility | Strong | One-script regeneration + integrity audit is rare and valuable. Add CI numbers-match test (F5). |

## Part A — Fixed in this pass (2026-07-19)

1. **Critical contradiction**: Appendix C rec. (2) claimed entropy "does not predict bias
   out-of-sample," contradicting §5.5's R²=0.27 inverted predictor. Rewritten.
2. Typo mid-sentence in "Beyond first order" ("every order. along").
3. **Corollary 2** now states it holds at *fixed responsiveness* and points to why the
   naive reading fails empirically.
4. **§5.1 overstatement**: "increases bias for all five types" → exact claim
   (all five point estimates positive; 3/5 CIs exclude zero; pooled LMM p<10⁻³).
5. Reproducibility section now lists the multitemplate and attention harnesses/raw files.
6. New limitation: verbosity-terse truncation can change true quality; verified from raw
   data that the quality-preserving padded-only contrast shows the same direction
   (0.29→0.53, 11/13 families) and stated it.
7. New limitation: raw-attention metric is a coarse proxy; null rules out only the
   coarse hypothesis.
8. 60% → 59% mitigation figure (two places; matches the computed 1.09→0.45).

**Second round, after the literature novelty check:**

9. **G-Eval prior art (fatal attack, fixed).** Expected-value/logit scoring is
   established (G-Eval, Liu et al. 2023; Wang et al. 2025 "Judgment Distribution,"
   EMNLP Findings; TrustJudge 2025). The paper no longer claims the readout as a
   contribution: §3.2, Contribution 4, the abstract, and Related Work now cite this
   line and scope our claim to (i) documenting the parse-failure *confound* for
   base-vs-instruct comparisons and (ii) using the distribution as the measured object
   of the theory. All four citations verified against arXiv (titles + full author lists).
10. **Capability confound (fatal attack, fixed with new analysis).** The entropy–bias
   relation survives partialling out model size: partial rank ρ = −0.38 (p < 10⁻⁴)
   vs pooled −0.41, and size correlates *positively* with bias (+0.18) — the opposite
   direction of the confound story. Honest caveat added: relation strong <3B
   (ρ = −0.51, −0.42), flat in the small >3B subsample (n=30). Computed in
   `analyze_mechanism.py` (`size_confound_control` block) so it regenerates from the
   raw file like every other number.
11. Related work now cites "Safer or Luckier?" (ACL 2025) as the closest
   confidence≠robustness prior, positioned at model level vs our distribution level.

Recompiled clean: 15 pages, no undefined references, all new content verified in the PDF.

## Part 0.5 — Novelty audit (independent literature sweep, 2026-07-19)

Per-claim verdicts from a systematic search:

- **Tuning increases judge bias** — PARTIALLY NOVEL. Closest prior: Pan et al.
  (arXiv:2508.15815, user-deference; already cited). The controlled base-vs-instruct
  comparison across 13 families × 5 scoring-bias types is new; the direction
  (tuning → more bias) echoes the sycophancy literature.
- **Decomposition theory** — PARTIALLY NOVEL. The math is standard softmax calculus;
  the decisiveness×responsiveness framing for judge bias is the new part. Paper now
  says so explicitly.
- **Negative entropy↔bias ("confidence is not robustness")** — MOSTLY NOVEL. Not
  directly established anywhere found; nearest is arXiv:2503.09347 at model level.
  This plus the one-pass predictor are the paper's core novelty — defend them first.
- **Expected-value scoring** — NOT NOVEL (G-Eval 2023). Now correctly attributed;
  the parse-failure confound documentation is the remaining new piece.
- **One-forward-pass bias predictor** — MOSTLY NOVEL. Nearest: entropy→correctness
  predictors (arXiv:2602.13699). Bias as the target is new.
- **Patching/attention** — methodology NOT novel (ROME/MEMIT lineage;
  arXiv:2510.12229 patches tuning-induced moral bias to mid layers); application to
  judge scoring bias is incremental but sound.

**Overall:** competition-level (ISEF/Regeneron): competitive. Top venue: workshop /
Findings realistic after Parts B–C; main-track needs frontier judges (C1) and the
stage ablation (C2).

## Part B — Statistical rigor upgrades (do before any submission)

**B1. Clustered inference for the pooled correlations (most important).**
ρ=−0.41 and ρ=+0.82 pool 130 points from 26 checkpoints — points within a checkpoint are
not independent. The within-base/within-instruct splits already reported partially
answer this; make it airtight:
- *How*: repeated-measures correlation (`pingouin.rm_corr`, subject=checkpoint) or an
  LMM `bias ~ entropy + (1|family) + (1|probe)`; report next to the pooled ρ.
- *Where*: one paragraph in §5.2 + a stats appendix.
- *Cost*: 1–2 h, no new data.

**B2. Bootstrap CI on the LOO predictor.**
R²=0.27 from 13 LOO folds is fragile. Bootstrap families (10⁴ resamples of the LOO
predictions), report the CI; if it spans 0, say the predictor is suggestive, not
established. Also report rank correlation of LOO predictions.
*Cost*: 1 h.

**B3. Leave-one-family and leave-one-vendor sensitivity.**
Re-run headline tests excluding (a) each family in turn, (b) all Qwen models at once
(largest vendor block), (c) all models <0.5B. Report min/max of the instruct effect.
Kills the "driven by one vendor / by tiny models" review.
*Cost*: 2 h, no new data.

**B4. Readout-robustness check.**
Correlate EV-based Δ with discrete flip-rate-based bias per checkpoint×probe; if high,
findings are not an artifact of the expected-value readout. One number in Method.
*Cost*: 30 min.

## Part C — New experiments, ordered by impact per unit effort

**C1. Frontier/closed judges (highest impact).**
The whole paper lives at ≤8B. `repro/closed_harness.py` exists; needs an
OpenRouter/OpenAI key (~$5–20). Run the 5 probes on 3–5 frontier models
(GPT-4o(-mini), Claude, Gemini, Llama-3.1-405B via logprobs or 20-sample distributions).
Question answered: does the confidence–bias inversion persist at frontier scale? Either
answer is publishable; running it converts the paper's biggest limitation into a result.
*Cost*: key + one evening.

**C2. Tuning-stage ablation (best mechanistic addition).**
OLMo-2 and Tülu publish intermediate checkpoints (SFT-only, +DPO, +final). Run the
harness on each stage: which stage inflates responsiveness? Turns "instruction tuning"
from a black box into a stage-resolved claim. No other paper in this niche has this.
*Cost*: 1–2 Kaggle GPU sessions, harness reuse.

**C3. Human validation of the gold set.**
2–3 humans independently rank the 20 good/bad pairs; report agreement (expect ~100%).
Removes the "author-written ground truth" objection.
*Cost*: 1 h of two other people's time.

**C4. Scale extension to 14–32B.**
Qwen2.5-14B/32B base+instruct fit on Kaggle 2×T4 with 4-bit quantization
(bitsandbytes NF4). Extends the size axis, tests whether the inversion bends at scale.
*Cost*: 2–3 GPU sessions; quantization noise must be reported.

**C5. Public-dataset item set.**
Rebuild the 50 items from a public source (e.g. Dolly-15k or Alpaca responses,
filtered to mid-quality) and replicate §5.1–5.2. Removes item-authorship as a variable
and adds a second-item-set replication — reviewers love this.
*Cost*: half a day.

**C6. Non-English replication.**
Translate the 50 items (one language, e.g. Chinese on Qwen — native strength).
Drops the English-only limitation.
*Cost*: half a day.

**C7. Positive circuit identification.**
Upgrade the attention null: per-head patching or path patching between the nuisance
span and the score position, base vs instruct. If a head/MLP route is found, the
mechanism story is complete end-to-end. Hardest item on this list.
*Cost*: several days; genuinely research-grade.

**C8. Mitigation breadth.**
Marginalization currently tested on score-ID only. Apply format-marginalization /
exemplar-withholding / length-normalization to each of the five probes; report a
mitigation table. Also test template-ensembling (average over the 3 templates —
data already exists in `results_multitemplate.json`).
*Cost*: 2–3 h, mostly no new data.

## Part D — Theory strengthening

**D1. Exact finite-perturbation expression.**
For δ = t·u the tilted score is the CGF derivative; write the exact series with the
third/fourth cumulants computed from the data, and show empirically how far first-order
is from exact for the measured δ's. Converts "beyond first order" from a paragraph
into a verifiable appendix.

**D2. Tie the measured responsiveness to the theory's ‖δ_π‖.**
The paper measures TV distance between mean distributions; the theory bounds via logit
displacement. Add the formal link (TV ≤ ½‖δ‖∞-type / Pinsker-style inequality) so the
measured quantity provably lower-bounds the theoretical term.

**D3. Crossover condition.**
Derive the inequality stating when a responsiveness rise beats a decisiveness drop
(Δbias > 0 iff Δlog‖δ_π‖ > −Δlog√Var). Check each of the 13 families against it —
a per-family theory test, not just a pooled correlation.

## Part E — Presentation

1. **Concept figure** (new Fig. 1): schematic of the decomposition — score = mean of a
   distribution; two arrows (sharpening ↓variance, tuning ↑responsiveness); bias =
   product. Top papers open with this.
2. Abstract: add evidence scale ("26 checkpoints, 65 model×probe cells, 13,000
   per-item scores").
3. Terminology audit: pick one term per concept (bias *type* / probe / variant;
   family / checkpoint / model) and use it everywhere.
4. Positioning table: add a "Scale" column (models' size range) — strengthens the row
   contrast.
5. Venue versions: current generic `article` → prepare `acl` (for ACL SRW) and
   `neurips` (for NeurIPS HS) branches of the tex. Content unchanged.
6. Proofread pass: en-dashes in ranges, `\citet` vs `\citep`, spacing around math.

## Part F — Process & credibility (institute-level hygiene)

1. **USER ACTIONS (blocking, security):** revoke both Kaggle tokens pasted in chat;
   retract Zenodo DOI 10.5281/zenodo.21361920; withdraw any prior submission of the
   fabricated version; push `honest-rewrite` to the public repo.
2. **Numbers-match CI**: a GitHub Action that runs the analyze scripts on the committed
   JSONs and diffs the generated tables against the committed ones. Any drift fails the
   build. This is the strongest possible reproducibility signal and directly supports
   the integrity narrative.
3. Pin the environment: `requirements.txt` with exact versions + the Kaggle kernel
   preamble documented (torch 2.6.0+cu124, transformers 4.49.0).
4. arXiv preprint (cs.CL needs endorsement — a teacher/mentor with an arXiv record can
   endorse); then the venue submission cites the arXiv version.
5. External read-through by one senior person (teacher, professor, or an open-review
   community like ML Collective) before submission.
6. Camera-ready checklist: acknowledgments, compute statement (already have),
   license table for the 13 model families.

## Status update (2026-07-19, evening pass)

DONE since the morning review: B1 (within-checkpoint + LMM; found and reported the
within-judge entropy null and the within-judge responsiveness ρ=+0.64), B2 (clustered
bootstrap; predictor downgraded to rank signal), B3 (leave-one-family/vendor/size),
B4 (EV/flip concordance ρ=0.56), C2 (stage ablation, preregistered P7–P9: SFT installs
the responsiveness 84–99%, preference tuning the confidence), C5 (Dolly-15k public-items
replication: 7/8 families, ρ=−0.44), C8 (template ensembling −22%), D1 (cumulant
appendix), D2 (TV→logit-displacement lemma), D3 (per-cell test, 75% sign accuracy),
E1 (concept figure), E2 (evidence scale), E3 (terminology), F2 (numbers-match CI),
F3 (pinned requirements). Paper: 18 pages, clean build, CI-verified reproduction.

REMAINING: C1 frontier judges (needs user API key), C3 human gold validation (needs
humans), C7 circuit-level patching (beyond span-patching), E5 venue-format branches,
F1 (user: tokens/Zenodo/push), F4-F5 (arXiv, external reader).

## Second status update (2026-07-19, night pass)

Additionally DONE: exact sign-flip permutation (p=0.00098), 12-spec robustness sweep
(argmax boundary found + reported), forest plot, split-half reliability 0.99, bound
tightness 0.45x, explicit cumulant series, notation + compute-disclosure appendices,
Broader Impact, README rewrite, REBUTTAL_FAQ.md (14 objections), variant-level
decomposition (verbosity 99% padded; authority 2:1 novice-punishment), cross-dataset
synthesis (26/30 positive, +0.23), D1-exact series appendix, CI-gate bug found+fixed.

PREREGISTRATION SCOREBOARD (FINAL, all 20 adjudicated 2026-07-19/20):
CONFIRMED: P1 sharpening; P3 patching; P4 generality; P7 SFT installs
responsiveness (84-99%); P8 preference tuning sharpens; P10a sycophancy
(largest effect, +0.46); P11 Chinese (4/4); P13a authority span-encoding
(layers 3-14); P15a entropy-bias across 10 templates (rho=-0.51, n=180);
P17 range scaling (both clauses); P18 readout robustness (rho=0.79, mass
question closed); P19a chat-template control (bias survives, often larger).
FAILED (reported): P2 original sign prediction (the paper's central inversion);
P10b anchoring (+equivalence-bounded); P13b exemplar span-locality; P14 dose
monotonicity + slopes (step function found); P16 both clauses (corrected our
own confound framing); P15b tiny-scale per-template direction.
SCOPED/MARGINAL: P5 predictor (rank signal only); P9 7/8; P12 met nominally,
attenuated at 14B; P19b/c underpowered/mixed.
P20 frontier (OpenRouter logprobs, <$2): (a) CONFIRMED — GPT-4o-mini/GPT-4o/
Llama-70B biased on 5/5 probes, largest biases in study; (b) failed within-trio
(n=3) but pooled law STRENGTHENS to rho=-0.45 (n=145); (c) FAILED — deployed
judges MORE biased than small open models; Qwen-72B unobtainable (no logprob
provider). 32B: OOM on P100, dead. Queue empty; program complete; main merged;
tags v2.0-honest + v2.1-frontier.

## Priority order (if time is short)

1. C1 frontier judges — converts the biggest weakness into a headline.
2. B1–B3 clustered stats + sensitivity — makes the core numbers referee-proof.
3. C2 stage ablation — the most novel single addition available.
4. C3 human gold + C5 public items — cheap objection-removal.
5. D2–D3 — closes the theory–measurement gap.
6. E1 concept figure + venue formatting.
7. Everything else.
