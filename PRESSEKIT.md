# Press Kit — Bias in LLM-as-a-Judge Research

## Quick Facts
- **Project**: Two studies on bias in AI evaluation systems
- **Researchers**: Student A, Student B (High School Name)
- **Status**: Pre-publication, preparing for ISEF 2027
- **Repository**: github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge (122 files, open source)

## Key Findings

### Study 1: Root Cause
"Bias is learned during instruction tuning, not pre-training. Base models show 1.77-2.29× lower scoring bias than instruction-tuned models."

### Study 2: Bias Interactions
"When multiple biases co-occur, they compound rather than adding linearly. Interaction ratios reach 2.10× expected additive effects."

## Impact
- 35+ bias types documented in LLM judges
- 23 have no mitigation strategy
- First systematic evidence of bias interaction effects
- Practical: evaluation pipelines must test bias combinations

## Media Assets
- **Slides**: presentation.html (12 slides, HTML/CSS, arrow key navigation)
- **Dashboard**: dashboard/interactive_viz.html (D3.js visualizations)
- **Live Dashboard**: dashboard/live_dashboard.html (real-time updates)
- **Paper**: paper/paper_biasinteraction_final.tex and paper_rootcause_final.tex
- **Monograph**: paper/monograph.md (comprehensive writeup)

## Quotes

> "Scoring bias is not inherent to language models. It's something we teach them during instruction tuning. This is actually good news — it means we can fix it."

> "When position bias and verbosity bias occur simultaneously, the combined effect is up to 2× worse than if they simply added together."

## Availability
Both researchers available for interviews or questions.
Contact: student.email@example.com

## Repository Stats
- 122 files, 24 commits
- 37 Python modules for pipelines and analysis
- 35 Markdown documents
- 7 HTML dashboards and visualizations
- 6 LaTeX papers
- Docker, docker-compose, FastAPI
- Comprehensive test suite (60 tests)
