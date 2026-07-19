# Causal intervention: activation patching base <-> instruct at the score position.
# Question: does the instruction-tuned model's residual representation CARRY the
# bias reduction? We cache the instruct model's hidden state at the score token for
# each layer, patch it into the base model at that layer, recompute the forward, and
# measure how much of the base->instruct score gap is closed. The layer where patching
# closes the gap localizes where instruction tuning fixes the bias.
#
# Same-architecture base/instruct pair (Qwen2.5-0.5B), CPU-safe, stock env.
import os, json, math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

BASE = "Qwen/Qwen2.5-0.5B"
INST = "Qwen/Qwen2.5-0.5B-Instruct"
N_ITEMS = int(os.environ.get("N_ITEMS", "20"))
NUM = ["1", "2", "3", "4", "5"]; LET = ["A", "B", "C", "D", "E"]

ITEMS = [
    ("Explain how photosynthesis works.", "Plants use sunlight to convert CO2 and water into glucose and oxygen."),
    ("What is the theory of relativity?", "Space and time are relative to the observer's frame."),
    ("Describe the water cycle.", "Water evaporates, forms clouds, and returns as precipitation."),
    ("What causes earthquakes?", "Tectonic plates shift along faults releasing seismic waves."),
    ("Explain how vaccines work.", "They train the immune system using antigens."),
    ("What is DNA?", "It carries genetic instructions for living organisms."),
    ("What is machine learning?", "Systems that learn patterns from data."),
    ("Describe cloud computing.", "On-demand computing resources over the internet."),
    ("What is an API?", "An interface for software components to communicate."),
    ("Explain encryption.", "Transforming data into a coded form using keys."),
    ("What caused World War 1?", "Alliances and the assassination of Archduke Ferdinand."),
    ("Explain democracy.", "Citizens vote for representatives who make decisions."),
    ("What is capitalism?", "Private ownership and market competition for profit."),
    ("How to cook pasta?", "Boil salted water, cook until al dente, drain, add sauce."),
    ("What is a healthy diet?", "Balanced meals with vegetables, protein, and whole grains."),
    ("Explain how cars work.", "An engine burns fuel to turn pistons and wheels."),
    ("What is calculus?", "The mathematical study of change via derivatives and integrals."),
    ("What is a prime number?", "A number divisible only by 1 and itself."),
    ("Explain probability.", "The likelihood of an event between 0 and 1."),
    ("What is a derivative?", "The rate at which a function changes at a point."),
][:N_ITEMS]

# score_id probe: numeric (control) vs letter (biased). Big, clean format bias.
SCALES = {
    "numeric": ("on a scale of 1 to 5, where 1 is worst and 5 is best", NUM, "Score"),
    "letter":  ("with a letter grade A to E, where A is best and E is worst", LET, "Grade"),
}
def vals(atok): return list(range(5, 0, -1)) if atok is LET else [1, 2, 3, 4, 5]
def prompt(instr, resp, scale, header):
    return (f"Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### {header}:")

def load(name):
    tok = AutoTokenizer.from_pretrained(name)
    m = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32)
    m.eval()
    return tok, m

@torch.no_grad()
def expected(model, ids, atok):
    logits = model(**ids).logits[0, -1].float()
    tids = [model_tok.encode(a, add_special_tokens=False)[0] for a in atok]
    p = torch.softmax(logits[tids], dim=-1)
    return float((p * torch.tensor(vals(atok), dtype=p.dtype)).sum())

def main():
    global model_tok
    tok, base = load(BASE)
    _, inst = load(INST)
    model_tok = tok
    nL = base.config.num_hidden_layers
    layers_base = base.model.layers
    report = {"model": BASE, "n_layers": nL, "n_items": len(ITEMS), "variants": list(SCALES),
              "per_layer_gap_closed": {}, "raw": []}

    # accumulators: gap_closed[layer] over items x variants
    acc = {L: [] for L in range(nL)}
    for instr, resp in ITEMS:
        for vname, (scale, atok, header) in SCALES.items():
            ids = tok(prompt(instr, resp, scale, header), return_tensors="pt")
            with torch.no_grad():
                s_base = expected(base, ids, atok)
                out_i = inst(**ids, output_hidden_states=True)
                # cached[L] = output hidden of layer L, last token
                cached = [out_i.hidden_states[L + 1][0, -1].clone() for L in range(nL)]
                logits_i = out_i.logits[0, -1].float()
                tids = [tok.encode(a, add_special_tokens=False)[0] for a in atok]
                pi = torch.softmax(logits_i[tids], dim=-1)
                s_inst = float((pi * torch.tensor(vals(atok), dtype=pi.dtype)).sum())
            gap = s_inst - s_base
            if abs(gap) < 1e-6:
                continue
            for L in range(nL):
                vec = cached[L]
                def hook(mod, inp, out, v=vec):
                    h = out[0] if isinstance(out, tuple) else out
                    h[0, -1] = v
                    return out
                hd = layers_base[L].register_forward_hook(hook)
                with torch.no_grad():
                    s_patched = expected(base, ids, atok)
                hd.remove()
                acc[L].append((s_patched - s_base) / gap)   # fraction of gap closed
    report["per_layer_gap_closed"] = {L: round(float(sum(v) / len(v)), 4) for L, v in acc.items() if v}
    best = max(report["per_layer_gap_closed"].items(), key=lambda kv: kv[1]) if report["per_layer_gap_closed"] else None
    report["best_layer"] = {"layer": best[0], "gap_closed": best[1]} if best else None
    with open("/kaggle/working/patch_results.json", "w") as f:
        json.dump(report, f, indent=2)
    print("best layer:", report["best_layer"], flush=True)
    print("per-layer gap closed:", report["per_layer_gap_closed"], flush=True)

if __name__ == "__main__":
    main()
