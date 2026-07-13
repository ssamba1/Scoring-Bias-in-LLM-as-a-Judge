# Project Checklist — From Here to Submission

## Phase 0: Decision (Day 1)
- [ ] Pick Option 1 (Root Cause) or Option 2 (Bias Interaction)
- [ ] Read the relevant proposal in `proposals/`
- [ ] Read the elaborated version in `proposals/`

## Phase 1: Environment Setup (Day 1-2)

### Option 2
- [ ] Get API keys for Claude, GPT-4o, Gemini, DeepSeek, Llama
- [ ] `pip install -r pipeline_biasinteraction/requirements.txt`
- [ ] Add keys to `pipeline_biasinteraction/scoring_pipeline.py`
- [ ] Run 10-item pilot: `python3 pipeline_biasinteraction/scoring_pipeline.py --judge claude --input data/items_base.csv`
- [ ] Verify scores look reasonable

### Option 1
- [ ] Get HuggingFace token
- [ ] Request access for Llama 3, Gemma 2 models
- [ ] Set up Colab or local GPU
- [ ] `pip install -r pipeline_rootcause/requirements.txt`
- [ ] Implement `score_with_hf_model()` in `rootcause_pipeline.py`
- [ ] Run 10-item pilot

## Phase 2: Data Collection (Day 2-4)

### Option 2
- [ ] Run Claude: `python3 scoring_pipeline.py --judge claude --repeats 3`
- [ ] Run GPT-4o: `python3 scoring_pipeline.py --judge gpt4o --repeats 3`
- [ ] Run Gemini: `python3 scoring_pipeline.py --judge gemini --repeats 3`
- [ ] Run DeepSeek: `python3 scoring_pipeline.py --judge deepseek --repeats 3`
- [ ] Run Llama: `python3 scoring_pipeline.py --judge llama --repeats 3`
- [ ] Check data quality (no nulls, all scores 1-5)

### Option 1
- [ ] Run base models (3 models × 50 items)
- [ ] Run instruct models (3 models × 50 items)
- [ ] Verify all inferences completed

## Phase 3: Analysis (Day 4-5)
- [ ] Run `python3 pipeline_biasinteraction/analysis.py` (Option 2)
- [ ] Run `python3 explore_results.py` to explore
- [ ] Run `python3 pipeline_biasinteraction/generate_figures.py`
- [ ] OR: Run `python3 explore_rootcause.py` (Option 1)
- [ ] Check: are the results significant? (p < 0.05)
- [ ] Check: do the interaction ratios show compounding or cancelling?

## Phase 4: Paper Writing (Day 5-7)
- [ ] Read the paper draft in `paper/paper_biasinteraction.md` or `paper/paper_rootcause.md`
- [ ] Replace synthetic results with real results
- [ ] Replace figure placeholders with real figures
- [ ] Update references with actual citation counts
- [ ] Proofread and edit

## Phase 5: Polish (Day 7-10)
- [ ] Convert to LaTeX: `paper/paper_latex.tex`
- [ ] Compile to PDF
- [ ] Read the ISEF application package: `isef/application_package.md`
- [ ] Fill in the ISEF forms
- [ ] Practice the presentation: `isef/presentation_slides.md`

## Phase 6: Submit (Day 10)
- [ ] Submit to arXiv (for preprint)
- [ ] Submit to ISEF / NeurIPS HS track / science fair

## Reference Materials
- Literature review: `literature/literature_review.md`
- Paper notes: `literature/paper_notes.md`
- 35 bias types catalog: `literature_audit/bias_inventory.md`
- Getting started: `GETTING_STARTED.md`

## Costs to Budget
- Option 2 API calls: ~$28 (5 judges)
- Option 1 GPU: ~$10-15 (Colab)
- Domain for project website: $0 (GitHub Pages)
- LaTeX: $0 (Overleaf free tier)
