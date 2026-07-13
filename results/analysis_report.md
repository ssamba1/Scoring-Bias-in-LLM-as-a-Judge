# Bias Interaction Experiment — Analysis Report
*Generated: 2026-07-13 08:10*

## Overview

| Judge | N | Mean | StDev | Baseline | Worst | Degradation |
|-------|---|------|-------|----------|-------|-------------|
| claude | 3200 | 3.39 | 0.49 | 0.00 | 0.00 | 0.000 |
| deepseek | 3200 | 3.42 | 0.49 | 0.00 | 0.00 | 0.000 |
| gemini | 3200 | 3.46 | 0.50 | 0.00 | 0.00 | 0.000 |
| gpt4o | 3200 | 3.38 | 0.49 | 0.00 | 0.00 | 0.000 |
| llama | 3200 | 3.36 | 0.64 | 0.00 | 0.00 | 0.000 |

## Bias Effects

| Judge | Position Bias | Verbosity Bias | Combined | Interaction Ratio | Effect |
|-------|--------------|----------------|----------|-------------------|--------|
| claude | 0.265 | 0.183 | 0.000 | 0.00 | cancelling |
| deepseek | 0.108 | 0.197 | 0.000 | 0.00 | cancelling |
| gemini | 0.310 | 0.308 | 0.000 | 0.00 | cancelling |
| gpt4o | 0.240 | 0.155 | 0.000 | 0.00 | cancelling |
| llama | 0.363 | 0.325 | 0.000 | 0.00 | cancelling |

## Score Distribution

| Judge | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|
| claude | 0 | 0 | 1948 | 1252 | 0 |
| deepseek | 0 | 0 | 1858 | 1342 | 0 |
| gemini | 0 | 0 | 1742 | 1458 | 0 |
| gpt4o | 0 | 0 | 1970 | 1230 | 0 |
| llama | 0 | 285 | 1485 | 1430 | 0 |

## Key Findings

- **Cancelling biases**: claude, deepseek, gemini, gpt4o, llama — biases partially offset
- **Average degradation across judges**: 0.000