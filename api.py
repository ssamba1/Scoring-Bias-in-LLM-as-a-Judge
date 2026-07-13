"""
FastAPI Web Service — Experiment Management API.
Provides RESTful endpoints for:
- Querying experiment results
- Triggering experiment runs
- Exporting results and figures
- Health monitoring

Run with: uvicorn api:app --host 0.0.0.0 --port 8000
"""
import csv, json, os, io, datetime, random
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    # Fallback: create a stub that explains how to install
    import sys
    print("FastAPI not installed. Run: pip install fastapi uvicorn")
    print("Then: uvicorn api:app --host 0.0.0.0 --port 8000")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

app = FastAPI(
    title="Bias Research API",
    description="API for LLM-as-a-Judge Bias Experiment Management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class ExperimentConfig(BaseModel):
    name: str
    judges: List[str] = ["claude", "gpt4o"]
    items: int = 50
    repeats: int = 3
    temperature: float = 0.0

class JudgeStats(BaseModel):
    name: str
    total_scores: int
    mean_score: float
    std_score: float
    min_score: float
    max_score: float
    n_conditions: int

# --- Helper Functions ---

def load_results_csv() -> List[Dict]:
    """Load the most recent results CSV."""
    path = RESULTS_DIR / "bias_interaction_synthetic_v2.csv"
    if not path.exists():
        path = RESULTS_DIR / "bias_interaction_synthetic.csv"
    if not path.exists():
        return []
    with open(path) as f:
        return list(csv.DictReader(f))

def compute_judge_stats(judge_name: str) -> Optional[JudgeStats]:
    """Compute statistics for a specific judge."""
    data = load_results_csv()
    if not data:
        return None
    jd = [r for r in data if r.get("judge") == judge_name]
    if not jd:
        return None
    scores = [float(r["score"]) for r in jd]
    n = len(scores)
    mean = sum(scores) / n
    std = (sum((s - mean) ** 2 for s in scores) / (n - 1)) ** 0.5 if n > 1 else 0
    conditions = len(set(r.get("condition", "") for r in jd))
    return JudgeStats(
        name=judge_name,
        total_scores=n,
        mean_score=round(mean, 3),
        std_score=round(std, 3),
        min_score=round(min(scores), 1),
        max_score=round(max(scores), 1),
        n_conditions=conditions,
    )

# --- Endpoints ---

@app.get("/")
async def root():
    return {
        "service": "Bias Research API",
        "version": "1.0.0",
        "endpoints": {
            "/": "This documentation",
            "/health": "Health check",
            "/judges": "List all available judges",
            "/judge/{name}": "Get statistics for a judge",
            "/experiment/run": "Run a new experiment (POST)",
            "/results/top-contested": "Get most contested items",
            "/results/export/{format}": "Export results (csv/json)",
            "/dashboard": "Interactive dashboard HTML",
        }
    }

@app.get("/health")
async def health():
    data = load_results_csv()
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "results_loaded": len(data) > 0,
        "n_data_points": len(data) if data else 0,
        "results_dir": str(RESULTS_DIR),
        "docker": os.path.exists("/.dockerenv"),
    }

@app.get("/judges")
async def list_judges():
    """List all judges with summary statistics."""
    data = load_results_csv()
    if not data:
        # Return default judge list
        return {
            "judges": [
                {"name": "claude", "status": "no_data", "description": "Anthropic Claude Sonnet 4"},
                {"name": "gpt4o", "status": "no_data", "description": "OpenAI GPT-4o"},
                {"name": "gemini", "status": "no_data", "description": "Google Gemini 2.0 Flash"},
                {"name": "deepseek", "status": "no_data", "description": "DeepSeek V3"},
                {"name": "llama", "status": "no_data", "description": "Meta Llama 3 70B"},
            ]
        }

    judges_in_data = set(r.get("judge", "") for r in data)
    result = []
    for name in sorted(judges_in_data):
        stats = compute_judge_stats(name)
        if stats:
            result.append({
                "name": name,
                "total_scores": stats.total_scores,
                "mean_score": stats.mean_score,
                "std_score": stats.std_score,
                "min_score": stats.min_score,
                "max_score": stats.max_score,
                "n_conditions": stats.n_conditions,
            })
    return {"judges": result}

@app.get("/judge/{name}")
async def judge_details(name: str):
    """Get detailed statistics for a specific judge."""
    stats = compute_judge_stats(name)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Judge '{name}' not found in results")

    data = load_results_csv()
    jd = [r for r in data if r.get("judge") == name]

    # Condition breakdown
    conditions = {}
    for r in jd:
        c = r.get("condition", "unknown")
        if c not in conditions:
            conditions[c] = []
        conditions[c].append(float(r["score"]))

    condition_stats = {}
    for cond, scores in conditions.items():
        n = len(scores)
        m = sum(scores) / n
        condition_stats[cond] = {
            "n": n,
            "mean": round(m, 3),
            "std": round((sum((s - m) ** 2 for s in scores) / (n - 1)) ** 0.5 if n > 1 else 0, 3),
        }

    # Interaction analysis (if applicable)
    interaction = {}
    baseline = [r for r in jd if r.get("condition") == "baseline"]
    worst = [r for r in jd if r.get("condition") == "worst_case" or r.get("condition") == "worst"]
    if baseline and worst:
        b_mean = sum(float(r["score"]) for r in baseline) / len(baseline)
        w_mean = sum(float(r["score"]) for r in worst) / len(worst)
        interaction["degradation"] = round(b_mean - w_mean, 3)

        # Compute interaction ratio
        first = [r for r in jd if r.get("position") == "first" and r.get("length") == "normal"]
        second = [r for r in jd if r.get("position") == "second" and r.get("length") == "normal"]
        long_r = [r for r in jd if r.get("length") == "long" and r.get("position") == "first"]
        normal = [r for r in jd if r.get("length") == "normal" and r.get("position") == "first"]

        if first and second and long_r and normal:
            pos_bias = abs(sum(float(r["score"]) for r in first)/len(first) -
                          sum(float(r["score"]) for r in second)/len(second))
            verb_bias = abs(sum(float(r["score"]) for r in long_r)/len(long_r) -
                           sum(float(r["score"]) for r in normal)/len(normal))
            combined = b_mean - w_mean
            sum_ind = pos_bias + verb_bias
            if sum_ind > 0:
                interaction["interaction_ratio"] = round(combined / sum_ind, 3)
                if interaction["interaction_ratio"] > 1.05:
                    interaction["pattern"] = "compounding"
                elif interaction["interaction_ratio"] < 0.95:
                    interaction["pattern"] = "cancelling"
                else:
                    interaction["pattern"] = "additive"

    return {
        "name": name,
        "statistics": stats.model_dump() if hasattr(stats, 'model_dump') else stats.dict(),
        "condition_breakdown": condition_stats,
        "interaction_analysis": interaction,
        "n_items": len(jd) // max(len(condition_stats), 1) if condition_stats else 0,
    }

@app.post("/experiment/run")
async def run_experiment(config: ExperimentConfig):
    """Register and trigger a new experiment run."""
    from experiment_tracker import ExperimentTracker
    from experiment_scheduler import ExperimentScheduler

    tracker = ExperimentTracker()
    config_dict = config.model_dump() if hasattr(config, 'model_dump') else config.dict()

    # Register
    eid = tracker.register_experiment(
        name=config_dict.get("name", "API Triggered Experiment"),
        config=config_dict,
        description="Triggered via API"
    )

    return {
        "experiment_id": eid,
        "config": config_dict,
        "status": "registered",
        "message": f"Experiment {eid} registered. Run: experiment_tracker.py start --experiment {eid}",
        "estimated_cost": f"~${len(config_dict.get('judges', [])) * 5:.2f}",
    }

@app.get("/results/top-contested")
async def top_contested(limit: int = Query(10, ge=1, le=100)):
    """Get the most contested items (highest inter-judge variance)."""
    data = load_results_csv()
    if not data:
        return {"items": []}

    # Group by item_id
    from collections import defaultdict
    items = defaultdict(list)
    for r in data:
        iid = r.get("item_id", r.get("probe_id", "0"))
        items[iid].append(r)

    # Compute variance per item
    item_variance = []
    for iid, judges in items.items():
        scores = [float(j["score"]) for j in judges]
        if len(scores) > 1:
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            item_variance.append({
                "item_id": str(iid),
                "n_judges": len(judges),
                "mean_score": round(mean, 2),
                "variance": round(variance, 3),
                "min_score": round(min(scores), 1),
                "max_score": round(max(scores), 1),
            })

    item_variance.sort(key=lambda x: x["variance"], reverse=True)
    return {"contested_items": item_variance[:limit]}

@app.get("/results/export/{fmt}")
async def export_results(fmt: str = "csv"):
    """Export results in CSV or JSON format."""
    data = load_results_csv()
    if not data:
        raise HTTPException(status_code=404, detail="No results found")

    if fmt == "csv":
        # Return as CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=experiment_results.csv"}
        )
    elif fmt == "json":
        return JSONResponse(content={"data": data, "count": len(data)})
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")

@app.get("/dashboard")
async def dashboard():
    """Interactive dashboard HTML."""
    html_path = BASE_DIR / "dashboard" / "interactive_viz.html"
    if html_path.exists():
        with open(html_path) as f:
            content = f.read()
        return HTMLResponse(content=content)
    # Fallback to explorer
    html_path = BASE_DIR / "dashboard" / "explorer.html"
    if html_path.exists():
        with open(html_path) as f:
            content = f.read()
        return HTMLResponse(content=content)
    return HTMLResponse("<h1>Dashboard not found</h1><p>Run: cd dashboard && ls</p>")

@app.get("/experiments")
async def list_experiments():
    """List all registered experiments."""
    from experiment_tracker import ExperimentTracker
    tracker = ExperimentTracker()
    experiments = tracker.list_experiments()
    return {"experiments": experiments}

@app.get("/system-info")
async def system_info():
    """Get system information for reproducibility."""
    import platform, sys
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "timestamp": datetime.datetime.now().isoformat(),
        "docker": os.path.exists("/.dockerenv"),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
