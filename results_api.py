#!/usr/bin/env python3
"""
Experiment Results Management API — store, query, compare, and export results.
Provides a programmatic interface for all experiment outputs.
"""
import csv, json, os, sqlite3, datetime, hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"

class ResultsAPI:
    """Unified API for managing experiment results."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or RESULTS_DIR / "experiment_db.sqlite"
        self._init_db()

    def _init_db(self):
        """Initialize the results database."""
        os.makedirs(self.db_path.parent, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                config_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS judges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                name TEXT NOT NULL,
                model TEXT,
                provider TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            );
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judge_id INTEGER,
                item_id INTEGER,
                condition TEXT,
                score REAL,
                repeat_num INTEGER DEFAULT 1,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (judge_id) REFERENCES judges(id)
            );
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                analysis_type TEXT,
                results_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            );
            CREATE INDEX IF NOT EXISTS idx_scores_judge ON scores(judge_id);
            CREATE INDEX IF NOT EXISTS idx_scores_item ON scores(item_id);
            CREATE INDEX IF NOT EXISTS idx_scores_condition ON scores(condition);
        """)
        conn.commit()
        conn.close()

    def create_experiment(self, name: str, description: str = "",
                          config: Optional[Dict] = None) -> int:
        """Create a new experiment entry."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "INSERT INTO experiments (name, description, config_json) VALUES (?, ?, ?)",
            (name, description, json.dumps(config or {}))
        )
        experiment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return experiment_id

    def import_csv(self, csv_path: Path, experiment_id: int,
                   judge_name: str = None, model: str = None,
                   provider: str = None) -> int:
        """Import results from a CSV file into the database."""
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        conn = sqlite3.connect(str(self.db_path))
        imported = 0

        with open(csv_path) as f:
            rows = list(csv.DictReader(f))

        # Infer judge name from file if not provided
        if judge_name is None:
            judge_name = csv_path.stem.replace("results_", "")

        # Create judge entry
        cursor = conn.execute(
            "INSERT INTO judges (experiment_id, name, model, provider) VALUES (?, ?, ?, ?)",
            (experiment_id, judge_name, model or judge_name, provider or "api")
        )
        judge_id = cursor.lastrowid

        # Import scores
        for row in rows:
            score = row.get("score") or row.get("score_mean") or row.get("score_median")
            if score is None:
                continue
            try:
                score = float(score)
            except ValueError:
                continue

            conn.execute(
                "INSERT INTO scores (judge_id, item_id, condition, score, repeat_num) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    judge_id,
                    int(row.get("item_id", 0)),
                    row.get("condition", "baseline"),
                    score,
                    int(row.get("repeat_num", 1)),
                )
            )
            imported += 1

        conn.commit()
        conn.close()
        return imported

    def get_experiment(self, experiment_id: int) -> Optional[Dict]:
        """Get experiment details."""
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute(
            "SELECT * FROM experiments WHERE id = ?", (experiment_id,)
        ).fetchone()
        conn.close()

        if row:
            return {
                "id": row[0], "name": row[1], "description": row[2],
                "config": json.loads(row[3]) if row[3] else {},
                "created_at": row[4],
            }
        return None

    def list_experiments(self) -> List[Dict]:
        """List all experiments with summary stats."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute("""
            SELECT e.id, e.name, e.description, e.created_at,
                   COUNT(DISTINCT j.id) as n_judges,
                   COUNT(s.id) as n_scores
            FROM experiments e
            LEFT JOIN judges j ON j.experiment_id = e.id
            LEFT JOIN scores s ON s.judge_id = j.id
            GROUP BY e.id
            ORDER BY e.created_at DESC
        """).fetchall()
        conn.close()

        return [
            {"id": r[0], "name": r[1], "description": r[2],
             "created_at": r[3], "n_judges": r[4], "n_scores": r[5]}
            for r in rows
        ]

    def get_judge_summary(self, experiment_id: int) -> List[Dict]:
        """Get summary statistics for each judge in an experiment."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute("""
            SELECT j.name,
                   COUNT(s.id) as n_scores,
                   ROUND(AVG(s.score), 3) as mean_score,
                   ROUND(MIN(s.score), 1) as min_score,
                   ROUND(MAX(s.score), 1) as max_score,
                   COUNT(DISTINCT s.condition) as n_conditions,
                   COUNT(DISTINCT s.item_id) as n_items
            FROM judges j
            JOIN scores s ON s.judge_id = j.id
            WHERE j.experiment_id = ?
            GROUP BY j.id
            ORDER BY j.name
        """, (experiment_id,)).fetchall()
        conn.close()

        return [
            {"name": r[0], "n_scores": r[1], "mean_score": r[2],
             "min_score": r[3], "max_score": r[4],
             "n_conditions": r[5], "n_items": r[6]}
            for r in rows
        ]

    def get_bias_analysis(self, experiment_id: int, judge_name: str) -> Dict:
        """Compute bias metrics for a specific judge."""
        conn = sqlite3.connect(str(self.db_path))
        # Get scores by condition
        rows = conn.execute("""
            SELECT s.condition, s.score, s.item_id
            FROM scores s
            JOIN judges j ON s.judge_id = j.id
            WHERE j.experiment_id = ? AND j.name = ?
        """, (experiment_id, judge_name)).fetchall()
        conn.close()

        if not rows:
            return {"error": "No data found"}

        # Organize by condition
        conditions = {}
        for cond, score, item_id in rows:
            if cond not in conditions:
                conditions[cond] = []
            conditions[cond].append((score, item_id))

        # Compute metrics
        bias = {}
        for cond, scores in conditions.items():
            scores_only = [s for s, _ in scores]
            bias[cond] = {
                "n": len(scores_only),
                "mean": sum(scores_only) / len(scores_only),
                "min": min(scores_only),
                "max": max(scores_only),
            }

        # Interaction ratios
        if "baseline" in bias and "worst_case" in bias:
            combined = bias["baseline"]["mean"] - bias["worst_case"]["mean"]
            bias["combined_effect"] = round(combined, 3)

        return bias

    def export_to_json(self, experiment_id: int, output_path: Path = None) -> Dict:
        """Export complete experiment data to JSON."""
        experiment = self.get_experiment(experiment_id)
        judges = self.get_judge_summary(experiment_id)

        data = {
            "experiment": experiment,
            "judges": judges,
            "exported_at": datetime.datetime.now().isoformat(),
        }

        if output_path:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Exported to {output_path}")

        return data

    def compare_experiments(self, experiment_ids: List[int]) -> Dict:
        """Compare multiple experiments."""
        comparison = {}
        for eid in experiment_ids:
            exp = self.get_experiment(eid)
            judges = self.get_judge_summary(eid)
            comparison[str(eid)] = {
                "name": exp["name"] if exp else f"Experiment {eid}",
                "judges": judges,
            }
        return comparison

    def store_analysis(self, experiment_id: int, analysis_type: str,
                       results: Dict) -> int:
        """Store analysis results."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "INSERT INTO analyses (experiment_id, analysis_type, results_json) "
            "VALUES (?, ?, ?)",
            (experiment_id, analysis_type, json.dumps(results))
        )
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id

    def get_analyses(self, experiment_id: int) -> List[Dict]:
        """Get all analyses for an experiment."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT id, analysis_type, results_json, created_at "
            "FROM analyses WHERE experiment_id = ? ORDER BY created_at DESC",
            (experiment_id,)
        ).fetchall()
        conn.close()
        return [
            {"id": r[0], "type": r[1], "results": json.loads(r[2]),
             "created_at": r[3]}
            for r in rows
        ]

    def stats(self) -> Dict:
        """Get database statistics."""
        conn = sqlite3.connect(str(self.db_path))
        exp_count = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        judge_count = conn.execute("SELECT COUNT(*) FROM judges").fetchone()[0]
        score_count = conn.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
        analysis_count = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        conn.close()

        return {
            "experiments": exp_count,
            "judges": judge_count,
            "scores": score_count,
            "analyses": analysis_count,
            "db_size_mb": os.path.getsize(self.db_path) / 1024 / 1024,
        }

    def import_all_csv(self, experiment_id: int) -> int:
        """Import all results CSV files into the database."""
        total = 0
        for csv_path in RESULTS_DIR.glob("results_*.csv"):
            imported = self.import_csv(csv_path, experiment_id)
            total += imported
            print(f"  {csv_path.name}: {imported} rows")
        return total

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["list", "create", "import", "summary",
                                            "stats", "export"])
    parser.add_argument("--experiment", type=int, help="Experiment ID")
    parser.add_argument("--name", help="Experiment name")
    parser.add_argument("--output", help="Output path")
    args = parser.parse_args()

    api = ResultsAPI()

    if args.command == "list":
        for exp in api.list_experiments():
            print(f"  [{exp['id']}] {exp['name']} — {exp['n_judges']} judges, "
                  f"{exp['n_scores']} scores ({exp['created_at']})")

    elif args.command == "create":
        eid = api.create_experiment(args.name or f"Experiment {datetime.datetime.now():%Y%m%d_%H%M}")
        print(f"Created experiment [{eid}]: {args.name}")

    elif args.command == "import":
        if not args.experiment:
            print("Need --experiment ID. Create one with: python3 results_api.py create")
            return
        total = api.import_all_csv(args.experiment)
        print(f"Imported {total} total scores")

    elif args.command == "summary":
        if not args.experiment:
            experiments = api.list_experiments()
            if experiments:
                args.experiment = experiments[0]["id"]
            else:
                print("No experiments found")
                return
        judges = api.get_judge_summary(args.experiment)
        print(f"Experiment [{args.experiment}] summary:")
        for j in judges:
            print(f"  {j['name']:<15} n={j['n_scores']:>6} mean={j['mean_score']:.3f} "
                  f"items={j['n_items']} conditions={j['n_conditions']}")

    elif args.command == "stats":
        s = api.stats()
        print(f"Database: {api.db_path}")
        print(f"  Experiments: {s['experiments']}")
        print(f"  Judges: {s['judges']}")
        print(f"  Scores: {s['scores']}")
        print(f"  Analyses: {s['analyses']}")
        print(f"  Size: {s['db_size_mb']:.1f} MB")

    elif args.command == "export":
        if not args.experiment:
            print("Need --experiment ID")
            return
        api.export_to_json(args.experiment, Path(args.output) if args.output else None)
        print("Export complete")

if __name__ == "__main__":
    main()
