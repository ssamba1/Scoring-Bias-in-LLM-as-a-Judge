# Model Cards — All 31 Model Variants

## NeurIPS Datasheet Format

This document provides detailed model cards for all 31 model variants used in this study: 9 base models (pre-training only), 9 instruction-tuned versions of those base models, and 13 additional instruct-only models evaluated via the OpenRouter API. Each card reports the Hugging Face model ID, parameter count, architecture, training data, license, known biases, and study-specific bias metrics.

---

### 1. Meta Llama 3.1 8B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Meta-Llama-3.1-8B` (base), `meta-llama/Meta-Llama-3.1-8B-Instruct` (instruct) |
| **Parameters** | 8.03B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training data** | Base: ~15T tokens from publicly available sources (CommonCrawl, C4, GitHub, Wikipedia, books). Instruct: SFT on ~1M human-annotated examples + RLHF (PPO) with ~100K human preferences. |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF (PPO). |
| **Context window** | 131,072 tokens |
| **License** | Llama 3.1 Community License (gated access) |
| **Release date** | July 2024 |
| **Known biases** | Verbosity bias (prefers longer responses), position bias in pairwise comparisons, self-enhancement bias for Llama-generated responses |
| **Study metrics** | **Base Δ**: 0.60 rub, 0.20 ID, 0.60 ref — **Instruct Δ**: 0.60 rub, 0.60 ID, 0.80 ref |
| **Change** | Rubric: +0.50, Score ID: +0.40, Ref Answer: +0.20 |

---

### 2. Meta Llama 3.2 1B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Llama-3.2-1B` (base), `meta-llama/Llama-3.2-1B-Instruct` (instruct) |
| **Parameters** | 1.23B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training data** | Pre-trained on ~9T tokens. Instruct: SFT on ~500K examples + RLHF (PPO). |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF (PPO). |
| **Context window** | 131,072 tokens |
| **License** | Llama 3.2 Community License (gated access) |
| **Release date** | September 2024 |
| **Known biases** | Limited instruction following at 1B scale; higher susceptibility to format confusion; shows lower scoring variance overall |
| **Study metrics** | **Base Δ**: 0.00 rub, 1.30 ID, 2.20 ref — **Instruct Δ**: 0.20 rub, 2.00 ID, 2.60 ref |
| **Change** | Rubric: +0.20, Score ID: +0.70, Ref Answer: +0.40 |

---

### 3. Meta Llama 3.2 3B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Llama-3.2-3B` (base), `meta-llama/Llama-3.2-3B-Instruct` (instruct) |
| **Parameters** | 3.21B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training data** | Pre-trained on ~9T tokens. Instruct: SFT on ~1M examples + RLHF (PPO). |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF (PPO). |
| **Context window** | 131,072 tokens |
| **License** | Llama 3.2 Community License (gated access) |
| **Release date** | September 2024 |
| **Known biases** | Large rubric order bias in base variant (Δ=3.50), the highest observed among all models. Instruct variant shows dramatic improvement (Δ=0.80, -77%). |
| **Study metrics** | **Base Δ**: 3.50 rub, 3.70 ID, 3.10 ref — **Instruct Δ**: 0.80 rub, 2.40 ID, 2.50 ref |
| **Change** | Rubric: -2.70, Score ID: -1.30, Ref Answer: -0.60 |

---

### 4. Meta Llama 2 7B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `meta-llama/Llama-2-7b-hf` (base), `meta-llama/Llama-2-7b-chat-hf` (instruct) |
| **Parameters** | 6.74B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~2T tokens. Instruct: SFT on ~27K examples + RLHF (PPO). |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF (PPO). |
| **Context window** | 4,096 tokens |
| **License** | Llama 2 Community License (gated access) |
| **Release date** | July 2023 |
| **Known biases** | Position bias (documented), self-enhancement bias, limited context window restricts complex scoring tasks |
| **Study metrics** | **Base Δ**: 0.30 rub, 2.80 ID, 1.10 ref — **Instruct Δ**: 0.70 rub, 1.30 ID, 1.50 ref |
| **Change** | Rubric: +0.40, Score ID: -1.50, Ref Answer: +0.40 |

---

### 5. Mistral 7B v0.3 (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `mistralai/Mistral-7B-v0.3` (base), `mistralai/Mistral-7B-Instruct-v0.3` (instruct) |
| **Parameters** | 7.24B |
| **Architecture** | Dense Transformer (Grouped-Query Attention, Sliding Window Attention) |
| **Training data** | Pre-trained on publicly available data. Instruct: SFT on publicly available instruction datasets + DPO. |
| **Training method** | Base: pre-training only. Instruct: SFT + DPO. |
| **Context window** | 32,768 tokens |
| **License** | Apache 2.0 |
| **Release date** | May 2024 |
| **Known biases** | Strong self-enhancement bias; DPO training may reduce format bias less effectively than RLHF |
| **Study metrics** | **Base Δ**: 0.00 rub, 0.00 ID, 0.00 ref — **Instruct Δ**: 0.20 rub, 0.70 ID, 0.70 ref |
| **Change** | Rubric: +0.20, Score ID: +0.70, Ref Answer: +0.70 |

---

### 6. Qwen 2.5 0.5B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-0.5B` (base), `Qwen/Qwen2.5-0.5B-Instruct` (instruct) |
| **Parameters** | 0.49B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~18T tokens across 29 languages. Instruct: SFT on curated instruction data + RLHF. |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF. |
| **Context window** | 32,768 tokens |
| **License** | Apache 2.0 |
| **Release date** | September 2024 |
| **Known biases** | Very small model shows limited semantic understanding; high susceptibility to reference answer priming. Score ID bias improves substantially after instruction tuning. |
| **Study metrics** | **Base Δ**: 0.10 rub, 1.30 ID, 2.60 ref — **Instruct Δ**: 0.20 rub, 0.40 ID, 1.20 ref |
| **Change** | Rubric: +0.10, Score ID: -0.90, Ref Answer: -1.40 |

---

### 7. Qwen 2.5 1.5B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-1.5B` (base), `Qwen/Qwen2.5-1.5B-Instruct` (instruct) |
| **Parameters** | 1.54B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~18T tokens. Instruct: SFT on curated instruction data + RLHF. |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF. |
| **Context window** | 32,768 tokens |
| **License** | Apache 2.0 |
| **Release date** | September 2024 |
| **Known biases** | Very high base score ID bias (Δ=3.10) driven by letter grades (score 1.0 vs numeric 4.1). Instruction tuning reduces but does not eliminate this gap. |
| **Study metrics** | **Base Δ**: 0.10 rub, 3.10 ID, 2.60 ref — **Instruct Δ**: 0.40 rub, 1.80 ID, 1.80 ref |
| **Change** | Rubric: +0.30, Score ID: -1.30, Ref Answer: -0.80 |

---

### 8. Qwen 2.5 7B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-7B` (base), `Qwen/Qwen2.5-7B-Instruct` (instruct) |
| **Parameters** | 7.63B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~18T tokens. Instruct: SFT on curated instruction data + RLHF. |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF. |
| **Context window** | 131,072 tokens (32K for base) |
| **License** | Apache 2.0 |
| **Release date** | September 2024 |
| **Known biases** | Strong base model score ID bias; instruction tuning is the most effective of all Qwen2.5 sizes (Score ID: -2.10 Δ). Reference answer bias nearly eliminated in instruct variant. |
| **Study metrics** | **Base Δ**: 0.60 rub, 2.50 ID, 2.40 ref — **Instruct Δ**: 0.00 rub, 0.40 ID, 0.90 ref |
| **Change** | Rubric: -0.60, Score ID: -2.10, Ref Answer: -1.50 |

---

### 9. Google Gemma 2 2B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-2-2b` (base), `google/gemma-2-2b-it` (instruct) |
| **Parameters** | 2.57B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training data** | Pre-trained on ~6T tokens from web documents, code, and mathematical data. Instruct: SFT + RLHF. |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF. |
| **Context window** | 8,192 tokens |
| **License** | Gemma License (gated access) |
| **Release date** | June 2024 |
| **Known biases** | Moderate score ID bias in base variant; instruction tuning is highly effective for this model (-1.50 Δ for both Score ID and Reference Answer). |
| **Study metrics** | **Base Δ**: 0.10 rub, 2.10 ID, 2.60 ref — **Instruct Δ**: 0.10 rub, 0.60 ID, 1.10 ref |
| **Change** | Rubric: 0.00, Score ID: -1.50, Ref Answer: -1.50 |

---

### 10. Google Gemma 2 9B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-2-9b` (base), `google/gemma-2-9b-it` (instruct) |
| **Parameters** | 9.24B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training data** | Pre-trained on ~8T tokens. Instruct: SFT + RLHF. |
| **Training method** | Base: pre-training only. Instruct: SFT + RLHF. |
| **Context window** | 8,192 tokens |
| **License** | Gemma License (gated access) |
| **Release date** | June 2024 |
| **Known biases** | Moderate base bias across all probes. Instruction tuning produces consistent reductions in all three bias types. |
| **Study metrics** | **Base Δ**: 0.20 rub, 2.40 ID, 2.00 ref — **Instruct Δ**: 0.00 rub, 0.50 ID, 1.10 ref |
| **Change** | Rubric: -0.20, Score ID: -1.90, Ref Answer: -0.90 |

---

### 11. StableLM 2 1.6B (Base + Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `stabilityai/stablelm-2-1_6b` (base), `stabilityai/stablelm-2-1_6b-chat` (instruct) |
| **Parameters** | 1.64B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~2T tokens. Instruct: SFT only (no RLHF). |
| **Training method** | Base: pre-training only. Instruct: SFT only. |
| **Context window** | 4,096 tokens |
| **License** | Stability AI License |
| **Release date** | March 2024 |
| **Known biases** | Very high base reference answer bias (Δ=3.80), the highest observed. Score ID bias also high (Δ=2.90). SFT-only training shows limited bias reduction compared to RLHF models. |
| **Study metrics** | **Base Δ**: 0.40 rub, 2.90 ID, 3.80 ref — **Instruct Δ**: 0.30 rub, 2.50 ID, 3.40 ref |
| **Change** | Rubric: -0.10, Score ID: -0.40, Ref Answer: -0.40 |

---

### 12. Qwen 3 8B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen3-8B` |
| **Parameters** | 8.15B |
| **Architecture** | Dense Transformer + SwiGLU activation |
| **Training data** | Pre-trained on ~18T tokens; SFT + RLHF |
| **Context window** | 131,072 tokens |
| **License** | Apache 2.0 |
| **Release date** | April 2025 |
| **Known biases** | High rubric order bias (Δ=1.20) despite being an instruct model; suggests the Qwen3 generation may have different scoring behavior than Qwen2.5 |
| **Instruct Δ** | 1.20 (rub), 0.50 (ID), 0.00 (ref) |

---

### 13. Qwen 3 14B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen3-14B` |
| **Parameters** | 14.18B |
| **Architecture** | Dense Transformer + SwiGLU activation |
| **Training data** | Pre-trained on ~18T tokens; SFT + RLHF |
| **Context window** | 131,072 tokens |
| **License** | Apache 2.0 |
| **Release date** | April 2025 |
| **Known biases** | The least biased model in the entire study (mean Δ=0.07). Near-zero bias across all probes. |
| **Instruct Δ** | 0.10 (rub), 0.00 (ID), 0.10 (ref) |

---

### 14. Qwen 3 32B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen3-32B` |
| **Parameters** | 32.76B |
| **Architecture** | Dense Transformer + SwiGLU activation |
| **Training data** | Pre-trained on ~18T tokens; SFT + RLHF |
| **Context window** | 131,072 tokens |
| **License** | Apache 2.0 |
| **Release date** | April 2025 |
| **Known biases** | Low bias across all probes; shows the scaling trend of decreased bias with increased model size within the Qwen3 family |
| **Instruct Δ** | 0.80 (rub), 0.20 (ID), 0.30 (ref) |

---

### 15. Qwen 2.5 72B (Instruct only)

| Field | Value |
|-------|-------|
| **Model ID** | `Qwen/Qwen2.5-72B-Instruct` |
| **Parameters** | 72.71B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~18T tokens; SFT + RLHF |
| **Context window** | 131,072 tokens |
| **License** | Apache 2.0 |
| **Release date** | September 2024 |
| **Known biases** | High rubric order bias (Δ=1.30) despite large scale. Reference answer bias is low (Δ=0.30). |
| **Instruct Δ** | 1.30 (rub), 0.80 (ID), 0.30 (ref) |

---

### 16. Google Gemma 3 4B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-3-4b-it` |
| **Parameters** | 3.82B |
| **Architecture** | Dense + MoE (Mixture of Experts) |
| **Training data** | Pre-trained on ~6T tokens; SFT + RLHF |
| **Context window** | 32,768 tokens |
| **License** | Gemma License (gated access) |
| **Release date** | March 2025 |
| **Known biases** | Low overall bias; well-balanced across all three probes |
| **Instruct Δ** | 0.20 (rub), 0.50 (ID), 0.10 (ref) |

---

### 17. Google Gemma 3 12B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-3-12b-it` |
| **Parameters** | 12.15B |
| **Architecture** | Dense + MoE |
| **Training data** | Pre-trained on ~6T tokens; SFT + RLHF |
| **Context window** | 32,768 tokens |
| **License** | Gemma License (gated access) |
| **Release date** | March 2025 |
| **Known biases** | Moderate rubric order and reference answer bias (both Δ=0.90); score ID bias is low (Δ=0.30) |
| **Instruct Δ** | 0.90 (rub), 0.30 (ID), 0.90 (ref) |

---

### 18. Google Gemma 3 27B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-3-27b-it` |
| **Parameters** | 27.20B |
| **Architecture** | Dense + MoE |
| **Training data** | Pre-trained on ~6T tokens; SFT + RLHF |
| **Context window** | 32,768 tokens |
| **License** | Gemma License (gated access) |
| **Release date** | March 2025 |
| **Known biases** | Moderate rubric order bias (Δ=0.80); score ID bias is the lowest among Gemma3 models (Δ=0.20) |
| **Instruct Δ** | 0.80 (rub), 0.20 (ID), 0.50 (ref) |

---

### 19. Google Gemma 4 31B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemma-4-31b-it` |
| **Parameters** | 30.70B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on ~10T tokens; SFT + RLHF |
| **Context window** | 262,144 tokens |
| **License** | Apache 2.0 |
| **Release date** | April 2026 |
| **Known biases** | Very low overall bias; the Gemma 4 generation shows substantial bias reduction compared to Gemma 3 |
| **Instruct Δ** | 0.40 (rub), 0.10 (ID), 0.20 (ref) |

---

### 20. Microsoft Phi-4 (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `microsoft/phi-4` |
| **Parameters** | 14.68B |
| **Architecture** | Dense Transformer |
| **Training data** | Synthetic data + filtered web data; SFT only |
| **Training method** | SFT (no RLHF) |
| **Context window** | 131,072 tokens |
| **License** | MIT |
| **Release date** | December 2024 |
| **Known biases** | Low reference answer bias (Δ=0.10) but moderate rubric order (Δ=0.60) and score ID (Δ=0.70) bias. SFT-only training pattern. |
| **Instruct Δ** | 0.60 (rub), 0.70 (ID), 0.10 (ref) |

---

### 21. Mistral Nemo 12B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `mistralai/Mistral-Nemo-Base-2407` |
| **Parameters** | 12.0B |
| **Architecture** | Dense Transformer (Grouped-Query Attention) |
| **Training data** | Pre-trained on web data; SFT |
| **Context window** | 131,072 tokens |
| **License** | Apache 2.0 |
| **Release date** | July 2024 |
| **Known biases** | High score ID bias (Δ=1.00); moderate rubric order (Δ=0.30) and reference answer (Δ=0.50) |
| **Instruct Δ** | 0.30 (rub), 1.00 (ID), 0.50 (ref) |

---

### 22. Mistral 3.2 24B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `mistralai/Mistral-Small-24B-Instruct-2501` |
| **Parameters** | 24.0B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on web data; further trained with SFT |
| **Context window** | 128,000 tokens |
| **License** | Apache 2.0 |
| **Release date** | January 2025 |
| **Known biases** | Low and balanced bias across all three probes |
| **Instruct Δ** | 0.30 (rub), 0.30 (ID), 0.40 (ref) |

---

### 23. DeepSeek V3 (Chat)

| Field | Value |
|-------|-------|
| **Model ID** | `deepseek-ai/DeepSeek-V3` |
| **Parameters** | 671B total (37B activated per token) |
| **Architecture** | Mixture of Experts (256 experts, top-8 routing) |
| **Training data** | Pre-trained on ~14.8T tokens; SFT + RLHF |
| **Context window** | 128,000 tokens |
| **License** | DeepSeek License |
| **Release date** | December 2024 |
| **Known biases** | Low overall bias; moderate score ID bias (Δ=0.80) |
| **Instruct Δ** | 0.20 (rub), 0.80 (ID), 0.30 (ref) |

---

### 24. DeepSeek V4-Flash (Chat)

| Field | Value |
|-------|-------|
| **Model ID** | `deepseek-ai/DeepSeek-V4-Flash` |
| **Parameters** | 671B total (37B activated) |
| **Architecture** | MoE (256 experts) |
| **Training data** | SFT + RLHF |
| **Context window** | 128,000 tokens |
| **License** | DeepSeek License |
| **Release date** | 2026 |
| **Known biases** | Low bias profile; balanced across all probes with slightly higher score ID bias (Δ=0.50) |
| **Instruct Δ** | 0.30 (rub), 0.50 (ID), 0.30 (ref) |

---

### 25. Hermes 3 70B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `NousResearch/Hermes-3-Llama-3.1-70B` |
| **Parameters** | 70.6B |
| **Architecture** | Dense Transformer |
| **Training data** | SFT on a diverse corpus of synthetic and human-generated instruction data (on Llama-3.1-70B base) |
| **Training method** | SFT (no RLHF) |
| **Context window** | 131,072 tokens |
| **License** | Llama 3.1 Community License |
| **Release date** | August 2024 |
| **Known biases** | Highest score ID bias observed (Δ=1.80); the descriptive and letter conditions produce very different scores than numeric. Moderate rubric order bias (Δ=0.80). |
| **Instruct Δ** | 0.80 (rub), 1.80 (ID), 0.50 (ref) |

---

### 26. Zephyr 7B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `HuggingFaceH4/zephyr-7b-beta` |
| **Parameters** | 7.24B |
| **Architecture** | Dense Transformer |
| **Training data** | SFT on publicly available instruction data + DPO (on Mistral 7B base) |
| **Training method** | SFT + DPO |
| **Context window** | 32,768 tokens |
| **License** | MIT |
| **Release date** | November 2023 |
| **Known biases** | Low overall bias profile; well-balanced across all probes |
| **Instruct Δ** | 0.30 (rub), 0.50 (ID), 0.20 (ref) |

---

### 27. MythoMax 13B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Gryphe/MythoMax-L2-13b` |
| **Parameters** | 12.9B |
| **Architecture** | Dense Transformer (merge of multiple fine-tunes on Llama 2) |
| **Training data** | Merged fine-tunes (Mythologic, Chronos, etc.) |
| **Context window** | 4,096 tokens |
| **License** | Apache 2.0 |
| **Release date** | 2024 |
| **Known biases** | Highest rubric order bias (Δ=1.50); high score ID bias (Δ=1.30). The merged fine-tuning approach may produce unusual scoring patterns. |
| **Instruct Δ** | 1.50 (rub), 1.30 (ID), 0.20 (ref) |

---

### 28. SOLAR 10.7B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `upstage/SOLAR-10.7B-Instruct-v1.0` |
| **Parameters** | 10.7B |
| **Architecture** | Dense Transformer (depth-upscaled from 32 to 48 layers) |
| **Training data** | Pre-trained on ~2T tokens; SFT on instruction data |
| **Context window** | 32,768 tokens |
| **License** | Apache 2.0 |
| **Release date** | December 2023 |
| **Known biases** | High rubric order bias (Δ=1.10); low reference answer bias (Δ=0.20) |
| **Instruct Δ** | 1.10 (rub), 0.80 (ID), 0.20 (ref) |

---

### 29. NVIDIA Nemotron Nano 30B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `nvidia/Nemotron-3-Nano-30B-A3B` |
| **Parameters** | 30B total (3B activated) |
| **Architecture** | MoE (Mamba-Transformer hybrid) |
| **Training data** | SFT + RLHF on NVIDIA curated data |
| **Context window** | 256,000 tokens |
| **License** | NVIDIA Open Model License |
| **Release date** | April 2025 |
| **Known biases** | Low overall bias; well-balanced across probes |
| **Instruct Δ** | 0.50 (rub), 0.20 (ID), 0.30 (ref) |

---

### 30. NVIDIA Nemotron Super 120B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `nvidia/Nemotron-3-Super-120B-A12B` |
| **Parameters** | 120B total (12B activated) |
| **Architecture** | MoE (Mamba-Transformer hybrid) |
| **Training data** | SFT + RLHF |
| **Context window** | 1,048,576 tokens |
| **License** | NVIDIA Open Model License |
| **Release date** | April 2025 |
| **Known biases** | Very low overall bias (mean Δ=0.27); the largest context window model in the study |
| **Instruct Δ** | 0.50 (rub), 0.20 (ID), 0.10 (ref) |

---

### 31. Hy3 295B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `Tencent/Hunyuan-Large` |
| **Parameters** | 295B total (21B activated) |
| **Architecture** | MoE (192 experts, top-8) |
| **Training data** | SFT + RLHF |
| **Context window** | 256,000 tokens |
| **License** | Apache 2.0 |
| **Release date** | 2025 |
| **Known biases** | High rubric order bias (Δ=1.00) and score ID bias (Δ=1.20) despite being the largest parameter count model |
| **Instruct Δ** | 1.00 (rub), 1.20 (ID), 0.60 (ref) |

---

### 32. GPT-OSS 20B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `openai/gpt-oss-20b` |
| **Parameters** | 21B total (3.6B activated) |
| **Architecture** | MoE |
| **Training data** | SFT + RLHF |
| **Context window** | 131,072 tokens |
| **License** | Apache 2.0 |
| **Release date** | 2025 |
| **Known biases** | The least biased instruct-only model (mean Δ=0.10). Near-zero bias across all probes. |
| **Instruct Δ** | 0.10 (rub), 0.10 (ID), 0.10 (ref) |

---

### 33. Command-R (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `CohereForAI/c4ai-command-r-v01` |
| **Parameters** | 35B |
| **Architecture** | Dense Transformer |
| **Training data** | SFT + RLHF on Cohere curated data |
| **Context window** | 128,000 tokens |
| **License** | CC-BY-NC |
| **Release date** | March 2024 |
| **Known biases** | High score ID bias (Δ=1.10); moderate reference answer bias (Δ=0.90) |
| **Instruct Δ** | 0.30 (rub), 1.10 (ID), 0.90 (ref) |

---

### 34. GLM-4.7 (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `THUDM/glm-4-9b-chat` |
| **Parameters** | 9.0B |
| **Architecture** | Dense Transformer |
| **Training data** | Pre-trained on multilingual data; SFT + RLHF |
| **Context window** | 128,000 tokens |
| **License** | Apache 2.0 |
| **Release date** | June 2024 |
| **Known biases** | Low overall bias (mean Δ=0.20); one of the least biased instruct models |
| **Instruct Δ** | 0.10 (rub), 0.20 (ID), 0.30 (ref) |

---

### 35. Gemini 2.5-Flash (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `google/gemini-2.5-flash` (API, no public weights) |
| **Parameters** | Not disclosed |
| **Architecture** | Not disclosed |
| **Training data** | Not disclosed; RLHF |
| **Context window** | 1,048,576 tokens |
| **License** | Google TOS |
| **Release date** | 2025 |
| **Known biases** | High reference answer bias (Δ=0.90); well-balanced in other probes |
| **Instruct Δ** | 0.30 (rub), 0.30 (ID), 0.90 (ref) |

---

### 36. Lunaris 8B (Instruct)

| Field | Value |
|-------|-------|
| **Model ID** | `arcee-ai/Lunaris-8B` |
| **Parameters** | 8.0B |
| **Architecture** | Dense Transformer |
| **Training data** | DPO fine-tune on Llama-3.1-8B base |
| **Training method** | SFT + DPO |
| **Context window** | 8,192 tokens |
| **License** | Apache 2.0 |
| **Release date** | 2025 |
| **Known biases** | High reference answer bias (Δ=1.00); moderate rubric order (Δ=0.40) and score ID (Δ=0.40) |
| **Instruct Δ** | 0.40 (rub), 0.40 (ID), 1.00 (ref) |
