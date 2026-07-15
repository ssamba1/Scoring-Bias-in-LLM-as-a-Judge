# arXiv Submission: Where Does Scoring Bias Come From?

**Author:** Sricharan Samba  
**arXiv ID:** 2607.xxxxx  
**Date:** July 2026  

---

## Files Included

- **main.tex**  Full manuscript (20 pages, two-column, camera-ready)
- **fig1_framework.html** through **fig8_mitigation.html**  Publication figures
- **metadata.yaml**  arXiv submission metadata
- **submit.sh**  Automated submission script

## How to Reproduce

1. Clone: `git clone https://github.com/ssamba1/Scoring-Bias-in-LLM-as-a-Judge`
2. Generate figures: `python3 paper/generate_png_figures.py`
3. Compile PDF: `cd paper && pdflatex main.tex && pdflatex main.tex`

## Citation

```bibtex
@article{samba2026scoring,
  title={Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge},
  author={Samba, Sricharan},
  journal={arXiv preprint},
  year={2026}
}
```

## License

CC-BY 4.0
