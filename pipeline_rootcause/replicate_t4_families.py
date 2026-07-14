#!/usr/bin/env python3
"""
12-FAMILY REPLICATION — Kaggle T4 GPU
Loads models from HuggingFace, runs inference locally.
No API costs, no rate limits. ~30-60 min total.

Set HF_TOKEN env var for gated models (Llama, Gemma):
  import os; os.environ["HF_TOKEN"] = "hf_..."
"""
import json, os, time, re, gc, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path

# ── 50 Items ──
ITEMS = [
    (1, "Explain how photosynthesis converts light energy into chemical energy.",
     "Photosynthesis happens in plants where they use sunlight to make food. Chlorophyll captures light and converts CO2 and water into glucose and oxygen."),
    (2, "Describe the structure of an atom.",
     "An atom has a nucleus with protons and neutrons, and electrons orbit around it in shells."),
    (3, "What is Newton's second law of motion?",
     "Force equals mass times acceleration. F = ma."),
    (4, "Explain the water cycle.",
     "Water evaporates from oceans, forms clouds, and falls as rain. Then it flows back to oceans."),
    (5, "What causes the seasons on Earth?",
     "The Earth's axis is tilted, so different parts get different amounts of sunlight throughout the year."),
    (6, "Describe how vaccines work.",
     "Vaccines expose the immune system to a harmless version of a pathogen, building immunity without causing disease."),
    (7, "Explain the difference between DNA and RNA.",
     "DNA is double-stranded and stores genetic information. RNA is single-stranded and aids in protein synthesis."),
    (8, "What is the greenhouse effect?",
     "Greenhouse gases trap heat in the atmosphere, warming the planet. Essential for life but excess causes global warming."),
    (9, "Describe cellular respiration.",
     "Cells break down glucose with oxygen to produce energy (ATP), carbon dioxide, and water in mitochondria."),
    (10, "Why is the sky blue?",
     "Sunlight scatters in the atmosphere. Blue light scatters more due to its shorter wavelength."),
    (11, "What is machine learning?",
     "Machine learning is when computers learn patterns from data without being explicitly programmed for every case."),
    (12, "How does a database index work?",
     "An index is like a book's table of contents — it finds data faster without scanning everything."),
    (13, "Difference between TCP and UDP?",
     "TCP is reliable and connection-oriented. UDP is faster but doesn't guarantee delivery."),
    (14, "What is an API?",
     "An API lets software applications communicate using defined requests and responses."),
    (15, "How does encryption work?",
     "Encryption converts readable data into coded form using algorithms and keys. Only authorized parties can decrypt."),
    (16, "What is a blockchain?",
     "A blockchain is a distributed ledger with data in cryptographically linked blocks. Each references the previous one."),
    (17, "Describe a neural network.",
     "A neural network has layers of connected nodes that process information. Connection weights adjust during training."),
    (18, "What is version control?",
     "Version control tracks file changes over time, letting you revert to previous versions and collaborate."),
    (19, "What is a software container?",
     "A container packages code and dependencies so it runs consistently across environments."),
    (20, "Difference between HTTP and HTTPS?",
     "HTTPS encrypts data between browser and server via SSL/TLS; HTTP sends plain text."),
    (21, "Explain supply and demand.",
     "High demand and low supply raises prices. Excess supply over demand lowers prices."),
    (22, "Causes of World War I?",
     "Militarism, alliances, imperialism, nationalism, and assassination of Archduke Franz Ferdinand."),
    (23, "Republic vs democracy?",
     "In a democracy, people vote directly on laws. In a republic, they elect representatives."),
    (24, "What is opportunity cost?",
     "The value of the next best alternative given up when making a choice."),
    (25, "Describe the Renaissance.",
     "Cultural rebirth in Europe from 14th-17th centuries, focusing on art, science, and humanism."),
    (26, "What is comparative advantage?",
     "Countries should specialize in goods where they have lower opportunity cost and trade for others."),
    (27, "Cult vs religion difference?",
     "Cults are smaller, newer, centered on a charismatic leader. Religions are established with broader followings."),
    (28, "Describe the Cold War.",
     "Geopolitical tension between US and Soviet Union from 1947-1991 without direct military conflict."),
    (29, "Significance of Magna Carta?",
     "Established in 1215 that everyone, including the king, is subject to the law. Influenced constitutional governance."),
    (30, "What is inflation?",
     "When the general price level rises over time, reducing purchasing power."),
    (31, "How to make coffee?",
     "Boil water, add ground coffee to a filter, pour water over it, let drip, serve."),
    (32, "Flat tire procedure?",
     "Pull over safely, use jack to lift car, remove lug nuts, replace with spare, tighten nuts."),
    (33, "How to create a budget?",
     "List income and expenses, categorize spending, set savings goals, track monthly."),
    (34, "Best way to study for an exam?",
     "Review notes, practice problems, spaced repetition, take breaks, sleep well before test."),
    (35, "How to cook pasta?",
     "Boil salted water, add pasta, cook until al dente, drain, add sauce."),
    (36, "Pack for a beach trip?",
     "Towel, sunscreen, water, snacks, sunglasses, hat, swimsuit, book or music."),
    (37, "How to change a light bulb?",
     "Turn off power, let bulb cool, remove old bulb, screw in new one securely."),
    (38, "Proper hand washing?",
     "Wet hands, apply soap, scrub 20 seconds including between fingers, rinse, dry with clean towel."),
    (39, "How to tie a tie?",
     "Wrap wide end around narrow end, pass through loop, tighten. Four-in-hand is simplest."),
    (40, "Fire emergency procedure?",
     "Stay low to avoid smoke, feel doors for heat, use stairs not elevators, call 911 when safe."),
    (41, "What is the Pythagorean theorem?",
     "a² + b² = c², where c is the hypotenuse of a right triangle."),
    (42, "Area of a circle?",
     "Area = πr², where r is the radius."),
    (43, "What is a derivative?",
     "A derivative measures how a function changes as its input changes — the slope at a point."),
    (44, "Quadratic formula?",
     "x = (-b ± √(b² - 4ac)) / 2a for ax² + bx + c = 0."),
    (45, "What is probability?",
     "Probability measures event likelihood from 0 (impossible) to 1 (certain)."),
    (46, "What is a prime number?",
     "Divisible only by 1 and itself. Examples: 2, 3, 5, 7, 11."),
    (47, "How to calculate the mean?",
     "Add all values and divide by the count of values."),
    (48, "Permutation vs combination?",
     "Permutations consider order (ABC ≠ CBA). Combinations do not (ABC = CBA)."),
    (49, "What is a logarithm?",
     "The power to which a base must be raised to get a number. log₂(8)=3 because 2³=8."),
    (50, "What is standard deviation?",
     "Measures data spread from the mean. Low value = data points close to the mean."),
]

# ── Scoring prompts ──
def build_prompt(rubric, instruction, response):
    return f"Evaluate the following response.\n### Instruction: {instruction}\n### Response: {response}\n### {rubric}\n### Score:"

NUMERIC = "Score from 1-5 (where 1 is worst, 5 is best)"
REVERSED = "Score from 1-5 (where 1 is best, 5 is worst)"
LETTER = "Score from A-E (where A is best, E is worst)"
DESCRIPTIVE = "Score: Poor, Fair, Average, Good, or Excellent"

def extract_score(text, variant):
    t = text.strip()
    if variant == "letter":
        m = re.search(r'[A-Ea-e]', t)
        if m: return " ABCDE".index(m.group().upper())
    elif variant == "descriptive":
        tl = t.lower()
        if "excellent" in tl: return 5
        if "good" in tl: return 4
        if "average" in tl or "fair" in tl or "acceptable" in tl: return 3
        if "poor" in tl or "bad" in tl: return 2
        if "terrible" in tl or "very poor" in tl: return 1
    nums = re.findall(r'[1-5]', t)
    return int(nums[0]) if nums else 3

PROBES = [
    ("rubric_order", ["normal","reversed"]),
    ("score_id", ["numeric","letter","descriptive"]),
    ("reference_answer", ["no_ref","good_ref","poor_ref"]),
]

# ── Models (base + instruct pairs, small enough for T4 16GB) ──
# Qwen = open (Apache 2.0, no auth). Llama/Gemma = gated (need HF_TOKEN).
MODELS = [
    # Open (no auth needed)
    ("Qwen/Qwen2.5-0.5B", "Qwen2.5-0.5B"),
    ("Qwen/Qwen2.5-0.5B-Instruct", "Qwen2.5-0.5B-IT"),
    ("Qwen/Qwen2.5-1.5B", "Qwen2.5-1.5B"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen2.5-1.5B-IT"),
    ("Qwen/Qwen2.5-7B", "Qwen2.5-7B"),
    ("Qwen/Qwen2.5-7B-Instruct", "Qwen2.5-7B-IT"),
    # Gated (need HF_TOKEN set)
    ("meta-llama/Llama-3.2-1B", "Llama-3.2-1B"),
    ("meta-llama/Llama-3.2-1B-Instruct", "Llama-3.2-1B-IT"),
    ("meta-llama/Llama-3.2-3B", "Llama-3.2-3B"),
    ("meta-llama/Llama-3.2-3B-Instruct", "Llama-3.2-3B-IT"),
    ("google/gemma-2-2b", "Gemma-2-2B"),
    ("google/gemma-2-2b-it", "Gemma-2-2B-IT"),
]

CK = "/kaggle/working/t4fam_ck.json"
OT = "/kaggle/working/t4fam_results.json"
HF_TOKEN = os.environ.get("HF_TOKEN", None)

all_r = {}
done = set()
if os.path.exists(CK):
    with open(CK) as f:
        cp = json.load(f)
    all_r = cp.get("r", {})
    done = set(cp.get("d", []))
    print(f"Resumed: {len(done)} models done")

for mid, nm in MODELS:
    if nm in done:
        print(f"SKIP {nm} (checkpointed)")
        continue
    
    print(f"\n=== LOADING {nm} ({mid}) ===")
    t0 = time.time()
    
    # Load tokenizer + model
    tok_kwargs = {"token": HF_TOKEN} if HF_TOKEN else {}
    model_kwargs = {
        "torch_dtype": torch.float16,
        "device_map": "auto",
        "token": HF_TOKEN
    } if HF_TOKEN else {
        "torch_dtype": torch.float16,
        "device_map": "auto"
    }
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(mid, **tok_kwargs)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(mid, **model_kwargs)
        model.eval()
        print(f"Loaded in {time.time()-t0:.0f}s")
    except Exception as e:
        print(f"FAILED to load {nm}: {e}")
        continue
    
    # Run probes
    rs = {}
    for pt, pv in PROBES:
        rs[pt] = {}
        for vn in pv:
            scores = []
            for inst, resp in ITEMS:
                # Build prompt
                rubric = NUMERIC
                if pt == "rubric_order" and vn == "reversed":
                    rubric = REVERSED
                elif pt == "score_id":
                    if vn == "letter": rubric = LETTER
                    elif vn == "descriptive": rubric = DESCRIPTIVE
                
                r = resp
                if pt == "reference_answer":
                    if vn == "good_ref": r = f"[Good example]\n{resp}"
                    elif vn == "poor_ref": r = f"[Poor example]\n{resp}"
                
                prompt = build_prompt(rubric, inst, r)
                inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
                
                with torch.no_grad():
                    out = model.generate(
                        **inputs,
                        max_new_tokens=5,
                        temperature=0.0,
                        do_sample=False,
                        pad_token_id=tokenizer.pad_token_id
                    )
                
                # Extract only the new tokens
                new_tokens = out[0][inputs.input_ids.shape[1]:]
                text = tokenizer.decode(new_tokens, skip_special_tokens=True)
                score = extract_score(text, vn if pt == "score_id" else "numeric")
                scores.append(score)
                
                if len(scores) % 10 == 0:
                    print(".", end="", flush=True)
            
            rs[pt][vn] = scores
            avg = sum(scores) / len(scores)
            print(f" {vn[:3]}={avg:.1f}", end="", flush=True)
        print()
    
    all_r[nm] = rs
    done.add(nm)
    with open(CK, "w") as f:
        json.dump({"r": all_r, "d": list(done)}, f)
    
    # Free GPU memory
    del model, tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    print(f"Freed GPU. {time.time()-t0:.0f}s total for {nm}")

with open(OT, "w") as f:
    json.dump(all_r, f)
print(f"\nDONE. Saved to {OT}")
print(f"Models completed: {len(done)}/{len(MODELS)}")
