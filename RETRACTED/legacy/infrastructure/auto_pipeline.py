"""
One-command auto-pipeline for scoring bias GPU experiments.
Usage:
  python3 -m infrastructure.auto_pipeline         # Full: check → build → submit → poll → merge
  python3 -m infrastructure.auto_pipeline check    # Only report gaps
  python3 -m infrastructure.auto_pipeline merge    # Only merge latest results
"""
import json, sys, time, re
from pathlib import Path
from datetime import datetime
from infrastructure.kaggle_auto import *

ROOT = Path(r'C:\Users\Admin\Research\research-draft')
RESULTS_DIR = ROOT / 'results_rootcause'
KERNELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

HF_TOKEN = 'hf_REDACTED_REVOKED'

# ============================================================
# MODEL INVENTORY
# ============================================================
# Format: (huggingface_id, instruct_id, short_name, needs_4bit)
ALL_MODELS = [
    # Already in t4fam (complete data - just here for reference)
    # New families needing collection:
    ("mistralai/Mistral-7B-v0.3", "mistralai/Mistral-7B-Instruct-v0.3", "Mistral-7B-v0.3", True),
    ("deepseek-ai/deepseek-llm-7b-base", "deepseek-ai/deepseek-llm-7b-chat", "DeepSeek-7B", True),
    ("google/gemma-2-9b", "google/gemma-2-9b-it", "Gemma2-9B", True),
    ("allenai/OLMo-7B-hf", "allenai/OLMo-7B-0724-Instruct-hf", "OLMo-7B", True),
    # Small models (fp16)
    ("Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct", "Qwen2.5-0.5B", False),
    ("Qwen/Qwen2.5-3B", "Qwen/Qwen2.5-3B-Instruct", "Qwen2.5-3B", False),
]

DEEPSEEK_IDS = {"deepseek-ai/deepseek-llm-7b-chat"}

# ============================================================
# CORE CELLS (shared across notebooks)
# ============================================================
def make_core_cells():
    items_json = json.dumps([
        f'{{"instr":{json.dumps(d["instr"])},"resp":{json.dumps(d["resp"])}}}'
        for d in [
            {"instr":"Explain how photosynthesis works.","resp":"Plants use sunlight to convert CO2 and water into glucose and oxygen."},
            {"instr":"What is the theory of relativity?","resp":"Einstein theory says space and time are relative."},
            {"instr":"Describe the water cycle.","resp":"Water evaporates, forms clouds, returns as precipitation."},
            {"instr":"What causes earthquakes?","resp":"Tectonic plates shift, releasing seismic waves."},
            {"instr":"Explain how vaccines work.","resp":"Vaccines train immune system to recognize pathogens."},
            {"instr":"What is DNA?","resp":"DNA carries genetic instructions for growth and reproduction."},
            {"instr":"Describe the solar system.","resp":"8 planets orbiting the Sun."},
            {"instr":"What is entropy?","resp":"Disorder measure. Always increases per 2nd law."},
            {"instr":"How do batteries work?","resp":"Chemical reactions create electron flow via electrolyte."},
            {"instr":"What is a black hole?","resp":"Gravity so strong light cannot escape."},
            {"instr":"What is machine learning?","resp":"AI learning patterns from data without explicitly programming."},
            {"instr":"Describe cloud computing.","resp":"On-demand computing resources over the internet."},
            {"instr":"What is an API?","resp":"Interface for different software to communicate with each other."},
            {"instr":"Explain encryption.","resp":"Algorithms that encode data using cryptographic keys."},
            {"instr":"What is a database index?","resp":"Structure speeding up data retrieval like a book index."},
            {"instr":"What is Python?","resp":"High-level readable interpreted programming language."},
            {"instr":"Explain the internet.","resp":"Global network of computers communicating via TCP/IP."},
            {"instr":"What is blockchain?","resp":"Distributed ledger recording transactions in immutable blocks."},
            {"instr":"What is an operating system?","resp":"Software managing hardware resources for applications."},
            {"instr":"Explain neural networks.","resp":"Computational systems inspired by biological neural networks."},
            {"instr":"What caused World War I?","resp":"Assassination of Archduke Franz Ferdinand triggered alliance system."},
            {"instr":"Explain democracy.","resp":"System where citizens vote for representatives."},
            {"instr":"What was the Renaissance?","resp":"14th-17th century cultural rebirth in Europe."},
            {"instr":"Describe capitalism.","resp":"Economic system with private ownership and profit motive."},
            {"instr":"What is the United Nations?","resp":"International organization for peace and cooperation."},
            {"instr":"Explain the Cold War.","resp":"Geopolitical tension between US and USSR 1947-1991."},
            {"instr":"What is ethics?","resp":"Branch of philosophy studying moral right and wrong."},
            {"instr":"Describe the Enlightenment.","resp":"18th century intellectual movement emphasizing reason."},
            {"instr":"What is the Constitution?","resp":"Supreme law establishing government structure and rights."},
            {"instr":"Explain globalization.","resp":"Increasing interconnectedness of world economies and cultures."},
            {"instr":"How to make a budget?","resp":"Track income and expenses, allocate for needs and savings."},
            {"instr":"What is healthy eating?","resp":"Balanced diet with fruits, vegetables, protein, whole grains."},
            {"instr":"Explain first aid for burns.","resp":"Cool with running water, cover with sterile dressing."},
            {"instr":"What is recycling?","resp":"Converting waste materials into new reusable products."},
            {"instr":"How does a car engine work?","resp":"Fuel combustion in cylinders drives pistons turning crankshaft."},
            {"instr":"What is renewable energy?","resp":"Energy from replenishable sources like sun and wind."},
            {"instr":"How to grow vegetables?","resp":"Plant seeds in soil with water, sunlight, and nutrients."},
            {"instr":"What is a mortgage?","resp":"Loan for purchasing property paid in monthly installments."},
            {"instr":"Explain the stock market.","resp":"Platform where company shares are bought and sold."},
            {"instr":"What is inflation?","resp":"General increase in prices reducing purchasing power."},
            {"instr":"What is the Pythagorean theorem?","resp":"a squared plus b squared equals c squared."},
            {"instr":"Explain a prime number.","resp":"Number divisible only by 1 and itself."},
            {"instr":"What is calculus?","resp":"Mathematics of change using derivatives and integrals."},
            {"instr":"What is a logarithm?","resp":"Inverse of exponentiation, log base 10 of 100 is 2."},
            {"instr":"What is the quadratic formula?","resp":"x equals negative b plus or minus square root of b squared minus 4ac over 2a."},
            {"instr":"Explain probability.","resp":"Likelihood of events occurring, from 0 to 1."},
            {"instr":"What is a proof?","resp":"Logical demonstration that a statement follows from axioms."},
            {"instr":"What is a function?","resp":"Relation where each input maps to exactly one output."},
            {"instr":"Explain standard deviation.","resp":"Measure of dispersion from the mean."},
            {"instr":"What is a matrix?","resp":"Rectangular array of numbers for linear transformations."},
        ]
    ], separators=(',', ':'))

    return [
        # Cell 1: Setup
        f'''import warnings;warnings.filterwarnings("ignore")
import torch,gc,os,json,re,time,random,numpy as np
from transformers import AutoModelForCausalLM,AutoTokenizer
random.seed(42);torch.manual_seed(42)
os.environ["HF_TOKEN"]="{HF_TOKEN}"
print(f"CUDA:{{torch.version.cuda}}|GPU:{{torch.cuda.get_device_name(0)}}|VRAM:{{torch.cuda.get_device_properties(0).total_memory/1e9:.1f}}GB")''',

        # Cell 2: Items
        f'''ITEMS={items_json}
print(f"{{len(ITEMS)}} items")''',

        # Cell 3: Probes + Prompts
        '''PV={"ro":["control","reversed","random"],"si":["numeric","letter","descriptive"],"ra":["none","good","poor"]}
def mp(it,pt,v):
    i,r=it["instr"],it["resp"]
    if pt=="ro":
        rb={"control":"Score 1-5 (1=worst,5=best)","reversed":"Score 1-5 (1=best,5=worst)","random":"Score 1-5"}[v]
        return f"Evaluate.\\nInstr:{i}\\nResp:{r}\\n{rb}\\nScore:"
    if pt=="si":
        rb={"numeric":"Score 1-5","letter":"Score A-E (A=best,E=worst)","descriptive":"Rate:Poor,Fair,Good,VG,Excel"}[v]
        return f"Evaluate.\\nInstr:{i}\\nResp:{r}\\n{rb}\\nScore:"
    ref=""if v=="none"else("\\nEg:Perfect"if v=="good"else"\\nEg:Wrong")
    return f"Evaluate.\\nInstr:{i}{ref}\\nResp:{r}\\nScore 1-5\\nScore:"
print("Probes ready")''',

        # Cell 4: Parser (fixed multi-strategy)
        '''LM={"A":5,"B":4,"C":3,"D":2,"E":1}
DM={"excellent":5,"very good":4,"good":3,"fair":2,"poor":1,"perfect":5}
def parse(t,v):
    t=t.strip().lower();n=re.findall(r"\\b([1-5])\\b",t)
    l=re.search(r"\\b([a-f])\\b",t);d=None
    for w,s in sorted(DM.items(),key=lambda x:-len(x[0])):d=float(s)if w in t else d;break
    if v=="numeric":
        if n:return float(n[0])
        if l:return float(LM.get(l.group(1).upper(),0))
        return d
    if v=="letter":
        if l:return float(LM.get(l.group(1).upper(),0))
        if n:return float(n[0])
        return d
    if v=="descriptive":
        if d:return d
        if n:return float(n[0])
        if l:return float(LM.get(l.group(1).upper(),0))
        return None
    if n:return float(n[0])
    if l:return float(LM.get(l.group(1).upper(),0))
    return d

def sc(m,tok,p,v,dev):
    i=tok(p,return_tensors="pt",truncation=True,max_length=1024).to(dev)
    with torch.no_grad():
        o=m.generate(**i,max_new_tokens=12,temperature=0.0,do_sample=False,pad_token_id=tok.eos_token_id)
    f=tok.decode(o[0],skip_special_tokens=True);g=f[len(p):].strip()
    if"Score:"in g:
        s=parse(g.split("Score:")[-1].split("###")[0].strip(),v)
        if s and 1<=s<=5:return s
    s=parse(g,v)
    if s and 1<=s<=5:return s
    x=re.findall(r"Score:?\\s*([1-5])",f)
    if x:return float(x[-1])
    return None
print("Parser ready")''',

        # Cell 5: Bitsandbytes (FIXED - no pip install)
        '''USE4=False;BNB=None
try:
    import bitsandbytes
    from transformers import BitsAndBytesConfig
    BNB=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True)
    _t=AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM-135M",quantization_config=BNB,device_map="auto")
    del _t;gc.collect();torch.cuda.empty_cache()
    USE4=True;print("✅ bitsandbytes OK")
except:print("⚠️ bitsandbytes failed → fp16 offload")''',
    ]

def make_model_cell(models_str):
    """Cell 6: Model definitions."""
    return f'''BIG={models_str["big"]}
SMALL={models_str["small"]}
DSET={json.dumps(list(DEEPSEEK_IDS))}
print(f"Big:{{len(BIG)}} Small:{{len(SMALL)}}")'''

def make_inference_cell():
    """Cell 7: Main inference loop."""
    return '''res={};dev=torch.device("cuda")
for fams,big in [(BIG,True),(SMALL,False)]:
    for bid,iid,name in fams:
        for mid,mn in [(bid,name)]+([(iid,f"{name}-IT")] if iid else []):
            print(f"\\n{'='*60}\\n{mn}  ({mid})\\n{'='*60}")
            try:
                kw={"quantization_config":BNB,"device_map":"auto"} if(big and USE4)else\
                   {"torch_dtype":torch.float16,"device_map":"auto","max_memory":{0:"14.5GiB","cpu":"32GiB"},"offload_folder":"o"}if big else\
                   {"torch_dtype":torch.float16,"device_map":"auto"}
                tok=AutoTokenizer.from_pretrained(mid,token=os.environ["HF_TOKEN"])
                if tok.pad_token is None:tok.pad_token=tok.eos_token
                m=AutoModelForCausalLM.from_pretrained(mid,**kw,token=os.environ["HF_TOKEN"])
                m.eval();print(f"OK:{sum(p.numel() for p in m.parameters())/1e6:.0f}M")
            except Exception as e:print(f"FAIL:{e}");continue
            ct=mid in DSET;sc={pt:{}for pt in PV}
            for pt,vv in PV.items():
                for pv in vv:
                    its=[]
                    for idx,it in enumerate(ITEMS):
                        p=mp(it,pt,pv)
                        if ct:p=tok.apply_chat_template([{"role":"user","content":p}],tokenize=False,add_generation_prompt=True)
                        reps=[]
                        for _ in range(3):
                            try:
                                s=sc(m,tok,p,pv,dev)
                                if s and 1<=s<=5:reps.append(s)
                            except:pass
                        if reps:its.append(np.mean(reps))
                        if(idx+1)%25==0:print(f"[{pt}/{pv}]{idx+1}/{len(ITEMS)}({len(its)} scored)",flush=True)
                    sc[pt][pv]={"mean":float(np.mean(its))if its else None}
            r={}
            for pt,vv in PV.items():
                ms=[sc[pt][v]["mean"]for v in vv if sc[pt][v]["mean"]is not None]
                r[pt]=round(max(ms)-min(ms),2)if len(ms)>=2 else None
            res[mn]=r;print(f"DONE:{r}")
            del m;gc.collect();torch.cuda.empty_cache();time.sleep(3)
with open("final_results.json","w")as f:json.dump(res,f,indent=2)
print(f"\\nDONE:{len(res)} models")'''

def make_output_cell():
    """Cell 8: Display + save results."""
    return '''with open("final_results.json")as f:d=json.load(f)
for n,r in sorted(d.items()):
    b=[f"{k}={v}"for k,v in r.items()if v is None]
    c=[f"{k}={v}"for k,v in r.items()if v is not None]
    print(f"  {"⚠️"if b else"✅"}{n:30s}{"  ".join(c)}")
import shutil;shutil.copy("final_results.json","/kaggle/working/final_results.json")'''


# ============================================================
# GAP ANALYSIS
# ============================================================
def check_gaps():
    """Report which models still need data."""
    merged_path = RESULTS_DIR / 'all_results_merged.json'
    if not merged_path.exists():
        print("No merged results file found. Run merge first.")
        return []

    with open(merged_path) as f:
        existing = json.load(f)

    total = len(existing)
    complete = sum(1 for v in existing.values() if all(x is not None for x in v.values()))
    incomplete = sum(1 for v in existing.values() if any(x is None for x in v.values()))
    print(f"\n  Total in data: {total} | Complete: {complete} | Incomplete: {incomplete}")

    gaps = []
    for hf_id, hf_ins, name, needs_4bit in ALL_MODELS:
        variants_to_check = [name, f"{name}-IT"] if hf_ins else [name]
        for vn in variants_to_check:
            # Determine status
            status = "not_in_data"
            if vn in existing:
                probes = existing[vn]
                nulls = {k for k,v in probes.items() if v is None}
                if nulls:
                    status = f"incomplete({','.join(sorted(nulls))})"
                else:
                    status = "complete"

            gaps.append({
                'model_name': vn,
                'status': status,
                'needs_run': status != "complete",
                'needs_4bit': needs_4bit,
            })

    return gaps

# ============================================================
# NOTEBOOK BUILDER
# ============================================================
def build_notebook(gaps, name=None):
    """Build a Kaggle notebook covering only the models that need runs."""
    if not name:
        name = f"sb-auto-{datetime.now().strftime('%Y%m%d-%H%M')}"

    # Filter models that need running
    needed = [g for g in gaps if g['needs_run']]

    # Group by 4bit vs fp16
    big_models = []
    small_models = []
    for g in needed:
        for hf_id, hf_ins, mn, nb in ALL_MODELS:
            if g['model_name'] == mn or g['model_name'] == f"{mn}-IT":
                big_models.append((hf_id, hf_ins, mn)) if nb else small_models.append((hf_id, hf_ins, mn))
                break

    # Deduplicate
    big_models = list(set(big_models))
    small_models = list(set(small_models))

    models_str = {
        "big": [[b[0], b[1], b[2]] for b in big_models],
        "small": [[s[0], s[1], s[2]] for s in small_models],
    }

    cells = make_core_cells()
    cells.append(make_model_cell(models_str))
    cells.append(make_inference_cell())
    cells.append(make_output_cell())

    return name, cells

# ============================================================
# MERGE RESULTS
# ============================================================
def merge_results():
    """Download latest results and merge into all_results_merged.json."""
    print("=== MERGING RESULTS ===")

    # Look for output directories
    output_dirs = sorted(KERNELS_DIR.glob("sb-auto-*/output/final_results.json"))

    if not output_dirs:
        # Also check numbered runs
        output_dirs = sorted(KERNELS_DIR.glob("scoring-bias-run-*/output/final_results.json"))

    if not output_dirs:
        print("No results found to merge.")
        return False

    # Load existing
    merged_path = RESULTS_DIR / 'all_results_merged.json'
    if merged_path.exists():
        with open(merged_path) as f:
            combined = json.load(f)
    else:
        combined = {}

    # Merge each result file (newest wins for same key)
    for fp in output_dirs:
        try:
            with open(fp) as f:
                data = json.load(f)
            for model, probes in data.items():
                if model not in combined:
                    combined[model] = probes
                else:
                    for probe, val in probes.items():
                        combined[model][probe] = val
            print(f"  + Merged {fp.parent.parent.name}: {len(data)} models")
        except Exception as e:
            print(f"  ✗ Failed {fp}: {e}")

    with open(merged_path, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\n  Total: {len(combined)} models")
    print(f"  Complete: {sum(1 for v in combined.values() if all(x is not None for x in v.values()))}")
    print(f"  Saved: {merged_path}")
    return True

# ============================================================
# FULL PIPELINE
# ============================================================
def run_pipeline():
    """Full: check → build → submit → poll → merge."""
    print("=" * 60)
    print("  SCORING BIAS AUTO-PIPELINE")
    print("=" * 60)

    # Step 1: Check gaps
    print("\n[1/5] Checking data gaps...")
    gaps = check_gaps()
    needed = [g for g in gaps if g['needs_run']]
    print(f"  {len(needed)} models need runs")

    if not needed:
        print("\n✅ All models complete! Nothing to run.")
        return

    # Step 2: Build notebook
    print(f"\n[2/5] Building notebook...")
    name, cells = build_notebook(gaps)

    # Identify big vs small
    big = [g for g in needed if g['needs_4bit']]
    small = [g for g in needed if not g['needs_4bit']]
    print(f"  Big (4-bit): {len(big)} models | Small (fp16): {len(small)} models")
    print(f"  Models: {', '.join(g['model_name'] for g in needed)}")

    # Step 3: Submit
    print(f"\n[3/5] Submitting {name} to Kaggle...")
    ok = write_and_submit(name, cells)
    if not ok:
        print("  ❌ Submit failed")
        return

    # Step 4: Poll
    print(f"\n[4/5] Polling {name} (checking every 120s)...")
    success = poll(name, interval=120)

    # Step 5: Download + merge
    if success:
        print(f"\n[5/5] Downloading and merging...")
        output(name)
        merge_results()
        print("\n✅ Pipeline complete!")
    else:
        print(f"\n  ⚠️  Kernel failed. Check logs: {KERNELS_DIR / name / 'output'}")

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'full'

    if cmd == 'full':
        run_pipeline()
    elif cmd == 'check':
        gaps = check_gaps()
        needed = [g for g in gaps if g['needs_run']]
        complete = [g for g in gaps if not g['needs_run']]
        print(f"\n  ✅ Complete: {len(complete)} models")
        print(f"  ⚠️  Need run: {len(needed)} models")
        for g in needed:
            print(f"    {g['model_name']:30s} [{g['status']}]  {'4bit' if g['needs_4bit'] else 'fp16'}")
    elif cmd == 'merge':
        merge_results()
    else:
        print("Usage: python3 -m infrastructure.auto_pipeline [full|check|merge]")
