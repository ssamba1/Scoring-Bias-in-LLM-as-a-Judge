#!/usr/bin/env python3
"""
Experiment Tracking System — hashes configurations, versions results, logs all parameters.
Ensures full reproducibility of every experiment run.
"""
import argparse, csv, json, hashlib, os, sys, time, datetime, platform
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent.parent
TRACKING_DIR = BASE_DIR / "experiment_tracking"
TRACKING_DIR.mkdir(exist_ok=True)

class ExperimentTracker:
    """Tracks experiment configurations, runs, and results."""

    def __init__(self):
        self.db_path = TRACKING_DIR / "experiment_log.json"
        self.log = self._load_log()

    def _load_log(self) -> List[Dict]:
        if self.db_path.exists():
            with open(self.db_path) as f:
                return json.load(f)
        return []

    def _save_log(self):
        with open(self.db_path, "w") as f:
            json.dump(self.log, f, indent=2)

    def _hash_config(self, config: Dict) -> str:
        """Generate a deterministic hash of the configuration."""
        serialized = json.dumps(config, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def _system_fingerprint(self) -> Dict:
        """Capture system information for reproducibility."""
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "timestamp": datetime.datetime.now().isoformat(),
            "hostname": platform.node(),
        }

    def register_experiment(self, name: str, config: Dict,
                            description: str = "") -> str:
        """Register a new experiment and return its ID."""
        config_hash = self._hash_config(config)
        experiment_id = f"exp_{config_hash}_{len(self.log):04d}"

        entry = {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "config": config,
            "config_hash": config_hash,
            "system": self._system_fingerprint(),
            "status": "registered",
            "created_at": datetime.datetime.now().isoformat(),
            "results": {},
            "artifacts": [],
        }
        self.log.append(entry)
        self._save_log()
        return experiment_id

    def start_run(self, experiment_id: str) -> bool:
        """Mark an experiment as running."""
        for entry in self.log:
            if entry["experiment_id"] == experiment_id:
                entry["status"] = "running"
                entry["started_at"] = datetime.datetime.now().isoformat()
                self._save_log()
                return True
        return False

    def complete_run(self, experiment_id: str, results: Dict,
                     artifacts: List[str] = None):
        """Mark an experiment as complete with results."""
        for entry in self.log:
            if entry["experiment_id"] == experiment_id:
                entry["status"] = "completed"
                entry["completed_at"] = datetime.datetime.now().isoformat()
                entry["duration_seconds"] = (
                    datetime.datetime.fromisoformat(entry["completed_at"]) -
                    datetime.datetime.fromisoformat(entry.get("started_at", entry["created_at"]))
                ).total_seconds()
                entry["results"] = results
                entry["artifacts"] = artifacts or []
                self._save_log()
                return True
        return False

    def fail_run(self, experiment_id: str, error: str):
        """Mark an experiment as failed."""
        for entry in self.log:
            if entry["experiment_id"] == experiment_id:
                entry["status"] = "failed"
                entry["error"] = error
                entry["failed_at"] = datetime.datetime.now().isoformat()
                self._save_log()
                return True
        return False

    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Get experiment by ID."""
        for entry in self.log:
            if entry["experiment_id"] == experiment_id:
                return entry
        return None

    def list_experiments(self, status: str = None) -> List[Dict]:
        """List all experiments, optionally filtered by status."""
        entries = self.log
        if status:
            entries = [e for e in entries if e["status"] == status]
        return entries

    def summary(self):
        """Print a summary of all experiments."""
        if not self.log:
            print("No experiments tracked yet.")
            return

        print(f"\n{'='*70}")
        print(f"EXPERIMENT TRACKING SUMMARY ({len(self.log)} total)")
        print(f"{'='*70}")
        print(f"{'ID':<25} {'Name':<25} {'Status':<12} {'Duration':<10}")
        print(f"{'-'*72}")
        for e in self.log:
            dur = e.get("duration_seconds", 0)
            dur_str = f"{dur:.0f}s" if dur < 3600 else f"{dur/3600:.1f}h"
            print(f"{e['experiment_id']:<25} {e['name']:<25} "
                  f"{e['status']:<12} {dur_str:<10}")

        completed = sum(1 for e in self.log if e["status"] == "completed")
        failed = sum(1 for e in self.log if e["status"] == "failed")
        running = sum(1 for e in self.log if e["status"] == "running")
        print(f"\n  Completed: {completed} | Failed: {failed} | Running: {running}")

    def compare_configs(self, id1: str, id2: str) -> Dict:
        """Compare two experiment configurations."""
        e1 = self.get_experiment(id1)
        e2 = self.get_experiment(id2)
        if not e1 or not e2:
            return {"error": "Experiment not found"}

        c1 = e1["config"]
        c2 = e2["config"]

        differences = []
        all_keys = set(list(c1.keys()) + list(c2.keys()))
        for key in sorted(all_keys):
            v1 = c1.get(key)
            v2 = c2.get(key)
            if v1 != v2:
                differences.append({"key": key, "value1": v1, "value2": v2})

        return {
            "id1": id1, "id2": id2,
            "name1": e1["name"], "name2": e2["name"],
            "n_differences": len(differences),
            "differences": differences,
            "same_config": len(differences) == 0,
        }

    def export_as_reproducible(self, experiment_id: str, output_path: Path = None) -> Dict:
        """Export a complete reproducible package for an experiment."""
        entry = self.get_experiment(experiment_id)
        if not entry:
            return {"error": "Not found"}

        package = {
            "reproducible_experiment": {
                "experiment_id": entry["experiment_id"],
                "name": entry["name"],
                "description": entry["description"],
                "config": entry["config"],
                "config_hash": entry["config_hash"],
                "system": entry["system"],
            },
            "reproducibility_instructions": {
                "python": entry["system"]["python_version"],
                "platform": entry["system"]["platform"],
                "config_hash_verification": f"python -c \"import hashlib, json; "
                    f"print(hashlib.sha256(json.dumps({json.dumps(entry['config'])}, sort_keys=True).encode()).hexdigest()[:16])\"",
            }
        }

        if output_path:
            with open(output_path, "w") as f:
                json.dump(package, f, indent=2)
            print(f"Reproducible package: {output_path}")

        return package

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command",
        choices=["register", "start", "complete", "fail", "list", "summary",
                 "compare", "export", "status"])
    parser.add_argument("--experiment", help="Experiment ID")
    parser.add_argument("--name", help="Experiment name")
    parser.add_argument("--description", default="")
    parser.add_argument("--config", default="{}", help="JSON config string")
    parser.add_argument("--results", default="{}", help="JSON results string")
    parser.add_argument("--error", help="Error message for failed runs")
    parser.add_argument("--compare", nargs=2, help="Compare two experiment IDs")
    parser.add_argument("--output", help="Output path for export")
    args = parser.parse_args()

    tracker = ExperimentTracker()

    if args.command == "register":
        config = json.loads(args.config) if isinstance(args.config, str) else args.config or {}
        eid = tracker.register_experiment(args.name or "unnamed", config, args.description)
        print(f"Registered: {eid}")
        print(f"  Config hash: {eid.split('_')[1]}")
        print(f"  To start: python3 experiment_tracker.py start --experiment {eid}")

    elif args.command == "start":
        if not args.experiment:
            print("Need --experiment. Run 'register' first.")
            return
        if tracker.start_run(args.experiment):
            print(f"Started: {args.experiment}")
        else:
            print(f"Experiment not found: {args.experiment}")

    elif args.command == "complete":
        if not args.experiment:
            print("Need --experiment")
            return
        results = json.loads(args.results) if isinstance(args.results, str) else args.results or {}
        tracker.complete_run(args.experiment, results)
        print(f"Completed: {args.experiment}")

    elif args.command == "fail":
        if not args.experiment:
            print("Need --experiment")
            return
        tracker.fail_run(args.experiment, args.error or "Unknown error")
        print(f"Failed: {args.experiment}")

    elif args.command == "list":
        for e in tracker.list_experiments():
            print(f"  {e['experiment_id']:<30} {e['name']:<30} {e['status']:<12}")

    elif args.command == "summary":
        tracker.summary()

    elif args.command == "compare":
        if args.compare:
            result = tracker.compare_configs(args.compare[0], args.compare[1])
            if "error" in result:
                print(f"Error: {result['error']}")
            elif result["same_config"]:
                print("Configurations are IDENTICAL")
            else:
                print(f"Configurations DIFFER ({result['n_differences']} differences):")
                for d in result["differences"]:
                    print(f"  {d['key']}: {d['value1']} → {d['value2']}")

    elif args.command == "export":
        if not args.experiment:
            print("Need --experiment")
            return
        tracker.export_as_reproducible(args.experiment, Path(args.output) if args.output else None)

    elif args.command == "status":
        tracker.summary()

if __name__ == "__main__":
    main()
