# Superseded manuscripts — none of these is the paper of record

Every `.tex` file in this directory is an earlier or abandoned manuscript. They are kept
because deleting drafts of a retracted project would remove the record of what was claimed
and when, which is the opposite of what this repository is for.

**The paper of record is `paper/honest/scoring_bias_v2.tex`.** Cite nothing else.

Several of these carry the fabricated 22-model "landscape", the invented per-domain table, and
the hardcoded attention numbers that `DATA_INTEGRITY_AUDIT.md` and `paper/PROVENANCE_AUDIT.md`
document. `camera_ready_paper.tex` and the `paper_rootcause_*`/`study1_*` drafts are of that
era. Their conclusions were overturned twice over: first by the audit, then by the 13-family
GPU run, which reversed the direction of the effect the earliest drafts reported.

The scripts that built and validated those manuscripts are quarantined under
`RETRACTED/legacy/paper_tools/`, so nothing here can be rebuilt by accident from a live
entry point.
