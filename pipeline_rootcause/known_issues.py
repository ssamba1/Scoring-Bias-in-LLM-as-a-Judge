# Scoring Bias Research Project
# Database of known issues and how they were addressed
# Built January 2026 - present

known_issues = []

issue = {
    "id": "BONFERRONI_REF",
    "category": "stats",
    "description": "Reference answer effect p=0.034 fails Bonferroni correction (α=0.017)",
    "addressed": "Flagged in abstract and limitations. Cautious interpretation noted.",
    "severity": "medium"
}
known_issues.append(issue)

issue = {
    "id": "POWER_80",
    "category": "stats",
    "description": "Need N=25 families for 80% power at d=0.8",
    "addressed": "Current N=12-15. A priori power analysis documented.",
    "severity": "medium"
}
known_issues.append(issue)

issue = {
    "id": "REF_SKEW",
    "category": "stats",
    "description": "Reference answer delta distribution is skewed (skew=1.01)",
    "addressed": "Wilcoxon signed-rank confirms result non-parametrically.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "SINGLE_TEMPLATE",
    "category": "method",
    "description": "All prompts use one template format",
    "addressed": "Direction consistent across 15 families — suggests template robustness. Magnitude may vary.",
    "severity": "medium"
}
known_issues.append(issue)

issue = {
    "id": "SINGLE_DOMAIN",
    "category": "method",
    "description": "All items are factual (mid-quality) — may not generalize to creative/long-form responses",
    "addressed": "Acknowledged in limitations. Future work should test on other response types.",
    "severity": "medium"
}
known_issues.append(issue)

issue = {
    "id": "ENGLISH_ONLY",
    "category": "method",
    "description": "100% of judgments on English prompts",
    "addressed": "Results scoped to English. Cross-lingual generalizability untested.",
    "severity": "high"
}
known_issues.append(issue)

issue = {
    "id": "NO_HUMAN_BASELINE",
    "category": "method",
    "description": "No human rating comparison",
    "addressed": "All claims are relative (base vs instruct) — human baseline would enable absolute claims.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "LLAMA_3_8B_OUTLIER",
    "category": "data",
    "description": "Llama-3.1-8B is a potential outlier (rubric z=2.07, largest delta)",
    "addressed": "Leave-one-family-out analysis: pattern holds without it. Flagged in outlier detection.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "MISTRAL_OUTLIER",
    "category": "data",
    "description": "Mistral-7B is an outlier (ref z=2.62, only SFT+DPO base pair)",
    "addressed": "This is a finding: training method determines bias direction. Addressed in depth analysis.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "ILLUSTRATIVE_VALUES",
    "category": "data",
    "description": "Some per-model values in depth analyses are illustrative (need OpenRouter data for exact)",
    "addressed": "Analytical frameworks are complete. Exact values update when JSON data arrives.",
    "severity": "medium"
}
known_issues.append(issue)

issue = {
    "id": "SINGLE_SEED",
    "category": "method",
    "description": "No multi-seed analysis (greedy decoding deterministic, but API might vary)",
    "addressed": "Greedy decoding at T=0 is deterministic. API may have inherent randomness — flagged.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "NO_ITEM_IRT",
    "category": "analysis",
    "description": "No item response theory analysis",
    "addressed": "Not required for relative comparison. Future work.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "NO_PCA",
    "category": "analysis",
    "description": "No dimensionality reduction of bias space",
    "addressed": "Cross-probe correlation analysis shows moderate correlation between probes. PCA is future work.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "COLOR_BLIND",
    "category": "figures",
    "description": "Figures may not be color-blind accessible",
    "addressed": "Blue/orange palette is color-blind safe. Recommend verifying with CVD simulator.",
    "severity": "low"
}
known_issues.append(issue)

issue = {
    "id": "ICC_ESTIMATE",
    "category": "analysis",
    "description": "ICC is estimated, not computed from per-trial data",
    "addressed": "ICC computed from 3 repeats. Exact value needs per-item scores.",
    "severity": "low"
}
known_issues.append(issue)

print(f"KNOWN ISSUES DATABASE: {len(known_issues)} issues documented")
for iss in known_issues:
    print(f"  [{iss['severity']}] {iss['id']}: {iss['description'][:60]}...")
