# ULTIMATE PUBLICATION REQUIREMENTS  10x DEPTH

## Section-by-Section Analysis of Top-Tier Papers vs Our Study 1

Based on exhaustive reading of: Li et al. (DASFAA 2026), Wang et al. (ACL 2024), Xu et al. (2026), Gao et al. (2025), NeurIPS/ACL/ICML checklists, ISEF judging criteria.

---

## 1. ABSTRACT (250 words max)

### What Top Papers Have
**Li et al.:** Problem → Gap → Method → 3 key findings → 3 contributions → code release
**Wang et al.:** Phenomenon → Evidence → Harm → 3 solutions → Human eval → Code release

### Our Status: ⚠️ 70%
| Requirement | Li et al. | Wang et al. | Us | Fix |
|------------|-----------|-------------|-----|-----|
| Problem statement | ✅ | ✅ | ✅ | - |
| Specific gap | ✅ | ✅ | ✅ | - |
| Method overview | ✅ | ✅ | ✅ | - |
| Quantitative results | ✅ 20-48% FR | ✅ 82.5% conflict | ✅ 44%/77%/35% | - |
| Number of judgments | ✅ 5,421 items | ✅ 80 examples | ✅ 8,100 judgments | - |
| **Significance statement** | ✅ | ✅ | ❌ | Add: "This is the first causal evidence that scoring bias is modulated by instruction tuning" |
| **Code/data release** | ✅ | ✅ | ❌ | Add: "All code and data are publicly available" |

---

## 2. INTRODUCTION (1-1.5 pages)

### What Top Papers Have
**Li et al.:** 6 paragraphs: (1) LLM-as-Judge importance, (2) existing biases, (3) gap in scoring bias, (4) practical motivation (financial advisor), (5) our approach, (6) contributions numbered
**Wang et al.:** 5 paragraphs: (1) evaluation problem, (2) LLMs as evaluators, (3) discovery of position bias, (4) proposed solution, (5) contributions + human annotation

### Our Status: ⚠️ 65%
| Element | Example from Li et al. | Us | Fix |
|---------|----------------------|-----|-----|
| **Practical motivation** | "financial advisory assistant  adding an in-context example shifted scores" | ❌ Missing | Add: concrete example of when scoring bias matters |
| **Explicit quote of gap** | "underlying causes remain to be validated" | ✅ We cite this | Done |
| **Numbered contributions** | 3 bullet points | ❌ Not in standalone paper | Add to study1_standalone.tex |
| **Comparison to prior work** | Detailed paragraph on what prior work missed | ✅ | Could add more citations |
| **Scope clarification** | "We shift focus from target biases to prompt biases" | ⚠️ Implicit | Make explicit |

---

## 3. RELATED WORK (1-2 pages)

### What Top Papers Have
**Li et al.:** §2.1 (LLM-as-Judge overview, 1 para) + §2.2 (Bias in LLM-as-Judge, 2 paras) = ~1 page
**Wang et al.:** §6.1 (LLM Evaluation, 1 para) + §6.2 (Bias in DNNs, 1 para) = ~0.5 page

### Our Status: ⚠️ 40%
| Missing component | Importance | Fix |
|------------------|------------|-----|
| **OffsetBias paper** (Park et al. 2024) | High  defines 6 bias types | Add 2-3 sentences |
| **CALM paper** (Ye et al. 2024) | High  quantifies 12 bias types | Add 2-3 sentences |
| **Bias mitigation approaches** (PAIRS, calibration) | Medium | Add paragraph |
| **Human evaluation papers** (Chen et al. 2024) | Medium | Add |
| **Position bias literature** (Shi et al. 2025) | Medium | Add |
| **RLAIF connection** (Lee et al. 2024) | Medium  connects to alignment | Add |
| **Our contribution statement** | Critical  explicit gap | ✅ Done |

---

## 4. METHOD (1-2 pages)

### What Top Papers Have
**Li et al.:** §3.1 (Problem formulation with equation), §3.2 (3 perturbation types), §3.3 (4 datasets with table), §3.4 (3 metric categories with equations) = 3.5 pages
**Wang et al.:** §2 (Positional Bias definition), §3 (Calibration: MEC, BPC, HITLC with equations) = 2 pages

### Our Status: ⚠️ 50%
| Missing | Impact | Fix |
|---------|--------|-----|
| **Formal problem formulation with equation** | High  Li et al. has P=(T,I*,[A],R) | Add equation defining scoring prompt components |
| **Metric equations (FR, MAD, delta)** | High  reproducible science | Add to paper |
| **Dataset table with statistics** | Medium  Li et al. Table 1 | Create table of our 50 items |
| **Hyperparameter table** | Medium  temperature, seeds, repeats | Add comprehensive table |
| **Hardware specification** | Low  we have it | Already in paper |
| **Exact prompt templates (appendix)** | Medium  Figure 3 in Li et al. | Add to appendix |
| **Scoring distribution baseline** | Medium  Figure 5 in Li et al. | Heatmap of score distributions |

---

## 5. EXPERIMENTS/RESULTS (2-4 pages)

### What Top Papers Have
**Li et al.:** §4.1 (Setup: models, prompt, hyperparameters), §4.2 (Main results: 3 findings with 2 full-page tables), §4.3 (3 mitigation strategies) = 5 pages
**Wang et al.:** §4 (Experiments: human annotation, setup, metrics, ablation, generalization) = 3 pages

### Our Status: ⚠️ 45%
| Critical Missing | Why It Matters | Fix |
|-----------------|---------------|-----|
| **Main results table** (model × probe × metric) | Every paper has this. Li et al. Table 3 is full-page | Create comprehensive table |
| **Ablation by model size** | Shows robustness | Compare 2B vs 7B vs 8B |
| **Ablation by item domain** | Shows generalization | 5 domains already in data |
| **Error bars on ALL figures** | NeurIPS requirement | ✅ Bootstrap CIs done |
| **Scoring tendency analysis** | Li et al. Figure 5  heatmap | Create per-model score distribution |
| **Per-item analysis** | Which items trigger most/least bias | Add analysis |
| **Mitigation experiments** | Li et al. §4.3 has 3 strategies | We have bias_mitigation.py  run it |
| **Comparison to baselines** | Wang et al. Table 4 (VANILLA vs MEC vs BPC) | Compare raw vs corrected scores |
| **Consistency across repeats** | Li et al. does 3 repeats, reports variance | Report per-repeat SD |

---

## 6. DISCUSSION (0.5-1 page)

### What Top Papers Have
**Li et al.:** 3 paragraphs embedded in results: (1) model scale → robustness, (2) bias can be positive, (3) scoring tendencies
**Wang et al.:** §5  ablation on evidence number k, temperature, BPDE effectiveness, generalization, fine-grained analysis = 2 pages

### Our Status: ⚠️ 55%
| Missing | Fix |
|---------|-----|
| **Why differential effect occurs (mechanism)** | ✅ IIAR hypothesis in paper |
| **Implications for practitioners** | ✅ 2 points in paper |
| **Comparison with specific prior work numbers** | Need: "Li et al. found 20-46% FR for rubric order. We find 49-64% FR. The higher rate is due to..." |
| **When does the finding NOT hold?** | Need: boundary conditions, limitations of small models |

---

## 7. LIMITATIONS (0.5 page)

### What Top Papers Have
**Li et al.:** §5  5 limitations: (1) framework expansion, (2) mitigation needed, (3) root causes unvalidated, (4) data distribution, (5) future work
**Wang et al.:** §7  brief, focused on generalizability

### Our Status: ✅ 80%
| Our Limitations | Good? |
|----------------|-------|
| 50 items  sufficient but smaller than benchmarks | ✅ |
| 2B-8B scale only | ✅ |
| Can't distinguish SFT vs RLHF | ✅ |
| Descriptive probe excluded | ✅ |
| English-only | ✅ |
| **Missing: single seed** | ❌ Add: "All experiments use seed 42. Multi-seed analysis needed for full confidence." |
| **Missing: single prompt template** | ❌ Add: "Results may vary with different prompt templates." |
| **Missing: no human baseline** | ❌ Add: "Without human evaluation, we cannot determine which scoring direction is 'correct'." |

---

## 8. BROADER IMPACT & ETHICS (0.5 page)

### What Top Papers Have
**Li et al.:** Disclosure of Interests (1 line)
**NeurIPS:** Requires separate broader impact and ethics sections

### Our Status: ✅ Added, but could be expanded
| Missing | Fix |
|---------|-----|
| **Environmental impact** | Compute: 6 GPU-hours on T4 = ~1.5 kg CO2 |
| **Who benefits, who is harmed** | More detail on potential misuse |
| **Data privacy** | No personal data  ✅ |
| **Mitigation recommendations** | ✅ In paper |

---

## 9. CONCLUSION (0.5 page)

### What Top Papers Have
**Li et al.:** 1 paragraph: (1) summary, (2) key findings, (3) recommendations, (4) code release
**Wang et al.:** 1 paragraph: (1) discovery, (2) 3 strategies, (3) results, (4) code

### Our Status: ✅ 85%
| Missing | Fix |
|---------|-----|
| **Numerical results in conclusion** | ✅ 44%/77%/35% included |
| **Explicit gap-filling statement** | ❌ Add: "This answers the open question posed by Li et al. (2025)" |
| **Future work directions** | ⚠️ Implicit  make explicit |

---

## 10. VISUALIZATIONS

### What Top Papers Have
**Li et al.:** 6 figures: (1) perturbation illustration, (2) framework overview, (3) prompt template, (4) data pipeline, (5) scoring tendency heatmap (2-panel), (6) accuracy bar chart (2-panel)
**Wang et al.:** 6 figures: (1) position bias illustration, (2) conflict rate vs score gap, (3) calibration framework, (4) accuracy vs k/temperature, (5) BPDE comparison, (6) fine-grained analysis

### Our Status: ❌ 20%
| Figure | Type | What It Shows | Priority |
|--------|------|--------------|----------|
| Figure 1 (missing) | Framework | Base vs instruct comparison overview | **Critical** |
| Figure 2 (missing) | Bar chart | Bias by probe type (base vs instruct) | **Critical** |
| Figure 3 (missing) | Bar chart | % Change by probe | **Critical** |
| Figure 4 (missing) | Heatmap | Score distribution per model (matching Li et al. Fig 5) | High |
| Figure 5 (missing) | Scatter | Bias vs model size (2B vs 7B vs 8B) | Medium |
| Figure 6 (missing) | Bar chart | Per-domain breakdown | Medium |
| Figure 7 (missing) | Line chart | Flip rate comparison (ours vs Li et al.) | Medium |
| Figure 8 (missing) | Framework | Calibration/mitigation results | Medium |

---

## 11. TABLES

### What Top Papers Have
**Li et al.:** 4 tables: (1) Dataset statistics, (2) LLM-human correlation, (3) Full FR/MAD results (5 models × 4 datasets × 5 perturbations = 100 cells), (4) Accuracy (Spearman/Pearson)
**Wang et al.:** 5 tables: (1) Win rate comparison, (2) Conflict rates, (3) Calibration template, (4) Full results (12 methods × 6 metrics), (5) Template generalization

### Our Status: ❌ 30%
| Table | What It Shows | Priority |
|-------|--------------|----------|
| Table 1 | Dataset/Item statistics | ✅ In paper |
| Table 2 | Base vs instruct results by probe | ✅ In paper |
| Table 3 | Per-family results | ✅ In paper |
| **Table 4 (missing)** | Full per-model, per-probe results (ALL 6 models × 3 probes) | **Critical** |
| **Table 5 (missing)** | Flip rate comparison with Li et al. | High |
| **Table 6 (missing)** | Ablation: per-domain | Medium |

---

## 12. STATISTICAL REPORTING

### NeuralPS/ACL Requirements
| Required | Example from Li et al. | Us |
|----------|----------------------|-----|
| Flip Rate (FR) | ✅ Table 3: 20-46% | ⚠️ Added in add_flip_rate.py |
| Mean Absolute Deviation (MAD) | ✅ Table 3: 0.19-0.53 | ❌ Not computed |
| Spearman's ρ | ✅ Table 4: 0.50-0.77 | ❌ Not computed |
| Pearson's r | ✅ Table 4: 0.53-0.78 | ❌ Not computed |
| Cohen's d | ❌ Not in Li et al. | ✅ We have it |
| Bootstrapped CI | ❌ Not in Li et al. | ✅ We have it |
| **Error bars on all figures** | ✅ | ❌ Missing |
| **k-fold or repeated measures** | ❌ Not in Li et al. | ❌ Missing |
| **Effect sizes** | ❌ Not in Li et al. | ✅ We have it |

---

## 13. SUBMISSION READINESS CHECKLIST

### Complete (✓) vs Missing (✗)

#### Paper Sections
- [ ] Abstract: 250 words, includes ALL: problem, gap, method, results, impact, code
- [ ] Introduction: practical motivation, gap quote, numbered contributions
- [ ] Related Work: OffsetBias, CALM, Li et al., position bias, mitigation, our gap
- [ ] Method: formal equation, perturbation table, dataset stats table, metric equations
- [ ] Results: full results table, per-probe analysis, per-model analysis, per-domain, flip rates
- [ ] Discussion: mechanism explanation, comparison to Li et al., boundary conditions
- [ ] Limitations: multi-seed, multi-template, human baseline, small models
- [ ] Broader Impact: environment, misuse, beneficiaries
- [ ] Ethics: IRB, licenses, data privacy
- [ ] Conclusion: numbers, gap reference, future work, code

#### Figures (need 8 total)
- [ ] Figure 1: Framework overview
- [ ] Figure 2: Bias by probe type
- [ ] Figure 3: % Change by probe
- [ ] Figure 4: Score distribution heatmap
- [ ] Figure 5: Bias vs model size
- [ ] Figure 6: Per-domain breakdown
- [ ] Figure 7: Flip rate comparison with Li et al.
- [ ] Figure 8: Calibration/mitigation results

#### Tables (need 6 total)
- [ ] Table 1: Dataset/item statistics
- [ ] Table 2: Base vs instruct by probe (fr, mad, delta, d)
- [ ] Table 3: Per-family results
- [ ] Table 4: Full per-model, per-probe results
- [ ] Table 5: Flip rate vs Li et al. comparison
- [ ] Table 6: Domain breakdown

#### Metrics (need 5)
- [ ] Flip Rate (FR)  matching Li et al.
- [ ] Mean Absolute Deviation (MAD)  matching Li et al.
- [ ] Cohen's d  effect size
- [ ] Bootstrapped 95% CI  uncertainty
- [ ] Spearman's ρ  accuracy (if human scores available)

#### NeurIPS Checklist (16 items)
- [ ] Q1: Claims match results
- [ ] Q2: Limitations section
- [ ] Q3: Theory assumptions
- [ ] Q4: Reproducibility
- [ ] Q5: Open code/data
- [ ] Q6: Experimental details
- [ ] Q7: Statistical significance
- [ ] Q8: Compute resources
- [ ] Q9: Code of ethics
- [ ] Q10: Broader impact
- [ ] Q11: Safeguards
- [ ] Q12: Licenses
- [ ] Q13: New assets
- [ ] Q14: Human subjects (N/A)
- [ ] Q15: IRB (N/A)
- [ ] Q16: LLM usage declaration

---

## 14. PRIORITIZED ACTION PLAN (ordered by impact)

### PHASE A: CRITICAL (must do  8 hours)
```
A1 [2h] Generate all 8 publication figures (fix_study1.py → matplotlib)
A2 [2h] Create full results table (Table 4: 6 models × 3 probes × 4 metrics)
A3 [1h] Add MAD metric (matching Li et al. methodology)
A4 [1h] Add per-domain analysis (5 domains × 3 probes)
A5 [1h] Write NeurIPS checklist in paper
A6 [1h] Add explicit "this answers Li et al.'s call" statements
```

### PHASE B: STRONG (should do  6 hours)
```
B1 [3h] Kaggle re-run: 100 items + fixed descriptive probe + multi-seed
B2 [2h] Update all analysis with new Kaggle data
B3 [1h] Generate per-model score distribution heatmap (Figure 4)
```

### PHASE C: POLISH (nice to do  4 hours)
```
C1 [1h] Spearman's ρ accuracy metric
C2 [2h] Human baseline: 5 people × 20 items
C3 [1h] Flip rate comparison bar chart (Figure 7)
```

---

## 15. VERDICT: What Makes a Paper "Top Research Institute Level"

### The Non-Negotiable Criteria

| Criterion | Our Score | Li et al. Score | Gap |
|-----------|-----------|-----------------|-----|
| **Clear gap, explicitly stated** | 8/10 | 9/10 | Minor |
| **Rigorous experimental design** | 7/10 | 9/10 | Need more conditions |
| **Sufficient scale (items × models)** | 5/10 | 9/10 | 50 items vs 5,421 |
| **Multiple complementary metrics** | 6/10 | 9/10 | Need MAD, Spearman's ρ |
| **Publication-quality figures** | 3/10 | 8/10 | Need 8 figures |
| **Comprehensive tables** | 4/10 | 9/10 | Need 6 tables |
| **Statistical rigor** | 6/10 | 7/10 | Need per-condition error bars |
| **Human evaluation** | 0/10 | 7/10 | Need human baseline |
| **Mitigation experiments** | 6/10 | 8/10 | Code exists, not run |
| **Novelty of contribution** | 9/10 | 8/10 | ✅ Stronger  first base-vs-instruct |
| **Reproducibility** | 8/10 | 7/10 | ✅ Better  full open source |
| **Writing quality** | 6/10 | 8/10 | Needs polishing |

### Overall Research Quality Index (RQ)

```
Our RQ:  69/120 (57%)
Li et al. RQ: 98/120 (82%)
Target for acceptance: >80/120

Our Unfair Advantage: Novelty (9/10)  nobody has done base-vs-instruct
Our Critical Gap: Scale (5/10) and Figures (3/10)
```

### The One-Week Plan to Close the Gap

```
Day 1 (8h): Generate all figures + tables. Add MAD metric. Add per-domain analysis.
Day 2 (8h): Kaggle re-run (100 items + fixed probe). Let it run overnight.
Day 3 (6h): Update all analysis with new data. Add Spearman's ρ.
Day 4 (4h): Run human baseline (5 friends × 20 items). Add to paper.
Day 5 (4h): Polish paper. Write checklist. Generate final PDF.
Day 6 (2h): Submit to arXiv. Prepare ISEF poster.
```

**Total: ~32 hours + 4 hours GPU = 36 hours to submission-ready**
