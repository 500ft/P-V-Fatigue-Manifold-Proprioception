# RoboSoft v2 Manuscript Outline

_Outline only. Result placeholders must be filled from committed v2 outputs after the
claim spine is frozen and the corresponding checks pass._

## Preferred title

**Stress-Testing P-V Health-Triggered Recalibration for Fatigue-Driven Drift in
Pneumatic Soft-Actuator Proprioception: A Simulation Study**

## One-sentence novelty statement

> Prior work establishes P-V fatigue diagnostics and pressure-based soft-robot
> proprioception; this study tests when a P-V-loop-derived actuator-state signal improves
> recalibration scheduling over matched non-P-V baselines, and maps the degradation and
> probe conditions under which that advantage fails.

## Abstract scaffold

1. **Known problem:** fatigue changes pneumatic actuator mechanics and invalidates a
   pressure-to-pose calibration.
2. **Prior-art boundary:** P-V fatigue sensitivity and pressure-only proprioception are
   established; the unresolved question is conditional recalibration policy value.
3. **Method:** preregistered causal intervention matrix, family-held-out degradation
   transfer, actuator-cluster inference, matched policy baselines, probe robustness, and
   task-tolerance sweep.
4. **Results:** insert only committed v2 effect sizes, uncertainty, failure regions, and
   policy frontier. Preserve negative results.
5. **Scope:** simulation-only unless the physical-pilot gate fires; no failure-prediction
   or universal-diagnostic claim.

## 1. Introduction

- State the deployment problem as calibration drift, not discovery of P-V fatigue.
- State the exact prior-art boundary in the first page.
- Explain why a state-triggered policy may transfer better than an absolute cycle clock.
- State the pressure-only estimator versus volumetric health-probe distinction.
- Contributions:
  1. causal specificity/failure map;
  2. degradation-family-held-out policy evaluation;
  3. matched error-versus-calibration-cost comparison;
  4. probe operating envelope;
  5. retained shared-manifold negative boundary result.

## 2. Related work

Use a compact comparison table with columns:

| Work category | P-V fatigue evidence | Pose estimation | State-triggered recalibration | Family transfer | Hardware |
|---|---|---|---|---|---|
| Before/after P-V fatigue studies | yes | no | no | no | yes |
| Pressure-only proprioception | no/secondary | yes | limited | varies | often yes |
| Adaptive drift correction | not fatigue-specific | yes | often always-on | varies | varies |
| This study | simulated P-V probe | yes | yes | required in v2 | only if pilot gate fires |

Do not claim the table proves global novelty; it documents the verified boundary.

## 3. Methods

### 3.1 System modes

- Normal pressure-only pose estimation.
- Intermittent volumetric P-V health probe.
- Triggered estimator recalibration.

### 3.2 Plant, kinematics, and network

Retain validated v1 methods compactly. Shared-manifold modeling is supporting context,
not the paper's main novelty.

### 3.3 Causal intervention matrix

Implement and state each frozen row from `claim-spine.md`. Explain which rows challenge
false positives, false negatives, nuisance recovery, and combined degradation.

### 3.4 Domain-shift design

- Split by actuator identity.
- Hold out an entire degradation family.
- Lock policy selection before evaluating the held-out family.

### 3.5 Baselines and selection fairness

All policies use the same training split and budget/cost rule. No test-set tuning.

### 3.6 Outcomes and statistics

- Tolerance-normalized pose error.
- Recalibrations per actuator.
- Budget-violation rate.
- Clustered association interval and leave-one-actuator-out sensitivity.
- Lead distribution with grid uncertainty.
- Intervention false-positive/false-negative rates.

## 4. Results

Suggested order:

1. Structural validation gates.
2. Retained negative manifold/corrector result.
3. Causal intervention and failure map.
4. Family-held-out transfer.
5. Matched policy Pareto frontier.
6. Probe robustness envelope.
7. Task-tolerance sensitivity.
8. Physical pilot, only if its evidence gate fires.

## 5. Discussion

- Explain why shared-manifold cross-talk was secondary in the tested model.
- Separate correlation, temporal lead, policy utility, and physical prediction.
- State which mechanisms the P-V signal misses or falsely flags.
- Discuss the operational cost of the probe itself.
- Treat hardware disagreement as a model-revision input.

## 6. Conclusion

Conclude with a conditional statement: where the state signal improved the policy,
where it failed, and what remains unmeasured. Do not end with a universal health-
monitoring claim.

## Figure plan

1. **System-mode diagram:** pressure-only estimation → intermittent P-V probe →
   conditional recalibration.
2. **Causal intervention matrix:** expected and observed P-V/pose channels.
3. **Family-held-out transfer:** device-cluster trajectories and uncertainty.
4. **Policy Pareto frontier:** task-normalized error versus recalibrations.
5. **Probe operating envelope:** robustness heatmap with explicit failure regions.
6. **Optional physical overlay:** measured versus simulated direction with uncertainty.

## Wording conversions

| Avoid | Use until stronger evidence exists |
|---|---|
| `validated health indicator` | `candidate P-V-derived health signal` |
| `cycle-resolved` | `life-stage-resolved` |
| `generalizes to unseen actuators` | `transfers to held-out parameter draws` |
| `measured P-V state` for simulation | `simulated observable P-V probe` |
| `cross-talk is generally second-order` | `cross-talk is second-order in the tested simulated envelope` |
| `predicts failure` | `schedules recalibration within the tested model` |
