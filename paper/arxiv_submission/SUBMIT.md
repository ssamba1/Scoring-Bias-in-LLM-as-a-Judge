# arXiv Submission Guide

## Files to Upload

Go to https://arxiv.org/submit and upload these files:

1. **`main.tex`** — Full manuscript (rename `camera_ready_full.tex`)
2. **`references.bib`** — Bibliography (16 entries)

arXiv's system will compile them automatically — they have LaTeX installed.

## Metadata Fields to Fill

| Field | Value |
|-------|-------|
| Title | Scoring Bias in LLM-as-a-Judge Models: A 22-Model Landscape with Base-Instruct Comparison |
| Authors | Sricharan Samba |
| Primary category | cs.CL (Computation and Language) |
| Secondary category | cs.AI, cs.LG |
| Abstract | (Paste from `main.tex`) |
| Comments | 20 pages, 3 tables, 2 figures. Code: https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge |

## After Submission

- arXiv will email you a confirmation link
- The paper goes live ~24 hours later
- You'll get an arXiv ID (e.g., 2607.12345)
- Add the arXiv ID to `paper/camera_ready_full.tex` line 13 (replace `arXiv:2607.xxxxx`)
- Push the updated paper to GitHub

## Zenodo DOI Already Set

DOI: **10.5281/zenodo.21361920**

Already included in the paper's Data Availability section.

## What the Paper Contains

- 22 instruct-tuned models (OpenRouter bias landscape)
- 8 base-instruct family pairs (differential effect)
- IIAR hypothesis (tested: not supported at 0.5B)
- 6 quantified limitations
- Full reproducible pipeline ($0 cost)

## After Publishing (v2 Ideas)

1. Run human baseline (3 raters, 50 items, 1 hour)
2. Domain analysis (already have the code)
3. Attention analysis at 3B+ scale
4. Add 5 more families via bitandbytes fix
