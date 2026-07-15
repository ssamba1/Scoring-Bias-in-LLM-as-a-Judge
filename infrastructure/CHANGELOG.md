# Changelog

## [1.0.0] — July 2026

### Added
- Complete camera-ready paper (20 pages, LaTeX)
- Interactive HTML article (distill.pub style)
- Leaderboard page (ranked model comparison)
- Graphical abstract (SVG)
- Supplementary formal proofs (4 theorems)
- UI tests (11 tests, all passing)
- Quantified limitations analysis (6 limitations, power analysis)
- Cross-probe correlation analysis
- Depth findings (5 independent findings)
- Training method decomposition
- Failure case analysis
- CI workflow (GitHub Actions)
- Dockerfile + docker-compose
- arXiv submission package
- ISEF competition materials
- Production-grade infrastructure:
  - .pre-commit-config.yaml with trailing-whitespace, end-of-file-fixer, check-yaml, check-json, check-added-large-files, flake8, black
  - .editorconfig with language-specific indentation rules
  - .gitattributes with proper diff and EOL settings
  - Comprehensive .gitignore (Python, LaTeX, OS, IDE)
  - Pinned requirements.txt via pip freeze
  - conda environment.yml
  - Improved Makefile with help, test, lint, paper, figures, reproduce-all, clean
  - Python 3.11 slim Dockerfile
  - .dockerignore for clean builds
  - docker-compose.yml with test and jupyter services
  - pytest.ini + conftest.py with project root discovery
  - GitHub Actions CI (test, lint, paper-check, docker)
  - KNOWN_ISSUES.md documenting known limitations
  - Binder configuration for cloud reproducibility
  - .hermes.md project config for Hermes agent
  - Lint report and project statistics in infrastructure/

## [0.9.0] — June 2026

### Added
- Initial project structure
- Core scoring pipeline
- Bias interaction experiments
- Root cause analysis framework
- Literature review infrastructure
