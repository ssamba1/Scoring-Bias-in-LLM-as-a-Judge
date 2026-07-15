#!/usr/bin/env python3
"""
Check Credentials — Scan the project for accidentally committed API keys,
tokens, secrets, and credentials. Reports findings with file paths.

Usage:
    python scripts/check_credentials.py [--path DIR] [--verbose]
"""

from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


# Patterns that might indicate credentials
PATTERNS: List[Tuple[str, str]] = [
    # API keys
    (r'(?i)(?:api[_-]?key|apikey|api_key)\s*[:=]\s*["\']?(sk-[a-zA-Z0-9]{20,})["\']?', "OpenAI-style API key"),
    (r'(?i)(?:api[_-]?key|apikey|api_key)\s*[:=]\s*["\']?([a-zA-Z0-9]{32,})["\']?', "Generic API key (32+ chars)"),
    # Tokens
    (r'(?i)(?:token|secret|password|passwd)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "Token/Secret"),
    # Bearer tokens
    (r'(?i)authorization:\s*Bearer\s+[a-zA-Z0-9_\-\.]{20,}', "Bearer token"),
    # SSH keys
    (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "Private SSH key"),
    # .env patterns
    (r'(?i)(OPENAI_API_KEY|ANTHROPIC_API_KEY|HUGGINGFACE_TOKEN|AWS_ACCESS_KEY|GITHUB_TOKEN)\s*=\s*\S+', "Environment variable with key"),
    # JWT tokens
    (r'eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}', "JWT token"),
    # Generic password assignment
    (r'(?i)password\s*=\s*["\'][^"\']{8,}["\']', "Password assignment"),
]

# Files/directories to skip
SKIP_DIRS = {".git", "__pycache__", ".ipynb_checkpoints", "node_modules", "venv", ".venv"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
            ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz", ".bz2", ".parquet",
            ".xlsx", ".pyc", ".ipynb"}  # Skip notebooks - code cells may trip patterns
SKIP_FILES = {".env", ".env.template", ".env.example"}  # Skip template env files


def scan_file(filepath: Path, verbose: bool) -> List[Dict[str, str]]:
    """Scan a single file for credential patterns."""
    findings: List[Dict[str, str]] = []

    try:
        content = filepath.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings

    for pattern, description in PATTERNS:
        for match in re.finditer(pattern, content, re.MULTILINE):
            finding = {
                "file": str(filepath),
                "pattern": description,
                "match": match.group(0)[:80],  # Truncate for display
                "line": content[:match.start()].count("\n") + 1,
            }
            findings.append(finding)
            if verbose:
                print(f"  [{description}] {filepath}:{finding['line']}")

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan for accidentally committed credentials")
    parser.add_argument("--path", type=str, default=".",
                        help="Project root directory")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed findings")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: Path not found: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Scanning {root} for credentials and secrets...")
    print(f"   (skipping: {', '.join(sorted(SKIP_DIRS))})")
    print()

    all_findings: List[Dict[str, str]] = []
    files_scanned = 0

    for filepath in root.rglob("*"):
        # Skip directories
        if filepath.is_dir():
            continue
        # Skip by parent dir
        if any(skip in filepath.parts for skip in SKIP_DIRS):
            continue
        # Skip by extension
        if filepath.suffix in SKIP_EXT:
            continue
        # Skip by filename
        if filepath.name in SKIP_FILES:
            continue
        # Only scan text-like files
        try:
            filepath.read_bytes()[:100]
        except OSError:
            continue

        if filepath.stat().st_size > 500_000:  # Skip files > 500KB
            continue

        files_scanned += 1
        findings = scan_file(filepath, args.verbose)
        all_findings.extend(findings)

    # Report
    if all_findings:
        print(f"\n⚠️  Found {len(all_findings)} potential credential(s) in {files_scanned} files scanned:")
        print("-" * 60)
        for f in all_findings:
            print(f"  [{f['pattern']}]")
            print(f"    File: {f['file']}:{f['line']}")
            print(f"    Match: {f['match']}")
            print()
        sys.exit(1)
    else:
        print(f"✅ No credentials found in {files_scanned} files scanned.")
        sys.exit(0)


if __name__ == "__main__":
    main()
