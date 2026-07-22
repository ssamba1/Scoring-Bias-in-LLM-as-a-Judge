"""
Kaggle automated notebook submission + monitoring for GPU experiments.
Usage:
  python kaggle_auto.py submit <notebook_name>  # Submit and run
  python kaggle_auto.py status <notebook_name>  # Check status
  python kaggle_auto.py output <notebook_name>  # Download results
  python kaggle_auto.py poll <notebook_name>    # Poll until complete
  python kaggle_auto.py full-run <notebook_name> # Submit → wait → download
  python kaggle_auto.py create <name>            # Write notebook from stdin
"""
import json, os, sys, subprocess, time, re, datetime
from pathlib import Path

KAGGLE_USERNAME = None
ROOT = Path(r'C:\Users\Admin\Research\research-draft')
KERNELS_DIR = ROOT / 'infrastructure' / 'kaggle_kernels'
RESULTS_DIR = ROOT / 'results_rootcause'



def get_username():
    """Auto-detect Kaggle username from API."""
    result = subprocess.run(
        ['python3', '-m', 'kaggle', 'kernels', 'list', '--mine'],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if '/' in line:
                parts = line.strip().split()
                if parts and '/' in parts[0]:
                    return parts[0].split('/')[0]
    return None

def kaggle_cmd(args):
    """Run kaggle CLI command."""
    env = os.environ.copy()
    env['KAGGLE_API_TOKEN'] = 'KGAT_REDACTED_REVOKED'
    return subprocess.run(
        ['python3', '-m', 'kaggle'] + args,
        capture_output=True, text=True, timeout=300, env=env
    )

def load_auth():
    """Auto-detect username. Returns (username, True/False)."""
    global KAGGLE_USERNAME
    username = get_username()
    if username:
        KAGGLE_USERNAME = username
        return username, True
    return None, False

def make_notebook(cells, metadata=None):
    """Create a Kaggle-compatible .ipynb from cell code strings.
    Must include execution_count and outputs for Kaggle API to accept."""
    default_metadata = {
        "kernelspec": {
            "language": "python",
            "display_name": "Python 3",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.13",
            "mimetype": "text/x-python",
            "codemirror_mode": {"name": "ipython", "version": 3},
            "pygments_lexer": "ipython3",
            "nbconvert_exporter": "python",
            "file_extension": ".py"
        },
        "kaggle": {
            "accelerator": "GPU",
            "dataSources": [],
            "dockerImageVersionId": 28755,
            "isInternetEnabled": True,
            "isGpuEnabled": True,
            "language": "python",
            "sourceType": "notebook"
        }
    }
    if metadata:
        default_metadata.update(metadata)

    nb = {
        "cells": [],
        "metadata": default_metadata,
        "nbformat": 4,
        "nbformat_minor": 0
    }

    for i, cell_code in enumerate(cells):
        source_lines = cell_code.split('\n')
        if source_lines and source_lines[0] == '':
            source_lines = source_lines[1:]
        source_lines = [l + '\n' for l in source_lines]

        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"id": f"cell_{i}"},
            "outputs": [],
            "source": source_lines
        })

    return nb

    return nb

def write_kernel_metadata(name, title=None):
    """Write kernel-metadata.json for a Kaggle kernel."""
    title = title or name.replace('_', ' ').title()
    metadata = {
        "id": f"{KAGGLE_USERNAME}/{name}",
        "title": title,
        "code_file": f"{name}.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": []
    }
    with open(KERNELS_DIR / name / 'kernel-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

def submit(name):
    """Create kernel directory, write files, and push to Kaggle."""
    kernel_dir = KERNELS_DIR / name
    kernel_dir.mkdir(parents=True, exist_ok=True)

    nb_file = kernel_dir / f'{name}.ipynb'
    meta_file = kernel_dir / 'kernel-metadata.json'

    if not nb_file.exists():
        print(f'❌ Notebook not found: {nb_file}')
        return False
    if not meta_file.exists():
        print(f'❌ Metadata not found: {meta_file}')
        return False

    print(f'🚀 Pushing {name} to Kaggle...')
    result = kaggle_cmd(['kernels', 'push', '-p', str(kernel_dir)])
    if result.returncode == 0:
        print(f'✅ Submitted: {name}')
        print(f'   Status: https://www.kaggle.com/code/{KAGGLE_USERNAME}/{name}')
        return True
    else:
        print(f'❌ Push failed: {result.stderr}')
        # Common fix: try pulling existing kernel first
        if 'already exists' in result.stderr.lower():
            print('   → Kernel exists, pulling then pushing...')
            kaggle_cmd(['kernels', 'pull', f'{KAGGLE_USERNAME}/{name}', '-p', str(kernel_dir)])
            result = kaggle_cmd(['kernels', 'push', '-p', str(kernel_dir)])
            if result.returncode == 0:
                print(f'✅ Updated: {name}')
                return True
        return False

def status(name):
    """Check kernel status."""
    result = kaggle_cmd(['kernels', 'status', f'{KAGGLE_USERNAME}/{name}'])
    if result.returncode == 0:
        status_str = result.stdout.strip()
        print(f'📊 {name}: {status_str}')
        return status_str
    else:
        print(f'❌ Status check failed: {result.stderr}')
        return None

def poll(name, interval=60, timeout=7200):
    """Poll kernel status until complete or timeout."""
    start = time.time()
    states_seen = set()

    while time.time() - start < timeout:
        s = status(name)
        if s:
            states_seen.add(s)
            elapsed = int(time.time() - start)
            elapsed_str = str(datetime.timedelta(seconds=elapsed))

            if 'complete' in s.lower() or 'succeeded' in s.lower():
                print(f'\n✅ Complete after {elapsed_str}!')
                return True
            elif 'error' in s.lower() or 'failed' in s.lower():
                print(f'\n❌ Failed after {elapsed_str}: {s}')
                return False
            elif 'cancel' in s.lower() or 'queued' in s.lower() or 'running' in s.lower():
                print(f'  ⏳ {elapsed_str} — {s}', end='\r')

        time.sleep(interval)

    print(f'\n⏰ Timeout after {timeout}s')
    return None

def output(name):
    """Download kernel output."""
    out_dir = KERNELS_DIR / name / 'output'
    out_dir.mkdir(parents=True, exist_ok=True)
    result = kaggle_cmd(['kernels', 'output', f'{KAGGLE_USERNAME}/{name}', '--path', str(out_dir)])
    if result.returncode == 0:
        print(f'✅ Output downloaded to {out_dir}')
        return True
    else:
        print(f'❌ Download failed: {result.stderr}')
        return False

def write_and_submit(name, cells, metadata=None, accelerator=None):
    """Single command: write notebook, submit, and return. Optional accelerator flag."""
    kernel_dir = KERNELS_DIR / name
    kernel_dir.mkdir(parents=True, exist_ok=True)

    nb = make_notebook(cells, metadata)
    nb_file = kernel_dir / f'{name}.ipynb'
    with open(nb_file, 'w') as f:
        json.dump(nb, f, indent=1)

    write_kernel_metadata(name)

    if accelerator:
        result = kaggle_cmd(['kernels', 'push', '-p', str(kernel_dir), '--accelerator', accelerator])
        if result.returncode == 0:
            print(f'✅ Submitted: {name} (accelerator={accelerator})')
            print(f'   Status: https://www.kaggle.com/code/{KAGGLE_USERNAME}/{name}')
            return True
        else:
            print(f'❌ Push failed: {result.stderr}')
            return False
    return submit(name)

# Auto-detect on import
if not KAGGLE_USERNAME:
    u = get_username()
    if u:
        KAGGLE_USERNAME = u

if __name__ == '__main__':
    # Auto-detect username if not set
    if not KAGGLE_USERNAME:
        u = get_username()
        if u:
            KAGGLE_USERNAME = u

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'auth':
        username, ok = load_auth()
        if ok:
            print(f'✅ Authenticated as {username}')
        else:
            print('❌ Auth failed — check KAGGLE_API_TOKEN')
            sys.exit(1)

    elif cmd == 'submit':
        if len(sys.argv) < 3:
            print('Usage: python kaggle_auto.py submit <name>')
            sys.exit(1)
        if not KAGGLE_USERNAME: load_auth()
        submit(sys.argv[2])

    elif cmd == 'status':
        if len(sys.argv) < 3:
            print('Usage: python kaggle_auto.py status <name>')
            sys.exit(1)
        if not KAGGLE_USERNAME: load_auth()
        status(sys.argv[2])

    elif cmd == 'output':
        if len(sys.argv) < 3:
            print('Usage: python kaggle_auto.py output <name>')
            sys.exit(1)
        if not KAGGLE_USERNAME: load_auth()
        output(sys.argv[2])

    elif cmd == 'poll':
        if len(sys.argv) < 3:
            print('Usage: python kaggle_auto.py poll <name> [interval_sec]')
            sys.exit(1)
        if not KAGGLE_USERNAME: load_auth()
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        poll(sys.argv[2], interval)

    elif cmd == 'full-run':
        if len(sys.argv) < 3:
            print('Usage: python kaggle_auto.py full-run <name>')
            sys.exit(1)
        if not KAGGLE_USERNAME: load_auth()
        name = sys.argv[2]
        if submit(name):
            success = poll(name, interval=60)
            if success:
                output(name)
        print(f'\nLogs: {KERNELS_DIR / name}')

    elif cmd == 'list':
        result = kaggle_cmd(['kernels', 'list', '--mine'])
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f'❌ Failed: {result.stderr}')

    else:
        print(f'Unknown command: {cmd}')
        print(__doc__)
