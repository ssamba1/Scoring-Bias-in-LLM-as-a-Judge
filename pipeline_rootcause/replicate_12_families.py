#!/usr/bin/env python3
"""
12-FAMILY REPLICATION — run on Kaggle or Colab
Cost: $0.17 (18 of 20 models are free on OpenRouter)
Time: ~2 hours (all 20 models, 450 calls each)
"""
import json, os, time, re, sys
from openai import OpenAI

# ── 50 Items (same as human baseline) ──
ITEMS = [
    (1,0,"Explain how photosynthesis converts light energy into chemical energy.",
     "Photosynthesis happens in plants where they use sunlight to make food. The chlorophyll captures light and converts CO2 and water into glucose and oxygen."),
    (2,0,"Describe the structure of an atom.",
     "An atom has a nucleus with protons and neutrons, and electrons orbit around it in shells."),
    (3,0,"What is Newton's second law of motion?",
     "Force equals mass times acceleration. F = ma."),
    (4,0,"Explain the water cycle.",
     "Water evaporates from oceans, forms clouds, and falls as rain. Then it flows back to oceans."),
    (5,0,"What causes the seasons on Earth?",
     "The Earth's axis is tilted, so different parts get different amounts of sunlight throughout the year."),
    (6,0,"Describe how vaccines work.",
     "Vaccines expose the immune system to a harmless version of a pathogen, building immunity without causing disease."),
    (7,0,"Explain the difference between DNA and RNA.",
     "DNA is double-stranded and stores genetic information. RNA is single-stranded and helps in protein synthesis."),
    (8,0,"What is the greenhouse effect?",
     "Greenhouse gases trap heat in the atmosphere, warming the planet. This is essential for life but excess causes global warming."),
    (9,0,"Describe the process of cellular respiration.",
     "Cells break down glucose with oxygen to produce energy (ATP), carbon dioxide, and water. It happens in mitochondria."),
    (10,0,"Explain why the sky is blue.",
     "Sunlight scatters in the atmosphere. Blue light scatters more than other colors because of its shorter wavelength."),
    (11,1,"What is machine learning?",
     "Machine learning is when computers learn patterns from data without being explicitly programmed for every case."),
    (12,1,"Explain how a database index works.",
     "An index is like a book's table of contents — it helps find data faster without scanning everything."),
    (13,1,"Describe the difference between TCP and UDP.",
     "TCP is reliable and connection-oriented. UDP is faster but doesn't guarantee delivery."),
    (14,1,"What is an API?",
     "An API lets different software applications communicate with each other using defined requests and responses."),
    (15,1,"Explain how encryption works.",
     "Encryption converts readable data into a coded form using algorithms and keys. Only authorized parties can decrypt it."),
    (16,1,"What is a blockchain?",
     "A blockchain is a distributed ledger where data is stored in blocks linked by cryptography. Each block references the previous one."),
    (17,1,"Describe the concept of a neural network.",
     "A neural network has layers of connected nodes that process information. Each connection has a weight that adjusts during training."),
    (18,1,"What is version control?",
     "Version control tracks changes to files over time, letting you revert to previous versions and collaborate with others."),
    (19,1,"Explain what a container is in software.",
     "A container packages code and its dependencies so it runs consistently across different environments."),
    (20,1,"What is the difference between HTTP and HTTPS?",
     "HTTPS encrypts data between browser and server using SSL/TLS, while HTTP sends it in plain text."),
    (21,2,"Explain the concept of supply and demand.",
     "When demand is high and supply is low, prices rise. When supply exceeds demand, prices fall."),
    (22,2,"Describe the main causes of World War I.",
     "Major causes include militarism, alliances, imperialism, nationalism, and the assassination of Archduke Franz Ferdinand."),
    (23,2,"What is the difference between a republic and a democracy?",
     "In a democracy, people vote directly on laws. In a republic, they elect representatives to make laws for them."),
    (24,2,"Explain the concept of opportunity cost.",
     "Opportunity cost is the value of the next best alternative you give up when making a choice."),
    (25,2,"Describe the Renaissance period.",
     "The Renaissance was a period of cultural rebirth in Europe from the 14th to 17th centuries, focusing on art, science, and humanism."),
    (26,2,"What is the theory of comparative advantage?",
     "Countries should specialize in producing goods where they have a lower opportunity cost and trade for others."),
    (27,2,"Explain the difference between a cult and a religion.",
     "Cults are typically smaller, newer, and centered around a charismatic leader. Religions are established with broader followings."),
    (28,2,"Describe the Cold War.",
     "The Cold War was a period of geopolitical tension between the US and Soviet Union from 1947-1991, without direct military conflict."),
    (29,2,"What is the significance of the Magna Carta?",
     "The Magna Carta (1215) established that everyone, including the king, is subject to the law. It influenced constitutional governance."),
    (30,2,"Explain the concept of inflation.",
     "Inflation is when the general price level of goods and services rises over time, reducing purchasing power."),
    (31,3,"How do you make a cup of coffee?",
     "Boil water, add ground coffee to a filter, pour water over it, let it drip through, and serve."),
    (32,3,"What should you do if you get a flat tire?",
     "Pull over safely, use the jack to lift the car, remove the lug nuts, replace with the spare tire, and tighten the nuts."),
    (33,3,"How do you create a budget?",
     "List your income and expenses, categorize spending, set savings goals, and track progress monthly."),
    (34,3,"What is the best way to study for an exam?",
     "Review notes, practice problems, use spaced repetition, take breaks, and get enough sleep before the test."),
    (35,3,"How do you cook pasta?",
     "Boil salted water, add pasta, cook until al dente, drain, and add sauce."),
    (36,3,"What should you pack for a beach trip?",
     "Towel, sunscreen, water, snacks, sunglasses, hat, swimsuit, and a book or music."),
    (37,3,"How do you change a light bulb?",
     "Turn off the power, let the bulb cool, remove the old bulb, and screw in the new one securely."),
    (38,3,"What is the proper way to wash your hands?",
     "Wet hands, apply soap, scrub for 20 seconds including between fingers, rinse, and dry with a clean towel."),
    (39,3,"How do you tie a tie?",
     "Wrap the wide end around the narrow end, pass it through the loop, and tighten. The four-in-hand knot is simplest."),
    (40,3,"What should you do in a fire emergency?",
     "Stay low to avoid smoke, feel doors for heat before opening, use stairs not elevators, and call 911 once safe."),
    (41,4,"What is the Pythagorean theorem?",
     "a² + b² = c², where c is the hypotenuse of a right triangle."),
    (42,4,"How do you calculate the area of a circle?",
     "Area = πr², where r is the radius."),
    (43,4,"Explain what a derivative is in calculus.",
     "A derivative measures how a function changes as its input changes — the slope at a point."),
    (44,4,"What is the quadratic formula?",
     "x = (-b ± √(b² - 4ac)) / 2a, used to solve ax² + bx + c = 0."),
    (45,4,"Explain the concept of probability.",
     "Probability measures the likelihood of an event, from 0 (impossible) to 1 (certain)."),
    (46,4,"What is a prime number?",
     "A prime number is only divisible by 1 and itself. Examples: 2, 3, 5, 7, 11."),
    (47,4,"How do you calculate the mean of a dataset?",
     "Add all values and divide by the count of values."),
    (48,4,"What is the difference between permutation and combination?",
     "Permutations consider order (ABC ≠ CBA). Combinations do not consider order (ABC = CBA)."),
    (49,4,"Explain the concept of a logarithm.",
     "A logarithm answers 'to what power must a base be raised to get a number?' log₂(8) = 3 because 2³ = 8."),
    (50,4,"What is standard deviation?",
     "Standard deviation measures how spread out numbers are from the mean. A low value means data points are close to the mean."),
]

# ── Prompt builder ──
NUMERIC_RUBRIC = "Score from 1-5 (where 1 is worst, 5 is best)"
LETTER_RUBRIC = "Score from A-E (where A is best, E is worst)"
DESCRIPTIVE_RUBRIC = "Score: Poor, Fair, Average, Good, or Excellent"

def build_prompt(rubric, instruction, response):
    return f"Evaluate the following response.\n### Instruction: {instruction}\n### Response: {response}\n### {rubric}\n### Score:"

def extract_score(text, variant):
    t = text.strip()
    if variant == "letter":
        m = re.search(r'\b([ABCDEabcde])\b', t)
        if m: return " ABCDE".index(m.group(1).upper())
        nums = re.findall(r'[1-5]', t)
        return int(nums[0]) if nums else 3
    elif variant == "descriptive":
        t_lower = t.lower()
        if "excellent" in t_lower: return 5
        if "good" in t_lower: return 4
        if "average" in t_lower or "acceptable" in t_lower or "fair" in t_lower: return 3
        if "poor" in t_lower or "bad" in t_lower: return 2
        if "terrible" in t_lower or "very poor" in t_lower: return 1
        nums = re.findall(r'[1-5]', t)
        return int(nums[0]) if nums else 3
    else:
        nums = re.findall(r'[1-5]', t)
        return int(nums[0]) if nums else 3

# ── Probes ──
PROBES = [
    ("rubric_order", ["normal","reversed","random"]),
    ("score_id", ["numeric","letter","descriptive"]),
    ("reference_answer", ["no_ref","good_ref","poor_ref"]),
]

def get_build_fn(pt, vn):
    def bp(vn_, it):
        iid, dom, inst, resp = it
        rubric = RUBRIC_NORMAL
        if pt == "rubric_order":
            if vn_ == "normal": rubric = RUBRIC_NORMAL
            elif vn_ == "reversed": rubric = RUBRIC_REVERSED
            elif vn_ == "random": rubric = RUBRIC_RANDOM
        use_resp = resp
        if pt == "reference_answer":
            if vn_ == "good_ref": use_resp = f"[Example of a good answer]\n{resp}"
            elif vn_ == "poor_ref": use_resp = f"[Example of a poor answer]\n{resp}"
        return build_prompt(rubric, inst, use_resp)
    return bp(vn)

def get_gs(pt, vn):
    if pt == "rubber_order": return lambda t: int(t.strip()[:1]) if t.strip()[:1] in "12345" else 3
    return lambda t: 3  # placeholder — real dispatch below

# ── Models (12 families, base+instruct pairs) ──
MODELS = [
    ("meta-llama/Llama-3.2-1B", "Llama3.2-1B"),
    ("meta-llama/Llama-3.2-1B-Instruct", "Llama3.2-1B-IT"),
    ("meta-llama/Llama-3.2-3B", "Llama3.2-3B"),
    ("meta-llama/Llama-3.2-3B-Instruct", "Llama3.2-3B-IT"),
    ("Qwen/Qwen2.5-0.5B", "Qwen2.5-0.5B"),
    ("Qwen/Qwen2.5-0.5B-Instruct", "Qwen2.5-0.5B-IT"),
    ("Qwen/Qwen2.5-1.5B", "Qwen2.5-1.5B"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen2.5-1.5B-IT"),
    ("google/gemma-2-2b", "Gemma2-2B"),
    ("google/gemma-2-2b-it", "Gemma2-2B-IT"),
    ("google/gemma-2-9b", "Gemma2-9B"),
    ("google/gemma-2-9b-it", "Gemma2-9B-IT"),
    ("mistralai/Mistral-7B-v0.3", "Mistral-7B"),
    ("mistralai/Mistral-7B-Instruct-v0.3", "Mistral-7B-IT"),
    ("meta-llama/Llama-3.1-8B", "Llama3.1-8B"),
    ("meta-llama/Llama-3.1-8B-Instruct", "Llama3.1-8B-IT"),
    ("Qwen/Qwen2.5-72B", "Qwen2.5-72B"),
    ("Qwen/Qwen2.5-72B-Instruct", "Qwen2.5-72B-IT"),
    ("mistralai/Mixtral-8x7B-v0.1", "Mixtral-8x7B"),
    ("mistralai/Mixtral-8x7B-Instruct-v0.1", "Mixtral-8x7B-IT"),
]

# ── Main ──
CK = "/kaggle/working/12fam_ck.json"
OT = "/kaggle/working/12fam_results.json"

key = os.environ.get("OPENROUTER_KEY", "")
if not key:
    key = input("Enter OpenRouter API key: ").strip()

client = OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")

all_r = {}
done = set()
total_cost = 0.0

if os.path.exists(CK):
    with open(CK) as f:
        cp = json.load(f)
    all_r = cp.get("r", {})
    done = set(cp.get("d", []))
    print(f"Resumed: {len(done)} models done")

def call_model(mid, prompt):
    global total_cost
    try:
        r = client.chat.completions.create(
            model=mid,
            messages=[{"role":"user","content":prompt}],
            max_tokens=5,
            temperature=0.0,
            timeout=15,
            stop=["\n", "###"]
        )
        out = r.choices[0].message.content.strip()
        # Track cost
        if hasattr(r, 'usage') and r.usage:
            total_cost += (r.usage.prompt_tokens * 0.90e-6 + r.usage.completion_tokens * 0.90e-6)
        return out
    except Exception as e:
        return None

for idx in range(0, len(MODELS), 2):
    base_name = MODELS[idx][1]
    pair_name = base_name[:base_name.rfind("-")] if "-" in base_name else base_name
    
    for mid, nm in [MODELS[idx], MODELS[idx+1]]:
        if nm in done:
            print(f"  [{nm}] SKIP (checkpointed)")
            continue
        
        print(f"\n[{nm}] ", end="", flush=True)
        rs = {}
        for pt, pv in PROBES:
            rs[pt] = {}
            for vn in pv:
                scores = []
                for it in ITEMS:
                    # Build prompt for this probe variant
                    rubric = NUMERIC_RUBRIC
                    if pt == "rubric_order":
                        if vn == "reversed": rubric = "Score from 1-5 (where 1 is best, 5 is worst)"
                        elif vn == "random": rubric = "Score from 1-5 (where 5 is average, labels mixed)"
                    elif pt == "score_id":
                        if vn == "letter": rubric = LETTER_RUBRIC
                        elif vn == "descriptive": rubric = DESCRIPTIVE_RUBRIC
                    
                    resp = it[3]
                    if pt == "reference_answer":
                        if vn == "good_ref": resp = f"[Good answer example]\n{it[3]}"
                        elif vn == "poor_ref": resp = f"[Poor answer example]\n{it[3]}"
                    
                    prompt = build_prompt(rubric, it[2], resp)
                    text = call_model(mid, prompt)
                    score = extract_score(text or "3", vn)
                    scores.append(score)
                    if len(scores) % 10 == 0:
                        print(".", end="", flush=True)
                rs[pt][vn] = scores
                avg = sum(scores) / max(len(scores), 1)
                print(f" {vn[:3]}={avg:.1f}", end="", flush=True)
            print()
        
        all_r[nm] = rs
        done.add(nm)
        with open(CK, "w") as f:
            json.dump({"r": all_r, "d": list(done)}, f)
        time.sleep(0.3)

with open(OT, "w") as f:
    json.dump(all_r, f)
print(f"\nDONE. Saved to {OT}")
print(f"Total API cost: ${total_cost:.4f}")
print(f"Models completed: {len(done)}/{len(MODELS)}")
