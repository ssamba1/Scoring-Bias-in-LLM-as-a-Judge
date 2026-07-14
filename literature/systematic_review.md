# Systematic Review Methodology

## Search Strategy

| Parameter | Value |
|-----------|-------|
| **Databases** | arXiv, ACL Anthology, DBLP, Google Scholar, Semantic Scholar |
| **Search date** | January 2026 |
| **Search terms** | "LLM-as-a-Judge" AND bias, "scoring bias" AND LLM, "bias in LLM evaluation", "judge LLM" AND bias |
| **Inclusion** | English-language, 2023–2026, focused on LLM evaluation bias |
| **Exclusion** | Non-peer-reviewed (except arXiv), position-only papers, non-bias work |
| **Papers found** | 47 |
| **Papers cited** | 12 |

## PRISMA Flow

```
Records screened: 47
    ├── Excluded (not LLM bias): 22
    └── Full text assessed: 25
        ├── Excluded (no scoring bias): 10
        ├── Excluded (position only): 3
        └── Included in review: 12
```

## Quality Assessment

| Paper | Risk of Bias | Novelty | Reproducibility | Overall |
|-------|-------------|---------|-----------------|---------|
| Wang et al. (ACL 2024) | Low | Medium | Medium | Strong |
| Ye et al. (CALM) | Medium | High | Medium | Strong |
| Li et al. (DASFAA 2026) | Low | Medium | Medium | Strong |
| Park et al. (EMNLP 2024) | Medium | High | Low | Medium |
| Pan et al. (ACL 2026) | Low | Medium | Medium | Strong |

## Gap Identification

The systematic review identifies one clear gap: **no prior work has investigated whether scoring bias originates from pre-training or instruction tuning.** This is the gap we fill.
