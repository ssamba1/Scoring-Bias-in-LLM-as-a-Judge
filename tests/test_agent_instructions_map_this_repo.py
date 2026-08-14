"""Does the file agents read as instructions describe this repository?

`.hermes.md` is read by coding agents before they touch anything. Its repository
map listed twenty-three paths, seventeen of which do not exist: pipeline
runners, an `infrastructure/` tree, `data/combined_80_items.json`, `binder/`,
`isef/`. Those are the *quarantined* layout -- they live under RETRACTED/legacy/
now -- so the map sent an agent looking for the retracted project's files and
never mentioned paper/honest/, mutation_check.py or verify_like_ci.py.

This is the third defect in this one file: it previously listed the retracted
conclusion under "Key Findings (must be correct in all outputs)" and cited the
deleted DOI. A wrong instruction file is worse than a missing one, because an
agent follows it confidently.

Six fraud-era scripts sat in the repository root for the same reason, including
`_verify_claims.py` -- a script that verifies claims in camera_ready_full.tex,
the retracted paper. It is the audit's own evidence, so it is quarantined with a
pointer from the audit rather than deleted.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HERMES = REPO / ".hermes.md"


def _tree_entries():
    if not HERMES.exists():
        pytest.skip("[repo] no .hermes.md")
    text = HERMES.read_text(encoding="utf-8", errors="replace")
    blocks = text.split("```")
    if len(blocks) < 2:
        pytest.skip("[.hermes.md] carries no repository map")
    # Entries are nested: a name under "paper/honest/" is relative to it. Track
    # the parent by the depth of the tree glyphs, or every child reads as a
    # missing top-level path.
    entries, parents = [], {}
    for line in blocks[1].splitlines():
        match = re.search(r"([\w./-]+/?)(?:\s|$)", line)
        if not match:
            continue
        token = match.group(1).rstrip()
        if not (token.endswith("/") or "." in token):
            continue
        if token == "Scoring-Bias-in-LLM-as-a-Judge/":
            continue  # the root line names the repo, not a path inside it
        depth = len(re.findall(r"[│ ]{4}|├|└", line[: match.start()]))
        prefix = parents.get(depth - 1, "")
        full = f"{prefix}{token}"
        if token.endswith("/"):
            parents[depth] = full
            parents.pop(depth + 1, None)
        entries.append(full)
    return [e for e in dict.fromkeys(entries) if e != "Scoring-Bias-in-LLM-as-a-Judge/"]


def test_every_mapped_path_exists():
    entries = _tree_entries()
    assert len(entries) >= 8, (
        f"only {len(entries)} paths parsed from the map ({entries}); the parse "
        f"no longer matches the file and would pass on anything"
    )
    missing = [e for e in entries if not (REPO / e).exists()]
    assert not missing, (
        f".hermes.md maps {len(missing)} path(s) that do not exist: {missing}. "
        f"An agent following this map looks for the retracted layout."
    )


def test_the_map_names_the_paper_of_record():
    entries = " ".join(_tree_entries())
    for required in ("paper/honest/", "tests/"):
        assert required in entries, (
            f"the map does not mention {required}, which is where the live work is"
        )


# Paths .hermes.md names only to say where they went. Each is checked to be
# genuinely absent by test_the_moved_paths_really_are_gone.
MOVED = {
    "paper/paper_biasinteraction.md",
    "paper/supplementary.md",
}


def _quoted_paths():
    """Every backtick-quoted repository path in the instructions.

    The tree parse above reads one ASCII block. Everything else the file says
    -- the conventions, the workflow, the entry points -- was unchecked, which
    is how "Main paper: `paper/paper_biasinteraction.md`" survived: a different
    project's pre-data draft, named as this repository's paper of record, in
    the file an agent reads first.
    """
    text = (REPO / ".hermes.md").read_text(encoding="utf-8", errors="replace")
    found = []
    for match in re.finditer(r"`([^`\s]+)`", text):
        candidate = match.group(1).rstrip(".,;:)")
        if candidate.startswith(("http", "-", "$", "/")) or " " in candidate:
            # A leading slash is a Kaggle or Colab path, named to explain that
            # the platforms differ. It is not a claim about this repository.
            continue
        if candidate in MOVED:
            # Named in a sentence that says where the file went. The pointer is
            # the correction, so requiring it to exist would forbid explaining
            # the move -- the same self-reference that has tripped guards here
            # before.
            continue
        if "/" not in candidate and not candidate.startswith("."):
            continue
        if candidate.endswith("/") or Path(candidate).suffix:
            found.append(candidate)
    return sorted(dict.fromkeys(found))


def test_the_moved_paths_really_are_gone():
    """MOVED excuses a path from existing, so it must not quietly come back."""
    back = [p for p in MOVED if (REPO / p).exists()]
    assert not back, (
        f"{back} exist again, but .hermes.md describes them as moved; either "
        f"the sentence is now wrong or the file should not be there"
    )


def test_every_quoted_path_exists():
    quoted = _quoted_paths()
    # Nine parse today. The floor is a check that the parse still works, not a
    # target: bare filenames like `macros.tex` are deliberately skipped because
    # they are ambiguous about which directory they mean.
    assert len(quoted) >= 8, (
        f"only {len(quoted)} quoted paths parsed from .hermes.md ({quoted}); "
        f"the parse no longer matches the file and would pass on anything"
    )
    missing = [p for p in quoted if not (REPO / p).exists()]
    assert not missing, (
        f".hermes.md quotes {len(missing)} path(s) that do not exist: {missing}. "
        f"An agent reading this file is being sent somewhere that is not here."
    )


def test_the_main_paper_line_names_the_paper_of_record():
    text = (REPO / ".hermes.md").read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Main paper:\s*`([^`]+)`", text)
    if not match:
        raise AssertionError(
            ".hermes.md no longer states which file is the main paper; that "
            "line named a different project's draft until 2026-08-13, and its "
            "absence is not an improvement"
        )
    named = match.group(1)
    assert named == "paper/honest/scoring_bias_v2.tex", (
        f".hermes.md calls {named!r} the main paper; the paper of record is "
        f"paper/honest/scoring_bias_v2.tex"
    )


def test_no_live_script_serves_the_retracted_paper():
    """A tool in the root that rebuilds or verifies camera_ready_full.tex reads
    as part of the release, whatever its filename suggests."""
    def acts_on_it(path):
        """Executable references only. run_all.sh names the retracted file in a
        comment recording that it used to build it -- documentation of the fix,
        not the defect. A guard that cannot tell those apart gets disabled."""
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            code = line.split("#", 1)[0]
            if "camera_ready_full" in code:
                return True
        return False

    # mutation_check.py names the retracted file as the *replacement* in the
    # mutation that proves run_all.sh cannot silently rebuild it. Naming the
    # material is the purpose, as with tests/fabricated_signatures.py, and the
    # exemption is by exact filename so a new script cannot inherit it.
    EXEMPT = {"mutation_check.py"}

    # paper/ as well as the root: seventeen scripts there built and validated
    # camera_ready*.tex, beside paper/honest/ and orphaned -- nothing referenced
    # them, which is exactly why they survived every earlier sweep.
    candidates = [p for p in REPO.glob("*.py")] + [
        p for p in (REPO / "paper").glob("*.py")
    ] + [p for p in (REPO / "paper").glob("*.sh")]
    offenders = [str(p.relative_to(REPO)) for p in candidates
                 if p.name not in EXEMPT and acts_on_it(p)]
    offenders += [p.name for p in (REPO / "run_all.sh", REPO / "Makefile")
                  if p.exists() and acts_on_it(p)]
    assert not offenders, (
        f"these live entry points act on the retracted paper: {offenders}. "
        f"Quarantine them under RETRACTED/legacy/ -- run_all.sh once rebuilt "
        f"camera_ready_full.tex and reported success."
    )


def test_the_quarantined_scripts_are_still_where_the_audit_says():
    """The audit cites its own verification script; moving it must not orphan that."""
    audit = REPO / "DATA_INTEGRITY_AUDIT.md"
    if not audit.exists():
        pytest.skip("[repo] no audit document")
    text = audit.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"`(RETRACTED/[\w./-]+\.py)`", text):
        cited = REPO / match.group(1)
        assert cited.exists(), (
            f"the audit cites {match.group(1)}, which is not there"
        )
