# Comprehensive Audit: Open Problems in Activation Steering / Representation Engineering

**Source:** Wehner et al. (2025)  "Taxonomy, Opportunities, and Challenges of Representation Engineering for Large Language Models", arXiv:2502.19649 (v5, Oct 2025)
**Audit date:** July 2026
**Scope:** Papers published AFTER Feb 2025 that address challenges listed in the survey

---

## Executive Summary

Of **12 challenges** enumerated in the Wehner et al. survey:
- **0 fully solved**  no challenge has been definitively put to rest
- **9 partially solved**  significant progress with clear remaining gaps
- **3 remain largely open**  little to no substantive progress since the survey

The field has seen explosive growth (100+ papers since the survey's literature cutoff), with notable advances in rotation-based steering (Angular/Spherical), conditional steering (CAST/MERA), flow-based methods (FLAS), improved control-reliability tradeoffs (SKOP/SVF), and identifiable concept learning (SSAEs). However, fundamental limitations persist, particularly around concept misspecification, complete concept representation learning, and the recent proof that steering vectors are **provably non-identifiable**.

---

## Challenge-by-Challenge Assessment

### 1. Multi-Concept Control
**Survey Status:** Simultaneous multi-concept steering reduces effectiveness and increases capability degradation.

**Papers since Feb 2025:**
- **Joshi et al. (Feb 2025)**  *Sparse Shift Autoencoders (SSAEs)*, arXiv:2502.12179. Introduces identifiable sparse representations of multi-concept shifts. Provides **identifiability guarantees** for disentangling multiple concepts from paired observations where multiple unknown concepts differ. Empirically demonstrates concept recovery across real-world language datasets. **NeurIPS 2025.**
- **Nguyen et al. (2025)**  Improves multi-concept steering by sparsely applying vectors per-token and enforcing orthogonality to reduce interference.
- **Beaglehole et al. (2025)**  Non-linear feature learning for multi-concept steering; learns a matrix capturing directions the probe is sensitive to.
- **Triantafyllopoulos et al. (May 2026)**  *Conceptors for Semantic Steering*, arXiv:2605.04980. Proposes conceptors (matrices) for multi-concept composition via Boolean AND operations. Enables multi-concept steering **without access to original activation data**.
- **Li et al. (Feb 2026)**  *Steering Vector Fields (SVF)*, arXiv:2602.01654. Supports coordinated multi-layer, multi-attribute control within a unified framework.
- **Jin et al. (May 2026)**  *FLAS: Flow-based Activation Steering*, arXiv:2605.05892. Learned concept-conditioned velocity field; supports multi-concept composition.

**Assessment: PARTIALLY SOLVED ✅**
- SSAEs provide theoretical identifiability for multi-concept disentanglement (key advance)
- Conceptors enable clean Boolean composition without data re-access
- SVF/FLAS provide unified multi-attribute frameworks
- **Remaining gaps:** Robust simultaneous steering of 5+ unrelated concepts without interference; evaluation is sparse; no comprehensive multi-concept benchmark

---

### 2. Long-Form Generation
**Survey Status:** RepE effectively controls short answers but lacks evidence for long-form generations and multi-turn conversations.

**Papers since Feb 2025:**
- **Li et al. (Feb 2026)**  *SVF*, arXiv:2602.01654. Explicitly designed for long-form control: "enables efficient long-form and multi-attribute control within a unified framework."
- **You et al. (Feb 2026)**  *Spherical Steering*, arXiv:2602.08169 (ICML 2026). Norm-preserving rotation maintains open-ended generation quality over extended outputs.
- **Luo et al. (May 2026)**  *SKOP*, arXiv:2605.06342. Addresses long-context retrieval where vanilla steering is ineffective; preserves attention patterns.
- **Vu & Nguyen (Oct 2025)**  *Angular Steering*, arXiv:2510.26243 (NeurIPS 2025 Spotlight). Rotation-based control maintains stability across generations.
- **Anonymous (2026)**  *Activation Steering for Aligned Open-ended Generation without Sacrificing Coherence*, arXiv:2604.08169. Directly tackles long-form alignment.
- **GCAD (2026)**  Attention-level activation steering for stable multi-turn behavior control.

**Assessment: PARTIALLY SOLVED ✅**
- Several methods now explicitly evaluate long-form/long-context settings
- Rotation methods preserve coherence over longer generations
- **Remaining gaps:** No systematic evaluation across diverse long-form tasks; multi-turn setting still underexplored; steering effect decay over very long generations not quantified

---

### 3. Out-of-Distribution (OOD) Generalization
**Survey Status:** Concept operators fail to generalize across different contexts, prompt templates, or tasks.

**Papers since Feb 2025:**
- **Gadgil et al. (Apr 2026)**  *Where to Steer (W2S)*, arXiv:2604.03867. Input-dependent layer selection; improves both in-distribution and OOD performance. Learns mapping from input embeddings to optimal steering layers.
- **Wang et al. (2025)**  *SAE-RSV: Refinement of Steering Vector via Sparse Autoencoder*. Improves OOD generalization by refining steering vectors learned from limited data.
- **Rodriguez et al. (Mar 2025)**  *LinEAS*, arXiv:2503.10679 (NeurIPS 2025). End-to-end learning with distributional loss accounting for all layer-wise shifts; more robust OOD.
- **Han et al. (Feb 2026)**  *Steer2Adapt*, arXiv:2602.07276. Dynamic composition of steering vectors; adapts to new tasks from few examples (8.2% average improvement across 9 tasks, 3 models).
- **Weight Arithmetic (2025)**  Weight steering outperforms activation steering for OOD generalization.

**Assessment: PARTIALLY SOLVED ✅**
- W2S adaptive layer selection is a principled approach to OOD
- LinEAS distributional loss improves OOD robustness
- Steer2Adapt provides few-shot adaptation to new distributions
- **Remaining gaps:** No guarantee of OOD generalization; concept operators still fail under significant distribution shift; most evaluations are limited

---

### 4. Capability Deterioration
**Survey Status:** RepE reduces general language modeling capabilities, quality, and diversity.

**Papers since Feb 2025:**
- **Luo et al. (May 2026)**  *SKOP*, arXiv:2605.06342. **Reduces utility degradation by 5-7×** while retaining >95% vanilla steering efficacy. Diagnoses attention rerouting as primary cause.
- **Vu & Nguyen (Oct 2025)**  *Angular Steering*, NeurIPS 2025 Spotlight. Rotation-based steering preserves general capabilities better than additive methods.
- **You et al. (Feb 2026)**  *Spherical Steering*, ICML 2026. Norm-preserving rotation; maintains open-ended generation quality; +10% on TruthfulQA, COPA, Storycloze while preserving coherence.
- **Hedström et al. (2025)**  *MERA: Mechanistic Error Reduction with Abstention*, ICML 2025. Conditional steering that abstains from intervention when it would degrade performance.
- **Lee et al. (ICLR 2025 Spotlight)**  *CAST: Conditional Activation Steering*. Refuses conditionally to minimize unnecessary capability impact.
- **Korznikov et al. (Sep 2025)**  *The Rogue Scalpel*, arXiv:2509.22067. **Demonstrates that even benign activation steering systematically breaks model safety safeguards.** Safety capabilities are actively harmed.
- **Xiong et al. (Feb 2026)**  *Steering Externalities*, arXiv:2602.04896. Benign activation steering unintentionally increases jailbreak risk.

**Assessment: PARTIALLY SOLVED ✅ (for general capabilities); REMAINS OPEN ❌ (for safety capabilities)**
- SKOP's 5-7× improvement in utility preservation is a major advance
- Rotation methods preserve activation distribution and coherence
- **Critical finding:** The Rogue Scalpel and Steering Externalities show steering actively compromises safety guardrails  this capability deterioration is **not solved and may be inherent**
- Safety-capability tradeoff remains the hardest subproblem

---

### 5. Learning Specific Concept Representations (Isolation)
**Survey Status:** RepE struggles to isolate a concept from other concepts; steering one affects unrelated ones.

**Papers since Feb 2025:**
- **Joshi et al. (Feb 2025)**  *SSAEs*, arXiv:2502.12179. Provides **identifiability guarantees** for learning specific concept representations from paired observations. Theoretically ensures that the learned concept operator captures a single concept.
- **Venkatesh & Kurapath (Feb 2026)**  *On the Non-Identifiability of Steering Vectors*, arXiv:2602.06801. **Proves that steering vectors are fundamentally non-identifiable via a constructive null-space argument.** A given behavioral effect can be achieved by infinitely many different steering vectors.
- **Luo et al. (May 2026)**  *SKOP*, arXiv:2605.06342. Preserves focus tokens to avoid collateral steering effects.
- **Beaglehole et al. (2025)**  Non-linear feature learning; top eigenvectors of learned matrices as concept operators.

**Assessment: REMAINS LARGELY OPEN ❌**
- SSAEs provide identifiability under **specific conditions** (paired observations, sparse concept shifts)  a significant but limited advance
- The non-identifiability proof (Venkatesh, Feb 2026) is a **fundamental limitation**: infinitely many steering vectors produce the same behavioral change
- Collateral effects (steering happiness reduces refusal; steering gender increases age bias) continue to be reported
- This challenge may be **inherently limited by the non-identifiability result**

---

### 6. Learning Complete Concept Representations
**Survey Status:** RepE struggles to capture all aspects of multifaceted concepts like honesty.

**Papers since Feb 2025:**
- **Chen et al. (2025, extending 2024b)**  Multiple orthogonal steering vectors for different aspects of a concept.
- **Multi-aspect SAE work (Durmus et al., 2024-2025)**  Discovers many features but concept coverage not systematic.
- **No dedicated paper solves "complete representation" problem.**

**Assessment: REMAINS OPEN ❌**
- No paper systematically addresses how to ensure all facets of a multifaceted concept are captured
- The "concept completeness" problem has received essentially zero dedicated attention
- Non-identifiability result (Feb 2026) implies there's no unique "complete" representation

---

### 7. Unreliability (including Hyperparameter Sensitivity)
**Survey Status:** RepE methods are unreliable  sensitive to hyperparameters, some concepts unsteerable, per-input negative effects.

**Papers since Feb 2025:**
- **Li et al. (Feb 2026)**  *SVF*, arXiv:2602.01654. Directly addresses unreliability: "delivers stronger and more reliable control." Context-dependent steering alleviates misalignment of static vectors across diverse inputs.
- **Vu & Nguyen (Oct 2025)**  *Angular Steering*, NeurIPS 2025 Spotlight. "Simplifies parameter selection and maintains model stability across a broader range of adjustments." Unified geometric framework.
- **Braun et al. (May 2025)**  *Understanding (Un)Reliability of Steering Vectors in Language Models*, arXiv:2505.22637. Identifies **geometric predictors** of steering unreliability; shows some concepts are unsteerable because positive/negative activations aren't linearly separable.
- **Jafari et al. (Feb 2026)**  *Mechanistic Indicators of Steering Effectiveness*, arXiv:2602.01716. Develops metrics to predict when steering will/won't work based on activation-space properties.
- **Gadgil et al. (Apr 2026)**  *W2S*, arXiv:2604.03867. Adaptive layer selection reduces per-input steering failures.
- **Hedström et al. (2025)**  *MERA*, ICML 2025. Mechanistic Error Reduction with Abstention  abstains when steering would harm.
- **Lee et al. (ICLR 2025 Spotlight)**  *CAST*  Conditional application based on input category.
- **Jiang et al. (Mar 2026)**  *Global Evolutionary Steering via Cross-Layer Consistency*, arXiv:2603.12298. Analyzes hyperparameter sensitivity of rectification strength and number of steered layers.

**Assessment: PARTIALLY SOLVED ✅**
- SVF's context-dependent steering is a principled approach to unreliability
- Geometric predictors (Braun) and mechanistic indicators (Jafari) provide tools to **predict** reliability
- Angular Steering's unified framework simplifies parameter selection
- CAST/MERA address selective application
- **Remaining gaps:** Per-input negative effects still occur; concept-dependent steerability not eliminated; no reliability guarantees

---

### 8. Spuriously Correlated Concepts
**Survey Status:** RI methods cannot disentangle correlated concepts; steering vectors capture spurious correlations.

**Papers since Feb 2025:**
- **Joshi et al. (Feb 2025)**  *SSAEs*, arXiv:2502.12179. **Directly addresses this** via identifiability: guarantees that when underlying concepts can change independently across paired observations, SSAEs recover them. "Sparse shift autoencoders" model differences between embeddings.
- **Conmy & Nanda (2024, extended 2025)**  Decompose steering vectors into SAE features, remove unrelated features. Sparse reconstruction of steering vectors.
- **Kharlapenko et al. (2025)**  Optimize SAE reconstruction of steering vectors toward good downstream performance while incentivizing sparsity.

**Assessment: PARTIALLY SOLVED ✅**
- SSAEs provide the strongest theoretical result: identifiability from paired observations where multiple but not all concepts change
- SAE-based cleanup of steering vectors helps in practice
- **Remaining gaps:** Theoretical guarantees require paired observations with specific sparsity patterns; SAE-based approaches are computationally expensive; no method handles all forms of correlation

---

### 9. Concept Misspecification
**Survey Status:** The specification of the concept (via inputs or scoring functions) may differ from the intended concept; inputs may activate wrong representations.

**Papers since Feb 2025:**
- **Deng et al. (2025)**  Matched pair trial design where pairs differ only in assigned roles, guaranteeing opposite behaviors. Reduces misspecification risk from pre-prompt following assumptions.
- **No other paper directly addresses concept misspecification as a primary problem.**

**Assessment: REMAINS OPEN ❌**
- Essentially **no progress** on the fundamental misspecification problem
- The risk that "I will be honest" activates "the human wants me to be honest" rather than the intended honesty representation is not addressed
- LLM-as-judge biases for output scoring remain unexamined in this context
- This is arguably the **most critical unsolved challenge** since it undermines the validity of all RepE

---

### 10. Interference from Superposition
**Survey Status:** Features represented in superposition cause interference; steering one feature affects others.

**Papers since Feb 2025:**
- **Joshi et al. (Feb 2025)**  *SSAEs*, arXiv:2502.12179. Sparse shift autoencoders are explicitly designed to address superposition via identifiability guarantees.
- **SAE-based steering (multiple papers)**  Conmy & Nanda, Kharlapenko et al., Makelo et al. (2025). SAE features as concept operators.
- **Luo et al. (May 2026)**  *SKOP*, arXiv:2605.06342. Attention rerouting addresses one mechanism of interference.
- **Mayne et al. (2024-2025)**  Identifies that steering vectors fall outside SAE training distribution, containing negative feature directions not accommodated in SAEs.

**Assessment: PARTIALLY SOLVED ✅**
- SAEs and SSAEs are the primary tools against superposition
- SSAEs add identifiability, moving beyond just "finding features"
- **Remaining gaps:** SAEs don't scale gracefully to all features; steering vectors often lie outside SAE training distribution; Mayne et al. show fundamental limitations of using SAEs to decompose steering vectors

---

### 11. Assumptions About Models' Representations
**Survey Status:** Methods assume linear directions, static representations, single-layer localization, no inter-layer interactions.

**Papers since Feb 2025:**
- **Vu & Nguyen (Oct 2025)**  *Angular Steering*, NeurIPS 2025 Spotlight. Unifies addition and orthogonalization under rotation. Removes need for choosing between additive and ablative methods.
- **You et al. (Feb 2026)**  *Spherical Steering*, ICML 2026. Norm-preserving rotation; directly challenges additive steering assumptions.
- **Jin et al. (May 2026)**  *FLAS*, arXiv:2605.05892. Learned velocity field  no fixed geometry assumptions. First steering method to consistently beat prompting.
- **Li et al. (Feb 2026)**  *SVF*, arXiv:2602.01654. Context-dependent steering direction  abandons static direction assumption.
- **Jiang et al. (Mar 2026)**  *Cross-Layer Consistency*, arXiv:2603.12298. Addresses inter-layer dependencies explicitly.
- **The Cylindrical Representation Hypothesis (2026)**  Proposes alternative geometric hypothesis (cylinders vs. linear directions).
- **Pham & Nguyen (2024, extended 2025)**  Direction-magnitude view of representations, rotations.

**Assessment: PARTIALLY SOLVED ✅**
- Rotation-based methods and flow-based methods substantially relax linearity and static-direction assumptions
- Cross-layer work addresses inter-layer dependencies
- **Remaining gaps:** No consensus on correct geometry; most practical methods still use simple vector addition; the linear representation hypothesis remains dominant but increasingly questioned

---

### 12. Shifting Activations off Their Natural Distribution
**Survey Status:** Steering moves activations off-distribution, degrading capabilities, especially with strong or multi-concept intervention.

**Papers since Feb 2025:**
- **You et al. (Feb 2026)**  *Spherical Steering*, ICML 2026. **Explicitly designed** to keep activations on-distribution: norm-preserving rotation "resolves this trade-off through activation rotation." Addresses "representation collapse and degraded open-ended generation."
- **Vu & Nguyen (Oct 2025)**  *Angular Steering*, NeurIPS 2025 Spotlight. Rotation within a fixed 2D subspace maintains natural distribution.
- **Rodriguez et al. (Mar 2025)**  *LinEAS*, NeurIPS 2025. Distributional loss "accounts simultaneously for all layer-wise distributional shifts."
- **Apple (2025/2026)**  *Transporting Activations*  Optimal transport to keep activations in distribution.
- **Singh et al. (2024, 2025)**  *MiMiC*  Matching mean and covariance of activations minimizes distortion.

**Assessment: PARTIALLY SOLVED ✅**
- Rotation methods (Angular/Spherical) directly solve the off-distribution problem for their paradigm
- LinEAS's distributional loss is principled
- **Remaining gaps:** Additive steering (still the most common method) inherently shifts activations off-distribution; the problem resurfaces under strong intervention even with modern methods; no evaluation standard for distribution shift

---

## Key Cross-Cutting Papers (2025-2026)

| Paper | Date | Venue | Primary Contributions |
|-------|------|-------|---------------------|
| **SSAEs** (Joshi et al.) | Feb 2025 | NeurIPS 2025 | Identifiable multi-concept steering; addresses superposition + spurious correlations |
| **LinEAS** (Rodriguez et al.) | Mar 2025 | NeurIPS 2025 | End-to-end distributional loss; OOD robustness; activation distribution preservation |
| **CAST** (Lee et al.) | 2024/2025 | ICLR 2025 Spotlight | Conditional steering; selective intervention preserves capabilities |
| **Angular Steering** (Vu & Nguyen) | Oct 2025 | NeurIPS 2025 Spotlight | Geometry-aware rotation; unifies addition/orthogonalization; reduces hyperparameter sensitivity |
| **The Rogue Scalpel** (Korznikov et al.) | Sep 2025 |  | Shows steering compromises safety; safety capability deterioration |
| **MERA** (Hedström et al.) | 2025 | ICML 2025 | Mechanistic error reduction with abstention |
| **SVF** (Li et al.) | Feb 2026 |  | Context-dependent steering vector fields; addresses unreliability + long-form |
| **Spherical Steering** (You et al.) | Feb 2026 | ICML 2026 | Norm-preserving rotation; keeps activations on-distribution |
| **Steer2Adapt** (Han et al.) | Feb 2026 |  | Dynamic composition; data-efficient task adaptation |
| **Non-Identifiability** (Venkatesh) | Feb 2026 |  | Proof of fundamental non-identifiability of steering vectors |
| **W2S** (Gadgil et al.) | Apr 2026 |  | Input-dependent layer selection; OOD improvements |
| **SKOP** (Luo et al.) | May 2026 |  | 5-7× utility preservation; attention-level intervention |
| **Conceptors** (Triantafyllopoulos) | May 2026 |  | Boolean multi-concept composition without original data |
| **FLAS** (Jin et al.) | May 2026 |  | Flow-based steering; first method to consistently beat prompting |
| **Steering Externalities** (Xiong et al.) | Feb 2026 |  | Benign steering increases jailbreak risk |

---

## Key Findings

1. **No challenge is fully solved.** Every challenge has either partial solutions or remains open.

2. **Three challenges remain largely open:**
   - **Concept Misspecification**  The gap between intended and specified concept is barely studied
   - **Complete Concept Representations**  No method ensures all facets of a concept are captured
   - **Learning Specific Concept Representations (Isolation)**  The non-identifiability proof (Feb 2026) suggests this may be fundamentally limited

3. **Two new problems have been discovered since the survey:**
   - **Safety capability deterioration** (The Rogue Scalpel, Sep 2025; Steering Externalities, Feb 2026): Steering for benign purposes actively breaks safety guardrails
   - **Non-identifiability** (Venkatesh, Feb 2026): Steering vectors are provably non-unique, challenging interpretability claims

4. **Rotation-based methods (Angular/Spherical) are the most promising paradigm shift**  they simultaneously address capability deterioration, off-distribution shifts, and hyperparameter sensitivity.

5. **The survey itself has been updated** (v5, Oct 2025) to incorporate some of this literature, so the "challenges section" now reflects some partial solutions (e.g., SSAEs for multi-concept, CAST for conditional steering).

---

## Scoring Summary

| Challenge | Survey Status | Current Status | Key Paper(s) |
|-----------|--------------|----------------|--------------|
| Multi-Concept Control | Open | **Partially Solved** | SSAEs (Joshi Feb 2025), Conceptors (Triantafyllopoulos May 2026), SVF (Li Feb 2026) |
| Long-Form Generation | Open | **Partially Solved** | SVF (Li Feb 2026), Spherical Steering (You Feb 2026), GCAD (2026) |
| OOD Generalization | Open | **Partially Solved** | W2S (Gadgil Apr 2026), LinEAS (Rodriguez Mar 2025), Steer2Adapt (Han Feb 2026) |
| Capability Deterioration | Open | **Partially Solved** (general); **Open** (safety) | SKOP (Luo May 2026), Angular Steering (Vu Oct 2025), Rogue Scalpel (Korznikov Sep 2025) |
| Specific Concept Representations | Open | **Remains Open** | Non-Identifiability (Venkatesh Feb 2026), SSAEs (Joshi Feb 2025) |
| Complete Concept Representations | Open | **Remains Open** |  (no dedicated work) |
| Unreliability | Open | **Partially Solved** | SVF (Li Feb 2026), Angular Steering (Vu Oct 2025), CAST (Lee ICLR 2025), Braun (May 2025) |
| Spuriously Correlated Concepts | Open | **Partially Solved** | SSAEs (Joshi Feb 2025), SAE-based cleanup (Conmy & Nanda 2025) |
| Concept Misspecification | Open | **Remains Open** | Deng et al. (2025)  only paper peripherally addressing it |
| Interference from Superposition | Open | **Partially Solved** | SSAEs (Joshi Feb 2025), SAE steering (multiple 2025) |
| Assumptions about Representations | Open | **Partially Solved** | Angular/Spherical Steering (2025-2026), FLAS (Jin May 2026) |
| Shifting Activations off Distribution | Open | **Partially Solved** | Spherical Steering (You Feb 2026), LinEAS (Rodriguez Mar 2025) |
