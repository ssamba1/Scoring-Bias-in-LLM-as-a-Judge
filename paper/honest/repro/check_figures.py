#!/usr/bin/env python3
"""Do the committed figures still show what the current data produces?

The CI gate regenerates every analysis and diffs the derived JSON and the LaTeX
tables. Figures were not covered, so a figure could drift from its data and
nothing would say so -- which is how a companion project ended up with a
published chart contradicting its own table for months.

Byte comparison does not work here. A PDF embeds a creation timestamp, so
regenerating produces different bytes for identical content. The companion
projects compare PNG bytes instead and skip the check whenever the rendering
stack differs, which means it lapses precisely when someone changes environment.

These figures are vector PDFs, so there is a better signal: the text drawn into
them -- axis labels, tick values, annotations, legend entries -- together with
the page geometry. Both are stack-independent in a way raster bytes are not. A
figure plotted from changed numbers moves its ticks or its annotations; a figure
rendered by a different matplotlib does not.

Which figures get checked is read off the paper, not listed here. The previous
version named four generators by hand while the paper included ten figures, so
six were unchecked and nothing said so -- the same failure as a hand-maintained
CI list, which is what this file exists to prevent. Now every \\includegraphics
in the paper must be reproduced by some generator, and one that no generator
writes is reported as unverifiable rather than passed over.

    python check_figures.py [--keep]

Regenerates into a scratch directory, compares content, and leaves the committed
figures untouched. Exit code 1 on any content difference or uncovered figure.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
FIGURES = PAPER / "figures"


def _included_figures():
    """Every figure the paper actually draws, resolved from its \\includegraphics."""
    names = set()
    for tex in PAPER.glob("*.tex"):
        body = tex.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", body):
            name = match.group(1).strip()
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            names.add(Path(name).name)
    return sorted(names)


def _generators():
    return sorted(HERE.glob("make_*.py"))


def _text(path):
    result = subprocess.run(
        ["pdftotext", "-raw", str(path), "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if result.returncode != 0:
        return None
    return " ".join(result.stdout.split())


def _geometry(path):
    result = subprocess.run(
        ["pdfinfo", str(path)], capture_output=True, text=True, errors="replace", timeout=180
    )
    for line in result.stdout.splitlines():
        if line.startswith("Page size"):
            return line.split(":", 1)[1].strip()
    return None


def main(keep=False):
    if shutil.which("pdftotext") is None:
        print("pdftotext not available; cannot compare figure content")
        return 0

    required = _included_figures()
    if not required:
        print("no figures referenced by the paper")
        return 0

    # Snapshot *every* file in the figure directory, not only the ones the paper
    # includes. The generators also emit PNG companions and figures the current
    # paper no longer draws; restoring just the required set left those rewritten
    # in the working tree, which is exactly the spurious diff this check exists
    # to avoid creating.
    originals = {p.name: p.read_bytes() for p in FIGURES.iterdir() if p.is_file()}

    if not originals:
        print("no committed figures to check")
        return 0

    scratch = Path(tempfile.mkdtemp(prefix="figure-check-"))
    for name, data in originals.items():
        (scratch / name).write_bytes(data)

    failures, unverifiable = [], []
    writers = {}  # figure name -> [generators that wrote it]
    try:
        for script in _generators():
            before = {p.name: p.read_bytes() for p in FIGURES.iterdir() if p.is_file()}
            result = subprocess.run(
                [sys.executable, str(script)], cwd=HERE, capture_output=True, text=True, timeout=1800
            )
            if result.returncode != 0:
                failures.append(f"{script.name} failed to run:\n{result.stderr[-600:]}")
            # Regenerating a PDF always changes its bytes (embedded timestamp),
            # so "changed" identifies exactly what this generator wrote. Running
            # them one at a time and diffing after each is the only way to see a
            # collision: run them all at once and the last writer silently wins.
            for path in FIGURES.iterdir():
                if path.is_file() and before.get(path.name) != path.read_bytes():
                    writers.setdefault(path.name, []).append(script.name)

        for name in sorted(set(required) & set(writers)):
            if len(writers[name]) > 1:
                failures.append(
                    f"{name}: written by {len(writers[name])} generators "
                    f"({', '.join(writers[name])}). Which one the paper ships is "
                    f"decided by filename order, not by intent."
                )

        for name in required:
            committed = scratch / name
            regenerated = FIGURES / name
            if not committed.exists():
                failures.append(f"{name}: included by the paper but not committed")
                continue
            if name not in writers:
                # No generator wrote this file, so it cannot be checked against
                # the data. Saying so is the point.
                unverifiable.append(name)
                continue
            old_text, new_text = _text(committed), _text(regenerated)
            if old_text != new_text:
                failures.append(
                    f"{name}: the text drawn into the figure changed. The committed "
                    f"figure does not show what the current data produces."
                )
            elif _geometry(committed) != _geometry(regenerated):
                failures.append(
                    f"{name}: page geometry changed "
                    f"({_geometry(committed)} -> {_geometry(regenerated)})"
                )
    finally:
        # Put the committed bytes back: regenerating changes only the embedded
        # timestamp, and leaving that behind would show as a spurious diff.
        for name, data in originals.items():
            (FIGURES / name).write_bytes(data)
        if not keep:
            shutil.rmtree(scratch, ignore_errors=True)

    if failures:
        print("FIGURE CONTENT DIFFERENCES:")
        for failure in failures:
            print(" -", failure)
        return 1

    checked = len(required) - len(unverifiable)
    print(f"figures match the current data ({checked}/{len(required)} checked, content compared)")
    if unverifiable:
        print(
            "  no generator in this directory writes: "
            + ", ".join(unverifiable)
            + "\n  these are committed but cannot be checked against the data."
        )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="keep the scratch copies")
    sys.exit(main(**vars(parser.parse_args())))
