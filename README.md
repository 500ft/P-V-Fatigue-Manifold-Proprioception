# P-V Fatigue Manifold Proprioception

Research package for the combined soft-robotics proposal:

**P-V hysteresis as a cycle-resolved fatigue leading indicator, and its coupling to pressure-only proprioception in shared-manifold soft pneumatic grippers.**

## Current Positioning

The core novelty has been reframed after literature and patent verification:

- Do **not** claim first use of pressure-volume (P-V) hysteresis for fatigue.
- Mosadegh et al. 2014 and US10639801B2 already establish before/after P-V hysteresis fatigue assessment.
- The defensible claim is the first operational, cycle-resolved P-V loop-shape leading indicator with quantified lead time, plus fatigue-triggered recalibration for shared-manifold pressure-only proprioception.

## Repository Contents

- `docs/A01_A04_Literature_Review.md` - annotated literature review and verified citation base.
- `docs/Proposal_A01_A04_Combined.md` - main proposal with research questions, novelty framing, methods, risks, and timeline.
- `docs/Draft1_A01_A04_Combined.pdf` - earlier draft PDF.
- `docs/paper_drafts.md` - draft paper/proposal text history.
- `docs/report.md` - research topic report.
- `docs/all_timespan_professor_review.md` - review notes across candidate topics.
- `data/outline.yaml` - structured topic outline.
- `data/fields.yaml` - research schema fields.
- `data/results/` - per-topic research JSON outputs.
- `scripts/generate_report.py` - report-generation script.
- `scripts/make_draft1_pdf.py` - draft PDF generation script.
- `references/patents/US10639801B2-low-strain-pneumatic-networks.pdf` - downloaded Google Patents PDF for the nearest patent prior art.

## Key Prior-Art Boundary

US Patent 10,639,801 confirms cycle-lifetime claims for low-strain PneuNets (>10,000, >200,000, and >1,000,000 cycles without failure). The Google Patents text source also states that fatigue was assessed using before/after P-V hysteresis curves at 2 Hz over 10^4, 2 x 10^5, and 10^6 complete-actuation cycles.

That makes the proposal's boundary:

1. Cycle-resolved P-V feature trajectories, not just before/after curves.
2. Quantified positive lead time before failure or visible damage.
3. Coupling between fatigue-induced compliance drift, shared-manifold cross-talk, and pressure-only pose-estimation degradation.
4. Recalibration triggered by a P-V health signal.

## Status

Metadata cleanup completed on 2026-06-18:

- Cleared all previous `[verify]` markers in the literature review.
- Corrected Guo et al. 2021 DOI to `10.1016/j.measurement.2021.110076`.
- Corrected the pneumatic RC-model citation to Stanley et al. 2021, DOI `10.1115/1.4049009`.
- Updated Lindenroth et al. from arXiv-only to the published IEEE/ASME Transactions on Mechatronics version.

## Next Work

- Expand `docs/Proposal_A01_A04_Combined.md` into a submission-ready Introduction and Related Work.
- Write the Week-3 coupling gate protocol and bill of materials.
- Convert the proposal into a polished paper draft after experimental parameters are fixed.
