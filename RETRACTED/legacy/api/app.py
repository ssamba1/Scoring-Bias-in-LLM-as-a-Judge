"""
scoring-bias API  FastAPI service for scoring bias analysis.

Provides RESTful endpoints for:
- GET  /health            Health check
- GET  /models            List all models with bias delta values
- POST /predict           Predict bias for a model

Run with:
    uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    import sys
    print("FastAPI not installed. Run: pip install fastapi uvicorn", file=sys.stderr)
    sys.exit(1)

# Add project root to path
API_DIR = Path(__file__).resolve().parent
ROOT = API_DIR.parent
sys.path.insert(0, str(ROOT))

app = FastAPI(
    title="Scoring Bias API",
    description="API for LLM-as-a-Judge Scoring Bias Analysis",
    version="1.0.0",
    contact={
        "name": "Sricharan Samba",
        "url": "https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Data ──

# Try to load pre-computed analysis results
DATA_DIR = ROOT / "data" / "raw"
RESULTS_FILE = ROOT / "output" / "deltas.json"

loaded_data: List[Dict[str, Any]] = []
if RESULTS_FILE.exists():
    with open(RESULTS_FILE) as f:
        loaded_data = json.load(f)
elif DATA_DIR.exists():
    # Try to compute on the fly from CSV
    csv_files = list(DATA_DIR.glob("*.csv"))
    if csv_files:
        import csv
        csv_path = csv_files[0]
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Compute quick deltas
        from collections import defaultdict
        groups: Dict[tuple, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        for row in rows:
            key = (row.get("model_name", "?"), row.get("probe", "?"))
            groups[key][row.get("condition", "normal")].append(float(row.get("score", 0)))

        for (model_name, probe), conditions in groups.items():
            control = conditions.get("normal", [])
            treatment_keys = [k for k in conditions if k != "normal"]
            for trt_key in treatment_keys:
                treatment = conditions[trt_key]
                if control and treatment:
                    delta = sum(treatment) / len(treatment) - sum(control) / len(control)
                    loaded_data.append({
                        "model_name": model_name,
                        "probe": probe,
                        "delta": round(delta, 4),
                        "n_control": len(control),
                        "n_treatment": len(treatment),
                    })


# ── Models ──

class PredictRequest(BaseModel):
    model_name: str
    probe: Optional[str] = None
    scores_control: Optional[List[float]] = None
    scores_treatment: Optional[List[float]] = None


class PredictResponse(BaseModel):
    model_name: str
    delta: Optional[float] = None
    interpretation: Optional[str] = None
    error: Optional[str] = None


# ── Endpoints ──


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "scoring-bias-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "data_loaded": len(loaded_data) > 0,
        "n_entries": len(loaded_data),
    }


@app.get("/models")
async def list_models(
    sort_by: str = Query("delta", description="Sort by field: delta, model_name"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(50, description="Max models to return"),
):
    """List all models with their delta values."""
    if not loaded_data:
        raise HTTPException(status_code=503, detail="No analysis data loaded")

    # Aggregate by model
    model_deltas: Dict[str, Dict[str, Any]] = {}
    for entry in loaded_data:
        name = entry["model_name"]
        if name not in model_deltas:
            model_deltas[name] = {
                "model_name": name,
                "probes": {},
                "avg_delta": 0.0,
            }
        model_deltas[name]["probes"][entry["probe"]] = {
            "delta": entry.get("delta"),
            "n_control": entry.get("n_control"),
            "n_treatment": entry.get("n_treatment"),
        }

    # Compute averages
    for name, info in model_deltas.items():
        deltas = [p["delta"] for p in info["probes"].values() if p["delta"] is not None]
        info["avg_delta"] = round(sum(deltas) / len(deltas), 4) if deltas else None
        info["n_probes"] = len(info["probes"])

    models_list = list(model_deltas.values())

    # Sort
    reverse = order.lower() != "asc"
    if sort_by == "delta":
        models_list.sort(key=lambda m: m.get("avg_delta") or 0, reverse=reverse)
    else:
        models_list.sort(key=lambda m: m.get("model_name", ""), reverse=reverse)

    return {
        "count": len(models_list),
        "models": models_list[:limit],
    }


@app.post("/predict")
async def predict_bias(request: PredictRequest):
    """Predict bias delta for a model.

    If scores are provided, compute delta directly.
    Otherwise, look up pre-computed values.
    """
    # Direct computation from scores
    if request.scores_control and request.scores_treatment:
        from scoring_bias.analysis import compute_delta, bootstrap_ci
        delta = compute_delta(request.scores_control, request.scores_treatment)
        _, ci_l, ci_u = bootstrap_ci(request.scores_control, request.scores_treatment)

        if delta is None:
            return PredictResponse(
                model_name=request.model_name,
                error="Could not compute delta (check input lengths)",
            )

        from scoring_bias.metrics import effect_size_interpretation
        return PredictResponse(
            model_name=request.model_name,
            delta=round(delta, 4),
            interpretation=effect_size_interpretation(delta),
        )

    # Look up pre-computed
    if not loaded_data:
        raise HTTPException(status_code=503, detail="No analysis data loaded")

    # Filter by model
    entries = [e for e in loaded_data if e["model_name"] == request.model_name]
    if request.probe:
        entries = [e for e in entries if e["probe"] == request.probe]

    if not entries:
        raise HTTPException(
            status_code=404,
            detail=f"No data for model '{request.model_name}'" +
                   (f" with probe '{request.probe}'" if request.probe else ""),
        )

    # Return aggregate
    deltas = [e["delta"] for e in entries if e.get("delta") is not None]
    avg_delta = round(sum(deltas) / len(deltas), 4) if deltas else None

    from scoring_bias.metrics import effect_size_interpretation
    return PredictResponse(
        model_name=request.model_name,
        delta=avg_delta,
        interpretation=effect_size_interpretation(avg_delta) if avg_delta else None,
    )


@app.get("/models/{model_name}")
async def get_model_detail(model_name: str):
    """Get detailed bias data for a specific model."""
    if not loaded_data:
        raise HTTPException(status_code=503, detail="No analysis data loaded")

    entries = [e for e in loaded_data if e["model_name"] == model_name]
    if not entries:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    return {
        "model_name": model_name,
        "n_entries": len(entries),
        "probes": entries,
    }

# API entry point
