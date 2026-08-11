#!/usr/bin/env python3
"""Do the committed figures still show what the current data produces?

The CI gate regenerates every analysis and diffs the derived JSON and the LaTeX
tables. Figures were not covered, so a figure could drift from its data and
nothing would say so -- which is how a companion project ended up with a
published chart contradicting its own table for months.

Byte comparison does not work here. A PDF embeds a creation timestamp, so
regenerating produces different bytes for identical content; the four figures
this script checks differ byte-for-byte on every run and are drawn from exactly
the same numbers. The companion projects compare PNG bytes instead and skip the
check whenever the rendering stack differs, which means it lapses precisely when
someone changes environment.

These figures are vector PDFs, so there is a better signal: the text drawn into
them -- axis labels, tick values, annotations, legend entries -- together with
the page geometry. Both are stack-independent in a way raster bytes are not. A
figure plotted from changed numbers moves its ticks or its annotations; a figure
rendered by a different matplotlib does not.

    python check_figures.py [--keep]

Regenerates into a scratch directory, compares content, and leaves the committed
figures untouched. Exit code 1 on any content difference.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent / "figures"

# generator -> the figures it writes
GENERATORS = {
    "make_concept_figure.py": ["fig_concept.pdf"],
    "make_forest_figure.py": ["fig_forest.pdf"],
    "make_dose_figure.py": ["fig_dose.pdf"],
    "make_stage_figure.py": ["fig_stages.pdf"],
}


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

    originals = {}
    for names in GENERATORS.values():
        for name in names:
            path = FIGURES / name
            if path.exists():
                originals[name] = path.read_bytes()
    if not originals:
        print("no committed figures to check")
        return 0

    scratch = Path(tempfile.mkdtemp(prefix="figure-check-"))
    for name, data in originals.items():
        (scratch / name).write_bytes(data)

    failures = []
    try:
        for generator in GENERATORS:
            script = HERE / generator
            if not script.exists():
                failures.append(f"{generator} is missing; its figures cannot be checked")
                continue
            result = subprocess.run(
                [sys.executable, str(script)], cwd=HERE, capture_output=True, text=True, timeout=1800
            )
            if result.returncode != 0:
                failures.append(f"{generator} failed to run:\n{result.stderr[-600:]}")

        for name in originals:
            committed, regenerated = scratch / name, FIGURES / name
            old_text, new_text = _text(committed), _text(regenerated)
            if old_text != new_text:
                failures.append(
                    f"{name}: the text drawn into the figure changed. The committed "
                    f"figure does not show what the current data produces."
                )
            elif _geometry(committed) != _geometry(regenerated):
                failures.append(f"{name}: page geometry changed ({_geometry(committed)} -> {_geometry(regenerated)})")
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

    print(f"figures match the current data ({len(originals)} checked, content compared)")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="keep the scratch copies")
    sys.exit(main(**vars(parser.parse_args())))
