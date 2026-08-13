# Submission checklist — Confidence Is Not Robustness

Describes `paper/honest/scoring_bias_v2.tex`, the corrected paper. The previous
version of this file described the retracted one — 20 figures, 10 tables, 286
references, "47 models, 41 complete" — and had every box ticked including items
that were never done. It is kept at
[`RETRACTED/legacy/paper_planning/`](../RETRACTED/legacy/paper_planning/) as part
of the record.

Counts below are checked against the paper by
`tests/test_the_submission_checklist_describes_this_paper.py`, so a box cannot
quietly outlive what it describes.

## Manuscript

- [x] Title and abstract accurately describe the work
- [x] Keywords present
- [x] Code availability statement with the GitHub URL
- [x] Ethics and broader-impact section (§10)
- [x] Competing interests declared
- [x] Preregistration status noted — twenty predictions, git-timestamped before
      their data existed, in `paper/honest/PREREGISTRATION.md`
- [x] Retraction of the prior version stated in the abstract, not only in an
      appendix
- [ ] **Author information complete.** `CITATION.cff` carries name and
      affiliation; no ORCID is set. Adding one is the author's own action — an
      ORCID identifies a person and cannot be minted on their behalf.

## Structure

- [x] Introduction with the problem statement and research questions
- [x] Related work with a positioning table
- [x] Method with full reproduction details (§3)
- [x] Results: 10 figures and 5 tables
- [x] Discussion with the theoretical interpretation
- [x] Limitations: 10 items (§7)
- [x] Conclusion
- [x] Reproducibility section naming every analyzer (§9)
- [x] References: 28 entries in `honest.bib`

## Figures and tables

- [x] Every figure included by the paper is present and regenerates from
      committed data — `repro/check_figures.py` compares the text drawn into
      each vector PDF against the current analysis
- [x] Every figure and table has a caption and is referenced in the text
- [x] No undefined `\ref{}` or `\label{}` — the archive build reports
      `undefined=0 overfull=0 missing=0`

## Data and code

- [x] All analysis code in the repository, CPU-only under `paper/honest/repro/`
- [x] All raw data committed, so no GPU and no API access is needed to
      reproduce any derived number
- [x] Reproduction pipeline documented (`ENVIRONMENT.md`)
- [x] Dockerfile and `docker-compose.yml` build and run the analysis
- [x] Seven raw files declare a panel size nothing in the release can verify,
      and that is disclosed rather than left implicit (`ENVIRONMENT.md`)
- [ ] **Zenodo DOI for this version.** The repository cites earlier deposits;
      minting a DOI for the corrected paper is the author's own action.

## Verification

- [x] `verify_like_ci.py` passes 8/8 locally, including regenerating every
      analysis and diffing the derived numbers against the committed ones
- [x] Full suite green
- [x] Every registered guard fails when its subject is mutated
      (`mutation_check.py`)
- [ ] **A green run on GitHub's own runners.** The local gate runs what CI runs;
      it is not the same as CI having run it.

## arXiv

- [x] `paper/honest/arxiv_submission/` holds the complete source, bundled
      figures, and bibliography
- [x] The archive rebuilds from the current paper rather than shipping a stale
      copy — a staleness guard compares it against the live source
- [ ] **Withdraw or replace the on-hold submission.** The earlier submission
      predates the retraction; check the on-hold PDF for the fabricated
      per-domain table before doing anything else, and do not resubmit from the
      old tarball. The author's action.
- [ ] **arXiv identifier, endorsement, categories, and licence.** The author's
      actions.

## Not claimed

- No human raters or human-gold labels were collected; the gold-standard
  analysis uses the released derived scores.
- No frontier base checkpoints exist publicly, so no causal base-vs-instruct
  contrast is possible at the frontier, and none is claimed.
