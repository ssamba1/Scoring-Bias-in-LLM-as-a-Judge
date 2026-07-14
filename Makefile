.PHONY: help install test lint figures paper archive ci clean setup reproduce-all download-data

help:
	@grep -E '^[a-zA-Z_-]+:.*#' Makefile | sort | while read -r line; do \
		name=$$(echo "$$line" | cut -d: -f1); \
		desc=$$(echo "$$line" | cut -d# -f2); \
		printf "  \033[36m%-20s\033[0m %s\n" "$$name" "$$desc"; \
	done

setup: install pre-commit  # Set up development environment

install:  # Install Python dependencies
	pip install -r requirements.txt
	pip install pre-commit pytest
	pre-commit install

pre-commit:  # Run pre-commit checks
	pre-commit run --all-files

test:  # Run all unit tests
	python3 -m pytest tests/test_all.py -v

lint:  # Run code quality checks
	pip install flake8 black -q
	flake8 results_rootcause/*.py tests/*.py pipeline_rootcause/*.py
	black --check results_rootcause/*.py tests/*.py pipeline_rootcause/*.py

figures:  # Generate publication-quality PNG figures
	python3 paper/generate_png_figures.py

paper: figures  # Compile paper PDF from LaTeX
	cd paper && pdflatex camera_ready_full.tex -interaction=nonstopmode && \
		pdflatex camera_ready_full.tex -interaction=nonstopmode

archive:  # Generate arXiv submission package
	python3 paper/arxiv_package.py

ci: test lint  # Run all CI checks

reproduce-all: setup test paper archive  # Full end-to-end reproduction

download-data:  # Download experiment results from remote
	@echo "See notebooks/reproduce_colab.ipynb for Colab reproduction"
	@echo "Results JSON should be placed at results_rootcause/study1_results.json"

clean:  # Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.aux' -delete
	find . -type f -name '*.log' -delete
	find . -type f -name '*.out' -delete
	find . -type f -name '*.pyc' -delete
