"""The vocabulary of the retraction, in one place.

Several guards need to name the fabricated material in order to look for it, and
a guard that names it trips the sweep that looks for it. That happened twice
while these tests were being written: first the retraction notice added to the
interactive index, then the submission test's own list of things the archive
must not contain.

Keeping the strings here means exactly one file needs an exemption from the
sweep, rather than one per guard that mentions them. Anything importing from
this module carries no literals of its own.

Every entry traces to `DATA_INTEGRITY_AUDIT.md`, which established that the
named models do not exist and the named values were never measured.
"""

# label -> (regex, a string it must match)
#
# The sample is not decoration: it is what proves the pattern still works. A
# regex broken by a later edit would otherwise leave every sweep green.
SIGNATURES = {
    # Models presented as evaluated that do not exist.
    "DeepSeek-V4": (r"DeepSeek-V4", "DeepSeek-V4-Flash"),
    "GLM-4.7": (r"GLM-4\.7", "Zhipu GLM-4.7 & 9B"),
    "Qwen3-*": (r"\bQwen3-\d", 'name:"Qwen3-14B"'),
    "Llama-4*": (r"\bLlama-4[\-\.]", "Llama-4-Scout"),
    # The fabricated per-domain bias table, identified by its values.
    "domain table 3-family": (r"1\.52\s*&\s*0\.98", r"Science & 1.52 & 0.98 \\"),
    "domain table 22-model": (r"0\.52\s*&\s*0\.65", r"Science & 0.52 & 0.65 & 0.38 \\"),
    # Scale claims the audit found unsupported by any run log.
    #
    # These were written as the exact phrasing of the artefact that prompted
    # each one, and on 2026-08-14 every one was probed against plausible
    # restatements of the same fabricated fact. Most let a restatement through:
    # "40,500 total judgments", "22-Model Landscape", "31 prompt variants",
    # "over 54,000 judgments". The 2026-08-11 note below had already recorded
    # this exact failure for one pattern -- a capital letter and an intervening
    # word -- and the fix was applied only to that one.
    #
    # The number is the tell, not the sentence around it. Each now allows an
    # optional qualifier before the noun, ignores case, and accepts the comma,
    # the plus sign and the British spelling. The noun is still required, so a
    # legitimate "22" or "15" in prose does not trip the sweep.
    "22-model landscape": (
        r"(?i)\b(?:22[-\s]model\s+landscape|landscape\s+of\s+22\s+models)",
        "the 22-model landscape",
    ),
    # Spelled out. The honest panel is thirteen families, so "fifteen ...
    # families" is not a phrasing this project can legitimately reach.
    "fifteen families": (
        r"(?i)\bfifteen\s+(?:\w+\s+){0,2}families",
        "fifteen model families",
    ),
    "40,500 judgments": (
        r"(?i)\b40,?500\+?\s+(?:\w+\s+){0,2}judg[e]?ments",
        "40,500 total judgments",
    ),
    "31 variants": (
        r"(?i)\b31\s+(?:\w+\s+){0,2}variants",
        "across 31 variants",
    ),
    # The same inflated counts as they appeared in the graphical abstract, which
    # sat in the live tree until 2026-08-11. "31 variants" above did not match
    # "31 Model Variants": a word in between and a capital letter were enough.
    # Written case-insensitively and tolerant of the intervening word, because
    # the wording varies between artefacts while the number is the tell.
    "31 model variants": (r"(?i)\b31\s+model\s+variants", "Across 31 Model Variants"),
    "15 model families": (
        r"(?i)\b15\s+(?:\w+\s+){0,2}families",
        "15 model families \xb7 50 items",
    ),
    "22 instruct models": (
        r"(?i)\b22\s+(?:instruct|instruction[-\s]tuned)\s+models",
        "9 base-instruct pairs \xb7 22 instruct models",
    ),
    "54,000 judgments": (
        r"(?i)\b54,?000\+?\s+(?:\w+\s+){0,2}judg[e]?ments",
        "54,000+ total judgments",
    ),
    # Placeholder authorship from the retracted submission metadata.
    "placeholder authors": (
        r"(?i)Student A(?:,| and)\s+Student B",
        "authors: Student A, Student B",
    ),
    # A second placeholder byline, found in paper/preregistration.md on
    # 2026-08-13 and quarantined with it. The pattern above is a literal, so it
    # matched one spelling of "we have not filled in the authors yet" and not
    # the other; an unattributed preregistration is the thing to catch, not a
    # particular pair of stand-in names.
    "placeholder byline": (r"(?i)\bAuthor Name\b", "Author Name, Author Name"),
}

PATTERNS = {label: pattern for label, (pattern, _) in SIGNATURES.items()}
SAMPLES = {label: sample for label, (_, sample) in SIGNATURES.items()}

# Exempt from the live-tree sweep, by exact path. Naming this material is the
# purpose of each of these; a pattern-based exemption would let a new file
# inherit the licence quietly.
SWEEP_EXEMPT = {
    "DATA_INTEGRITY_AUDIT.md",
    "paper/PROVENANCE_AUDIT.md",
    "RETRACTED/README.md",
    "tests/fabricated_signatures.py",
    "mutation_check.py",
}
