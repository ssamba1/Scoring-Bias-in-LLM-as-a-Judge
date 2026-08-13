# Pre-retraction paper documents

Nine documents that sat in `paper/` until 2026-08-13. All date from 2026-07-15,
before the fabrication was found, and nothing in the live tree referenced any of
them. They are moved rather than deleted because they are part of the record of
what this project was.

None of them contains the fabricated material itself — the live-tree sweep in
`tests/` covers every tracked file and passes — but several assert things the
corrected paper does not support, and two are directly superseded by honest
replacements they sat beside.

| File | What it is | Why it is not live |
| --- | --- | --- |
| `preregistration_statement.md` | A "Preregistration (Retrospective)" | Superseded by `paper/honest/PREREGISTRATION.md`, whose twenty predictions are git-timestamped before their data existed. A retrospective preregistration is not one, and in a project retracted for fabrication its presence beside a real one is actively misleading. |
| `preregistration_draft.md` | "Preregistration Draft — OSF-Style" for "Study 1", authored by "Author Name, Author Name" | The second non-authoritative preregistration to sit beside the real one. It names a different title and different research question from the paper that exists, and carries placeholder authorship that the fabrication sweep did not match — the sweep looks for "Student A, Student B". The authoritative preregistration is `paper/honest/PREREGISTRATION.md`. |
| `rebuttals.md` | Anticipated reviewer questions for the retracted study | Superseded by `paper/honest/REBUTTAL_FAQ.md`. Its answers contradict the corrected paper: it argues base models are "inherently bias-free with respect to surface form" and that their format-following failure *is* the mechanism, where P16 re-scoped the parse-failure confound to protocol-dependent and the frontier results show large biases in deployed judges. |
| `reviewer_response.md` | Response template for "Study 1" | Same era, same study, no longer the paper being defended. |
| `after_arxiv_plan.md` | "Path to S-Tier (NeurIPS/ACL Level)" | Planning for a submission that was retracted. |
| `ceiling_plan.md` | "Everything Buildable Right Now" | Same. |
| `s_tier_no_humans.md` | "Current: ~7.5/10, Target: 10/10" | Planning framed around a venue score rather than a result. |
| `depth_theory.md` | A Python script named `.md` | Never imported or run by anything; not a document. |
| `software_and_data.md` | Software versions and data description | Superseded by `paper/honest/repro/ENVIRONMENT.md` and `README.md`, which are checked against the environment that actually ran. |
| `paper_biasinteraction_compiled.md` | A compiled draft of the bias-interaction paper | A different project's paper. `paper/paper_biasinteraction.md` remains in the live tree because the agent instructions reference it. |
| `supplementary.md` | "Supplementary Materials" for the retracted multi-study write-up | Describes Study 2 — a full-factorial design over 400 items judged by five frontier models — which is not this paper's design, and opens by pointing at `literature_audit/bias_inventory.md`, a path quarantined in an earlier pass. The corrected paper's appendices are in the paper itself. |
| `submission_checklist.md` | The retracted paper's checklist | Claimed 20 figures, 10 tables, 286 references and "47 models, 41 complete" against a paper with 10 figures, 5 tables and 28 references, with every box ticked including ones nobody had done. Replaced by an honest `paper/submission_checklist.md` whose counts are recomputed from the paper. |

Nothing here should be cited, reused, or treated as describing the current
study. For that, see [`paper/honest/`](../../../paper/honest/).
