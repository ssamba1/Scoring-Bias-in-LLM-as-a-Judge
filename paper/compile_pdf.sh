#!/bin/bash
# Compile the paper PDF from LaTeX
# Requires: pdflatex, bibtex
set -e

cd "$(dirname "$0")/paper"

echo "=== Compiling camera_ready_full.tex ==="

# First pass
pdflatex camera_ready_full.tex -interaction=nonstopmode 2>&1 | tail -3

# Bibliography
bibtex camera_ready_full 2>&1 | tail -3

# Second pass
pdflatex camera_ready_full.tex -interaction=nonstopmode 2>&1 | tail -3

# Third pass (resolve cross-references)
pdflatex camera_ready_full.tex -interaction=nonstopmode 2>&1 | tail -3

echo ""
if [ -f camera_ready_full.pdf ]; then
    echo "✓ PDF compiled: paper/camera_ready_full.pdf"
    echo "  Size: $(ls -lh camera_ready_full.pdf | awk '{print $5}')"
else
    echo "✗ PDF compilation failed. Check paper/camera_ready_full.log for errors."
    exit 1
fi
