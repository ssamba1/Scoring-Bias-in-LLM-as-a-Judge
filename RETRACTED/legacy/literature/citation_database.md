# LLM-as-a-Judge Bias Research  Complete Citation Database

## 30+ References with DOI Links

---

### Foundational Papers

1. **Zheng, L.**, Chiang, W., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E., Zhang, H., Gonzalez, J., & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*.
   - arXiv: 2306.05685
   - DOI: 10.48550/arXiv.2306.05685

2. **Wang, P.**, Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Liu, Q., Liu, T., & Sui, Z. (2023). Large Language Models are not Fair Evaluators. *ACL 2024*.
   - arXiv: 2305.17926
   - DOI: 10.48550/arXiv.2305.17926
   - Cited: 1039+

3. **Gu, J.** et al. (2024). From Generation to Judgment: Opportunities and Challenges of LLM-as-a-Judge.
   - arXiv: 2411.15594
   - DOI: 10.48550/arXiv.2411.15594

### Bias Taxonomies

4. **Ye, J.**, Wang, Y., Huang, Y., Chen, D., Zhang, Q., Moniz, N., Gao, T., Geyer, W., Huang, C., Chen, Z., & others. (2024). Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge. *NeurIPS SafeGenAI Workshop 2024*.
   - arXiv: 2409.19112

5. **Park, J.**, Jwa, S., Meiying, R., Kim, D., & Choi, S. (2024). OffsetBias: Leveraging Debiased Data for Tuning Evaluators. *EMNLP 2024 Findings*.
   - DOI: 10.18653/v1/2024.findings-emnlp.61

6. **Chen, D.** et al. (2024). CALM: A Comprehensive Evaluation of Bias in LLM-as-a-Judge.
   - arXiv: 2410.02736

### Position Bias

7. **Shi, L.**, Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S. (2025). Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. *AACL-IJCNLP 2025*.
   - arXiv: 2406.07791
   - Key number: 15 judges × 150K instances

### Our Direct Gaps

8. **Li, Q.**, Dou, S., Shao, K., Chen, C., & Hu, H. (2025). Evaluating Scoring Bias in LLM-as-a-Judge. *DASFAA 2026*.
   - arXiv: 2506.22316
   - DOI: 10.48550/arXiv.2506.22316
   - **OUR GAP: Explicitly calls for root cause analysis**

9. **Soumik, R.** (2026). Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge. *TMLR 2026*.
   - arXiv: 2604.23178
   - **OUR GAP: Explicitly notes bias interactions as future work**

### Bias Detection & Mitigation

10. **Yang, H.**, Bao, R., Xiao, C., Ma, J., Bhatia, P., Gao, S., & Kass-Hout, T. (2025). Any Large Language Model Can Be a Reliable Judge: Debiasing with a Reasoning-based Bias Detector. *NeurIPS 2025*.
    - arXiv: 2505.17100
    - Key numbers: 31.3% verbosity, 15% sentiment, 12.9% position, 12.5% bandwagon

11. **Feuer, B.**, Rosenblatt, L., & Elachqar, O. (2026). Towards Provably Unbiased LLM Judges via Bias-Bounded Evaluation.
    - arXiv: 2603.05485

12. **Dev, S.** et al. (2026). Judge Reliability Harness: Stress Testing the Reliability of LLM Judges. *ICLR 2026 Workshop*.
    - arXiv: 2603.05399

### Root Cause (Our Methodology Validation)

13. **Pan, X.**, Fan, J., Xiong, Z., Hahami, E., Overwiening, J., & Xie, Z. (2025). User-Assistant Bias in LLMs. *ACL 2026 Findings*.
    - arXiv: 2508.15815
    - **Key:** Validates base-vs-instruct comparison methodology
    - Tested 52 models; found base models near-neutral, instruct models strongly biased

### Self-Preference & Family Bias

14. **Wataoka, K.**, Takahashi, T., & Ri, R. (2024). Self-Preference Bias in LLM-as-a-Judge. *NeurIPS SafeGenAI Workshop 2024*.

15. **Panickssery, A.** et al. (2024). LLM Evaluators Recognize and Favor Their Own Generations. *NeurIPS 2024*.

### Cross-Cultural & Multilingual

16. **Doğruöz, A.S.**, Liao, X., Blaschke, V., Prange, J., Li, S., & Adelani, D.I. (2026). Challenges and Recommendations for LLMs-as-a-Judge in Multilingual Settings and Low-Resource Languages.
    - arXiv: 2607.02235
    - Key: Only 33/650 papers focus on multilingual

### Score Range & Calibration

17. **Fujinuma, Y.** et al. (2026). Score Range Bias in LLM-as-a-Judge.

18. **Xu, C.** et al. (2026). Rubric Position Bias in LLM Evaluators.
    - arXiv: 2602.02219

### Surveys

19. **Li, Q.** et al. (2025). From Holistic Evaluation to Structured Criteria: A Survey of Rubrics Across the Evolving LLM Landscape.
    - arXiv: 2606.08625

### High School Projects

20. **AAVENUE** (2024). Detecting LLM Biases on NLU Tasks in AAVE via a Novel Benchmark. *NeurIPS High School Projects 2024*.
    - **Key:** High school students CAN do LLM bias research at top venues

### Other Related

21. **Zhao, Z.** et al. (2026). Bias in the Loop: A Framework for Analyzing LLM Judge Bias.
    - arXiv: 2604.16790

22. **Baek, C.** et al. (2026). AI Rater Discrimination: A Study of Bias in LLM Evaluation.
    - arXiv: 2606.03198

23. **Zhu, J.** et al. (2026). CyclicJudge: A Framework for Robust LLM Evaluation.
    - arXiv: 2603.01865

24. **Kim, S.** et al. (2024). Prometheus: Inducing Fine-grained Evaluation Capability in Language Models. *ICLR 2024*.

25. **Kim, S.** et al. (2024). Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models.

26. **Dubois, Y.** et al. (2024). AlpacaEval: An Automatic Evaluator of Instruction-following Models.

27. **Bai, Y.** et al. (2022). Constitutional AI: Harmlessness from AI Feedback. *arXiv:2212.08073*.

28. **Koo, R.** et al. (2024). Benchmarking Cognitive Biases in Large Language Models.

29. **Echterhoff, J.** et al. (2024). Anchoring Bias in LLM Evaluation.

30. **Tripathi, T.** et al. (2025). Pairwise or Pointwise? Evaluating Feedback Protocols for Bias in LLM-based Evaluation.
    - arXiv: 2504.14716

---

## How to Cite in Your Paper

```bibtex
@inproceedings{zheng2023judging,
  title={Judging {LLM-as-a-Judge} with {MT}-Bench and Chatbot Arena},
  author={Zheng, Lianmin and Chiang, Wei-Lin and Sheng, Ying and others},
  booktitle={NeurIPS},
  year={2023}
}

@article{li2025scoring,
  title={Evaluating Scoring Bias in {LLM-as-a-Judge}},
  author={Li, Qingquan and Dou, Shaoyu and Shao, Kailai and Chen, Chao and Hu, Haixiang},
  journal={arXiv preprint arXiv:2506.22316},
  year={2025}
}

@article{yang2025reliable,
  title={Any Large Language Model Can Be a Reliable Judge},
  author={Yang, Haoyan and Bao, Runxue and Xiao, Cao and others},
  journal={arXiv preprint arXiv:2505.17100},
  year={2025}
}

@article{pan2025user,
  title={User-Assistant Bias in {LLMs}},
  author={Pan, Xu and Fan, Jingxuan and Xiong, Zidi and others},
  journal={arXiv preprint arXiv:2508.15815},
  year={2025}
}

@article{soumik2026judging,
  title={Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies},
  author={Soumik, R.},
  journal={TMLR},
  year={2026}
}

@inproceedings{wang2023large,
  title={Large Language Models are not Fair Evaluators},
  author={Wang, Peiyi and Li, Lei and Chen, Liang and others},
  booktitle={ACL},
  year={2024}
}

@inproceedings{shi2025judging,
  title={Judging the Judges: A Systematic Study of Position Bias},
  author={Shi, Lin and Ma, Chiyu and Liang, Wenhua and others},
  booktitle={AACL-IJCNLP},
  year={2025}
}
```
