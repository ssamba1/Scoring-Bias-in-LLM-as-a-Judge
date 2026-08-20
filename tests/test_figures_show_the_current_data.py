"""Do the committed figures draw what the current data produces?

A figure is a published claim that no test read. The analyses, the prose, the
tables and the archive were all guarded; the ten PDFs in `paper/honest/figures`
were checked only by a CI workflow step, so on any machine without that step
a figure could go stale silently.

It did. Correcting the responsiveness term changed the mechanism panels, and
every local check stayed green while `fig_mech.pdf` still drew the old numbers.
CI caught it, which is the right outcome, but only after the wrong figure had
been committed twice and described as verified.

`check_figures.py` compares the text drawn into each figure against the data
rather than comparing bytes -- a PDF embeds a creation timestamp, so bytes
always differ, and a raster comparison lapses whenever the rendering stack
changes. This runs that same comparison as part of the suite.

It needs `pdftotext`, which is why it had lived only in CI. That is a reason to
skip where the tool is absent, not a reason for the check to exist nowhere:
pdftotext ships with Git for Windows, so the skip is narrower than it looks.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"
CHECKER = REPRO / "check_figures.py"


def test_the_committed_figures_match_the_data():
    if not CHECKER.exists():
        pytest.skip("[repro] check_figures.py not present")
    if shutil.which("pdftotext") is None:
        pytest.skip("[pdftotext] not on PATH; the figure content check needs it")

    result = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=str(REPRO), capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "the committed figures do not show what the current data produces:\n"
        f"{result.stdout.strip()}\n{result.stderr.strip()}\n"
        "Regenerate them (make_mech_figures.py and the other make_*_figure.py "
        "scripts) and rebuild the archive -- a figure is a published claim, and "
        "a stale one contradicts the corrected numbers beside it."
    )
