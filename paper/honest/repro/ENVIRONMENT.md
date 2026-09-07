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

Fourteen raw files declare `n_items`, the panel each cell was scored on and the
denominator of every mean in the file. Seven of them also store per-item score
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

## Why the two totals above read low until 2026-09-07

They said thirteen and six. Fourteen files declare `n_items` and seven of them
store per-item vectors. The one both totals missed records its vectors under
`ev_per_item` and `sampled_per_item` rather than the literal `per_item` key, so
a count looking for that one spelling does not see it. This is the third
undercount in this repository from the same cause: two per-item detectors were
widened for it, and `.hermes.md` reported ten released files carrying score
vectors where eleven do.

Worth separating, because the two halves failed differently. **The disclosure
itself never moved.** Seven declared panels are unverifiable, and the seven
files named above are exactly the seven the data says -- that list is derived
from a guard whose key matcher was already broad enough. What drifted was the
arithmetic framing it, which is the half nobody re-reads, sitting beside the
half everybody does. All four counts in that section -- including the number in
its heading, which states it a second time -- now recompute in
`tests/test_a_declared_panel_is_checkable_or_recorded.py`.

(This section is deliberately not part of the disclosure above. The guard reads
the disclosure section for filenames and treats each as a panel it covers, so a
file named there in passing would read as a claim that it is unverifiable. The
first version of this correction did exactly that and was caught.)

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
| `results_mechanism.json` | `link_points.resp[18]` | 0.1083 | 0.1084 |
| `results_mechanism.json` | `link_points.resp[61]` | 0.1465 | 0.1466 |
| `results_mechanism.json` | `link_points.resp[91]` | 0.3825 | 0.3826 |
| `results_mechanism.json` | `link_points.resp[92]` | 0.2231 | 0.2230 |

Four values in total, all in the fourth decimal place, all in the
responsiveness term -- a mean of total-variation distances, where the summation
order and the platform's libm decide the last bit. The differences are
deterministic: rerunning on the same machine reproduces the same values exactly,
so this is a platform difference and not nondeterminism in the analysis.

**No number the paper reports changes.** Every affected value is quoted to two or
three decimals, and `check_prose.py` passes unmodified against the Windows
output. The correlations these values feed (responsiveness--bias rho=+0.82, the
stage ladder) are unchanged at the precision reported.

This list was larger and is now smaller, for a reason worth recording. It used to
include three `results_stages_analysis.json` entries and the P7 SFT share, whose
lower end was 0.839 on Linux against 0.840 on Windows. Correcting the
score-ordering bug moved every responsiveness figure, and the stage values landed
off the rounding boundary they had been sitting on: the reproduction gate now
regenerates them identically on both platforms. The SFT share is 0.871 in both,
so the share the paper quotes is 87--94% and no longer straddles a tie. Platform
divergence here is a property of where a value falls relative to a rounding
boundary, not a fixed set of fields -- entries can leave this table as well as
join it, and `resp[61]` joined it.

If you reproduce on Windows or macOS and `git diff` shows these eight values,
that is expected. A difference anywhere else is not, and is worth reporting.

## Not pinned

The measurement runs (`*_harness.py`) used torch 2.6.0+cu124 and transformers
4.49.0 on Kaggle T4 GPUs; the frontier judges were queried through the
OpenRouter API. Neither is needed to reproduce the paper from the committed raw
data, and neither is expected to reproduce bit-exactly -- GPU kernels and remote
APIs do not promise that. `results_*.json` are the record of those runs.
