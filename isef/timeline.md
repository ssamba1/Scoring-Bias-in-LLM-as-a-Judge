# Gantt Chart — Bias Interaction Experiment

## Timeline Overview

```
Week 1      Week 2      Week 3      Week 4      Week 5      
├───────────┼───────────┼───────────┼───────────┼───────────┤
│Setup &    │Data       │Data       │Analysis   │Paper &    
│Pilot      │Collection │Collection │+ Figures  │Submission 
│           │(Judge 1-3)│(Judge 4-5)│           │          
```

## Detailed Schedule

### Week 1: Setup & Pilot
```
Day 1     Day 2     Day 3     Day 4     Day 5     Day 6     Day 7
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│Install   │Get API  │Test     │Generate  │Run      │Run 10-  │Analyze  │
│deps +    │keys +   │API      │items     │synthetic│item     │pilot    │
│clone repo│config   │connect- │(already  │pilot    │probe    │results  │
│          │         │ivity    │done)     │         │         │         │
```

### Week 2: Data Collection (Judges 1-3)
```
Day 8     Day 9     Day 10    Day 11    Day 12    Day 13    Day 14
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│Run       │Continue  │Run       │Continue  │Run       │Continue  │Quality  │
│Gemini    │Gemini    │DeepSeek  │DeepSeek  │Llama 3   │Llama 3   │check +  │
│(~30 min) │(if needed)│(~30 min)│(if needed)│(~30 min)│(if needed)│backup   │
```

### Week 3: Data Collection (Judges 4-5) + Begin Analysis
```
Day 15    Day 16    Day 17    Day 18    Day 19    Day 20    Day 21
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│Run       │Continue  │Run       │Continue  │Analyze   │Analyze   │Draft    │
│GPT-4o    │GPT-4o    │Claude    │Claude    │results   │results   │results  │
│(~2 hrs)  │(if needed)│(~2 hrs) │(if needed)│so far    │all judges│section  │
```

### Week 4: Analysis & Figures
```
Day 22    Day 23    Day 24    Day 25    Day 26    Day 27    Day 28
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│Run full  │Generate  │Create   │Write    │Write    │Write    │Edit +   │
│analysis  │figures   │tables   │intro +  │results  │discuss- │proofread│
│pipeline  │(6 plots) │+ stats  │related  │section  │ion      │paper    │
│          │          │         │work     │         │         │         │
```

### Week 5: Paper & Submission
```
Day 29    Day 30    Day 31    Day 32    Day 33    Day 34    Day 35
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│Convert   │Create   │Final    │Submit   │Respond  │Submit   │Celebrate│
│to LaTeX  │ISEF     │review   │to arXiv │to       │to ISEF  │🎉       │
│          │materials│+ polish │         │reviewers│/science │         │
│          │         │         │         │         │fair     │         │
```

## Milestones

| Milestone | Week | Deliverable |
|-----------|------|-------------|
| M1 | 1 | Pilot complete — pipeline verified |
| M2 | 2 | 3 judges scored — preliminary patterns visible |
| M3 | 3 | All 5 judges scored — data collection complete |
| M4 | 4 | Analysis complete — key findings confirmed |
| M5 | 5 | Paper submitted to arXiv |

## Task Dependencies

```
Setup (W1) ──> Gemini (W2) ──> DeepSeek (W2) ──> Llama (W2) ──> GPT-4o (W3) ──> Claude (W3) ──> Analysis (W4) ──> Paper (W5)
                    │                │                │                │                │
                    └────────────────┴────────────────┴────────────────┴────────────────┘
                                 All must complete before analysis
```

## Resource Loading

| Resource | W1 | W2 | W3 | W4 | W5 |
|----------|----|----|----|----|----|
| Student A | 50% | 30% | 30% | 50% | 50% |
| Student B | 50% | 30% | 30% | 50% | 50% |
| API budget | $0 | $3 | $23 | $0 | $0 |
