# arXiv Submission Package

This package contains all files required for submission to arXiv.org.

## Required Files

| File | Description | Included |
|------|-------------|----------|
| `paper.tex` | LaTeX source of paper | ✅ Yes |
| `references.bib` | BibTeX bibliography | ✅ Yes |
| `figures/*.png` | Figures and diagrams | Pending (generated from pipeline) |
| `README.md` | Submission metadata | ✅ This file |

## Submitting

### Method 1: Manual (recommended for first-time submitters)
1. Go to https://arxiv.org/submit
2. Create or log in to your account
3. Upload `paper_neurips_style.tex` as the main file
4. Upload `references.bib` as auxiliary file
5. Upload figures as additional files
6. Complete the metadata form
7. Submit and wait for moderation (usually 1-2 business days)

### Method 2: Automated (using arXiv API)
Not recommended for first-time submitters.

## Licensing

- Code: MIT License (see LICENSE file)
- Paper text: CC-BY 4.0
- Data: CC-BY 4.0

## Submission Checklist

Before submitting, verify:

- [ ] Paper compiles with `pdflatex paper.tex` (twice for references)
- [ ] All figures are 300+ DPI and in correct format
- [ ] Author names match institutional affiliations
- [ ] Abstract is under 1920 characters
- [ ] No identifying information in the PDF metadata
- [ ] No references to unpublished work that isn't on arXiv
- [ ] ORCID iDs included for all authors
- [ ] All external dependencies (code, data) linked in paper

## Post-Submission

- Moderation typically takes 1-2 business days
- Once announced, the paper becomes arXiv:XXXX.XXXXX
- Link will be added to the README
