"""Can the CI job that runs this suite actually import it?

The integrity job installed pytest and nothing else, deliberately: the point
was that the integrity checks and the stdlib-only prose gate run even with no
analysis stack present. Then the suite grew tests that recompute statistics
from the raw data, which import numpy and scipy, and pytest collection began
dying with ModuleNotFoundError before a single check ran.

Every run in the visible history was failing or cancelled while README.md and
the paper described this project as CI-enforced. The local gate was green
throughout, which is exactly what made it survive: `verify_like_ci.py` builds
its own pinned virtualenv, so it installs what the suite needs and never
reproduced the failure.

This compares what the suite imports against what the workflow installs. It is
a static check -- it reads import statements, not a live run -- so it cannot
prove CI passes. It can only stop the suite from quietly outgrowing its
installer again, which is the specific way this broke.
"""

import ast
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "repro.yml"
REQUIREMENTS = REPO / "paper" / "honest" / "repro" / "requirements-repro.txt"

# Modules the runner has without installing anything.
STDLIB = set(getattr(__import__("sys"), "stdlib_module_names", ()))
# Provided by the test runner itself.
ALWAYS = {"pytest"}


def _test_files():
    listing = subprocess.run(
        ["git", "ls-files", "tests/*.py"], cwd=REPO, capture_output=True, text=True, timeout=300
    ).stdout.split()
    files = [REPO / rel for rel in listing]
    if not files:
        pytest.skip("[tests] none tracked")
    return files


def _third_party_imports():
    found = set()
    for path in _test_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        # Module level only. An import inside a function is reached when that
        # test runs, and the ones here are wrapped in try/ImportError with a
        # skip -- cffconvert is optional on purpose. Only a top-level import
        # can kill collection, which is the failure this test exists for.
        for node in tree.body:
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module] if node.module and node.level == 0 else []
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top and top not in STDLIB and top not in ALWAYS:
                    found.add(top)
    # Modules that live in this repository, not on PyPI.
    local = {p.stem for p in (REPO / "tests").glob("*.py")}
    local |= {p.stem for p in REPO.glob("*.py")}
    return found - local


def test_the_workflow_installs_every_module_the_suite_imports():
    if not WORKFLOW.exists():
        pytest.skip("[ci] workflow not present")
    workflow = WORKFLOW.read_text(encoding="utf-8", errors="replace")
    requirements = (
        REQUIREMENTS.read_text(encoding="utf-8", errors="replace")
        if REQUIREMENTS.exists() else ""
    )
    installed = (workflow + "\n" + requirements).lower()

    imports = _third_party_imports()
    assert imports, "no third-party imports parsed; the sweep is looking at nothing"

    missing = sorted(m for m in imports if m.lower() not in installed)
    assert not missing, (
        f"the suite imports {missing}, which the integrity job neither "
        f"installs nor pulls in through requirements-repro.txt. Collection "
        f"fails there with ModuleNotFoundError before any check runs, and the "
        f"local gate will not reproduce it because it builds its own venv."
    )


def test_the_requirements_file_is_actually_installed():
    if not WORKFLOW.exists():
        pytest.skip("[ci] workflow not present")
    workflow = WORKFLOW.read_text(encoding="utf-8", errors="replace")
    integrity = re.search(r"\n  integrity:\n(.*?)(?=\n  \w[\w-]*:\n|\Z)", workflow, re.S)
    if not integrity:
        pytest.skip("[ci] no integrity job")
    body = integrity.group(1)
    assert "requirements-repro.txt" in body, (
        "the integrity job no longer installs requirements-repro.txt, so the "
        "suite's numpy and scipy imports have nothing to resolve against"
    )
    assert "pytest" in body, "the integrity job no longer installs pytest"
