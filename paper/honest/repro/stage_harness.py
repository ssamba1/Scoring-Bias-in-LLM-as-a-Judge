# Scoring-bias harness (ALIGNMENT-STAGE ABLATION) — logit scoring, per-item + argmax + domain.
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
                    "tokenizers==0.21.0", "accelerate==1.4.0"], check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SMOKE = os.environ.get("SMOKE", "0") == "1"
OUT_PATH = "/kaggle/working/results_stages.json"

# (label, hf_id, family, stage, stage_order, params_b) -- alignment-stage ladder.
# Which post-training stage inflates responsiveness/bias? OLMo-2 and Tulu-3 publish
# every intermediate checkpoint. Ascending size so the small family saves first.
MODELS = [
    ("OLMo-2-1B-base",     "allenai/OLMo-2-0425-1B",          "OLMo-2-1B", "base",     0, 1.0),
    ("OLMo-2-1B-SFT",      "allenai/OLMo-2-0425-1B-SFT",      "OLMo-2-1B", "SFT",      1, 1.0),
    ("OLMo-2-1B-DPO",      "allenai/OLMo-2-0425-1B-DPO",      "OLMo-2-1B", "DPO",      2, 1.0),
    ("OLMo-2-1B-RLVR",     "allenai/OLMo-2-0425-1B-Instruct", "OLMo-2-1B", "RLVR",     3, 1.0),
    ("OLMo-2-7B-base",     "allenai/OLMo-2-1124-7B",          "OLMo-2-7B", "base",     0, 7.0),
    ("OLMo-2-7B-SFT",      "allenai/OLMo-2-1124-7B-SFT",      "OLMo-2-7B", "SFT",      1, 7.0),
    ("OLMo-2-7B-DPO",      "allenai/OLMo-2-1124-7B-DPO",      "OLMo-2-7B", "DPO",      2, 7.0),
    ("OLMo-2-7B-RLVR",     "allenai/OLMo-2-1124-7B-Instruct", "OLMo-2-7B", "RLVR",     3, 7.0),
    ("Tulu-3-8B-SFT",      "allenai/Llama-3.1-Tulu-3-8B-SFT", "Tulu-3-8B", "SFT",      1, 8.0),
    ("Tulu-3-8B-DPO",      "allenai/Llama-3.1-Tulu-3-8B-DPO", "Tulu-3-8B", "DPO",      2, 8.0),
    ("Tulu-3-8B-RLVR",     "allenai/Llama-3.1-Tulu-3-8B",     "Tulu-3-8B", "RLVR",     3, 8.0),
]
if SMOKE:
    MODELS = MODELS[:1]

ITEMS = [
  ("Explain how photosynthesis works.", "Plants use sunlight to convert CO2 and water into glucose and oxygen.", "science"),
  ("What is the theory of relativity?", "Einstein theory says space and time are relative to observer frame.", "science"),
  ("Describe the water cycle.", "Water evaporates from oceans forms clouds returns as precipitation.", "science"),
  ("What causes earthquakes?", "Tectonic plates shift along fault lines releasing seismic waves.", "science"),
  ("Explain how vaccines work.", "Vaccines train immune system to recognize pathogens via antigens.", "science"),
  ("What is DNA?", "DNA carries genetic instructions for growth development reproduction.", "science"),
  ("Describe the solar system.", "Solar system has 8 planets orbiting the Sun.", "science"),
  ("What is entropy?", "Entropy measures disorder. Second law says entropy always increases.", "science"),
  ("How do batteries work?", "Chemical reactions create electron flow between electrodes via electrolyte.", "science"),
  ("What is a black hole?", "Region where gravity prevents anything including light from escaping.", "science"),
  ("What is machine learning?", "AI subset where systems learn patterns from data without explicit programming.", "technology"),
  ("Describe cloud computing.", "On-demand computing resources delivered over internet.", "technology"),
  ("What is an API?", "Interface allowing different software applications to communicate.", "technology"),
  ("Explain how encryption works.", "Algorithms transform readable data into encoded form using keys.", "technology"),
  ("What is a database index?", "Data structure that speeds up retrieval like a book index.", "technology"),
  ("What is Python?", "High-level programming language known for readability and libraries.", "technology"),
  ("Explain the internet.", "Global network of computers communicating via TCP/IP protocols.", "technology"),
  ("What is a blockchain?", "Distributed ledger where transactions are recorded in immutable blocks.", "technology"),
  ("What is an operating system?", "Software managing hardware providing services for applications.", "technology"),
  ("Explain neural networks.", "Computing systems inspired by biological neurons learning from data.", "technology"),
  ("What caused World War 1?", "Assassination of Archduke Ferdinand triggered alliances and nationalism.", "humanities"),
  ("Explain democracy.", "System where citizens vote for representatives to make decisions.", "humanities"),
  ("What is the Renaissance?", "Cultural rebirth in Europe from 14th to 17th century.", "humanities"),
  ("Describe capitalism.", "Economic system with private ownership profit motive market competition.", "humanities"),
  ("What is the UN?", "International organization promoting peace security cooperation among nations.", "humanities"),
  ("Explain the Cold War.", "Geopolitical tension between US and USSR from 1947 to 1991.", "humanities"),
  ("What is ethics?", "Study of moral principles guiding right and wrong behavior.", "humanities"),
  ("Describe feudalism.", "Medieval hierarchy where lords granted land to vassals for service.", "humanities"),
  ("What is philosophy?", "Study of fundamental questions about existence knowledge and values.", "humanities"),
  ("Explain globalization.", "Increasing interconnection of economies cultures populations worldwide.", "humanities"),
  ("How to cook pasta?", "Boil water add salt cook until al dente drain serve with sauce.", "daily_life"),
  ("What is a healthy diet?", "Balanced meals with fruits vegetables protein whole grains limited processed foods.", "daily_life"),
  ("Explain how cars work.", "Engine burns fuel to create combustion turning pistons rotating wheels.", "daily_life"),
  ("How to exercise properly?", "Warm up strength cardio with proper form cool down stretch.", "daily_life"),
  ("Describe sleep cycles.", "Sleep alternates between REM and non-REM stages in 90-minute cycles.", "daily_life"),
  ("What is meditation?", "Practice of focusing attention for mental clarity emotional calm.", "daily_life"),
  ("Explain first aid.", "Emergency care including CPR wound cleaning calling for help.", "daily_life"),
  ("How to save money?", "Track expenses create budget reduce unnecessary spending save regularly.", "daily_life"),
  ("What is climate change?", "Long-term temperature weather shifts due to greenhouse gas emissions.", "daily_life"),
  ("Explain recycling.", "Processing waste into new products to reduce resource consumption.", "daily_life"),
  ("What is calculus?", "Mathematical study of change involving derivatives and integrals.", "mathematics"),
  ("Explain p-value.", "Probability of observing results as extreme assuming null hypothesis is true.", "mathematics"),
  ("What is a prime number?", "Number divisible only by 1 and itself like 2 3 5 7 11.", "mathematics"),
  ("Describe standard deviation.", "Measure of how spread out numbers are from the mean.", "mathematics"),
  ("What is a logarithm?", "Inverse of exponentiation showing what power a base must be raised to.", "mathematics"),
  ("Explain probability.", "Measure of likelihood that an event will occur from 0 to 1.", "mathematics"),
  ("What is Bayes theorem?", "Describes probability based on prior knowledge of related conditions.", "mathematics"),
  ("Explain linear regression.", "Method to model relationship between variables by fitting linear equation.", "mathematics"),
  ("What is a derivative?", "Rate at which a function changes at a given point.", "mathematics"),
  ("Describe correlation.", "Statistical measure of how two variables move together from -1 to 1.", "mathematics"),
]
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
    for label, mid, family, stage, order, pb in MODELS:
        t0 = time.time()
        rec = {"family": family, "stage": stage, "stage_order": order, "params_b": pb}
        try:
            rec["scores"] = score_one(mid)
            print(f"  {label} ok ({time.time()-t0:.0f}s)", flush=True)
        except Exception as e:
            payload["errors"][mid] = f"{type(e).__name__}: {e}"
            print(f"  FAILED {mid}: {e}", flush=True)
        purge_cache()
        payload["results"][label] = rec
        with open(OUT_PATH, "w") as f:
            json.dump(payload, f, indent=2)
    print("WROTE", OUT_PATH, "models:", list(payload["results"].keys()), flush=True)

if __name__ == "__main__":
    main()
