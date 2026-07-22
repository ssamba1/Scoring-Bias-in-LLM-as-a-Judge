#!/usr/bin/env python3
"""Auto-retry: submit to Kaggle until T4 GPU allocated, then run the full notebook."""
import json, os, sys, subprocess, time, shutil
from pathlib import Path

KAGGLE_TOKEN = "KGAT_REDACTED_REVOKED"
KERNEL_NAME = "sb-t4-run"
KERNEL_DIR = Path(r"C:\Users\Admin\Research\research-draft\infrastructure\kaggle_kernels") / KERNEL_NAME
NOTEBOOK_SRC = Path(r"C:\Users\Admin\Research\research-draft\infrastructure\scoring_bias_final_colab.ipynb")

def k(args):
    env = os.environ.copy()
    env["KAGGLE_API_TOKEN"] = KAGGLE_TOKEN
    return subprocess.run(["python3", "-m", "kaggle"] + args, capture_output=True, text=True, timeout=60, env=env)

def submit():
    r = k(["kernels", "push", "-p", str(KERNEL_DIR), "--accelerator", "GPU_T4"])
    return r.returncode == 0

def poll(timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        r = k(["kernels", "status", f"sricharansamba/{KERNEL_NAME}"])
        if r.returncode == 0:
            s = r.stdout.strip()
            if "COMPLETE" in s: return "DONE"
            if "ERROR" in s: return "FAIL"
            if "RUNNING" in s or "QUEUED" in s:
                elapsed = int(time.time() - start)
                print(f"  [{elapsed}s] running...", end="\r")
        time.sleep(30)
    return "TIMEOUT"

def check_gpu():
    out_dir = KERNEL_DIR / "output"
    logs = list(out_dir.glob("*.log"))
    if not logs: return None
    with open(logs[0]) as f:
        c = f.read()
    if "Tesla T4" in c: return "T4"
    if "Tesla P100" in c: return "P100"
    return None

def fetch_output():
    k(["kernels", "output", f"sricharansamba/{KERNEL_NAME}", "--path", str(KERNEL_DIR / "output")])

# Setup kernel directory
KERNEL_DIR.mkdir(parents=True, exist_ok=True)
if not (KERNEL_DIR / f"{KERNEL_NAME}.ipynb").exists():
    shutil.copy(NOTEBOOK_SRC, KERNEL_DIR / f"{KERNEL_NAME}.ipynb")
    meta = {"id": f"sricharansamba/{KERNEL_NAME}", "title": "SB T4 Run",
            "code_file": f"{KERNEL_NAME}.ipynb", "language": "python",
            "kernel_type": "notebook", "is_private": True, "enable_gpu": True,
            "enable_tpu": False, "enable_internet": True, "dataset_sources": [],
            "competition_sources": [], "kernel_sources": [], "model_sources": []}
    with open(KERNEL_DIR / "kernel-metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

max_attempts = int(sys.argv[1]) if len(sys.argv) > 1 else 20

for attempt in range(1, max_attempts + 1):
    print(f"\n=== Attempt {attempt}/{max_attempts} ===")

    # Wait for quota
    r = k(["kernels", "push", "-p", str(KERNEL_DIR), "--accelerator", "GPU_T4"])
    while r.returncode != 0 and "quota" in r.stderr.lower():
        print(f"  Quota full, waiting 60s...")
        time.sleep(60)
        r = k(["kernels", "push", "-p", str(KERNEL_DIR), "--accelerator", "GPU_T4"])

    if r.returncode != 0:
        print(f"  Submit failed: {r.stderr[:100]}")
        continue

    print(f"  Submitted! Waiting up to 10min...")
    result = poll(timeout=600)
    fetch_output()
    gpu = check_gpu()
    print(f"  GPU: {gpu}  |  Result: {result}")

    if gpu == "T4":
        print(f"\n✅ T4 on attempt {attempt}!")
        sys.exit(0 if result == "DONE" else 1)

    time.sleep(10)

print(f"\n❌ No T4 after {max_attempts} attempts")
