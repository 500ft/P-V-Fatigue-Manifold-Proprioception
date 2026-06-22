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
- `docs/Gate0_Coupling_Simulation.md` - **Gate 0 result**: lumped-RC pre-test of the coupling spine (PASS). The mechanism is confirmed and the experiment is re-scoped around its findings.
- `docs/Gate0b_Failure_Mode_Literature.md` - **Gate 0b** (literature-resolved, PASS): silicone PneuNets fail gradually with micro-tear precursors → leading indicator is viable.
- `docs/Gate1_Volume_Estimation_Literature.md` - **Gate 1** (design-resolved): acquire P-V loops by volumetric drive + pressure-oscillation observer; flow integration rejected.
- `docs/Experimental_Protocol.md` - operational test runbook: the gate ladder, study protocols, and the minimum viable paper.
- `scripts/gate0_lumped_rc.py` - the Gate 0 simulation (writes `data/gate0/`).
- `sim/fatigue.py` - **Phase B model**: synthetic Mullins/recovery, irreversible
  compliance drift, acceleration onset, and late leak growth.
- `scripts/phaseB_fatigue_demo.py` - Phase B consistency demo (writes
  `data/sim/phaseB/`), including the independent pressure-decay leak observable.
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

- **Gate 0 (coupling simulation): DONE — PASS.** The fatigue→compliance→cross-talk spine
  is confirmed in a lumped-RC model and is robust across 400 randomized parameter sets
  (100 % monotone). Key finding: the coupling is **dynamic** (DC gain is
  compliance-independent), so the experiment must probe at the actuation band (~1–5 Hz)
  with history-dependent features. See `docs/Gate0_Coupling_Simulation.md`.
- **Gate 0b: DONE — PASS (literature-resolved).** Silicone PneuNets fail *gradually* with
  micro-tear precursors (Libby 2022: FEM agreement 96 %→80 %; Torzini 2024: 0.2–0.4 mm
  hump-base tears before rupture). Leading indicator is viable; target compliance/loop-area
  drift. One spot-check folded into rig bring-up. See `docs/Gate0b_Failure_Mode_Literature.md`.
- **Gate 1: DONE — design-resolved.** Acquire P-V loops by volumetric (syringe/stepper)
  drive; deployable in-loop volume via pressure-oscillation observer (~0.6 % RMS, Joshi &
  Paik 2023); naive flow integration rejected. See `docs/Gate1_Volume_Estimation_Literature.md`.
- **Gate 2 (next, ~1 day, \$0):** audit actual lab equipment (mocap? rig? syringe pump?)
  and replace the \$320 estimate with an audited BOM.
- Then: Week-3 hardware coupling gate, entered with the mechanism, failure mode, and volume
  method all pre-confirmed.
- **Remote simulation Phase A: DONE — PASS.** The SLS plant produces rate-dependent
  P-V loops and reduces to the Gate 0 model.
- **Remote simulation Phase B: DONE — PASS (synthetic consistency only).** The canonical
  actuator injects 16 % no-rest compliance/loop-area drift, a 30 % permanent Mullins
  floor with 24 h recovery time constant, curvature acceleration onset at 70 % life,
  and late leak growth to 20x conductance. Leakage is observed by a separate closed-valve
  pressure-decay probe; it is not observable in imposed-volume P-V loops.
- **Next remote simulation work: Phase C.** Extract P-V features, fit degradation/health
  indicators, separate linear-drift detectability from curvature-onset estimation, and
  run the pre-registered cadence/noise identifiability grid.
- Expand the proposal into submission-ready Intro/Related Work after Gate 2.

## License

This repository is dual-licensed:

- **Source code** (e.g. `sim/`, `scripts/`, `tests/`) is licensed under the
  **MIT License** — see [`LICENSE`](LICENSE).
- **The manuscript, documentation, and figures** (notably `docs/`) are licensed
  under **Creative Commons Attribution 4.0 International (CC BY 4.0)** — see
  [`LICENSE-docs`](LICENSE-docs).

Copyright (c) 2026 Mergen Ulziibayar.
