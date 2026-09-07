# RoboSoft v2 Claim Spine

_Frozen 2026-08-03 before v2 result generation. Amend only with a dated rationale.
This spine does not modify the frozen v1.3 result spine or publication record._

## Working title

**Stress-Testing P-V Health-Triggered Recalibration for Fatigue-Driven Drift in
Pneumatic Soft-Actuator Proprioception: A Simulation Study**

If a physical campaign clears its evidence gate, remove `A Simulation Study` only after
the manuscript includes measured methods, uncertainty, results, and limitations.

## Novelty boundary

Prior work already establishes P-V fatigue diagnostics, hysteresis-derived health
features, pressure-based soft-robot proprioception, pneumatic coupling, and adaptive
recalibration. V2 does not claim any of those ideas individually.

The research question is:

> Under which degradation mechanisms and probe conditions does a P-V-loop-derived
> actuator-state signal schedule pressure-to-pose recalibration more effectively than
> a train-matched cycle-count clock, and under which conditions does it fail?

The intended contribution is a preregistered **conditional evaluation and failure
map**: causal intervention controls, degradation-family transfer, matched policy
baselines, measurement robustness, and an explicit accuracy-versus-calibration-cost
frontier. Shared-manifold cross-talk is a retained negative secondary result.

## Hypotheses, not acceptance criteria

- **H1 — State beats clock under transfer.** A P-V-derived policy will produce a
  better held-out error/recalibration frontier than an absolute cycle-count policy when
  degradation changes the actuator state represented by the P-V probe.
- **H2 — The signal is conditional, not universal.** Mechanisms that decouple P-V
  loop shape from pose drift will create explicit false-positive or false-negative
  regions.
- **H3 — Cross-talk remains secondary in the tested regime.** Supply-network coupling
  will remain smaller than compliance-driven pose drift over the existing registered
  parameter envelope.

Any hypothesis may fail. A failed hypothesis remains in the paper and narrows the claim.

## Independent units and splits

- Primary independent unit: simulated actuator identity.
- Domain-shift unit: degradation-law family.
- No trace-level random split.
- Training selects thresholds and policy hyperparameters.
- Held-out actuator identities and at least one entire degradation family remain unseen
  until final evaluation.
- Life stages and repeated traces are dependent observations, not additional devices.

## Preregistered intervention matrix

| Intervention | Expected P-V response | Expected pose response | Diagnostic role |
|---|---|---|---|
| Compliance/stiffness drift | change | change | coupled positive control |
| Viscoelastic-loss drift | strong loop-area change | possibly weak pose change | false-positive challenge |
| Kinematic-gain or pose-sensor bias | little P-V change | change | false-negative challenge |
| Leak/conductance growth | pressure-decay and possible loop change | condition-dependent | competing-observable challenge |
| Mullins recovery/rest history | reversible loop change | reversible/limited drift | nuisance/recovery challenge |
| Combined mechanism | mixed | mixed | deployment-like stress test |

If the implemented model cannot produce the intended decoupling, that row is reported as
an unresolved design limitation rather than silently removed.

## Baselines

- Never recalibrate.
- Always recalibrate.
- Absolute cycle-count schedule.
- P-V loop-area fractional threshold.
- Static compliance or P-V slope.
- Pressure-decay leak indicator.
- Change-point/CUSUM policy using a matched training and false-alarm rule.

All adaptive policies must be tuned on training data under the same error budget or
calibration-cost constraint. No baseline receives test-set tuning.

## Primary endpoints

1. Held-out pose error normalized by task tolerance.
2. Recalibrations per actuator.
3. Error-versus-recalibration Pareto dominance, not a single cherry-picked threshold.
4. Budget-violation rate across held-out actuator identities and degradation families.
5. Trigger lead distribution with observation-grid uncertainty stated.
6. False-positive and false-negative rates in the decoupled intervention matrix.

## Statistical rules

- Report the pooled association as descriptive.
- Resample complete actuator trajectories for the primary correlation interval.
- Report leave-one-actuator-out point estimates.
- Report the number of independent actuator identities beside every interval.
- Do not treat denser life stages as increased independent sample size.
- If only six held-out identities remain, emphasize effect sizes and sensitivity rather
  than significance language.

## Task-tolerance rule

The v1 budget of 0.159 mm is a generator-derived operating point, not a universal
robotics requirement. V2 reports a preregistered tolerance sweep and normalizes pose
error by actuator length or task tolerance. Any single selected operating point must be
justified from a stated task rather than from favorable test behavior.

## Probe-robustness axes

- Pressure and volume noise.
- Quantization.
- Sampling/decimation.
- Probe amplitude and frequency.
- Recovery/rest interval.

For every point, report error, recalibration count, budget status, and failure mode.

## Claim language gates

| Evidence state | Allowed wording |
|---|---|
| Simulation only | `candidate health signal`, `simulation-derived state signal`, `within the tested generator` |
| Multi-family simulation passes | `robust across the tested degradation families` |
| Small hardware pilot passes | `directionally consistent in a three-actuator pilot` |
| Larger physical campaign | `experimentally supported` only with uncertainty and device-level replication |

Never use `validated fatigue diagnostic`, `predicts failure`, `cycle-resolved`, or
`generalizes to actuators` without the corresponding evidence.

## Falsification and downgrade rules

- If actuator-cluster uncertainty includes weak or reversed association, lead with the
  policy frontier and downgrade correlation claims.
- If the P-V policy does not beat the cycle clock on a held-out degradation family,
  report the failed family and restrict the method's domain.
- If another observable dominates loop area, retitle around state-triggered
  recalibration rather than P-V loop area.
- If task-tolerance sweeps show no operationally meaningful regime, frame the result as
  a methodological negative finding.
- If hardware disagrees with simulation, revise the generator; do not average the
  disagreement away.

## Frozen non-results

No v2 numerical result, pass verdict, or hardware claim is frozen here. The spine
freezes questions, comparisons, endpoints, and downgrade rules before those results are
generated.
