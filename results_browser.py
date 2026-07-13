#!/usr/bin/env python3
"""Results Browser — interactive tool to explore results without Python.
Usage: python3 results_browser.py
"""
import csv, json, sys, os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_available_results():
    """List all available result files."""
    files = list(RESULTS_DIR.glob("*.csv")) + list(RESULTS_DIR.glob("*.json"))
    return sorted(files)

def show_menu():
    clear_screen()
    print("="*60)
    print("  RESULTS BROWSER — Bias Interaction Experiment")
    print("="*60)
    
    files = get_available_results()
    if not files:
        print("\n  No results found. Run generate_synthetic_pilot.py first.")
        return None
    
    print(f"\n  {'#':<3} {'File':<50} {'Size':<10}")
    print(f"  {'-'*63}")
    for i, f in enumerate(files, 1):
        size = f.stat().st_size
        if size < 1024:
            size_str = f"{size}B"
        elif size < 1024*1024:
            size_str = f"{size/1024:.1f}KB"
        else:
            size_str = f"{size/1024/1024:.1f}MB"
        name = str(f.relative_to(BASE_DIR))
        print(f"  {i:<3} {name:<50} {size_str:<10}")
    
    print(f"\n  {'q':<3} {'Quit'}")
    print()
    return files

def view_csv(filepath):
    """View a CSV file in a paginated table."""
    clear_screen()
    print(f"Viewing: {filepath.relative_to(BASE_DIR)}")
    print("="*60)
    
    with open(filepath) as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    
    print(f"Rows: {len(rows)} | Columns: {', '.join(headers)}")
    print("-"*60)
    
    # Show first 20 rows
    page_size = 20
    for i, row in enumerate(rows[:page_size]):
        # Show key columns only
        display = {}
        for k in headers[:6]:  # First 6 columns
            display[k] = str(row[k])[:30]
        print(f"  {i+1}. {json.dumps(display)}")
    
    if len(rows) > page_size:
        print(f"  ... and {len(rows) - page_size} more rows")
    
    input(f"\nPress Enter to go back...")

def view_json(filepath):
    """View a JSON file."""
    clear_screen()
    print(f"Viewing: {filepath.relative_to(BASE_DIR)}")
    print("="*60)
    
    with open(filepath) as f:
        try:
            data = json.load(f)
        except:
            data = f.read()
    
    if isinstance(data, dict):
        print(json.dumps(data, indent=2)[:2000])
    elif isinstance(data, list):
        print(f"Array with {len(data)} items")
        print(json.dumps(data[:3], indent=2))
        if len(data) > 3:
            print(f"... and {len(data) - 3} more items")
    else:
        print(str(data)[:2000])
    
    input(f"\nPress Enter to go back...")

def show_summary():
    """Show a quick summary of all results."""
    clear_screen()
    print("="*60)
    print("  QUICK SUMMARY")
    print("="*60)
    
    # Check synthetic pilot
    sp = RESULTS_DIR / "bias_interaction_synthetic.csv"
    if sp.exists():
        with open(sp) as f:
            rows = list(csv.DictReader(f))
        judges = sorted(set(r["judge"] for r in rows))
        print(f"\n  Bias Interaction Synthetic: {len(rows)} rows")
        print(f"  Judges: {', '.join(judges)}")
        
        for j in judges:
            jd = [r for r in rows if r["judge"] == j]
            scores = [float(r["score"]) for r in jd]
            avg = sum(scores)/len(scores)
            print(f"    {j}: avg={avg:.2f}, n={len(jd)}")
    
    # Check root cause
    rc = RESULTS_DIR / "rootcause_synthetic.csv"
    if rc.exists():
        with open(rc) as f:
            rows = list(csv.DictReader(f))
        models = sorted(set(r["model"] for r in rows))
        print(f"\n  Root Cause Synthetic: {len(rows)} rows")
        print(f"  Models: {', '.join(models)}")
    
    # Check real results
    real = list(RESULTS_DIR.glob("results_*.csv"))
    if real:
        print(f"\n  Real Results: {len(real)} judges complete")
        for f in real:
            with open(f) as fh:
                n = len(list(csv.DictReader(fh)))
            print(f"    {f.stem.replace('results_','')}: {n} rows")
    else:
        print(f"\n  Real Results: None yet")
    
    input(f"\nPress Enter to go back...")

def main():
    while True:
        files = show_menu()
        if files is None:
            input("Press Enter...")
            continue
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == 'q' or choice == 'quit':
            break
        elif choice == 's' or choice == 'summary':
            show_summary()
            continue
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                f = files[idx]
                if f.suffix == '.csv':
                    view_csv(f)
                elif f.suffix == '.json':
                    view_json(f)
        except (ValueError, IndexError):
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
