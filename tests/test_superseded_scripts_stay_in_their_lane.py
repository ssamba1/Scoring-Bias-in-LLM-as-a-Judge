"""Can anything under superseded/ write into the paper of record?

`superseded/make_figures.py` draws Figure 1 titled "Instruction tuning reduces
scoring bias (n=7 families)" -- the conclusion the 13-family panel overturned.
It used to live in repro/, where it resolved its output as

    FIG = HERE.parent / "figures"

which was the current paper's figure directory. Moving the file to superseded/
did not change that expression: HERE.parent is still paper/honest, so the
relocated script could still overwrite the paper's Figure 1 with the false
title. The same was true of `superseded/analyze.py`, whose TAB_DIR resolved to
the live tables directory.

Relocating a script does not relocate its paths. This checks that no script
under superseded/ addresses a sibling directory of its own parent, which is the
only way it can reach the live tree from where it now sits.

The check is static rather than behavioural on purpose: running these scripts to
find out where they write is precisely the thing that would do the damage.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest


def _figure_text(path):
    """The text drawn into a figure, or None if it cannot be read."""
    result = subprocess.run(
        ["pdftotext", "-raw", str(path), "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
    )
    return " ".join(result.stdout.split()) if result.returncode == 0 else None

REPO = Path(__file__).resolve().parent.parent
SUPERSEDED = REPO / "paper" / "honest" / "superseded"

# `HERE.parent / "figures"`, `OUT_DIR.parent / 'tables'`, `.parents[0] / "figures"`
ESCAPES = re.compile(
    r"""\.\s*parents?\s*(?:\[\s*\d+\s*\])?\s*/\s*['"](figures|tables|repro)['"]""",
    re.X,
)

LIVE_DIRS = ("figures", "tables", "repro")


def _scripts():
    if not SUPERSEDED.is_dir():
        pytest.skip("[superseded] directory not present")
    scripts = sorted(SUPERSEDED.glob("*.py"))
    if not scripts:
        pytest.skip("[superseded] no scripts to check")
    return scripts


def _code_only(path):
    """Source with comments and string literals removed.

    Both scripts carry a comment quoting the defective expression, to explain why
    the corrected line reads the way it does. A scan of raw text flags those
    comments -- the same trap as a guard that spells out the fabricated names it
    hunts for. Only executable code can actually write to a directory.
    """
    import io
    import tokenize

    kept = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8")).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            kept.append((tok.start[0], tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return [(1, path.read_text(encoding="utf-8", errors="replace"))]
    return kept


@pytest.mark.parametrize("script", _scripts(), ids=lambda p: p.name)
def test_script_does_not_address_the_live_paper_directories(script):
    # Rebuild each line from its non-comment, non-string tokens. The directory
    # name itself is a string literal, so match on the tokens either side of it.
    by_line = {}
    for lineno, piece in _code_only(script):
        by_line.setdefault(lineno, []).append(piece)
    raw = script.read_text(encoding="utf-8", errors="replace").splitlines()

    escapes = []
    for lineno, pieces in by_line.items():
        joined = "".join(pieces)
        if re.search(r"\.parents?(\[\s*\d+\s*\])?/", joined) and lineno <= len(raw):
            source_line = raw[lineno - 1]
            if ESCAPES.search(source_line) and not source_line.lstrip().startswith("#"):
                escapes.append(f"{script.name}:{lineno}: {source_line.strip()}")
    assert not escapes, (
        f"{script.name} builds a path into a sibling of its own parent, which is "
        f"the paper of record's tree: {escapes}. A superseded script must write "
        f"beside itself -- these scripts draw the overturned conclusion."
    )


def test_the_pattern_matches_the_expression_it_was_written_for():
    """Vacuity guard: the regex must still catch the original bug."""
    original = 'FIG = HERE.parent / "figures"'
    assert ESCAPES.search(original), "the escape pattern no longer matches the original defect"
    assert ESCAPES.search("TAB_DIR = OUT_DIR.parent / 'tables'")
    assert not ESCAPES.search('FIG = HERE / "figures"'), "the pattern flags the correct form"


def test_superseded_outputs_are_not_shared_with_the_paper():
    """No file name under superseded/ may collide with one the paper ships.

    Two generators writing one filename is how the paper's Figure 1 came to
    depend on filename ordering. Keeping the names disjoint across directories
    removes the possibility rather than detecting it later.
    """
    live_names = set()
    for name in LIVE_DIRS[:2]:
        live = REPO / "paper" / "honest" / name
        if live.is_dir():
            live_names |= {p.name for p in live.iterdir() if p.is_file()}

    clashes = []
    for sub in LIVE_DIRS[:2]:
        mirror = SUPERSEDED / sub
        if not mirror.is_dir():
            continue
        for path in mirror.iterdir():
            if path.is_file() and path.name in live_names:
                clashes.append(f"{sub}/{path.name}")
    # Sharing a filename is expected -- the superseded draft has its own fig1 --
    # so the question is not whether names collide but whether the live copy is
    # the superseded one. `assert isinstance(clashes, list)` stood here and
    # could not fail; this checks the thing that would actually be wrong.
    if not clashes:
        pytest.skip("[no shared names] nothing to distinguish")
    if shutil.which("pdftotext") is None:
        pytest.skip("[pdftotext] cannot read figure text to tell the copies apart")

    same = []
    for name in clashes:
        live = REPO / "paper" / "honest" / name
        mirror = SUPERSEDED / name
        if not (live.exists() and mirror.exists() and live.suffix == ".pdf"):
            continue
        if _figure_text(live) == _figure_text(mirror):
            same.append(name)
    assert not same, (
        f"the paper ships {same}, whose drawn text is identical to the "
        f"superseded draft's copy -- a superseded generator has written into "
        f"the live tree"
    )
