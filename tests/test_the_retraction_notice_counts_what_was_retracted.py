"""The interactive hub must name every dashboard it withdrew.

`paper/interactive/index.html` tells a reader which dashboards were retracted
and where they were put. It said "Three of the four dashboards here have been
retracted" and named Bias Explorer, Model Comparison and Model Ranking.

Four are preserved under `RETRACTED/paper/interactive/`. The fourth is the
Root-Cause Summary dashboard, and git records it plainly: it lived at
`paper/interactive/analysis_dashboard.html` and was moved out by the commit
"Quarantine 44 fabricated artefacts the first retraction left behind". So the
hub had five dashboards, four were withdrawn, and the notice accounted for
three.

Nothing was hidden -- the file is in the repository, in the directory the notice
points at. But an undercount in a retraction notice is the worst place for one:
the whole purpose of the notice is to say what was withdrawn, and a reader
checking it against the directory finds one more than they were told about.

This compares the two directly. It cannot know whether the prose is *fair*, only
whether it accounts for everything that is there, which is the part that can be
checked mechanically.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "paper" / "interactive" / "index.html"
QUARANTINE = "RETRACTED/paper/interactive/"

# Display name in the notice -> the file it was moved to.
DASHBOARDS = {
    "Bias Explorer": "bias_explorer.html",
    "Model Comparison": "model_comparison.html",
    "Model Ranking": "ranking_table.html",
    "Root-Cause Summary": "analysis_dashboard.html",
}


def _notice_text():
    if not INDEX.exists():
        pytest.skip("[interactive] index.html not present")
    raw = INDEX.read_text(encoding="utf-8", errors="replace")
    stripped = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S)
    stripped = re.sub(r"<[^>]+>", " ", stripped).replace("&nbsp;", " ")
    return " ".join(stripped.split())


def _quarantined():
    listing = subprocess.run(
        ["git", "ls-files", QUARANTINE],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    if listing.returncode != 0:
        pytest.skip("[git] cannot list the quarantine directory")
    return sorted(Path(line).name for line in listing.stdout.split() if line.endswith(".html"))


def test_every_quarantined_dashboard_is_named_in_the_notice():
    text, quarantined = _notice_text(), _quarantined()
    if not quarantined:
        pytest.skip("[interactive] nothing quarantined")

    known = {name: display for display, name in DASHBOARDS.items()}
    unaccounted = sorted(f for f in quarantined if f not in known)
    assert not unaccounted, (
        f"{unaccounted} are quarantined under {QUARANTINE} but this test does "
        f"not know their display name. Add them to DASHBOARDS and name them in "
        f"the notice, or a reader comparing the notice against the directory "
        f"finds withdrawn material the notice never mentions."
    )

    unnamed = sorted(known[f] for f in quarantined if known[f] not in text)
    assert not unnamed, (
        f"{unnamed} are preserved under {QUARANTINE} but are not named in the "
        f"retraction notice. The notice exists to say what was withdrawn."
    )


def test_the_notice_counts_them_correctly():
    text, quarantined = _notice_text(), _quarantined()
    if not quarantined:
        pytest.skip("[interactive] nothing quarantined")

    words = {3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven"}
    expected = words.get(len(quarantined))
    assert expected, f"no word for {len(quarantined)} retracted dashboards"
    assert f"{expected} of the" in text, (
        f"the notice does not say '{expected} of the ...' -- {len(quarantined)} "
        f"dashboards are quarantined under {QUARANTINE}. It previously said "
        f"'Three of the four' while four were withdrawn."
    )

    live = sorted(
        p.name for p in (REPO / "paper" / "interactive").glob("*.html")
        if p.name != "index.html"
    )
    total = words.get(len(quarantined) + len(live))
    assert total and f"of the {total.lower()} dashboards" in text, (
        f"the notice should describe {len(quarantined)} of "
        f"{len(quarantined) + len(live)} dashboards; the hub currently holds "
        f"{live} alongside {len(quarantined)} quarantined"
    )


def test_the_quarantine_path_the_notice_gives_is_real():
    text = _notice_text()
    assert QUARANTINE in text, (
        f"the notice no longer tells the reader where the withdrawn dashboards "
        f"are. It pointed at {QUARANTINE}."
    )
    assert (REPO / QUARANTINE).is_dir(), (
        f"{QUARANTINE} is named in the retraction notice but is not a directory"
    )
