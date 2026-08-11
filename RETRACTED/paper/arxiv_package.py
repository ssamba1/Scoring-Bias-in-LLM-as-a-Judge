#!/usr/bin/env python3
"""arXiv submission package generator.
Creates the complete submission bundle with all required files.
"""
import json, os, shutil, sys, time
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
OUT = BASE / "arxiv_submission"
PAPER_SRC = BASE / "camera_ready.tex"
FIGURES_DIR = BASE / "figures" / "study1"

# Metadata
META = {
    "title": "Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge",
    "authors": "Student A, Student B",
    "primary_class": "cs.CL",
    "secondary_classes": ["cs.AI", "cs.LG", "stat.ML"],
    "license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
    "abstract": "LLMs are increasingly deployed as automated judges in the LLM-as-a-Judge paradigm, yet they exhibit systematic scoring biases that compromise evaluation reliability. Li et al. documented three scoring bias types across five frontier models, but explicitly noted that \"the underlying causes of these scoring biases remain to be validated.\" We present the first systematic investigation of whether scoring bias originates from pre-training or emerges during instruction tuning. Through controlled experiments spanning 3 model families (Llama 3 8B, Mistral 7B, Gemma 2 2B) with 6 total variants (base + instruct each) across 3 scoring bias probes and 3 variants per probe totaling 8,100 judgments on a free GPU, we find that instruction tuning has differential effects: format-related biases (rubric order, score ID) decrease by 44% and 77% respectively, while content-related bias (reference answer) increases by 35%. This pattern is consistent across all three families. Our flip rates are consistent with Li et al. (25-48%), validating our methodology.",
    "comments": "8 pages, 3 tables, 8 figures. Submitted to NeurIPS 2026 High School Projects Track."
}

def create_package():
    """Build the arXiv submission directory."""
    print("="*60)
    print("ARXIV SUBMISSION PACKAGE GENERATOR")
    print("="*60)
    
    # Clean and create output directory
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    
    # 1. Copy main paper
    print("\n1. Copying main paper...")
    if PAPER_SRC.exists():
        shutil.copy(PAPER_SRC, OUT / "main.tex")
        print(f"   main.tex ({PAPER_SRC.stat().st_size:,} bytes)")
    else:
        print("   WARNING: camera_ready.tex not found")
    
    # 2. Copy figures
    print("2. Copying figures...")
    fig_count = 0
    if FIGURES_DIR.exists():
        for f in FIGURES_DIR.glob("*.html"):
            shutil.copy(f, OUT / f.name)
            fig_count += 1
        # Also copy PNG/PDF if they exist
        for ext in ["*.png", "*.pdf", "*.jpg"]:
            for f in FIGURES_DIR.glob(ext):
                shutil.copy(f, OUT / f.name)
    print(f"   {fig_count} figures copied")
    
    # 3. Generate metadata file
    print("3. Generating metadata...")
    meta_file = OUT / "metadata.yaml"
    meta_content = f"""---
title: "{META['title']}"
authors:
  - name: "{META['authors'].split(',')[0].strip()}"
  - name: "{META['authors'].split(',')[1].strip()}"
primary_class: "{META['primary_class']}"
secondary_classes: [{', '.join(f'"{c}"' for c in META['secondary_classes'])}]
license: "{META['license']}"
abstract: |
  {META['abstract']}
comments: "{META['comments']}"
---
"""
    meta_file.write_text(meta_content)
    print(f"   metadata.yaml")
    
    # 4. Generate submission script
    print("4. Generating submission script...")
    script = OUT / "submit.sh"
    script.write_text(f"""#!/bin/bash
# arXiv upload helper
# 1. tar the package: tar -czf submission.tar.gz arxiv_submission/
# 2. Upload to https://arxiv.org/submit
# 3. Fill in the web form with the metadata below

echo "Submission package ready:"
echo "  tar -czf submission.tar.gz arxiv_submission/"
echo ""
echo "METADATA:"
echo "  Title: {META['title']}"
echo "  Authors: {META['authors']}"
echo "  Primary class: {META['primary_class']}"
echo "  Secondary classes: {', '.join(META['secondary_classes'])}"
echo "  License: {META['license']}"
""")
    os.chmod(script, 0o755)
    print(f"   submit.sh")
    
    # 5. Generate archive
    print("5. Generating archive...")
    archive = BASE / "arxiv_submission.tar.gz"
    shutil.make_archive(str(BASE / "arxiv_submission"), 'gztar', OUT.parent, OUT.name)
    print(f"   {archive.name} ({archive.stat().st_size:,} bytes)")
    
    # 6. Summary
    print("\n" + "="*60)
    print("PACKAGE COMPLETE")
    print("="*60)
    total = sum(1 for _ in OUT.rglob("*"))
    print(f"\n  {total} files in {OUT}")
    print(f"  Archive: {archive}")
    print(f"  Size: {archive.stat().st_size:,} bytes")
    print(f"\nTo submit to arXiv:")
    print("  1. Open https://arxiv.org/submit")
    print("  2. Upload arxiv_submission.tar.gz")
    print("  3. Use above metadata")
    print("  4. Click Submit")
    print("="*60)

if __name__ == "__main__":
    create_package()
