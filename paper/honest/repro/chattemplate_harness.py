# Chat-template harness (P19, CPU) -- is the instruct-side bias an artifact of
# scoring instruct models in raw completion format (out of distribution for them)?
# Scores each instruct checkpoint BOTH ways: raw "### Score:" format and its own
# chat template; base checkpoints in raw format for the effect baseline.
import os, sys, subprocess, json, time, shutil, glob, math

if os.environ.get("R") != "1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.49.0", "tokenizers==0.21.0", "accelerate==1.4.0"],
                   check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_chat.json"

PAIRS = [
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

NUM = ["1", "2", "3", "4", "5"]
PROBES = {
    "rubric_order": {
        "control":  ("on a scale of 1 to 5, where 1 is worst and 5 is best", ""),
        "reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst", ""),
        "random":   ("on a scale of 1 to 5 (3=worst, 5=middle, 1=best)", ""),
    },
    "authority": {
        "none":   ("on a scale of 1 to 5, where 1 is worst and 5 is best", ""),
        "expert": ("on a scale of 1 to 5, where 1 is worst and 5 is best",
                   "The following response was written by a leading domain expert.\n"),
        "novice": ("on a scale of 1 to 5, where 1 is worst and 5 is best",
                   "The following response was written by a struggling beginner.\n"),
    },
}

def body(instr, resp, scale, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}")

def raw_prompt(instr, resp, scale, prefix):
    return body(instr, resp, scale, prefix) + "\n### Score:"

def chat_prompt(tok, instr, resp, scale, prefix):
    msg = body(instr, resp, scale, prefix) + "\nRespond with only the score."
    return tok.apply_chat_template([{"role": "user", "content": msg}],
                                   tokenize=False, add_generation_prompt=True)

@torch.no_grad()
def score(tok, model, prompt):
    ids = tok(prompt, return_tensors="pt")
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in NUM]
    probs = full[tids] / full[tids].sum()
    p = probs.tolist()
    ent = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    return float((probs * torch.tensor([1., 2., 3., 4., 5.])).sum()), ent

def run_model(name, formats):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32,
                                                 trust_remote_code=True)
    model.eval()
    out = {}
    for fmt in formats:
        out[fmt] = {}
        for probe, variants in PROBES.items():
            out[fmt][probe] = {}
            for variant, (scale, prefix) in variants.items():
                es, ents = [], []
                for instr, resp in ITEMS:
                    p = (raw_prompt(instr, resp, scale, prefix) if fmt == "raw"
                         else chat_prompt(tok, instr, resp, scale, prefix))
                    e, en = score(tok, model, p)
                    es.append(round(e, 4)); ents.append(en)
                out[fmt][probe][variant] = {
                    "mean": round(sum(es) / len(es), 4),
                    "mean_entropy": round(sum(ents) / len(ents), 4)}
    del model, tok
    return out

def purge():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    payload = {"n_items": len(ITEMS), "errors": {}, "results": {}}
    for label, b, i in PAIRS:
        rec = {}
        for kind, mid, fmts in (("base", b, ["raw"]), ("instruct", i, ["raw", "chat"])):
            t0 = time.time()
            try:
                rec[kind] = run_model(mid, fmts)
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
