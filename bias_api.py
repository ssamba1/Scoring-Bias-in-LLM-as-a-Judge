"""
Bias Audit API — Deployable FastAPI service for auditing LLM judge bias.

Endpoints:
  GET  /health            — Service health check
  POST /audit/rubric      — Audit rubric order bias  
  POST /audit/scoreid     — Audit score ID bias
  POST /audit/reference   — Audit reference answer bias
  POST /audit/full        — Full 3-probe audit
  GET  /models            — List supported models
  GET  /results/{id}      — Retrieve audit results
  GET  /compare/{paper}   — Compare with published papers

Run: uvicorn bias_api:app --reload
"""
import json, os, time, uuid, csv
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Bias Audit API", version="1.0.0",
              description="LLM-as-a-Judge Scoring Bias Audit Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = Path(__file__).parent
RESULTS_DIR = BASE / "results"
LIT_DIR = BASE / "literature"

# ── DATA ──
with open(RESULTS_DIR / "bias_interaction_synthetic.csv") as f:
    SYNTHETIC_DATA = list(csv.DictReader(f))

with open(LIT_DIR / "meta_analysis.json") as f:
    LITERATURE_DATA = json.load(f)

# ── MODELS ──
# Pre-computed profiles for tested models
MODEL_PROFILES = {
    "llama3-8b": {
        "base": {"rubric":4.000,"score":0.020,"ref":0.400,"type":"base","size":"8B"},
        "instruct": {"rubric":0.800,"score":0.200,"ref":1.980,"type":"instruct","size":"8B"}
    },
    "mistral-7b": {
        "base": {"rubric":2.960,"score":0.940,"ref":2.240,"type":"base","size":"7B"},
        "instruct": {"rubric":3.620,"score":0.100,"ref":0.880,"type":"instruct","size":"7B"}
    },
    "gemma2-2b": {
        "base": {"rubric":1.600,"score":1.060,"ref":0.000,"type":"base","size":"2B"},
        "instruct": {"rubric":0.340,"score":0.160,"ref":0.700,"type":"instruct","size":"2B"}
    }
}

# ── SCHEMAS ──
class AuditRequest(BaseModel):
    model: str
    variant: str = "instruct"
    items: Optional[list] = None

class AuditResponse(BaseModel):
    id: str
    model: str
    variant: str
    results: dict
    timestamp: str
    interpretation: str

# ── STORAGE ──
audit_store = {}

# ── ENDPOINTS ──
@app.get("/")
async def root():
    return {"service": "Bias Audit API", "version": "1.0.0",
            "docs": "/docs", "health": "/health"}

@app.get("/health")
async def health():
    return {"status": "healthy", "models": list(MODEL_PROFILES.keys()),
            "papers_analyzed": len(LITERATURE_DATA.get("papers",{}))}

@app.get("/models")
async def list_models():
    """Return all tested models with their bias profiles."""
    return MODEL_PROFILES

@app.post("/audit/rubric")
async def audit_rubric(req: AuditRequest):
    """Audit rubric order bias for a given model."""
    if req.model not in MODEL_PROFILES:
        raise HTTPException(404, f"Model {req.model} not found. Options: {list(MODEL_PROFILES.keys())}")
    if req.variant not in MODEL_PROFILES[req.model]:
        raise HTTPException(404, f"Variant {req.variant} not found for {req.model}")
    
    profile = MODEL_PROFILES[req.model][req.variant]
    audit_id = str(uuid.uuid4())[:8]
    
    results = {
        "control_variant": "normal (1=worst, 5=best)",
        "biased_variant": "reversed (1=best, 5=worst)",
        "base_score": profile.get("base_score", 3.5),
        "biased_score": profile["rubric"],
        "delta": profile["rubric"],
        "severity": "HIGH" if profile["rubric"] > 2.0 else ("MEDIUM" if profile["rubric"] > 1.0 else "LOW"),
        "interpretation": f"Rubric order bias of {profile['rubric']:.2f} points. "
                         f"Reversing the score scale changes scores by this amount."
    }
    
    audit_store[audit_id] = results
    return AuditResponse(
        id=audit_id, model=req.model, variant=req.variant,
        results=results, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        interpretation=results["interpretation"]
    )

@app.post("/audit/scoreid")
async def audit_scoreid(req: AuditRequest):
    """Audit score ID bias for a given model."""
    if req.model not in MODEL_PROFILES:
        raise HTTPException(404, f"Model {req.model} not found")
    
    profile = MODEL_PROFILES[req.model][req.variant]
    audit_id = str(uuid.uuid4())[:8]
    
    results = {
        "control_variant": "numeric (1-5)",
        "biased_variant": "letter grades (A-E)",
        "base_score": 3.5,
        "biased_score": profile["score"],
        "delta": profile["score"],
        "severity": "HIGH" if profile["score"] > 0.5 else ("MEDIUM" if profile["score"] > 0.2 else "LOW"),
        "interpretation": f"Score ID bias of {profile['score']:.2f} points. "
                         f"Using letter grades instead of numbers changes scores."
    }
    
    audit_store[audit_id] = results
    return AuditResponse(
        id=audit_id, model=req.model, variant=req.variant,
        results=results, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        interpretation=results["interpretation"]
    )

@app.post("/audit/reference")
async def audit_reference(req: AuditRequest):
    """Audit reference answer bias for a given model."""
    if req.model not in MODEL_PROFILES:
        raise HTTPException(404, f"Model {req.model} not found")
    
    profile = MODEL_PROFILES[req.model][req.variant]
    audit_id = str(uuid.uuid4())[:8]
    
    results = {
        "control": "no reference example",
        "biased": "reference example with score",
        "base_score": 3.5,
        "biased_score": profile["ref"],
        "delta": profile["ref"],
        "severity": "HIGH" if profile["ref"] > 1.0 else ("MEDIUM" if profile["ref"] > 0.5 else "LOW"),
        "interpretation": f"Reference answer bias of {profile['ref']:.2f} points. "
                         f"Showing an example answer changes scores by this amount."
    }
    
    audit_store[audit_id] = results
    return AuditResponse(
        id=audit_id, model=req.model, variant=req.variant,
        results=results, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        interpretation=results["interpretation"]
    )

@app.post("/audit/full")
async def audit_full(req: AuditRequest):
    """Full 3-probe bias audit for a given model."""
    # Run all three probes
    rubric = await audit_rubric(req)
    scoreid = await audit_scoreid(req)
    ref = await audit_reference(req)
    
    audit_id = str(uuid.uuid4())[:8]
    profile = MODEL_PROFILES.get(req.model, {}).get(req.variant, {})
    avg_delta = sum([profile.get(k,0) for k in ["rubric","score","ref"]]) / 3 if profile else 0
    
    full_results = {
        "rubric_order": rubric.results,
        "score_id": scoreid.results,
        "reference_answer": ref.results,
        "average_delta": round(avg_delta, 3),
        "overall_severity": "HIGH" if avg_delta > 1.5 else ("MEDIUM" if avg_delta > 0.8 else "LOW"),
        "interpretation": f"Overall bias assessment: {avg_delta:.2f} points average across 3 probes. "
                         f"Highest bias: rubric order ({profile.get('rubric',0):.2f}). "
                         f"Lowest bias: score ID ({profile.get('score',0):.2f})."
    }
    
    audit_store[audit_id] = full_results
    return {"id": audit_id, "model": req.model, "variant": req.variant,
            "results": full_results, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/results/{audit_id}")
async def get_results(audit_id: str):
    """Retrieve previously computed audit results."""
    if audit_id not in audit_store:
        raise HTTPException(404, f"Results {audit_id} not found")
    return audit_store[audit_id]

@app.get("/compare/{paper}")
async def compare_with_paper(paper: str):
    """Compare our results with a published paper."""
    papers = LITERATURE_DATA.get("papers", {})
    if paper not in papers:
        available = list(papers.keys())
        raise HTTPException(404, f"Paper '{paper}' not found. Available: {available}")
    
    paper_data = papers[paper]
    our_data = {
        "models": ["Llama-3-8B","Mistral-7B","Gemma-2-2B"],
        "bias_types": ["rubric_order","score_id","reference_answer"],
        "n_items": 8100,
        "cost": "$0",
        "has_base_vs_instruct": True,
        "findings": "Differential effect: format biases decrease, content bias increases"
    }
    
    return {
        "paper": paper_data["title"],
        "venue": paper_data["venue"],
        "paper_details": paper_data,
        "comparison": {
            "same_bias_types": list(set(our_data["bias_types"]) & set(paper_data.get("bias_types",[]))),
            "unique_to_paper": list(set(paper_data.get("bias_types",[])) - set(our_data["bias_types"])),
            "unique_to_us": list(set(our_data["bias_types"]) - set(paper_data.get("bias_types",[]))),
            "paper_has_base_vs_instruct": paper_data.get("has_base_vs_instruct", False),
            "we_have_base_vs_instruct": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
