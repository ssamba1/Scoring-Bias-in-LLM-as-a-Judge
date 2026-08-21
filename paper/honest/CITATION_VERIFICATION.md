# Citation verification

Checked 2026-08-21 against primary sources: the arXiv API
(`export.arxiv.org/api/query?id_list=...`) for every entry carrying an arXiv
identifier, and the publisher's own page for the two that do not.

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

**Result: 26 arXiv identifiers, all resolving, every title and first
author matching the entry. Two further entries cite a publisher page rather
than a preprint and were checked by hand. No phantoms, no misattributions.**

## arXiv entries

| key | arXiv | title as arXiv reports it | first author |
|---|---|---|---|
| `bai2022constitutional` | 2212.08073 | Constitutional AI: Harmlessness from AI Feedback | Bai |
| `chen2024humans` | 2402.10669 | Humans or LLMs as the Judge? A Study on Judgement Biases | Chen |
| `gemma2` | 2408.00118 | Gemma 2: Improving Open Language Models at a Practical Size | Gemma Team |
| `gu2024survey` | 2411.15594 | A Survey on LLM-as-a-Judge | Gu |
| `guo2017calibration` | 1706.04599 | On Calibration of Modern Neural Networks | Guo |
| `kadavath2022know` | 2207.05221 | Language Models (Mostly) Know What They Know | Kadavath |
| `lee2025correctly` | 2511.21140 | How to Correctly Report LLM-as-a-Judge Evaluations | Lee |
| `li2025scoring` | 2506.22316 | Evaluating Scoring Bias in LLM-as-a-Judge | Li |
| `liu2023geval` | 2303.16634 | G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment | Liu |
| `llama3` | 2407.21783 | The Llama 3 Herd of Models | Grattafiori |
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
| `ye2024justice` | 2410.02736 | Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge | Ye |
| `zheng2023judging` | 2306.05685 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Zheng |

## Entries citing a publisher page

| key | source | checked |
|---|---|---|
| `falcon3` | `huggingface.co/blog/falcon3` | Page exists: "Welcome to the Falcon 3 Family of Open Models!", Technology Innovation Institute, December 2024. No arXiv report exists for Falcon 3. |
| `granite3` | `github.com/ibm-granite/granite-3.0-language-models/` | Repository exists and publishes its own recommended citation, which is the entry used here: title, author `{Granite Team, IBM}`, October 2024. |

## Note on corporate authors

Five model reports are cited by their corporate author -- Meta AI, Gemma Team,
Qwen Team, OLMo Team, Falcon-LLM Team, Granite Team -- rather than by the first
individual on the author list. arXiv lists Grattafiori et al. for Llama 3, for
instance. This is the usual convention for model reports and is applied
consistently across all of them; it is recorded here so the difference from the
arXiv metadata is not later mistaken for an error.

