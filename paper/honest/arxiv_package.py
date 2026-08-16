#!/usr/bin/env python3
"""Build the arXiv submission for the honest study, and verify it.

The previous packager (`paper/arxiv_package.py`, now retracted) built from
`camera_ready.tex`, carried placeholder names as the author list, and described
the retracted finding in its abstract metadata. Running it would have rebuilt a
fabricated submission. It is quarantined; this replaces it.

(The placeholder names are not spelled out here on purpose: the fabrication
sweep in `tests/` searches for them, and a file that quotes them trips it. The
strings live in `tests/fabricated_signatures.py`, which is the one file exempt.)

Two properties matter more than convenience here, both learned the hard way in
this project:

  * The archive is verified by EXTRACTING IT and compiling that, not by
    compiling the staging directory. A packaging fault -- a file assembled but
    not added to the tar -- passes the second check and fails the first.
  * arXiv does not run BibTeX. The .bbl is built here and shipped, or the
    references silently vanish from the announced paper.

A digest of the sources is written into the archive as SOURCE.json, so a later
edit to the paper without repackaging is detectable rather than invisible.

    python arxiv_package.py            build and verify
    python arxiv_package.py --check    verify the existing archive only
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = "scoring_bias_v2"
STAGING = HERE / "arxiv_submission"
ARCHIVE = HERE / "arxiv_submission.tar.gz"

# The three top-level sources. Everything else the paper reads is resolved from
# the source below rather than listed here -- a hand-maintained list is how a
# figure goes missing from a submission, and it is how the generated tables went
# undigested while this comment claimed otherwise.
SOURCES = [f"{MAIN}.tex", "macros.tex", "honest.bib"]


def _referenced_assets(tex: str):
    figures = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", tex)
    inputs = re.findall(r"\\input\{([^}]*)\}", tex)
    return figures, inputs


def _resolve(name: str, suffixes=(".tex", ".pdf", ".png")):
    for base in (HERE, HERE / "figures", HERE / "tables"):
        for suffix in ("",) + suffixes:
            candidate = base / (name + suffix)
            if candidate.is_file():
                return candidate
    return None


def _digest(path: Path) -> str:
    """Line-ending normalised, so a CRLF checkout is not a false mismatch."""
    data = path.read_bytes()
    if path.suffix in {".tex", ".bib", ".md"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _stage(src: Path, dest: Path) -> None:
    """Copy into the package, normalising text to LF.

    A plain byte copy carries the working tree's line endings into the archive,
    so a package built on Windows holds CRLF for files git stores as LF. The
    archive then genuinely differs from the sources on any Linux checkout, and
    the guard that exists to prove "the archive is these sources" fails there
    while passing where it was built -- the check reports clean exactly where it
    is least needed. Normalising here makes the package canonical, which is also
    what git stores and what arXiv's build sees.

    Figures are copied byte-for-byte: they are binary, and replacing \\r\\n in a
    PNG corrupts it.
    """
    if src.suffix in {".tex", ".bib", ".md", ".bbl"}:
        dest.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
    else:
        shutil.copy(src, dest)


def _latex(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)


def build():
    tex = (HERE / f"{MAIN}.tex").read_text(encoding="utf-8", errors="replace")
    figures, inputs = _referenced_assets(tex)

    missing = [n for n in figures + inputs if _resolve(n) is None]
    if missing:
        raise SystemExit(f"referenced but not found: {missing}")

    # Rebuild the .bbl from the current .bib: arXiv will not do it.
    print("compiling locally to refresh the .bbl")
    _latex(["pdflatex", "-interaction=nonstopmode", f"{MAIN}.tex"], HERE)
    bibtex = _latex(["bibtex", MAIN], HERE)
    if bibtex.returncode != 0:
        raise SystemExit(f"bibtex failed:\n{bibtex.stdout[-1500:]}")
    _latex(["pdflatex", "-interaction=nonstopmode", f"{MAIN}.tex"], HERE)
    _latex(["pdflatex", "-interaction=nonstopmode", f"{MAIN}.tex"], HERE)

    log = (HERE / f"{MAIN}.log").read_text(encoding="utf-8", errors="ignore")
    overfull = log.count("Overfull \\hbox")
    undefined = len(re.findall(r"(Citation|Reference).*undefined", log))
    print(f"  local build: {overfull} overfull, {undefined} undefined")
    if undefined:
        raise SystemExit("undefined references; fix before packaging")

    if STAGING.exists():
        shutil.rmtree(STAGING)
    (STAGING / "figures").mkdir(parents=True)
    (STAGING / "tables").mkdir(parents=True)

    _stage(HERE / f"{MAIN}.tex", STAGING / "main.tex")
    _stage(HERE / f"{MAIN}.bbl", STAGING / "main.bbl")
    _stage(HERE / "macros.tex", STAGING / "macros.tex")
    for name in set(figures):
        src = _resolve(name)
        _stage(src, STAGING / "figures" / src.name)
    for name in set(inputs):
        src = _resolve(name)
        if src.parent.name == "tables":
            _stage(src, STAGING / "tables" / src.name)

    # The tables are \input by the paper and bundled above, but they were not
    # digested, so a regenerated table shipped stale and silently: the analysis
    # rewrites the numbers, the archive keeps the previous ones, and every check
    # still passed. Digest whatever the paper actually pulls in, resolved from
    # the source, rather than the three names someone typed here.
    #
    # Figures are deliberately excluded. They are PDFs carrying an embedded
    # creation timestamp, so their bytes change on every regeneration even when
    # the content is identical -- digesting them would report staleness that
    # isn't real. check_figures.py compares their content instead.
    digested = list(SOURCES)
    for name in sorted(set(inputs)):
        src = _resolve(name)
        if src.parent.name == "tables":
            digested.append(f"tables/{src.name}")

    manifest = {
        "main": "main.tex",
        "built_from": f"{MAIN}.tex",
        "sources": {name: _digest(HERE / name) for name in digested if (HERE / name).exists()},
        "note": (
            "Digests are of the paper sources at packaging time, line-ending "
            "normalised. If they no longer match, this archive is stale: "
            "rebuild before submitting."
        ),
    }
    # write_bytes, not write_text: on Windows the text writer translates \n to
    # \r\n, which put CRLF into the manifest of an otherwise LF package.
    (STAGING / "SOURCE.json").write_bytes(
        json.dumps(manifest, indent=2).encode("utf-8"))

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with tarfile.open(ARCHIVE, "w:gz") as tar:
        for path in sorted(STAGING.rglob("*")):
            if path.is_file():
                tar.add(path, arcname=str(path.relative_to(STAGING)))
    print(f"  wrote {ARCHIVE.name} ({ARCHIVE.stat().st_size:,} bytes)")
    return verify()


def verify():
    """Extract the archive somewhere clean and compile THAT."""
    if not ARCHIVE.exists():
        raise SystemExit(f"{ARCHIVE.name} does not exist; run without --check")

    with tempfile.TemporaryDirectory(prefix="arxiv-verify-") as tmp:
        work = Path(tmp)
        with tarfile.open(ARCHIVE, "r:gz") as tar:
            # filter="data" refuses absolute paths, ".." escapes and unsafe
            # metadata. It becomes the default in 3.14; setting it explicitly
            # keeps this verification step working the same way on both sides of
            # that change instead of warning now and altering behaviour later.
            tar.extractall(work, filter="data")

        if not (work / "main.bbl").exists():
            raise SystemExit("no main.bbl in the archive; arXiv does not run BibTeX")

        for _ in range(2):
            _latex(["pdflatex", "-interaction=nonstopmode", "main.tex"], work)
        log_path = work / "main.log"
        if not log_path.exists():
            raise SystemExit("the extracted archive did not compile at all")
        log = log_path.read_text(encoding="utf-8", errors="ignore")
        undefined = len(re.findall(r"(Citation|Reference).*undefined", log))
        overfull = log.count("Overfull \\hbox")
        missing = len(re.findall(r"File .* not found", log))
        pages = re.search(r"Output written.*?\((\d+) pages", log)
        if not (work / "main.pdf").exists():
            raise SystemExit(f"no PDF from the extracted archive:\n{log[-1500:]}")
        print(
            f"  extracted archive compiles: {pages.group(1) if pages else '?'} pages, "
            f"{undefined} undefined, {overfull} overfull, {missing} missing files"
        )
        if undefined or missing:
            raise SystemExit("the archive does not stand alone")

    # Are the shipped digests still the current sources?
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        manifest = json.loads(tar.extractfile("SOURCE.json").read().decode("utf-8"))
    stale = [
        name
        for name, digest in manifest["sources"].items()
        if (HERE / name).exists() and _digest(HERE / name) != digest
    ]
    if stale:
        raise SystemExit(f"archive is stale for {stale}; rebuild it")
    print("  archive matches the current sources")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify only")
    args = parser.parse_args()
    sys.exit(verify() if args.check else build())
