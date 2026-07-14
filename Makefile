.PHONY: install test lint paper figures clean

install:
	pip install -r requirements.txt

test:
	python3 tests/test_all.py

lint:
	pip install flake8 black -q
	flake8 results_rootcause/*.py tests/*.py
	black --check results_rootcause/*.py tests/*.py

figures:
	python3 paper/generate_png_figures.py

paper: figures
	cd paper && pdflatex camera_ready_full.tex && pdflatex camera_ready_full.tex

archive:
	python3 paper/arxiv_package.py

ci: test lint

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.aux' -delete
	find . -type f -name '*.log' -delete
	find . -type f -name '*.out' -delete
