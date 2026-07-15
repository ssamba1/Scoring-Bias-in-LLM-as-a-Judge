.PHONY: help install test lint figures paper archive ci setup clean reproduce-all download-data pre-commit \
        install-package run-api run-dashboard export-data check-credentials health-check

help:  # Show available targets
	@grep -E '^[a-zA-Z_-]+:.*#' Makefile | sort | while read -r line; do \
		name=$$(echo "$$line" | cut -d: -f1); \
		desc=$$(echo "$$line" | cut -d# -f2); \
		printf "  \033[36m%-20s\033[0m %s\n" "$$name" "$$desc"; \
	done

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
