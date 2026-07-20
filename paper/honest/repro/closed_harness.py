#!/usr/bin/env python3
"""
Closed / frontier-model harness (C10) -- extends the study to API-only judges
(GPT-4o-class, Claude, Gemini, ...) via OpenRouter token logprobs.

The mechanism needs the judge's score DISTRIBUTION, not just a written score. Many
chat APIs expose top-k logprobs; we prompt for a single score token, read the
logprobs over the valid answer tokens {1..5}, and recover the same expected-value
score s and entropy H(sigma) used for the open-weight models. The identical
analysis (analyze_mechanism.py) then tests whether the negative decisiveness<->bias
relation holds for frontier closed judges too.

Requires an API key with logprob support:
    export OPENROUTER_API_KEY=...            # or OPENAI_API_KEY with base_url swap
Cost: a few US$ for the models below at 50 items x 5 probes x 3 variants.
NOT run automatically -- it spends money. Run it yourself:  python closed_harness.py

Output: results_closed.json (same schema as results_scaled.json -> feeds analyze_mechanism.py)
NOTE: closed models have no "base" checkpoint, so this tests the cross-sectional
decisiveness<->bias law across judges, not the base-vs-instruct delta.
"""
from __future__ import annotations
import os, json, math, time
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("pip install requests")

API_KEY = os.environ.get("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
HERE = Path(__file__).resolve().parent

# judge models with logprob support (edit as availability changes)
MODELS = [
    "openai/gpt-4o-mini", "openai/gpt-4o", "meta-llama/llama-3.1-70b-instruct",
    "qwen/qwen-2.5-72b-instruct",
]
NUM = ["1", "2", "3", "4", "5"]; LET = ["A", "B", "C", "D", "E"]; DESC = ["Poor", "Fair", "Good", "Great", "Excellent"]
NUM_SCALE = "on a scale of 1 to 5, where 1 is worst and 5 is best"
PROBES = {
    "rubric_order": {"control": (NUM_SCALE, NUM), "reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst", NUM), "random": ("on a scale of 1 to 5 (3=worst,5=middle,1=best)", NUM)},
    "score_id": {"numeric": (NUM_SCALE, NUM), "letter": ("with a letter grade A to E, where A is best and E is worst", LET), "descriptive": ("as one of: Poor, Fair, Good, Great, Excellent", DESC)},
    "reference_answer": {"none": (NUM_SCALE, NUM), "good": (NUM_SCALE, NUM), "poor": (NUM_SCALE, NUM)},
    "authority": {"none": (NUM_SCALE, NUM), "expert": (NUM_SCALE, NUM), "novice": (NUM_SCALE, NUM)},
    "verbosity": {"control": (NUM_SCALE, NUM), "verbose": (NUM_SCALE, NUM), "terse": (NUM_SCALE, NUM)},
}
PREFIX = {"good": "For reference, an excellent answer would be thorough and precise.\n",
          "poor": "For reference, a poor answer would be vague or wrong.\n",
          "expert": "The following response was written by a leading domain expert.\n",
          "novice": "The following response was written by a struggling beginner.\n"}
_FILLER = " To elaborate, this is a rich topic worth considering from several angles."
ITEMS = json.loads((HERE.parents[2] / "data" / "combined_80_items.json").read_text())[:50]


def vals(a): return list(range(5, 0, -1)) if a is LET else [1, 2, 3, 4, 5]


def transform(probe, variant, resp):
    if probe == "verbosity" and variant == "verbose": return resp + _FILLER + _FILLER
    if probe == "verbosity" and variant == "terse": return (resp.split(".")[0] or resp).strip() + "."
    return resp


def build(instr, resp, scale, prefix):
    return (f"{prefix}Evaluate the following response to the instruction {scale}. "
            f"Reply with only the score.\nInstruction: {instr}\nResponse: {resp}\nScore:")


def score_api(model, prompt, answer_tokens):
    r = requests.post(BASE_URL, headers={"Authorization": f"Bearer {API_KEY}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 1, "temperature": 0, "logprobs": True, "top_logprobs": 20},
                      timeout=30)
    r.raise_for_status()
    top = r.json()["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    lp = {d["token"].strip(): d["logprob"] for d in top}
    probs = []
    for a in answer_tokens:
        probs.append(math.exp(lp[a]) if a in lp else 0.0)
    z = sum(probs) or 1e-9
    probs = [p / z for p in probs]
    v = vals(answer_tokens)
    exp = sum(p * vi for p, vi in zip(probs, v))
    ent = -sum(p * math.log2(p) for p in probs if p > 0)
    return round(exp, 4), round(ent, 4), max(1, min(5, round(exp)))


def main():
    if not API_KEY:
        raise SystemExit("Set OPENROUTER_API_KEY. This harness spends money; run it deliberately.")
    payload = {"models": MODELS, "errors": {}, "results": {}}
    for model in MODELS:
        rec = {"instruct": {}}   # closed models are instruct-only
        for probe, variants in PROBES.items():
            rec["instruct"][probe] = {}
            for variant, (scale, atok) in variants.items():
                exp, ent, arg = [], [], []
                for it in ITEMS:
                    p = build(it["instr"], transform(probe, variant, it["resp"]), scale, PREFIX.get(variant, ""))
                    try:
                        e, h, a = score_api(model, p, atok)
                    except Exception as ex:
                        payload["errors"].setdefault(model, str(ex)); continue
                    exp.append(e); ent.append(h); arg.append(a); time.sleep(0.05)
                if exp:
                    n = len(exp)
                    rec["instruct"][probe][variant] = {"per_item": exp, "per_item_argmax": arg,
                        "per_item_entropy": ent, "mean": round(sum(exp)/n, 4),
                        "mean_entropy": round(sum(ent)/n, 4)}
        payload["results"][model.split("/")[-1]] = rec
        (HERE / "results_closed.json").write_text(json.dumps(payload, indent=2))
        print("done", model, flush=True)
    print("WROTE results_closed.json")


if __name__ == "__main__":
    main()
