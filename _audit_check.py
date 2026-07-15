#!/usr/bin/env python3
"""Comprehensive audit helper script."""
import json
import os
import glob
import re

PROJECT = r'C:\Users\Admin\Research\research-draft'

def count_figures():
    """Count PNG files in paper/figures/ and \includegraphics calls in the paper."""
    png_dir = os.path.join(PROJECT, 'paper', 'figures')
    png_files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
    print(f"\n=== FIGURES ===")
    print(f"PNG files in paper/figures/: {len(png_files)}")
    for f in sorted(png_files):
        print(f"  {f}")

    # Count includegraphics in camera_ready_full.tex
    paper_path = os.path.join(PROJECT, 'paper', 'camera_ready_full.tex')
    with open(paper_path, 'r') as f:
        content = f.read()

    includes = re.findall(r'\\includegraphics(?:\[.*?\])?\{(.*?)\}', content)
    print(f"\n\\includegraphics calls in paper: {len(includes)}")
    for inc in includes:
        print(f"  {inc}")

    # Check which figures are referenced vs exist
    ref_basenames = set(os.path.basename(inc).strip() for inc in includes)
    png_basenames = set(png_files)
    missing = ref_basenames - png_basenames
    unreferenced = png_basenames - ref_basenames
    if missing:
        print(f"\nMISSING figures (referenced but not found): {missing}")
    if unreferenced:
        print(f"\nUNREFERENCED figures (exist but not in paper): {sorted(unreferenced)}")

    return len(includes), len(png_files)

def check_results():
    """Check data integrity in results files."""
    print(f"\n=== DATA INTEGRITY ===")
    files = {
        't4fam_results.json': os.path.join(PROJECT, 'results_rootcause', 't4fam_results.json'),
        'study1_results.json': os.path.join(PROJECT, 'results_rootcause', 'study1_results.json'),
        'rootcause_analysis.json': os.path.join(PROJECT, 'results_rootcause', 'rootcause_analysis.json'),
    }

    all_models = set()
    total_judgments_est = 0

    for name, path in files.items():
        if not os.path.exists(path):
            print(f"{name}: FILE NOT FOUND")
            continue
        with open(path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            print(f"{name}: {len(data)} items (list)")
            # Try to extract model names
            for item in data[:3]:
                if isinstance(item, dict):
                    print(f"    sample keys: {list(item.keys())[:6]}")
        elif isinstance(data, dict):
            print(f"{name}: {len(data)} keys (dict)")
            print(f"    keys: {list(data.keys())[:10]}")

            # Try different structures
            if 'models' in data:
                all_models.update(data['models'])
            if 'results' in data and isinstance(data['results'], dict):
                all_models.update(data['results'].keys())
        else:
            print(f"{name}: type={type(data).__name__}")

    print(f"\nUnique models across all files: {len(all_models)}")
    if all_models:
        print(f"  Models: {sorted(all_models)}")

def check_paper_audit():
    """Comprehensive paper audit."""
    print(f"\n=== PAPER AUDIT ===")
    paper_path = os.path.join(PROJECT, 'paper', 'camera_ready_full.tex')
    with open(paper_path, 'r') as f:
        content = f.read()

    lines = content.count('\n') + 1
    words = len(content.split())

    # Count things
    figures = len(re.findall(r'\\includegraphics', content))
    tables = len(re.findall(r'\\begin\{table\}', content)) + len(re.findall(r'\\begin\{table\*\}', content))
    refs_count = len(re.findall(r'\\cite\{', content))
    sections = len(re.findall(r'\\section\{', content))
    subsections = len(re.findall(r'\\subsection\{', content))

    # Abstract word count
    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    abstract_words = 0
    if abstract_match:
        abstract_text = abstract_match.group(1)
        # Remove LaTeX commands
        abstract_text = re.sub(r'\\[a-zA-Z]+', '', abstract_text)
        abstract_text = re.sub(r'\{|\}', '', abstract_text)
        abstract_text = re.sub(r'\$.*?\$', '', abstract_text)
        abstract_words = len(abstract_text.split())

    print(f"Lines: {lines}")
    print(f"Words: {words}")
    print(f"Abstract word count: {abstract_words} {'OK (<200)' if abstract_words <= 200 else 'EXCEEDS 200!'}")
    print(f"Figures (\\includegraphics): {figures}")
    print(f"Tables: {tables}")
    print(f"Citations: {refs_count}")
    print(f"Sections: {sections}")
    print(f"Subsections: {subsections}")

    # Check required sections
    required_sections = ['Introduction', 'Method', 'Results', 'Discussion', 'Limitations', 'Broader Impact', 'Conclusion']
    missing_sections = []
    for s in required_sections:
        if not re.search(r'\\section\{' + s, content):
            missing_sections.append(s)

    if missing_sections:
        print(f"\nMISSING sections: {missing_sections}")
    else:
        print(f"\nAll required sections present: OK")

    # Check for placeholder text
    placeholders = ['TODO', 'FIXME', 'XXX', 'TBD', 'CHANGEME']
    found_placeholders = []
    for p in placeholders:
        if p in content:
            found_placeholders.append(p)
    if found_placeholders:
        print(f"\nPLACEHOLDER TEXT FOUND: {found_placeholders}")
    else:
        print(f"\nNo placeholder text found: OK")

    # Check cross-references
    labels = set(re.findall(r'\\label\{([^}]+)\}', content))
    refs = set(re.findall(r'\\ref\{([^}]+)\}', content))
    missing_refs = refs - labels
    if missing_refs:
        print(f"\nMISSING LABELS (\\ref without \\label): {missing_refs}")
    else:
        print(f"\nAll \\ref have matching \\label: OK ({len(refs)} references)")

    # Check bibliography
    bib_path = os.path.join(PROJECT, 'paper', 'references.bib')
    if os.path.exists(bib_path):
        with open(bib_path, 'r') as f:
            bib_content = f.read()
        bib_entries = set(re.findall(r'@\w+\{([^,]+),', bib_content))
        cites = set(re.findall(r'\\cite\{([^}]+)\}', content))
        # Split multi-cites
        all_cites = set()
        for c in cites:
            for part in c.split(','):
                all_cites.add(part.strip())
        missing_cites = all_cites - bib_entries
        if missing_cites:
            print(f"\nMISSING BIB ENTRIES (\\cite without bib entry): {missing_cites}")
        else:
            print(f"\nAll \\cite have matching bib entries: OK ({len(all_cites)} citations)")

    return lines, words, figures, tables, refs_count, sections, abstract_words

def total_file_counts():
    """Count total files and lines in project."""
    print(f"\n=== PROJECT STATS ===")
    total_files = 0
    total_lines = 0
    exts = {}

    for root, dirs, files in os.walk(PROJECT):
        # Skip .git
        if '.git' in root:
            continue
        for f in files:
            ext = os.path.splitext(f)[1]
            exts[ext] = exts.get(ext, 0) + 1
            total_files += 1
            try:
                with open(os.path.join(root, f), 'r', errors='ignore') as fh:
                    total_lines += sum(1 for _ in fh)
            except:
                pass

    print(f"Total non-git files: {total_files}")
    print(f"Total lines: {total_lines}")
    for ext, count in sorted(exts.items(), key=lambda x: -x[1])[:20]:
        print(f"  {ext or '(no ext)'}: {count}")
    return total_files, total_lines

if __name__ == '__main__':
    count_figures()
    check_results()
    check_paper_audit()
    total_file_counts()
    print("\n=== AUDIT COMPLETE ===")
