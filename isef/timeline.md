# Research Timeline

## Project: Scoring Bias in LLM-as-a-Judge Models

---

### Project Overview

**Start Date:** January 2026
**Current Date:** July 14, 2026
**Total Duration:** ~6 months
**Target Competition:** ISEF 2027

---

### Phase 1: Literature Review & Gap Identification

| Dates | Activities | Deliverables |
|-------|------------|--------------|
| Jan 2026 (Weeks 1–2) | Systematic literature review of LLM bias research | Read 60+ papers; built bias taxonomy |
| Jan 2026 (Weeks 3–4) | Identified open problems in LLM-as-a-Judge | Discovered Li et al. (2026) open question: "where does scoring bias come from?" |
| Feb 2026 (Week 1) | Formulated research questions and hypotheses | RQ1–RQ4 and H1–H4 specified |

**Milestone:** Gap identified (scoring bias root cause) — no prior work addressed this question ✓

---

### Phase 2: Experimental Design

| Dates | Activities | Deliverables |
|-------|------------|--------------|
| Feb 2026 (Weeks 2–3) | Designed perturbation framework based on Li et al. (2026) | 3 scoring bias probes (rubric order, score ID, reference answer) |
| Feb 2026 (Week 4) | Selected model families; designed item set | 50 items across 5 domains; 9 base-instruct pairs + 22 instruct models |
| Mar 2026 (Week 1) | Built inference pipeline; set up Kaggle environment | Python scripts for model inference, data collection, and analysis |

**Milestone:** Complete experimental protocol with 54,000 judgment capacity ✓

---

### Phase 3: Data Collection

| Dates | Activities | Deliverables |
|-------|------------|--------------|
| Mar 2026 (Weeks 2–3) | Primary data collection on Kaggle T4 GPU | 9 families × 2 variants × 3 probes × 3 variants × 50 items × 3 repeats = **24,300 judgments** |
| Mar 2026 (Week 4) | Supplementary data collection via OpenRouter API | 22 instruct-only models = **29,700 judgments** |
| Mar 2026 (Week 4) | Quality checks on collected data | Verified deterministic output (temperature 0); identified 5 excluded models (stop-token truncation) |

**Milestone:** 54,000 total judgments collected at cost under $3 ✓

---

### Phase 4: Analysis

| Dates | Activities | Deliverables |
|-------|------------|--------------|
| Apr 2026 (Weeks 1–2) | Statistical analysis | Calculated Δ, flip rate, Cohen's d, MAD for all probes and models |
| Apr 2026 (Week 2) | Alternative explanation testing | Tested and ruled out 4 competing hypotheses |
| Apr 2026 (Week 3) | Attention weight analysis (Qwen2.5-0.5B, Llama-3.2-3B) | Format Efficiency Hypothesis evidence |
| Apr 2026 (Week 3) | Cross-validation of results | Verified pattern consistency across model sizes and training methods |

**Milestone:** Core findings established — differential effect confirmed ✓

---

### Phase 5: Communication & Publication

| Dates | Activities | Deliverables |
|-------|------------|--------------|
| Apr–May 2026 (Weeks 4–6) | Paper writing | Camera-ready paper (5 pages, single author) |
| May 2026 (Week 1) | Figures and tables | 4 key tables (bias landscape, per-model, base-instruct comparison, alternative explanations) |
| May 2026 (Week 2) | Peer feedback and revisions | Addressed feedback; strengthened limitations section |
| Jun 2026 | Code and data release | GitHub repository with full reproduction pipeline |
| Jun 2026 | arXiv preprint and Zenodo archival | arXiv:2607.xxxxx; DOI: 10.5281/zenodo.21361920 |

**Milestone:** Full research package publicly available ✓

---

### Phase 6: Competition Preparation

| Dates | Activities | Deliverables |
|-------|------------|--------------|
| Jul 2026 (Weeks 1–2) | ISEF materials preparation | Abstract, research plan, project summary, safety form, poster template, presentation outline |
| Jul 2026 (Week 2) | Presentation rehearsal | 5-minute presentation timed and practiced |
| Jul–Aug 2026 (Ongoing) | Additional data collection | Adding more model families to increase statistical power (target: N ≥ 12) |

**Milestone:** ISEF application package complete ✓

---

### Future Plans (Through ISEF 2027)

| Dates | Activities | Target |
|-------|------------|--------|
| Aug–Oct 2026 | Expand to N ≥ 12 model families | Statistical significance at p < 0.05 |
| Oct–Dec 2026 | Develop and test mitigation strategies (multi-model ensembling, calibration) | Quantified bias reduction across models |
| Dec 2026–Feb 2027 | Cross-lingual evaluation | Test non-English scoring bias |
| Feb–Apr 2027 | Rehearse and refine presentation | ISEF 2027 finals |
| May 2027 | **ISEF 2027 Competition** | Present at Regeneron ISEF |

---

### Key ISEF Dates (2026–2027)

- **Now:** ISEF materials preparation
- **Fall 2026:** Regional/State fair registration (varies by region)
- **Winter 2026–2027:** Regional/State fairs
- **Spring 2027:** ISEF finalist selection
- **May 2027:** Regeneron ISEF 2027

---

### Computational Resources Used

| Resource | Purpose | Cost |
|----------|---------|------|
| Kaggle T4 GPU (free tier) | Primary model inference (local models) | $0 |
| OpenRouter API | Instruct-only model inference (22 models) | < $3 |
| Local CPU | Analysis, paper writing, attention extraction | $0 |
| **Total** | | **< $3 USD** |
