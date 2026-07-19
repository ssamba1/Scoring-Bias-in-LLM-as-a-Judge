# Scoring-bias harness (PUBLIC-DATASET ITEMS, C5 replication) — logit scoring, per-item + argmax + domain.
# 13 open-license base/instruct families, 0.13B-8B. Fixes the P100+cu128 GPU by
# reinstalling a compatible torch+transformers, then restarting. Incremental save;
# HF cache is purged per model to avoid disk fill. No synthetic data.
import os, sys, subprocess, json, time, traceback, shutil, glob
# ---- enable GPU: the stock cu128 torch can't run the P100 (sm_60); pin a stack that
# can (torch 2.6 cu124 + matching torchvision + transformers 4.49), then restart. ----
def _cuda_bad():
    try:
        import torch
        if not torch.cuda.is_available():
            return False
        (torch.ones(4, device="cuda") @ torch.ones(4, device="cuda")).item()
        return False
    except Exception:
        return True
if os.environ.get("R") != "1" and _cuda_bad():
    print("Pinning GPU stack (torch2.6/cu124 + transformers4.49)...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "torch==2.6.0",
                    "torchvision==0.21.0", "--index-url",
                    "https://download.pytorch.org/whl/cu124"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "transformers==4.49.0",
                    "tokenizers==0.21.0", "accelerate==1.4.0", "datasets"], check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SMOKE = os.environ.get("SMOKE", "0") == "1"
OUT_PATH = "/kaggle/working/results_dolly.json"

# (family_label, base_id, instruct_id, params_b, training_of_instruct)
# ascending by size so the small families all complete + save before big ones
PAIRS = [
    ("SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M-Instruct", 0.135, "SFT+DPO"),
    ("SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M-Instruct", 0.36, "SFT+DPO"),
    ("Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct", 0.5, "RLHF"),
    ("Falcon3-1B",   "tiiuae/Falcon3-1B-Base", "tiiuae/Falcon3-1B-Instruct", 1.0, "SFT+DPO"),
    ("Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct", 1.5, "RLHF"),
    ("SmolLM2-1.7B", "HuggingFaceTB/SmolLM2-1.7B", "HuggingFaceTB/SmolLM2-1.7B-Instruct", 1.7, "SFT+DPO"),
    ("Granite-3.1-2B", "ibm-granite/granite-3.1-2b-base", "ibm-granite/granite-3.1-2b-instruct", 2.0, "SFT+RLHF"),
    ("Qwen2.5-3B",   "Qwen/Qwen2.5-3B",   "Qwen/Qwen2.5-3B-Instruct",   3.0, "RLHF"),
]
if SMOKE:
    PAIRS = PAIRS[:2]

# Items drawn from a PUBLIC dataset (databricks-dolly-15k, CC BY-SA 3.0) rather
# than author-written, to remove item authorship as a variable. Deterministic
# selection: open_qa/general_qa, no context, instruction and response length
# bounded; responses truncated to the first sentence to hold quality mid-level.
def _load_items(n=50, seed=42):
    import random
    from datasets import load_dataset
    ds = load_dataset("databricks/databricks-dolly-15k", split="train")
    cand = []
    for ex in ds:
        if ex["category"] not in ("open_qa", "general_qa"):
            continue
        if ex["context"]:
            continue
        instr = ex["instruction"].strip()
        resp = ex["response"].strip().split("\n")[0]
        first = resp.split(". ")[0].strip()
        if not first.endswith("."):
            first += "."
        if 20 <= len(instr) <= 90 and 40 <= len(first) <= 160:
            cand.append((instr, first, ex["category"]))
    random.Random(seed).shuffle(cand)
    return cand[:n]

ITEMS = _load_items()
if SMOKE:
    ITEMS = ITEMS[:6]

NUM = ["1", "2", "3", "4", "5"]; LET = ["A", "B", "C", "D", "E"]
DESC = ["Poor", "Fair", "Good", "Great", "Excellent"]
PROBES = {
    "rubric_order": {
        "control":  ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score", ""),
        "reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst", NUM, "Score", ""),
        "random":   ("on a scale of 1 to 5 (3=worst, 5=middle, 1=best)",     NUM, "Score", ""),
    },
    "score_id": {
        "numeric":     ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM,  "Score", ""),
        "letter":      ("with a letter grade A to E, where A is best and E is worst", LET, "Grade", ""),
        "descriptive": ("as one of: Poor, Fair, Good, Great, Excellent",       DESC, "Rating", ""),
    },
    "reference_answer": {
        "none": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score", ""),
        "good": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score",
                 "For reference, an excellent answer would be thorough, precise, and complete.\n"),
        "poor": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score",
                 "For reference, a poor answer would be vague, wrong, or off-topic.\n"),
    },
}

# ---- content-perturbation probes (test the theory BEYOND the 3 scoring biases) ----
# Each variant: (prefix_prepended, response_transform). Scored numeric 1-5.
_FILLER = (" To elaborate, this is a rich topic worth considering carefully from "
           "several complementary angles, each adding useful nuance and context.")
def _id(r): return r
def _verbose(r): return r + _FILLER + _FILLER
def _terse(r): return (r.split(".")[0] or r).strip() + "."
PERTURB = {
    "authority": {   # prestige/authority bias -- framing must not change quality
        "none":   ("", _id),
        "expert": ("The following response was written by a leading domain expert.\n", _id),
        "novice": ("The following response was written by a struggling beginner.\n", _id),
    },
    "verbosity": {   # verbosity/length bias -- padding must not change quality
        "control": ("", _id),
        "verbose": ("", _verbose),
        "terse":   ("", _terse),
    },
}
_NUM_SCALE = "on a scale of 1 to 5, where 1 is worst and 5 is best"

def token_values(a):
    return list(range(5, 0, -1)) if a is LET else list(range(1, len(a) + 1))

def build_prompt(instr, resp, scale, header, ref):
    return (f"{ref}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### {header}:")

def _pick_device():
    if not torch.cuda.is_available():
        return "cpu"
    try:
        (torch.ones(4, device="cuda") @ torch.ones(4, device="cuda")).item()
        return "cuda"
    except Exception as e:
        print(f"CUDA unusable ({str(e)[:80]}); using CPU", flush=True)
        return "cpu"

DEVICE = _pick_device()

import math

@torch.no_grad()
def score_logits(tok, model, prompt, answer_tokens):
    """Return dict: expected score, discrete argmax score, entropy (bits) of the
    score distribution, max prob (decisiveness), mass on answer tokens vs all vocab,
    and the K-way probability vector. The distribution IS the mechanism signal."""
    ids = tok(prompt, return_tensors="pt").to(DEVICE)
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in answer_tokens]
    mass = float(full[tids].sum())                       # P(answer set) vs whole vocab
    probs = full[tids] / full[tids].sum()
    vals = token_values(answer_tokens)
    vt = torch.tensor(vals, dtype=probs.dtype, device=probs.device)
    p = probs.tolist()
    ent = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    return {"exp": round(float((probs * vt).sum()), 4),
            "arg": int(vals[int(torch.argmax(probs))]),
            "ent": round(ent, 4), "maxp": round(float(probs.max()), 4),
            "mass": round(mass, 4), "dist": [round(x, 4) for x in p]}

def score_one(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype, trust_remote_code=True).to(DEVICE)
    model.eval()
    def measure(prompts, atok):
        exp, arg, ent, maxp, mass, dists = [], [], [], [], [], []
        for p in prompts:
            r = score_logits(tok, model, p, atok)
            exp.append(r["exp"]); arg.append(r["arg"]); ent.append(r["ent"])
            maxp.append(r["maxp"]); mass.append(r["mass"]); dists.append(r["dist"])
        n = len(exp)
        md = [round(sum(d[k] for d in dists) / n, 4) for k in range(len(dists[0]))]
        return {"per_item": exp, "per_item_argmax": arg, "per_item_entropy": ent,
                "mean": round(sum(exp) / n, 4), "mean_entropy": round(sum(ent) / n, 4),
                "mean_maxprob": round(sum(maxp) / n, 4), "mean_mass": round(sum(mass) / n, 4),
                "mean_dist": md}
    out = {}
    # format-perturbation probes (the 3 scoring biases)
    for probe, variants in PROBES.items():
        out[probe] = {}
        for variant, (scale, atok, header, ref) in variants.items():
            out[probe][variant] = measure(
                [build_prompt(i, r, scale, header, ref) for i, r, _d in ITEMS], atok)
    # content-perturbation probes (authority, verbosity) -- generality test
    for probe, variants in PERTURB.items():
        out[probe] = {}
        for variant, (prefix, tf) in variants.items():
            out[probe][variant] = measure(
                [build_prompt(i, tf(r), _NUM_SCALE, "Score", prefix) for i, r, _d in ITEMS], NUM)
    del model, tok
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    return out

def purge_cache():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    import transformers
    env = {"torch": torch.__version__, "transformers": transformers.__version__,
           "device": DEVICE, "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
    print("ENV", env, flush=True)
    payload = {"env": env, "smoke": SMOKE, "n_items": len(ITEMS),
               "domains": [d for *_, d in ITEMS], "errors": {}, "results": {}}
    for label, base_id, inst_id, pb, train in PAIRS:
        rec = {"params_b": pb, "training": train}
        for kind, mid in (("base", base_id), ("instruct", inst_id)):
            t0 = time.time()
            try:
                rec[kind] = score_one(mid)
                print(f"  {label}/{kind} ok ({time.time()-t0:.0f}s)", flush=True)
            except Exception as e:
                payload["errors"][mid] = f"{type(e).__name__}: {e}"
                print(f"  FAILED {mid}: {e}", flush=True)
            purge_cache()
        payload["results"][label] = rec
        with open(OUT_PATH, "w") as f:
            json.dump(payload, f, indent=2)
    print("\nWROTE", OUT_PATH, "families:", list(payload["results"].keys()), flush=True)

if __name__ == "__main__":
    main()
