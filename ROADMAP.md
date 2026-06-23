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

- [ ] **Wks 1-3 — Phase D:** PCC kinematics (pressure -> bend -> tip SE(3)),
      sensor model (noise/quantization/sampling/contact), and the ~2000-trace
      labeled dataset (shared-manifold vs isolated-supply control). Validation:
      noise-free pose recoverable exactly; isolated control shows near-zero
      cross-talk.
- [ ] **Wks 3-4 — Phase E:** ridge / ARX / ESN proprioception correctors. Confirm
      the Gate 0 prediction (static ridge blind to fatigue-induced dynamic
      cross-talk drift; ARX/ESN recover it).
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

## Portfolio statement

> First-authored a preprint and validated simulation pipeline modeling
> pressure-volume hysteresis as a cycle-resolved fatigue leading indicator for
> soft pneumatic actuators, with ground-truth-recovery validation of every
> estimator.
