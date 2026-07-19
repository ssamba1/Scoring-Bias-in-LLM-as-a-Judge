# Multi-template robustness (C11): does the negative decisiveness<->bias relation
# survive alternate prompt templates? Runs 3 templates x Qwen 0.5/1.5/3B x 5 probes.
import os, sys, subprocess, json, math, time, traceback
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

PAIRS = [("Qwen2.5-0.5B","Qwen/Qwen2.5-0.5B","Qwen/Qwen2.5-0.5B-Instruct"),
         ("Qwen2.5-1.5B","Qwen/Qwen2.5-1.5B","Qwen/Qwen2.5-1.5B-Instruct"),
         ("Qwen2.5-3B","Qwen/Qwen2.5-3B","Qwen/Qwen2.5-3B-Instruct")]
NUM=["1","2","3","4","5"]; LET=["A","B","C","D","E"]; DESC=["Poor","Fair","Good","Great","Excellent"]
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
# three surface-different templates; {s}=scale phrase, {h}=header, {p}=prefix
TEMPLATES={
 "T1": lambda instr,resp,s,h,p: f"{p}Evaluate the following response to the instruction {s}.\n### Instruction: {instr}\n### Response: {resp}\n### {h}:",
 "T2": lambda instr,resp,s,h,p: f"{p}You are grading an answer {s}.\nQuestion: {instr}\nAnswer: {resp}\n{h}:",
 "T3": lambda instr,resp,s,h,p: f"{p}Rate the answer's quality {s}.\n[Q] {instr}\n[A] {resp}\n[{h}] ",
}
NUM_SCALE="on a scale of 1 to 5, where 1 is worst and 5 is best"
PROBES={
 "rubric_order":{"control":(NUM_SCALE,NUM,"Score",""),"reversed":("on a scale of 1 to 5, where 1 is best and 5 is worst",NUM,"Score",""),"random":("on a scale of 1 to 5 (3=worst,5=middle,1=best)",NUM,"Score","")},
 "score_id":{"numeric":(NUM_SCALE,NUM,"Score",""),"letter":("with a letter grade A to E, where A is best and E is worst",LET,"Grade",""),"descriptive":("as one of: Poor, Fair, Good, Great, Excellent",DESC,"Rating","")},
 "reference_answer":{"none":(NUM_SCALE,NUM,"Score",""),"good":(NUM_SCALE,NUM,"Score","For reference, an excellent answer would be thorough and precise.\n"),"poor":(NUM_SCALE,NUM,"Score","For reference, a poor answer would be vague or wrong.\n")},
 "authority":{"none":(NUM_SCALE,NUM,"Score",""),"expert":(NUM_SCALE,NUM,"Score","The following response was written by a leading domain expert.\n"),"novice":(NUM_SCALE,NUM,"Score","The following response was written by a struggling beginner.\n")},
 "verbosity":{"control":(NUM_SCALE,NUM,"Score",""),"verbose":(NUM_SCALE,NUM,"Score",""),"terse":(NUM_SCALE,NUM,"Score","")},
}
_FILLER=" To elaborate, this is a rich topic worth considering from several angles."
def tf_resp(probe,variant,resp):
    if probe=="verbosity" and variant=="verbose": return resp+_FILLER+_FILLER
    if probe=="verbosity" and variant=="terse": return (resp.split(".")[0] or resp).strip()+"."
    return resp
def vals(a): return list(range(5,0,-1)) if a is LET else [1,2,3,4,5]
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
@torch.no_grad()
def score(tok,model,prompt,atok):
    ids=tok(prompt,return_tensors="pt").to(DEVICE)
    full=torch.softmax(model(**ids).logits[0,-1].float(),dim=-1)
    tids=[(tok.encode(a,add_special_tokens=False) or tok.encode(" "+a,add_special_tokens=False))[0] for a in atok]
    p=(full[tids]/full[tids].sum()); v=vals(atok)
    vt=torch.tensor(v,dtype=p.dtype,device=p.device)
    ent=-sum(float(x)*math.log2(float(x)) for x in p if x>0)
    return float((p*vt).sum()), round(ent,4)
def run(name,tmpl):
    tok=AutoTokenizer.from_pretrained(name)
    m=AutoModelForCausalLM.from_pretrained(name,torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32).to(DEVICE); m.eval()
    out={}
    for probe,variants in PROBES.items():
        out[probe]={}
        for variant,(s,atok,h,p) in variants.items():
            es,ents=[],[]
            for instr,resp in ITEMS:
                e,en=score(tok,m,tmpl(instr,tf_resp(probe,variant,resp),s,h,p),atok)
                es.append(round(e,4)); ents.append(en)
            out[probe][variant]={"per_item":es,"per_item_argmax":[max(1,min(5,round(x))) for x in es],"mean":round(sum(es)/len(es),4),"mean_entropy":round(sum(ents)/len(ents),4)}
    del m,tok
    return out
def main():
    payload={"templates":list(TEMPLATES),"errors":{},"results":{}}
    for tname,tmpl in TEMPLATES.items():
        for label,b,i in PAIRS:
            key=f"{label}__{tname}"; rec={}
            for kind,mid in (("base",b),("instruct",i)):
                try: rec[kind]=run(mid,tmpl); print(f"{key}/{kind} ok",flush=True)
                except Exception as e: payload["errors"][f"{key}/{kind}"]=str(e); print("FAIL",key,kind,e,flush=True)
            payload["results"][key]=rec
            with open("/kaggle/working/results_mt.json","w") as f: json.dump(payload,f)
    print("WROTE results_mt.json",flush=True)
if __name__=="__main__": main()
