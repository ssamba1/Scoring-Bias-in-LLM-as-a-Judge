#!/usr/bin/env python3
"""Upload dataset to HuggingFace Hub.
Requires: pip install huggingface_hub
Usage: HF_TOKEN=hf_... python3 pipeline_rootcause/upload_dataset.py
"""
import json, os
from pathlib import Path
from huggingface_hub import HfApi, DatasetCard

# Load all results
DATA_DIR = Path(__file__).parent.parent / "results_rootcause"

# Merge T4 + OpenRouter + Kaggle
all_data = {}
for path in ["t4fam_results.json", "study1_results.json"]:
    p = DATA_DIR / path
    if p.exists():
        with open(p) as f:
            all_data.update(json.load(f))

api = HfApi(token=os.environ.get("HF_TOKEN", ""))

# Create dataset repo
repo_id = "ssamba1/scoring-bias-llm-judge"
try:
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    print(f"Created/verified repo: {repo_id}")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Upload data file
api.upload_file(
    path_or_fileobj=json.dumps(all_data, indent=2).encode(),
    path_in_repo="data.json",
    repo_id=repo_id,
    repo_type="dataset",
)
print(f"Uploaded data.json ({len(all_data)} models, {len(json.dumps(all_data))} bytes)")

# Upload README
api.upload_file(
    path_or_fileobj=Path(DATA_DIR.parent / "data" / "dataset_card.md").read_bytes(),
    path_in_repo="README.md",
    repo_id=repo_id,
    repo_type="dataset",
)

print(f"\nDataset: https://huggingface.co/datasets/{repo_id}")
print("DONE.")
