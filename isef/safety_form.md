# ISEF Safety and Ethics Statement

## Project: Scoring Bias in LLM-as-a-Judge Models

**Researcher:** Sricharan Samba
**Institution:** South Forsyth High School
**Category:** Systems Software

---

### Safety Compliance Declaration

This project presents **NO safety hazards** of any kind. Below is a complete checklist of ISEF safety categories:

| Category | Status | Notes |
|----------|--------|-------|
| Hazardous Chemicals | ❌ Not Used | No chemicals, reagents, or hazardous materials |
| Fire / Explosives | ❌ Not Used | No open flames, explosives, or combustion |
| High Voltage / Electrical | ❌ Not Used | Standard computer hardware only |
| Sharp Objects | ❌ Not Used | No blades, needles, or sharps |
| Human Subjects | ❌ Not Involved | No surveys, interviews, or user studies |
| Vertebrate Animals | ❌ Not Involved | No animal testing or observation |
| Recombinant DNA | ❌ Not Used | No biological materials |
| Human/Animal Tissue | ❌ Not Used | No tissue samples |
| Controlled Substances | ❌ Not Used | No drugs or regulated substances |
| Radioactive Materials | ❌ Not Used | No radiation sources |
| Lasers | ❌ Not Used | No laser devices |
| Biohazards (BSL-1+) | ❌ Not Used | No microorganisms or pathogens |

---

### Research Ethics Statement

This research was conducted in accordance with the NeurIPS Code of Ethics and ISEF ethical guidelines.

#### Data Privacy
- No personally identifiable information (PII) was collected or stored
- No human interaction data of any kind was used
- All evaluation items are synthetic or adapted from public, open benchmarks
- No cookies, tracking, or analytics were deployed

#### Model Usage
- All models used are publicly available open-weight models
- Model usage follows each provider's terms of service and licensing
- No model weights are redistributed
- OpenRouter API usage followed rate limits with exponential backoff
- Total API cost was under $3 USD

#### Environmental Impact
- Primary compute on Kaggle T4 GPU (educational free tier)
- Supplementary compute via OpenRouter API (minimal per-call cost)
- Estimated carbon footprint: negligible (< 5 kg CO₂ equivalent)
- Greedy decoding (temperature 0) minimized unnecessary computation

#### Dual Use Considerations
- This research studies AI bias to improve fairness and reliability of automated evaluation
- Understanding scoring bias helps build more trustworthy AI evaluation systems
- The benefits of transparent bias research substantially outweigh any potential dual-use concerns
- All findings are reported transparently with quantified limitations

#### Reproducibility
- All code, data, and analysis are publicly available
- Random seed 42 ensures fully deterministic experimental pipeline
- Complete reproduction instructions available in the GitHub repository
- Docker image provided for environment consistency

---

### ISEF Approval Category

This project qualifies for **expedited/automated approval** under ISEF rules as it involves:
- No human subjects (Category 4 exemption)
- No vertebrate animals (Categories 5A–5E exemption)
- No hazardous materials or biohazards
- Only computational research using publicly available models and data

**Approval Status:** No SRC/IRB approval needed.

---

### Emergency Contact

In the unlikely event of a safety concern:
- **Researcher:** Sricharan Samba — srisamba09@gmail.com
- **School:** South Forsyth High School, Cumming, GA
- **Safety Mentor:** Available upon request
