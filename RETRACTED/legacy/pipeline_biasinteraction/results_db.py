#!/usr/bin/env python3
"""Results database using SQLite for storing and querying experiment results."""
import sqlite3, csv, json, os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "results" / "experiment.db"
RESULTS_DIR = BASE_DIR / "results"

SCHEMA = """
CREATE TABLE IF NOT EXISTS judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judge TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    condition TEXT NOT NULL,
    position TEXT,
    length TEXT,
    sentiment TEXT,
    score REAL,
    repeat_num INTEGER DEFAULT 1,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(judge, item_id, condition, repeat_num)
);

CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    config_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bias_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER,
    judge TEXT NOT NULL,
    bias_type TEXT NOT NULL,
    effect_size REAL,
    ci_lower REAL,
    ci_upper REAL,
    p_value REAL,
    significant INTEGER,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);

CREATE INDEX IF NOT EXISTS idx_judgments_judge ON judgments(judge);
CREATE INDEX IF NOT EXISTS idx_judgments_item ON judgments(item_id);
CREATE INDEX IF NOT EXISTS idx_judgments_condition ON judgments(condition);
"""

def init_db(db_path=None):
    db_path = db_path or DB_PATH
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

def import_csv_to_db(csv_path, db_path=None):
    """Import results CSV into SQLite database."""
    conn = init_db(db_path)
    db_path = db_path or DB_PATH

    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    inserted = 0
    for row in rows:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO judgments
                (judge, item_id, condition, position, length, sentiment, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("judge", ""),
                int(row.get("item_id", 0)),
                row.get("condition", ""),
                row.get("position", ""),
                row.get("length", ""),
                row.get("sentiment", ""),
                float(row.get("score", 0)),
            ))
            inserted += 1
        except (ValueError, KeyError) as e:
            print(f"Error on row: {e}")

    conn.commit()
    print(f"Imported {inserted} judgments into {db_path}")
    return conn

def query_judge_bias(judge_name, conn=None):
    """Query bias statistics for a specific judge."""
    close = False
    if conn is None:
        conn = init_db()
        close = True

    results = conn.execute("""
        SELECT condition, AVG(score) as mean, COUNT(*) as n,
               MIN(score) as min, MAX(score) as max,
               STDEV(score) as std
        FROM judgments
        WHERE judge = ?
        GROUP BY condition
        ORDER BY condition
    """, (judge_name,)).fetchall()

    if close:
        conn.close()

    return results

def get_experiment_summary(conn=None):
    """Get summary statistics for all judges."""
    close = False
    if conn is None:
        conn = init_db()
        close = True

    summary = conn.execute("""
        SELECT judge,
               COUNT(*) as total_judgments,
               ROUND(AVG(score), 3) as mean_score,
               ROUND(MIN(score), 1) as min_score,
               ROUND(MAX(score), 1) as max_score,
               COUNT(DISTINCT item_id) as unique_items,
               COUNT(DISTINCT condition) as conditions
        FROM judgments
        GROUP BY judge
        ORDER BY judge
    """).fetchall()

    if close:
        conn.close()

    return summary

def main():
    print("="*60)
    print("EXPERIMENT RESULTS DATABASE")
    print("="*60)

    # Initialize
    conn = init_db()
    print(f"Database: {DB_PATH}")

    # Import synthetic results if CSV exists
    csv_path = RESULTS_DIR / "bias_interaction_synthetic.csv"
    if csv_path.exists():
        import_csv_to_db(str(csv_path))

    # Show summary
    print("\nExperiment Summary:")
    print(f"{'Judge':<15} {'Items':<8} {'Mean':<8} {'Range':<12} {'Conditions':<10}")
    print("-"*53)
    for row in get_experiment_summary(conn):
        judge, total, mean, mn, mx, items, conds = row
        print(f"{judge:<15} {items:<8} {mean:<8} {mn}-{mx:<8} {conds:<10}")

    conn.close()
    print(f"\nDatabase ready. Path: {DB_PATH}")

if __name__ == "__main__":
    main()
