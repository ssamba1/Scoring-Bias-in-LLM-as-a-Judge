#!/usr/bin/env python3
"""Progress tracker — CLI dashboard for experiment status.
Reports which judges have been run, analysis progress, and next steps.
"""
import csv, json, os
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

def check_judges():
    """Check which judges have results."""
    completed = []
    pending = ["claude", "gpt4o", "gemini", "deepseek", "llama"]
    
    for f in Path(RESULTS_DIR).glob("results_*.csv"):
        judge = f.stem.replace("results_", "")
        if judge in pending:
            pending.remove(judge)
            completed.append(judge)
    
    return completed, pending

def check_analysis():
    """Check analysis status."""
    status = {}
    status["synthetic_pilot"] = (RESULTS_DIR / "bias_interaction_synthetic.csv").exists()
    status["root_cause_synthetic"] = (RESULTS_DIR / "rootcause_synthetic.csv").exists()
    status["summary_json"] = (RESULTS_DIR / "synthetic_summary.json").exists()
    status["figures"] = list((BASE_DIR / "paper/figures").glob("*.png"))
    return status

def check_db():
    """Check database status."""
    db_path = RESULTS_DIR / "experiment.db"
    return db_path.exists()

def print_dashboard():
    """Print the experiment dashboard."""
    print("="*65)
    print("LLM-as-a-Judge BIAS RESEARCH — EXPERIMENT DASHBOARD")
    print("="*65)
    
    # Judge status
    completed, pending = check_judges()
    print(f"\n📊 JUDGE STATUS ({len(completed)}/5 complete)")
    for j in completed:
        path = RESULTS_DIR / f"results_{j}.csv"
        with open(path) as f:
            n = len(list(csv.DictReader(f)))
        print(f"  ✅ {j:<12} {n} results")
    for j in pending:
        print(f"  ⏳ {j:<12} not run yet")
    
    # Analysis status
    analysis = check_analysis()
    print(f"\n🔬 ANALYSIS STATUS")
    print(f"  {'Synthetic pilot:' if analysis['synthetic_pilot'] else '  Synthetic pilot:'} {'✅ generated' if analysis['synthetic_pilot'] else '⏳ pending'}")
    print(f"  {'Root cause synthetic:' if analysis['root_cause_synthetic'] else '  Root cause synthetic:'} {'✅ generated' if analysis['root_cause_synthetic'] else '⏳ pending'}")
    print(f"  {'Summary JSON:' if analysis['summary_json'] else '  Summary JSON:'} {'✅ saved' if analysis['summary_json'] else '⏳ pending'}")
    print(f"  Figures: {len(analysis['figures'])} generated")
    
    # Database
    if check_db():
        db_path = RESULTS_DIR / "experiment.db"
        size_mb = os.path.getsize(db_path) / 1024 / 1024
        print(f"\n🗄️  DATABASE: ✅ exists ({size_mb:.1f} MB)")
    else:
        print(f"\n🗄️  DATABASE: ⏳ not created yet")
    
    # Paper status
    paper_dir = BASE_DIR / "paper"
    paper_files = list(paper_dir.glob("*.md")) + list(paper_dir.glob("*.tex")) + list(paper_dir.glob("*.bib"))
    print(f"\n📝 PAPER: {len(paper_files)} files")
    for f in paper_files:
        size_kb = os.path.getsize(f) / 1024
        print(f"  {'📄' if f.suffix == '.md' else '📑' if f.suffix == '.tex' else '📚'} {f.name:<30} {size_kb:.1f} KB")
    
    # Next steps
    print(f"\n🎯 NEXT STEPS")
    if pending:
        print(f"  Run pending judges: {' '.join(pending)}")
    else:
        print(f"  ✅ All judges complete — proceed to analysis")
    
    if not analysis["figures"]:
        print(f"  Generate figures: python3 pipeline_biasinteraction/generate_figures.py")
    
    print(f"  Explore results: python3 explore_results.py")
    print(f"  Run tests: python3 tests/run_tests.py")
    print(f"\n{'='*65}")

if __name__ == "__main__":
    print_dashboard()
