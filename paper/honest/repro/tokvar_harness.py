# Readout-variant harness (P18, CPU) -- is the measured bias robust to WHICH
# answer-token variant the readout uses? Three readouts from the same logits:
# bare digits ("1".."5") vs the FULL union of vocab tokens decoding to each digit
# (v2: vocab scan; the v1 space-prefixed readout was degenerate on these tokenizers).
# If bias Delta and the base-vs-instruct effect agree across readouts, the
# "tiny bare-token mass" objection to expected-value scoring is closed.
import os, sys, subprocess, json, time, shutil, glob, math

if os.environ.get("R") != "1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.49.0", "tokenizers==0.21.0", "accelerate==1.4.0"],
                   check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_tokvar.json"

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

def build(instr, resp, scale, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### Score:")

_DIGIT_SETS = {}

def digit_token_sets(tok, name):
    """All single vocab tokens that decode (after strip) to each digit.
    v2 fix: ' 4' tokenizes as [space][4] on these tokenizers, so the v1
    space-prefixed readout was degenerate; the vocab scan gets the true set."""
    if name in _DIGIT_SETS:
        return _DIGIT_SETS[name]
    sets = {a: [] for a in NUM}
    for i in range(len(tok)):
        s = tok.decode([i]).strip()
        if s in sets:
            sets[s].append(i)
    _DIGIT_SETS[name] = sets
    return sets

@torch.no_grad()
def score_variants(tok, model, prompt, dsets):
    ids = tok(prompt, return_tensors="pt")
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    vt = torch.tensor([1., 2., 3., 4., 5.])
    outp = {}
    bare = [(tok.encode(a, add_special_tokens=False) or [None])[0] for a in NUM]
    if all(t is not None for t in bare) and len(set(bare)) == 5:
        pr = full[bare]
        mass = float(pr.sum())
        pr = pr / pr.sum()
        outp["bare"] = {"exp": round(float((pr * vt).sum()), 4), "mass": round(mass, 5)}
    else:
        outp["bare"] = None
    pu = torch.stack([full[dsets[a]].sum() for a in NUM])
    mass = float(pu.sum())
    pu = pu / pu.sum()
    outp["union"] = {"exp": round(float((pu * vt).sum()), 4), "mass": round(mass, 5)}
    # v3: the space-appended position -- prompt + " " puts the digit choice at the
    # immediate next token, where the bulk of the numeric mass lives.
    ids2 = tok(prompt + " ", return_tensors="pt")
    full2 = torch.softmax(model(**ids2).logits[0, -1].float(), dim=-1)
    if all(t_ is not None for t_ in bare) and len(set(bare)) == 5:
        pr2 = full2[bare]
        mass2 = float(pr2.sum())
        pr2 = pr2 / pr2.sum()
        outp["space_appended"] = {"exp": round(float((pr2 * vt).sum()), 4),
                                  "mass": round(mass2, 5)}
    else:
        outp["space_appended"] = None
    return outp

def run_model(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32,
                                                 trust_remote_code=True)
    model.eval()
    dsets = digit_token_sets(tok, name)
    out = {"digit_set_sizes": {a: len(v) for a, v in dsets.items()}}
    for probe, variants in PROBES.items():
        out[probe] = {}
        for variant, (scale, prefix) in variants.items():
            per = {"bare": [], "union": [], "space_appended": []}
            masses = {"bare": [], "union": [], "space_appended": []}
            for instr, resp in ITEMS:
                sv = score_variants(tok, model, build(instr, resp, scale, prefix), dsets)
                for k in per:
                    if sv.get(k):
                        per[k].append(sv[k]["exp"]); masses[k].append(sv[k]["mass"])
            out[probe][variant] = {
                k: {"mean": round(sum(v) / len(v), 4),
                    "mean_mass": round(sum(masses[k]) / len(masses[k]), 5)}
                for k, v in per.items() if v}
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
