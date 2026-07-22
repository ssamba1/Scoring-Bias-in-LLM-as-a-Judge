#!/usr/bin/env python3
"""Results archiving system  snapshot, version, and compare experiment results.
Usage: python3 archive_results.py --snapshot
       python3 archive_results.py --list
       python3 archive_results.py --compare snapshot_001 snapshot_002
"""
import csv, json, os, shutil, datetime, sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
ARCHIVE_DIR = BASE_DIR / "results_archive"

def create_snapshot(description=""):
    """Create a timestamped snapshot of current results."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"snapshot_{timestamp}"
    snapshot_path = ARCHIVE_DIR / snapshot_name

    os.makedirs(snapshot_path, exist_ok=True)

    # Copy all result files
    copied = 0
    for f in RESULTS_DIR.glob("*"):
        if f.is_file():
            shutil.copy2(f, snapshot_path / f.name)
            copied += 1

    # Save metadata
    meta = {
        "snapshot": snapshot_name,
        "timestamp": timestamp,
        "description": description,
        "n_files": copied,
        "files": [f.name for f in RESULTS_DIR.glob("*") if f.is_file()],
    }

    with open(snapshot_path / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Snapshot created: {snapshot_name}")
    print(f"  Files archived: {copied}")
    print(f"  Location: {snapshot_path}")
    return snapshot_name

def list_snapshots():
    """List all available snapshots."""
    snapshots = sorted(ARCHIVE_DIR.glob("snapshot_*"))

    if not snapshots:
        print("No snapshots found.")
        return []

    print(f"\n{'Snapshot':<25} {'Date':<20} {'Files':<8} {'Description':<30}")
    print("-"*83)

    snap_list = []
    for s in snapshots:
        meta_path = s / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            name = meta["snapshot"]
            date = meta["timestamp"]
            n_files = meta.get("n_files", "?")
            desc = meta.get("description", "")
            print(f"{name:<25} {date:<20} {n_files:<8} {desc:<30}")
            snap_list.append(name)

    return snap_list

def compare_snapshots(snap1, snap2):
    """Compare two snapshots and show differences."""
    path1 = ARCHIVE_DIR / snap1
    path2 = ARCHIVE_DIR / snap2

    if not path1.exists():
        print(f"Snapshot not found: {snap1}")
        return
    if not path2.exists():
        print(f"Snapshot not found: {snap2}")
        return

    print(f"\nComparing: {snap1} vs {snap2}")
    print("="*60)

    # Compare CSV files
    for csv_file in ["bias_interaction_synthetic.csv"]:
        f1 = path1 / csv_file
        f2 = path2 / csv_file

        if f1.exists() and f2.exists():
            with open(f1) as f:
                d1 = list(csv.DictReader(f))
            with open(f2) as f:
                d2 = list(csv.DictReader(f))

            print(f"\n{csv_file}:")
            print(f"  Snapshot 1: {len(d1)} rows")
            print(f"  Snapshot 2: {len(d2)} rows")

            if d1 and d2:
                # Compare mean scores
                judges1 = set(r["judge"] for r in d1)
                judges2 = set(r["judge"] for r in d2)

                common_judges = judges1 & judges2
                if common_judges:
                    print(f"\n  Per-judge comparison:")
                    for judge in sorted(common_judges):
                        s1 = [float(r["score"]) for r in d1 if r["judge"] == judge]
                        s2 = [float(r["score"]) for r in d2 if r["judge"] == judge]
                        if s1 and s2:
                            m1 = sum(s1)/len(s1)
                            m2 = sum(s2)/len(s2)
                            delta = m2 - m1
                            print(f"    {judge:<12} {m1:.3f} → {m2:.3f} (Δ={delta:+.3f})")

def archive_current(description=""):
    """Convenience: snapshot current results."""
    return create_snapshot(description)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 archive_results.py --snapshot [description]")
        print("  python3 archive_results.py --list")
        print("  python3 archive_results.py --compare snap1 snap2")
        print("  python3 archive_results.py --archive [description]")
        return

    cmd = sys.argv[1]

    if cmd == "--snapshot":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        create_snapshot(desc)
    elif cmd == "--list":
        list_snapshots()
    elif cmd == "--compare" and len(sys.argv) >= 4:
        compare_snapshots(sys.argv[2], sys.argv[3])
    elif cmd == "--archive":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        archive_current(desc)
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
