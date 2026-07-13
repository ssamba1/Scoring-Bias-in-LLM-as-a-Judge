#!/usr/bin/env python3
"""
Automated Experiment Scheduler — runs batches of experiments at scheduled times.
Designed for overnight/unattended execution of API-based experiments.
"""
import argparse, csv, json, os, sys, time, datetime, subprocess, threading, signal
from pathlib import Path
from typing import List, Optional, Dict

BASE_DIR = Path(__file__).parent.parent
SCHEDULE_DIR = BASE_DIR / "schedules"

class ExperimentScheduler:
    """Schedule and execute batches of experiments."""

    def __init__(self, schedule_path: Optional[Path] = None):
        self.schedule_path = Path(schedule_path) if schedule_path else SCHEDULE_DIR / "default_schedule.json"
        self.schedule_path.parent.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.current_process = None

    def create_schedule(self, judges: List[str], probes: List[str] = None,
                        items: int = None, repeats: int = 3,
                        stagger_delay: int = 60,
                        output_path: Optional[Path] = None) -> Path:
        """Create an experiment schedule."""
        schedule = {
            "created_at": datetime.datetime.now().isoformat(),
            "judges": judges,
            "probes": probes or ["rubric_order", "score_id", "reference_answer",
                                 "position", "verbosity", "sentiment"],
            "items": items or 400,
            "repeats": repeats,
            "stagger_delay_seconds": stagger_delay,
            "estimated_total_hours": self._estimate_hours(judges, items, repeats),
            "experiments": [],
        }

        # Generate individual experiment entries
        for judge in judges:
            for probe in schedule["probes"]:
                schedule["experiments"].append({
                    "judge": judge,
                    "probe": probe,
                    "items": schedule["items"],
                    "repeats": schedule["repeats"],
                    "estimated_seconds": self._estimate_seconds(items, repeats),
                    "status": "pending",
                })

        output_path = output_path or SCHEDULE_DIR / f"schedule_{len(judges)}judges.json"
        with open(output_path, "w") as f:
            json.dump(schedule, f, indent=2)

        print(f"Schedule created: {output_path}")
        print(f"  Judges: {', '.join(judges)}")
        print(f"  Probes: {', '.join(schedule['probes'])}")
        print(f"  Items: {items} × {repeats} repeats")
        print(f"  Total experiments: {len(schedule['experiments'])}")
        print(f"  Estimated time: {schedule['estimated_total_hours']:.1f} hours")
        return output_path

    def _estimate_seconds(self, items: int, repeats: int) -> int:
        """Estimated seconds per experiment."""
        return items * repeats * 2  # ~2 seconds per API call

    def _estimate_hours(self, judges: List[str], items: int, repeats: int) -> float:
        """Estimated total hours."""
        total_calls = len(judges) * 6 * items * repeats
        return total_calls * 2 / 3600  # ~2s per call

    def load_schedule(self, path: Optional[Path] = None) -> Dict:
        """Load a schedule from file."""
        path = path or self.schedule_path
        with open(path) as f:
            return json.load(f)

    def save_schedule(self, schedule: Dict, path: Optional[Path] = None):
        """Save schedule status."""
        path = path or self.schedule_path
        with open(path, "w") as f:
            json.dump(schedule, f, indent=2)

    def execute_experiment(self, judge: str, probe: str, items: int,
                           repeats: int, timeout: int = 3600) -> Dict:
        """Execute a single experiment."""
        start_time = time.time()
        print(f"\n[{datetime.datetime.now():%H:%M:%S}] Running {judge}/{probe} "
              f"({items} items × {repeats} repeats)")

        cmd = [
            sys.executable, str(BASE_DIR / "inference_executor.py"),
            "--judge", judge,
            "--benchmark", str(BASE_DIR / "benchmark" / "scoring_bias_benchmark.json"),
            "--probe", probe,
            "--items", str(items),
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            success = result.returncode == 0
            return {
                "judge": judge, "probe": probe, "items": items, "repeats": repeats,
                "success": success, "stdout": result.stdout[-500:],
                "stderr": result.stderr[-500:],
                "duration_seconds": time.time() - start_time,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        except subprocess.TimeoutExpired:
            return {
                "judge": judge, "probe": probe, "items": items, "repeats": repeats,
                "success": False, "error": "timeout",
                "duration_seconds": timeout,
                "timestamp": datetime.datetime.now().isoformat(),
            }

    def run_schedule(self, path: Optional[Path] = None,
                     max_experiments: int = None,
                     stagger: int = None):
        """Execute all pending experiments in a schedule."""
        schedule = self.load_schedule(path)
        std = stagger or schedule.get("stagger_delay_seconds", 60)
        self.running = True

        executed = 0
        for experiment in schedule["experiments"]:
            if not self.running:
                print("\nScheduler stopped.")
                break
            if experiment["status"] == "completed":
                continue
            if max_experiments and executed >= max_experiments:
                break

            result = self.execute_experiment(
                experiment["judge"], experiment["probe"],
                experiment["items"], experiment["repeats"]
            )
            experiment["result"] = result
            experiment["status"] = "completed" if result["success"] else "failed"
            executed += 1

            # Save progress
            self.save_schedule(schedule)

            # Stagger
            if self.running and std > 0:
                print(f"  Waiting {std}s before next experiment...")
                time.sleep(std)

        # Summary
        completed = sum(1 for e in schedule["experiments"] if e["status"] == "completed")
        failed = sum(1 for e in schedule["experiments"] if e["status"] == "failed")
        print(f"\n{'='*50}")
        print(f"SCHEDULE COMPLETE: {completed} completed, {failed} failed")
        print(f"{'='*50}")

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        print("Stopping scheduler...")

    def show_status(self, path: Optional[Path] = None):
        """Show schedule execution status."""
        schedule = self.load_schedule(path)
        completed = sum(1 for e in schedule["experiments"] if e["status"] == "completed")
        failed = sum(1 for e in schedule["experiments"] if e["status"] == "failed")
        pending = sum(1 for e in schedule["experiments"] if e["status"] == "pending")
        total = len(schedule["experiments"])

        print(f"\nSchedule: {schedule['created_at']}")
        print(f"  Total: {total} experiments")
        print(f"  Completed: {completed}")
        print(f"  Failed: {failed}")
        print(f"  Pending: {pending}")
        print(f"  Progress: {completed/total*100:.1f}%" if total > 0 else "")

        if failed > 0:
            print(f"\n  Failed experiments:")
            for e in schedule["experiments"]:
                if e["status"] == "failed":
                    print(f"    {e['judge']}/{e['probe']}: {e.get('result', {}).get('error', 'unknown')}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create", "run", "status", "stop"])
    parser.add_argument("--schedule", help="Schedule file path")
    parser.add_argument("--judges", nargs="+", default=None,
                        help="Judges to include")
    parser.add_argument("--probes", nargs="+", default=None)
    parser.add_argument("--items", type=int, default=400)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--delay", type=int, default=60,
                        help="Stagger delay between experiments (seconds)")
    parser.add_argument("--max", type=int, help="Max experiments to run")
    args = parser.parse_args()

    scheduler = ExperimentScheduler()

    if args.command == "create":
        judges = args.judges or ["claude", "gpt4o", "gemini", "deepseek", "llama"]
        scheduler.create_schedule(
            judges=judges, probes=args.probes, items=args.items,
            repeats=args.repeats, stagger_delay=args.delay
        )

    elif args.command == "run":
        schedule_path = Path(args.schedule) if args.schedule else None
        scheduler.run_schedule(
            path=schedule_path, max_experiments=args.max, stagger=args.delay
        )

    elif args.command == "status":
        path = Path(args.schedule) if args.schedule else None
        scheduler.show_status(path)

    elif args.command == "stop":
        scheduler.stop()

if __name__ == "__main__":
    main()
