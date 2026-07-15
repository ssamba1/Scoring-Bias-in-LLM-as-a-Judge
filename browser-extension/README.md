# Scoring Bias Browser Extension  Concept

## Overview

A browser extension that shows scoring bias scores for LLM evaluation
platforms (Chatbot Arena, MT-Bench leaderboard, LMSYS, etc.). The
extension overlays bias information directly on evaluation results.

## Key Features

### 1. Bias Badges
- Small badges next to model evaluation scores
- Shows bias direction (lenient/strict) and magnitude
- Color-coded: green (low bias), yellow (medium), red (high)

### 2. Popup Dashboard
- Click extension icon to see overall bias landscape
- Filter by probe type (rubric order, score ID, reference answer)
- Search specific models

### 3. Export
- Copy bias data for selected models
- Export as CSV or JSON for further analysis

## Architecture (Concept)

```
Browser Extension
├── manifest.json  Permissions, content scripts
├── popup/
│   ├── index.html  Popup UI
│   ├── popup.js  Popup logic
│   └── styles.css
├── content/
│   ├── content.js  Page injection
│   └── annotator.js  DOM manipulation
└── data/
    └── biasData.json  Pre-computed bias values
```

## Data Flow

1. Extension loads `biasData.json` on install
2. Content script detects evaluation platforms by URL pattern
3. Annotator matches model names on the page
4. Bias badges are injected next to model scores
5. Clicking a badge opens detailed probe breakdown

## Supported Platforms (Planned)

- Chatbot Arena / LMSYS
- MT-Bench Leaderboard
- Open LLM Leaderboard
- Hugging Face model cards

## Development Status

**Concept only**  Not implemented. This document outlines the
proposed extension for future development.

## Privacy

- No data collection
- All data stored locally
- No network requests after install
- Open source
