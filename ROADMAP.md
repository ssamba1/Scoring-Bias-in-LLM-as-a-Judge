# Project Roadmap

## Current Status (July 2026)
✅ **Gap verification** — Both niches 100% confirmed untouched  
✅ **Infrastructure** — All pipelines, papers, tools built  
✅ **Tests** — 13/13 passing  
✅ **Benchmark** — Scoring Bias Benchmark v1.0 (950 probes)  
✅ **Papers** — Full LaTeX drafts for both options  
✅ **Survey** — Comprehensive literature survey (30 refs, 19 bias types)  

## Phase 1: Data Collection (Week 1-2)
[ ] Set up API keys in `.env`  
[ ] Run synthetic pilot to verify pipeline  
[ ] Run 10-item probe for each judge  
[ ] Run full experiment for all 5 judges  
[ ] Run quality check on results  
[ ] Import results into database  

## Phase 2: Analysis (Week 2-3)
[ ] Run analysis pipeline  
[ ] Generate figures  
[ ] Compute interaction ratios  
[ ] Run Bayesian analysis  
[ ] Run results comparison  
[ ] Generate analysis report  

## Phase 3: Writing (Week 3-4)
[ ] Plug real results into paper drafts  
[ ] Replace synthetic figures with real figures  
[ ] Update references with actual citation counts  
[ ] Proofread and edit  
[ ] Compile LaTeX to PDF  
[ ] Review with advisor/mentor  

## Phase 4: Submission (Week 4-5)
[ ] Submit to arXiv  
[ ] Prepare ISEF application  
[ ] Practice presentation  
[ ] Submit to ISEF  
[ ] Write blog post  
[ ] Share on social media / with press  

## Phase 5: Future Work (Months 2-6)
[ ] Expand to more bias types (authority, bandwagon, cross-cultural)  
[ ] Test more model families (Qwen, DeepSeek, OLMo)  
[ ] Validate mitigations under multi-bias conditions  
[ ] Write full journal paper  
[ ] Submit to workshop / conference  
[ ] Release as open-source bias testing toolkit  

## Extended Studies (Months 3-12)
[ ] Cross-cultural bias in LLM judges  
[ ] Temporal stability of judge bias  
[ ] Judge fatigue over long evaluation sessions  
[ ] Bias interaction × mitigation interaction  
[ ] Mechanistic interpretability of bias circuits  

## Publication Targets

| Venue | Deadline | Status |
|-------|----------|--------|
| arXiv preprint | Rolling | Ready for submission |
| ISEF 2027 | March 2027 | Prep in progress |
| NeurIPS HS Track 2027 | June 2027 | Target |
| ICML NextGen 2027 | January 2027 | Target |
| ACL workshop | March 2027 | Target |

## Key Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| M1: Data collection complete | Week 2 | All 5 judges scored |
| M2: Analysis complete | Week 3 | Interaction ratios confirmed |
| M3: Paper ready | Week 4 | PDF of paper |
| M4: arXiv submission | Week 5 | arXiv ID |
| M5: ISEF submission | March 2027 | Application complete |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| API key issues | Low | High | Test with synthetic data first |
| Rate limiting | Medium | Medium | Staggered execution, exponential backoff |
| Judge model changes | Low | Medium | Pin model versions |
| Being scooped | Low | High | Submit to arXiv ASAP |
| Cost overrun | Low | Low | ~$26 total, well within budget |
