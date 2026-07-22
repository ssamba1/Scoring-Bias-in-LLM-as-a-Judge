# Hardware Requirements

## Minimum (Local CPU)
- 8GB RAM
- 4 CPU cores
- Python 3.11+
- Internet connection for API models

## Recommended (Local GPU)
- 16GB RAM
- NVIDIA T4 (16GB VRAM) or better
- CUDA 12.1+
- 50GB free disk for model cache

## Cloud
- OpenRouter API: No GPU. $0-3 total cost.
- Kaggle T4 GPU: Free. 30 hours/week limit.
- Colab T4 GPU: Free. 12 hours continuous.

## Expected Runtime

| Experiment | Platform | Time |
|-----------|----------|------|
| 3 models (local CPU) | Local | ~30 min |
| 27 models (API) | OpenRouter | ~4-8 hours |
| 44 families (GPU) | Kaggle T4 | ~30 hours |
| Full analysis pipeline | Local | ~5 min |
