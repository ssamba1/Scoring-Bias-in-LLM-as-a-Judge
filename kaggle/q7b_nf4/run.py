"""Qwen2.5-7B at nf4 -- the quantization control.

The paper's only causal point above 8B is a 4-bit 14B run, attenuated to +0.06
against the panel's +0.26. Nothing in the project says how much of that is
quantization, because the 14B has no fp16 counterpart and cannot get one: fp16
needs ~29.6 GB and Kaggle grants a single 16 GB card.

Qwen2.5-7B does have one. It is in the main panel at fp16, scored on these exact
items by this exact harness, so running it at nf4 differences the quantization
effect directly instead of assuming it.

Panel reference (fp16): base mean bias 0.3312, instruct 0.8747, delta +0.5436.
If nf4 shrinks that delta materially, the 14B attenuation is a quantization
artefact and the paper's scale claim rests on nothing. If it barely moves, the
attenuation is more likely real and the scope limit is genuine.

Hardware note. int8 was tried first and failed on both checkpoints with a
cublasLt error: bitsandbytes LLM.int8 needs compute capability 7.5+, and Kaggle
gave a Tesla P100 (6.0). 4-bit uses different kernels and does work there -- the
committed 14B nf4 run was itself produced on a P100. So nf4 is the arm this
hardware can actually run, and it happens to be the one with a reference.
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

# bitsandbytes is required for load_in_8bit and is NOT in the fp16 arm's list,
# which needed no quantizer. Without it the harness raises on model load after
# the weights have already been downloaded.
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "transformers>=4.44", "accelerate>=0.33",
                "bitsandbytes>=0.43"], check=True)

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

os.environ["PRECISION"] = "nf4"
os.environ["QUANT_MODEL"] = "qwen7b"
os.chdir(WORK)
sys.argv = [path]

import runpy
try:
    runpy.run_path(path, run_name="__main__")
except RuntimeError as exc:
    # nf4 Qwen2.5-7B is about 4 GB and fits any Kaggle GPU with room to spare,
    # so an OOM here would mean something other than model size and should not
    # be diagnosed from a traceback alone.
    if "out of memory" in str(exc).lower():
        print("\nOOM on a ~4 GB model: not a capacity problem. Check whether a "
              "previous model was left resident, or whether device_map placed "
              "activations badly.", flush=True)
    raise

out = os.path.join(WORK, "results_7b_nf4.json")
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
