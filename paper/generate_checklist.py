#!/usr/bin/env python3
"""NeurIPS 2026 Paper Checklist — Auto-generated for Study 1.
Copy the output into the LaTeX file before submission.
"""
print("%" * 65)
print("% NEURIPS 2026 PAPER CHECKLIST — Study 1")
print("% Generated automatically — verify each answer")
print("%" * 65)
print()
print("\\begin{neurlipschecklist}")
print()
items = [
    ("1. Claims", "Do the main claims made in the abstract and introduction accurately reflect the paper's contributions and scope?",
     "Yes", "Our abstract and introduction state: instruction tuning has differential effects on scoring bias (format biases decrease 44-77%, content bias increases 35%). These claims are directly supported by our experimental results in Section 4 (Table 1). Scope is limited to 3 model families at 2-8B scale, as stated in Section 6 (Limitations)."),
    ("2. Limitations", "Does the paper point out any strong assumptions and how robust the results are to violations of these assumptions?",
     "Yes", "Section 6 (Limitations) discusses: (1) limited item count (50 vs benchmark standards), (2) 2-8B model scale only, (3) inability to distinguish SFT vs RLHF, (4) excluded descriptive probe variant, (5) English-only results, (6) single seed, (7) single prompt template, (8) no human baseline."),
    ("3. Theory", "If theoretical results are included, did you state the full set of assumptions and include complete proofs?",
     "No", "This paper is empirical (not theoretical). We do not present formal theorems. The IIAR hypothesis is conjectural and presented in the Discussion section."),
    ("4. Reproducibility", "If the contribution is a dataset or model, what steps did you take to make your results reproducible?",
     "Yes", "Complete reproduction steps: (1) All code at github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge, (2) Kaggle notebook at pipeline_rootcause/study1_full.kaggle.ipynb, (3) Fixed seed=42, temperature=0, (4) Tensor dtypes specified (float16), (5) GPU configuration documented (Kaggle T4, 17GB VRAM)."),
    ("5. Open data/code", "Did you include the code, data, and instructions needed to reproduce the main experimental results?",
     "Yes", "Complete open-source repository at github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge containing all code (MIT license), data (CC-BY 4.0), and detailed reproduction instructions in REPLICATION.md and GETTING_STARTED.md."),
    ("6. Experimental details", "Did you specify all the training details (data splits, hyperparameters, how they were chosen)?",
     "Yes", "Section 3 (Method) specifies: temperature=0, 3 repeats, 50 items, 3 probe variants. Hyperparameters chosen for determinism (temperature=0) and standard practice (3 repeats following prior work). No training — inference-only."),
    ("7. Statistical significance", "Does the paper report error bars suitably and correctly defined or other appropriate information about statistical significance?",
     "Yes", "We report: (1) Bootstrap 95% confidence intervals for all mean estimates, (2) Cohen's d effect sizes, (3) Standard Error of the Mean (SEM) on all bar charts, (4) Flip Rate (FR) matching Li et al. methodology."),
    ("8. Compute resources", "For each experiment, does the paper provide sufficient information on the computer resources needed to reproduce the experiments?",
     "Yes", "Section 3: Kaggle T4 GPU (NVIDIA Tesla T4, 17GB VRAM), ~6 hours total compute, ~$0 cost (Kaggle free tier). Transformers Inference API used for model loading."),
    ("9. Code of ethics", "Have you read the NeurIPS Code of Ethics and ensured that your research conforms to it?",
     "Yes", "We have read and conform to the NeurIPS Code of Ethics. This research involves no human subjects, no private data, and no potentially harmful applications."),
    ("10. Broader impact", "Did you include a discussion of the broader impact of your work?",
     "Yes", "Section 7 (Broader Impact) discusses: potential for over-reliance on biased judges, differential mitigation implications, adversarial prompt risks, and recommendations for practitioners."),
    ("11. Safeguards", "Did you discuss the potential negative societal impact of your work?",
     "Yes", "Section 7 discusses: (1) how findings could be used to construct adversarial prompts, (2) risk of blanket debiasing strategies backfiring, (3) systematic disadvantage to certain response types. We recommend transparent bias reporting."),
    ("12. Licenses", "Did you specify the licenses of all assets (code, data, models)?",
     "Yes", "Code: MIT license. Data: CC-BY 4.0. Models: Meta Llama 3 Community License (meta-llama), Apache 2.0 (Mistral), Gemma Terms of Use (Google). Licenses documented in repository and ethics statement."),
    ("13. New assets", "If releasing new assets, did you document them and provide these details?",
     "No", "We do not release new datasets or models. We use existing open-weight models and synthetic evaluation items. Our GitHub repository contains analysis code only."),
    ("14. Human subjects", "If you used crowdsourcing or conducted research with human subjects, did you include the full text of instructions?",
     "N/A", "This research did not involve human subjects or crowdsourcing. All experiments were conducted using automated pipelines with publicly available models."),
    ("15. IRB approvals", "Did you describe any potential participant risks and obtain IRB approvals?",
     "N/A", "No human subjects — IRB approval not required."),
    ("16. LLM usage", "Does the paper describe the usage of LLMs if it is an important, original, or non-standard component of the core methods?",
     "Yes", "LLMs are the OBJECT of study (as judges), not a tool used in our methods. Our core method is comparing model outputs under different prompt conditions, which does not rely on LLMs for analysis."),
]

for num, question, answer, justification in items:
    print("\\item[{\\textbf{" + num.split()[0] + ":}}]")
    print("  " + question)
    print()
    print("  \\textbf{Answer:} " + answer + ".")
    print()
    print("  \\textbf{Justification:} " + justification)
    print()

print("\\end{neurlipschecklist}")
