# arXiv Submission Checklist — preprint v1

**Decision: GO for arXiv-first posting, taken 2026-07-02** (delegated portfolio
review; rationale recorded in the manuscript status block and
`Progress/P-V-Fatigue-Manifold-Proprioception/PLAN.md`). Peer-review submission
(RoboSoft) is a separate decision at the next deadline cycle.

## What is being posted

- `docs/preprint_v1.pdf` — rendered manuscript (reportlab toolchain,
  `scripts/make_preprint_pdf.py`; regenerate after ANY edit to
  `docs/preprint_v1.md`).
- Category: **cs.RO** (primary), cross-list **eess.SY**.
- License: arXiv default (perpetual non-exclusive) is fine; do NOT select CC-BY
  unless a journal's policy later requires it.

## Pre-upload checks (all must hold)

- [ ] `python -m pytest` green (129 tests) at the commit being described.
- [ ] Numbers in the abstract match `data/sim/phaseD/study3_results.json` /
      `study4_results.json` (r = 0.885, CI [0.835, 0.958]; 2 vs 5
      recalibrations; 6.3% default coupling, 10% at ≈1.7× softer supply).
- [ ] Figures 1–5 embedded and legible at print size.
- [ ] Author affiliation + email current; no acknowledgments owed (this is
      solo, unfunded work — if any PI/lab input was used, acknowledge or
      clear it first).
- [ ] Repo URL in §7 Reproducibility points at the public GitHub and the
      commit hash is pinned.

## Upload steps (owner)

1. arXiv account with an @nyu.edu email (institutional address usually avoids
   the endorsement gate for cs.RO; if endorsement is requested, any published
   NYU robotics contact can endorse).
2. New submission → cs.RO → upload the PDF (arXiv accepts PDF-only when not
   TeX-derived; this PDF is reportlab-generated, which is acceptable).
3. Abstract: paste from the manuscript (plain-text the math symbols).
4. After the announcement email: record the arXiv ID + version in this file,
   the README, and the Progress repo.

## After posting

- [ ] Add the arXiv badge/ID to `README.md`.
- [ ] Cite-as block (BibTeX) in `README.md`.
- [ ] Mark the summer deliverable DONE in `ROADMAP.md` and the Progress repo.
- [ ] Open the RoboSoft-deadline decision as a calendar item.
