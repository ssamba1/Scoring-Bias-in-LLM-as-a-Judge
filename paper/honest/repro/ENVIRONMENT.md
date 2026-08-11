# Reproduction environment

The analysis stack is pinned in [`requirements-repro.txt`](requirements-repro.txt):

    numpy==2.4.4   scipy==1.17.1   statsmodels==0.14.6

Everything under `repro/` is CPU-only. The raw data is committed, so no GPU and
no API access are needed to reproduce any derived number in the paper.

## Where bit-exact reproduction is verified

On **Linux** with those pins. The `regenerate-and-diff` job in
[`.github/workflows/repro.yml`](../../../.github/workflows/repro.yml) reruns
every analysis on `ubuntu-latest` and fails if any derived JSON or LaTeX table
differs from what is committed, byte for byte. That is the guarantee behind the
paper's reproducibility claim, and it is checked on every push.

## Where it is not, and by how much

Reproducing on **Windows** with the same pins gives last-digit differences in two
files. Measured, not assumed -- numpy 2.4.4 / scipy 1.17.1 on Windows 11,
python 3.13:

| file | field | Linux (committed) | Windows |
|---|---|---|---|
| `results_stages_analysis.json` | Tulu-3-8B DPO `resp` | 0.4863 | 0.4862 |
| `results_stages_analysis.json` | OLMo-2-1B RLVR `resp` | 0.1967 | 0.1966 |
| `results_stages_analysis.json` | P7 SFT share | 0.839 | 0.84 |
| `results_mechanism.json` | 4 of 130 `link_points.resp` | e.g. 0.6995 | 0.6996 |

Eight values in total, all in the fourth decimal place, all in the
responsiveness term -- a mean of total-variation distances, where the summation
order and the platform's libm decide the last bit. The differences are
deterministic: rerunning on the same machine reproduces the same values exactly,
so this is a platform difference and not nondeterminism in the analysis.

**No number the paper reports changes.** Every affected value is quoted to two or
three decimals, and `check_prose.py` passes unmodified against the Windows
output -- including the "84--99%" SFT share, whose lower end is 0.839 on Linux
and 0.840 on Windows and rounds to 84 either way. The correlations these values
feed (responsiveness--bias rho=+0.82, the stage ladder) are unchanged at the
precision reported.

If you reproduce on Windows or macOS and `git diff` shows these eight values,
that is expected. A difference anywhere else is not, and is worth reporting.

## Not pinned

The measurement runs (`*_harness.py`) used torch 2.6.0+cu124 and transformers
4.49.0 on Kaggle T4 GPUs; the frontier judges were queried through the
OpenRouter API. Neither is needed to reproduce the paper from the committed raw
data, and neither is expected to reproduce bit-exactly -- GPU kernels and remote
APIs do not promise that. `results_*.json` are the record of those runs.
