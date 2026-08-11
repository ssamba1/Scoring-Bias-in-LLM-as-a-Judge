"""Does every Makefile recipe name a file that exists?

The Makefile is the documented way in: `make ci`, `make integrity`, `make
archive`. Nothing checked that its recipes still point at real files, and eight
targets had rotted -- some from this session's quarantine sweep, some from
before it:

    lint               api/app.py            the file is api.py
    archive            paper/arxiv_package.py  now paper/honest/arxiv_package.py
    run-dashboard      dashboard/app.py      the file is dashboard.py
    export-data        scripts/export_data.py
    export-all         scripts/export_data.py    there is no scripts/ directory
    check-credentials  scripts/check_credentials.py
    health-check       scripts/health_check.py
    download-data      results_rootcause/study1_results.json  quarantined

`lint` is a prerequisite of `ci`, so the advertised CI entry point failed on the
first target it reached. A broken make target is a small thing that wastes the
time of exactly the person doing the right thing: the reader who tries to run
the checks.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
MAKEFILE = REPO / "Makefile"

FILEISH = re.compile(r"(?<![\w/*.-])([\w./-]+\.(?:py|sh|tex|json|txt|yml|cfg|toml))")


def _recipes():
    if not MAKEFILE.exists():
        pytest.skip("[makefile] not present")
    recipes, target = {}, None
    for line in MAKEFILE.read_text(encoding="utf-8", errors="replace").splitlines():
        header = re.match(r"^([a-zA-Z][\w-]*):", line)
        if header:
            target = header.group(1)
            recipes.setdefault(target, [])
        elif line.startswith("\t") and target:
            recipes[target].append(line.strip())
        elif not line.strip():
            target = None
    return {name: lines for name, lines in recipes.items() if lines}


def _search_roots(lines):
    """Repo root plus every directory the recipe cd's into.

    A recipe's `cd` may be several lines above the command that names the file,
    so the directories are collected over the whole recipe rather than per line.
    Getting this wrong reports `make paper` as broken because its cd and its
    filename sit on different lines.
    """
    roots = [REPO]
    for line in lines:
        for target in re.findall(r"cd\s+([\w./-]+)", line):
            candidate = REPO / target
            if candidate.is_dir():
                roots.append(candidate)
    return roots


@pytest.mark.parametrize("target", sorted(_recipes()))
def test_target_names_only_files_that_exist(target):
    lines = _recipes()[target]
    roots = _search_roots(lines)

    missing = []
    for line in lines:
        if line.lstrip("@-").startswith(("echo", "printf")):
            continue  # prose, not paths
        for name in FILEISH.findall(line):
            if any((root / name).exists() for root in roots):
                continue
            missing.append(name)
    assert not missing, (
        f"`make {target}` names {sorted(set(missing))}, which the repository does "
        f"not contain; the target fails at that command"
    )


def test_ci_and_reproduce_all_reach_only_working_targets():
    """The aggregate entry points must not depend on a broken target."""
    recipes = _recipes()
    text = MAKEFILE.read_text(encoding="utf-8", errors="replace")
    for aggregate in ("ci", "reproduce-all"):
        match = re.search(rf"^{aggregate}:\s*([\w\s-]*?)(?:#|$)", text, re.M)
        if not match:
            continue
        for prerequisite in match.group(1).split():
            assert prerequisite in recipes or re.search(
                rf"^{prerequisite}:", text, re.M
            ), f"`make {aggregate}` depends on `{prerequisite}`, which is not a target"


def test_every_phony_target_exists():
    """A .PHONY entry with no rule is a target the help text may still advertise."""
    text = MAKEFILE.read_text(encoding="utf-8", errors="replace")
    phony = re.search(r"\.PHONY:\s*((?:.|\n)*?)\n\n", text)
    if not phony:
        pytest.skip("[makefile] no .PHONY block")
    declared = set(phony.group(1).replace("\\", " ").split())
    defined = set(re.findall(r"^([a-zA-Z][\w-]*):", text, re.M))
    ghosts = sorted(declared - defined)
    assert not ghosts, f".PHONY declares {ghosts}, which have no rule"
