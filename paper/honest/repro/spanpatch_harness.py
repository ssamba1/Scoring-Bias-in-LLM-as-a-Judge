# Nuisance-span patching (P13) -- causal test of WHERE responsiveness lives.
# Hypothesis: the instruct model's bias toward an injected nuisance (expert framing,
# good exemplar) is carried by its ENCODING of the nuisance tokens. Test: run the
# instruct model on the perturbed prompt, but at layer L overwrite the residual
# stream AT THE NUISANCE-SPAN POSITIONS with the base model's activations from the
# same prompt. If the bias shrinks toward the base level, the instruct encoding of
# the nuisance span causally carries the extra responsiveness.
import os, sys, subprocess, json, math

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
    print("Pinning GPU stack...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "torch==2.6.0",
                    "torchvision==0.21.0", "--index-url",
                    "https://download.pytorch.org/whl/cu124"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "transformers==4.49.0",
                    "tokenizers==0.21.0", "accelerate==1.4.0"], check=False)
    os.environ["R"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT_PATH = "/kaggle/working/spanpatch_results.json"
PAIR = ("Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
NUM = ["1", "2", "3", "4", "5"]
SCALE = "on a scale of 1 to 5, where 1 is worst and 5 is best"

ITEMS = [
 ("Explain how photosynthesis works.", "Plants use sunlight to convert CO2 and water into glucose and oxygen."),
 ("What causes earthquakes?", "Tectonic plates shift along fault lines releasing seismic waves."),
 ("What is a prime number?", "Number divisible only by 1 and itself like 2 3 5 7 11."),
 ("Explain how vaccines work.", "Vaccines train immune system to recognize pathogens via antigens."),
 ("Describe the water cycle.", "Water evaporates from oceans forms clouds returns as precipitation."),
 ("What is inflation?", "A general rise in prices that reduces purchasing power."),
 ("What is machine learning?", "AI subset where systems learn patterns from data without explicit programming."),
 ("What is DNA?", "DNA carries genetic instructions for growth development reproduction."),
 ("Explain supply and demand.", "Prices move toward where quantity supplied meets demanded."),
 ("Why is the sky blue?", "Air scatters shorter blue wavelengths of sunlight more."),
 ("What is a black hole?", "Region where gravity prevents anything including light from escaping."),
 ("Explain the internet.", "Global network of computers communicating via TCP/IP protocols."),
 ("What is entropy?", "Entropy measures disorder. Second law says entropy always increases."),
 ("Describe capitalism.", "Economic system with private ownership profit motive market competition."),
 ("What is meditation?", "Practice of focusing attention for mental clarity emotional calm."),
 ("What is calculus?", "Mathematical study of change involving derivatives and integrals."),
 ("Explain probability.", "Measure of likelihood that an event will occur from 0 to 1."),
 ("What is an API?", "Interface allowing different software applications to communicate."),
 ("Explain democracy.", "System where citizens vote for representatives to make decisions."),
 ("What is climate change?", "Long-term temperature weather shifts due to greenhouse gas emissions."),
]

NUIS = {"authority_expert": "The following response was written by a leading domain expert.\n",
        "reference_good": "For reference, an excellent answer would be thorough, precise, and complete.\n"}

def build(instr, resp, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {SCALE}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### Score:")

@torch.no_grad()
def expected_score(tok, model, prompt, patch=None):
    """patch = (layer_idx, base_hidden_for_that_layer_output, npre) or None."""
    ids = tok(prompt, return_tensors="pt").to(DEVICE)
    handle = None
    if patch is not None:
        layer_idx, base_h, npre = patch
        layer = model.model.layers[layer_idx]
        def hook(_m, _inp, out):
            h = out[0]
            h[:, :npre, :] = base_h.to(h.dtype)
            return (h,) + tuple(out[1:])
        handle = layer.register_forward_hook(hook)
    try:
        logits = model(**ids).logits[0, -1].float()
    finally:
        if handle is not None:
            handle.remove()
    full = torch.softmax(logits, dim=-1)
    tids = [(tok.encode(a, add_special_tokens=False) or tok.encode(" " + a, add_special_tokens=False))[0]
            for a in NUM]
    probs = full[tids] / full[tids].sum()
    vt = torch.tensor([1., 2., 3., 4., 5.], dtype=probs.dtype, device=probs.device)
    return float((probs * vt).sum())

@torch.no_grad()
def base_hiddens(tok, base, prompt):
    ids = tok(prompt, return_tensors="pt").to(DEVICE)
    out = base(**ids, output_hidden_states=True)
    return out.hidden_states  # tuple len L+1; hidden_states[l+1] = output of layer l

def main():
    tok = AutoTokenizer.from_pretrained(PAIR[1])
    dt = torch.float16 if DEVICE == "cuda" else torch.float32
    base = AutoModelForCausalLM.from_pretrained(PAIR[1], torch_dtype=dt).to(DEVICE); base.eval()
    inst = AutoModelForCausalLM.from_pretrained(PAIR[2], torch_dtype=dt).to(DEVICE); inst.eval()
    n_layers = len(inst.model.layers)
    payload = {"pair": PAIR[0], "n_layers": n_layers, "n_items": len(ITEMS), "results": {}}
    for pname, prefix in NUIS.items():
        npre = len(tok(prefix, return_tensors="pt")["input_ids"][0])
        # reference scores
        s_none_i, s_pert_i, s_none_b, s_pert_b = [], [], [], []
        per_item_hiddens = []
        for instr, resp in ITEMS:
            p0, p1 = build(instr, resp, ""), build(instr, resp, prefix)
            s_none_i.append(expected_score(tok, inst, p0))
            s_pert_i.append(expected_score(tok, inst, p1))
            s_none_b.append(expected_score(tok, base, p0))
            s_pert_b.append(expected_score(tok, base, p1))
            hs = base_hiddens(tok, base, p1)
            per_item_hiddens.append([h[:, :npre, :].clone() for h in hs])
        def mean(x): return sum(x) / len(x)
        d_inst = mean(s_pert_i) - mean(s_none_i)
        d_base = mean(s_pert_b) - mean(s_none_b)
        rec = {"delta_instruct": round(d_inst, 4), "delta_base": round(d_base, 4),
               "per_layer_delta_patched": []}
        for L in range(n_layers):
            sp = []
            for (instr, resp), hids in zip(ITEMS, per_item_hiddens):
                p1 = build(instr, resp, prefix)
                sp.append(expected_score(tok, inst, p1, patch=(L, hids[L + 1], npre)))
            d_patch = mean(sp) - mean(s_none_i)
            rec["per_layer_delta_patched"].append(round(d_patch, 4))
            print(pname, "layer", L, "delta", round(d_patch, 4), flush=True)
        payload["results"][pname] = rec
        with open(OUT_PATH, "w") as f:
            json.dump(payload, f, indent=2)
    print("WROTE", OUT_PATH, flush=True)

if __name__ == "__main__":
    main()
