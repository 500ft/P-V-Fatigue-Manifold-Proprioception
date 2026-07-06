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

**Policy update 2026-01-21 (verified 2026-07-06): endorsement is REQUIRED,
not probable.** arXiv's updated policy makes an institutional email
insufficient by itself — automatic endorsement now needs an institutional
email **and** prior authorship on a paper already in the target endorsement
domain. A first-time submitter with no prior cs-domain arXiv paper must get
a **personal endorsement from an established cs-domain arXiv author**.

1. Create the arXiv account with the @nyu.edu address (still required — the
   institutional address remains part of the credibility signal).
2. Begin a submission to **cs.RO** to obtain the **endorsement code** the
   form issues. **Guard: do NOT upload a PDF and do NOT click final submit
   during this step** — it exists only to generate the code; abandon the
   draft after.
3. Send the code with a 3-sentence note (title + "simulation-only
   soft-robotics study" + the `preprint-v1.2` tag URL + attached PDF) to a
   faculty member who has authored papers in the cs endorsement domain — an
   NYU Tandon MAE/ECE robotics professor is the natural ask (a
   fire-science/CUSP contact will not qualify; the endorser must be
   established in **cs**). This is the multi-day item; everything else in
   this runbook fits in an afternoon.

## Phase 1 — Fix the three blockers (repo work, ~1–2 h)

### 1a. Embed every font (B1)

- In `scripts/make_preprint_pdf.py`: register `DejaVuSansMono.ttf` (bundled
  with matplotlib alongside the already-registered DejaVuSans family) and
  replace **every** style that defaults to Helvetica or uses Courier with the
  DejaVu equivalents. The leaks are the styles that never set `fontName`
  (reportlab defaults to Helvetica) and the code-span/`Courier` faces.
- Add `scripts/check_pdf_arxiv.py` (pypdf), stricter than "FontFile exists":
  - walk font resources **recursively, including XObject/Form resources**,
    not just top-level page `/Font` dicts;
  - a font counts as embedded iff its descriptor has `/FontFile`,
    `/FontFile2`, **or** `/FontFile3`;
  - **fail** any Base-14 face (Helvetica/Courier/Times/Symbol/ZapfDingbats)
    that is not embedded; **fail** Type3 (bitmap) fonts outright — arXiv
    requires outline fonts;
  - fail encrypted PDFs, zero pages, and embedded JavaScript.
  Wire it into CI next to `check_manuscript_numbers` so a font regression
  can never ship again.
- Gate: `check_pdf_arxiv.py` passes; re-run the pypdf font dump and confirm
  zero unembedded rows.

### 1b. Name and pin the repository (B2)

- §7 first sentence names the repo explicitly:
  `https://github.com/500ft/P-V-Fatigue-Manifold-Proprioception`, and states
  the pinned version as the annotated tag **`preprint-v1.2`**.
- Referencing the *tag name* (not a commit hash) avoids the chicken-and-egg
  of the final render changing the hash. **Exact order (never tag ahead of
  CI):** edit §7 → re-render → run all checks locally → commit → push branch
  → **wait for CI green on that commit** → `git tag -a preprint-v1.2 -m
  "arXiv v1 source state"` on the green commit → `git push --tags` → open
  the GitHub tag URL and confirm it resolves.
- Gate: the tag exists on GitHub, resolves in a browser, and points at a
  CI-green commit whose PDF is the one uploaded.

### 1c. Condensed metadata abstract (B3)

- Write `docs/arxiv_abstract.txt`, **≤ 1,920 characters and ASCII-only** —
  arXiv metadata fields do not support Unicode, and copied Greek glyphs and
  long dashes are the classic silent failures. Write `tau*` as plain ASCII
  (preferred over `$\tau^*$` to reduce form friction), `r = 0.885`,
  hyphens instead of en/em dashes, no markdown. The PDF keeps the full
  Unicode abstract; this file is only for the metadata field.
- Content priorities for the cut (keep → drop): the four findings with their
  headline numbers (r = 0.885 CI, ~0% dynamic-corrector gain, 60% fewer
  recalibrations + clock-baseline failure, negative lead at deployed tau*
  with the frontier clause) and the two scope caveats (sim-only,
  single-generator) → drop the mechanism walk-through and pipeline
  inventory, which §1/§3 carry.
- Gate (enforce all four in `check_manuscript_numbers`, which reads this
  file too):
  `t = open('docs/arxiv_abstract.txt').read()` →
  `len(t) <= 1920` · `t.isascii()` · no `**`/backticks/markdown · every
  quoted number matches the study JSONs.

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
- **License (DECIDED for v1.2):** select **"arXiv.org perpetual,
  non-exclusive license 1.0"**. Rationale: it grants arXiv distribution
  rights while limiting third-party downstream reuse — the least surprising
  choice if RoboSoft/IEEE or another publisher matters later. The license
  choice is **irrevocable per version**, but different versions may carry
  different licenses, so CC-BY remains available for a future v2 if a
  funder/journal ever requires it. Do NOT add any copyright or license
  statement to the PDF front page.

## Phase 3 — Submit (owner, ~30 min once endorsed)

1. Weekday, **before 14:00 ET**, so the announcement lands the next business
   day (submissions after cutoff roll forward). *As of this runbook's date
   (Saturday 2026-07-04): the earliest clean window is Monday 2026-07-06
   before 14:00 ET — do not submit on the weekend if next-business-day
   handling matters.*
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

- [x] `python -m pytest` fully green at the described commit (in CI).
- [x] `python -m scripts.check_manuscript_numbers` green (in CI, now incl.
      the four abstract gates).
- [x] Figures 1–5 embedded and legible.
- [x] Author affiliation + email current; solo unfunded work, no
      acknowledgments owed.
- [x] **B1 fonts — CLEARED 2026-07-06**: all five faces embedded
      (DejaVuSans family + DejaVuSansMono); `check_pdf_arxiv.py` gates it
      in CI. Three Helvetica/Courier sources found and killed (code-span
      Courier, canvas initialFontName, Table cell-style FONTNAME).
- [x] **B2 repo pin — CLEARED 2026-07-06**: §7 names the repo and pins tag
      `preprint-v1.2`.
- [x] **B3 abstract — CLEARED 2026-07-06**: `docs/arxiv_abstract.txt` at
      1,898 chars, ASCII, markdown-free, numbers JSON-asserted.

**Remaining before upload: Phase 0 (endorsement — owner) and the tag push
after CI green. Then Phase 3.**
