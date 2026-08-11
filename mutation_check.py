#!/usr/bin/env python3
"""Do the guards fail when the thing they protect breaks?

A suite reports "all passed" whether or not its assertions could ever fail. This
repository has a specific reason to care: it published fabricated data, and the
tests added afterwards are the only thing standing between that and a repeat. A
guard that cannot fail is worse than no guard, because it is believed.

For each entry below: break the protected thing, run the named test file, and
require it to FAIL. A mutation that leaves the test green is a guard to rewrite.

Every mutation also runs against the unmutated tree first (the BASE column). A
test that was already failing would otherwise look like a successful catch.

Nothing is left modified. The original bytes are written to `.mutation_stash/`
before the file is touched, so an out-of-band kill is recoverable, and restored
in a `finally`.

    python mutation_check.py [-v]
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
STASH = BASE / ".mutation_stash"
MANIFEST = STASH / "manifest.json"

# (file, find, replace, test file, label)
MUTATIONS = [
    (
        # A fabricated model name reappears in a live file. This is the exact
        # regression that mattered: ranking_table.html sat in the live tree for
        # two weeks listing Qwen3-14B, a model that does not exist.
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct (GLM-4.7)</h2>",
        "tests/test_no_fabricated_artefacts.py",
        "fabricated model name returns to a live page",
    ),
    (
        # The fabricated per-domain values return, by value rather than by name.
        # Written literally: the first attempt inserted "1.52 &amp; 0.98" and the
        # sweep correctly did not match it, because the entity puts "amp;"
        # between the number and the ampersand. The mutation was wrong, not the
        # guard -- which is the whole reason to run mutations against a baseline.
        "paper/interactive/index.html",
        '<span class="tag chart">paired chart</span>',
        '<span class="tag chart">paired chart 1.52 & 0.98</span>',
        "tests/test_no_fabricated_artefacts.py",
        "fabricated domain values return",
    ),
    (
        # The quarantine loses its explanation. Moving files without saying why
        # is not a retraction.
        "RETRACTED/README.md",
        "do not use or cite",
        "archived materials",
        "tests/test_no_fabricated_artefacts.py",
        "retraction notice loses its warning",
    ),
    (
        # A whole quarantined group stops being described. This one needs every
        # occurrence replaced: the path appears three times, and the guard only
        # asks whether it appears at all, so mutating the first left the test
        # satisfied by the other two and the guard looked broken when it was not.
        "RETRACTED/README.md",
        "paper/interactive/",
        "paper/elsewhere/",
        "tests/test_no_fabricated_artefacts.py",
        "quarantined group undocumented",
        True,
    ),
    (
        # The paper is edited without repackaging: the archive is now stale and
        # would ship the previous text.
        "paper/honest/scoring_bias_v2.tex",
        "\\section*{Reproducibility}",
        "\\section*{Reproducibility and Data}",
        "tests/test_submission_is_buildable.py",
        "paper edited without repackaging",
    ),
    (
        # A small-n rank correlation drifts to where the choice of p-value method
        # decides the verdict. This is the shape of the defect that moved a
        # companion paper's claim from the significant side of 0.05 to the other.
        "paper/honest/repro/results_peritem.json",
        '"spearman_p": 0.8301',
        '"spearman_p": 0.049',
        "tests/test_small_n_statistics.py",
        "small-n correlation drifts near 0.05",
    ),
    (
        # The paper claims more evidence than the release contains. This is the
        # defect class the audit found in the fabricated version -- inflated
        # scale -- and until now nothing connected the prose to the data.
        "paper/honest/scoring_bias_v2.tex",
        "over 56{,}000 scored judgments",
        "over 560{,}000 scored judgments",
        "tests/test_scale_claims_match_the_data.py",
        "paper overstates how many judgments exist",
    ),
    (
        # The family count drifts away from the panel actually run. \NFAM is a
        # macro, so this is written once -- but a macro is only single-source,
        # not verified.
        "paper/honest/macros.tex",
        "\\newcommand{\\NFAM}{13}",
        "\\newcommand{\\NFAM}{19}",
        "tests/test_scale_claims_match_the_data.py",
        "family count drifts from the panel",
    ),
    (
        # The checkpoint count drifts in one of the three places it is written.
        # Mutating the body copy leaves the two in macros.tex correct, so this
        # also proves the guard reads more than the first occurrence.
        "paper/honest/scoring_bias_v2.tex",
        "26 checkpoints",
        "40 checkpoints",
        "tests/test_scale_claims_match_the_data.py",
        "checkpoint count drifts in one place of three",
    ),
    (
        # A derived file drops out of the diff list. This is the regression that
        # actually happened: results_14b_analysis.json was committed, cited by
        # the paper for "positive for 3/5 probes", and compared against nothing.
        ".github/workflows/repro.yml",
        "paper/honest/repro/results_14b_analysis.json",
        "paper/honest/repro/results_zh_analysis.json",
        "tests/test_every_derived_file_is_reproduced.py",
        "derived file drops out of the diff list",
    ),
    (
        # The file is still diffed but no longer regenerated, so the diff
        # compares it to itself and passes forever. A reproduction gate that
        # cannot fail is the failure mode this whole file exists to catch.
        ".github/workflows/repro.yml",
        "analyze_newprobes.py results_14b.json",
        "analyze_newprobes.py results_zh.json",
        "tests/test_every_derived_file_is_reproduced.py",
        "derived file diffed but never regenerated",
    ),
    (
        # A citation points at an identifier that resolves to nothing. The
        # retracted version cited works that did not exist, and a bad identifier
        # compiles silently -- LaTeX reports an undefined key, never a key
        # pointing somewhere false.
        "paper/honest/honest.bib",
        "eprint    = {2411.15594}",
        "eprint    = {2413.15594}",
        "tests/test_citations_are_well_formed.py",
        "citation points at a nonexistent arXiv id",
    ),
    (
        # The quotation drifts back to the inexact wording. The source says
        # "scoring bias"; the paper had pluralised it and added "these". A
        # quotation that still reads correctly is the kind nobody re-checks.
        "paper/honest/scoring_bias_v2.tex",
        "the underlying causes of scoring bias remain",
        "the underlying causes of these scoring biases remain",
        "tests/test_quotation_integrity.py",
        "quotation drifts from its source wording",
    ),
    (
        # The mischaracterisation returns: Thakur et al.'s judges are all
        # instruction-tuned, and the claim that they compared base vs instruct
        # judges describes this paper's design, not theirs.
        "paper/honest/scoring_bias_v2.tex",
        "thirteen instruction-tuned judges on answers from both base and instruction-tuned",
        "base and instruct judges differ, and more besides",
        "tests/test_quotation_integrity.py",
        "cited work's design mischaracterised again",
    ),
    (
        # The ethics statement reverts to claiming every model is open-weight
        # while the frontier run queries GPT-4o through a commercial API.
        "paper/honest/scoring_bias_v2.tex",
        "No human subjects. The \\NFAM-family panel and every ablation use public open-weight",
        "No human subjects. All models are public open-weight checkpoints, and every ablation uses",
        "tests/test_ethics_matches_the_experiments.py",
        "ethics claims every model is open-weight",
    ),
    (
        # A registered prediction stops being mentioned. This is the regression
        # that had already happened: P4 was registered, its result computed, and
        # the paper never connected the two.
        # Every mention has to go: the first attempt replaced only the "preregistered
        # P4" clause and the guard correctly stayed green, because the very next
        # clause still says "so P4 holds". replace_all is the point here.
        "paper/honest/macros.tex",
        "P4",
        "P4x",
        "tests/test_preregistration_is_reported.py",
        "registered prediction loses its reported outcome",
        True,
    ),
    (
        # The registered grouping stops being reported, leaving only the wider
        # one the analysis uses -- so P4 has no verdict on its own terms.
        "paper/honest/macros.tex",
        "authority and verbosity alone; restricted to those two probes as registered,",
        "these probes; restricted to them,",
        "tests/test_preregistration_is_reported.py",
        "registered grouping replaced by the wider one",
    ),
    (
        # A local regeneration overwrites CI's value for a tie-prone entry. This
        # is the exact byte that turned the reproduction gate red for five
        # consecutive commits.
        "paper/honest/repro/results_mechanism.json",
        "      0.6995,",
        "      0.6996,",
        "tests/test_analysis_stack_matches_the_pins.py",
        "local regeneration overwrites CI's rounding",
    ),
    (
        # A second file's tie-prone value. Found by regenerating into a scratch
        # copy and diffing, before CI ever saw it -- so this mutation proves the
        # guard covers the values that have not yet gone wrong, not only the four
        # that did.
        "paper/honest/repro/results_stages_analysis.json",
        '"resp": 0.4863,',
        '"resp": 0.4862,',
        "tests/test_analysis_stack_matches_the_pins.py",
        "tie-prone value drifts in a second file",
    ),
    (
        # The external dataset loses its licence attribution. CC BY-SA asks for
        # it whether or not the text itself is redistributed.
        "paper/honest/macros.tex",
        "(Databricks, CC BY-SA 3.0; open",
        "(open",
        "tests/test_third_party_data_is_attributed.py",
        "third-party dataset loses its attribution",
    ),
    (
        # A person-level property returns to the top level, which is exactly what
        # made the record fail CFF validation and be ignored by GitHub/Zenodo.
        "CITATION.cff",
        "doi: 10.5281/zenodo.21499823",
        "orcid: \"\"\ndoi: 10.5281/zenodo.21499823",
        "tests/test_citation_metadata_is_valid.py",
        "citation record invalid again (misplaced orcid)",
    ),
    (
        # The citation record advertises the withdrawn, fabricated Zenodo version.
        "CITATION.cff",
        "doi: 10.5281/zenodo.21499823",
        "doi: 10.5281/zenodo.21361920",
        "tests/test_citation_metadata_is_valid.py",
        "citation record points at the retracted archive",
    ),
    (
        # The badge advertises a licence the repository does not carry.
        "README.md",
        "badge/License-MIT-1a1a2e",
        "badge/License-CC_BY_4.0-1a1a2e",
        "tests/test_release_surfaces_agree.py",
        "readme badge contradicts the LICENSE file",
    ),
    (
        # The README's scale reverts to the model's row count.
        "README.md",
        "19,500 per-item scores",
        "13,000 per-item scores",
        "tests/test_release_surfaces_agree.py",
        "readme scale stops matching the released panel",
    ),
    (
        # One cell of the main table stops matching the value it was generated
        # from. The whole point of pinning per cell is that this names the cell.
        "paper/honest/tables/tab_v2_family.tex",
        "Granite-3.1-2B & 2 & SFT+RLHF & 0.8 & 0.7",
        "Granite-3.1-2B & 2 & SFT+RLHF & 0.8 & 1.9",
        "tests/test_cited_tables_are_pinned.py",
        "a single table cell drifts from its source",
    ),
    (
        # The table's metadata column disagrees with the data: this family's
        # training recipe is what the base-vs-instruct claim rests on.
        "paper/honest/tables/tab_v2_family.tex",
        "OLMo-2-7B & 7 & SFT+DPO+RLVR",
        "OLMo-2-7B & 7 & SFT",
        "tests/test_cited_tables_are_pinned.py",
        "table metadata disagrees with the data",
    ),
    (
        # A headline effect size drifts in the summary table.
        "paper/honest/tables/tab_v2_summary.tex",
        "Rubric order & 0.32 & 0.55",
        "Rubric order & 0.32 & 0.95",
        "tests/test_summary_tables_are_pinned.py",
        "summary table effect size drifts",
    ),
    (
        # A confidence interval's lower endpoint changes sign, turning an
        # interval that contains zero into one that excludes it. A guard
        # comparing magnitudes would pass this; that is why it compares signed.
        "paper/honest/tables/tab_v2_summary.tex",
        "[-0.09, +0.75]",
        "[+0.09, +0.75]",
        "tests/test_summary_tables_are_pinned.py",
        "CI endpoint flips sign (contains zero -> excludes)",
    ),
    (
        # The domain breakdown stops matching its source.
        "paper/honest/tables/tab_v2_domain.tex",
        "Daily Life & 0.44 & 0.70",
        "Daily Life & 0.44 & 0.90",
        "tests/test_summary_tables_are_pinned.py",
        "domain table cell drifts",
    ),
    (
        # The ground-truth degradation table stops matching its source.
        "paper/honest/tables/tab_gold.tex",
        "Verbose & 0.70 & 0.73",
        "Verbose & 0.70 & 0.93",
        "tests/test_summary_tables_are_pinned.py",
        "ground-truth table cell drifts",
    ),
    (
        # A stored condition mean stops matching the per-item scores it was
        # computed from. Every analysis reads these `mean` fields rather than
        # the arrays, so a wrong one propagates into every table and headline
        # with nothing downstream able to notice.
        "paper/honest/repro/results_scaled.json",
        '"mean": 2.8754',
        '"mean": 3.4754',
        "tests/test_effects_recompute_from_raw.py",
        "stored mean contradicts its own per-item scores",
    ),
    (
        # A per-family effect in the sensitivity analysis diverges from what the
        # raw scores give.
        "paper/honest/repro/results_robustness.json",
        '"Falcon3-3B": 0.489',
        '"Falcon3-3B": 0.589',
        "tests/test_effects_recompute_from_raw.py",
        "per-family effect diverges from the raw scores",
    ),
    (
        # The forest plot's point estimate stops matching the recomputation --
        # and lands outside its own confidence interval.
        "paper/honest/repro/results_robustness.json",
        '"effect": 0.578',
        '"effect": 1.578',
        "tests/test_effects_recompute_from_raw.py",
        "forest point estimate leaves its own interval",
    ),
    # ---- guards that had never been exercised -------------------------------
    # A file-level mutation proves the file can fail, not that each guard inside
    # it can. Measuring per test FUNCTION showed 35 of 72 proven and 37 never
    # touched; the entries below were written for the untouched ones.
    (
        "paper/honest/repro/dolly_harness.py",
        "databricks-dolly-15k, CC BY-SA 3.0",
        "databricks-dolly-15k, public domain",
        "tests/test_third_party_data_is_attributed.py",
        "harness stops recording the dataset licence",
    ),
    (
        "CITATION.cff",
        "license: MIT",
        "license: Apache-2.0",
        "tests/test_release_surfaces_agree.py",
        "citation record contradicts the LICENSE file",
    ),
    (
        "paper/honest/scoring_bias_v2.tex",
        "two proprietary models (GPT-4o-mini, GPT-4o)",
        "two hosted models (GPT-4o-mini, GPT-4o)",
        "tests/test_ethics_matches_the_experiments.py",
        "ethics stops disclosing closed-weight judges",
    ),
    (
        "paper/honest/scoring_bias_v2.tex",
        "plus under US\\$2 of API calls",
        "plus a negligible amount of API usage",
        "tests/test_ethics_matches_the_experiments.py",
        "ethics drops the cost the appendix discloses",
    ),
    (
        "paper/honest/macros.tex",
        "\\newcommand{\\MAXB}{8}",
        "\\newcommand{\\MAXB}{4}",
        "tests/test_scale_claims_match_the_data.py",
        "parameter range excludes models actually run",
    ),
    (
        "paper/honest/macros.tex",
        "five bias types",
        "six bias types",
        "tests/test_scale_claims_match_the_data.py",
        "bias-type count drifts from the probes run",
        True,
    ),
    (
        # A family disappears from the table: the per-cell cases would simply
        # stop being generated, so only the completeness guard can catch it.
        "paper/honest/tables/tab_v2_family.tex",
        "SmolLM2-360M & 0.36 & SFT+DPO & 0.2 & 0.3 & 1.6 & 2.4 & 0.1 & 0.0 & 0.2 & 0.1 & 0.1 & 0.3 \\\\",
        "",
        "tests/test_cited_tables_are_pinned.py",
        "family silently dropped from the table",
    ),
    (
        "paper/honest/tables/tab_v2_domain.tex",
        "Daily Life & 0.44 & 0.70 \\\\",
        "",
        "tests/test_summary_tables_are_pinned.py",
        "domain silently dropped from the table",
    ),
    (
        "paper/honest/repro/results_robustness.json",
        '"full_mean_effect": 0.257',
        '"full_mean_effect": 0.357',
        "tests/test_effects_recompute_from_raw.py",
        "headline effect diverges from the raw scores",
    ),
    (
        # The paper claims a registration number that was never registered.
        "paper/honest/macros.tex",
        "This is preregistered P4",
        "This is preregistered P25",
        "tests/test_preregistration_is_reported.py",
        "paper invents a preregistration id",
    ),
    # ---- replication arms, one per arm so each guard is exercised -----------
    (
        # The deployed-judge arm: the largest biases the project reports.
        "paper/honest/repro/results_closed_analysis.json",
        '"rubric_order": 1.483',
        '"rubric_order": 2.483',
        "tests/test_replication_arms_recompute.py",
        "frontier judge delta diverges from raw scores",
    ),
    (
        "paper/honest/repro/results_zh_analysis.json",
        '"mean_base": 0.415',
        '"mean_base": 0.915',
        "tests/test_replication_arms_recompute.py",
        "Chinese replication diverges from raw scores",
    ),
    (
        "paper/honest/repro/results_probes2_analysis.json",
        '"mean_base": 0.799',
        '"mean_base": 0.299',
        "tests/test_replication_arms_recompute.py",
        "new-probe suite diverges from raw scores",
    ),
    (
        "paper/honest/repro/results_14b_analysis.json",
        '"mean_base": 0.343',
        '"mean_base": 0.843',
        "tests/test_replication_arms_recompute.py",
        "14B extension diverges from raw scores",
    ),
    (
        "paper/honest/repro/results_robustness.json",
        '"SmolLM2-135M": 0.19,',
        '"SmolLM2-135M": 0.59,',
        "tests/test_replication_arms_recompute.py",
        "public-item effect diverges from raw scores",
    ),
    # ---- bibliography and vacuity guards -----------------------------------
    (
        # A citation key that resolves to no entry. LaTeX reports this too, but
        # only when the paper is rebuilt; the suite should not need a build.
        "paper/honest/scoring_bias_v2.tex",
        "\\citet{thakur2024judging} evaluated",
        "\\citet{thakur2024judgingX} evaluated",
        "tests/test_citations_are_well_formed.py",
        "citation key resolves to no bibliography entry",
    ),
    (
        # Two entries share a key: BibTeX silently keeps one, so a citation
        # quietly resolves to the wrong work.
        "paper/honest/honest.bib",
        "@article{gu2024survey,",
        "@article{li2025scoring,",
        "tests/test_citations_are_well_formed.py",
        "two bibliography entries share a key",
    ),
    (
        # An entry loses its only identifier. falcon3 is cited as a release page
        # with no arXiv id, DOI or venue, so its url is the single thing a
        # reader can follow; howpublished names where it lives but resolves to
        # nothing. (A multi-line anchor was tried first and went stale: this
        # file is CRLF in the working tree, so "\n" matched nothing. Single-line
        # anchors do not have that problem.)
        "paper/honest/honest.bib",
        "  url    = {https://huggingface.co/blog/falcon3}, month = {December}, year = {2024}",
        "  month = {December}, year = {2024}",
        "tests/test_citations_are_well_formed.py",
        "cited work left with nothing a reader can follow",
    ),
    # ---- one per retraction signature ---------------------------------------
    # The sweep carries eleven patterns, each naming a specific artefact from
    # the fabricated version. Two of them were exercised; a pattern that has
    # never caught anything is indistinguishable from one that no longer can.
    # Each entry below puts that signature's own artefact back into a live page
    # -- the exact regression each pattern exists to stop -- and requires the
    # sweep to find it. They share an anchor because they are applied one at a
    # time and restored between runs.
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct (DeepSeek-V4-Flash)</h2>",
        "tests/test_no_fabricated_artefacts.py",
        "signature: DeepSeek-V4 returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        '<h2>Base vs Instruct</h2><!-- name:"Qwen3-14B" -->',
        "tests/test_no_fabricated_artefacts.py",
        "signature: Qwen3-* returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct (Llama-4-Scout)</h2>",
        "tests/test_no_fabricated_artefacts.py",
        "signature: Llama-4* returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct</h2><!-- Science 0.52 & 0.65 & 0.38 -->",
        "tests/test_no_fabricated_artefacts.py",
        "signature: 22-model domain table returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct across the 22-model landscape</h2>",
        "tests/test_no_fabricated_artefacts.py",
        "signature: 22-model landscape claim returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct</h2><p>40,500 judgments</p>",
        "tests/test_no_fabricated_artefacts.py",
        "signature: inflated judgment count returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct</h2><p>across 31 variants</p>",
        "tests/test_no_fabricated_artefacts.py",
        "signature: 31-variant claim returns",
    ),
    (
        "paper/interactive/index.html",
        "<h2>Base vs Instruct</h2>",
        "<h2>Base vs Instruct</h2><!-- Student A, Student B -->",
        "tests/test_no_fabricated_artefacts.py",
        "signature: placeholder authorship returns",
    ),
    (
        # The licence changes in the file while the badge and citation record
        # keep advertising the old one -- the same disagreement as before, but
        # arriving from the other direction.
        "LICENSE",
        "MIT License",
        "Apache License",
        "tests/test_release_surfaces_agree.py",
        "LICENSE changes, badge and record do not",
    ),
    (
        # The citation record gains a key the CFF schema does not define, which
        # is what made it invalid before: additionalProperties is false.
        "CITATION.cff",
        "cff-version: 1.2.0",
        "cffversion: 1.2.0",
        "tests/test_citation_metadata_is_valid.py",
        "citation record gains an unschema'd key",
    ),
    (
        # A second small-n correlation drifts into the band where the choice of
        # p-value method decides the verdict. The first such mutation covers one
        # correlation; the scan is meant to cover every one of them.
        "paper/honest/repro/results_peritem.json",
        '"spearman_p": 0.7268',
        '"spearman_p": 0.062',
        "tests/test_small_n_statistics.py",
        "a second small-n correlation drifts near 0.05",
    ),
    (
        # The ethics statement keeps the word "proprietary" but stops naming
        # which judges are proprietary, so a reader cannot tell what was used.
        "paper/honest/scoring_bias_v2.tex",
        "two proprietary models (GPT-4o-mini, GPT-4o)",
        "two proprietary models (names withheld)",
        "tests/test_ethics_matches_the_experiments.py",
        "ethics stops naming the closed-weight judges",
    ),
    # ---- reaching the "is this reading real data" guards ---------------------
    # These exist to fail when a parse silently returns less than it should, and
    # none had ever been made to do it. Dropping one scored item from the panel,
    # and renaming one frontier judge, is enough -- and both anchors carry \r\n
    # because these files are CRLF in the working tree.
    (
        "paper/honest/repro/results_scaled.json",
        "\r\n              2.3313,",
        "",
        "tests/test_effects_recompute_from_raw.py",
        "a scored item vanishes from the panel",
    ),
    (
        "paper/honest/repro/results_scaled.json",
        "\r\n              2.3313,",
        "",
        "tests/test_release_surfaces_agree.py",
        "panel shrinks below the count the README states",
    ),
    (
        # Every closed judge has to be renamed, not one: with gpt-4o still in
        # the roster the study is still using a proprietary judge, so the guard
        # was right to stay green on the first attempt at this.
        "paper/honest/repro/results_closed_analysis.json",
        '"gpt-4o',
        '"open-4o',
        "tests/test_ethics_matches_the_experiments.py",
        "roster no longer contains any closed judge",
        True,
    ),
    (
        "paper/honest/repro/results_closed_analysis.json",
        '"gpt-4o-mini"',
        '"open-4o-mini"',
        "tests/test_replication_arms_recompute.py",
        "a frontier judge drops out of the arm",
    ),
    # ---- one per published headline number -----------------------------------
    # The prose gate compares each of these against the derived JSON. Until it
    # was wrapped in a test it could not be reached by this harness at all, so
    # no drifted headline number had ever been demonstrated to be caught. Each
    # entry drifts one published figure in the paper's own text.
    (
        "paper/honest/macros.tex",
        "entropy $2.04\\!\\to\\!1.45$ bits",
        "entropy $2.14\\!\\to\\!1.45$ bits",
        "tests/test_prose_matches_derived_values.py",
        "headline: entropy before tuning drifts",
    ),
    (
        "paper/honest/macros.tex",
        "falls from $2.04$ to $1.45$ bits",
        "falls from $2.04$ to $1.35$ bits",
        "tests/test_prose_matches_derived_values.py",
        "headline: entropy after tuning drifts",
    ),
    (
        "paper/honest/macros.tex",
        "with bias ($\\rho=-0.41$",
        "with bias ($\\rho=-0.51$",
        "tests/test_prose_matches_derived_values.py",
        "headline: entropy-bias correlation drifts",
    ),
    (
        "paper/honest/macros.tex",
        "$\\sqrt{\\mathrm{Var}_\\sigma(v)}$ ($\\rho=-0.25$",
        "$\\sqrt{\\mathrm{Var}_\\sigma(v)}$ ($\\rho=-0.35$",
        "tests/test_prose_matches_derived_values.py",
        "headline: variance-term correlation drifts",
    ),
    (
        "paper/honest/macros.tex",
        "11/13 families; Fig.~\\ref{fig:mech}a",
        "12/13 families; Fig.~\\ref{fig:mech}a",
        "tests/test_prose_matches_derived_values.py",
        "headline: decisiveness family count drifts",
    ),
    (
        "paper/honest/macros.tex",
        "$d_z=1.44$, 12/13 families",
        "$d_z=1.44$, 13/13 families",
        "tests/test_prose_matches_derived_values.py",
        "headline: responsiveness family count drifts",
    ),
    (
        "paper/honest/macros.tex",
        "positive in 24/26 checkpoints",
        "positive in 25/26 checkpoints",
        "tests/test_prose_matches_derived_values.py",
        "headline: within-checkpoint count drifts",
    ),
    (
        "paper/honest/macros.tex",
        "rank correlation $\\rho=0.58$",
        "rank correlation $\\rho=0.68$",
        "tests/test_prose_matches_derived_values.py",
        "headline: predictor rank correlation drifts",
    ),
    (
        "paper/honest/macros.tex",
        "gives $R^2=0.27$",
        "gives $R^2=0.37$",
        "tests/test_prose_matches_derived_values.py",
        "headline: predictor R^2 drifts",
    ),
    (
        "paper/honest/macros.tex",
        "(positive in 8/9 remaining families)",
        "(positive in 9/9 remaining families)",
        "tests/test_prose_matches_derived_values.py",
        "headline: excluding-Qwen count drifts",
    ),
    (
        "paper/honest/macros.tex",
        "gives $+0.29$ (9/10)",
        "gives $+0.29$ (10/10)",
        "tests/test_prose_matches_derived_values.py",
        "headline: >=1B family count drifts",
    ),
    (
        "paper/honest/macros.tex",
        "a majority (12/20) of the cells",
        "a majority (14/20) of the cells",
        "tests/test_prose_matches_derived_values.py",
        "headline: decrease-cell count drifts",
    ),
    (
        "paper/honest/macros.tex",
        "recomputed on the control variant alone it is $\\rho=-0.34$",
        "recomputed on the control variant alone it is $\\rho=-0.44$",
        "tests/test_prose_matches_derived_values.py",
        "headline: control-variant correlation drifts",
    ),
    # Every remaining published figure, one mutation each. A gate that covers
    # only the numbers that happened to get attention is a gate with a shape
    # nobody chose.
    (
        "paper/honest/macros.tex", "0.15\\!\\to\\!0.26", "0.15\\!\\to\\!0.36",
        "tests/test_prose_matches_derived_values.py", "headline: responsiveness rise drifts",
    ),
    (
        "paper/honest/macros.tex", "d_z=1.44", "d_z=1.54",
        "tests/test_prose_matches_derived_values.py", "headline: responsiveness effect size drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=+0.82", "\\rho=+0.92",
        "tests/test_prose_matches_derived_values.py", "headline: responsiveness-bias rho drifts",
    ),
    (
        "paper/honest/macros.tex", "coefficient $+0.16$", "coefficient $+0.26$",
        "tests/test_prose_matches_derived_values.py", "headline: mixed-model coefficient drifts",
    ),
    (
        "paper/honest/macros.tex", "n=13{,}000", "n=14{,}000",
        "tests/test_prose_matches_derived_values.py", "headline: mixed-model n drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=-0.38", "\\rho=-0.48",
        "tests/test_prose_matches_derived_values.py", "headline: size-partialled rho drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=+0.18", "\\rho=+0.28",
        "tests/test_prose_matches_derived_values.py", "headline: size-bias rho drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=-0.51", "\\rho=-0.61",
        "tests/test_prose_matches_derived_values.py", "headline: sub-1B band rho drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=+0.64", "\\rho=+0.74",
        "tests/test_prose_matches_derived_values.py", "headline: within-checkpoint responsiveness drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=-0.05", "\\rho=-0.15",
        "tests/test_prose_matches_derived_values.py", "headline: within-checkpoint entropy drifts",
    ),
    (
        "paper/honest/macros.tex", "\\rho=0.56", "\\rho=0.66",
        "tests/test_prose_matches_derived_values.py", "headline: readout concordance drifts",
    ),
    (
        "paper/honest/macros.tex", "0.00098", "0.00198",
        "tests/test_prose_matches_derived_values.py", "headline: exact permutation p drifts",
    ),
    (
        "paper/honest/macros.tex", "59\\%", "69\\%",
        "tests/test_prose_matches_derived_values.py", "headline: marginalization mitigation drifts",
        True,
    ),
    (
        "paper/honest/macros.tex", "increases} it to $1.88$", "increases} it to $1.98$",
        "tests/test_prose_matches_derived_values.py", "headline: argmax readout drifts",
    ),
    (
        "paper/honest/scoring_bias_v2.tex", "\\rho=-0.45", "\\rho=-0.55",
        "tests/test_prose_matches_derived_values.py", "headline: frontier pooled rho drifts",
    ),
    (
        "paper/honest/macros.tex", "n=145", "n=155",
        "tests/test_prose_matches_derived_values.py", "headline: frontier pooled n drifts",
        True,
    ),
    (
        "paper/honest/macros.tex", "positive for 3/5 probes", "positive for 4/5 probes",
        "tests/test_prose_matches_derived_values.py", "headline: 14B probe count drifts",
    ),
    (
        "paper/honest/macros.tex", "mean bias in 4/4 families", "mean bias in 3/4 families",
        "tests/test_prose_matches_derived_values.py", "headline: prereg-analyzer family count drifts",
    ),
    (
        "paper/honest/macros.tex", "base to SFT in 10/10", "base to SFT in 9/10",
        "tests/test_prose_matches_derived_values.py", "headline: SFT stage cell count drifts",
    ),
    (
        "paper/honest/macros.tex", "mean bias in 7/8 families", "mean bias in 6/8 families",
        "tests/test_prose_matches_derived_values.py", "headline: public-item family count drifts",
    ),
    (
        # Most entries stop parsing, so the bibliography checks would run on a
        # nearly empty set and pass without examining anything.
        "paper/honest/honest.bib",
        "@inproceedings{",
        "%inproceedings{",
        "tests/test_citations_are_well_formed.py",
        "bibliography parse collapses to a few entries",
        True,
    ),
    (
        # The retraction vocabulary stops matching its own example, which is the
        # one thing that proves the sweep can still fire.
        "tests/fabricated_signatures.py",
        '"GLM-4.7": (r"GLM-4\\.7", "Zhipu GLM-4.7 & 9B")',
        '"GLM-4.7": (r"GLM-4\\.8", "Zhipu GLM-4.7 & 9B")',
        "tests/test_no_fabricated_artefacts.py",
        "retraction pattern stops matching its own sample",
    ),
    (
        # The pinned array grows, so the recorded indices no longer identify the
        # values they were recorded for.
        "paper/honest/repro/results_mechanism.json",
        '"resp": [\n      0.0271,',
        '"resp": [\n      0.0271,\n      0.0271,',
        "tests/test_analysis_stack_matches_the_pins.py",
        "pinned indices stop identifying their values",
    ),
    (
        # The reproduction stack stops being pinned at all.
        "paper/honest/repro/requirements-repro.txt",
        "scipy==1.17.1",
        "scipy",
        "tests/test_analysis_stack_matches_the_pins.py",
        "numeric stack no longer pinned",
    ),
    (
        # Every registered prediction stops parsing, so the compliance check
        # would run on an empty list and report success.
        "paper/honest/PREREGISTRATION.md",
        "- **P",
        "- **Q",
        "tests/test_preregistration_is_reported.py",
        "prediction list stops parsing",
        True,
    ),
    (
        # The paper's quotations stop parsing, making the quotation checks
        # vacuous rather than failing.
        "paper/honest/scoring_bias_v2.tex",
        "``",
        "`",
        "tests/test_quotation_integrity.py",
        "quotation sweep collapses to nothing",
        True,
    ),
]


def _stash(rel: str, data: bytes):
    STASH.mkdir(exist_ok=True)
    target = STASH / rel.replace("/", "__")
    target.write_bytes(data)
    MANIFEST.write_text(json.dumps({"file": rel, "stash": target.name}), encoding="utf-8")


def _clear_stash():
    shutil.rmtree(STASH, ignore_errors=True)


def _run(test_file: str):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-q", "--no-header", "-x"],
        cwd=BASE,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return result.returncode


def main(verbose=False):
    if not (BASE / "tests").is_dir():
        raise SystemExit("no tests/ directory")

    print(f"{'mutation':46s} {'BASE':>5} {'MUT':>5}  verdict")
    print("-" * 72)

    misses, stale = [], []
    for entry in MUTATIONS:
        rel, find, replace, test_file, label = entry[:5]
        replace_all = len(entry) > 5 and entry[5]
        path = BASE / rel
        if not path.exists():
            stale.append(f"{label}: {rel} absent")
            continue
        # Bytes throughout. Reading as text and writing it back rewrites CRLF
        # line endings as LF, which leaves the tree dirty after a run that is
        # supposed to restore it exactly -- a mutation harness that edits the
        # files it restores is not one to trust.
        original = path.read_bytes()
        find_b, replace_b = find.encode("utf-8"), replace.encode("utf-8")
        if find_b not in original:
            stale.append(f"{label}: anchor not found in {rel}")
            print(f"{label:46s} {'-':>5} {'-':>5}  ** STALE ANCHOR **")
            continue
        if original.count(find_b) > 1 and not replace_all:
            print(f"  (note: {label} anchor occurs {original.count(find_b)}x; first is mutated)")

        base_rc = _run(test_file)
        _stash(rel, original)
        try:
            count = -1 if replace_all else 1
            path.write_bytes(original.replace(find_b, replace_b, count))
            mutated_rc = _run(test_file)
        finally:
            path.write_bytes(original)
            _clear_stash()

        caught = base_rc == 0 and mutated_rc != 0
        verdict = "ok" if caught else ("BASE ALREADY RED" if base_rc != 0 else "NOT CAUGHT")
        if not caught:
            misses.append(label)
        print(f"{label:46s} {base_rc:>5} {mutated_rc:>5}  {verdict}")

    print()
    if stale:
        print("mutations whose anchor no longer matches:", stale)
    if misses:
        print("guards that did NOT catch their mutation:", misses)
        return 1
    checked = len(MUTATIONS) - len(stale)
    print(f"every guard caught its mutation ({checked} checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main("-v" in sys.argv))
