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

# Both substituted at push time; see kaggle/push.sh.
#
# EXPECTED_SHA256 is the digest of the GIT BLOB, not of the working file: this
# repository is checked out with CRLF on Windows, and GitHub serves what git
# stores, which is LF. Hashing the working copy would produce a digest that
# never matches and a check that always fails.
COMMIT = "__COMMIT__"
EXPECTED_SHA256 = "__SHA256__"
REPO = "ssamba1/Scoring-Bias-in-LLM-as-a-Judge"
HARNESS = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/paper/honest/repro/q14b_harness.py"
WORK = "/kaggle/working"

subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "transformers>=4.44", "accelerate>=0.33"], check=True)

# Refuse before downloading 30 GB if the GPU cannot hold the model.
#
# The first run of this kernel asked for 2x T4 via "accelerator" in
# kernel-metadata.json. Kaggle ignored the field -- the pushed kernel came back
# with machine_shape "Gpu", one card -- and device_map="auto" responded by
# offloading most of the model to CPU RAM instead of raising. It crawled for two
# hours and produced nothing. A silently dropped config field turned a hard
# error into an indefinite one, which is far harder to notice than a crash.
#
# fp16 weights are ~29.6 GB. Check first, and say what to run instead.
import torch

if not torch.cuda.is_available():
    raise SystemExit("no CUDA device; this kernel needs a GPU accelerator")

total = sum(torch.cuda.get_device_properties(i).total_memory
            for i in range(torch.cuda.device_count())) / 1e9
names = ", ".join(torch.cuda.get_device_properties(i).name
                  for i in range(torch.cuda.device_count()))
print(f"visible GPUs: {names} ({total:.1f} GB total)", flush=True)

NEEDED_GB = 31.0   # ~29.6 GB of weights plus headroom
if total < NEEDED_GB:
    raise SystemExit(
        f"fp16 Qwen2.5-14B needs about {NEEDED_GB:.0f} GB and this session has "
        f"{total:.1f} GB. device_map='auto' would offload to CPU and run for "
        f"hours without failing, so stopping here instead.\n"
        f"Run the int8 arm (kaggle/q14b_int8, ~14.8 GB, fits one 16 GB card), "
        f"or obtain a genuine multi-GPU session -- note that the 'accelerator' "
        f"field in kernel-metadata.json did not take effect."
    )

source = urllib.request.urlopen(HARNESS, timeout=120).read()
digest = hashlib.sha256(source).hexdigest()
print(f"harness {COMMIT[:7]} sha256={digest[:16]}... ({len(source)} bytes)", flush=True)

# Recording a digest proves nothing on its own; it has to be compared against
# one fixed before the run. Without this the "pinned" harness is only pinned by
# hope -- a raw URL that resolved to something else would sail straight through
# and produce numbers attributed to a commit that did not generate them.
if digest != EXPECTED_SHA256:
    raise SystemExit(
        f"harness digest mismatch\n  expected {EXPECTED_SHA256}\n  got      {digest}\n"
        f"The pinned commit did not serve the bytes this kernel was built for. "
        f"Refusing to run rather than attribute results to the wrong harness."
    )
print("digest matches the pinned commit", flush=True)

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
