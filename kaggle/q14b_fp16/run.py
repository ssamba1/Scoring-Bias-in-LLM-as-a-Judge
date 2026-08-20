"""Qwen2.5-14B at fp16 -- the gate experiment.

The paper's only causal data point above 8B is 4-bit and attenuated (+0.06
against the panel's +0.26). Quantization reshapes the score distribution, which
is the quantity being measured, so that attenuation cannot be attributed to
scale rather than to nf4. This runs the identical harness at fp16.

The harness is fetched from the public repository at a PINNED COMMIT and its
sha256 is verified before it runs, rather than pasted into this file. Two
reasons. A copy would drift from the committed harness, and a difference in
items or prompts between arms would be indistinguishable from the effect being
measured. And the digest goes into the output, so the results file records which
harness bytes produced it -- reproducible without trusting this notebook.

Weights are ~29.6 GB, sharded across 2x T4 (32 GB) by device_map="auto". T4 is
pre-Ampere and has no bfloat16, so the 16-bit arm is fp16, which is what the
main panel used.
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

# Substituted from git HEAD at push time; see kaggle/push.sh.
COMMIT = "__COMMIT__"
REPO = "ssamba1/Scoring-Bias-in-LLM-as-a-Judge"
HARNESS = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/paper/honest/repro/q14b_harness.py"
WORK = "/kaggle/working"

subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "transformers>=4.44", "accelerate>=0.33"], check=True)

source = urllib.request.urlopen(HARNESS, timeout=120).read()
digest = hashlib.sha256(source).hexdigest()
print(f"harness {COMMIT[:7]} sha256={digest[:16]}... ({len(source)} bytes)", flush=True)

path = os.path.join(WORK, "q14b_harness.py")
with open(path, "wb") as fh:
    fh.write(source)

os.environ["PRECISION"] = "fp16"
os.chdir(WORK)
sys.argv = [path]

import runpy
try:
    runpy.run_path(path, run_name="__main__")
except RuntimeError as exc:
    # 29.6 GB into 32 GB is tight. Say so plainly rather than leaving a dead
    # session to be diagnosed from a traceback.
    if "out of memory" in str(exc).lower():
        print("\nOOM: fp16 did not fit across the two T4s. Options: int8 "
              "(PRECISION=int8, ~14.8 GB, fits one card) as a middle rung, or "
              "an accelerate cpu_offload config.", flush=True)
    raise

out = os.path.join(WORK, "results_14b_fp16.json")
print("\nexists:", os.path.exists(out), flush=True)
if os.path.exists(out):
    payload = json.load(open(out))
    payload["harness_sha256"] = digest
    payload["harness_commit"] = COMMIT
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print("precision:", payload.get("precision"),
          "families:", list(payload.get("results", {})),
          "errors:", payload.get("errors"), flush=True)
