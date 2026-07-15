#!/usr/bin/env python3
"""
Health Check — Verify project integrity.

Checks:
- All required files exist
- All JSON is valid
- Bib entries match citations in paper
- Python files compile without syntax errors

Usage:
    python scripts/health_check.py [--path DIR]

Exit code: 0 = healthy, non-zero = issues found
"""

from __future__ import annotations
import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


# Required files for a healthy project
REQUIRED_FILES = [
    "README.md",
    "pyproject.toml",
    "Makefile",
    "LICENSE",
    "CITATION.cff",
    "requirements.txt",
    "pytest.ini",
    "cli.py",
    "src/scoring_bias/__init__.py",
    "src/scoring_bias/analysis.py",
    "src/scoring_bias/metrics.py",
    "src/scoring_bias/models.py",
    "src/scoring_bias/visualization.py",
    "tests/conftest.py",
    "tests/test_analysis.py",
    "tests/test_metrics.py",
    "tests/test_models.py",
    "api/app.py",
    "api/requirements.txt",
    "dashboard/app.py",
    "dashboard/requirements.txt",
    "paper/references.bib",
    "data/raw/items_all_conditions.csv",
    "notebooks/01_data_overview.py",
    "notebooks/02_bias_landscape.py",
    "notebooks/03_base_instruct_comparison.py",
    "notebooks/04_bayesian_analysis.py",
    "notebooks/colab_reproduction.py",
    "notebooks/binder_demo.py",
]

# Bib citation keys used in the paper
EXPECTED_BIB_KEYS = [
    "samba2026scoring",
    "li2025scoring",
    "wang2023large",
    "ye2024justice",
    "park2024offsetbias",
    "pan2025user",
    "thakur2024judging",
    "chen2024humans",
    "xu2026position",
    "zheng2023judging",
    "alpacaeval",
    "bai2022constitutional",
    "gu2024survey",
    "llama3",
    "mistral",
    "gemma2",
    "qwen",
    "zhu2023judgelm",
    "shi2024position",
    "zhou2026robust",
    "yang2025debiasing",
    "li2025validating",
]


def check_files(root: Path) -> List[str]:
    """Check that all required files exist."""
    issues: List[str] = []
    for rel_path in REQUIRED_FILES:
        filepath = root / rel_path
        if not filepath.exists():
            issues.append(f"MISSING: {rel_path}")
        elif filepath.stat().st_size == 0:
            issues.append(f"EMPTY: {rel_path}")
    return issues


def check_json_validity(root: Path) -> List[str]:
    """Check that all JSON files parse correctly."""
    issues: List[str] = []
    for json_file in root.rglob("*.json"):
        # Skip node_modules, etc.
        if any(p in json_file.parts for p in (".git", "__pycache__", "node_modules")):
            continue
        try:
            with open(json_file) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            issues.append(f"INVALID JSON: {json_file} — {e}")
    return issues


def check_bib_entries(root: Path) -> List[str]:
    """Check that all bib entries are valid and expected keys exist."""
    issues: List[str] = []
    bib_path = root / "paper" / "references.bib"
    if not bib_path.exists():
        return ["MISSING: paper/references.bib"]

    content = bib_path.read_text()

    # Check for syntax (basic: @ symbol + key)
    entries = re.findall(r'@\w+\{(\w+),', content)
    if not entries:
        return ["NO BIB ENTRIES FOUND: paper/references.bib"]

    # Check expected keys
    for key in EXPECTED_BIB_KEYS:
        if key not in entries:
            issues.append(f"MISSING BIB KEY: {key}")

    # Check for duplicate keys
    seen = {}
    for key in entries:
        if key in seen:
            issues.append(f"DUPLICATE BIB KEY: {key}")
        seen[key] = seen.get(key, 0) + 1

    return issues


def check_python_syntax(root: Path) -> List[str]:
    """Check that all Python files compile without syntax errors."""
    issues: List[str] = []
    for py_file in root.rglob("*.py"):
        # Skip excluded paths
        if any(p in py_file.parts for p in (".git", "__pycache__", "node_modules",
                                              ".ipynb_checkpoints")):
            continue
        # Skip jupytext notebooks (they use shell escapes)
        if py_file.parent.name == "notebooks":
            continue
        try:
            ast.parse(py_file.read_text())
        except SyntaxError as e:
            issues.append(f"SYNTAX ERROR: {py_file} — {e}")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Project health check")
    parser.add_argument("--path", type=str, default=".",
                        help="Project root directory")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    print(f"🔍 Running health check on {root}")
    print("=" * 50)

    all_issues: List[str] = []

    # File existence
    print("\n📁 Checking required files...")
    issues = check_files(root)
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ All required files present")

    # JSON validity
    print("\n🔤 Checking JSON validity...")
    issues = check_json_validity(root)
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ All JSON files valid")

    # Bib entries
    print("\n📚 Checking bib entries...")
    issues = check_bib_entries(root)
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ Bib entries look good")

    # Python syntax
    print("\n🐍 Checking Python syntax...")
    issues = check_python_syntax(root)
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ All Python files compile")

    # Summary
    print("\n" + "=" * 50)
    if all_issues:
        print(f"❌ {len(all_issues)} issue(s) found")
        sys.exit(1)
    else:
        print("✅ Project is healthy!")
        sys.exit(0)


if __name__ == "__main__":
    main()
