# Phase D–F Result Spine (pre-registration) — freeze before generating data

_Frozen 2026-06-23. Edit only with a dated note explaining why. The point of this file is
that Phases D–F build toward a fixed target instead of exploring; the result JSON is frozen
before any conclusions are written._

## The one-paragraph claim (the paper lives or dies on this)

> In a shared-manifold soft pneumatic gripper, fatigue-induced compliance drift manifests as
> a *dynamic* (actuation-band) pressure cross-talk that a static pressure→pose calibrator
> cannot track, degrading pressure-only proprioception over life. A P-V-health-triggered
> recalibration recovers pose accuracy at a small fraction of the recalibration count of
> always-on recalibration. **All results are simulation.**

## Target figures (only these; everything else is supporting)

1. **Curvature drift vs life.** Tip-pose error of a *frozen* static-ridge calibrator vs
   normalized life, shared vs isolated supply. Prediction: error grows with life under
   shared supply, ~flat under isolated. *(Phase E)*
2. **Static-blind / dynamic-recover.** Pose RMSE: static ridge vs ARX on held-out actuators
   and later life stages. Prediction: ARX < ridge once dynamic cross-talk appears; both
   comparable when it is absent. *(Phase E)*
3. **P-V leading indicator.** Compliance / loop-area drift (the P-V health index) leads pose
   degradation by a positive margin. *(Phase F)*
4. **Recalibration trade-off.** Pose error **and** recalibration count on the same axes for
   fixed vs P-V-triggered vs always-on. Prediction: triggered ≈ always-on accuracy at far
   fewer recalibrations. *(Phase F)*

## Pre-registered acceptance / honesty rules

- Split by **actuator identity**, never by trace.
- "Generalization to unseen actuators" tests overfitting to *one generator*, not real
  device variation — **state this in the abstract.**
- ARX beating ridge is a **hypothesis**, not an acceptance criterion; negative results are
  retained.
- ESN is a stretch goal only — do not add reservoir tuning unless ARX plateaus with time to
  spare.
- Per Gate 0 the cross-talk is **dynamic** (DC gain is compliance-independent): traces must
  excite the actuation band (~1–5 Hz) and correctors must see history; a static pose dataset
  cannot show the effect.
- Freeze the result JSON before writing conclusions.

## Status

- Phase D foundation implemented and gated: `sim/kinematics.py` (fatigue-coupled PCC,
  analytically invertible), `sim/sensors.py` (seeded noise/quantization/sampling/contact),
  with `tests/test_kinematics.py` (machine-precision forward↔inverse + curvature-drift) and
  `tests/test_sensors.py` (determinism, noise-free passthrough, quantization, contact).
- Phase D dataset pipeline implemented and gated: `sim/network.py` (shared-manifold vs
  isolated-supply time-domain dynamics with per-chamber fatigue degradation) +
  `scripts/phaseD_dataset.py` (the 2,000-trace generator, split by actuator identity, NPZ +
  manifest + SHA-256), with `tests/test_network.py` (isolated coupling ≈ 0; shared
  measurable; Gate-0 DC-independent / actuation-band drift; single-chamber reduction). Smoke
  run confirms shared vs isolated changes the focal pose (~4% median curvature shift).
- Phase E correctors implemented and run: `pipeline/correctors.py` (static ridge vs dynamic
  lagged-input), `scripts/run_study2.py`, `tests/test_correctors.py`. See Findings below.

## Findings (Phase E — 2026-06-24, retained verbatim per the honesty rules)

Pressure-only proprioception, features = [shared-manifold pressure, all chamber commands],
per-actuator calibration, held-out actuators.

- **Experiment A (drift) — confirmed, but reframed.** A young-calibrated static estimator's
  curvature RMSE grows ~100x over life (0.004 → 0.46 at 0.9 life), and the shared vs isolated
  curves are nearly identical. The dominant pressure-only proprioception error is therefore
  the **fatigue compliance-scale drift**, which is *topology-independent*. This is the strong,
  clean result, and it is exactly what motivates Phase F (P-V-health-triggered recalibration).
- **Experiment B (static-blind / dynamic-recover) — NOT supported (negative result, retained).**
  The dynamic corrector yields ~0% improvement over the static ridge under *either* topology,
  even with neighbor commands observable. The shared-manifold cross-talk is real in the network
  dynamics (`tests/test_network.py`) but is a second-order (~4%) perturbation that does not
  materially degrade pose estimation at these physically reasonable network parameters; an
  ARX/dynamic corrector is not needed. Whether a softer supply (larger cross-talk) changes this
  is a parameter-sensitivity question left as future work — deliberately NOT tuned here, to
  avoid fishing for the hypothesized result.

**Revised contribution.** The defensible headline is the **compliance-drift leading indicator +
P-V-triggered recalibration** (Phase F), not dynamic cross-talk recovery. Cross-talk is reported
honestly as present-but-second-order.
