# Bias Interaction Experiment — Analysis Report
*Generated: 2026-07-13 01:24*

## Overview

| Judge | N | Mean | StDev | Baseline | Worst | Degradation |
|-------|---|------|-------|----------|-------|-------------|
| claude | 3200 | 3.44 | 0.34 | 3.50 | 3.12 | 0.373 |
| deepseek | 3200 | 3.47 | 0.34 | 3.49 | 3.17 | 0.318 |
| gemini | 3200 | 3.41 | 0.40 | 3.51 | 2.97 | 0.533 |
| gpt4o | 3200 | 3.45 | 0.29 | 3.48 | 3.14 | 0.341 |
| llama | 3200 | 3.39 | 0.48 | 3.51 | 2.80 | 0.706 |

## Bias Effects

| Judge | Position Bias | Verbosity Bias | Combined | Interaction Ratio | Effect |
|-------|--------------|----------------|----------|-------------------|--------|
| claude | 0.117 | 0.082 | 0.000 | 0.00 | cancelling |
| deepseek | 0.022 | 0.075 | 0.000 | 0.00 | cancelling |
| gemini | 0.159 | 0.114 | 0.000 | 0.00 | cancelling |
| gpt4o | 0.060 | 0.076 | 0.000 | 0.00 | cancelling |
| llama | 0.263 | 0.155 | 0.000 | 0.00 | cancelling |

## Score Distribution

| Judge | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|
| claude | 0 | 7 | 1627 | 1566 | 0 |
| deepseek | 0 | 5 | 1516 | 1678 | 1 |
| gemini | 0 | 54 | 1623 | 1520 | 3 |
| gpt4o | 0 | 2 | 1560 | 1638 | 0 |
| llama | 0 | 155 | 1534 | 1502 | 9 |

## Key Findings

- **Cancelling biases**: claude, deepseek, gemini, gpt4o, llama — biases partially offset
- **Average degradation across judges**: 0.454