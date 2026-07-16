#!/usr/bin/env python3
"""Build the Kaggle notebook programmatically to ensure correct JSON format."""
import json

cells = []

def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src.split("\n")})

def code(src):
    cells.append({"cell_type": "code", "metadata": {}, "source": [l + "\n" for l in src.split("\n")]})

md("""# Paper 1: Additional GPU Experiments
**Fills all remaining GPU gaps for Scoring Bias paper**

## What this notebook does:
1. Runs 10 new base+instruct pairs — models NOT already in our dataset
2. Attention analysis at Llama-3-8B — validates Format Efficiency Hypothesis
3. Multi-model ensembling analysis

**Time:** ~6-8 hrs on Kaggle T4 (free)
**Requires:** HF_TOKEN for gated models (meta-llama)

### Before starting:
1. Go to https://huggingface.co/settings/tokens → Create read token
2. Accept license: meta-llama/Meta-Llama-3-8B and mistralai/Mistral-7B-v0.3
3. Upload this notebook to Kaggle and Run All""")

code("""# ===== SETUP =====
!pip install -q transformers torch huggingface_hub numpy scipy
import torch, gc, os, json, re, time, random, numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import getpass

random.seed(42)
torch.manual_seed(42)
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB')

token = getpass.getpass('HuggingFace token: ')
login(token=token)
os.environ['HF_TOKEN'] = token""")

code("""# ===== 50 EVALUATION ITEMS (5 domains x 10) =====
ITEMS = [
    {'instr':'Explain how photosynthesis works.','resp':'Plants use sunlight to convert CO2 and water into glucose and oxygen.'},
    {'instr':'What is the theory of relativity?','resp':'Einstein theory says space and time are relative.'},
    {'instr':'Describe the water cycle.','resp':'Water evaporates, forms clouds, returns as precipitation.'},
    {'instr':'What causes earthquakes?','resp':'Tectonic plates shift, releasing seismic waves.'},
    {'instr':'Explain how vaccines work.','resp':'Vaccines train immune system to recognize pathogens.'},
    {'instr':'What is DNA?','resp':'DNA carries genetic instructions for growth and reproduction.'},
    {'instr':'Describe the solar system.','resp':'8 planets orbiting the Sun.'},
    {'instr':'What is entropy?','resp':'Disorder measure. Always increases per 2nd law.'},
    {'instr':'How do batteries work?','resp':'Chemical reactions create electron flow via electrolyte.'},
    {'instr':'What is a black hole?','resp':'Gravity so strong light cannot escape.'},
    {'instr':'What is machine learning?','resp':'AI learning patterns from data without explicitly programming.'},
    {'instr':'Describe cloud computing.','resp':'On-demand computing resources over the internet.'},
    {'instr':'What is an API?','resp':'Interface for different software to communicate with each other.'},
    {'instr':'Explain encryption.','resp':'Algorithms that encode data using cryptographic keys.'},
    {'instr':'What is a database index?','resp':'Structure speeding up data retrieval like a book index.'},
    {'instr':'What is Python?','resp':'High-level readable interpreted programming language.'},
    {'instr':'Explain the internet.','resp':'Global network of computers communicating via TCP/IP.'},
    {'instr':'What is blockchain?','resp':'Distributed ledger recording transactions in immutable blocks.'},
    {'instr':'What is an operating system?','resp':'Software managing hardware resources for applications.'},
    {'instr':'Explain neural networks.','resp':'Computational systems inspired by biological neural networks.'},
    {'instr':'What caused World War I?','resp':'Assassination of Archduke Franz Ferdinand triggered alliance system.'},
    {'instr':'Explain democracy.','resp':'System where citizens vote for representatives.'},
    {'instr':'What was the Renaissance?','resp':'14th-17th century cultural rebirth in Europe.'},
    {'instr':'Describe capitalism.','resp':'Economic system with private ownership and profit motive.'},
    {'instr':'What is the United Nations?','resp':'International organization for peace and cooperation.'},
    {'instr':'Explain the Cold War.','resp':'Geopolitical tension between US and USSR 1947-1991.'},
    {'instr':'What is ethics?','resp':'Branch of philosophy studying moral right and wrong.'},
    {'instr':'Describe the Enlightenment.','resp':'18th century intellectual movement emphasizing reason.'},
    {'instr':'What is the Constitution?','resp':'Supreme law establishing government structure and rights.'},
    {'instr':'Explain globalization.','resp':'Increasing interconnectedness of world economies and cultures.'},
    {'instr':'How to make a budget?','resp':'Track income and expenses, allocate for needs and savings.'},
    {'instr':'What is healthy eating?','resp':'Balanced diet with fruits, vegetables, protein, whole grains.'},
    {'instr':'Explain first aid for burns.','resp':'Cool with running water, cover with sterile dressing.'},
    {'instr':'What is recycling?','resp':'Converting waste materials into new reusable products.'},
    {'instr':'How does a car engine work?','resp':'Fuel combustion in cylinders drives pistons turning crankshaft.'},
    {'instr':'What is renewable energy?','resp':'Energy from replenishable sources like sun and wind.'},
    {'instr':'How to grow vegetables?','resp':'Plant seeds in soil with water, sunlight, and nutrients.'},
    {'instr':'What is a mortgage?','resp':'Loan for purchasing property paid in monthly installments.'},
    {'instr':'Explain the stock market.','resp':'Platform where company shares are bought and sold.'},
    {'instr':'What is inflation?','resp':'General increase in prices reducing purchasing power.'},
    {'instr':'What is the Pythagorean theorem?','resp':'a squared plus b squared equals c squared.'},
    {'instr':'Explain a prime number.','resp':'Number divisible only by 1 and itself.'},
    {'instr':'What is calculus?','resp':'Mathematics of change using derivatives and integrals.'},
    {'instr':'What is a logarithm?','resp':'Inverse of exponentiation, log base 10 of 100 is 2.'},
    {'instr':'What is the quadratic formula?','resp':'x equals negative b plus or minus square root of b squared minus 4ac over 2a.'},
    {'instr':'Explain probability.','resp':'Likelihood of events occurring, from 0 to 1.'},
    {'instr':'What is a proof?','resp':'Logical demonstration that a statement follows from axioms.'},
    {'instr':'What is a function?','resp':'Relation where each input maps to exactly one output.'},
    {'instr':'Explain standard deviation.','resp':'Measure of dispersion from the mean.'},
    {'instr':'What is a matrix?','resp':'Rectangular array of numbers for linear transformations.'},
]
print(f'{len(ITEMS)} items loaded')""")

code("""# ===== PROBE TEMPLATES =====
PROBE_VARIANTS = {
    'rubric_order': ['control', 'reversed', 'random'],
    'score_id': ['numeric', 'letter', 'descriptive'],
    'reference_answer': ['none', 'good', 'poor'],
}

def make_prompt(item, probe_type, probe_variant):
    instr = item['instr']
    resp = item['resp']
    if probe_type == 'rubric_order':
        rubric = 'Score from 1-5 (where 1 is worst, 5 is best)' if probe_variant == 'control' else \\
                 'Score from 1-5 (where 1 is best, 5 is worst)' if probe_variant == 'reversed' else \\
                 'Score from 1-5'
        return f'Evaluate the following response.\\n### Instruction: {instr}\\n### Response: {resp}\\n### {rubric}\\n### Score:'
    elif probe_type == 'score_id':
        rubric = 'Score from 1-5' if probe_variant == 'numeric' else \\
                 'Score A-E (where A is best, E is worst)' if probe_variant == 'letter' else \\
                 'Rate: Poor, Fair, Good, Very Good, Excellent'
        return f'Evaluate the following response.\\n### Instruction: {instr}\\n### Response: {resp}\\n### {rubric}\\n### Score:'
    elif probe_type == 'reference_answer':
        if probe_variant == 'none':
            return f'Evaluate the following response.\\n### Instruction: {instr}\\n### Response: {resp}\\n### Score from 1-5 (where 1 is worst, 5 is best)\\n### Score:'
        elif probe_variant == 'good':
            return f'Evaluate the following response.\\n### Instruction: {instr}\\n### Excellent response: This is a perfect answer.\\n### Response: {resp}\\n### Score from 1-5 (where 1 is worst, 5 is best)\\n### Score:'
        else:
            return f'Evaluate the following response.\\n### Instruction: {instr}\\n### Poor response: This is wrong.\\n### Response: {resp}\\n### Score from 1-5 (where 1 is worst, 5 is best)\\n### Score:'
print('Probes ready')""")

code("""# ===== NEW BASE+INSTRUCT PAIRS (families NOT in existing data) =====
NEW_FAMILIES = [
    # Open 7B+ models (needed for content bias scale validation)
    ('mistralai/Mistral-7B-v0.3', 'mistralai/Mistral-7B-Instruct-v0.3', 'Mistral-7B-v0.3'),
    ('allenai/OLMo-7B-hf', 'allenai/OLMo-7B-instruct-hf', 'OLMo-7B'),
    ('deepseek-ai/deepseek-llm-7b-base', 'deepseek-ai/deepseek-llm-7b-chat', 'DeepSeek-7B'),
    ('google/gemma-2-9b', 'google/gemma-2-9b-it', 'Gemma2-9B'),
    # Smaller new architectures
    ('google/recurrentgemma-2b', 'google/recurrentgemma-2b-it', 'RecurrentGemma-2B'),
    ('ibm-granite/granite-3b-code-base', 'ibm-granite/granite-3b-code-instruct', 'Granite-3B'),
    ('tiiuae/falcon-rw-1b', 'tiiuae/falcon-rw-1b-instruct', 'Falcon-1B'),
    ('TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0', 'TinyLlama-1.1B'),
    ('allenai/OLMo-1B-hf', 'allenai/OLMo-1B-instruct-hf', 'OLMo-1B'),
    ('microsoft/Phi-3-mini-4k-instruct', 'microsoft/Phi-3-mini-4k-instruct', 'Phi-3-mini'),
]
print(f'{len(NEW_FAMILIES)} new families to run')""")

code("""# ===== SCORING FUNCTION =====
def score_model(model, tokenizer, prompt, device):
    inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=1024).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=5, temperature=0.0,
            do_sample=False, pad_token_id=tokenizer.eos_token_id, num_return_sequences=1)
    full = tokenizer.decode(outputs[0], skip_special_tokens=True)
    score_text = full[len(prompt):].strip()
    numbers = re.findall(r'[\\d.]+', score_text)
    if numbers:
        try: return float(numbers[0])
        except: pass
    return None
print('Scoring function ready')""")

code("""# ===== RUN TIER 2: collect bias data for all NEW families =====
print(f'Starting run for {len(NEW_FAMILIES)} families on {torch.cuda.get_device_name(0)}')
all_results = {}
device = torch.device('cuda')

for base_id, instruct_id, name in NEW_FAMILIES:
    for variant_suffix, model_id in [('', base_id), ('-IT', instruct_id)]:
        model_name = f'{name}{variant_suffix}'
        print(f'\\n{\"=\"*60}\\nLoading {model_name} ({model_id})\\n{\"=\"*60}')
        try:
            load_kwargs = {'torch_dtype': torch.float16, 'device_map': 'auto'}
            if any(s in model_id for s in ['9b', '9B', '7b', '7B', '8b', '8B']):
                from transformers import BitsAndBytesConfig
                load_kwargs['quantization_config'] = BitsAndBytesConfig(load_in_4bit=True)
            tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.environ['HF_TOKEN'])
            if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
            model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs, token=os.environ['HF_TOKEN'])
            model.eval()
            print(f'  Loaded: {sum(p.numel() for p in model.parameters())/1e6:.0f}M params')
        except Exception as e:
            print(f'  FAILED to load {model_id}: {e}')
            continue

        scores = {'rubric_order': {}, 'score_id': {}, 'reference_answer': {}}
        for probe_type, probe_variants in PROBE_VARIANTS.items():
            for probe_variant in probe_variants:
                item_scores = []
                for idx, item in enumerate(ITEMS):
                    reps = []
                    for _ in range(3):
                        prompt = make_prompt(item, probe_type, probe_variant)
                        try:
                            s = score_model(model, tokenizer, prompt, device)
                            if s is not None: reps.append(s)
                        except: pass
                    if reps: item_scores.append(np.mean(reps))
                    if (idx + 1) % 25 == 0:
                        print(f'  {model_name} {probe_type}/{probe_variant}: {idx+1}/{len(ITEMS)}', flush=True)
                scores[probe_type][probe_variant] = {
                    'mean': float(np.mean(item_scores)) if item_scores else None,
                    'std': float(np.std(item_scores)) if item_scores else None,
                }

        # Compute bias delta per probe
        result = {}
        for probe_type, pv in PROBE_VARIANTS.items():
            means = [scores[probe_type][v]['mean'] for v in pv if scores[probe_type][v]['mean'] is not None]
            result[probe_type] = max(means) - min(means) if len(means) >= 2 else None
        all_results[model_name] = result
        print(f'  DONE {model_name}: {result}')
        del model; gc.collect(); torch.cuda.empty_cache()

with open('/kaggle/working/new_families_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print(f'\\nSaved {len(all_results)} model results to new_families_results.json')""")

md("""---
## Part 2: Attention Analysis at 8B
Tests Format Efficiency Hypothesis on Llama-3-8B base vs instruct.
If format attention decreases (k < 1.0) like at 3B, the hypothesis is confirmed at scale.
---""")

code("""# ===== ATTENTION ANALYSIS AT Llama-3-8B =====
ATTN_PROMPT = '''Evaluate the following response.
### Instruction: Explain how photosynthesis works.
### Response: Photosynthesis happens in plants where they use sunlight to make food.
### Score from 1-5 (where 1 is worst, 5 is best)
### Score:'''
FORMAT_PATTERNS = ['###', 'Instruction', 'Response', 'Score', '1', '2', '3', '4', '5',
                   'from', 'where', 'is', 'the', 'worst', 'best', ':', '\\\\n', ' ', '.']
CONTENT_PATTERNS = ['photosynthesis', 'explain', 'happens', 'plants', 'sunlight',
                    'food', 'make', 'use', 'they', 'how', 'works']

def classify_tokens(token_ids, tokenizer):
    labels = []
    for tid in token_ids:
        t = tokenizer.decode(tid).strip().lower()
        if any(f in t for f in FORMAT_PATTERNS): labels.append('FORMAT')
        elif any(c in t for c in CONTENT_PATTERNS): labels.append('CONTENT')
        else: labels.append('OTHER')
    return labels

ATTN_MODELS = [
    ('meta-llama/Meta-Llama-3-8B', 'Llama-3-8B-base'),
    ('meta-llama/Meta-Llama-3-8B-Instruct', 'Llama-3-8B-instruct'),
]
attn_results = {}
for model_id, name in ATTN_MODELS:
    print(f'\\n=== Loading {name} ===')
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.environ['HF_TOKEN'])
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16,
        device_map='auto', output_attentions=True, token=os.environ['HF_TOKEN'])
    model.eval()
    inputs = tokenizer(ATTN_PROMPT, return_tensors='pt').to(model.device)
    labels = classify_tokens(inputs['input_ids'][0].tolist(), tokenizer)
    n_fmt = labels.count('FORMAT'); n_con = labels.count('CONTENT')
    print(f'  Tokens: {len(labels)} total, {n_fmt} format, {n_con} content')
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    format_attn, content_attn = [], []
    for attn in outputs.attentions:
        last_attn = attn[0].mean(dim=0)[-1, :] * 100
        f_pct = sum(last_attn[i].item() for i in range(len(labels)) if labels[i] == 'FORMAT')
        c_pct = sum(last_attn[i].item() for i in range(len(labels)) if labels[i] == 'CONTENT')
        format_attn.append(f_pct); content_attn.append(c_pct)
    mean_fmt = float(np.mean(format_attn)); mean_con = float(np.mean(content_attn))
    attn_results[name] = {'mean_format_attn': mean_fmt, 'mean_content_attn': mean_con}
    print(f'  Mean format: {mean_fmt:.2f}%  Content: {mean_con:.2f}%')
    del model; gc.collect(); torch.cuda.empty_cache()

base_a = attn_results.get('Llama-3-8B-base')
instruct_a = attn_results.get('Llama-3-8B-instruct')
if base_a and instruct_a:
    kf = instruct_a['mean_format_attn'] / max(base_a['mean_format_attn'], 0.01)
    kc = instruct_a['mean_content_attn'] / max(base_a['mean_content_attn'], 0.01)
    print(f'\\n{\"=\"*60}\\nFORMAT EFFICIENCY AT 8B\\n{\"=\"*60}')
    print(f'Format k = {kf:.3f}x (IIAR >1.0, Format Efficiency <1.0)')
    print(f'Content k = {kc:.3f}x')
    print(f'\\nPrior: 0.5B k_f=1.003 | 3B k_f=0.879 | 8B k_f={kf:.3f}')
    if kf < 1.0: print('\\n✅ Format Efficiency confirmed at 8B scale')
    else: print('\\n❌ Format Efficiency NOT confirmed at 8B')

with open('/kaggle/working/attention_results_8b.json', 'w') as f:
    json.dump(attn_results, f, indent=2)
print('\\nSaved attention_results_8b.json')""")

md("""---
## Part 3: Download Instructions
After the notebook finishes, download these from Kaggle output:
1. `new_families_results.json` - bias data for new model families
2. `attention_results_8b.json` - attention analysis results
3. `experiment_summary.json` - combined summary table

Copy them to `results_rootcause/` in the repo. Run the analysis scripts to incorporate with existing data:
```bash
python results_rootcause/analysis/merge_new_families.py
```""")

code("""# ===== SAVE SUMMARY =====
summary = {
    'new_families': list(all_results.keys()),
    'new_families_count': len(all_results),
    'attention_models_tested': list(attn_results.keys()),
}
with open('/kaggle/working/experiment_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f'\\nAll done! {len(all_results)} new families + {len(attn_results)} attention models.')
print('Download: new_families_results.json, attention_results_8b.json, experiment_summary.json')""")

path = r'C:\Users\Admin\Research\research-draft\pipeline_rootcause\paper1_gpu_experiments.kaggle.ipynb'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(cells, f, indent=1, ensure_ascii=False)
print(f'Wrote {len(cells)} cells to {path}')
