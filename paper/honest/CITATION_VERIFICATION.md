# Citation verification

Checked 2026-08-21, and again on 2026-09-07 for the five entries added that
day, against primary sources: the arXiv API
(`export.arxiv.org/api/query?id_list=...`) for every entry carrying an arXiv
identifier, Crossref for every DOI, and the publisher's own page for the two
that carry neither.

This exists because the offline guard in
`tests/test_citations_are_well_formed.py` says plainly what it cannot do: it
checks that every entry is *findable*, not that it is *real*, since proving
that needs the network and a test that passes silently when offline would be
worse than none. This file is the network half, recorded once so the offline
half can pin it. `tests/test_citations_match_the_verified_record.py` fails if
the bibliography stops matching what was verified.

It is not a formality here. A previous version of this bibliography cited
arXiv:2410.17703 for IBM Granite; that identifier belongs to "Schemes of
Associative Algebras", a math.AG paper. And the companion project shipped a
sentence in quotation marks attributed to a survey that does not contain it.
A resolving identifier and a correct one are different things.

**Result: 30 arXiv identifiers, all resolving, every title and first
author matching the entry. One further entry (`zahraei2026prior`) is a
proceedings paper with a DOI and no preprint, resolved through Crossref; two
more cite a publisher page rather than a preprint and were checked by hand.
No phantoms, no misattributions.**

## arXiv entries

| key | arXiv | title as arXiv reports it | first author |
|---|---|---|---|
| `chen2024humans` | 2402.10669 | Humans or LLMs as the Judge? A Study on Judgement Biases | Chen |
| `gu2024survey` | 2411.15594 | A Survey on LLM-as-a-Judge | Gu |
| `guo2017calibration` | 1706.04599 | On Calibration of Modern Neural Networks | Guo |
| `itzhak2024instructed` | 2308.00225 | Instructed to Bias: Instruction-Tuned Language Models Exhibit Emergent Cognitive Bias | Itzhak |
| `kadavath2022know` | 2207.05221 | Language Models (Mostly) Know What They Know | Kadavath |
| `kapetanovic2026anchoring` | 2608.25869 | Anchoring Bias in LLM-as-a-Judge Systems: Prior Scores Compromise Evaluation Independence | Kapetanovic |
| `lee2025correctly` | 2511.21140 | How to Correctly Report LLM-as-a-Judge Evaluations | Lee |
| `li2025scoring` | 2506.22316 | Evaluating Scoring Bias in LLM-as-a-Judge | Li |
| `liu2023geval` | 2303.16634 | G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment | Liu |
| `llama3` | 2407.21783 | The Llama 3 Herd of Models | Grattafiori |
| `norman2026reliability` | 2606.19544 | Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias | Norman |
| `olmo2` | 2501.00656 | 2 OLMo 2 Furious | OLMo Team |
| `pan2025user` | 2508.15815 | User-Assistant Bias in LLMs | Pan |
| `park2024offsetbias` | 2407.06551 | OffsetBias: Leveraging Debiased Data for Tuning Evaluators | Park |
| `qwen25` | 2412.15115 | Qwen2.5 Technical Report | Qwen Team |
| `saferluckier2025` | 2503.09347 | Safer or Luckier? LLMs as Safety Evaluators Are Not Robust to Artifacts | Chen |
| `shi2024position` | 2406.07791 | Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge | Shi |
| `smollm2` | 2502.02737 | SmolLM2: When Smol Goes Big - Data-Centric Training of a Small Language Model | Ben Allal |
| `soumik2026judging` | 2604.23178 | Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines | Soumik |
| `stablelm2` | 2402.17834 | Stable LM 2 1.6B Technical Report | Bellagente |
| `thakur2024judging` | 2406.12624 | Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges | Thakur |
| `tian2025overconfidence` | 2508.06225 | Overconfidence in LLM-as-a-Judge: Diagnosis and Confidence-Driven Solution | Tian |
| `trustjudge2025` | 2509.21117 | TrustJudge: Inconsistencies of LLM-as-a-Judge and How to Alleviate Them | Wang |
| `wang2023large` | 2305.17926 | Large Language Models are not Fair Evaluators | Wang |
| `wang2025judgmentdist` | 2503.03064 | Improving LLM-as-a-Judge Inference with the Judgment Distribution | Wang |
| `xu2026inside` | 2607.11871 | Inside the Unfair Judge: A Mechanistic Interpretability Account of LLM-as-Judge Bias | Xu |
| `ye2024justice` | 2410.02736 | Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge | Ye |
| `zheng2023judging` | 2306.05685 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Zheng |

## Entries citing a publisher page

| key | source | checked |
|---|---|---|
| `falcon3` | <https://huggingface.co/blog/falcon3> | Page exists: "Welcome to the Falcon 3 Family of Open Models!", Technology Innovation Institute, December 2024. No arXiv report exists for Falcon 3. |
| `granite3` | <https://github.com/ibm-granite/granite-3.0-language-models/> | Repository exists and publishes its own recommended citation, which is the entry used here: title, author `{Granite Team, IBM}`, October 2024. |

## Note on corporate authors

Five model reports are cited by their corporate author -- Meta AI, Gemma Team,
Qwen Team, OLMo Team, Falcon-LLM Team, Granite Team -- rather than by the first
individual on the author list. arXiv lists Grattafiori et al. for Llama 3, for
instance. This is the usual convention for model reports and is applied
consistently across all of them; it is recorded here so the difference from the
arXiv metadata is not later mistaken for an error.

## Characterizations of cited work

A resolving identifier says nothing about whether the sentence around it is
true. The verbs are where the unsupported claim hides: "introduced", "first",
"showed" are assertions about the literature, and a plural subject generalises a
result that may have been measured on one model. The companion project shipped
three defects of exactly this kind, and this paper has already corrected two of
its own (an inexact quotation of Li et al., and a mischaracterisation of Thakur
et al.'s design -- both recorded in `tests/test_quotation_integrity.py`).

Every remaining priority verb next to a citation was checked on 2026-08-21.

| claim in the paper | checked against | verdict |
|---|---|---|
| `liu2023geval` "introduced probability-weighted scores" | G-Eval body (ar5iv, 2303.16634) | Supported. Their scoring function is `score = sum_i p(s_i) * s_i`, presented as their own proposal to obtain "more fine-grained, continuous scores". |
| `wang2025judgmentdist` "show the distribution mean outperforms the mode across judging settings" | abstract, 2503.03064 | Supported, and close to verbatim: "taking the mean of the judgment distribution consistently outperforms taking the mode (i.e. greedy decoding) in all evaluation settings (i.e. pointwise, pairwise, and listwise)". |
| `li2025scoring` "introduced the three scoring biases and called for root-cause analysis" | 2506.22316 | Supported. They examine rubric order, score ID and reference answer, and their Limitations ask for the causes to be validated -- the sentence this paper quotes. |
| `thakur2024judging` "evaluated thirteen instruction-tuned judges on answers from both base and instruction-tuned exam-takers" | 2406.12624 | Supported. This is the corrected wording; the earlier version said they "found base and instruct judges differ", which reversed which side of their design the split is on. |

| `itzhak2024instructed` "compare pretrained against instruction-tuned and RLHF models ... and find a stronger presence of all three in the tuned models" | abstract, 2308.00225 | Supported, close to verbatim: "we find a stronger presence of biases in models that have undergone instruction tuning". The three biases named in the paper (decoy, certainty, belief bias) are the three the abstract names. |
| `norman2026reliability` "21 judges from nine providers over approximately 541,000 judgments ... test-retest reliability above 0.95 coexisting with position bias above 0.10" | abstract, 2606.19544 | Supported. "21 judges from nine providers", "approximately 541,000 individual judgments", and the consistency-bias paradox is their own term for ">0.95" reliability with ">0.10" position bias. |
| `xu2026inside` "biased inputs are displaced along a low-dimensional, type-specific subspace ... steering shifts scores in both directions ... a linear projection anticipates judge failures on unseen benchmarks" | abstract and HTML body, 2607.11871 | Supported. Judge count (7), bias-type count (7: prestige, verbosity, bandwagon, authority, sentiment, refinement, diversity) and benchmark count (9) all read from the paper; the judge names are deliberately not listed here, because one of them matches a pattern in `tests/fabricated_signatures.py` and a record file is not worth weakening that sweep for. It reports no training-stage comparison, no decomposition and no preregistration -- the three cells its row leaves empty. |
| `zahraei2026prior` "present at SFT, substantially amplified by DPO -- misinformation +2.44 -> +3.29, a 35% increase -- and neither resolved nor significantly worsened by RLVR (+3.14)" | Section 5.4 and Table 2 of the ACL PDF | Supported, and quoted from the section itself, not the project page. Table 2's misinformation T1 row reads 40.7% (+2.44) / 54.8% (+3.29) / 52.3% (+3.14). The causal claim in its table row is their model-organism experiment (Appendix C: fine-tuning on documents about a fictional person shifts ratings symmetrically), not the stage ladder. Judge count 15 taken from their main results figure. |
| `kapetanovic2026anchoring` "across 185,271 successful evaluations ... on seven of the eight models tested the bootstrap interval ... lies below zero, and Cohen's d reaches 0.71" | abstract, 2608.25869 | Supported, and this row records a defect caught in drafting: an earlier version wrote "|d| up to 0.71 on seven of eight models", which joins two separate results. Seven of eight is the count whose task-stratified bootstrap interval for the total anchored-metadata effect lies below zero; 0.71 is the maximum absolute Cohen's d. Likewise their threshold finding is reported as a suggestion from "selected model-task probes", and the paper says so rather than calling it a reproduction. |

No priority verb in the paper claims something its source does not.

## Second pass, 2026-09-07

Five entries were added in one pass: `itzhak2024instructed`,
`norman2026reliability`, `xu2026inside`, `zahraei2026prior` and
`kapetanovic2026anchoring`. All four arXiv identifiers were fetched from
`export.arxiv.org` in a single query and their titles, author lists and posting
dates compared to the entries; both new DOIs were resolved through Crossref;
`zahraei2026prior`'s stage numbers were read from the published PDF rather than
from the authors' project page, which states the same result in rounder terms.

Worth recording, because it is the same failure this file already documents in a
different costume: the drafting error in the `kapetanovic2026anchoring` row was
not a wrong identifier or a wrong paper. Every number in the sentence was real
and came from the right abstract. They were *joined wrongly* -- a count from one
result attached to an effect size from another. Nothing downstream could have
caught it: the entry is well-formed, the identifier resolves, the DOI is
absent-but-not-required, and the sentence reads fluently. Only rereading the
abstract against the sentence found it.
## DOIs

Checked 2026-08-21 against Crossref. Every entry carrying a DOI was resolved and
its metadata compared to the entry. **One was wrong.**

| key | DOI | resolves to | verdict |
|---|---|---|---|
| `itzhak2024instructed` | 10.1162/tacl_a_00673 | "Instructed to Bias: Instruction-Tuned Language Models Exhibit Emergent Cognitive Bias", Itay Itzhak, TACL 12, pp. 771-785, 2024 | correct |
| `li2025scoring` | 10.1007/978-981-92-0372-7_2 | "Evaluating Scoring Bias in LLM-as-a-Judge", Qingquan Li, LNCS / DASFAA 2026, pp. 19-34 | correct |
| `wang2023large` | 10.18653/v1/2024.acl-long.511 | "Large Language Models are not Fair Evaluators", Peiyi Wang, ACL 2024 | correct |
| `gu2024survey` | 10.1016/j.xinn.2025.101253 | "A survey on LLM-as-a-judge", Jiawei Gu, The Innovation 7(6), 2026 | **corrected** from 10.1016/j.xinn.2025.100456, which resolves at neither doi.org nor Crossref |
| `pan2025user` | 10.18653/v1/2026.findings-acl.449 | "User-Assistant Bias in LLMs", Xu Pan, Findings of ACL 2026 | correct |
| `zahraei2026prior` | 10.18653/v1/2026.findings-acl.2087 | "Prior Beliefs Prejudice LLM-as-Judge: Evidence from Persuasion Evaluation", Pardis Sadat Zahraei, Findings of ACL 2026, pp. 42049-42082 | correct |
| `park2024offsetbias` | 10.18653/v1/2024.findings-emnlp.57 | "OffsetBias: Leveraging Debiased Data for Tuning Evaluators", Junsoo Park, Findings of EMNLP 2024 | correct |

Two things this pass is worth recording beyond the fix.

**A DOI that does not resolve is invisible to every other check here.** The
arXiv identifier for that survey (2411.15594) is correct and was verified in the
pass above; the entry was well-formed; the paper compiled. Only resolving the
DOI itself found it. arXiv records no DOI for that preprint, so the published
version had to be located by title search.

**Read identifiers at full length.** A first pass printed the DOIs truncated to
28 characters, which cut `2024.acl-long.511` down to `2024.acl-long.51` -- and
that shorter string is itself a real DOI, belonging to Song et al.'s FineSurE.
Chasing it produced a confident and completely false report of a
wrong-paper citation. The bibliography was right; the display was not. Any
identifier check has to be done on the full string.
