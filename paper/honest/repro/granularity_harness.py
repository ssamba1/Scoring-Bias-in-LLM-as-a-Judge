# Scale-granularity harness (P17, CPU) -- does bias grow with the rating scale's
# value range, as the Var_sigma(v) term predicts? Scales: 1-3, 1-5, 0-9 (all
# single-token answer sets). Probes: rubric reversal + authority framing.
import os, sys, subprocess, json, time, shutil, glob, math

if os.environ.get("R") != "1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.49.0", "tokenizers==0.21.0", "accelerate==1.4.0"],
                   check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_gran.json"

PAIRS = [
    ("SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M-Instruct"),
    ("SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M-Instruct"),
    ("Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"),
    ("Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct"),
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

SCALES = {
    "K3":  {"tokens": ["1", "2", "3"], "values": [1, 2, 3],
            "control": "on a scale of 1 to 3, where 1 is worst and 3 is best",
            "reversed": "on a scale of 1 to 3, where 1 is best and 3 is worst"},
    "K5":  {"tokens": ["1", "2", "3", "4", "5"], "values": [1, 2, 3, 4, 5],
            "control": "on a scale of 1 to 5, where 1 is worst and 5 is best",
            "reversed": "on a scale of 1 to 5, where 1 is best and 5 is worst"},
    "K10": {"tokens": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "values": list(range(10)),
            "control": "on a scale of 0 to 9, where 0 is worst and 9 is best",
            "reversed": "on a scale of 0 to 9, where 0 is best and 9 is worst"},
}
AUTH = {"none": "", "expert": "The following response was written by a leading domain expert.\n",
        "novice": "The following response was written by a struggling beginner.\n"}

def build(instr, resp, scale, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### Score:")

@torch.no_grad()
def score(tok, model, prompt, tokens, values):
    ids = tok(prompt, return_tensors="pt")
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in tokens]
    probs = full[tids] / full[tids].sum()
    vt = torch.tensor([float(v) for v in values])
    p = probs.tolist()
    ent = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    return float((probs * vt).sum()), ent

def run_model(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32,
                                                 trust_remote_code=True)
    model.eval()
    out = {}
    for sk, sc in SCALES.items():
        out[sk] = {"range": sc["values"][-1] - sc["values"][0], "probes": {}}
        # rubric reversal
        rec = {}
        for variant in ("control", "reversed"):
            es, ents = [], []
            for instr, resp in ITEMS:
                e, en = score(tok, model, build(instr, resp, sc[variant], ""),
                              sc["tokens"], sc["values"])
                es.append(round(e, 4)); ents.append(en)
            rec[variant] = {"mean": round(sum(es) / len(es), 4),
                            "mean_entropy": round(sum(ents) / len(ents), 4)}
        out[sk]["probes"]["rubric_reversal"] = rec
        # authority framing (control scale)
        rec2 = {}
        for variant, prefix in AUTH.items():
            es, ents = [], []
            for instr, resp in ITEMS:
                e, en = score(tok, model, build(instr, resp, sc["control"], prefix),
                              sc["tokens"], sc["values"])
                es.append(round(e, 4)); ents.append(en)
            rec2[variant] = {"mean": round(sum(es) / len(es), 4),
                             "mean_entropy": round(sum(ents) / len(ents), 4)}
        out[sk]["probes"]["authority"] = rec2
        print(name.split("/")[-1], sk, "done", flush=True)
    del model, tok
    return out

def purge():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    payload = {"n_items": len(ITEMS), "errors": {}, "results": {}}
    for label, b, i in PAIRS:
        rec = {}
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
