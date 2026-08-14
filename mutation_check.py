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
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
# The stash location is overridable so the guards on the lock can exercise a run
# of their own. Without it they cannot: a mutation run always holds a stash, so
# a guard reading the default location sees one and skips -- and a guard that
# skips whenever this checker is running is one this checker can never exercise.
# Tests set it; nothing else should.
STASH = BASE / os.environ.get("MUTATION_STASH_DIR", ".mutation_stash")
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
        # The published value was 0.15 and the data give 0.1446; corrected to
        # 0.14, so the anchor moves with it.
        "paper/honest/macros.tex", "0.14\\!\\to\\!0.26", "0.14\\!\\to\\!0.36",
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
    # Secondary and appendix figures: the ones a referee recomputes precisely
    # because nobody is watching them.
    (
        "paper/honest/macros.tex", "0.75$/$0.71", "0.85$/$0.71",
        "tests/test_prose_matches_derived_values.py", "secondary: score-ID flip rates drift",
    ),
    (
        "paper/honest/macros.tex", "0.22\\!\\to\\!0.38", "0.22\\!\\to\\!0.48",
        "tests/test_prose_matches_derived_values.py", "secondary: reference-answer flip rise drifts",
    ),
    (
        "paper/honest/macros.tex", "0.24\\!\\to\\!0.41", "0.24\\!\\to\\!0.51",
        "tests/test_prose_matches_derived_values.py", "secondary: authority flip rise drifts",
    ),
    (
        "paper/honest/macros.tex", "and $2.02$", "and $2.12$",
        "tests/test_prose_matches_derived_values.py", "secondary: frontier maximum drifts",
    ),
    (
        "paper/honest/macros.tex", "frontier mean bias ($0.89$)", "frontier mean bias ($0.99$)",
        "tests/test_prose_matches_derived_values.py", "secondary: frontier mean bias drifts",
    ),
    (
        "paper/honest/macros.tex", "open-instruct mean ($0.69$)", "open-instruct mean ($0.79$)",
        "tests/test_prose_matches_derived_values.py", "secondary: open-instruct mean drifts",
    ),
    (
        "paper/honest/macros.tex", "+0.26$", "+0.36$",
        "tests/test_prose_matches_derived_values.py", "secondary: panel mean effect drifts",
        True,
    ),
    (
        "paper/honest/macros.tex", "[-0.62", "[-0.72",
        "tests/test_prose_matches_derived_values.py", "secondary: predictor R^2 interval drifts",
    ),
    (
        "paper/honest/macros.tex", "(8/16 cells positive)", "(9/16 cells positive)",
        "tests/test_prose_matches_derived_values.py", "secondary: dose-response cells drift",
    ),
    (
        "paper/honest/macros.tex", "(3/8 pairs", "(4/8 pairs",
        "tests/test_prose_matches_derived_values.py", "secondary: dose-response slope pairs drift",
    ),
    (
        "paper/honest/macros.tex", "6/10 templates", "7/10 templates",
        "tests/test_prose_matches_derived_values.py", "secondary: template direction drifts",
    ),
    (
        "paper/honest/macros.tex", "raw in 4/6 cells", "raw in 5/6 cells",
        "tests/test_prose_matches_derived_values.py", "secondary: chat-template cells drift",
    ),
    (
        "paper/honest/macros.tex", "in only 1/3 families", "in only 2/3 families",
        "tests/test_prose_matches_derived_values.py", "secondary: chat-vs-raw families drift",
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
    (
        # A generated table changes and the archive is not rebuilt, so the
        # submission ships the previous numbers. The pinning tests catch a table
        # that contradicts its JSON, but not one that was regenerated correctly
        # and never repackaged -- there the tree is consistent and only the
        # archive is behind. Until the tables were digested, SOURCE.json listed
        # three top-level files and nothing compared the bundled tables at all.
        "paper/honest/tables/tab_v2_summary.tex",
        "+0.24 (+83",
        "+0.99 (+83",
        "tests/test_submission_is_buildable.py",
        "regenerated table ships stale in the archive",
    ),
    (
        # The README's scale claim drifts from the panel. The README is read far
        # more often than the paper and was covered by nothing; the quarantine
        # sweep found the retracted counts surviving longest in exactly the
        # places nobody thinks of as "the paper".
        "README.md",
        "26 checkpoints",
        "36 checkpoints",
        "tests/test_scale_claims_match_the_data.py",
        "README checkpoint count drifts from the panel",
    ),
    (
        # The main-panel score count drifts. This one is counted out of
        # results_scaled.json rather than compared to another prose copy of
        # itself, so a matching drift in both places still fails.
        "README.md",
        "19,500 per-item",
        "29,500 per-item",
        "tests/test_scale_claims_match_the_data.py",
        "README main-panel score count drifts",
    ),
    (
        # The overturned direction is asserted again on a live page. This is the
        # defect that survived three fabrication sweeps, because an honestly
        # measured number from a smaller slice looks nothing like a fabrication.
        "paper/interactive/base_vs_instruct.html",
        "bias mostly falls after instruction tuning",
        "instruction tuning reduces evaluation bias",
        "tests/test_superseded_claims_are_not_asserted.py",
        "superseded direction asserted on a live page",
    ),
    (
        # Items go missing from a raw file. The reproduction gate cannot see
        # this: the analyses would faithfully re-derive the result from the
        # shortened data and it would match what was committed, because the
        # gate compares derived JSON to derived JSON.
        "paper/honest/repro/results_14b.json",
        '"n_items": 50',
        '"n_items": 60',
        "tests/test_released_data_is_well_formed.py",
        "raw arrays no longer match the declared item count",
    ),
    (
        # The multiple-comparison column silently becomes Bonferroni. Every
        # printed value would still look like a plausible corrected p-value,
        # and the header would still say Holm. 5 x 0.0681 = 0.3405.
        "paper/honest/tables/tab_v2_summary.tex",
        "0.204 &",
        "0.341 &",
        "tests/test_holm_correction_is_correct.py",
        "Holm column becomes Bonferroni",
    ),
    (
        # The paper stops disclosing that one CI verdict depends on the
        # bootstrap draw. Reference answer's lower bound is -0.000, so whether
        # its interval excludes zero -- an asterisk in the summary table -- is
        # decided by the seed.
        "paper/honest/macros.tex",
        "not stable across bootstrap seeds",
        "stable across bootstrap seeds",
        "tests/test_bootstrap_verdicts_are_seed_stable.py",
        "seed-fragile CI verdict stops being disclosed",
    ),
    (
        # The exact test's p-value drifts to a value no enumeration over 13
        # families could produce. 0.0012 sits between 9/8192 and 10/8192 and
        # looks like a perfectly ordinary p-value.
        "paper/honest/repro/results_robustness.json",
        '"exact_p_two_sided": 0.00098',
        '"exact_p_two_sided": 0.0012',
        "tests/test_exact_permutation_test_is_exact.py",
        "exact p is not attainable at this n",
    ),
    (
        # The test becomes a Monte Carlo approximation while still being called
        # exact. Half the sign patterns is a plausible-looking resample count.
        "paper/honest/repro/results_robustness.json",
        '"n_patterns": 8192',
        '"n_patterns": 4096',
        "tests/test_exact_permutation_test_is_exact.py",
        "sampled test described as exact",
    ),
    (
        # The paper describes a random effect the model does not fit. This is
        # the defect the guard was written for: the prose claimed intercepts for
        # family AND item while the fit declares family alone, which describes a
        # more conservative model than was run.
        "paper/honest/macros.tex",
        "random intercept for family,",
        "random intercepts for family and item;",
        "tests/test_model_description_matches_the_fit.py",
        "paper claims a random effect the model lacks",
    ),
    (
        # A runner stops rerunning one of the analyses. This is the historical
        # defect exactly: results_14b_analysis.json was committed and cited
        # while no runner regenerated it.
        "run_all.sh",
        "analyze_closed.py",
        "analyze_closed_DISABLED.py",
        "tests/test_every_analysis_is_run_everywhere.py",
        "a runner stops rerunning an analysis",
    ),
    (
        # One of the four copies of the bias measure drifts to a different
        # statistic. Every file would still emit plausible numbers; only the
        # cross-file comparisons would stop meaning the same thing.
        "paper/honest/repro/analyze_stages.py",
        "return max(means.values()) - min(means.values())",
        "return sum(means.values()) / len(means)",
        "tests/test_the_bias_measure_matches_its_definition.py",
        "a copy of the bias measure drifts from the definition",
    ),
    (
        # A variance decomposition loses a component, so the shares no longer
        # sum to one. Every share still looks like a plausible proportion.
        "paper/honest/repro/results_robustness.json",
        '"family:probe": 0.368',
        '"family:probe": 0.168',
        "tests/test_stored_statistics_satisfy_their_identities.py",
        "a decomposition's shares stop summing to one",
    ),
    (
        # A specification-curve entry stops following from the panel. The curve
        # is the paper's answer to "did you pick the analysis that worked?", so
        # a stored verdict that no longer follows from the data is the one place
        # a reader is least able to check by hand.
        "paper/honest/repro/results_robustness.json",
        '"ev|maxmin|format": {\n        "mean_effect": 0.302',
        '"ev|maxmin|format": {\n        "mean_effect": 0.402',
        "tests/test_specification_curve_recomputes.py",
        "a specification-curve entry drifts from the panel",
    ),
    (
        # A preregistered probe's adjudication stops following from its run.
        # "sycophancy confirms, anchoring refuses" is read from this summary,
        # and until now nothing recomputed it from the measurements.
        "paper/honest/repro/results_probes2_analysis.json",
        '"families_positive": "11/13"',
        '"families_positive": "13/13"',
        "tests/test_new_probe_counts_recompute_from_raw.py",
        "a probe's adjudication stops matching its raw run",
    ),
    (
        # A per-family effect flips sign while the "8/9" summary above it does
        # not. The paper quotes the summary; nothing recomputed it from the
        # values in the same file until now.
        "paper/honest/repro/results_robustness.json",
        '"Granite-3.1-8B": 0.578',
        '"Granite-3.1-8B": -0.578',
        "tests/test_fraction_summaries_recompute.py",
        "a fraction summary stops matching its per-family values",
    ),
    (
        # A recorded verdict stops agreeing with the numbers beside it. The
        # summary table's asterisks are read from this flag, not from the
        # interval, so the interval could move and the asterisk stay.
        "paper/honest/repro/results_peritem.json",
        '"boot_ci95": [\n        0.081,',
        '"boot_ci95": [\n        -0.081,',
        "tests/test_flags_agree_with_their_numbers.py",
        "a verdict flag disagrees with its own interval",
    ),
    (
        # The ground-truth table stops matching the runs behind it. Its margin
        # drops are what P6's failed second clause rests on -- instruct loses
        # more margin than base -- and the prose gate only compares the paper
        # against this same derived file.
        "paper/honest/repro/results_gold.json",
        '"margin_drop": 2.4319',
        '"margin_drop": 1.4319',
        "tests/test_the_ground_truth_table_recomputes.py",
        "the ground-truth table leaves its own runs behind",
    ),
    (
        # The ground-truth prose goes back to generalising one authority
        # framing to the probe, claiming the untested expert variant too.
        "paper/honest/macros.tex",
        "the authority framing tested here---the novice variant, the only one this run used---is nearly harmless",
        "authority framing is nearly harmless",
        "tests/test_the_gold_conditions_are_named_precisely.py",
        "one authority variant is generalised to the probe",
    ),
    (
        # The paper goes back to calling 35 item-by-rubric-order pairs "items",
        # which is impossible from a 20-item panel and overstates how
        # independent the causal test's sample is.
        "paper/honest/macros.tex",
        "$n=35$ of the 40 item$\\times$rubric-order pairs",
        "$n=35$ items",
        "tests/test_the_patched_units_are_described_correctly.py",
        "the patched pairs are called items again",
    ),
    (
        # The ground-truth run's lost model stops being disclosed, leaving a
        # shell entry in the data with no path to a reader.
        "paper/honest/repro/ENVIRONMENT.md",
        "**The ground-truth run lost StableLM-2-1.6B.** Both its checkpoints failed with\n"
        "`AttributeError: 'StableLmConfig' object has no attribute 'pad_token_id'`, a\n"
        "known quirk of that config.",
        "**The ground-truth run completed.**",
        "tests/test_recorded_failures_are_disclosed.py",
        "a recorded run failure stops being disclosed",
    ),
    (
        # Instruct attention to the nuisance rises above base, restoring the
        # mechanism the retracted version invented at exactly this point.
        "paper/honest/repro/attn_results.json",
        '"authority_expert": 0.37777',
        '"authority_expert": 0.40777',
        "tests/test_the_attention_null_holds.py",
        "the refuted attention mechanism comes back",
    ),
    (
        # The smallest Chinese family effect flips sign, turning the paper's
        # 4/4 replication into 3/4 while every string pin still matches.
        "paper/honest/repro/results_zh_analysis.json",
        '"Qwen2.5-1.5B": 0.115',
        '"Qwen2.5-1.5B": -0.115',
        "tests/test_the_chinese_replication_recomputes.py",
        "a Chinese family effect flips sign",
    ),
    (
        # Pooling the frontier judges is reported as strengthening the law;
        # the stored pooled correlation drifts to weaker than the open-only
        # one, which reverses the point of having run them.
        "paper/honest/repro/results_closed_analysis.json",
        '"pooled_rho": -0.452',
        '"pooled_rho": -0.352',
        "tests/test_the_frontier_pooling_recomputes.py",
        "the frontier pooling stops strengthening the law",
    ),
    (
        # The stage ladder's exception disappears: Tulu-3-8B's RLVR step is
        # made to fall, so entropy falls at all eight transitions and the
        # caption's original "every stage sharpens" becomes true again.
        "paper/honest/repro/results_stages_analysis.json",
        '        0.9209,\n        1.1061\n      ],',
        '        0.9209,\n        0.8061\n      ],',
        "tests/test_the_stage_ladder_recomputes.py",
        "the stage ladder's one exception disappears",
    ),
    (
        # The bound's measured tightness drifts from the distributions. The
        # mean still sits inside min and max, so the relationships the theory
        # test checks all still hold.
        "paper/honest/repro/results_robustness.json",
        '"mean_gradnorm_over_sqrtvar": 0.451',
        '"mean_gradnorm_over_sqrtvar": 0.471',
        "tests/test_the_bound_tightness_recomputes.py",
        "the bound's tightness drifts from the distributions",
    ),
    (
        # The concordance between the distributional readout and the discrete
        # one drifts from the cells. Its n is checked elsewhere and stays 130,
        # so only recomputing the value sees this.
        "paper/honest/repro/results_robustness.json",
        '"spearman_evbias_fliprate": 0.557',
        '"spearman_evbias_fliprate": 0.257',
        "tests/test_the_readout_concordance_recomputes.py",
        "the readout concordance drifts from the cells",
    ),
    (
        # A per-family pair moves, so the registered test's p-value no longer
        # follows from the thirteen pairs it is computed over. The Holm check
        # takes the raw p as given, so only the enumeration sees this.
        "paper/honest/repro/results_peritem.json",
        '"score_id": {\n        "base_delta": 1.609',
        '"score_id": {\n        "base_delta": 2.609',
        "tests/test_the_registered_per_probe_test_recomputes.py",
        "a preregistered p-value stops following from its pairs",
    ),
    (
        # Two variance components swap. They still sum to one, so the identity
        # check passes and only a recompute from the cells sees it.
        "paper/honest/repro/results_robustness.json",
        '"probe": 0.236,\n    "kind": 0.056,',
        '"probe": 0.056,\n    "kind": 0.236,',
        "tests/test_the_variance_decomposition_recomputes.py",
        "variance components swap while still summing to one",
    ),
    (
        # The answer to the size-confound objection drifts from the runs it is
        # computed on. Pinning it as a string proves only that the sentence was
        # not reworded, so only a recompute sees this.
        "paper/honest/repro/results_mechanism.json",
        '"partial_rank_rho_given_log10_params": -0.382',
        '"partial_rank_rho_given_log10_params": -0.582',
        "tests/test_the_size_confound_control_recomputes.py",
        "the size-partialled correlation drifts from the runs",
    ),
    (
        # The reliability the paper offers against "n=13 is small" drifts from
        # the scores it is measured on. Both stored numbers move together, so
        # the Spearman-Brown identity still holds and only a recompute sees it.
        "paper/honest/repro/results_robustness.json",
        '"split_half_spearman": 0.986,\n    "spearman_brown": 0.993,',
        '"split_half_spearman": 0.886,\n    "spearman_brown": 0.94,',
        "tests/test_split_half_reliability_recomputes.py",
        "the estimator's reliability drifts from its scores",
    ),
    (
        # The agent instructions state a study size no count of the released
        # data produces, in the section headed "must be correct in all outputs".
        ".hermes.md",
        "63,040 across the",
        "62,940 across the",
        "tests/test_the_agent_findings_match_the_data.py",
        "the agent instructions state an uncountable study size",
    ),
    (
        # A dead import returns, which is what the lint gate is for.
        "verify_like_ci.py",
        "import subprocess",
        "import json\nimport subprocess",
        "tests/test_the_lint_gate_passes.py",
        "the lint gate stops being clean",
    ),
    (
        # black goes back into the gate it has never passed.
        "Makefile",
        "lint:  # Run code quality checks (flake8)",
        "lint:  # Run code quality checks (flake8)\n\tblack --check tests/",
        "tests/test_the_lint_gate_passes.py",
        "black returns to a gate it has never passed",
    ),
    (
        # CI stops installing the stack the suite imports, so collection dies
        # on the runner while every local check stays green.
        ".github/workflows/repro.yml",
        "pip install -r paper/honest/repro/requirements-repro.txt",
        "pip install -r paper/honest/repro/requirements-absent.txt",
        "tests/test_ci_installs_what_the_suite_imports.py",
        "CI stops installing what the suite imports",
    ),
    (
        # The paper goes back to claiming one command re-collects the data.
        "paper/honest/scoring_bias_v2.tex",
        "\\path{run_all.sh} runs the CPU half of that pipeline in order",
        "\\path{run_all.sh} runs all of them in order",
        "tests/test_the_reproduction_script_does_what_the_paper_says.py",
        "the paper overstates what one command reproduces",
    ),
    (
        # The reproduction script silently stops regenerating one analysis.
        "run_all.sh",
        "analyze_tokvar.py",
        "analyze_SKIPPED.py",
        "tests/test_the_reproduction_script_does_what_the_paper_says.py",
        "the reproduction script drops an analyzer",
    ),
    (
        # The public page's figures button points back at the quarantined
        # directory, inviting a reader to look at withdrawn material.
        "paper/interactive/index.html",
        'href="../honest/arxiv_submission/figures/"',
        'href="../figures/"',
        "tests/test_documents_point_at_files_that_exist.py",
        "a public page links to a quarantined directory",
    ),
    (
        # The README's headline link points at a built PDF that .gitignore
        # excludes, so it is a 404 for everyone who has not built it.
        "README.md",
        "**[`paper/honest/scoring_bias_v2.tex`](paper/honest/scoring_bias_v2.tex)**",
        "**[`paper/honest/scoring_bias_v2.pdf`](paper/honest/scoring_bias_v2.pdf)**",
        "tests/test_documents_point_at_files_that_exist.py",
        "a document links to something that is not published",
    ),
    (
        # A placeholder arXiv identifier reaches the paper, the exact shape
        # found in the bib entry quarantined earlier today.
        "paper/honest/macros.tex",
        "% Macros filled from the real 13-family",
        "\\newcommand{\\ARXIVID}{2607.xxxxx}\n% Macros filled from the real 13-family",
        "tests/test_no_draft_markers_reach_the_reader.py",
        "a placeholder identifier reaches the paper",
    ),
    (
        # The overturned direction returns with a capital at the start of the
        # sentence -- the spelling the whole pattern set missed until the
        # casing was fixed.
        "paper/submission_checklist.md",
        "## Manuscript",
        "## Manuscript\nInstruction tuning improves robustness.",
        "tests/test_no_document_states_the_overturned_direction.py",
        "the overturned direction returns at the start of a sentence",
    ),
    (
        # A bibliography entry citing the retracted paper returns to the live
        # tree, with the withdrawn record as its doi field.
        "CITATION.cff",
        "repository-code:",
        "doi = {10.5281/zenodo.21361920}\nrepository-code:",
        "tests/test_one_doi_is_cited_everywhere.py",
        "the withdrawn DOI is used as a citable field",
    ),
    (
        # The retracted paper's fabricated title returns in title case, the
        # spelling the case-sensitive pattern missed for a year.
        "CITATION.cff",
        'title: "Confidence Is Not Robustness',
        'x-prior-title: A 22-Model Landscape with Base-Instruct Comparison\ntitle: "Confidence Is Not Robustness',
        "tests/test_no_fabricated_artefacts.py",
        "a fabricated scale claim returns in a different case",
    ),
    (
        # An artifact stops naming the archive of record, so two files answer
        # "where does this work live" differently.
        ".hermes.md",
        "archived at DOI\n10.5281/zenodo.21499823",
        "archived at DOI\n10.5281/zenodo.99999999",
        "tests/test_one_doi_is_cited_everywhere.py",
        "a publishing artifact drifts from the archive of record",
    ),
    (
        # The withdrawn record is offered as citable, with nothing saying it
        # archived the fabricated version.
        "CITATION.cff",
        "# NOTE: a prior Zenodo record (10.5281/zenodo.21361920) archived an earlier version\n"
        "# whose results were fabricated; it was removed at the author's request prior to any\n"
        "# dissemination. Cite only the DOI above. Full audit: DATA_INTEGRITY_AUDIT.md.",
        "# See also 10.5281/zenodo.21361920",
        "tests/test_one_doi_is_cited_everywhere.py",
        "the withdrawn DOI is presented as citable",
    ),
    (
        # The setup script's last step runs a file that is not there, so a new
        # contributor's install fails where it should say it worked.
        "setup.sh",
        "$PY -m pytest tests/ -q",
        "$PY tests/run_all_tests.py",
        "tests/test_documents_point_at_files_that_exist.py",
        "a script runs a file that does not exist",
    ),
    (
        # The README's data table points at a directory the reader is not in.
        "README.md",
        "| `paper/honest/repro/results_scaled.json` |",
        "| `repro/results_scaled.json` |",
        "tests/test_documents_point_at_files_that_exist.py",
        "a document quotes a path that does not resolve",
    ),
    (
        # The agent instructions send a reader to a path that is not there.
        ".hermes.md",
        "- arXiv package: `paper/honest/arxiv_package.py`",
        "- arXiv package: `paper/arxiv_package.py`",
        "tests/test_agent_instructions_map_this_repo.py",
        "the agent map quotes a path that does not exist",
    ),
    (
        # The map names something other than the paper of record as the paper.
        ".hermes.md",
        "- Main paper: `paper/honest/scoring_bias_v2.tex`",
        "- Main paper: `paper/honest/superseded_draft.tex`",
        "tests/test_agent_instructions_map_this_repo.py",
        "the agent map names the wrong paper of record",
    ),
    (
        # The inverted judge attribution returns to the live tree.
        "paper/submission_checklist.md",
        "## Structure",
        "## Structure\nGemini shows near-additive behavior.",
        "tests/test_superseded_claims_are_not_asserted.py",
        "an inverted judge attribution returns to the live tree",
    ),
    (
        # The overturned multiplicative claim returns to the live tree.
        "paper/submission_checklist.md",
        "## Manuscript",
        "## Manuscript\nInstruct models exhibit 3-12x more scoring bias than base models.",
        "tests/test_superseded_claims_are_not_asserted.py",
        "a multiplicative bias claim returns to the live tree",
    ),
    (
        # An unattributed byline reaches the live tree under the spelling the
        # literal placeholder pattern did not match.
        "paper/submission_checklist.md",
        "# Submission checklist",
        "Author Name, Author Name\n\n# Submission checklist",
        "tests/test_no_fabricated_artefacts.py",
        "a placeholder byline reaches the live tree",
    ),
    (
        # The checklist's figure count drifts from the paper it describes.
        "paper/submission_checklist.md",
        "Results: 10 figures and 5 tables",
        "Results: 20 figures and 5 tables",
        "tests/test_the_submission_checklist_describes_this_paper.py",
        "the checklist miscounts the paper's figures",
    ),
    (
        # A box only the author can complete is ticked as done.
        "paper/submission_checklist.md",
        "- [ ] **Zenodo DOI for this version.**",
        "- [x] **Zenodo DOI for this version.**",
        "tests/test_the_submission_checklist_describes_this_paper.py",
        "an author-only action is ticked as done",
    ),
    (
        # A quarantined pre-retraction rebuttal returns to the live tree,
        # asserting the mechanism story the corrected paper overturned.
        "paper/submission_checklist.md",
        "## Verification",
        "## Verification\nPretrained representations are inherently bias-free.",
        "tests/test_superseded_claims_are_not_asserted.py",
        "an overturned mechanism claim returns to the live tree",
    ),
    (
        # A reviewer-facing pointer goes back to the section it used to mean,
        # which still exists and now holds something else entirely.
        "paper/honest/REBUTTAL_FAQ.md",
        "7/8 families, ρ=−0.44 (§5.17)",
        "7/8 families, ρ=−0.44 (§5.10)",
        "tests/test_the_rebuttal_faq_points_at_the_paper.py",
        "the FAQ points a reviewer at the wrong section",
    ),
    (
        # The FAQ goes back to claiming per-probe significance the registered
        # test does not support.
        "paper/honest/REBUTTAL_FAQ.md",
        '**"No probe is individually significant."**',
        '**"Only 3/5 probes individually significant."**',
        "tests/test_the_rebuttal_faq_points_at_the_paper.py",
        "the FAQ overstates the per-probe evidence",
    ),
    (
        # The disclosure drops one of the seven files whose declared panel
        # size nothing in the release can check.
        "paper/honest/repro/ENVIRONMENT.md",
        "`results_tokvar.json`, `patch_results.json`",
        "`patch_results.json`",
        "tests/test_a_declared_panel_is_checkable_or_recorded.py",
        "the unverifiable-panel disclosure drops a file",
    ),
    (
        # A file exempted as aggregate-only starts carrying a per-item vector,
        # so its panel size became checkable and the exemption is now hiding a
        # check that could run.
        "paper/honest/repro/patch_results.json",
        '"raw": [',
        '"per_item_raw": [',
        "tests/test_a_declared_panel_is_checkable_or_recorded.py",
        "an aggregate-only exemption outlives its reason",
    ),
    (
        # An item vanishes from a sampled cell, leaving 19 scores where the
        # file declares 20. Until the per-item detectors learned the affixed
        # key names and learned that null is a recorded outcome, no guard in
        # the suite could see this array at all.
        "paper/honest/repro/results_sampled.json",
        "              3.4286,\n              2.5,\n              5.0,\n              1.6667,\n",
        "              3.4286,\n              5.0,\n              1.6667,\n",
        "tests/test_the_item_panel_is_what_the_paper_says.py",
        "a sampled cell is scored on a short panel",
    ),
    (
        # The sampled run's recorded parse rates stop supporting the parse
        # rate the release reports for them.
        "paper/honest/repro/results_sampled.json",
        '"parse_rate": 0.5188',
        '"parse_rate": 0.9188',
        "tests/test_the_readout_predictions_recompute.py",
        "a reported parse rate drifts from the conditions it averages",
    ),
    (
        # Bias per unit range stops being bias divided by the range.
        "paper/honest/repro/results_gran_analysis.json",
        '"bias_per_unit_range_base": 0.0414',
        '"bias_per_unit_range_base": 0.0814',
        "tests/test_the_readout_predictions_recompute.py",
        "a per-unit-range figure stops dividing by the range",
    ),
    (
        # The answer mass at the space-appended position drifts from the run.
        "paper/honest/repro/results_tokvar.json",
        '"mean_mass": 0.66763',
        '"mean_mass": 0.16763',
        "tests/test_the_readout_predictions_recompute.py",
        "a readout's reported answer mass drifts from its cells",
    ),
    (
        # A split verdict's weak half strengthens without the sentence changing.
        # "6/10 templates" carries the whole qualification; at 8/10 the prose
        # still reads as reporting a failed clause.
        "paper/honest/repro/results_t10_analysis.json",
        '"T02": -0.076',
        '"T02": 0.076',
        "tests/test_the_split_verdicts_recompute.py",
        "a split verdict's count drifts from its own values",
    ),
    (
        # The clustering disclosure is dropped. Without it the pooled p reads as
        # 180 independent draws when it is 60 judge x template cells of three
        # probes, which is where its <1e-6 comes from.
        "paper/honest/macros.tex",
        "not 180 independent draws",
        "180 fully independent draws",
        "tests/test_the_pooled_template_law_is_a_between_probe_contrast.py",
        "the ten-template pooled p stops disclosing its clustering",
    ),
    (
        # The probe-centred value drifts toward the pooled one. At -0.39 the
        # qualification still reads as present while no longer being a
        # qualification: it would say the law survives probe-centring nearly
        # intact, which is the claim the recomputation refutes.
        "paper/honest/macros.tex",
        "the relation weakens to $r=-0.19$",
        "the relation weakens to $r=-0.39$",
        "tests/test_the_pooled_template_law_is_a_between_probe_contrast.py",
        "the probe-centred template value drifts from the data",
    ),
    (
        # A reported failure quietly becomes a success. Nobody re-derives a
        # number that already says the prediction did not work, so P14's counts
        # could drift in either direction unnoticed.
        "paper/honest/repro/results_dose_analysis.json",
        '"instruct_steeper": "3/8"',
        '"instruct_steeper": "7/8"',
        "tests/test_the_dose_failure_recomputes.py",
        "a reported failure stops matching its own cells",
    ),
    (
        # The span-patch band stops matching the curve beneath it. "Localized in
        # a mid-network band" is what makes this a causal finding rather than a
        # diffuse one, and the band and the curve are printed in one sentence.
        "paper/honest/repro/spanpatch_analysis.json",
        '"layers_with_reduction_ge_50pct": [\n        3,',
        '"layers_with_reduction_ge_50pct": [\n        2,\n        3,',
        "tests/test_the_span_patch_band_recomputes.py",
        "the span-patch band stops matching its curve",
    ),
    (
        # The patching harness initialises a container it never fills again. A
        # future run would ship an empty "raw" that a reader auditing a
        # retracted project cannot tell from per-item data withheld or lost.
        "paper/honest/repro/patch_harness.py",
        'report = {"model": BASE, "n_layers": nL, "n_items": len(ITEMS), "variants": list(SCALES)}',
        'report = {"model": BASE, "n_layers": nL, "n_items": len(ITEMS), "variants": list(SCALES), "raw": []}',
        "tests/test_released_files_promise_no_missing_data.py",
        "a harness reintroduces a container it never fills",
    ),
    (
        # Responsiveness stops being the total-variation shift the paper defines
        # it as. It is the term the mechanism argument turns on -- "far more
        # tightly than decisiveness" -- and reading what the analyzer wrote
        # cannot tell that apart from the analyzer computing something else.
        "paper/honest/repro/results_mechanism.json",
        '"base_mean": 0.1446',
        '"base_mean": 0.1146',
        "tests/test_responsiveness_recomputes_from_the_shifts.py",
        "responsiveness stops being a total-variation shift",
    ),
    (
        # A cell's decisiveness stops being the mean of its own per-item
        # entropies. Entropy is the "confidence" in the paper's title and the
        # x-axis of its headline correlation.
        "paper/honest/repro/results_scaled.json",
        '"mean_entropy": 2.0947',
        '"mean_entropy": 1.0947',
        "tests/test_entropy_recomputes_from_the_distributions.py",
        "a stored entropy leaves its own items behind",
    ),
    (
        # The mixed-model coefficient stops matching the per-item scores it was
        # fitted on. Rerunning the fit would reproduce it either way; only
        # arithmetic that shares no code with the model can tell.
        "paper/honest/repro/results_mechanism.json",
        '"instruct_coef": 0.1559',
        '"instruct_coef": 0.2559',
        "tests/test_the_mixed_model_effect_reproduces.py",
        "the mixed-model effect leaves its own rows behind",
    ),
    (
        # The stored reduction stops equalling the two means it cuts between.
        # check_prose compares the paper's 22% against this fraction, so a
        # fraction that disagrees with its own inputs passes that check exactly.
        "paper/honest/repro/results_robustness.json",
        '"reduction_frac": 0.216',
        '"reduction_frac": 0.316',
        "tests/test_stored_statistics_satisfy_their_identities.py",
        "a stored reduction disagrees with its own means",
    ),
    (
        # The SFT share stops being a share of the rise it names. The abstract,
        # the contribution list and the stage section all carry this number.
        "paper/honest/repro/results_stages_analysis.json",
        '"sft_share_of_total_rise": [\n      0.839,',
        '"sft_share_of_total_rise": [\n      0.639,',
        "tests/test_stored_statistics_satisfy_their_identities.py",
        "the SFT share stops matching its responsiveness path",
    ),
    (
        # The out-of-sample R^2 becomes the squared correlation. Both are
        # plausible numbers to see printed beside "R^2" -- 0.301 against 0.272
        # -- but r^2 ignores whether the predictions are on the right scale, and
        # only the variance-explained form supports "predictable out-of-sample".
        "paper/honest/repro/results_mechanism.json",
        '"loo_r2": 0.272',
        '"loo_r2": 0.301',
        "tests/test_the_headline_correlation_recomputes.py",
        "the out-of-sample R^2 becomes a squared correlation",
    ),
    (
        # The stored headline correlation stops matching the points it was
        # computed from. Every other check on this number reads the stored value
        # -- paper matches JSON, JSON regenerates from raw -- which is a closed
        # circle an analysis that is consistently wrong satisfies.
        "paper/honest/repro/results_mechanism.json",
        "2.2799",
        "0.2799",
        "tests/test_the_headline_correlation_recomputes.py",
        "the headline correlation leaves its own points behind",
    ),
    (
        # One analyzer's copy of the control mapping drifts. Decisiveness and
        # bias would then be measured against different baselines, and both
        # numbers would look entirely ordinary. Five copies of one rule is how
        # the sibling paper's denial regex went wrong for months.
        "paper/honest/repro/analyze_stages.py",
        'CONTROL = {"rubric_order": "control", "score_id": "numeric"',
        'CONTROL = {"rubric_order": "reversed", "score_id": "numeric"',
        "tests/test_the_control_variant_is_one_definition.py",
        "an analyzer's control variant drifts from the others",
    ),
    (
        # A cell loses a variant. Δ is a max-minus-min over variants, so a
        # spread computed over a subset can only be smaller -- the cell reports
        # too little bias, in a paper whose headline is that bias rises, and
        # every value in it stays perfectly plausible.
        "paper/honest/repro/results_zh.json",
        '"random": {',
        '"random_REMOVED": {',
        "tests/test_no_cell_is_missing_a_variant.py",
        "a cell is scored over fewer variants than the probe defines",
    ),
    (
        # A scoring harness starts sampling. The released scores would carry
        # sampling noise while the paper still called them deterministic, and a
        # noisy score is still a number in range -- nothing else would notice.
        "paper/honest/repro/probes2_harness.py",
        "@torch.no_grad()",
        "@torch.no_grad()\ndef _sampled(m, **kw): return m.generate(do_sample=True)",
        "tests/test_only_the_sampled_arm_samples.py",
        "a scoring harness starts sampling",
    ),
    (
        # One arm scores its answer tokens differently from the others, so its
        # bias values stop belonging on the same axis -- while every number it
        # produces still looks entirely plausible. The paper compares these arms
        # directly ("the largest tuning effect of any probe on the panel").
        "paper/honest/repro/probes2_harness.py",
        'SCALE = "on a scale of 1 to 5, where 1 is worst and 5 is best"',
        'SCALE = "on a scale of 1 to 5, where 1 is best and 5 is worst"',
        "tests/test_every_arm_measures_the_same_thing.py",
        "an arm is scored under a different rubric from the panel",
    ),
    (
        # A published dashboard shows a value that is in no data file. Forty-two
        # hand-copied numbers sat on that page, compared against nothing --
        # which is the shape of what this project retracted.
        "paper/interactive/base_vs_instruct.html",
        '"Qwen2.5-7B":      {rubric_order:0.6',
        '"Qwen2.5-7B":      {rubric_order:1.6',
        "tests/test_the_interactive_page_matches_its_data.py",
        "the dashboard publishes a value not in its run",
    ),
    (
        # A second, disagreeing pin for the same package. requirements.txt held
        # numpy==1.26.4 against the analysis stack's 2.4.4, and the Dockerfile
        # installed requirements.txt -- so the published container reproduced
        # none of the paper's numbers.
        "requirements.txt",
        "pytest==8.3.4",
        "pytest==8.3.4\nnumpy==1.26.4",
        "tests/test_environment_doc_matches_the_pins.py",
        "two files pin the same package differently",
    ),
    (
        # A compose service mounts a directory that does not exist. Docker
        # creates an empty bind mount and the service serves nothing -- three of
        # the four services here were in that state.
        "docker-compose.yml",
        "    command: [\"python\", \"-m\", \"pytest\", \"tests/\", \"-q\"]",
        "    command: [\"python\", \"-m\", \"pytest\", \"tests/\", \"-q\"]\n    volumes:\n      - ./notebooks:/app/notebooks",
        "tests/test_live_entry_points_are_alive.py",
        "a compose service mounts a missing directory",
    ),
    (
        # The container's default command runs a script that is not there --
        # or, as it did until now, one that displayed the synthetic datasets.
        # `docker run` is a published entry point and no test read it.
        "Dockerfile",
        'CMD ["python3", "verify_like_ci.py"]',
        'CMD ["python3", "dashboard.py"]',
        "tests/test_live_entry_points_are_alive.py",
        "the container's default command names a missing script",
    ),
    (
        # The issue template hands a first-time contributor the fabricated
        # dataset as its worked example. GitHub renders this to anyone reporting
        # a problem, and nothing else in the suite reads .github/.
        ".github/ISSUE_TEMPLATE/data_issue.md",
        "`paper/honest/repro/results_scaled.json`",
        "`results_rootcause/study1_results.json`",
        "tests/test_live_entry_points_are_alive.py",
        "the issue template cites the fabricated dataset",
    ),
    (
        # A live document states the direction the data overturned. Two
        # public-facing artifacts did -- a graphical abstract and a video
        # narration -- and neither carried a fabricated signature, so the
        # signature sweep could not see them.
        "README.md",
        "## How to cite",
        "Instruction tuning improves format robustness.\n\n## How to cite",
        "tests/test_no_document_states_the_overturned_direction.py",
        "a live document asserts the overturned direction",
    ),
    (
        # A script under paper/ starts acting on the retracted manuscript again.
        # Seventeen such scripts sat beside paper/honest/ until they were
        # quarantined, orphaned and unreferenced -- which is why every earlier
        # sweep missed them.
        "paper/__init__.py",
        "# Package",
        'PAPER = "camera_ready_full.tex"',
        "tests/test_agent_instructions_map_this_repo.py",
        "a paper/ script acts on the retracted manuscript",
    ),
    (
        # A root entry point starts reading the fabrication-era synthetic data
        # again, in a repository whose paper states none is used. Nothing else
        # fails when this happens: no test imports it, CI does not run it, and
        # the paper does not cite it. It just sits there looking maintained.
        "setup.sh",
        'echo "  2. Reproduce every number:   bash run_all.sh"',
        'echo "  2. Pilot: python3 gen.py results/bias_interaction_synthetic.csv"',
        "tests/test_live_entry_points_are_alive.py",
        "a root entry point serves the synthetic data again",
    ),
    (
        # The map agents read points at a directory that is not there. A wrong
        # instruction file is worse than a missing one: it is followed.
        ".hermes.md",
        "├── tests/                      # pytest suite",
        "├── testz/                      # pytest suite",
        "tests/test_agent_instructions_map_this_repo.py",
        "the agent instructions map a path that does not exist",
    ),
    (
        # The README's raw-file table drops the frontier-judge data. Whole
        # sections of the paper lose their listed source, in the first place
        # anyone looks for it.
        "README.md",
        "| `paper/honest/repro/results_closed.json` |",
        "| `paper/honest/repro/results_closed_OMITTED.json` |",
        "tests/test_the_release_promises_hold.py",
        "the README's data table drops a released run",
    ),
    (
        # A quoted value drifts far enough to print differently but not far
        # enough to trip the old 0.006 tolerance: -0.4155 rounds to -0.42 beside
        # a paper saying -0.41. Only the half-unit-in-the-last-place cap catches
        # this band; it passed for as long as the tolerance was a flat constant.
        "paper/honest/repro/results_mechanism.json",
        '"spearman_rho": -0.413',
        '"spearman_rho": -0.4155',
        "tests/test_prose_matches_derived_values.py",
        "a quoted value drifts into the next printed digit",
    ),
    (
        # A macro used inside the abstract's parentheses takes its sentence-final
        # period back, so the sentence stops mid-clause on the page. Compiles
        # clean, no box overfull, every number right; only visible when read.
        "paper/honest/macros.tex",
        "instruction tuning does not protect it}",
        "instruction tuning does not protect it.}",
        "tests/test_macro_sentences_punctuate_once.py",
        "a parenthesised macro ends the sentence early",
    ),
    (
        # The abstract drops the scope its section carries. Twice today a claim
        # was corrected in its section and left bare in the abstract, which is
        # where it is actually read.
        "paper/honest/scoring_bias_v2.tex",
        "are as a group the most\nconfident",
        "are the most\nconfident",
        "tests/test_superlatives_are_true.py",
        "the abstract drops a scope the body carries",
    ),
    (
        # One variant of the Chinese suite reverts to English. The run still
        # produces a full set of numbers, described as a Chinese replication,
        # while testing something between two languages that nobody named.
        "paper/honest/repro/zh_harness.py",
        '"reversed": ("按1到5分评分，1分最好，5分最差"',
        '"reversed": ("on a scale of 1 to 5, where 1 is best and 5 is worst"',
        "tests/test_the_chinese_replication_is_chinese.py",
        "a variant of the Chinese suite reverts to English",
    ),
    (
        # The letter scale is scored the way it reads rather than the way the
        # judge was instructed: A worth 1 instead of 5. Every number downstream
        # stays plausible and one whole probe is inverted.
        "paper/honest/repro/scaled_harness.py",
        "list(range(5, 0, -1)) if a is LET",
        "list(range(1, 6)) if a is LET",
        "tests/test_the_printed_prompt_is_the_prompt_that_ran.py",
        "the letter scale is scored backwards",
    ),
    (
        # The appendix prints a prompt the harness does not send.
        "paper/honest/scoring_bias_v2.tex",
        "Evaluate the following response to the instruction",
        "Rate the following response to the instruction",
        "tests/test_the_printed_prompt_is_the_prompt_that_ran.py",
        "the printed prompt stops being the prompt that ran",
    ),
    (
        # The positioning table's own row overstates the study. The audit caught
        # the retracted version's row saying "31 models" against a body that said
        # otherwise; a self-row is the one row nobody re-derives.
        "paper/honest/scoring_bias_v2.tex",
        "\\textbf{7 (4 new)}",
        "\\textbf{9 (4 new)}",
        "tests/test_the_positioning_row_matches_the_study.py",
        "the positioning row overstates the bias types",
    ),
    (
        # The abstract goes back to calling the fabricated predecessor merely
        # unreliable. Softening in the most-read sentence while the accurate
        # word survives in an appendix is how this drifts back.
        "paper/honest/scoring_bias_v2.tex",
        "prior, fabricated version of this project is included",
        "prior, unreliable version of this project is included",
        "tests/test_the_retraction_is_not_softened.py",
        "the retraction is described more gently than the audit",
    ),
    (
        # The GPU-hour total drifts away from the itemisation beneath it. A
        # total that no longer matches its parts is arithmetic over an intended
        # design rather than a record of what ran -- the audit's finding about
        # the retracted version, in one number.
        "paper/honest/scoring_bias_v2.tex",
        "17 GPU-hours",
        "25 GPU-hours",
        "tests/test_compute_disclosure_matches_the_run.py",
        "the GPU-hour total leaves its own breakdown",
    ),
    (
        # The compute disclosure's call count stops matching the data those
        # calls produced. This is the number the retracted version inflated.
        "paper/honest/scoring_bias_v2.tex",
        "$2{,}250$\nsingle-token logprob calls",
        "$2{,}500$\nsingle-token logprob calls",
        "tests/test_compute_disclosure_matches_the_run.py",
        "the stated API call count leaves the data behind",
    ),
    (
        # A factor of the same product drifts while the product still looks
        # plausible -- the failure a total-only check cannot see.
        "paper/honest/scoring_bias_v2.tex",
        "(three judges $\\times$",
        "(four judges $\\times$",
        "tests/test_compute_disclosure_matches_the_run.py",
        "a factor of the call count drifts from the run",
    ),
    (
        # A guard loses its only registration, so nothing shows it can fail.
        #
        # The replacement misspells the *directory* rather than the file. Written
        # as another tests/ path it would itself read as a registration -- the
        # coverage sweep scans this file for exactly that pattern -- and the
        # unmutated tree would fail on a test file that never existed.
        # Split for the same reason as the lock anchor below: written whole, the
        # find string would occur here as well as in the entry it targets, and
        # the checker would mutate its own registration to no effect.
        "mutation_check.py",
        '"tests/test_holm' '_correction_is_correct.py"',
        '"testz/test_holm_correction_is_correct.py"',
        "tests/test_every_guard_has_a_mutation.py",
        "a guard loses its only registered mutation",
    ),
    (
        # This checker releases a lock it does not hold, so a run refused for
        # colliding with another deletes that run's stash -- the refusal causing
        # the damage it exists to prevent.
        #
        # Mutating this file is safe only because the guard runs the checker as
        # a fresh subprocess, which loads the mutated source; the parent has
        # already imported its own. The guard points that subprocess at a stash
        # of its own, so it does not have to skip while this run holds the real
        # one. If a run is killed here, the recovery path restores this file
        # like any other.
        # The anchor is split across two literals on purpose. Written whole, it
        # would occur twice in this file -- here and in the code -- and the
        # registration comes first, so the checker would mutate its own entry
        # and change no behaviour. It reported NOT CAUGHT, correctly.
        "mutation_check.py",
        "    if _HOLDS" "_LOCK:",
        "    if True:",
        "tests/test_mutation_runs_cannot_collide.py",
        "a refused run deletes the holder's stash",
    ),
    (
        # The stage-ablation exception disappears from the data while the paper
        # still states it -- or, run the other way, the paper's "seven of eight"
        # stops matching the transitions. A universal claim in a caption is
        # falsified by one counterexample, and nothing was counting them.
        "paper/honest/repro/results_stages_analysis.json",
        "1.1061",
        "0.9061",
        "tests/test_prose_matches_derived_values.py",
        "the stage-ablation exception stops matching the data",
        True,  # the value appears in both the trajectory table and P8_paths
    ),
    (
        # The Reproducibility section's count of analysis scripts drifts from the
        # directory. The section is what a replicator follows; an undercount
        # sends them away having reproduced part of the paper.
        "paper/honest/scoring_bias_v2.tex",
        "the fourteen \\path{repro/analyze_*.py}",
        "the twelve \\path{repro/analyze_*.py}",
        "tests/test_reproducibility_section_is_complete.py",
        "the reproduction recipe undercounts its own scripts",
    ),
    (
        # The limitation names a prediction among the failures that is recorded
        # as confirmed. A reckoning with a wrong entry in it reads as one that
        # has been done.
        "paper/honest/scoring_bias_v2.tex",
        "(P14 and P16 outright",
        "(P11 and P16 outright",
        "tests/test_preregistration_is_reported.py",
        "a confirmed prediction is listed among the failures",
    ),
    (
        # A tool starts using a scratch path inside the repo that .gitignore
        # does not cover. Such a directory survives an interrupted run, and
        # `git add -A` would then commit an entire virtualenv.
        #
        # The mutation moves the tool's path rather than editing .gitignore:
        # un-ignoring .mutation_stash mid-run exposes this checker's own stash
        # of pre-mutation sources to every guard that walks the working tree,
        # which aborted the run and left two mutations applied the first time
        # it was tried.
        "verify_like_ci.py",
        'REPO / ".verify-venv"',
        'REPO / ".verify-venv-2"',
        "tests/test_tooling_scratch_is_ignored.py",
        "a tooling scratch directory stops being ignored",
    ),
    (
        # The disclosure attached to the frontier group comparison goes stale.
        # A stated exception with a wrong count reads as checked and is not.
        "paper/honest/repro/results_closed_analysis.json",
        '"mean_entropy": 0.968',
        '"mean_entropy": 1.968',
        "tests/test_superlatives_are_true.py",
        "a stated exception count drifts from the data",
    ),
    (
        # The probe the paper calls the panel's largest tuning effect stops
        # being it. A superlative is the one claim that goes false without its
        # own source changing, so it has to be recomputed, not stored.
        "paper/honest/repro/results_probes2_analysis.json",
        '"mean_change": 0.457',
        '"mean_change": 0.157',
        "tests/test_superlatives_are_true.py",
        "the paper's largest-effect claim stops being the largest",
    ),
    (
        # A run outside the superlative's scope grows past it and is not named.
        # The sentence stays true as scoped and misleading as read.
        "paper/honest/repro/results_zh_analysis.json",
        '"mean_change": 0.763',
        '"mean_change": 1.763',
        "tests/test_superlatives_are_true.py",
        "an out-of-scope effect outgrows the superlative undisclosed",
    ),
    (
        # A probe starts surviving the registered correction, so the paper's
        # disclosure that none does becomes false -- in the paper's own favour,
        # which is the direction nobody re-reads.
        "paper/honest/repro/results_peritem.json",
        '"wilcoxon_p_holm": 0.133',
        '"wilcoxon_p_holm": 0.013',
        "tests/test_prose_matches_derived_values.py",
        "a probe starts surviving the registered correction",
    ),
    (
        # The refuted core prediction loses its recorded outcome. P2 was
        # registered as a positive correlation, measured negative, and reported
        # in the paper under a different label -- which is exactly how a
        # registered id comes to look merely unadjudicated.
        "paper/honest/PREREGISTRATION.md",
        "**P2 (link) — refuted in sign",
        "**P2 (link).** Refuted in sign",
        "tests/test_preregistration_is_reported.py",
        "a registered prediction loses its recorded outcome",
    ),
    (
        # An outcome's evidence drifts from the analysis it cites. The verdict
        # would still read as though it had been checked.
        "paper/honest/PREREGISTRATION.md",
        "p = 0.00371 across 26 checkpoints",
        "p = 0.00171 across 26 checkpoints",
        "tests/test_preregistration_outcomes_match_the_data.py",
        "a recorded outcome drifts from its evidence",
    ),
    (
        # A full-panel statistic quietly drops cells. The range it reports stays
        # correct for the cells it kept, which is why the paper's "across all
        # 130 cells" would go on reading fine.
        "paper/honest/repro/results_robustness.json",
        '"max": 0.566,\n    "n": 130',
        '"max": 0.566,\n    "n": 128',
        "tests/test_full_panel_statistics_use_the_full_panel.py",
        "a full-panel statistic stops covering the panel",
    ),
    (
        # One item changes domain, so the panel stops being ten per domain.
        # Balance is what licenses reading the per-domain comparison as a
        # comparison of domains rather than of sample sizes.
        "paper/honest/repro/scaled_harness.py",
        'to reduce resource consumption.", "daily_life"',
        'to reduce resource consumption.", "science"',
        "tests/test_the_item_panel_is_what_the_paper_says.py",
        "the item panel stops being balanced across domains",
    ),
    (
        # A released raw file's declared panel size stops matching the cells it
        # holds. A smoke-truncated run looks like a real one in every respect
        # except the denominator every per-item statistic divides by.
        "paper/honest/repro/results_scaled.json",
        '"n_items": 50',
        '"n_items": 49',
        "tests/test_the_item_panel_is_what_the_paper_says.py",
        "a released file's panel size stops matching its cells",
    ),
    (
        # The fourth cumulant after tuning grows instead of shrinking. The
        # appendix's conclusion is that every measured cumulant moves toward the
        # decisive limit, so this falsifies it -- and the recompute from the
        # control distributions disagrees with the stored value either way.
        "paper/honest/repro/results_robustness.json",
        '"k4": -0.294',
        '"k4": -4.294',
        "tests/test_cumulants_recompute_from_raw.py",
        "a cumulant moves away from the decisive limit",
    ),
    (
        # The count of families whose control variance drops stops matching the
        # families. "11/13" was pinned only as a string in the paper, which
        # proves the sentence was not reworded, not that it is true.
        "paper/honest/repro/results_robustness.json",
        '"k2_drop_families": "11/13"',
        '"k2_drop_families": "12/13"',
        "tests/test_cumulants_recompute_from_raw.py",
        "the cumulant family count stops matching the families",
    ),
    (
        # One domain stops supporting "instruct bias exceeds base bias in every
        # one of the five item domains". The audit's FABRICATED verdict was on a
        # per-domain table, so this is the claim a sceptical reader checks first.
        "paper/honest/repro/results_peritem.json",
        '"humanities": {\n      "base": 0.428',
        '"humanities": {\n      "base": 0.828',
        "tests/test_prose_matches_derived_values.py",
        "a domain stops backing the not-domain-specific claim",
    ),
    (
        # The measured sensitivity exceeds the bound the paper proves for it.
        # Either the measurement or the proposition would be wrong, and nothing
        # checked the inequality -- only the number summarising its slack.
        "paper/honest/repro/results_robustness.json",
        '"max": 0.566',
        '"max": 1.166',
        "tests/test_the_theory_holds_in_its_own_data.py",
        "measurement violates the paper's own bound",
    ),
    (
        # A checker admits it cannot run and returns success in the same block.
        # This is the shape the guard does catch; the success-path variant it
        # cannot catch is documented in the test rather than registered here.
        "paper/honest/repro/check_figures.py",
        '  macOS:         brew install poppler"\n        )\n        return 1',
        '  macOS:         brew install poppler"\n        )\n        return 0',
        "tests/test_checks_do_not_pass_quietly.py",
        "a checker reports success when its tooling is missing",
    ),
    (
        # A test in the suite becomes vacuous. The guard's inputs are the test
        # files themselves, so the mutation necessarily lands in tests/ -- but
        # in a *different* file from the guard being exercised, which is no more
        # circular than mutating any other source the guard reads.
        "tests/test_small_n_statistics.py",
        "assert not risky, (",
        "assert isinstance(risky, list), (",
        "tests/test_no_test_is_vacuous.py",
        "a test in the suite becomes vacuous",
    ),
    (
        # A README figure drifts from the result it quotes. I said last commit
        # that this guard would need the harness to mutate the test suite; that
        # was wrong. It reads the README and the derived JSON, both tracked, so
        # it is mutable like any other.
        "README.md",
        "rho=-0.44",
        "rho=-0.54",
        "tests/test_readme_figures_match_the_data.py",
        "a README figure drifts from its source",
    ),
    (
        # An unfinished note reaches the paper's sources. Previously only the
        # archive was checked, which no string swap can reach -- so this guard
        # had my word for it and nothing else.
        "paper/honest/scoring_bias_v2.tex",
        "\\section{Related Work}",
        "\\section{Related Work}\\paragraph{TODO: finish the survey}",
        "tests/test_no_draft_markers_reach_the_reader.py",
        "a draft marker reaches the paper sources",
    ),
    (
        # The audit's trail to its evidence breaks. Verified by hand when the
        # guard was written; registered here so it stays verified.
        "DATA_INTEGRITY_AUDIT.md",
        "RETRACTED/data/study1_results.json",
        "RETRACTED/data/study1_results_moved.json",
        "tests/test_audit_evidence_paths_resolve.py",
        "audit cites evidence that is not there",
    ),
    (
        # The environment document drifts from the pins it documents.
        "paper/honest/repro/ENVIRONMENT.md",
        "scipy==1.17.1",
        "scipy==1.17.0",
        "tests/test_environment_doc_matches_the_pins.py",
        "environment doc drifts from requirements-repro.txt",
    ),
    (
        # A make target points at a file that does not exist. This is the state
        # eight targets were actually in.
        #
        # Re-anchored: the previous anchor was `streamlit run dashboard.py`, and
        # run-dashboard has since been removed -- it served the fabrication-era
        # synthetic data. A stale anchor means the guard stops being exercised
        # while the run still prints a cheerful total, so it is repaired rather
        # than dropped.
        "Makefile",
        "python scan_secrets.py",
        "python scan_secrets_missing.py",
        "tests/test_make_targets_are_not_broken.py",
        "make target names a missing file",
    ),
    (
        # The superseded figure generator can reach the live tree again -- the
        # defect that let it overwrite the paper's Figure 1.
        "paper/honest/superseded/make_figures.py",
        'FIG = HERE / "figures"',
        'FIG = HERE.parent / "figures"',
        "tests/test_superseded_scripts_stay_in_their_lane.py",
        "superseded generator can write into the paper",
    ),
    (
        # The promised single-script reproduction builds the retracted paper.
        "run_all.sh",
        "pdflatex -interaction=nonstopmode scoring_bias_v2.tex",
        "pdflatex -interaction=nonstopmode camera_ready_full.tex",
        "tests/test_the_release_promises_hold.py",
        "the reproduction script rebuilds the retracted paper",
    ),
    (
        # A number appears in the paper that no result file explains -- the
        # inflated frontier call count, restored.
        "paper/honest/scoring_bias_v2.tex",
        "$2{,}250$",
        "$4{,}500$",
        "tests/test_every_number_is_accounted_for.py",
        "an unexplained number returns to the paper",
    ),
    (
        # A float label sits outside any float, so it numbers the section.
        "paper/honest/scoring_bias_v2.tex",
        "\\section{Related Work}",
        "\\label{fig:orphan}\\section{Related Work}",
        "tests/test_float_numbering_is_correct.py",
        "a figure label numbers a section",
    ),
    (
        # A per-template correlation drifts. These were quoted in the prose while
        # no analysis emitted them, so nothing could compare them to the data;
        # they are emitted as C8b now and this proves the comparison bites.
        "paper/honest/repro/results_robustness.json",
        '"spearman_rho": -0.457',
        '"spearman_rho": -0.157',
        "tests/test_prose_matches_derived_values.py",
        "per-template correlation drifts from the data",
    ),
]


LOCK = STASH / "lock.json"


def _stash(rel: str, data: bytes):
    STASH.mkdir(exist_ok=True)
    target = STASH / rel.replace("/", "__")
    target.write_bytes(data)
    MANIFEST.write_text(json.dumps({"file": rel, "stash": target.name}), encoding="utf-8")


def _clear_stash():
    """Remove the stash, keeping the lock: the run is not over until it is."""
    for path in STASH.glob("*"):
        if path.name != LOCK.name:
            path.unlink(missing_ok=True)


def _recover():
    """Restore a file left mutated by a run that was killed mid-mutation.

    The restore in main() sits in a `finally`, so an exception restores. A kill
    -- a CI timeout, a closed terminal -- does not, and what survives is a
    source file of the paper with a deliberate error in it. Twice today that
    was macros.tex, carrying an invented preregistration id and a wrong n.
    """
    if not MANIFEST.exists():
        return None
    record = json.loads(MANIFEST.read_text(encoding="utf-8"))
    saved = STASH / record["stash"]
    target = BASE / record["file"]
    if not saved.exists() or not target.exists():
        return None
    if saved.read_bytes() == target.read_bytes():
        return None
    target.write_bytes(saved.read_bytes())
    return record["file"]


def _take_lock(force: bool):
    """One run at a time. Concurrent runs corrupt the tree, silently.

    Two runs overlapping is not a hypothetical: verify_like_ci.py invokes this
    checker, so running it beside a direct invocation is enough. The second run
    reads an already-mutated file as its "original" and writes that back as the
    restore -- the mutation becomes permanent and the tree looks clean.
    """
    if LOCK.exists() and not force:
        held = LOCK.read_text(encoding="utf-8", errors="replace").strip()
        raise SystemExit(
            f"another mutation run holds the lock ({held}).\n"
            f"Two runs share one working tree: the second reads a mutated file "
            f"as its original and makes the mutation permanent.\n"
            f"If no run is active, that lock is from an interrupted one -- "
            f"rerun with --force, which restores any half-applied mutation first."
        )
    restored = _recover() if force or LOCK.exists() else None
    shutil.rmtree(STASH, ignore_errors=True)
    STASH.mkdir(exist_ok=True)
    LOCK.write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
    global _HOLDS_LOCK
    _HOLDS_LOCK = True
    return restored


_HOLDS_LOCK = False


def _release_lock():
    """Only the holder clears the stash.

    Releasing unconditionally means a run that was *refused* deletes the stash
    of the run it refused to disturb -- taking with it the only copy of the
    file that run is currently holding mutated. The refusal would cause exactly
    the damage it exists to prevent.
    """
    if _HOLDS_LOCK:
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


def main(verbose=False, force=False):
    if not (BASE / "tests").is_dir():
        raise SystemExit("no tests/ directory")

    restored = _take_lock(force)
    if restored:
        print(f"restored {restored} from an interrupted run before starting\n")

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
        # An anchor that spans a line break is written here with \n, but git
        # checks these files out with CRLF on Windows, so the anchor stops
        # matching and the mutation is skipped -- reported as STALE, easy to read
        # as "that guard was retired" rather than "that guard is no longer being
        # exercised". Match the file's own line endings instead.
        if find_b not in original and b"\n" in find_b and b"\r\n" in original:
            find_b = find_b.replace(b"\n", b"\r\n")
            replace_b = replace_b.replace(b"\n", b"\r\n")
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
    checked = len(MUTATIONS) - len(stale)
    if misses:
        print("guards that did NOT catch their mutation:", misses)
        return 1
    if stale:
        # A stale anchor is not a neutral event. The mutation does not run, so
        # the guard it exercises is no longer known to work, and the run still
        # printed a cheerful "every guard caught its mutation" with a quietly
        # smaller number. That is the shape of defect this file exists to catch,
        # applied to this file. A mutation that is genuinely obsolete should be
        # deleted, which is visible in the diff; one that stopped matching by
        # accident should be repaired. Neither is silence.
        print(f"{len(stale)} mutation(s) did not run because their anchor no longer matches:")
        for entry in stale:
            print(f"  - {entry}")
        print(
            f"\nonly {checked}/{len(MUTATIONS)} mutations were exercised. Repair the "
            f"anchor, or delete the entry if the mutation is obsolete -- a "
            f"registered mutation that never runs is a guard nobody is checking."
        )
        return 1
    print(f"every guard caught its mutation ({checked} checked)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main("-v" in sys.argv, "--force" in sys.argv))
    finally:
        _release_lock()
