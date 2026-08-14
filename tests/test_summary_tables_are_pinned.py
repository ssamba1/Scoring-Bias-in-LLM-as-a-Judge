r"""The summary, domain and ground-truth tables, pinned cell by cell.

Companion to test_cited_tables_are_pinned.py, which covers the per-family table.
These three carry the numbers the abstract and the results section quote
directly -- the per-probe effect sizes, the domain breakdown, and the
ground-truth degradation -- so a cell drifting from its source here moves a
headline claim, not a supporting one.

Same construction: expected values are read from the derived JSON at collection
time, never written into this file, so the test cannot become a second copy of
the data that drifts on its own. Each case names the row and column that stopped
matching.

The confidence intervals are pinned as a pair rather than as two independent
numbers. An interval whose endpoints came from different runs is a defect no
per-endpoint check would notice, since each endpoint on its own would still
trace to something.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HONEST = REPO / "paper" / "honest"
TABLES = HONEST / "tables"
REPRO = HONEST / "repro"


def _load(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _body_rows(name):
    """Rows of a generated table that start with a label and contain columns."""
    path = TABLES / name
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "&" not in line or line.lstrip().startswith("%"):
            continue
        if any(tag in line for tag in ("\\multirow", "\\multicolumn", "textbf{Probe}",
                                       "textbf{Domain}", "textbf{Family}")):
            continue
        cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
        if not cells or not re.match(r"^[A-Za-z]", cells[0]):
            continue
        rows.append(cells)
    return rows


def _number(cell):
    """First signed number in a table cell, ignoring LaTeX decoration."""
    text = re.sub(r"\\textbf\{|\\[a-zA-Z]+|[{}$]", " ", cell)
    m = re.search(r"[-+]?\d*\.?\d+", text.replace("\u2212", "-"))
    return float(m.group(0)) if m else None


# ---- per-probe summary table -------------------------------------------------
PERITEM = _load(REPRO / "results_peritem.json")
SUMMARY = (PERITEM or {}).get("summary", {})

# column index -> (json key, decimals). Columns after the label:
# base, instruct, change, d_z, CI, p_Holm, flips
SUMMARY_COLUMNS = [
    (0, "base_mean_delta", 2),
    (1, "instruct_mean_delta", 2),
    (2, "mean_change", 2),
    (3, "cohen_dz", 2),
    (5, "wilcoxon_p_holm", 3),
]


def _summary_cases():
    out = []
    by_label = {rec["label"]: (probe, rec) for probe, rec in SUMMARY.items() if "label" in rec}
    for cells in _body_rows("tab_v2_summary.tex"):
        entry = by_label.get(cells[0])
        if not entry:
            continue
        probe, record = entry
        for offset, key, places in SUMMARY_COLUMNS:
            if key not in record or offset + 1 >= len(cells):
                continue
            out.append(pytest.param(probe, key, cells[offset + 1], record[key], places,
                                    id=f"{probe}-{key}"))
    return out


SUMMARY_CASES = _summary_cases()


@pytest.mark.skipif(not SUMMARY_CASES, reason="[table] tab_v2_summary.tex or its source is absent")
@pytest.mark.parametrize("probe,key,printed,value,places", SUMMARY_CASES)
def test_summary_cell_matches_its_source(probe, key, printed, value, places):
    shown = _number(printed)
    assert shown is not None, f"{probe}/{key}: no number in cell {printed!r}"
    assert abs(shown - round(value, places)) < 10 ** -places / 2 + 1e-9, (
        f"{probe} / {key}: the table shows {shown}, the data holds {value} "
        f"(rounds to {round(value, places)})"
    )


def _ci_cases():
    out = []
    by_label = {rec["label"]: (probe, rec) for probe, rec in SUMMARY.items() if "label" in rec}
    for cells in _body_rows("tab_v2_summary.tex"):
        entry = by_label.get(cells[0])
        if not entry or len(cells) < 6:
            continue
        probe, record = entry
        if "boot_ci95" in record:
            out.append(pytest.param(probe, cells[5], record["boot_ci95"], id=probe))
    return out


CI_CASES = _ci_cases()


@pytest.mark.skipif(not CI_CASES, reason="[table] no confidence intervals to check")
@pytest.mark.parametrize("probe,printed,interval", CI_CASES)
def test_summary_interval_matches_its_source(probe, printed, interval):
    """Both endpoints, together: a mixed-run interval passes any per-endpoint check."""
    found = [float(x) for x in re.findall(r"[-+]?\d*\.\d+", printed.replace("\u2212", "-"))]
    assert len(found) == 2, f"{probe}: expected two endpoints in {printed!r}, found {found}"
    expected = [round(v, 2) for v in interval]
    # Signed, not magnitude. Comparing absolute values would accept an endpoint
    # whose sign had flipped -- which for a bootstrap interval is the difference
    # between excluding zero and containing it, i.e. the entire claim.
    assert found == expected, (
        f"{probe}: the table shows [{found[0]:+}, {found[1]:+}], the data holds "
        f"[{expected[0]:+}, {expected[1]:+}]"
    )
    assert found[0] <= found[1], f"{probe}: interval endpoints are out of order: {found}"


# ---- domain table ------------------------------------------------------------
DOMAIN = (PERITEM or {}).get("domain", {})


def _domain_cases():
    out = []
    for cells in _body_rows("tab_v2_domain.tex"):
        key = cells[0].strip().lower().replace(" ", "_")
        record = DOMAIN.get(key)
        if not record or len(cells) < 3:
            continue
        out.append(pytest.param(key, "base", cells[1], record["base"], id=f"{key}-base"))
        out.append(pytest.param(key, "instruct", cells[2], record["instruct"],
                                id=f"{key}-instruct"))
    return out


DOMAIN_CASES = _domain_cases()


@pytest.mark.skipif(not DOMAIN_CASES, reason="[table] tab_v2_domain.tex or its source is absent")
@pytest.mark.parametrize("domain,arm,printed,value", DOMAIN_CASES)
def test_domain_cell_matches_its_source(domain, arm, printed, value):
    shown = _number(printed)
    assert shown == round(value, 2), (
        f"{domain} / {arm}: the table shows {shown}, the data holds {value}"
    )


# ---- ground-truth degradation table -----------------------------------------
GOLD = _load(REPRO / "results_gold.json") or {}
DEGRADATION = GOLD.get("degradation", {})


def _gold_cases():
    out = []
    for cells in _body_rows("tab_gold.tex"):
        condition = cells[0].strip().lower()
        record = DEGRADATION.get(condition)
        if not record or len(cells) < 5:
            continue
        for index, (arm, key) in enumerate(
            [("base", "accuracy_under_bias"), ("instruct", "accuracy_under_bias"),
             ("base", "margin_drop"), ("instruct", "margin_drop")]
        ):
            if key in record.get(arm, {}):
                out.append(pytest.param(condition, arm, key, cells[index + 1],
                                        record[arm][key], id=f"{condition}-{arm}-{key}"))
    return out


GOLD_CASES = _gold_cases()


@pytest.mark.skipif(not GOLD_CASES, reason="[table] tab_gold.tex or its source is absent")
@pytest.mark.parametrize("condition,arm,key,printed,value", GOLD_CASES)
def test_gold_cell_matches_its_source(condition, arm, key, printed, value):
    shown = _number(printed)
    assert shown == round(value, 2), (
        f"{condition} / {arm} / {key}: the table shows {shown}, the data holds {value}"
    )


# ---- structural guards -------------------------------------------------------
def test_the_generated_case_sets_are_not_empty():
    """Vacuity guard: a parse returning nothing silently deletes every case above."""
    assert len(SUMMARY_CASES) >= 20, f"{len(SUMMARY_CASES)} summary cases generated"
    assert len(CI_CASES) == 5, f"{len(CI_CASES)} interval cases, expected 5 probes"
    assert len(DOMAIN_CASES) == 10, f"{len(DOMAIN_CASES)} domain cases, expected 5 x 2"
    assert len(GOLD_CASES) >= 8, f"{len(GOLD_CASES)} ground-truth cases generated"


def test_every_probe_and_domain_in_the_data_is_tabulated():
    """A row dropped from a table would otherwise just reduce the case count."""
    if not SUMMARY or not DOMAIN:
        pytest.skip("[source] results_peritem.json not present")
    tabulated = {cells[0] for cells in _body_rows("tab_v2_summary.tex")}
    missing = sorted(r["label"] for r in SUMMARY.values() if r.get("label") not in tabulated)
    assert not missing, f"probes in the data but absent from the summary table: {missing}"

    shown = {c[0].strip().lower().replace(" ", "_") for c in _body_rows("tab_v2_domain.tex")}
    absent = sorted(set(DOMAIN) - shown)
    assert not absent, f"domains in the data but absent from the domain table: {absent}"
