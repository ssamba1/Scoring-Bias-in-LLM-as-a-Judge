# Contributing to Scoring Bias in LLM-as-a-Judge

Thank you for your interest in contributing to this research project! We welcome contributions that advance the understanding of scoring bias in LLM-as-a-Judge models.

## 🧪 Types of Contributions

### 1. Adding New Models
The most impactful contribution is evaluating new models (especially base-instruct pairs) using the existing probe framework.

To add a model:
1. Add the model to the inference pipeline in `results_rootcause/`
2. Run the analysis on all 3 probes × 3 variants × 50 items
3. Submit the results as a structured JSON file
4. Update the model cards in `data/model_cards/all_models.md`

### 2. Adding New Probe Types
If you identify a new scoring bias type:
1. Define the probe variants in the prompt template format
2. Implement inference for the new probe
3. Update the analysis pipeline to compute Δ, flip rate, and effect sizes
4. Document the probe in the appendices

### 3. New Analyses
- Domain-specific bias analysis (requires per-item score data)
- Cross-lingual evaluation (requires translated items)
- Human baseline studies
- Mitigation strategies (ensembling, calibration)

### 4. Bug Fixes & Improvements
- Code optimization, documentation fixes, test additions
- Reproducibility enhancements

## 📋 Development Workflow

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run existing tests**: `python tests/test_all.py`
5. **Make your changes**
6. **Add tests** for new functionality
7. **Run all tests** and ensure they pass
8. **Submit a pull request**

## 📝 Code Style

- Python: Follow PEP 8
- LaTeX: Keep lines under 80 characters where possible
- JSON: Use consistent formatting (2-space indentation)
- Markdown: Use GitHub-flavored markdown
- Include docstrings for all Python functions (NumPy style preferred)

## 🔬 Research Integrity

All contributions must adhere to:
- Transparent reporting of all methods and results
- Disclosure of any API costs or computational resources used
- Clear separation between pre-registered analyses and post-hoc findings
- Open data sharing where possible

## ✅ Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass
- [ ] New models have corresponding model cards
- [ ] References have complete DOIs/URLs
- [ ] Documentation updated if relevant
- [ ] All analysis results are reproducible

## 📧 Contact

For questions: srisamba09@gmail.com

## 📄 License

By contributing, you agree that your contributions will be licensed under CC-BY 4.0.
