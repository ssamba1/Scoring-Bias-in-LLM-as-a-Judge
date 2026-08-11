.PHONY: help install test lint figures paper archive ci setup clean reproduce-all pre-commit \
        install-package run-api run-dashboard check-credentials health-check \
        validate docs integrity verify-clean arxiv-package

help:  # Show available targets
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║   Scoring Bias  Makefile Help                              ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "── Development ────────────────────────────────────────────────"
	@printf "  \033[36m%-22s\033[0m %s\n" "make setup" "Set up development environment"
	@printf "  \033[36m%-22s\033[0m %s\n" "make install" "Install Python dependencies + pre-commit"
	@printf "  \033[36m%-22s\033[0m %s\n" "make install-package" "Install scoring-bias package in dev mode"
	@printf "  \033[36m%-22s\033[0m %s\n" "make pre-commit" "Run pre-commit on all files"
	@echo ""
	@echo "── Testing & Quality ──────────────────────────────────────────"
	@printf "  \033[36m%-22s\033[0m %s\n" "make test" "Run all unit tests with pytest"
	@printf "  \033[36m%-22s\033[0m %s\n" "make test-cov" "Run tests with coverage report"
	@printf "  \033[36m%-22s\033[0m %s\n" "make lint" "Run flake8 + black (check mode)"
	@printf "  \033[36m%-22s\033[0m %s\n" "make ci" "Run test + lint (CI pipeline)"
	@echo ""
	@echo "── Paper & Figures ────────────────────────────────────────────"
	@printf "  \033[36m%-22s\033[0m %s\n" "make paper" "Compile paper PDF from LaTeX"
	@printf "  \033[36m%-22s\033[0m %s\n" "make figures" "Regenerate all publication figures"
	@printf "  \033[36m%-22s\033[0m %s\n" "make archive" "Generate arXiv submission package"
	@echo ""
	@echo "── Data & Validation ──────────────────────────────────────────"
	@printf "  \033[36m%-22s\033[0m %s\n" "make validate" "Run data validation pipeline"
	@echo ""
	@echo "── Infrastructure ─────────────────────────────────────────────"
	@printf "  \033[36m%-22s\033[0m %s\n" "make docs" "Build project documentation"
	@printf "  \033[36m%-22s\033[0m %s\n" "make clean" "Remove all build artifacts and caches"
	@printf "  \033[36m%-22s\033[0m %s\n" "make check-credentials" "Scan for accidentally committed credentials"
	@printf "  \033[36m%-22s\033[0m %s\n" "make health-check" "Verify project integrity"
	@printf "  \033[36m%-22s\033[0m %s\n" "make run-api" "Start the FastAPI server"
	@printf "  \033[36m%-22s\033[0m %s\n" "make run-dashboard" "Start the Streamlit dashboard"
	@echo ""
	@echo "── Pipeline ───────────────────────────────────────────────────"
	@printf "  \033[36m%-22s\033[0m %s\n" "make reproduce-all" "Full end-to-end reproduction: setup → test → paper → archive"

setup: install install-package pre-commit  # Set up development environment

install:  # Install Python dependencies
	pip install -U pip
	pip install -r requirements.txt
	pip install pre-commit pytest pytest-cov
	pre-commit install

install-package:  # Install the scoring-bias package in dev mode
	pip install -e ".[dev,api,dashboard,notebook]"

pre-commit:  # Run pre-commit checks on all files
	pre-commit run --all-files

test:  # Run all unit tests with pytest
	python -m pytest tests/ -v --tb=short

test-cov:  # Run tests with coverage report
	python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing

lint:  # Run code quality checks (flake8 + black)
	pip install flake8 black -q
	flake8 src/scoring_bias/ cli.py tests/*.py api.py \
		--max-line-length=100 --count --statistics
	black --check --diff src/scoring_bias/ cli.py tests/*.py api.py

figures:  # Regenerate the paper's figures from the committed data
	cd paper/honest/repro && for f in make_*.py; do python $$f; done

paper: figures  # Compile the paper PDF (regenerates figures first)
	cd paper/honest && pdflatex -interaction=nonstopmode scoring_bias_v2.tex && \
		bibtex scoring_bias_v2 && \
		pdflatex -interaction=nonstopmode scoring_bias_v2.tex && \
		pdflatex -interaction=nonstopmode scoring_bias_v2.tex

validate:  # Check the paper's prose and figures against the derived data
	cd paper/honest/repro && python check_prose.py && python check_figures.py

docs:  # Build project documentation
	@echo "Building documentation..."
	@if command -v pdoc > /dev/null 2>&1; then \
		pdoc --output-dir docs/api src/scoring_bias/; \
		echo "✓ API docs generated in docs/api/"; \
	else \
		echo "⚠️ pdoc not installed. Install with: pip install pdoc"; \
		echo "   Falling back to markdown docs summary."; \
		@echo "See README.md and paper/ for project documentation."; \
	fi

archive: arxiv-package  # Generate arXiv submission package (alias)

ci: test lint  # Run all CI checks (test + lint)

reproduce-all: setup test paper archive  # Full end-to-end reproduction pipeline

run-api:  # Start the FastAPI server
	uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

run-dashboard:  # Start the Streamlit dashboard
	streamlit run dashboard.py

check-credentials:  # Scan every commit for credentials
	python scan_secrets.py

health-check: integrity  # Verify project integrity (alias)

clean:  # Remove all build artifacts, caches, and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.aux' -delete
	find . -type f -name '*.log' -delete
	find . -type f -name '*.out' -delete
	find . -type f -name '*.toc' -delete
	find . -type f -name '*.bbl' -delete
	find . -type f -name '*.blg' -delete
	find . -type f -name '*.pyc' -delete
	rm -rf build/ dist/ *.egg-info/

integrity:  # Fabrication sweep, guard mutations, and history secret scan
	python -m pytest tests/ -q -rs
	python mutation_check.py
	python scan_secrets.py

verify-clean:  # Run the suite in a fresh clone of HEAD
	python verify_clean_clone.py

arxiv-package:  # Build and verify the honest paper's submission archive
	cd paper/honest && python arxiv_package.py
