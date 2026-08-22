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
- [x] Results: 11 figures and 5 tables
- [x] Discussion with the theoretical interpretation
- [x] Limitations: 10 items (§7)
- [x] Conclusion
- [x] Reproducibility section naming every analyzer (§9)
- [x] References: 28 entries in `honest.bib`

## Figures and tables

- [x] Every figure included by the paper is present and regenerates from
      committed data — `paper/honest/repro/check_figures.py` compares the text drawn into
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
- [x] **Public metadata outside the repository matches the study.** Checked
      2026-08-21 with `gh repo view`. It did not: the GitHub description still
      advertised "31 model variants, 3 perturbation probes, 40,500+ judgments" --
      the retracted landscape figures, on the first line anyone reads, in search
      results and link previews. Corrected to the current panel. Topics and
      homepage are empty; there are no GitHub Releases; the issue and PR
      templates carry no study figures.

      No test can reach this. It lives outside the repository, so it is checked
      here rather than guarded:

          gh repo view <owner>/<repo> --json description,homepageUrl,repositoryTopics

      The same question applies to the Zenodo record's own title and description
      once a new version is minted -- deposit metadata is a separate surface from
      the files in the deposit.

- [ ] **Zenodo DOI for this version -- BLOCKING, and verified stale.** The paper
      states, present tense, that "the repository snapshot, paper, and all raw
      data are archived at DOI 10.5281/zenodo.21499823". That record is v2.1.0,
      published 2026-07-22. Its PDF was downloaded and checked on 2026-08-20: it
      still carries d_z=1.44, 24/26, sign accuracy 75%, responsiveness 0.14->0.26
      and rho=+0.64 -- every figure the score-ordering correction changed. A
      referee following that DOI gets the paper with the errors in it, which is
      the worst possible surface for this project to be wrong on.
      Mint a new version and update the DOI in the paper, README and CITATION.cff
      before submitting, or cite the concept DOI 10.5281/zenodo.21499822, which
      always resolves to the newest version. Minting is the author's own action.

      The edit either side of minting is scripted, because eight files name the
      DOI and README names it five times:

          python release_doi.py bundle                    # files to upload
          python release_doi.py set-doi 10.5281/zenodo.<new>
          python paper/honest/arxiv_package.py && python -m pytest tests/ -q

      Rehearsed end to end on a throwaway clone: the swap touches eight files,
      leaves the concept DOI and the retracted deposit's ID alone, and the suite
      passes afterwards with this item's guard standing down by itself.

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
- [x] `paper/honest/ARXIV_ABSTRACT.txt` is the abstract to paste into the
      submission form. The paper's own abstract is 3,184 characters against
      arXiv's 1,920-character metadata field, and arXiv truncates from the end
      rather than refusing it -- which would silently drop the ground-truth
      result, the mitigation figure, the frontier-judge finding, and last of
      all the sentence disclosing the prior fabricated version. Do not paste
      the abstract out of the PDF.
- [ ] **arXiv identifier, endorsement, categories, and licence.** The author's
      actions.

## Not claimed

- No human raters or human-gold labels were collected; the gold-standard
  analysis uses the released derived scores.
- No frontier base checkpoints exist publicly, so no causal base-vs-instruct
  contrast is possible at the frontier, and none is claimed.
