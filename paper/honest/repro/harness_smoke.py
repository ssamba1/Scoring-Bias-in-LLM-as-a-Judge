# Scoring-bias harness (FIXED) — logit scoring, per-item logging.
# Root-cause fix for the old "(0 scored)" runs: never rely on the model to EMIT a
# parseable digit. Instead read P(token) over the valid answer tokens at the score
# position and take the expected value. A score is ALWAYS produced.
#
# Runs on a Kaggle T4 (GPU + internet). Smoke config: 2 open models, 10 items.
import json, os, sys, time, traceback
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SMOKE = os.environ.get("SMOKE", "1") == "1"
N_ITEMS = 10 if SMOKE else 50
MODELS = ["Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"] if SMOKE else [
    "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-7B", "Qwen/Qwen2.5-7B-Instruct",
    "stabilityai/stablelm-2-1_6b", "stabilityai/stablelm-2-1_6b-chat",
]

# ---- 10 built-in items (instr, resp), mid-quality so bias can move either way ----
ITEMS = [
    ("Explain how photosynthesis works.", "Plants use sunlight to convert CO2 and water into glucose and oxygen."),
    ("What is the theory of relativity?", "It says space and time are linked and gravity bends spacetime."),
    ("Describe the water cycle.", "Water evaporates, forms clouds, then falls as rain and collects again."),
    ("What causes earthquakes?", "Tectonic plates shift and release energy that shakes the ground."),
    ("Explain how vaccines work.", "They train the immune system using a weakened or partial pathogen."),
    ("What is machine learning?", "Computers learn patterns from data instead of being explicitly programmed."),
    ("Describe how a bill becomes law.", "It is proposed, debated, voted on, and then signed by the executive."),
    ("What is inflation?", "A general rise in prices that reduces the purchasing power of money."),
    ("How do plants get nitrogen?", "Through the soil, often via bacteria that fix nitrogen for them."),
    ("What is a prime number?", "A number greater than 1 divisible only by 1 and itself."),
][:N_ITEMS]

# ---- probe -> variant -> (scale text, answer tokens, header) ----
NUM = ["1", "2", "3", "4", "5"]
LET = ["A", "B", "C", "D", "E"]
DESC = ["Poor", "Fair", "Good", "Great", "Excellent"]
PROBES = {
    "rubric_order": {
        "control":  ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score"),
        "reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst", NUM, "Score"),
        "random":   ("on a scale of 1 to 5 (3=worst, 5=middle, 1=best)",     NUM, "Score"),
    },
    "score_id": {
        "numeric":     ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM,  "Score"),
        "letter":      ("with a letter grade A to E, where A is best and E is worst", LET, "Grade"),
        "descriptive": ("as one of: Poor, Fair, Good, Great, Excellent",       DESC, "Rating"),
    },
    "reference_answer": {
        "none": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score", ""),
        "good": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score",
                 "For reference, an excellent answer would be thorough, precise, and complete.\n"),
        "poor": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score",
                 "For reference, a poor answer would be vague, wrong, or off-topic.\n"),
    },
}
# letter grades map A..E -> 5..1 (A best); descriptive Poor..Excellent -> 1..5
def token_values(answer_tokens):
    if answer_tokens is LET:   # A best -> 5 down to E -> 1
        return list(range(5, 0, -1))
    return list(range(1, len(answer_tokens) + 1))  # numeric / descriptive ascending

def build_prompt(instr, resp, scale, header, ref=""):
    return (f"{ref}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### {header}:")

@torch.no_grad()
def score_logits(tok, model, prompt, answer_tokens):
    """Return (expected_score, argmax_score). Expected = sum_k value_k * P(k);
    argmax = value of the single most probable answer token (discrete 1..5, for
    flip-rate). Both always defined -> no '0 scored' failure."""
    ids = tok(prompt, return_tensors="pt").to(model.device)
    logits = model(**ids).logits[0, -1].float()
    tids = []
    for a in answer_tokens:
        cand = tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False)
        tids.append(cand[0])
    probs = torch.softmax(logits[tids], dim=-1)
    vals = token_values(answer_tokens)
    vt = torch.tensor(vals, dtype=probs.dtype, device=probs.device)
    expected = float((probs * vt).sum())
    argmax = int(vals[int(torch.argmax(probs))])
    return expected, argmax

def pick_device():
    """Use CUDA only if it can actually run a kernel on this GPU (P100/sm_60 with
    a cu128 torch cannot -> fall back to CPU)."""
    if not torch.cuda.is_available():
        return "cpu"
    try:
        _ = (torch.ones(2, device="cuda") + 1).sum().item()
        return "cuda"
    except Exception as e:
        print(f"  CUDA unusable ({e}); using CPU", flush=True)
        return "cpu"

DEVICE = None  # set in main()

def run_model(name):
    print(f"\n=== {name} on {DEVICE} ===", flush=True)
    tok = AutoTokenizer.from_pretrained(name)
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype).to(DEVICE)
    model.eval()
    out = {}
    for probe, variants in PROBES.items():
        out[probe] = {}
        for variant, spec in variants.items():
            scale, atok, header = spec[0], spec[1], spec[2]
            ref = spec[3] if len(spec) > 3 else ""
            exp_items, arg_items = [], []
            for instr, resp in ITEMS:
                p = build_prompt(instr, resp, scale, header, ref)
                e, a = score_logits(tok, model, p, atok)
                exp_items.append(round(e, 4)); arg_items.append(a)
            out[probe][variant] = {"per_item": exp_items, "per_item_argmax": arg_items,
                                   "mean": round(sum(exp_items) / len(exp_items), 4)}
            print(f"  [{probe}/{variant}] {len(exp_items)} scored, mean={out[probe][variant]['mean']}", flush=True)
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return out

def main():
    print(f"torch {torch.__version__}  cuda={torch.cuda.is_available()}  "
          f"{torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}", flush=True)
    print(f"SMOKE={SMOKE}  N_ITEMS={N_ITEMS}  models={len(MODELS)}", flush=True)
    import transformers
    global DEVICE
    DEVICE = pick_device()
    env = {"torch": torch.__version__, "transformers": transformers.__version__,
           "cuda": torch.cuda.is_available(), "device_used": DEVICE,
           "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
    print("ENV", env, flush=True)
    errors = {}
    results = {}
    for name in MODELS:
        try:
            results[name.split("/")[-1]] = run_model(name)
        except Exception as e:
            errors[name] = f"{type(e).__name__}: {e}\n" + traceback.format_exc()
            print(f"  FAILED {name}: {e}", flush=True)
            traceback.print_exc()
    with open("/kaggle/working/results_fixed.json", "w") as f:
        json.dump({"config": {"smoke": SMOKE, "n_items": N_ITEMS, "models": MODELS},
                   "env": env, "errors": errors, "results": results}, f, indent=2)
    print("\nWROTE /kaggle/working/results_fixed.json", flush=True)
    # quick delta preview
    for m, r in results.items():
        for probe in r:
            means = [v["mean"] for v in r[probe].values()]
            print(f"  {m} {probe}: delta={round(max(means)-min(means),3)}", flush=True)

if __name__ == "__main__":
    main()
