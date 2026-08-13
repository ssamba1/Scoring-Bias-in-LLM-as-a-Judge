"""Which files declare a panel size that nothing in the release can verify?

A raw file's `n_items` is its own claim about how many items each cell was
scored on, and every mean in it divides by that number. Where the file also
stores per-item vectors, the claim is checkable, and
test_no_released_cell_was_scored_on_a_truncated_panel checks it. Seven files
store only the means, so their `n_items` is unfalsifiable from their contents:
a run truncated to six items would write six-item means under `n_items: 20` and
read as a full run everywhere it is quoted.

That is a limitation of what those harnesses recorded, not a defect to fix --
the per-item scores were never written, and inventing them is the one thing
this repository must never do. What is fixable is the *silence*. Until now the
truncation guard skipped these files with "records no per-item vectors", which
reads as an absence of anything to check rather than as an unverifiable claim,
and the two are opposite in meaning.

So the set is written down here with a reason each, in the same spirit as the
allowlist in test_every_number_is_accounted_for: a number nobody can check has
to be visible and the set of them has to stay small. A new file that declares a
panel and stores no way to confirm it fails this test until someone either
records the vectors or states why they do not exist.
"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REPRO = REPO / "paper" / "honest" / "repro"

# Files whose cells hold only aggregates, with why no per-item vector exists.
MEANS_ONLY = {
    "results_chat.json":
        "the chat-template harness records one mean per cell per readout",
    "results_gran.json":
        "the granularity harness records one mean per rating scale",
    "results_t10.json":
        "the ten-template harness records one mean per template",
    "results_tokvar.json":
        "the token-variant harness records a mean and an answer mass per readout",
    "patch_results.json":
        "the patch harness records a per-layer curve, not a per-item one",
    "patch_results_qwen05.json":
        "the Qwen-0.5B patch harness records the same per-layer curve",
    "spanpatch_results.json":
        "the span-patch harness records per-layer deltas per span",
}


def _is_per_item_key(key):
    parts = str(key).split("_")
    return any(a == "per" and b == "item" for a, b in zip(parts, parts[1:]))


def _per_item_lengths(blob):
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if _is_per_item_key(key) and isinstance(value, list):
                    found.append(len(value))
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(blob)
    return found


def _declaring_files():
    out = []
    for path in sorted(REPRO.glob("*.json")):
        if path.name.endswith("_analysis.json"):
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        if isinstance(blob, dict) and isinstance(blob.get("n_items"), int):
            out.append((path.name, blob))
    return out


def test_every_declared_panel_is_checkable_or_recorded_as_not():
    unexplained = []
    for name, blob in _declaring_files():
        if _per_item_lengths(blob):
            continue
        if name not in MEANS_ONLY:
            unexplained.append(f"{name} (declares n_items={blob['n_items']})")
    assert not unexplained, (
        f"{len(unexplained)} file(s) declare a panel size that nothing in them "
        f"can confirm, and are not recorded as aggregate-only: {unexplained}. "
        f"Record the per-item vectors, or add the file to MEANS_ONLY with the "
        f"reason its harness did not write them."
    )


def test_the_recorded_files_are_still_aggregate_only():
    """If a harness starts writing vectors, the exemption has to go."""
    now_checkable = []
    for name, blob in _declaring_files():
        if name in MEANS_ONLY and _per_item_lengths(blob):
            now_checkable.append(name)
    assert not now_checkable, (
        f"{now_checkable} now record per-item vectors, so their panel size is "
        f"checkable; remove them from MEANS_ONLY so the truncation guard covers "
        f"them instead of exempting them"
    )


def test_the_environment_note_names_the_same_files():
    """A reader learns this from ENVIRONMENT.md, not from the test file."""
    note = REPRO / "ENVIRONMENT.md"
    if not note.exists():
        pytest.skip("[repro] ENVIRONMENT.md not present")
    # Only this section counts. patch_results.json is also discussed under the
    # empty-keys heading, and a file named anywhere else in the document would
    # otherwise read as a disclosure it is not part of.
    body = note.read_text(encoding="utf-8", errors="replace")
    heading = "## Seven declared panel sizes cannot be checked"
    if heading not in body:
        raise AssertionError(
            f"ENVIRONMENT.md has no section beginning {heading!r}; the seven "
            f"unverifiable panel sizes are disclosed nowhere a reader will look"
        )
    section = body.split(heading, 1)[1]
    text = section.split("\n## ", 1)[0]

    missing = sorted(name for name in MEANS_ONLY if name not in text)
    assert not missing, (
        f"ENVIRONMENT.md does not name {missing}, whose declared panel size "
        f"nothing in the release can check; the disclosure has to list every "
        f"file it covers or it understates what is unverifiable"
    )

    checkable = sorted(
        name for name, blob in _declaring_files()
        if name not in MEANS_ONLY and _per_item_lengths(blob) and name in text
    )
    assert not checkable, (
        f"ENVIRONMENT.md lists {checkable} as aggregate-only, but they record "
        f"per-item vectors; the note overstates what is unverifiable"
    )


def test_the_exemption_list_is_not_a_dumping_ground():
    present = {name for name, _ in _declaring_files()}
    stale = sorted(set(MEANS_ONLY) - present)
    assert not stale, (
        f"MEANS_ONLY names {stale}, which no longer declare a panel size in the "
        f"release; an exemption that protects nothing hides the next one"
    )

    declaring = len(present)
    if not declaring:
        pytest.skip("[repro] no raw files declare a panel size")
    exempt = len([n for n in MEANS_ONLY if n in present])
    # A ratchet, not a judgement about what fraction is acceptable. Seven of
    # thirteen panel-declaring files are aggregate-only, which is worse than I
    # expected when writing this and is what the release actually is. Pinning
    # the measured count means an eighth cannot be added without editing this
    # number, while a harness that starts recording vectors lowers it.
    assert exempt <= 7, (
        f"{exempt} of {declaring} panel-declaring files now claim a denominator "
        f"nobody can check, up from 7; record the per-item vectors for the new "
        f"one rather than raising this bound"
    )

    for name, reason in MEANS_ONLY.items():
        assert len(reason.split()) >= 5, (
            f"the exemption for {name} reads {reason!r}, which does not say "
            f"what the harness recorded instead"
        )
