# Scoring Bias VSCode Extension  Concept

## Overview

A VSCode extension that detects and highlights potential scoring bias
when using LLM-as-a-Judge for evaluation tasks. The extension helps
researchers and practitioners identify when their evaluation rubrics,
score labels, or reference answers may introduce systematic bias.

## Key Features

### 1. Inline Annotation
- Hover over rubric text to see predicted bias score
- Color-coded indicators: green (low bias), yellow (medium), red (high)
- Warnings when rubric order may reverse score direction

### 2. Evaluation Preview
- Side panel shows bias landscape for the current model
- Pre-computed delta values from the 22-model study
- Compare your rubric against published benchmarks

### 3. Reproducibility Checker
- Validates evaluation configuration against best practices
- Suggests rubric formats that minimize bias
- Flags potential confounds (e.g., all-normal conditions)

## Architecture (Concept)

```
Extension Host
├── activationEvents: ["onLanguage:json", "onLanguage:markdown"]
├── main.ts  Activation, commands, tree views
├── biasProvider.ts  Data provider for bias landscape
├── inlineAnnotator.ts  Document decoration provider
└── telemetry.ts  Optional anonymous usage stats

Data:
├── biasData.json  Pre-computed deltas for 22 models
├── rubricPatterns.json  Known bias patterns
└── modelProfiles.json  Model metadata
```

## Commands

| Command | Description |
|---------|-------------|
| `scoringBias.showLandscape` | Open bias landscape view |
| `scoringBias.checkRubric` | Analyze current rubric for bias |
| `scoringBias.compareModels` | Compare two models side-by-side |
| `scoringBias.exportReport` | Export bias analysis as JSON |

## How to Use

1. Install from VS Code Marketplace (pending)
2. Open a rubric JSON or markdown evaluation config
3. The extension automatically annotates bias-prone sections
4. Open the Scoring Bias panel from the activity bar

## Development Status

**Concept only**  Not implemented. This document outlines the
proposed extension for future development.

## Related Resources

- Full paper: [arXiv:2607.xxxxx](https://arxiv.org/abs/2607.xxxxx)
- Data: Pre-computed bias deltas for 22 models
- Dashboard: Streamlit-based interactive explorer
