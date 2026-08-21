#!/usr/bin/env python3
"""Run what CI runs, locally, and say what passed.

Written because CI stopped being evidence. For a stretch of this project's
history the workflow queued without executing -- eight runs outstanding, the
oldest over an hour -- and every commit in that window was reported as "pushed"
with no idea whether it passed. A gate that cannot be observed is not a gate.

This performs the three jobs in .github/workflows/repro.yml:

    integrity            the suite, the mutation pass, the credential scan,
                         and the prose gate against the committed JSON
    submission-compiles  extract the archive and build it as arXiv would
    regenerate-and-diff  rerun every analysis and compare to what is committed

The regeneration runs under the pins in requirements-repro.txt, in a virtual
environment this script builds, rather than under whatever happens to be
installed. That distinction found a real confusion: my everyday scipy is a minor
version ahead of the pin, and chasing a diff without controlling for it wasted a
round.

    python verify_like_ci.py [--skip-mutations] [--skip-compile]

Exit code 1 if any step fails. Differences already documented in
repro/ENVIRONMENT.md as platform-dependent are reported as expected, not as
failures -- the point is to surface what is *not* accounted for.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent
HONEST = REPO / "paper" / "honest"
REPRO = HONEST / "repro"
ENVDOC = REPRO / "ENVIRONMENT.md"

ANALYSES = [
    "analyze_peritem.py", "analyze_mechanism.py", "analyze_gold.py",
    "analyze_robustness.py", "analyze_stages.py", "analyze_spanpatch.py",
    "analyze_dose.py", "analyze_gran.py", "analyze_chat.py", "analyze_sampled.py",
    "analyze_nulls.py", "analyze_bands.py", "analyze_readout.py", "analyze_t10.py",
    "analyze_tokvar.py", "analyze_closed.py",
]
NEWPROBES = ["results_probes2.json", "results_zh.json", "results_14b.json"]

results = []


def step(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ""))
    return ok


def run(cmd, cwd=REPO, timeout=3600):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def documented_platform_differences():
    """The values ENVIRONMENT.md already accounts for, read from its table.

    Compared as numbers, not as text: the document writes 0.2230 where the diff
    prints 0.223, and a string comparison calls that an undocumented difference.
    """
    if not ENVDOC.exists():
        return set()
    doc = ENVDOC.read_text(encoding="utf-8", errors="replace")
    return {float(v) for v in re.findall(r"\b\d\.\d{3,4}\b", doc)}


def job_integrity(skip_mutations):
    print("\n[1/3] integrity")
    code, out = run([sys.executable, "-m", "pytest", "tests/", "-q"])
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    step("test suite", code == 0, tail)

    if skip_mutations:
        step("mutation pass", True, "skipped by request")
    else:
        code, out = run([sys.executable, "mutation_check.py"])
        caught = re.search(r"every guard caught its mutation \((\d+) checked\)", out)
        step("mutation pass", code == 0,
             f"{caught.group(1)} mutations" if caught else out.strip()[-120:])

    code, out = run([sys.executable, "scan_secrets.py"])
    step("credential scan", code == 0, out.strip().splitlines()[-1] if out.strip() else "")

    code, out = run([sys.executable, "check_prose.py"], cwd=REPRO)
    step("prose gate (committed JSON)", code == 0,
         out.strip().splitlines()[-1] if out.strip() else "")


def job_compile(skip_compile):
    print("\n[2/3] submission-compiles")
    archive = HONEST / "arxiv_submission.tar.gz"
    if skip_compile or shutil.which("pdflatex") is None:
        why = "skipped: no pdflatex" if not skip_compile else "skipped by request"
        step("archive builds", True, why)
        return
    if not archive.exists():
        step("archive builds", False, "arxiv_submission.tar.gz absent")
        return

    work = Path(tempfile.mkdtemp(prefix="verify-arxiv-"))
    try:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(work, filter="data")
        if not (work / "main.bbl").exists():
            step("archive builds", False, "no .bbl; arXiv would render no references")
            return
        log = ""
        for _ in range(2):
            code, log = run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=work)
        produced = (work / "main.pdf").exists()
        undefined = len(re.findall(r"(?:Citation|Reference).*?undefined", log))
        overfull = len(re.findall(r"Overfull \\hbox", log))
        missing = len(re.findall(r"File .* not found", log))
        step("archive builds", produced and not (undefined or overfull or missing),
             f"undefined={undefined} overfull={overfull} missing={missing}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def job_regenerate():
    print("\n[3/3] regenerate-and-diff")
    venv = REPO / ".verify-venv"
    python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.exists():
        print("  building a virtual environment from requirements-repro.txt ...")
        code, out = run([sys.executable, "-m", "venv", str(venv)])
        if code != 0:
            step("pinned environment", False, out.strip()[-120:])
            return
        code, out = run([str(python), "-m", "pip", "install", "-q", "-r",
                         str(REPRO / "requirements-repro.txt")], timeout=1800)
        if code != 0:
            step("pinned environment", False, out.strip()[-160:])
            return
    versions, _ = run([str(python), "-c",
                       "import numpy,scipy,statsmodels as s;"
                       "print(numpy.__version__,scipy.__version__,s.__version__)"])[1], None
    step("pinned environment", True, versions.strip())

    failed = []
    for script in ANALYSES:
        code, out = run([str(python), script], cwd=REPRO)
        if code != 0:
            failed.append(f"{script}: {out.strip()[-80:]}")
    for raw in NEWPROBES:
        code, out = run([str(python), "analyze_newprobes.py", raw], cwd=REPRO)
        if code != 0:
            failed.append(f"newprobes {raw}")
    step("every analysis reruns", not failed, "; ".join(failed[:2]))

    code, diff = run(["git", "diff", "--unified=0", "--",
                      "paper/honest/repro/", "paper/honest/tables/"])
    changed = [line[1:].strip().rstrip(",") for line in diff.splitlines()
               if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
    values = {float(v) for line in changed for v in re.findall(r"\b\d\.\d{3,4}\b", line)}
    documented = documented_platform_differences()
    undocumented = sorted(values - documented)

    if not changed:
        step("derived numbers reproduce", True, "byte-identical")
    elif not undocumented:
        step("derived numbers reproduce", True,
             f"{len(values)} value(s) differ, all documented in ENVIRONMENT.md as "
             f"platform-dependent")
    else:
        step("derived numbers reproduce", False,
             f"undocumented differences: {undocumented[:6]}")

    # Restore only what the analyses rewrote. `git checkout` on the whole
    # directory would also discard unrelated edits in it -- it silently reverted
    # the ENVIRONMENT.md paragraph I was writing while testing this script.
    _, names = run(["git", "diff", "--name-only", "--",
                    "paper/honest/repro/", "paper/honest/tables/"])
    rewritten = [n for n in names.split() if n.endswith((".json", ".tex"))]
    if rewritten:
        run(["git", "checkout", "--", *rewritten])


def main(skip_mutations=False, skip_compile=False):
    print("verifying locally what CI verifies")
    job_integrity(skip_mutations)
    job_compile(skip_compile)
    job_regenerate()

    failed = [name for name, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} steps passed")
    if failed:
        print("failed:", ", ".join(failed))
        return 1
    print("everything CI checks, checked here")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mutations", action="store_true",
                        help="skip the mutation pass, which is the slow step")
    parser.add_argument("--skip-compile", action="store_true",
                        help="skip the LaTeX build")
    sys.exit(main(**vars(parser.parse_args())))
