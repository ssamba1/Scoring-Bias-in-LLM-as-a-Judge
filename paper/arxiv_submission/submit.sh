#!/bin/bash
# arXiv upload helper
# 1. tar the package: tar -czf submission.tar.gz arxiv_submission/
# 2. Upload to https://arxiv.org/submit
# 3. Fill in the web form with the metadata below

echo "Submission package ready:"
echo "  tar -czf submission.tar.gz arxiv_submission/"
echo ""
echo "METADATA:"
echo "  Title: Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge"
echo "  Authors: Student A, Student B"
echo "  Primary class: cs.CL"
echo "  Secondary classes: cs.AI, cs.LG, stat.ML"
echo "  License: http://arxiv.org/licenses/nonexclusive-distrib/1.0/"
