# Ten-template breadth harness (P15, CPU) -- does the negative entropy-bias law and
# the instruct>base pattern hold across ten surface-distinct prompt templates?
# Small models only (CPU-friendly): SmolLM2-135M/360M, Qwen2.5-0.5B.
import os, sys, subprocess, json, time, shutil, glob, math

if os.environ.get("R") != "1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.49.0", "tokenizers==0.21.0", "accelerate==1.4.0"],
                   check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/results_t10.json"

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

NUM = ["1", "2", "3", "4", "5"]; LET = ["A", "B", "C", "D", "E"]
DESC = ["Poor", "Fair", "Good", "Great", "Excellent"]
NUM_SCALE = "on a scale of 1 to 5, where 1 is worst and 5 is best"

# ten surface-distinct templates: {p}=prefix, {s}=scale, {i}=instruction, {r}=response, {h}=header
TEMPLATES = {
 "T01": "{p}Evaluate the following response to the instruction {s}.\n### Instruction: {i}\n### Response: {r}\n### {h}:",
 "T02": "{p}You are grading an answer {s}.\nQuestion: {i}\nAnswer: {r}\n{h}:",
 "T03": "{p}Rate the answer's quality {s}.\n[Q] {i}\n[A] {r}\n[{h}] ",
 "T04": "{p}As an impartial evaluator, judge this response {s}.\nTask: {i}\nSubmission: {r}\nYour {h}:",
 "T05": "{p}Please assess the reply below {s}.\n<prompt>{i}</prompt>\n<reply>{r}</reply>\n<{h}>",
 "T06": "{p}Grade the following {s}.\nINSTRUCTION: {i}\nRESPONSE: {r}\nGRADING -- {h}:",
 "T07": "{p}Review this answer and score it {s}.\n1) The question was: {i}\n2) The answer given: {r}\n3) {h}:",
 "T08": "{p}Here is a task and a response. Score the response {s}.\nTask description: {i}\nCandidate response: {r}\nFinal {h}:",
 "T09": "{p}Quality check {s}.\n>> {i}\n<< {r}\n== {h}:",
 "T10": "{p}An assistant answered a user. Rate the answer {s}.\nUser: {i}\nAssistant: {r}\nRating -- {h}:",
}

PROBES = {
 "rubric_order": {"control": (NUM_SCALE, NUM, "Score", ""),
                  "reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst", NUM, "Score", ""),
                  "random":   ("on a scale of 1 to 5 (3=worst, 5=middle, 1=best)", NUM, "Score", "")},
 "score_id": {"numeric": (NUM_SCALE, NUM, "Score", ""),
              "letter":  ("with a letter grade A to E, where A is best and E is worst", LET, "Grade", ""),
              "descriptive": ("as one of: Poor, Fair, Good, Great, Excellent", DESC, "Rating", "")},
 "authority": {"none":   (NUM_SCALE, NUM, "Score", ""),
               "expert": (NUM_SCALE, NUM, "Score", "The following response was written by a leading domain expert.\n"),
               "novice": (NUM_SCALE, NUM, "Score", "The following response was written by a struggling beginner.\n")},
}

def vals(a):
    return list(range(5, 0, -1)) if a is LET else list(range(1, len(a) + 1))

@torch.no_grad()
def score(tok, model, prompt, atok):
    ids = tok(prompt, return_tensors="pt")
    full = torch.softmax(model(**ids).logits[0, -1].float(), dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in atok]
    probs = full[tids] / full[tids].sum()
    v = vals(atok)
    vt = torch.tensor(v, dtype=probs.dtype)
    p = probs.tolist()
    ent = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    return float((probs * vt).sum()), ent

def run_model(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32,
                                                 trust_remote_code=True)
    model.eval()
    out = {}
    for tname, tmpl in TEMPLATES.items():
        out[tname] = {}
        for probe, variants in PROBES.items():
            out[tname][probe] = {}
            for variant, (s, atok, h, p) in variants.items():
                es, ents = [], []
                for instr, resp in ITEMS:
                    e, en = score(tok, model,
                                  tmpl.format(p=p, s=s, i=instr, r=resp, h=h), atok)
                    es.append(round(e, 4)); ents.append(en)
                out[tname][probe][variant] = {
                    "mean": round(sum(es) / len(es), 4),
                    "mean_entropy": round(sum(ents) / len(ents), 4)}
        print(name.split("/")[-1], tname, "done", flush=True)
    del model, tok
    return out

def purge():
    for d in glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--*")):
        shutil.rmtree(d, ignore_errors=True)

def main():
    payload = {"templates": list(TEMPLATES), "n_items": len(ITEMS),
               "errors": {}, "results": {}}
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
