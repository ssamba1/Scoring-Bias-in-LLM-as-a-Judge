#!/usr/bin/env python3
"""
scoring-bias CLI  Command-line interface for scoring bias analysis.

Usage:
    scoring-bias compute-deltas [--input FILE] [--output DIR]
    scoring-bias compute-flip-rates [--input FILE] [--output DIR]
    scoring-bias bootstrap-ci [--input FILE] [--output DIR] [--n-resamples N]
    scoring-bias generate-figures [--input FILE] [--output DIR] [--format png|pdf|svg]
    scoring-bias run-all [--input FILE] [--output DIR]

Options:
    --input FILE     Input data file (CSV) [default: data/raw/items_all_conditions.csv]
    --output DIR     Output directory [default: output/]
    --n-resamples N  Bootstrap resamples [default: 10000]
    --format fmt     Figure format [default: png]
"""

from __future__ import annotations
import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


# ── Helpers ──


def _resolve_path(p: str, base_dir: Path) -> Path:
    """Resolve path relative to project root if not absolute."""
    path = Path(p)
    if path.is_absolute():
        return path
    return base_dir / path


def _load_data(filepath: Path) -> List[Dict[str, str]]:
    """Load CSV data file with error handling."""
    if not filepath.exists():
        print(f"Error: Input file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        print(f"Error: Empty CSV file: {filepath}", file=sys.stderr)
        sys.exit(1)
    return rows


def _ensure_output_dir(output_dir: Path) -> Path:
    """Create output directory if needed."""
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ── Command implementations ──


def cmd_compute_deltas(args: argparse.Namespace) -> None:
    """Compute bias deltas (Δ = treatment - control) for all models and probes."""
    data = _load_data(args.input_file)
    output_dir = _ensure_output_dir(args.output_dir)

    # Group by model and probe
    results: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
    for row in data:
        model = row.get("model_name", "unknown")
        probe = row.get("probe", "unknown")
        condition = row.get("condition", "normal")
        try:
            score = float(row.get("score", 0))
        except (ValueError, TypeError):
            continue
        results.setdefault(model, {}).setdefault(probe, {}).setdefault(condition, []).append(score)

    # Compute deltas
    deltas_output = []
    for model, probes in sorted(results.items()):
        for probe, conditions in sorted(probes.items()):
            control = conditions.get("normal", [])
            treatment_keys = [k for k in conditions if k != "normal"]
            for trt_key in treatment_keys:
                treatment = conditions[trt_key]
                if control and treatment:
                    delta = sum(treatment) / len(treatment) - sum(control) / len(control)
                    deltas_output.append({
                        "model_name": model,
                        "probe": probe,
                        "control_condition": "normal",
                        "treatment_condition": trt_key,
                        "delta": round(delta, 4),
                        "n_control": len(control),
                        "n_treatment": len(treatment),
                    })

    # Save
    output_path = output_dir / "deltas.json"
    with open(output_path, "w") as f:
        json.dump(deltas_output, f, indent=2)
    print(f"Saved {len(deltas_output)} delta entries to {output_path}")

    # Also print summary
    print(f"\nDelta Summary ({len(deltas_output)} entries):")
    for entry in deltas_output[:10]:
        print(f"  {entry['model_name']:30s} | {entry['probe']:20s} | Δ = {entry['delta']:+.4f}")
    if len(deltas_output) > 10:
        print(f"  ... and {len(deltas_output) - 10} more")


def cmd_compute_flip_rates(args: argparse.Namespace) -> None:
    """Compute flip rates for all model-probe combinations."""
    data = _load_data(args.input_file)
    output_dir = _ensure_output_dir(args.output_dir)

    results: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
    for row in data:
        model = row.get("model_name", "unknown")
        probe = row.get("probe", "unknown")
        condition = row.get("condition", "normal")
        try:
            score = float(row.get("score", 0))
        except (ValueError, TypeError):
            continue
        results.setdefault(model, {}).setdefault(probe, {}).setdefault(condition, []).append(score)

    flip_output = []
    for model, probes in sorted(results.items()):
        for probe, conditions in sorted(probes.items()):
            control = conditions.get("normal", [])
            treatment_keys = [k for k in conditions if k != "normal"]
            for trt_key in treatment_keys:
                treatment = conditions[trt_key]
                if control and treatment and len(control) == len(treatment):
                    flips = sum(1 for c, t in zip(control, treatment) if abs(c - t) >= 0.5)
                    flip_rate = flips / len(control)
                    flip_output.append({
                        "model_name": model,
                        "probe": probe,
                        "treatment_condition": trt_key,
                        "flip_rate": round(flip_rate, 4),
                        "flips": flips,
                        "total": len(control),
                    })

    output_path = output_dir / "flip_rates.json"
    with open(output_path, "w") as f:
        json.dump(flip_output, f, indent=2)
    print(f"Saved {len(flip_output)} flip-rate entries to {output_path}")

    for entry in flip_output[:10]:
        print(f"  {entry['model_name']:30s} | {entry['probe']:20s} | flip_rate = {entry['flip_rate']:.2%}")
    if len(flip_output) > 10:
        print(f"  ... and {len(flip_output) - 10} more")


def cmd_bootstrap_ci(args: argparse.Namespace) -> None:
    """Bootstrap confidence intervals for bias deltas."""
    import random
    from statistics import mean

    data = _load_data(args.input_file)
    output_dir = _ensure_output_dir(args.output_dir)
    n_resamples = args.n_resamples

    results: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
    for row in data:
        model = row.get("model_name", "unknown")
        probe = row.get("probe", "unknown")
        condition = row.get("condition", "normal")
        try:
            score = float(row.get("score", 0))
        except (ValueError, TypeError):
            continue
        results.setdefault(model, {}).setdefault(probe, {}).setdefault(condition, []).append(score)

    ci_output = []
    for model, probes in sorted(results.items()):
        for probe, conditions in sorted(probes.items()):
            control = conditions.get("normal", [])
            treatment_keys = [k for k in conditions if k != "normal"]
            for trt_key in treatment_keys:
                treatment = conditions[trt_key]
                if not control or not treatment or len(control) != len(treatment):
                    continue

                paired_deltas = [t - c for c, t in zip(control, treatment)]
                observed = mean(paired_deltas)
                n = len(paired_deltas)

                # Bootstrap
                boot_means = []
                random.seed(42)
                for _ in range(n_resamples):
                    resample = [random.choice(paired_deltas) for _ in range(n)]
                    boot_means.append(mean(resample))

                boot_means.sort()
                lower_idx = int(n_resamples * 0.025)
                upper_idx = int(n_resamples * 0.975)
                ci_lower = boot_means[lower_idx]
                ci_upper = boot_means[upper_idx]

                ci_output.append({
                    "model_name": model,
                    "probe": probe,
                    "treatment_condition": trt_key,
                    "delta": round(observed, 4),
                    "ci_lower": round(ci_lower, 4),
                    "ci_upper": round(ci_upper, 4),
                    "ci_level": 0.95,
                    "n_resamples": n_resamples,
                    "n_pairs": n,
                })

    output_path = output_dir / "bootstrap_ci.json"
    with open(output_path, "w") as f:
        json.dump(ci_output, f, indent=2)
    print(f"Saved {len(ci_output)} bootstrap CI entries to {output_path}")

    for entry in ci_output[:8]:
        print(f"  {entry['model_name']:30s} | {entry['probe']:20s} | "
              f"Δ={entry['delta']:+.4f} [{entry['ci_lower']:.4f}, {entry['ci_upper']:.4f}]")
    if len(ci_output) > 8:
        print(f"  ... and {len(ci_output) - 8} more")


def cmd_generate_figures(args: argparse.Namespace) -> None:
    """Generate publication-quality figures."""
    output_dir = _ensure_output_dir(args.output_dir)
    fig_format = args.format

    print("Generating figures...")
    try:
        from scoring_bias.analysis import compute_model_summary
        from scoring_bias.visualization import (
            plot_bias_landscape,
            plot_flip_rate_chart,
        )
        from scoring_bias.models import BiasResult, ProbeType
    except ImportError as e:
        print(f"Error: Cannot import scoring_bias package ({e}).", file=sys.stderr)
        print("Install with: pip install -e .", file=sys.stderr)
        sys.exit(1)

    # Load data and build BiasResult
    data = _load_data(args.input_file)

    # Aggregate scores by model, probe, condition
    by_model: Dict[str, Dict[str, List[float]]] = {}
    probe_map: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
    for row in data:
        model = row.get("model_name", "unknown")
        probe = row.get("probe", "rubric_order")
        condition = row.get("condition", "normal")
        try:
            score = float(row.get("score", 0))
        except (ValueError, TypeError):
            continue

        if model not in probe_map:
            probe_map[model] = {}
        if probe not in probe_map[model]:
            probe_map[model][probe] = {}
        if condition not in probe_map[model][probe]:
            probe_map[model][probe][condition] = []
        probe_map[model][probe][condition].append(score)

    # Build BiasResult
    result = BiasResult()
    for model_name, probes in probe_map.items():
        profile = compute_model_summary(
            model_name,
            {ProbeType(k): v for k, v in probes.items()},
        )
        result.model_profiles[model_name] = profile

    # Generate figures
    if result.model_profiles:
        fig1 = plot_bias_landscape(result, save_path=str(output_dir / f"bias_landscape.{fig_format}"))
        print(f"  ✓ bias_landscape.{fig_format}")

        fig2 = plot_flip_rate_chart(result, save_path=str(output_dir / f"flip_rates.{fig_format}"))
        print(f"  ✓ flip_rates.{fig_format}")

        # Per-model probe breakdowns
        for mname in list(result.model_profiles.keys())[:5]:
            from scoring_bias.visualization import plot_probe_breakdown
            safe_name = mname.replace("/", "_").replace(" ", "_")
            fig3 = plot_probe_breakdown(
                result.model_profiles[mname],
                save_path=str(output_dir / f"probe_breakdown_{safe_name}.{fig_format}"),
            )
            print(f"  ✓ probe_breakdown_{safe_name}.{fig_format}")

    print(f"\nAll figures saved to {output_dir}/")


def cmd_run_all(args: argparse.Namespace) -> None:
    """Run the full analysis pipeline: deltas → flip rates → CI → figures."""
    print("=" * 60)
    print("  Scoring Bias Analysis  Full Pipeline")
    print("=" * 60)

    # Step 1: Deltas
    print("\n[1/4] Computing bias deltas...")
    cmd_compute_deltas(args)

    # Step 2: Flip rates
    print("\n[2/4] Computing flip rates...")
    cmd_compute_flip_rates(args)

    # Step 3: Bootstrap CI
    print("\n[3/4] Bootstrapping confidence intervals...")
    cmd_bootstrap_ci(args)

    # Step 4: Figures
    print("\n[4/4] Generating figures...")
    cmd_generate_figures(args)

    print("\n" + "=" * 60)
    print(f"  Pipeline complete. All outputs in {args.output_dir}")
    print("=" * 60)


# ── Main CLI ──


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="scoring-bias: LLM-as-a-Judge Scoring Bias Analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scoring-bias run-all
  scoring-bias compute-deltas --output results/deltas/
  scoring-bias generate-figures --format pdf
  scoring-bias bootstrap-ci --n-resamples 50000
        """,
    )

    # Global defaults
    base_dir = Path(__file__).parent.resolve()

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # compute-deltas
    p_deltas = subparsers.add_parser("compute-deltas", help="Compute bias deltas")
    p_deltas.add_argument("--input", dest="input_file", type=str,
                          default=str(base_dir / "data" / "raw" / "items_all_conditions.csv"),
                          help="Input CSV file")
    p_deltas.add_argument("--output", dest="output_dir", type=str,
                          default=str(base_dir / "output"),
                          help="Output directory")
    p_deltas.set_defaults(func=cmd_compute_deltas)

    # compute-flip-rates
    p_flip = subparsers.add_parser("compute-flip-rates", help="Compute score flip rates")
    p_flip.add_argument("--input", dest="input_file", type=str,
                        default=str(base_dir / "data" / "raw" / "items_all_conditions.csv"),
                        help="Input CSV file")
    p_flip.add_argument("--output", dest="output_dir", type=str,
                        default=str(base_dir / "output"),
                        help="Output directory")
    p_flip.set_defaults(func=cmd_compute_flip_rates)

    # bootstrap-ci
    p_bs = subparsers.add_parser("bootstrap-ci", help="Bootstrap confidence intervals")
    p_bs.add_argument("--input", dest="input_file", type=str,
                      default=str(base_dir / "data" / "raw" / "items_all_conditions.csv"),
                      help="Input CSV file")
    p_bs.add_argument("--output", dest="output_dir", type=str,
                      default=str(base_dir / "output"),
                      help="Output directory")
    p_bs.add_argument("--n-resamples", dest="n_resamples", type=int, default=10_000,
                      help="Number of bootstrap resamples")
    p_bs.set_defaults(func=cmd_bootstrap_ci)

    # generate-figures
    p_fig = subparsers.add_parser("generate-figures", help="Generate figures")
    p_fig.add_argument("--input", dest="input_file", type=str,
                       default=str(base_dir / "data" / "raw" / "items_all_conditions.csv"),
                       help="Input CSV file")
    p_fig.add_argument("--output", dest="output_dir", type=str,
                       default=str(base_dir / "output" / "figures"),
                       help="Output directory")
    p_fig.add_argument("--format", dest="format", type=str, default="png",
                       choices=["png", "pdf", "svg"], help="Figure format")
    p_fig.set_defaults(func=cmd_generate_figures)

    # run-all
    p_all = subparsers.add_parser("run-all", help="Run full analysis pipeline")
    p_all.add_argument("--input", dest="input_file", type=str,
                       default=str(base_dir / "data" / "raw" / "items_all_conditions.csv"),
                       help="Input CSV file")
    p_all.add_argument("--output", dest="output_dir", type=str,
                       default=str(base_dir / "output"),
                       help="Output directory")
    p_all.set_defaults(func=cmd_run_all)

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Convert string paths to Path objects
    args.input_file = Path(args.input_file)
    args.output_dir = Path(args.output_dir)

    args.func(args)


if __name__ == "__main__":
    main()
