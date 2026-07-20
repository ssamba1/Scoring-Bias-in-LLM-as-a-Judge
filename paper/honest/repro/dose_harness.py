# Dose-response harness (P14, CPU) -- does bias grow with nuisance MAGNITUDE, and
# is the instruct slope steeper? Verbosity dose = number of filler units appended;
# authority dose = graded strength of the expert framing. Small models, CPU-friendly.
import os, sys, subprocess, json, time, shutil, glob, math

if os.environ.get("R") != "1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.49.0", "tokenizers==0.21.0", "accelerate==1.4.0"],
                   check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_dose.json"

PAIRS = [
    ("SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M-Instruct", 0.135),
    ("SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M-Instruct", 0.36),
    ("Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct", 0.5),
    ("Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct", 1.5),
]

ITEMS = [
 ("Explain how photosynthesis works.", "Plants use sunlight to convert CO2 and water into glucose and oxygen."),
 ("What causes earthquakes?", "Tectonic plates shift along fault lines releasing seismic waves."),
 ("What is a prime number?", "Number divisible only by 1 and itself like 2 3 5 7 11."),
 ("Explain how vaccines work.", "Vaccines train immune system to recognize pathogens via antigens."),
 ("Describe the water cycle.", "Water evaporates from oceans forms clouds returns as precipitation."),
 ("What is machine learning?", "AI subset where systems learn patterns from data without explicit programming."),
 ("What is DNA?", "DNA carries genetic instructions for growth development reproduction."),
 ("What is a black hole?", "Region where gravity prevents anything including light from escaping."),
 ("Explain the internet.", "Global network of computers communicating via TCP/IP protocols."),
 ("What is an API?", "Interface allowing different software applications to communicate."),
 ("Explain democracy.", "System where citizens vote for representatives to make decisions."),
 ("What is ethics?", "Study of moral principles guiding right and wrong behavior."),
 ("What is a healthy diet?", "Balanced meals with fruits vegetables protein whole grains limited processed foods."),
 ("What is meditation?", "Practice of focusing attention for mental clarity emotional calm."),
 ("What is climate change?", "Long-term temperature weather shifts due to greenhouse gas emissions."),
 ("What is calculus?", "Mathematical study of change involving derivatives and integrals."),
 ("Explain probability.", "Measure of likelihood that an event will occur from 0 to 1."),
 ("What is a derivative?", "Rate at which a function changes at a given point."),
 ("Describe standard deviation.", "Measure of how spread out numbers are from the mean."),
 ("Explain linear regression.", "Method to model relationship between variables by fitting linear equation."),
]

NUM = ["1", "2", "3", "4", "5"]
SCALE = "on a scale of 1 to 5, where 1 is worst and 5 is best"
_FILLER = (" To elaborate, this is a rich topic worth considering carefully from "
           "several complementary angles, each adding useful nuance and context.")

# dose 0 = control for both probes
VERBOSITY_DOSES = [0, 1, 2, 4, 8]           # filler units appended
AUTHORITY_DOSES = [                          # graded framing strength
    "",
    "The following response was written by someone with some familiarity with the topic.\n",
    "The following response was written by a knowledgeable person.\n",
    "The following response was written by an expert.\n",
    "The following response was written by the world's foremost authority on the topic.\n",
]

def build(instr, resp, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {SCALE}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### Score:")

@torch.no_grad()
def score(tok, model, prompt):
    ids = tok(prompt, return_tensors="pt")
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in NUM]
    probs = full[tids] / full[tids].sum()
    vt = torch.tensor([1., 2., 3., 4., 5.])
    p = probs.tolist()
    ent = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    return float((probs * vt).sum()), ent

def run_model(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32,
                                                 trust_remote_code=True)
    model.eval()
    out = {"verbosity": {}, "authority": {}}
    for dose in VERBOSITY_DOSES:
        es, ents = [], []
        for instr, resp in ITEMS:
            e, en = score(tok, model, build(instr, resp + _FILLER * dose, ""))
            es.append(round(e, 4)); ents.append(en)
        out["verbosity"][str(dose)] = {"per_item": es,
                                       "mean": round(sum(es) / len(es), 4),
                                       "mean_entropy": round(sum(ents) / len(ents), 4)}
    for i, prefix in enumerate(AUTHORITY_DOSES):
        es, ents = [], []
        for instr, resp in ITEMS:
            e, en = score(tok, model, build(instr, resp, prefix))
            es.append(round(e, 4)); ents.append(en)
        out["authority"][str(i)] = {"per_item": es,
                                    "mean": round(sum(es) / len(es), 4),
                                    "mean_entropy": round(sum(ents) / len(ents), 4)}
    del model, tok
    return out

def purge():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    payload = {"doses": {"verbosity": VERBOSITY_DOSES, "authority": len(AUTHORITY_DOSES)},
               "n_items": len(ITEMS), "errors": {}, "results": {}}
    for label, b, i, pb in PAIRS:
        rec = {"params_b": pb}
        for kind, mid in (("base", b), ("instruct", i)):
            t0 = time.time()
            try:
                rec[kind] = run_model(mid)
                print(f"{label}/{kind} ok ({time.time()-t0:.0f}s)", flush=True)
            except Exception as e:
                payload["errors"][mid] = f"{type(e).__name__}: {e}"
                print("FAIL", mid, e, flush=True)
            purge()
        payload["results"][label] = rec
        with open(OUT_PATH, "w") as f:
            json.dump(payload, f, indent=2)
    print("WROTE", OUT_PATH, flush=True)

if __name__ == "__main__":
    main()
