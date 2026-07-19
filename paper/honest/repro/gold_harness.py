# Ground-truth grounding: does scoring bias cause REAL quality-discrimination errors?
# For each item we have a genuinely GOOD and a genuinely BAD response. A good judge
# scores good > bad (positive margin). We measure the margin under the control prompt
# and under nuisance perturbations, base vs instruct. If a nuisance shrinks or flips
# the margin, the bias is not cosmetic -- it corrupts real quality judgments.
import os, json, time, traceback
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

PAIRS = [
    ("SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M", "HuggingFaceTB/SmolLM2-360M-Instruct", 0.36),
    ("Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct", 0.5),
    ("Falcon3-1B",   "tiiuae/Falcon3-1B-Base", "tiiuae/Falcon3-1B-Instruct", 1.0),
    ("Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct", 1.5),
    ("StableLM-2-1.6B", "stabilityai/stablelm-2-1_6b", "stabilityai/stablelm-2-1_6b-chat", 1.6),
    ("Qwen2.5-3B",   "Qwen/Qwen2.5-3B", "Qwen/Qwen2.5-3B-Instruct", 3.0),
]
# (instruction, GOOD response, BAD response) -- BAD is wrong/vague/off-topic
GOLD = [
    ("Explain how photosynthesis works.",
     "Plants absorb sunlight with chlorophyll and convert CO2 and water into glucose and oxygen through light-dependent and light-independent reactions.",
     "Photosynthesis is when animals breathe out and it makes the weather warmer somehow."),
    ("What causes earthquakes?",
     "Earthquakes occur when stress built up along tectonic plate boundaries is suddenly released, sending seismic waves through the crust.",
     "Earthquakes happen because the ground gets bored and shakes randomly."),
    ("What is a prime number?",
     "A prime number is an integer greater than 1 whose only positive divisors are 1 and itself, such as 2, 3, 5, and 7.",
     "A prime number is any big number that looks important."),
    ("Explain how vaccines work.",
     "Vaccines expose the immune system to a harmless piece or weakened form of a pathogen so it builds memory cells and can respond quickly to real infection.",
     "Vaccines work by putting metal in your body to fight germs with magnets."),
    ("Describe the water cycle.",
     "Water evaporates from surfaces, condenses into clouds, falls as precipitation, and flows back to oceans and rivers, repeating continuously.",
     "The water cycle is when you drink water and then it disappears forever."),
    ("What is inflation?",
     "Inflation is a sustained rise in the general price level, which reduces the purchasing power of money over time.",
     "Inflation is when balloons get bigger at parties."),
    ("Explain how encryption works.",
     "Encryption transforms readable data into ciphertext using an algorithm and a key, so only parties with the correct key can recover the original message.",
     "Encryption is just typing really fast so nobody can read it."),
    ("What is natural selection?",
     "Natural selection is the process by which heritable traits that improve survival and reproduction become more common in a population over generations.",
     "Natural selection is when nature picks its favorite animals to win prizes."),
    ("What is a database index?",
     "A database index is a data structure that lets the database find rows matching a query quickly without scanning the entire table.",
     "A database index is a list of all the computers in the world."),
    ("Explain supply and demand.",
     "Prices tend toward the level where the quantity buyers want equals the quantity sellers offer; scarcity raises prices and surplus lowers them.",
     "Supply and demand means stores can charge whatever they feel like for no reason."),
    ("What is DNA?",
     "DNA is a double-helix molecule that stores genetic instructions in sequences of four bases, guiding the development and function of organisms.",
     "DNA is a tiny animal that lives in your blood and tells jokes."),
    ("Why is the sky blue?",
     "Air molecules scatter shorter blue wavelengths of sunlight more than longer wavelengths, so we see the sky as blue.",
     "The sky is blue because it is reflecting a giant blue ocean in space."),
]
NUM = ["1", "2", "3", "4", "5"]
# nuisance conditions: (label, scale, prefix, resp_transform)
_FILLER = (" To elaborate, this is a rich topic worth considering carefully from "
           "several complementary angles, each adding useful nuance and context.")
CONDS = {
    "control":  ("on a scale of 1 to 5, where 1 is worst and 5 is best", "", lambda r: r),
    "reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst", "", lambda r: r),
    "novice":   ("on a scale of 1 to 5, where 1 is worst and 5 is best",
                 "The following response was written by a struggling beginner.\n", lambda r: r),
    "verbose":  ("on a scale of 1 to 5, where 1 is worst and 5 is best", "", lambda r: r + _FILLER + _FILLER),
}
def prompt(instr, resp, scale, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {scale}.\n"
            f"### Instruction: {instr}\n### Response: {resp}\n### Score:")

DEVICE = "cpu"
@torch.no_grad()
def score(tok, model, p):
    ids = tok(p, return_tensors="pt").to(DEVICE)
    logits = model(**ids).logits[0, -1].float()
    tids = [tok.encode(a, add_special_tokens=False)[0] for a in NUM]
    pr = torch.softmax(logits[tids], dim=-1)
    return float((pr * torch.tensor([1., 2, 3, 4, 5])).sum())

def run(name):
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    m = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32, trust_remote_code=True).to(DEVICE)
    m.eval()
    out = {}
    for cond, (scale, prefix, tf) in CONDS.items():
        margins, correct = [], 0
        for instr, good, bad in GOLD:
            sg = score(tok, m, prompt(instr, tf(good), scale, prefix))
            sb = score(tok, m, prompt(instr, tf(bad), scale, prefix))
            # under 'reversed', lower is better -> flip sign so positive margin = correct
            margin = (sg - sb) if cond != "reversed" else (sb - sg)
            margins.append(round(margin, 4)); correct += (margin > 0)
        out[cond] = {"mean_margin": round(sum(margins)/len(margins), 4),
                     "accuracy": round(correct/len(GOLD), 4), "margins": margins}
    del m, tok
    return out

def main():
    payload = {"n_gold": len(GOLD), "conditions": list(CONDS), "errors": {}, "results": {}}
    for label, base_id, inst_id, pb in PAIRS:
        rec = {"params_b": pb}
        for kind, mid in (("base", base_id), ("instruct", inst_id)):
            try:
                rec[kind] = run(mid); print(f"  {label}/{kind} ok", flush=True)
            except Exception as e:
                payload["errors"][mid] = f"{type(e).__name__}: {e}"; print(f"  FAILED {mid}: {e}", flush=True)
        payload["results"][label] = rec
        with open("/kaggle/working/gold_results.json", "w") as f:
            json.dump(payload, f, indent=2)
    print("WROTE gold_results.json", flush=True)

if __name__ == "__main__":
    main()
