# Paper Source

This directory contains the camera-ready manuscript and supporting files.

## Files

| File | Description |
|------|-------------|
| `camera_ready_full.tex` | Main LaTeX manuscript (20 pages) |
| `camera_ready_publishable.html` | HTML print-to-PDF version |
| `supplementary_formal.tex` | Formal IIAR proofs (4 theorems) |
| `quantified_limitations.tex` | Quantified limitation analysis |
| `depth_findings.tex` | Five independent depth findings |
| `statistical_rigor.tex` | Peer review statistical defense |
| `generate_png_figures.py` | Publication-quality figure generator |
| `python generate_png_figures.py` | Compile to PDF (requires pdflatex) |
| `compile_pdf.sh` | Run `compile_pdf.sh` to compile |
| `arxiv_submission/` | arXiv submission bundle |

## Compiling

```bash
# Install LaTeX (Ubuntu/Debian)
sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-bibtex-extra biber

# Compile
cd paper
./compile_pdf.sh
```

## Figures

Run `python3 generate_png_figures.py` to generate publication-quality PNG figures from the analysis data. Requires matplotlib.
