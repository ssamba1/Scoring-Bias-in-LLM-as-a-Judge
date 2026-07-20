# Sampled-readout harness (P16, CPU) -- does the standard generate-and-parse
# protocol (a) drop base-model items at a much higher rate (the confound), and
# (b) agree with expected-value scoring where it parses at all?
import os, sys, subprocess, json, time, shutil, glob, re

if os.environ.get("R") != "1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.49.0", "tokenizers==0.21.0", "accelerate==1.4.0"],
                   check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_sampled.json"
torch.manual_seed(42)

PAIRS = [
    ("SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M", "HuggingFaceTB/SmolLM2-135M-Instruct"),
    ("SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M-Instruct"),
    ("Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"),
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
K_SAMPLES = 8
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

def build(instr, resp, scale, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### Score:")

@torch.no_grad()
def ev_score(tok, model, prompt):
    ids = tok(prompt, return_tensors="pt")
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in NUM]
    probs = full[tids] / full[tids].sum()
    return float((probs * torch.tensor([1., 2., 3., 4., 5.])).sum())

@torch.no_grad()
def sampled_scores(tok, model, prompt, k=K_SAMPLES):
    ids = tok(prompt, return_tensors="pt")
    outs = model.generate(**ids, do_sample=True, temperature=1.0, top_p=1.0,
                          max_new_tokens=6, num_return_sequences=k,
                          pad_token_id=tok.eos_token_id)
    scores = []
    for o in outs:
        txt = tok.decode(o[ids["input_ids"].shape[1]:], skip_special_tokens=True)
        m = re.search(r"[1-5]", txt)
        scores.append(int(m.group()) if m else None)
    return scores

def run_model(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32,
                                                 trust_remote_code=True)
    model.eval()
    out = {}
    for probe, variants in PROBES.items():
        out[probe] = {}
        for variant, (scale, prefix) in variants.items():
            evs, samp, parsed = [], [], 0
            for instr, resp in ITEMS:
                p = build(instr, resp, scale, prefix)
                evs.append(round(ev_score(tok, model, p), 4))
                ss = sampled_scores(tok, model, p)
                ok = [s for s in ss if s is not None]
                parsed += len(ok)
                samp.append(round(sum(ok) / len(ok), 4) if ok else None)
            n_total = len(ITEMS) * K_SAMPLES
            out[probe][variant] = {
                "ev_per_item": evs,
                "sampled_per_item": samp,
                "parse_rate": round(parsed / n_total, 4),
                "ev_mean": round(sum(evs) / len(evs), 4),
                "sampled_mean": (round(sum(s for s in samp if s is not None) /
                                       max(1, sum(1 for s in samp if s is not None)), 4)
                                 if any(s is not None for s in samp) else None)}
            print(name.split("/")[-1], probe, variant,
                  "parse", out[probe][variant]["parse_rate"], flush=True)
    del model, tok
    return out

def purge():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    payload = {"k_samples": K_SAMPLES, "n_items": len(ITEMS), "errors": {}, "results": {}}
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
