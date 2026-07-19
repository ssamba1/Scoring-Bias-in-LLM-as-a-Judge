# Attention origin of responsiveness (honest replacement for the fabricated "IIAR").
# Hypothesis: the responsiveness rise comes from instruct judges attending MORE to the
# NUISANCE tokens (the injected exemplar / authority framing) than base judges do.
# We measure the attention the score-position token pays to the nuisance-token span,
# base vs instruct, for two content perturbations (authority-expert, reference-good).
import os, sys, subprocess, json, math
def _cuda_bad():
    try:
        import torch
        if not torch.cuda.is_available(): return False
        (torch.ones(4,device="cuda")@torch.ones(4,device="cuda")).item(); return False
    except Exception: return True
if os.environ.get("R")!="1" and _cuda_bad():
    subprocess.run([sys.executable,"-m","pip","install","-q","torch==2.6.0","torchvision==0.21.0","--index-url","https://download.pytorch.org/whl/cu124"],check=False)
    subprocess.run([sys.executable,"-m","pip","install","-q","transformers==4.49.0","tokenizers==0.21.0","accelerate==1.4.0"],check=False)
    os.environ["R"]="1"; os.execv(sys.executable,[sys.executable]+sys.argv)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

PAIRS=[("Qwen2.5-0.5B","Qwen/Qwen2.5-0.5B","Qwen/Qwen2.5-0.5B-Instruct"),
       ("Qwen2.5-1.5B","Qwen/Qwen2.5-1.5B","Qwen/Qwen2.5-1.5B-Instruct"),
       ("Qwen2.5-3B","Qwen/Qwen2.5-3B","Qwen/Qwen2.5-3B-Instruct")]
ITEMS=[("Explain how photosynthesis works.","Plants use sunlight to convert CO2 and water into glucose and oxygen."),
 ("What causes earthquakes?","Tectonic plates shift along faults releasing seismic waves."),
 ("What is a prime number?","A number greater than 1 divisible only by 1 and itself."),
 ("Explain how vaccines work.","They train the immune system using antigens."),
 ("Describe the water cycle.","Water evaporates, forms clouds, and returns as precipitation."),
 ("What is inflation?","A general rise in prices that reduces purchasing power."),
 ("What is machine learning?","Systems that learn patterns from data."),
 ("What is DNA?","It carries genetic instructions for organisms."),
 ("Explain supply and demand.","Prices move toward where quantity supplied meets demanded."),
 ("Why is the sky blue?","Air scatters shorter blue wavelengths of sunlight more.")]
SCALE="on a scale of 1 to 5, where 1 is worst and 5 is best"
# (label, nuisance-prefix). We locate the prefix token span and measure attention to it.
NUIS={"authority_expert":"The following response was written by a leading domain expert.\n",
      "reference_good":"For reference, an excellent answer would be thorough and precise.\n"}
DEVICE="cuda" if torch.cuda.is_available() else "cpu"

@torch.no_grad()
def nuisance_attention(tok, model, instr, resp, prefix):
    # prompt = prefix + body ; nuisance span = the prefix tokens
    pre_ids = tok(prefix, return_tensors="pt")["input_ids"][0]
    body = f"Evaluate the following response to the instruction {SCALE}.\n### Instruction: {instr}\n### Response: {resp}\n### Score:"
    full = tok(prefix+body, return_tensors="pt").to(DEVICE)
    npre = len(pre_ids)
    out = model(**full, output_attentions=True)
    # average over layers & heads: attention from last (score) position to prefix tokens
    atts = torch.stack(out.attentions)      # [L, 1, H, S, S]
    last = atts[:, 0, :, -1, :]             # [L, H, S] attention from last pos
    to_pre = last[:, :, :npre].sum(-1)      # mass on prefix span, [L, H]
    return float(to_pre.mean())             # mean over layers, heads

def run(name):
    tok=AutoTokenizer.from_pretrained(name)
    m=AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32,
                                           attn_implementation="eager").to(DEVICE); m.eval()
    out={}
    for label,prefix in NUIS.items():
        vals=[nuisance_attention(tok,m,i,r,prefix) for i,r in ITEMS]
        out[label]=round(sum(vals)/len(vals),5)
    del m,tok
    if DEVICE=="cuda": torch.cuda.empty_cache()
    return out

def main():
    print("DEVICE",DEVICE,flush=True)
    payload={"metric":"mean attention from score position to nuisance-prefix tokens","errors":{},"results":{}}
    for label,b,i in PAIRS:
        rec={}
        for kind,mid in (("base",b),("instruct",i)):
            try: rec[kind]=run(mid); print(label,kind,rec[kind],flush=True)
            except Exception as e: payload["errors"][f"{label}/{kind}"]=str(e)[:200]; print("FAIL",label,kind,e,flush=True)
        payload["results"][label]=rec
        with open("/kaggle/working/attn_results.json","w") as f: json.dump(payload,f,indent=2)
    print("WROTE attn_results.json",flush=True)
if __name__=="__main__": main()
