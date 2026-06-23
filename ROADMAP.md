# Roadmap — P-V Fatigue / Manifold Proprioception

_Last updated: 2026-06-23 · Horizon: 8 weeks (through ~2026-08-23)_

## Role in the portfolio

**Research flagship.** This is the project that demonstrates original,
publishable work for graduate admissions, and signals R&D capability for
industry. The bar for "done this summer" is **a public preprint**, not just more
code.

## Where it is now

- **Phase A — DONE/PASS.** Viscoelastic (SLS) pneumatic plant; rate-dependent
  P-V hysteresis validated against the closed-form dissipation; reduces to the
  Gate 0 linear cross-talk model.
- **Phase B — DONE/PASS (synthetic consistency).** Canonical fatigue model:
  Mullins softening + partial recovery (30% permanent floor, 24 h time
  constant), irreversible compliance drift, curvature acceleration onset at 70%
  life, late leak growth to 20x conductance observed via a separate closed-valve
  pressure-decay probe.
- **Phase C — DONE/PASS (synthetic validation).** Causal P-V features, Mullins
  recovery normalization, HI metrics, matched-FA 3sigma/CUSUM detectors, and four
  degradation models across the 144-condition identifiability grid. The matched
  segmented model recovers the quadratic onset ceiling and fails on
  logistic-onset variants (the intended inverse-crime / generalization result).

## Target by end of August

Phases D-F complete **and a preprint on arXiv.** The deliverable that matters
for both grad school and industry is the written, public artifact.

## Milestones

- [ ] **Wk 0 — Freeze the result spine first (before generating data):** pre-register
      the one-paragraph claim and the 3-4 target figures in
      [`docs/result_spine.md`](docs/result_spine.md) so Phases D-F build toward a fixed
      target instead of exploring.
- [ ] **Wks 1-3 — Phase D:** PCC kinematics (pressure -> bend -> tip SE(3)),
      sensor model (noise/quantization/sampling/contact), and the ~2000-trace
      labeled dataset (shared-manifold vs isolated-supply control). Validation:
      noise-free pose recoverable to machine precision; split by **actuator
      identity, not by trace**; traces are *dynamic* (per Gate 0 the cross-talk is in the
      actuation-band dynamics, not the DC map); Phase-D foundation implemented and gated
      (`sim/kinematics.py`, `sim/sensors.py`, `tests/test_kinematics.py`,
      `tests/test_sensors.py`), and the dynamic shared-vs-isolated dataset pipeline now
      implemented (`sim/network.py`, `scripts/phaseD_dataset.py`, `tests/test_network.py`) —
      full 2000-trace build via `python -m scripts.phaseD_dataset`; isolated control shows near-zero
      cross-talk.
- [ ] **Wks 3-4 — Phase E:** ridge / ARX proprioception correctors (lead with these; **ESN is a stretch goal only**). Confirm
      the Gate 0 prediction (static ridge blind to fatigue-induced dynamic
      cross-talk drift; ARX recovers it; add ESN only if ARX plateaus with time to spare — reservoir tuning is reproducibility risk for marginal gain).
      **Implemented + run (2026-06-24):** the over-life drift is dominated by the
      compliance-scale change (topology-independent, ~100x), which motivates Phase F
      recalibration; the dynamic corrector does **not** beat static (cross-talk is
      second-order) — negative result retained, see [`docs/result_spine.md`](docs/result_spine.md).
- [ ] **Wks 4-5 — Phase F:** cross-talk-drift vs P-V-compliance correlation over
      life; P-V-triggered recalibration vs fixed vs always-on.
- [ ] **Wks 6-8 — Paper:** assemble the modeling paper (intro, methods, the
      pre-registered results, honest limitations) and **post to arXiv.**

## Honesty constraint (non-negotiable)

Every result is labeled simulation. The paper claims no experimental validation
from this work; modeling assumptions are stated as choices. The contributions
are the pipeline, the design outputs, and (framed as a prediction) the modeling
result. If lab access appears, fold in the single-actuator micro-tear spot-check
to anchor the synthetic story to reality.

## CAD / FEA capability (where it applies)

The author can do CAD and FEA. For the **sim-only preprint this is off the critical path** —
the deliverable is the modeling result. Where it applies (and pays off if lab access
appears): (a) parametric CAD of the PneuNet actuator + mold to ground the PCC segment
geometry (length, chamber spacing) used by `sim/kinematics.py`; (b) CAD of the Gate-1
volumetric-drive rig (syringe/stepper) and the mocap pose-truth fixture; (c) hyperelastic
FEA of the bending chamber as an independent check on the pressure->curvature law. All
trigger-gated on hardware access; must not delay the paper.

## Portfolio statement

> First-authored a preprint and validated simulation pipeline modeling
> pressure-volume hysteresis as a cycle-resolved fatigue leading indicator for
> soft pneumatic actuators, with ground-truth-recovery validation of every
> estimator.
