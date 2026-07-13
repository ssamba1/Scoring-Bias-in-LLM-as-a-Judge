# Publication Roadmap

## From Here to Published: All Venues, All Steps

---

## Timeline Overview

```
WEEK 1 (NOW)              WEEK 2                WEEK 3                WEEK 4
┌──────────────────┐    ┌──────────────────┐   ┌──────────────────┐  ┌──────────────────┐
│ Kaggle finishes   │    │ arXiv submission  │   │ ISEF application  │  │ Peer review       │
│ Human baseline    │    │ Paper polish      │   │ Conference subm.  │  │ Revisions         │
│ Post-processing   │    │ Response prep     │   │                    │  │ Acceptance        │
└──────────────────┘    └──────────────────┘   └──────────────────┘  └──────────────────┘
```

---

## Step 1: When Kaggle Finishes (Today/Tomorrow)

**Actions:**
1. Download `study1_max_scale.json` from Kaggle Output tab
2. Place in `results_rootcause/study1_max_scale.json`
3. Run: `python3 results_rootcause/postprocess_max_scale.py`
   → Generates: summary table, paired t-tests, LaTeX table
4. Run: `python3 paper/auto_update_paper.py`
   → Populates all tables with real data
5. Collect 5 human raters (30 min per person)
6. Run: `python3 results_rootcause/postprocess_max_scale.py --human`
   → Adds human comparison to paper

---

## Step 2: arXiv Submission (Free, Immediate, 30 min)

**What it gives you:** Timestamped preprint, permanent DOI, citable, establishes priority.

**Process:**
1. Create account at [arxiv.org](https://arxiv.org/submit)
2. Endorsement needed (ask a mentor/professor to endorse you)
3. Upload `paper/arxiv_submission.tar.gz` (already built — 11 files, 11KB)
4. Fill metadata:
   - Title: "Where Does Scoring Bias Come From? A Base vs Instruct Comparison of LLM-as-a-Judge"
   - Authors: Your real names
   - Primary class: cs.CL (Computation and Language)
   - Secondary: cs.AI, cs.LG, stat.ML
   - License: arXiv perpetual non-exclusive
5. Click Submit

**Time:** 30 minutes
**Cost:** $0
**Result:** arxiv.org/abs/XXXX.XXXXX within 24 hours

---

## Step 3: ISEF Application (Deadline Varies, ~2 hrs)

**What it gives you:** Chance at Grand Award ($6,000), recognition, college applications.

**Process:**
1. Check your region's ISEF affiliated fair deadline (typically Oct-Feb)
2. Fill official forms (content in `isef/application_text.md`)
3. Print poster from `isef/poster.html` as 48"×36" trifold
4. Practice 8-10 minute interview using `isef/booth_guide.md`
5. Record 3-minute video from `isef/video_script.md`
6. Submit

**Key dates:** ISEF 2027 finals: May 2027
**Cost:** Travel to fair (varies)

---

## Step 4: Conference Submission

### Option A: NeurIPS High School Projects Track (Best Fit)
**Deadline:** ~June 2027 (check neurips.cc)
**Format:** 4-page paper + poster
**Our advantage:** Real data, novel finding, complete infrastructure, $0 cost
**Acceptance rate:** ~25%

### Option B: ACL Rolling Review (ARR)
**Deadline:** Monthly deadlines
**Format:** 8-page paper
**Our advantage:** Direct comparison to Li et al. (DASFAA) — we answer their gap
**Acceptance rate:** ~25% for Findings

### Option C: EMNLP
**Deadline:** ~May 2027
**Format:** 8-page paper
**Similar work:** OffsetBias (Park et al., EMNLP 2024) — same scale as ours

---

## Step 5: Camera-Ready (After Acceptance)

1. Address reviewer comments (use `paper/reviewer_response.md`)
2. Compile final PDF from `paper/camera_ready.tex`
3. Add DOI from acceptance notification
4. Upload to proceedings

---

## What We Can Do RIGHT NOW (While Kaggle Runs)

| Task | Time | Who |
|------|------|-----|
| Create arXiv account | 5 min | You |
| Get endorsement | 10 min | Ask mentor |
| Collect human ratings | 2 hrs | You + 5 friends |
| Print ISEF poster | 30 min | Print shop |
| Fill ISEF forms | 1 hr | You |

---

## The 3 Remaining Files

When the GPU finishes, three files need to be updated with real data:

1. `results_rootcause/study1_max_scale.json` — Downloaded from Kaggle
2. `data/human_baseline_sheet.md` — Scores from 5 people
3. `paper/camera_ready.tex` — Auto-populated from step 1+2

Everything else (258 files) is ready.
