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
4. **Run existing tests**: `python -m pytest tests/ -v`
5. **Make your changes**
6. **Add tests** for new functionality
7. **Run all tests** and ensure they pass
8. **Run pre-commit**: `pre-commit run --all-files`
9. **Submit a pull request**

## 📝 Code Style

- **Python**: Follow PEP 8. Use 4-space indentation. Include NumPy-style docstrings for all public functions.
- **LaTeX**: Keep lines under 80 characters where possible. Use 2-space indentation for .tex files.
- **JSON**: Use 2-space indentation.
- **Markdown**: Use GitHub-flavored markdown. Wrap lines at 80 characters for readability.
- **YAML**: Use 2-space indentation.

## 🔍 Code Review Guidelines

All pull requests require review before merging. Reviewers should check for:

### Correctness
- Does the code do what it claims?
- Are edge cases handled (empty inputs, missing data, API failures)?
- Are floating-point comparisons robust?
- Are statistical computations correct (effect sizes, p-values, Bayesian posteriors)?

### Reproducibility
- Are all random seeds fixed (seed=42)?
- Is temperature=0 for all judge calls?
- Are exact model versions and API parameters documented?
- Are intermediate outputs deterministic given the same inputs?

### Code Quality
- Is the code well-structured and readable?
- Are there sufficient docstrings and inline comments?
- Are variable names descriptive and unambiguous?
- Is there unnecessary duplication that could be refactored?

### Testing
- Do new features have corresponding tests?
- Do tests cover the main success paths and key failure modes?
- Are tests deterministic and isolated (no shared mutable state)?

### Research Integrity
- Is there clear separation between pre-registered analyses and post-hoc findings?
- Are limitations transparently discussed?
- Are all assumptions stated explicitly?

## ✅ Testing Requirements

All contributions must maintain or improve test coverage:

- **Unit tests**: Required for all new Python functions and methods. Place in `tests/` with filename `test_<module>.py`.
- **Regression tests**: Required for bug fixes. Add a test that fails on the old code and passes with the fix.
- **Data integrity tests**: Required when adding/modifying experiment data. Verify schema, ranges, and expected distributions.
- **Running tests**: Always run `python -m pytest tests/ -v` before submitting. All tests must pass.
- **Coverage**: Aim for 80%+ coverage on new code. Run `python -m pytest tests/ --cov=src --cov-report=term-missing` to verify.

## ✅ Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass (`python -m pytest tests/ -v`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] New models have corresponding model cards
- [ ] New functions have NumPy-style docstrings
- [ ] References have complete DOIs/URLs
- [ ] Documentation updated if relevant
- [ ] All analysis results are reproducible
- [ ] Code has been self-reviewed

## 🔬 Research Integrity

All contributions must adhere to:
- Transparent reporting of all methods and results
- Disclosure of any API costs or computational resources used
- Clear separation between pre-registered analyses and post-hoc findings
- Open data sharing where possible

## 📧 Contact

For questions: srisamba09@gmail.com

## 📄 License

By contributing, you agree that your contributions will be licensed under CC-BY 4.0.
