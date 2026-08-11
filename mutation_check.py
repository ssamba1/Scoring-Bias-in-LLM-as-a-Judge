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
        # The external dataset loses its licence attribution. CC BY-SA asks for
        # it whether or not the text itself is redistributed.
        "paper/honest/macros.tex",
        "(Databricks, CC BY-SA 3.0; open",
        "(open",
        "tests/test_third_party_data_is_attributed.py",
        "third-party dataset loses its attribution",
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
