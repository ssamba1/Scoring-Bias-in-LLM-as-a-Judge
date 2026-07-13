# Ethics Statement

## Research Ethics Compliance

### Human Subjects
This research does NOT involve human subjects. All evaluation items are synthetically generated or adapted from public benchmarks. No human annotators, survey participants, or user data are involved.

### Data Privacy
- No personally identifiable information (PII) is collected or stored
- No user interaction data is used
- All generated data is synthetic
- No cookies, tracking, or analytics are deployed

### API Usage
- All API usage follows each provider's terms of service
- Rate limits are respected with exponential backoff
- No abusive or prohibited content is submitted
- API keys are stored locally and never shared

### Model Usage
- Open-weight models (Llama 3, Mistral, Gemma 2) are used in accordance with their respective licenses
- No model weights are redistributed
- All model access is through official channels

### Environmental Impact
- Estimated compute: ~$10-26 in cloud resources
- Carbon footprint: negligible (< 5 kg CO2 equivalent)
- We use efficient inference practices (batch processing, temperature=0)

### Bias and Fairness
- This research studies AI bias to improve fairness, not to amplify it
- We test models from multiple providers to avoid vendor-specific conclusions
- Our findings are reported transparently with all limitations acknowledged

### Dual Use
- Understanding scoring bias helps build fairer AI evaluation systems
- Our methodology could theoretically be used to exploit bias, but this is no different from existing knowledge
- We believe the benefits of transparent bias research outweigh potential misuse risks

### Reproducibility
- All code is openly available at github.com/ssamba1/research-draft
- Synthetic data generation is fully deterministic (seed=42)
- Experimental protocols are documented in the runbook
- Temperature=0 ensures deterministic judge responses

## ISEF Ethics Requirements
- [x] No human subjects
- [x] No vertebrate animals
- [x] No hazardous materials
- [x] No controlled substances
- [x] No human/animal tissue
- [x] Minimal environmental impact
- [x] All software/data properly licensed

## Approval Status
This project qualifies for expedited/automated approval under ISEF rules as it involves no human subjects, animals, or hazardous materials.
