#!/bin/bash
# Build all LaTeX papers to PDF
# Requires: pdflatex, bibtex
# Usage: bash build_papers.sh

set -e

echo "========================================="
echo "  Building Research Papers to PDF"
echo "========================================="

cd "$(dirname "$0")/paper"

compile_paper() {
    local tex_file="$1"
    local base_name="${tex_file%.tex}"
    
    echo ""
    echo "--- Building: $base_name ---"
    
    # First pass
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1 || true
    
    # Bibliography
    if [ -f "${base_name}.aux" ]; then
        bibtex "${base_name}" > /dev/null 2>&1 || true
    fi
    
    # Second pass
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1 || true
    
    # Third pass for references
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1 || true
    
    if [ -f "${base_name}.pdf" ]; then
        local size=$(stat -f%z "${base_name}.pdf" 2>/dev/null || stat -c%s "${base_name}.pdf" 2>/dev/null || echo "0")
        echo "  ✓ ${base_name}.pdf ($(echo "scale=1; $size/1024" | bc) KB)"
    else
        echo "  ✗ ${base_name}.pdf not found (check LaTeX errors)"
    fi
}

# Compile each paper
compile_paper "paper_neurips_style.tex"
compile_paper "paper_rootcause_latex.tex"
compile_paper "formal_framework.tex"

echo ""
echo "========================================="
echo "  Build Complete"
echo "========================================="
ls -la *.pdf 2>/dev/null || echo "  (No PDFs generated)"
