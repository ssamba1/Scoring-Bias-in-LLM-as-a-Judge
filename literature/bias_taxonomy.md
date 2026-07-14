# Bias Taxonomy: Complete Catalog

| # | Bias Type | Definition | First Documented | Studied By | Tested in this work? | Our finding |
|---|-----------|-----------|-----------------|------------|---------------------|-------------|
| 1 | **Rubric Order** | Score changes when rubric scale direction is reversed | Li et al. 2025 | Li, Xu, **This work** | **Yes** | −44% (instruct) |
| 2 | **Score ID** | Score changes when label format changes (numeric/letter/descriptive) | Li et al. 2025 | Li, **This work** | **Yes** | −77% (instruct) |
| 3 | **Reference Answer** | Score changes when exemplar is shown before scoring | Li et al. 2025 | Li, **This work** | **Yes** | +35% (instruct) |
| 4 | **Position Bias** | Score changes when response order is swapped | Wang et al. 2023 | Wang, Zheng, Ye, Park | **No** | Future work |
| 5 | **Verbosity Bias** | Longer responses scored higher regardless of quality | Saito et al. 2023 | Ye, Park | **No** | Future work |
| 6 | **Self-Enhancement** | Model favors its own generated responses | Ye et al. 2024 | Ye, Park, Pan | **No** | Future work |
| 7 | **Sentiment Bias** | Emotional tone affects scoring | Ye et al. 2024 | Ye | **No** | Future work |
| 8 | **Authority Bias** | Fake citations increase scores | Ye et al. 2024 | Ye, Park | **No** | Future work |
| 9 | **Bandwagon Effect** | "Majority agrees" affects scoring | Ye et al. 2024 | Ye | **No** | Future work |
| 10 | **Distraction Bias** | Irrelevant information affects scoring | Ye et al. 2024 | Ye | **No** | Future work |
| 11 | **Fallacy Oversight** | Logical fallacies overlooked if conclusion is correct | Ye et al. 2024 | Ye | **No** | Future work |
| 12 | **Diversity Bias** | Demographic identity affects scoring | Ye et al. 2024 | Ye | **No** | Future work |
| 13 | **Compassion Fade** | Model name affects scoring | Ye et al. 2024 | Ye | **No** | Future work |
| 14 | **User-Assistant Bias** | Model favors user-provided content | Pan et al. 2026 | Pan | **No** | Future work |
| 15 | **Base vs Instruct Gap** | Systematic difference between training stages | **This work** | **This work** | **Yes** | Differential effect |

## Bias Type Coverage: This Work vs Literature

```
                    Ye (2024) ── 12 bias types
                   /       \
         Wang (2023)        Park (2024) ── 6 bias types
              |                  |
         Position            Length, Authority,
         Bias                Self-Enhancement
              |
         Li (2025) ── 3 scoring biases
              |
         THIS WORK ── 15 bias types cataloged
                       ── 3 empirically tested
                       ── 12 identified for future work
```

## Key Gap

Of 15 documented bias types, **only 3 have been tested for base vs instruct differences** — and this work is the first to do so. The remaining 12 are open for future investigation.
