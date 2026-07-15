.PHONY: help install test lint figures paper archive ci setup clean reproduce-all download-data pre-commit \
        install-package run-api run-dashboard export-data check-credentials health-check \
        validate docs

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
	@printf "  \033[36m%-22s\033[0m %s\n" "make export-data" "Export results to CSV"
	@printf "  \033[36m%-22s\033[0m %s\n" "make export-all" "Export to CSV + JSON + Excel + Parquet"
	@printf "  \033[36m%-22s\033[0m %s\n" "make download-data" "Instructions for downloading experiment data"
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
	flake8 src/scoring_bias/ cli.py tests/*.py scripts/*.py api/app.py \
		--max-line-length=100 --count --statistics
	black --check --diff src/scoring_bias/ cli.py tests/*.py scripts/*.py api/app.py

figures:  # Generate publication-quality PNG figures
	python paper/generate_png_figures.py

paper: figures  # Compile paper PDF from LaTeX (generates figures first)
	cd paper && pdflatex -interaction=nonstopmode camera_ready_full.tex && \
		pdflatex -interaction=nonstopmode camera_ready_full.tex

validate:  # Run data validation pipeline
	python results_rootcause/validation/run_all_validation.py

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

archive:  # Generate arXiv submission package
	python paper/arxiv_package.py

ci: test lint  # Run all CI checks (test + lint)

reproduce-all: setup test paper archive  # Full end-to-end reproduction pipeline

run-api:  # Start the FastAPI server
	uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

run-dashboard:  # Start the Streamlit dashboard
	streamlit run dashboard/app.py

export-data:  # Export analysis results to CSV
	python scripts/export_data.py --format csv

export-all:  # Export to all formats
	python scripts/export_data.py --format csv
	python scripts/export_data.py --format json
	python scripts/export_data.py --format excel
	python scripts/export_data.py --format parquet

check-credentials:  # Scan for accidentally committed credentials
	python scripts/check_credentials.py

health-check:  # Verify project integrity
	python scripts/health_check.py

download-data:  # Download experiment results from remote
	@echo "See notebooks/reproduce_colab.ipynb for Colab reproduction"
	@echo "Results JSON should be placed at results_rootcause/study1_results.json"

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
