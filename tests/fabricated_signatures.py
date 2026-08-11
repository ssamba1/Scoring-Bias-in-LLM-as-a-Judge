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
    "22-model landscape": (r"22[- ]model landscape", "the 22-model landscape"),
    "40,500 judgments": (r"40,?500\s+judgments", "40,500 judgments"),
    "31 variants": (r"\b31\s+variants", "across 31 variants"),
    # Placeholder authorship from the retracted submission metadata.
    "placeholder authors": (r"Student A, Student B", "authors: Student A, Student B"),
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
