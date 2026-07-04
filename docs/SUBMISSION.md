# arXiv Submission Runbook — preprint v1.2

**Decision: GO for arXiv-first posting, taken 2026-07-02** (delegated portfolio
review; rationale recorded in the manuscript status block and
`Progress/P-V-Fatigue-Manifold-Proprioception/PLAN.md`). Peer-review submission
(RoboSoft) is a separate decision (trigger: re-check the 2027 CFP early August).

**2026-07-04 pre-flight audit found three real blockers** — the paper is
manuscript-ready but not yet *mechanically* submittable. They are Phase 1
below. Everything was verified against the actual v1.2 PDF and text, not
assumed.

| # | Blocker (verified) | Why it blocks |
|---|---|---|
| B1 | **Helvetica + Courier are NOT embedded** in `preprint_v1.pdf` (DejaVu family is; the reportlab standard-14 base fonts are not) | Unembedded fonts are a standard arXiv auto-hold/rejection reason for PDF-only submissions |
| B2 | **§7 never names the repository** ("in the repository", no URL) and pins no version | The reproducibility claim is unverifiable by a reader; also a pre-upload checklist item that was silently unmet |
| B3 | **Abstract is 3,389 chars; arXiv's metadata field caps at 1,920** | The submission form will reject or truncate it |

---

## Phase 0 — Endorsement (owner; START FIRST, longest lead time)

1. Create the arXiv account with the @nyu.edu address.
2. Begin a submission to **cs.RO** immediately — not to finish it, but because
   the form tells you on the spot whether you need an endorsement. First-time
   submitters usually do; institutional email does not waive it.
3. If endorsement is required: the form issues an endorsement code. Send it
   with a 3-sentence note (title + "simulation-only soft-robotics study" +
   repo link) to a faculty member who has published in cs.RO recently — an
   NYU Tandon MAE robotics professor is the natural ask. This is the
   multi-day item; everything else in this runbook fits in an afternoon.

## Phase 1 — Fix the three blockers (repo work, ~1–2 h)

### 1a. Embed every font (B1)

- In `scripts/make_preprint_pdf.py`: register `DejaVuSansMono.ttf` (bundled
  with matplotlib alongside the already-registered DejaVuSans family) and
  replace **every** style that defaults to Helvetica or uses Courier with the
  DejaVu equivalents. The leaks are the styles that never set `fontName`
  (reportlab defaults to Helvetica) and the code-span/`Courier` faces.
- Add `scripts/check_pdf_arxiv.py`: opens the rendered PDF with pypdf and
  **fails if any font lacks an embedded FontFile**, if the PDF is encrypted,
  or if the page count is 0. Wire it into CI next to
  `check_manuscript_numbers` so a font regression can never ship again.
- Gate: `check_pdf_arxiv.py` passes; re-run the pypdf font dump and confirm
  zero `embedded=False` rows.

### 1b. Name and pin the repository (B2)

- §7 first sentence names the repo explicitly:
  `https://github.com/500ft/P-V-Fatigue-Manifold-Proprioception`, and states
  the pinned version as the annotated tag **`preprint-v1.2`**.
- Referencing the *tag name* (not a commit hash) avoids the chicken-and-egg
  of the final render changing the hash: edit §7 → re-render → commit → then
  `git tag -a preprint-v1.2 -m "arXiv v1 source state" && git push --tags`.
- Gate: the tag exists on GitHub and points at the commit whose PDF is
  uploaded.

### 1c. Condensed metadata abstract (B3)

- Write `docs/arxiv_abstract.txt`, **≤ 1,920 characters**, plain text
  (strip markdown bold; Greek letters may stay as Unicode or become inline
  TeX `$\tau$` — arXiv accepts both). The PDF keeps the full abstract; this
  file is only for the metadata field.
- Content priorities for the cut (keep → drop): the four findings with their
  headline numbers (r = 0.885 CI, ~0% dynamic-corrector gain, 60% fewer
  recalibrations + clock-baseline failure, negative lead at deployed τ\* with
  the frontier clause) and the two scope caveats (sim-only, single-generator)
  → drop the mechanism walk-through and pipeline inventory, which §1/§3 carry.
- Gate: `python -c "print(len(open('docs/arxiv_abstract.txt').read()))"`
  ≤ 1920, and every number in it passes `check_manuscript_numbers` (extend
  the script to read this file too).

### 1d. Wrap Phase 1

- Re-render; `pytest` + `check_manuscript_numbers` + `check_pdf_arxiv` + CI
  green; commit; tag `preprint-v1.2`; push with tags.

## Phase 2 — Metadata pack (so the form is a paste job)

Prepare `docs/arxiv_metadata.md` with the exact strings:

- **Title:** as the manuscript (unchanged).
- **Authors:** Mergen Ulziibayar (NYU Tandon, Dept. of Mechanical & Aerospace
  Engineering).
- **Abstract:** contents of `docs/arxiv_abstract.txt`.
- **Primary category:** cs.RO. **Cross-list:** eess.SY.
- **Comments field:** "11 pages, 5 figures. Simulation-only study; code and
  frozen results at https://github.com/500ft/P-V-Fatigue-Manifold-Proprioception
  (tag preprint-v1.2)".
- **License:** arXiv perpetual non-exclusive (v1.0). Do NOT pick CC-BY unless
  a journal later requires it.

## Phase 3 — Submit (owner, ~30 min once endorsed)

1. Weekday, **before 14:00 ET**, so the announcement lands the next business
   day (submissions after cutoff roll forward).
2. New submission → PDF-only upload (reportlab output is not TeX-derived, so
   PDF-only is allowed; if the form asks, state the PDF was not produced by
   TeX). Paste the metadata pack. Preview — check the abstract renders and
   the fonts display (the preview uses your uploaded bytes).
3. Submit. **A moderation hold of several days is normal for first-time
   submitters** — do not resubmit or email within the first week.

## Phase 4 — After the announcement email

- [ ] Record the arXiv ID + version in this file.
- [ ] README: arXiv badge + cite-as BibTeX (`@misc{..., eprint={ID},
      archivePrefix={arXiv}, primaryClass={cs.RO}}`).
- [ ] Mark the summer deliverable DONE in `ROADMAP.md` and the Progress repo
      (README one-liner + PLAN step 1).
- [ ] RoboSoft trigger stands: re-check the 2027 CFP early August.

## Standing pre-upload checks (unchanged, all currently green except B1–B3)

- [x] `python -m pytest` fully green at the described commit (137, in CI).
- [x] `python -m scripts.check_manuscript_numbers` green (in CI).
- [x] Figures 1–5 embedded and legible.
- [x] Author affiliation + email current; solo unfunded work, no
      acknowledgments owed.
- [ ] B1 fonts · B2 repo pin · B3 abstract — Phase 1 above.
