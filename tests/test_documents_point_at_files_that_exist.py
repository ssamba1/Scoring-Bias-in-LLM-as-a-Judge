"""Does every path a live document quotes actually resolve?

Extending this check from the agent instructions' tree block to the rest of
that one file found four defects in it, so it is worth asking of every document
a reader might follow. It found two more:

  * README.md's "Real data of record" table listed all nineteen raw files as
    `repro/...`. The table follows a reproduction recipe that has already `cd`ed
    into paper/honest, so the paths were right for the shell and wrong for the
    reader, who is standing at the repository root when the table is what they
    are reading.
  * paper/submission_checklist.md pointed at `repro/check_figures.py` from
    paper/, which is not where it is either.

Neither is a wrong claim about the data. Both are a reader typing a path and
finding nothing, in the two documents most likely to be a first stop.

A path is resolved from the repository root or from the document's own
directory, since both conventions are in use and both are legible in context.
DOIs, URLs, absolute platform paths, globs and file:line references are not
paths to check.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Documents whose purpose is to preserve a superseded record. Their paths point
# into a layout that deliberately no longer exists.
EXEMPT_PREFIXES = ("RETRACTED/", "paper/archive/", "results_rootcause/")

# path -> the document that names it only to say where it went. Each is checked
# to be genuinely absent, so an exemption cannot outlive its reason.
MOVED = {
    "paper/paper_biasinteraction.md": ".hermes.md",
    "paper/supplementary.md": ".hermes.md",
}


def _documents():
    listing = subprocess.run(
        ["git", "ls-files", "*.md"], cwd=REPO, capture_output=True, text=True, timeout=300
    ).stdout.split()
    docs = [d for d in listing if not d.startswith(EXEMPT_PREFIXES)]
    if not docs:
        pytest.skip("[docs] none tracked")
    return sorted(docs)


def _quoted_paths(doc):
    text = (REPO / doc).read_text(encoding="utf-8", errors="replace")
    found = []
    for match in re.finditer(r"`([^`\s]+)`", text):
        candidate = match.group(1).rstrip(".,;:)")
        if candidate.startswith(("http", "-", "$", "/", "10.")):
            continue
        if " " in candidate or "/" not in candidate:
            continue
        if "*" in candidate or ":" in candidate:
            continue
        if candidate.endswith("/") or Path(candidate).suffix:
            found.append(candidate)
    return sorted(dict.fromkeys(found))


@pytest.mark.parametrize("doc", _documents())
def test_every_quoted_path_resolves(doc):
    here = (REPO / doc).parent
    missing = [
        p for p in _quoted_paths(doc)
        if not (REPO / p).exists() and not (here / p).exists()
        and MOVED.get(p) != doc
    ]
    assert not missing, (
        f"{doc} quotes {len(missing)} path(s) that resolve neither from the "
        f"repository root nor from {doc}'s own directory: {missing}. A reader "
        f"following the document finds nothing there."
    )


def test_the_moved_paths_really_are_gone():
    back = sorted(p for p in MOVED if (REPO / p).exists())
    assert not back, (
        f"{back} exist again, but a document describes them as moved; either "
        f"that sentence is now wrong or the file should not be there"
    )


def _scripts():
    listing = subprocess.run(
        ["git", "ls-files", "*.sh"], cwd=REPO, capture_output=True, text=True, timeout=300
    ).stdout.split()
    scripts = [s for s in listing if not s.startswith(EXEMPT_PREFIXES)]
    if not scripts:
        pytest.skip("[scripts] none tracked")
    return sorted(scripts)


@pytest.mark.parametrize("script", _scripts())
def test_every_script_runs_a_file_that_exists(script):
    """In a shell script a dead path is a crash, not a confused reader.

    setup.sh ended with `$PY tests/run_tests.py`. No such file has existed
    since the rewrite, so the last step of setup -- the one that tells a new
    contributor the install worked -- always failed.
    """
    here = (REPO / script).parent
    text = (REPO / script).read_text(encoding="utf-8", errors="replace")
    missing = []
    for match in re.finditer(r"(?<![\w$/\"'-])([\w.-]+/[\w./-]+\.(?:py|sh|json|tex))", text):
        candidate = match.group(1)
        if "$" in candidate or "*" in candidate:
            continue
        if not (REPO / candidate).exists() and not (here / candidate).exists():
            missing.append(candidate)
    assert not missing, (
        f"{script} names {sorted(set(missing))}, which do not exist; running "
        f"the script fails at that line"
    )


def test_the_sweep_reads_real_documents():
    """Vacuity guard: a parse that finds nothing would pass everywhere."""
    total = sum(len(_quoted_paths(doc)) for doc in _documents())
    assert total >= 30, (
        f"only {total} quoted paths parsed across {len(_documents())} documents; "
        f"the parse no longer matches how the docs are written"
    )
