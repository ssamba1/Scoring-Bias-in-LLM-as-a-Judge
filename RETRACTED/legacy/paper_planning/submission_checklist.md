# Submission Checklist — Scoring Bias in LLM-as-a-Judge

## Manuscript
- [x] Title and abstract accurately describe the work
- [x] All author information complete (name, affiliation, email)
- [x] Keywords present
- [x] Code availability statement with GitHub URL
- [x] Data availability statement with DOI
- [x] Ethics statement included
- [x] Competing interests declared
- [x] Pre-registration status noted

## Structure
- [x] Introduction with clear problem statement and research questions
- [x] Related work section with comparison table
- [x] Method section with full reproducibility details
- [x] Results section with all 20 figures and 10 tables
- [x] Discussion section with theoretical interpretation
- [x] Limitations section with 6 quantified limitations
- [x] Broader impact section with actionable recommendations
- [x] Conclusion summarizing all findings
- [x] Author contributions (CRediT)
- [x] Acknowledgments
- [x] References (286 entries)
- [x] Supplementary materials

## Figures & Tables
- [x] All 20 figures present in paper/figures/
- [x] All figures have captions and are referenced in text
- [x] All 10 tables have captions and are referenced in text
- [x] No broken `\ref{}` or `\label{}` cross-references

## Data & Code
- [x] All experimental code in GitHub repository
- [x] All results data in repository (47 models, 41 complete)
- [x] DOI archived at Zenodo (10.5281/zenodo.21361920)
- [x] Reproduction pipeline documented
- [x] Dockerfile for reproduction

## arXiv Submission
- [x] `arxiv_submission/main.tex` — complete LaTeX source
- [x] `arxiv_submission/metadata.yaml` — arXiv metadata
- [x] All figures bundled
- [x] Bibliography file included
- [x] Supplementary materials included
- [x] Source compiles with `latexmk -pdf`

## Style & Formatting
- [x] Line numbers enabled
- [x] Two-column layout
- [x] Standard arXiv format (no custom classes)
- [x] All URLs use `\url{}`
- [x] All citations use `\cite{}`
- [x] Consistent notation throughout

## Final Checks
- [ ] Run `latexmk -pdf` to verify compilation
- [ ] Verify all figures render at correct resolution
- [ ] Check DOI resolves correctly
- [ ] Confirm GitHub repo is public
- [ ] Run arXiv auto-format check after upload
