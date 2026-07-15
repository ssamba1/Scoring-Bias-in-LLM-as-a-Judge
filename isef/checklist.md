# ISEF Competition Checklist

## Project: Scoring Bias in LLM-as-a-Judge Models

**Researcher:** Sricharan Samba
**Category:** Systems Software

---

### Required Forms & Documentation

- [x] **1. Research Plan Completed**
  - Completed in `research_plan.md`
  - Includes abstract, research question, methodology, bibliography, timeline, approvals

- [x] **2. Abstract Written (250 words max)**
  - Completed in `abstract.md`
  - 248 words, single paragraph
  - Includes title, purpose, procedure, data summary, conclusions
  - No citations included

- [x] **3. Project Summary Board Template**
  - Completed in `poster_template.md`
  - Content organized for 36×48 inch display board
  - Covers: title, introduction, methods, results, conclusions, future work
  - Designed for ISEF three-panel format

- [x] **4. Safety Review Completed**
  - Completed in `safety_form.md`
  - All ISEF safety categories checked and confirmed N/A
  - No hazardous materials, no human subjects, no animals
  - Qualifies for expedited/automated approval

- [x] **5. All Data Collected & Documented**
  - 24,300 judgments from base-instruct paired models (9 families)
  - 29,700 judgments from instruct-only models (22 models)
  - Total: 54,000 deterministic judgments at temperature 0
  - Data publicly available on GitHub
  - Per-model scores published in paper Table 3
  - Full item-level data in repository

- [x] **6. Code Repository Ready for Review**
  - GitHub: https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge
  - Complete reproduction pipeline (run_all.sh)
  - Docker setup for environment consistency
  - All random seeds fixed (42)
  - Test suite included
  - MIT licensed

- [x] **7. Paper Written and Formatted**
  - Complete camera-ready paper: 5 pages, single author
  - 31 model variants, 3 probes, 4 metrics
  - Covers related work, methodology, results, discussion, limitations
  - arXiv preprint available
  - DOI: 10.5281/zenodo.21361920

---

### Additional Preparation Items

- [ ] **Presentation slides prepared** — see `presentation_outline.md` for 5-minute outline
- [ ] **Q&A preparation** — anticipated questions included in presentation outline
- [ ] **Timeline documentation** — see `timeline.md`
- [ ] **Ethics statement** — see `safety_form.md`
- [ ] **Poster design finalized** — see `poster_template.md` for content layout
- [ ] **Judges' questions anticipated** — see presentation_outline.md Q&A prep
- [ ] **Code/data QR code generated** — include on poster for live demo access

---

### Notes for ISEF Submission

- **Category:** Systems Software — this is a pure computational project
- **No SRC/IRB pre-approval needed** — no human subjects, animals, or hazardous materials
- **Single researcher** — all work performed by Sricharan Samba
- **All materials open source** — judges can inspect every aspect of the methodology
- **Total project cost:** Under $3 USD (OpenRouter API only; Kaggle GPU was free educational tier)
