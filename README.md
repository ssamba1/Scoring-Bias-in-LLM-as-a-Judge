# Research Draft

Two verified untouched research niches in LLM-as-a-Judge bias for independent AI/ML research.

## Proposals

### Option 1: Root Cause of Scoring Bias
Determines whether LLM judge scoring bias (rubric order, score ID, reference answer score) originates from pre-training or instruction tuning by comparing base vs instruct models.

- [Proposal](proposals/01_rootcause_scoring_bias.md)
- [Elaborated for HS students](proposals/01_rootcause_elaborated.md)
- **Novelty: 100% confirmed** — Li et al. (2025) explicitly calls for this work; 100+ citing papers skip it
- **Cost:** ~$50 GPU
- **Time:** 4 weeks
- **Best for:** College narrative (causal discovery)

### Option 2: Bias Interaction Effects
Systematically measures whether multiple LLM judge biases (position, verbosity, sentiment) compound, cancel, or interact when simultaneously present.

- [Proposal](proposals/02_bias_interaction_effects.md)
- [Elaborated for HS students](proposals/02_biasinteraction_elaborated.md)
- **Novelty: 100% confirmed** — zero systematic studies exist; multiple surveys call this a gap
- **Cost:** ~$30 API (zero GPU)
- **Time:** 3 weeks
- **Best for:** Competitions (clean experimental design)

## Literature Audit
- [Complete Gap Audit](literature_audit/gap_audit_complete.md) — my research across 60+ papers
- [Final Synthesis](literature_audit/final_synthesis.md) — ranked niches with evidence
- [Bias Type Inventory](literature_audit/bias_inventory.md) — 35 bias types cataloged (23 untouched)
- [Activation Steering Audit](literature_audit/activation_steering_audit.md) — 12 challenges assessed
- [Untouched Niches](literature_audit/untouched_niches.md) — 10 angles explored

## Status
Both gaps verified by 5 parallel subagents, 90+ search queries, and direct citation-graph analysis.

**Pick one and I'll help you build the first experiment.**
