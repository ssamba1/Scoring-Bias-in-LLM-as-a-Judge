# Superseded pilot data — the paper of record derives nothing from this directory

This holds the early "root cause" pilot: `t4fam_results.json` (7 small base/instruct pairs,
per-variant means only), `rootcause_results.json` (3 families, 8 items), and the analyses
built on them.

**Nothing in `paper/honest/` reads any of it.** The only live code that touches these files is
`paper/honest/superseded/`, which exists to document what the earlier analysis said and is
fenced off by its own guard (`tests/test_superseded_scripts_stay_in_their_lane.py`).

Two things a reader should know before drawing on anything here:

- **The pilot's conclusion was overturned.** These runs supported "instruction tuning reduces
  format bias". The 13-family GPU run behind the paper of record found the opposite sign. Do
  not cite the direction reported in this directory's outputs.
- **`rootcause_results.json` is degenerate.** `paper/PROVENANCE_AUDIT.md` records that all three
  instruct families report byte-identical bias (0.467 / 0.367 / −0.167) and every base is
  exactly 0.0. `t4fam_results.json` is the more plausible of the two and is still only means
  over 7 families.

Kept because deleting the inputs to a retracted analysis would remove the evidence the audit
rests on. `DATA_INTEGRITY_AUDIT.md` cites files here directly.
