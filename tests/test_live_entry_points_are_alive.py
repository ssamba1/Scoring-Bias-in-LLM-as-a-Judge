"""Does every tracked entry point at the repository root still work?

Six scripts sat in the root looking like tools of this project:

  api.py                served results/bias_interaction_synthetic*.csv over HTTP
  dashboard.py          reported the status of the same synthetic datasets
  cli.py                imported scoring_bias.*, a package with no tracked files
  inference_executor.py needed benchmark/, a directory with no tracked files
  run_rootcause.sh      ran pipeline_rootcause/, emptied in an earlier sweep
  run_biasinteraction.sh ran pipeline_biasinteraction/, likewise

Two of them published the fabrication-era synthetic data in a repository whose
paper states that no synthetic data is used, and `make run-api` /
`make run-dashboard` advertised them. The other four fail on the first line in
any clone. All are quarantined now.

What makes this class hard to see is that nothing about a dead entry point
fails: the tests do not import it, CI does not run it, and the paper does not
cite it. It sits there looking maintained. So the check is structural -- a
tracked script must not depend on a directory the repository does not track,
and must not read the synthetic files.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Naming the fabrication-era data is the purpose of these files.
EXEMPT = {"mutation_check.py", "scan_secrets.py"}

SYNTHETIC = re.compile(r"bias_interaction_synthetic|rootcause_synthetic|synthetic_summary")


def _tracked(pattern):
    out = subprocess.run(["git", "ls-files", pattern], cwd=REPO,
                         capture_output=True, text=True, timeout=300).stdout
    return [line for line in out.splitlines() if line and "/" not in line]


def _tracked_dirs():
    out = subprocess.run(["git", "ls-files"], cwd=REPO,
                         capture_output=True, text=True, timeout=300).stdout
    return {line.split("/")[0] for line in out.splitlines() if "/" in line}


def _root_scripts():
    scripts = _tracked("*.py") + _tracked("*.sh")
    scripts = [s for s in scripts if s not in EXEMPT]
    if not scripts:
        pytest.skip("[repo] no tracked root scripts")
    return scripts


def test_no_root_script_serves_the_synthetic_data():
    offenders = []
    for name in _root_scripts():
        body = (REPO / name).read_text(encoding="utf-8", errors="replace")
        for line in body.splitlines():
            code = line.split("#", 1)[0]
            if SYNTHETIC.search(code):
                offenders.append(f"{name}: {line.strip()[:70]}")
                break
    assert not offenders, (
        f"these tracked entry points read the fabrication-era synthetic data, in "
        f"a repository whose paper says none is used: {offenders}"
    )


def test_no_root_script_depends_on_an_untracked_directory():
    """cli.py imported a package with no tracked files; it cannot run in a clone."""
    tracked_dirs = _tracked_dirs()
    offenders = []
    for name in _root_scripts():
        body = (REPO / name).read_text(encoding="utf-8", errors="replace")
        referenced = set(re.findall(r"(?:^|[\s\"'(/])(\w+)/", body, re.M))
        for directory in sorted(referenced):
            if not (REPO / directory).exists():
                continue
            if directory in tracked_dirs or directory.startswith("."):
                continue
            offenders.append(f"{name} -> {directory}/ (no tracked files)")
    assert not offenders, (
        f"these entry points depend on directories the repository does not track, "
        f"so they fail in any clean clone: {offenders}"
    )


def test_the_packaging_metadata_points_at_files_that_exist():
    """`pip install .` and `docker run` are entry points too.

    pyproject.toml declared `scoring-bias = "cli:main"`, so installing produced
    a command that failed on import; packages.find pointed at src/, which has no
    tracked files; and the Dockerfile's default command ran dashboard.py, which
    displayed the fabrication-era synthetic datasets. Three published surfaces,
    none of them exercised by any test, all broken or worse.
    """
    offenders = []

    pyproject = REPO / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        for module in re.findall(r'^\s*[\w-]+\s*=\s*"([\w.]+):\w+"', text, re.M):
            path = REPO / (module.replace(".", "/") + ".py")
            if not path.exists():
                offenders.append(f"pyproject console script -> {module} (no such module)")
        for where in re.findall(r'where\s*=\s*\["([^"]+)"\]', text):
            listing = subprocess.run(["git", "ls-files", where], cwd=REPO,
                                     capture_output=True, text=True, timeout=300).stdout
            if not listing.strip():
                offenders.append(f"pyproject packages.find where={where} (no tracked files)")

    dockerfile = REPO / "Dockerfile"
    if dockerfile.exists():
        for line in dockerfile.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip().startswith(("CMD", "ENTRYPOINT")):
                continue
            for token in re.findall(r'"([\w./-]+\.(?:py|sh))"', line):
                if not (REPO / token).exists():
                    offenders.append(f"Dockerfile {line.split()[0]} -> {token}")

    assert not offenders, (
        f"published entry points name things that are not there: {offenders}"
    )


def test_the_issue_templates_point_at_live_files():
    """GitHub renders these to anyone reporting a problem.

    The data-issue template offered `results_rootcause/study1_results.json` as
    its worked example -- the fabricated 22-model dataset, whose models the audit
    found do not exist. A contributor filing their first issue was being handed
    the retracted data as the canonical thing to talk about.
    """
    templates = sorted((REPO / ".github" / "ISSUE_TEMPLATE").glob("*.md"))
    if not templates:
        pytest.skip("[repo] no issue templates")
    offenders = []
    for path in templates:
        text = path.read_text(encoding="utf-8", errors="replace")
        for cited in re.findall(r"`([\w./-]+\.(?:json|py|tex|sh|csv))`", text):
            if not (REPO / cited).exists():
                offenders.append(f"{path.name} -> {cited}")
                continue
            if cited.startswith(("results_rootcause/", "RETRACTED/")):
                offenders.append(f"{path.name} -> {cited} (superseded data)")
    assert not offenders, (
        f"issue templates offer files that are missing or superseded: {offenders}"
    )


def test_the_makefile_advertises_no_removed_target():
    makefile = REPO / "Makefile"
    if not makefile.exists():
        pytest.skip("[repo] no Makefile")
    text = makefile.read_text(encoding="utf-8", errors="replace")
    advertised = set(re.findall(r'"make ([\w-]+)"', text))
    defined = set(re.findall(r"^([\w-]+):", text, re.M))
    missing = sorted(advertised - defined)
    assert not missing, (
        f"the help text offers targets that no longer exist: {missing}"
    )


def test_every_makefile_recipe_names_something_that_exists():
    """A recipe pointing at a quarantined script fails only when someone runs it."""
    makefile = REPO / "Makefile"
    if not makefile.exists():
        pytest.skip("[repo] no Makefile")
    missing = []
    for line in makefile.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("\t"):
            continue
        code = line.split("#", 1)[0]
        # A recipe may cd first: "cd paper/honest && python arxiv_package.py".
        # Resolving the script against the repository root alone reports every
        # such line as missing, which is how a guard ends up disabled.
        cd = re.search(r"\bcd\s+([\w./-]+)", code)
        base = REPO / cd.group(1) if cd else REPO
        for token in re.findall(r"(?<![\w/.-])([\w./-]+\.(?:py|sh))", code):
            if token.startswith("$") or "*" in token:
                continue
            if not (base / token).exists() and not (REPO / token).exists():
                missing.append(f"{token} ({line.strip()[:50]})")
    assert not missing, (
        f"Makefile recipes invoke files that are not there: {sorted(set(missing))}"
    )
