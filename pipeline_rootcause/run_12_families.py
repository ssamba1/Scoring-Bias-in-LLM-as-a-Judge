#!/usr/bin/env python3
"""
12-FAMILY BASE+INSTRUCT REPLICATION — run on OpenRouter
Extends from N=3 to N=12+ families with base+instruct pairs.

Cost: ~$15 total. Each family = 2 variants × 3 probes × 3 variants × 50 items = 900 calls
At ~$0.0002/call (small models), that's ~$0.18/family → 12 families ≈ $2.16
Add a few larger models (70B) at ~$0.002/call → ~$1.80 each → 3 × $1.80 = $5.40
Total: ~$7-10 for all 12 families + 3 large models.

Usage:
  export OPENROUTER_KEY=sk-or-v1-...
  python3 pipeline_rootcause/run_12_families.py
"""
import os, json, time, sys
from openai import OpenAI
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
# Import scoring functions
exec(open(Path(__file__).parent.parent / "paper" / "auto_update_paper.py").read().split("import")[0])

client = OpenAI(api_key=os.environ.get("OPENROUTER_KEY", ""), base_url="https://openrouter.ai/api/v1")

# Models with BOTH base and instruct variants available
FAMILIES = [
    # Small (free/cheap)
    ("meta-llama/Llama-3.2-1B", "Llama-3.2-1B"),
    ("meta-llama/Llama-3.2-1B-Instruct", "Llama-3.2-1B-IT"),
    ("meta-llama/Llama-3.2-3B", "Llama-3.2-3B"),
    ("meta-llama/Llama-3.2-3B-Instruct", "Llama-3.2-3B-IT"),
    ("Qwen/Qwen2.5-0.5B", "Qwen2.5-0.5B"),
    ("Qwen/Qwen2.5-0.5B-Instruct", "Qwen2.5-0.5B-IT"),
    ("Qwen/Qwen2.5-1.5B", "Qwen2.5-1.5B"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen2.5-1.5B-IT"),
    ("google/gemma-2-2b", "Gemma-2-2B"),
    ("google/gemma-2-2b-it", "Gemma-2-2B-IT"),
    ("google/gemma-2-9b", "Gemma-2-9B"),
    ("google/gemma-2-9b-it", "Gemma-2-9B-IT"),
    # Medium
    ("mistralai/Mistral-7B-v0.3", "Mistral-7B"),
    ("mistralai/Mistral-7B-Instruct-v0.3", "Mistral-7B-IT"),
    ("meta-llama/Llama-3.1-8B", "Llama-3.1-8B"),
    ("meta-llama/Llama-3.1-8B-Instruct", "Llama-3.1-8B-IT"),
    # Large
    ("Qwen/Qwen2.5-72B", "Qwen2.5-72B"),
    ("Qwen/Qwen2.5-72B-Instruct", "Qwen2.5-72B-IT"),
    ("mistralai/Mixtral-8x7B-v0.1", "Mixtral-8x7B"),
    ("mistralai/Mixtral-8x7B-Instruct-v0.1", "Mixtral-8x7B-IT"),
]

CK = Path(__file__).parent.parent / "results_rootcause" / "12_families_ck.json"
OUT = Path(__file__).parent.parent / "results_rootcause" / "12_families_results.json"

# Load checkpoint
done = set()
results = {}
if CK.exists():
    with open(CK) as f:
        cp = json.load(f)
    results = cp.get("results", {})
    done = set(cp.get("done", []))

PVS = [("rubric_order",["normal","reversed","random"]),("score_id",["numeric","letter","descriptive"]),("reference_answer",["no_ref","good_ref","poor_ref"])]

def call(mid, prompt):
    try:
        r = client.chat.completions.create(
            model=mid,
            messages=[{"role":"user","content":prompt}],
            max_tokens=5,
            temperature=0.0,
            timeout=15,
            stop=["\n", "###"]
        )
        return r.choices[0].message.content.strip()
    except:
        return None

for idx in range(0, len(FAMILIES), 2):
    base_name = FAMILIES[idx][1].replace("-IT", "").replace("-instruct", "").replace("-Instruct", "").replace("-base", "")
    
    for mid, nm in [FAMILIES[idx], FAMILIES[idx+1]]:
        if nm in done:
            print(f"SKIP {nm} (checkpointed)")
            continue
        
        print(f"\n[{nm}] ", end="", flush=True)
        rs = {}
        for pt, pv in PVS:
            rs[pt] = {}
            for vn in pv:
                scores = []
                for it in ITEMS:
                    text = call(mid, bp(pt, vn, it))
                    if text:
                        scores.append(gs(pt, vn)(text))
                    else:
                        scores.append(3)
                rs[pt][vn] = scores
            print(f"{pv[0][:3]}={sum(v for v in rs[pt][pv[0]])/len(rs[pt][pv[0]]):.1f}", end=" ")
        print()
        
        results[nm] = rs
        done.add(nm)
        with open(CK, "w") as f:
            json.dump({"results": results, "done": list(done)}, f)
        time.sleep(0.5)

with open(OUT, "w") as f:
    json.dump(results, f)
print(f"\nDONE. {OUT}")
