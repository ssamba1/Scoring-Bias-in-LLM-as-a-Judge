# Reproduction environment

## Two empty keys in the patching files

`patch_results.json` and `patch_results_qwen05.json` carry `"raw": []` and
`"per_layer_gap_closed": {}`. Both are empty because the harness initialised them and
never wrote to them — not because per-item patching data was withheld or lost. Nothing
reads either key, and the measurements the causal claim rests on are
`frac_toward_instruct`, `median_recovery`, `n_items_used` and `best_layer`, all present.
The harness no longer emits the unused keys. The released files are left exactly as they
were produced, because they are the record of what ran.


## Two runs record failures, and one of them leaves a shell entry

`gold_results.json` and `results_closed.json` are the only released runs whose
`errors` block is non-empty. Both failures are real and neither changes a
reported number, but only one of them was written down anywhere a reader would
see.

**The ground-truth run lost StableLM-2-1.6B.** Both its checkpoints failed with
`AttributeError: 'StableLmConfig' object has no attribute 'pad_token_id'`, a
known quirk of that config. The file still carries a `StableLM-2-1.6B` entry
holding `params_b` and nothing else, so counting the models in the file gives
six while only five have data. The ground-truth analysis therefore rests on five
families: SmolLM2-360M, Qwen2.5-0.5B, Falcon3-1B, Qwen2.5-1.5B and Qwen2.5-3B.
No number in the paper claims otherwise — the section quotes accuracies and
margins, not a family count — but the shell entry makes the panel look larger
than it is, and that is worth stating rather than leaving in a raw file.

**The frontier run lost qwen-2.5-72b-instruct** to a 404 from the provider. That
one was already disclosed: `results_closed_analysis.json` lists it under
`excluded` with the reason, and the paper says Claude and Gemini expose no
logprobs.

`tests/test_recorded_failures_are_disclosed.py` requires any run that records a
failure to name it here, and any model entry with no condition data to be named
as well.

## The local gate is not evidence about CI

`verify_like_ci.py` runs what the GitHub workflow runs, and it is what every
verification claim in this repository's commit history rests on. It has one
blind spot, and it hid a real failure for as long as the run history goes back:
it builds its own pinned virtualenv, so it installs exactly what the suite needs
and cannot fail the way a runner fails when the workflow installs too little.

That is what happened. The integrity job installed pytest alone, the suite grew
tests importing numpy and scipy, and collection died on the runner before any
check ran — while the local gate reported 8/8 every time. Fixed 2026-08-14, with
`tests/test_ci_installs_what_the_suite_imports.py` comparing what the suite
imports at module level against what the workflow installs.

Read the local gate as what it is: a check that the analyses reproduce and the
paper matches its data on one machine. Whether the workflow passes is a separate
fact, visible only in the Actions tab.

## Seven declared panel sizes cannot be checked from the released files

Thirteen raw files declare `n_items`, the panel each cell was scored on and the
denominator of every mean in the file. Six of them also store per-item score
vectors, so the declaration is checkable against the data, and
`tests/test_the_item_panel_is_what_the_paper_says.py` checks every vector in
them.

The other seven — `results_chat.json`, `results_gran.json`, `results_t10.json`,
`results_tokvar.json`, `patch_results.json`, `patch_results_qwen05.json` and
`spanpatch_results.json` — record only aggregates, because their harnesses wrote
one mean per cell and never wrote the per-item scores. Nothing in the release
can therefore confirm that those runs used the panel they declare. This is a
limitation of what was recorded, not withheld data, and the missing vectors are
not reconstructible after the fact; producing them any other way would be
fabrication.

The set is pinned in `tests/test_a_declared_panel_is_checkable_or_recorded.py`,
so it can shrink when a harness starts recording vectors but cannot grow
silently.

The analysis stack is pinned in [`requirements-repro.txt`](requirements-repro.txt):

    numpy==2.4.4   scipy==1.17.1   statsmodels==0.14.6

Everything under `paper/honest/repro/` is CPU-only. The raw data is committed, so no GPU and
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
| `results_mechanism.json` | `link_points.resp` | 0.6995 | 0.6996 |
| `results_mechanism.json` | `link_points.resp` | 0.1083 | 0.1084 |
| `results_mechanism.json` | `link_points.resp` | 0.3871 | 0.3872 |
| `results_mechanism.json` | `link_points.resp` | 0.2231 | 0.2230 |

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
