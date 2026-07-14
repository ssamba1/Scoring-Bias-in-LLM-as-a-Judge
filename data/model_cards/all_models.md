# Model Cards — All 30 Variants

## NeurIPS Datasheet Format

---

### 1. Meta Llama 3.1 8B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Meta-Llama-3.1-8B` |
| **Parameters** | 8.03B |
| **Architecture** | Dense Transformer |
| **Training** | Base: pre-training only. Instruct: SFT + RLHF (PPO). |
| **Context** | 131K tokens |
| **License** | Llama 3.1 Community License |
| **Base Δ** | 2.10 |
| **Instruct Δ** | 1.20 |
| **Change** | −43% |

### 2. Meta Llama 3.2 3B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Llama-3.2-3B` |
| **Parameters** | 3.21B |
| **Architecture** | Dense Transformer |
| **Training** | Base: pre-training. Instruct: SFT + RLHF (PPO). |
| **Context** | 131K tokens |
| **License** | Llama 3.2 Community License |
| **Base Δ** | 2.45 |
| **Instruct Δ** | 1.53 |
| **Change** | −38% |

### 3. Meta Llama 2 7B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Llama-2-7b-hf` |
| **Parameters** | 6.74B |
| **Architecture** | Dense Transformer |
| **Training** | Base: pre-training. Instruct: SFT + RLHF (PPO). |
| **Context** | 4K tokens |
| **License** | Llama 2 Community License |
| **Base Δ** | 2.80 |
| **Instruct Δ** | 1.65 |
| **Change** | −41% |

### 4. Mistral 7B v0.3 (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `mistralai/Mistral-7B-v0.3` |
| **Parameters** | 7.24B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training** | Base: pre-training. Instruct: SFT + DPO. |
| **Context** | 32K tokens |
| **License** | Apache 2.0 |
| **Base Δ** | 2.05 |
| **Instruct Δ** | 1.87 |
| **Change** | −9% |

### 5. Qwen 2.5 0.5B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-0.5B` |
| **Parameters** | 0.49B |
| **Architecture** | Dense Transformer |
| **Context** | 32K tokens |
| **License** | Apache 2.0 |
| **Base Δ** | 3.20 |
| **Instruct Δ** | 2.40 |
| **Change** | −25% |

### 6. Qwen 2.5 1.5B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-1.5B` |
| **Parameters** | 1.54B |
| **Architecture** | Dense Transformer |
| **Context** | 32K tokens |
| **License** | Apache 2.0 |
| **Base Δ** | 2.90 |
| **Instruct Δ** | 2.10 |
| **Change** | −28% |

### 7. Qwen 2.5 7B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-7B` |
| **Parameters** | 7.63B |
| **Architecture** | Dense Transformer |
| **Training** | Base: pre-training. Instruct: SFT + RLHF. |
| **Context** | 128K tokens |
| **License** | Apache 2.0 |
| **Base Δ** | 2.30 |
| **Instruct Δ** | 1.50 |
| **Change** | −35% |

### 8. Qwen 3 8B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `qwen/qwen3-8b` |
| **Parameters** | 8.15B |
| **Architecture** | Dense Transformer + SwiGLU |
| **Training** | SFT + RLHF |
| **Context** | 128K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 1.30 |

### 9. Qwen 3 14B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `qwen/qwen3-14b` |
| **Parameters** | 14.18B |
| **Architecture** | Dense Transformer + SwiGLU |
| **Context** | 128K tokens |
| **Instruct Δ** | 1.10 |

### 10. Qwen 3 32B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `qwen/qwen3-32b` |
| **Parameters** | 32.76B |
| **Architecture** | Dense Transformer + SwiGLU |
| **Context** | 128K tokens |
| **Instruct Δ** | 1.00 |

### 11. Google Gemma 2 2B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-2-2b` |
| **Parameters** | 2.57B |
| **Architecture** | Dense Transformer (GQA) |
| **Context** | 8K tokens |
| **License** | Gemma License |
| **Base Δ** | 2.60 |
| **Instruct Δ** | 1.10 |
| **Change** | −58% |

### 12. Google Gemma 2 9B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-2-9b` |
| **Parameters** | 9.24B |
| **Architecture** | Dense Transformer (GQA) |
| **Context** | 8K tokens |
| **License** | Gemma License |
| **Base Δ** | 2.40 |
| **Instruct Δ** | 0.90 |
| **Change** | −63% |

### 13. Google Gemma 3 4B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-3-4b-it` |
| **Parameters** | 3.82B |
| **Architecture** | Dense + MoE |
| **Context** | 32K tokens |
| **Instruct Δ** | 1.40 |

### 14. Google Gemma 3 12B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-3-12b-it` |
| **Parameters** | 12.15B |
| **Architecture** | Dense + MoE |
| **Context** | 32K tokens |
| **Instruct Δ** | 1.30 |

### 15. Google Gemma 3 27B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-3-27b-it` |
| **Parameters** | 27.20B |
| **Architecture** | Dense + MoE |
| **Context** | 32K tokens |
| **Instruct Δ** | 1.50 |

### 16. Google Gemma 4 31B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-4-31b-it` |
| **Parameters** | 30.70B |
| **Architecture** | Dense Transformer |
| **Context** | 256K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 0.73 |

### 17. Microsoft Phi-4 (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `microsoft/phi-4` |
| **Parameters** | 14.68B |
| **Architecture** | Dense Transformer |
| **Context** | 128K tokens |
| **License** | MIT |
| **Instruct Δ** | 0.83 |

### 18. Mistral Nemo 12B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `mistralai/mistral-nemo` |
| **Parameters** | 12.0B |
| **Architecture** | Dense (GQA) |
| **Context** | 128K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 1.10 |

### 19. DeepSeek V3 (Chat)

| Field | Value |
|-------|-------|
| **Model ID** | `deepseek/deepseek-chat` |
| **Parameters** | 671B (37B active) |
| **Architecture** | MoE (256 experts) |
| **Context** | 128K tokens |
| **License** | DeepSeek License |
| **Instruct Δ** | 1.43 |

### 20. NVIDIA Nemotron Nano 30B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `nvidia/nemotron-3-nano-30b-a3b` |
| **Parameters** | 30B (3B active) |
| **Architecture** | MoE (Mamba-Transformer hybrid) |
| **Context** | 256K tokens |
| **License** | NVIDIA Open License |
| **Instruct Δ** | 0.70 |

### 21. NVIDIA Nemotron Super 120B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `nvidia/nemotron-3-super-120b-a12b` |
| **Parameters** | 120B (12B active) |
| **Architecture** | MoE (Mamba-Transformer hybrid) |
| **Context** | 1M tokens |
| **License** | NVIDIA Open License |
| **Instruct Δ** | 0.70 |

### 22. Hermes 3 70B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `nousresearch/hermes-3-llama-3.1-70b` |
| **Parameters** | 70.6B |
| **Architecture** | Dense Transformer |
| **Context** | 131K tokens |
| **License** | Llama 3.1 Community License |
| **Instruct Δ** | 1.90 |

### 23. Zephyr 7B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `HuggingFaceH4/zephyr-7b-beta` |
| **Parameters** | 7.24B |
| **Training** | SFT + DPO (on Mistral 7B) |
| **Context** | 32K tokens |
| **License** | MIT |
| **Instruct Δ** | 1.83 |

### 24. MythoMax 13B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `gryphe/mythomax-l2-13b` |
| **Parameters** | 12.9B |
| **Architecture** | Dense Transformer |
| **Context** | 4K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 1.87 |

### 25. SOLAR 10.7B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `upstage/solar-10.7b-instruct-v1.0` |
| **Parameters** | 10.7B |
| **Architecture** | Dense (depth-upscaled) |
| **Context** | 32K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 2.00 |

### 26. Command R7B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `cohere/command-r7b-12-2024` |
| **Parameters** | 7.0B |
| **Architecture** | Dense Transformer |
| **Context** | 128K tokens |
| **License** | CC-BY-NC |

### 27. Inflection 3 Pi (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `inflection/inflection-3-pi` |
| **Parameters** | 8.0B |
| **Architecture** | Dense |
| **Context** | 8K tokens |

### 28. Nemotron Super 120B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `nvidia/nemotron-3-super-120b-a12b` |
| **Parameters** | 120B (12B active) |
| **Instruct Δ** | 0.91 |

### 29. Hy3 295B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `tencent/hy3` |
| **Parameters** | 295B (21B active) |
| **Architecture** | MoE (192 experts, top-8) |
| **Context** | 256K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 0.53 |

### 30. GPT-OSS 20B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `openai/gpt-oss-20b` |
| **Parameters** | 21B (3.6B active) |
| **Architecture** | MoE |
| **Context** | 131K tokens |
| **License** | Apache 2.0 |
| **Instruct Δ** | 1.23 |
