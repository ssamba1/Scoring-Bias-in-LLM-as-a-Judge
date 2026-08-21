"""Qwen2.5-14B at int8 -- the gate experiment, sized to the hardware.

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

The fp16 arm needed ~29.6 GB and was written for 2x T4. Kaggle silently
ignored the accelerator request -- the pushed kernel came back with
machine_shape "Gpu", a single card -- so device_map="auto" offloaded most of
the model to CPU RAM and the run crawled for hours without failing.

int8 is ~14.8 GB and fits one 16 GB card outright. It answers a slightly
different question, and a useful one: the committed 14B point is nf4, so
comparing int8 against it isolates quantization SEVERITY. If the attenuation
eases at int8, quantization is driving it; if it persists, that points at
scale, which is the thing the paper is scoped on.
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

os.environ["PRECISION"] = "int8"
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

out = os.path.join(WORK, "results_14b_int8.json")
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
