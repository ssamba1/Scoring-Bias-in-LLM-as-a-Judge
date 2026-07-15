#!/usr/bin/env python3
"""
Export Data — Export all analysis results to various formats.

Usage:
    python scripts/export_data.py [--format csv|excel|json|parquet] [--output DIR] [--input FILE]
"""

from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_data(input_path: Path) -> List[Dict[str, Any]]:
    """Load analysis data from CSV or JSON."""
    if not input_path.exists():
        print(f"Error: Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix == ".json":
        with open(input_path) as f:
            return json.load(f)
    elif input_path.suffix == ".csv":
        with open(input_path, newline="") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported input format: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)


def export_csv(data: List[Dict[str, Any]], output_path: Path) -> None:
    """Export to CSV."""
    if not data:
        print("Warning: No data to export")
        return
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ CSV exported: {output_path} ({len(data)} rows)")


def export_json(data: List[Dict[str, Any]], output_path: Path) -> None:
    """Export to JSON."""
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ JSON exported: {output_path} ({len(data)} entries)")


def export_excel(data: List[Dict[str, Any]], output_path: Path) -> None:
    """Export to Excel (.xlsx)."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas required for Excel export. pip install pandas", file=sys.stderr)
        sys.exit(1)
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"✓ Excel exported: {output_path} ({len(data)} rows)")


def export_parquet(data: List[Dict[str, Any]], output_path: Path) -> None:
    """Export to Parquet."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas required for Parquet export. pip install pandas", file=sys.stderr)
        sys.exit(1)
    try:
        import pyarrow  # noqa: F401
    except ImportError:
        print("Error: pyarrow required for Parquet export. pip install pyarrow", file=sys.stderr)
        sys.exit(1)
    df = pd.DataFrame(data)
    df.to_parquet(output_path, index=False)
    print(f"✓ Parquet exported: {output_path} ({len(data)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export analysis results to various formats")
    parser.add_argument("--format", choices=["csv", "excel", "json", "parquet"],
                        default="csv", help="Output format")
    parser.add_argument("--output", "-o", type=str, default="output/export",
                        help="Output directory")
    parser.add_argument("--input", "-i", type=str,
                        default="output/deltas.json",
                        help="Input data file (CSV or JSON)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_data(input_path)
    if not data:
        print("Warning: No data loaded from input file")

    fmt_map = {
        "csv": ("export.csv", export_csv),
        "json": ("export.json", export_json),
        "excel": ("export.xlsx", export_excel),
        "parquet": ("export.parquet", export_parquet),
    }

    filename, exporter = fmt_map[args.format]
    output_path = output_dir / filename
    exporter(data, output_path)


if __name__ == "__main__":
    main()
