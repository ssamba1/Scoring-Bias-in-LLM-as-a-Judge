#!/usr/bin/env python3
"""Prepare the Zenodo deposit, and retire the stale DOI in one step.

The paper states, present tense, that its snapshot is archived at
10.5281/zenodo.21499823. That record is v2.1.0 (2026-07-22) and still contains
the figures the score-ordering correction changed, so a referee following the
citation gets the uncorrected paper. Minting a new deposit needs Zenodo
credentials and is the author's action; everything either side of it is not, and
that is what this script does.

    python release_doi.py bundle
        Builds dist/zenodo/ -- the exact two files to upload -- and refuses if
        the compiled PDF does not match the current sources.

    python release_doi.py set-doi 10.5281/zenodo.NNNNNNNN
        Rewrites every surface that cites the DOI, in one pass, then verifies
        that none is left on the old one.

Five files cite it (README three times), which is the shape of edit where one
copy is missed and nobody notices until a reader clicks the wrong link.
tests/test_the_release_tool_knows_every_doi_surface.py fails if a sixth appears.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
HONEST = REPO / "paper" / "honest"
PDF = HONEST / "scoring_bias_v2.pdf"
DIST = REPO / "dist" / "zenodo"

# Every file that names the deposit. Kept here, asserted by a test.
DOI_SURFACES = (
    "README.md",
    "CITATION.cff",
    ".hermes.md",
    ".gitignore",
    "paper/honest/scoring_bias_v2.tex",
    "paper/submission_checklist.md",
    # Pins the live DOI as a constant; a deposit refresh that left this behind
    # would turn the "one DOI everywhere" guard into a guard for the old one.
    "tests/test_one_doi_is_cited_everywhere.py",
    # Two mutation anchors quote the DOI line of CITATION.cff. Rewriting the
    # file without them goes STALE, and a stale anchor is a guard that stops
    # being exercised while the run still reports success.
    "mutation_check.py",
)

# Files that name a Zenodo DOI and must NOT be rewritten, with the reason.
# Enumerated rather than pattern-matched: "skip anything under tests/" would
# have silently caught the one above that does need updating.
DOI_FROZEN = {
    "tests/test_the_archived_snapshot_claim_is_current.py":
        "names the stale deposit on purpose -- it is what the guard detects, and "
        "rewriting it would point the check at the DOI it is meant to flag",
    "paper/honest/REVIEW_AND_ROADMAP.md":
        "names 10.5281/zenodo.21361920, the deleted fabricated deposit, as a "
        "record of the retraction action; it is history, not a citation",
}

DOI_RE = re.compile(r"10\.5281/zenodo\.(\d+)")
CONCEPT = "10.5281/zenodo.21499822"          # all-versions record
LIVE = "10.5281/zenodo.21499823"             # the version the paper cites today
RETRACTED = "10.5281/zenodo.21361920"        # the fabricated deposit, deleted

# DOIs that must survive a refresh untouched. The first version of set-doi
# rewrote every Zenodo DOI it found. Rehearsed on a throwaway clone, it replaced
# the retracted deposit's ID in README, CITATION.cff and .hermes.md -- the
# references that exist to record the retraction -- and flattened the concept
# DOI into the version DOI. Replacing only the live ID is the whole job;
# "every DOI in the file" is a different and destructive one.
PROTECTED = {
    CONCEPT: "the all-versions record, and the self-healing alternative",
    RETRACTED: "the deleted fabricated deposit; those references are the record "
               "of the retraction",
}


def _run(cmd, **kw):
    return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, **kw)


def current_dois():
    """doi -> {surface: count}, over the files that cite one."""
    found = {}
    for rel in DOI_SURFACES:
        path = REPO / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for doi in DOI_RE.findall(text):
            full = f"10.5281/zenodo.{doi}"
            found.setdefault(full, {})[rel] = text.count(full)
    return found


def bundle(_args):
    if not PDF.exists():
        print(f"FAIL: {PDF.relative_to(REPO)} is not built; run arxiv_package.py first")
        return 1

    # The deposit must be the paper as it stands, not an older build.
    status = _run(["git", "status", "--porcelain"]).stdout.strip()
    if status:
        print("FAIL: working tree is dirty; commit before cutting a deposit so the")
        print("      archive corresponds to a commit someone can check out:")
        print("      " + status.splitlines()[0][:100])
        return 1

    sha = _run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    DIST.mkdir(parents=True, exist_ok=True)
    for old in DIST.glob("*"):
        old.unlink()

    source = DIST / f"confidence-is-not-robustness-{sha}.tar.gz"
    result = _run(["git", "archive", "--format=tar.gz", "-o", str(source), "HEAD"])
    if result.returncode != 0:
        print("FAIL: git archive:", result.stderr.strip()[:200])
        return 1
    shutil.copy(PDF, DIST / PDF.name)

    print(f"deposit bundle for {sha} in {DIST.relative_to(REPO)}/")
    for f in sorted(DIST.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
    print()
    print("Upload both to Zenodo as a NEW VERSION of concept record")
    print(f"  {CONCEPT}  (https://doi.org/{CONCEPT})")
    print("then run:")
    print("  python release_doi.py set-doi 10.5281/zenodo.<new-version-id>")
    return 0


def set_doi(args):
    new = args.doi.strip()
    if not DOI_RE.fullmatch(new):
        print(f"FAIL: {new!r} is not a Zenodo DOI of the form 10.5281/zenodo.NNNN")
        return 1

    if new in PROTECTED:
        print(f"FAIL: {new} is {PROTECTED[new]}; it is not a version DOI to cite")
        return 1

    before = current_dois()
    protected_before = {d: dict(s) for d, s in before.items() if d in PROTECTED}

    if LIVE not in before:
        print(f"note: no surface cites {LIVE}; nothing to retire")
        return 0

    changed = []
    for rel in list(before[LIVE]):
        path = REPO / rel
        text = path.read_bytes().decode("utf-8")
        path.write_bytes(text.replace(LIVE, new).encode("utf-8"))
        changed.append(f"{rel} ({before[LIVE][rel]}x)")

    after = current_dois()
    for line in changed:
        print("  " + line)

    if LIVE in after:
        print(f"FAIL: {LIVE} still present in {sorted(after[LIVE])}")
        return 1
    for doi, where in protected_before.items():
        if after.get(doi) != where:
            print(f"FAIL: {doi} was modified; it is {PROTECTED[doi]}")
            return 1

    print(f"\n{LIVE} -> {new} across {len(changed)} file(s); "
          f"{len(protected_before)} protected DOI(s) untouched")
    print("next: python paper/honest/arxiv_package.py && python -m pytest tests/ -q")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("bundle", help="build the files to upload").set_defaults(fn=bundle)
    p = sub.add_parser("set-doi", help="point every surface at a new DOI")
    p.add_argument("doi")
    p.set_defaults(fn=set_doi)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
