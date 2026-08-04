# P-V Fatigue Manifold Proprioception

P-V Fatigue Manifold Proprioception is a Python simulation and research package
that tests whether intermittent pressure-volume (P-V) loops can schedule
recalibration when soft-actuator motion is estimated from pressure alone.

Soft pneumatic actuators drift as they fatigue, but constant recalibration adds
time and instrumentation. This project compares P-V-triggered, cycle-count, and
always-on policies on synthetic shared-manifold grippers, with reproducible
studies and checked manuscript outputs.

![P-V recalibration trade-off](data/sim/phaseD/study3_fig4_recal_tradeoff.png)

### Key capabilities

- Simulates fatigue, recovery, leak growth, and shared-manifold cross-talk.
- Evaluates recalibration policies on held-out synthetic actuators.
- Regenerates study data, figures, and the simulation-only manuscript.
- Checks reported numbers and publication files against committed results.

**For:** soft-robotics researchers and students studying pneumatic-actuator
health monitoring, proprioception, and recalibration.

**Start here:** run `python -m scripts.run_study3`, then verify the repository
with the commands in [Reproduce and verify](#reproduce-and-verify).

## Current Positioning

The core novelty has been reframed after literature and patent verification:

- Do **not** claim first use of pressure-volume (P-V) hysteresis for fatigue.
- Mosadegh et al. 2014 and US10639801B2 already establish before/after P-V hysteresis fatigue assessment.
- The defensible v1 claim is a simulation-derived P-V recalibration signal evaluated against always-on and cycle-count policies. The five-stage study is life-stage-resolved, not evidence of cycle-by-cycle trigger timing.
- Shared-manifold cross-talk is retained as a negative secondary result: it is second-order within the tested simulated parameter envelope, not a general statement about all physical manifolds.
- The pose estimator is pressure-only during normal operation; the health signal comes from a separate intermittent volumetric P-V probe.

**Current release:** simulation-only manuscript v1.3, frozen at
[`preprint-v1.3`](https://github.com/500ft/P-V-Fatigue-Manifold-Proprioception/releases/tag/preprint-v1.3).
The PDF passes the repository's number and arXiv pre-flight checks. Public
citation still requires the owner to publish the preregistered Zenodo fallback or
record an arXiv identifier. The registered fallback date was 2026-08-02.

**RoboSoft-v2 development:** the new paper centers the conditional recalibration
decision rather than rediscovering P-V fatigue sensitivity. Start with the
[`novelty/evidence audit`](docs/reviews/novelty-evidence-audit-2026-08-03.md),
[`claim spine`](docs/specs/robosoft-v2/claim-spine.md), and
[`adaptive scope`](docs/specs/robosoft-v2/scope.md). The v1.3 PDF and publication
metadata remain unchanged.

## Repository Contents

- `docs/A01_A04_Literature_Review.md` - annotated literature review and verified citation base.
- `docs/Proposal_A01_A04_Combined.md` - main proposal with research questions, novelty framing, methods, risks, and timeline.
- `docs/Gate0_Coupling_Simulation.md` - **Gate 0 result**: lumped-RC pre-test of the coupling spine (PASS). The mechanism is confirmed and the experiment is re-scoped around its findings.
- `docs/Gate0b_Failure_Mode_Literature.md` - **Gate 0b** (literature-resolved, PASS): silicone PneuNets fail gradually with micro-tear precursors → a P-V health indicator is viable.
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

1. Life-stage-resolved P-V feature trajectories and explicit trigger-policy evaluation, not merely before/after comparison.
2. Quantified trigger timing before accuracy-budget violation, reported honestly whether positive or not.
3. Coupling between fatigue-induced compliance drift, shared-manifold cross-talk, and pressure-only pose-estimation degradation.
4. Recalibration triggered by a P-V health signal.

## Status

- **Manuscript v1.3 complete and tagged.** The checked PDF is
  [`docs/preprint_v1.pdf`](docs/preprint_v1.pdf); the exact release bytes have
  SHA-256 `6a6681fe1a77f7d972048dddc99a0a07b55e5d89dca1a83c11ba5b5cefd0777d`.
- **Simulation result complete.** The study uses 2,000 traces split by actuator
  identity. The frozen v1 paper reports pooled `r = 0.885` and a point-level
  bootstrap interval `[0.835, 0.958]`; v2 will replace that interval with
  actuator-cluster resampling and leave-one-actuator-out sensitivity. The deployed
  threshold has no positive temporal lead, and the manuscript reports that negative
  result directly.
- **Recalibration result complete.** The P-V-triggered policy meets the registered
  error budget with 2 recalibrations per actuator versus 5 for always-on; the
  equally tuned cycle-count baseline fails on held-out actuators.
- **Scope:** all results are synthetic and from one generative model. No physical
  actuator validation is claimed.
- **Publication blocker:** cs.RO endorsement is owner/external. The arXiv runbook
  remains active, but the packet is no longer dependent on the reply: reserve a
  Zenodo DOI now and publish v1.3 there on August 2 if no arXiv ID exists. See
  [`docs/ZENODO_FALLBACK.md`](docs/ZENODO_FALLBACK.md).

## Reproduce and verify

```bash
python -m pytest
python -m scripts.check_manuscript_numbers
python -m scripts.check_pdf_arxiv
python -m scripts.check_publication_fallback
```

Hardware work remains trigger-gated on matched actuator/lab access and a frozen
physical protocol; it is not required for the citable simulation release.

## License

This repository is dual-licensed:

- **Source code** (e.g. `sim/`, `scripts/`, `tests/`) is licensed under the
  **MIT License** — see [`LICENSE`](LICENSE).
- **The manuscript, documentation, and figures** (notably `docs/`) are licensed
  under **Creative Commons Attribution 4.0 International (CC BY 4.0)** — see
  [`LICENSE-docs`](LICENSE-docs).

Copyright (c) 2026 Mergen Ulziibayar.
