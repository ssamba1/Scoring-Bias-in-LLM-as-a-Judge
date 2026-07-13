# Ultimate Publication Requirements Checklist

## Study 1: Root Cause of Scoring Bias in LLM-as-a-Judge

---

## Part A: NeurIPS Paper Checklist (16 questions)
*Required for ALL NeurIPS submissions. Desk rejection if missing.*

| # | Question | Our Status | Evidence Needed |
|---|----------|-----------|-----------------|
| 1 | **Claims**: Do main claims match results? | ✅ Yes | Abstract: "instruction tuning has differential effects" — supported by data |
| 2 | **Limitations**: Separate limitations section? | ✅ Yes | In study1_standalone.tex (section 6) |
| 3 | **Theory/Proofs**: Assumptions stated? | ⚠️ Partial | We have informal IIAR hypothesis, no formal theorem (like monograph.tex) |
| 4 | **Reproducibility**: Steps to reproduce? | ✅ Yes | Complete Docker, Kaggle notebook, seed fixed, temperature 0 |
| 5 | **Open data/code**: URL or supplement? | ✅ Yes | github.com/ssamba1/research-draft |
| 6 | **Experimental details**: Hyperparameters, splits? | ✅ Yes | Temperature 0, 3 repeats, 50 items, 3 variants per probe |
| 7 | **Statistical significance**: Error bars, CIs, tests? | ⚠️ Partial | Bootstrap CIs, Cohen's d. Need: paired t-tests, Standard Error bars on ALL figures |
| 8 | **Compute resources**: GPU type, hours, memory? | ✅ Yes | T4 GPU, ~6 hours total, 17GB VRAM |
| 9 | **Code of ethics**: Conform to NeurIPS ethics? | ✅ Yes | No human subjects, open data — no concerns |
| 10 | **Broader impact**: Societal consequences? | ❌ Missing | Need 1 paragraph on how biased AI judges affect real-world evaluation |
| 11 | **Safeguards**: Malicious use prevention? | ❌ Missing | Need: discussion of how findings could be used to manipulate evaluations |
| 12 | **Licenses**: For all assets (code, data, models)? | ⚠️ Partial | MIT license for code. Need: model licenses (Llama3, Mistral, Gemma) |
| 13 | **New assets**: Documentation for new datasets/models? | ✅ No | We use existing models, no new datasets released |
| 14 | **Human subjects**: Instructions, compensation? | ✅ N/A | No human subjects |
| 15 | **IRB approval**: Ethics board review? | ✅ N/A | No human subjects |
| 16 | **LLM usage declaration**: Used LLMs in core method? | ⚠️ Need | We use LLMs as JUDGES (core method). Need declaration statement |

**NeurIPS score: 11/16 ✅, 3/16 ❌, 2/16 Partial**

---

## Part B: ISEF Judging Criteria (Science projects)
*Maximum 100 points. Creativity & Presentation = 55/100 points.*

### I. Research Question (10 pts)
| Sub-criterion | Our Status | Score |
|--------------|-----------|-------|
| Clear and focused purpose | ✅ "Where does scoring bias come from? Base vs instruct" | 4/4 |
| Identifies contribution to field | ✅ "First to compare base vs instruct for scoring bias" | 3/3 |
| Testable using scientific methods | ✅ Controlled perturbed-prompt experiment | 3/3 |
| **Total** | | **10/10** |

### II. Design & Methodology (15 pts)
| Sub-criterion | Our Status | Score |
|--------------|-----------|-------|
| Well-designed plan and data collection | ✅ 3 probes × 3 variants × 50 items × 3 repeats | 7/8 |
| Variables and controls defined | ✅ Control = unperturbed prompt, Var = biased prompt | 6/7 |
| **Total** | | **13/15** |
| **Gap**: Need explicit description of controlled variables | | -2 |

### III. Execution: Data Collection & Analysis (20 pts)
| Sub-criterion | Our Status | Score |
|--------------|-----------|-------|
| Systematic data collection | ✅ All automated via HuggingFace pipeline | 6/7 |
| Reproducibility of results | ✅ Kaggle notebook, seed fixed, temperature 0 | 5/6 |
| Appropriate statistical methods | ⚠️ Bootstrap CIs done. **Need: paired t-tests, ANOVA for probe×variant interaction** | 4/7 |
| Sufficient data | ⚠️ 50 items × 3 repeats = 150 per condition. Li et al. used 2,780. **Need: 100+ items** | 4/5 |
| **Total** | | **19/25** → scaled to **15/20** |

### IV. Creativity & Potential Impact (20 pts)
| Sub-criterion | Our Status | Score |
|--------------|-----------|-------|
| Significant creativity | ✅ First base-vs-instruct comparison for scoring bias | 9/10 |
| Impact/potential impact | ✅ Direct implications for AI evaluation fairness | 10/10 |
| **Total** | | **19/20** |

### V. Presentation (35 pts)
| Sub-criterion | Our Status | Score |
|--------------|-----------|-------|
| **Poster (10 pts):** Logical organization | ✅ Study1_standalone.tex is well-structured | 4/4 |
| Clarity of graphics | ⚠️ Need publication-quality figures (done in HTML, need for poster) | 3/4 |
| Supporting documentation | ✅ Complete GitHub repo | 2/2 |
| **Interview (25 pts):** Clear responses | ⚠️ Practice needed (student-dependent) | — |
| Understanding of basic science | ✅ Students can explain LLM scoring bias | 5/5 |
| Understanding limitations | ✅ Limitations section in paper | 5/5 |
| Degree of independence | ✅ All work done independently | 5/5 |
| Recognition of potential impact | ✅ Covered in paper | 5/5 |
| Ideas for further research | ✅ Future work in paper | 5/5 |
| **Total** | | **29/35** |

### ISEF Total Estimate: 85/100 (Strong)
- Typical winning ISEF score: 90-95/100
- **Gaps**: Statistical rigor (-2), more data (-1), figures (-1), presentation practice (-variable)

---

## Part C: ARR Responsible NLP Research Checklist (ACL Rolling Review)
*Required for ACL/EMNLP/NAACL submissions.*

| # | Question | Status |
|---|----------|--------|
| 1 | Papers with no strong empirical results? | ✅ We have real data |
| 2 | All used artifacts cited? | ⚠️ Need: full model citations with version numbers |
| 3 | Computational efficiency discussed? | ❌ Missing: cost per experiment, environmental impact |
| 4 | Risks/harms considered? | ❌ Missing: potential for findings to undermine trust in AI evaluation |
| 5 | Ethical considerations of data? | ✅ N/A (no human data) |
| 6 | Limitations clearly stated? | ✅ Yes, in paper |
| 7 | Societal impact considered? | ⚠️ Partial, needs expansion |

---

## Part D: ICML/NeurIPS Reproducibility Standards

| Requirement | Our Status |
|------------|-----------|
| **Exact code** | ✅ GitHub repo with all scripts |
| **Exact hyperparameters** | ✅ Temperature=0, seed=42, repeats=3, max_length=1024 |
| **Hardware specs** | ✅ T4 GPU, 17GB VRAM, ~6 hours |
| **Dependency versions** | ⚠️ Need: requirements.txt with exact versions (transformers, torch, etc.) |
| **Random seeds** | ⚠️ Only seed 42. Need: multi-seed analysis (42, 123, 456) |
| **Data splits** | ⚠️ Need: cross-validation or multiple item subsets |
| **Training curves** | ✅ N/A (inference-only) |
| **Evaluation protocol** | ✅ Complete, documented in notebook |
| **Raw predictions** | ❌ Missing: should release per-item scores, not just aggregates |
| **Error bars** | ⚠️ Partial: bootstrap CIs on summary stats. **Need: per-condition error bars** |

---

## Part E: Comprehensive Gap Analysis — What We MUST Do

### Critical (blocks submission)

| # | Gap | Current | Fix | Effort |
|---|-----|---------|-----|--------|
| C1 | **Statistical significance tests** | Bootstrap only | Add paired t-tests: base vs instruct for each probe. Add 2-way ANOVA: probe × variant interaction | 2 hours |
| C2 | **More evaluation items** | 50 items | Generate 100 items (template + diversity), re-run on Kaggle T4 (2 hours GPU) | 3 hours total |
| C3 | **Raw per-item scores** | Not released | Save per-item scores in JSON, upload to repo | 1 hour |
| C4 | **Dependency version lock** | No requirements.txt | `pip freeze > requirements.txt` with exact versions | 10 min |

### Important (significantly strengthens)

| # | Gap | Current | Fix | Effort |
|---|-----|---------|-----|--------|
| I1 | **Broken descriptive probe** | Excluded from analysis | Fix parser in Kaggle notebook (already done in code), re-run | Already in Kaggle notebook |
| I2 | **Multi-seed analysis** | Single seed 42 | Run with seeds 42, 123, 456 across 3 runs. Check if results hold | 3× GPU time (6 hours) |
| I3 | **Per-domain breakdown** | Not computed | Compute bias per item domain (science, tech, humanities, daily, math) | 1 hour |
| I4 | **Figure quality** | HTML-only | Generate vector PDF figures (matplotlib) | 3 hours |
| I5 | **Broader impact statement** | Missing | Write 1 paragraph on societal implications | 30 min |
| I6 | **Model license documentation** | Missing | Document licenses for Llama3 (Community License), Mistral (Apache 2.0), Gemma (Gemma Terms) | 30 min |

### Nice-to-Have (differentiates for ISEF)

| # | Gap | Current | Fix | Effort |
|---|-----|---------|-----|--------|
| N1 | **Large model validation** | 7B-8B only | Run one 70B model on subset of items (API cost ~$3) | $3 + 1 hour |
| N2 | **Human baseline** | No human comparison | Ask 5 people to score 20 items each, compare LLM vs human flip rates | 2 hours |
| N3 | **Error pattern analysis** | Not done | Which items trigger most bias? Which probe variants are most disruptive? | 2 hours |
| N4 | **Calibration curves** | Not done | Plot predicted score vs actual score for each probe variant | 1 hour |
| N5 | **Video demonstration** | Not created | Record 3-min screen capture showing bias discovery in real time | 1 hour |

---

## Part F: Final Roadmap to Submission

### Phase 1: Immediate Fixes (2-3 hours)
```
□ Add paired t-tests to analysis (fix_study1.py)        [1 hr]
□ Generate requirements.txt with exact versions          [10 min]
□ Release per-item raw scores as JSON                    [30 min]
□ Add broader impact + safeguards sections to paper      [30 min]
□ Add model license citations                            [30 min]
```

### Phase 2: Kaggle Re-run (3-4 hours GPU)
```
□ Update notebook: 100 items, fixed parser, seed sweep
□ Run on Kaggle T4: ~4 hours
□ Download results, update all analysis
```

### Phase 3: Polish (2-3 hours)
```
□ Generate vector publication figures (matplotlib PDFs)
□ Compute per-domain bias breakdown
□ Add error pattern analysis
□ Update paper with all new results
```

### Phase 4: Submission (1 hour)
```
□ Fill NeurIPS paper checklist
□ Write ISEF abstract (250 words)
□ Prepare poster (12 slides → 1 poster)
□ Submit to arXiv (free, immediate)
□ Submit to ISEF (deadline dependent)
```

**Total remaining work: ~10-12 hours + 4 hours GPU = ~14-16 hours for submission-ready**
