# Results

This document summarizes the committed simulation results. The manuscript in
[`preprint_v1.md`](preprint_v1.md) contains the complete methods, related work,
interpretation, and limitations. All result claims remain limited to the
repository's synthetic generator.

## Study 1: health-indicator validation

The study compares candidate health indicators against known synthetic fatigue
state, recovery behavior, onset changes, measurement noise, and held-out
actuator-life trajectories. Its figures are stored under `data/sim/study1/`.

## Study 2: pressure-only proprioception drift

The Phase D cohort shows increasing pose-estimation error when a young
calibration is held fixed as the simulated actuator ages. The study compares
static and dynamic correctors under shared and isolated supply topologies.

## Study 3: recalibration policy

| Result | Committed output |
| --- | --- |
| Dataset | 2,000 synthetic traces split by actuator identity |
| P-V association | Pooled `r = 0.885`; point-level bootstrap interval `[0.835, 0.958]` |
| P-V policy | 2 recalibrations per actuator versus 5 for always-on |
| Cycle-count baseline | Misses the registered held-out error budget at its train-selected period |
| Deployed threshold lead | No positive temporal lead at `tau = 0.05` |

The current point-level interval does not account for actuator clustering. The
planned follow-up uses actuator-cluster resampling and leave-one-actuator-out
sensitivity.

![P-V loop-area growth and pose degradation](../data/sim/phaseD/study3_fig3_leading_indicator.png)

![Recalibration policy trade-off](../data/sim/phaseD/study3_fig4_recal_tradeoff.png)

## Study 4: shared-manifold sensitivity

Shared-manifold cross-talk is second-order within the tested network envelope
and increases as the simulated supply becomes softer. The result is conditional
on the lumped pneumatic-network parameters and is not a measurement of a
physical gripper.

![Shared-manifold sensitivity](../data/sim/phaseD/study4_fig_crosstalk_sensitivity.png)

## Result sources

- Study JSON and figures: `data/sim/`
- Frozen claim ledger: [`result_spine.md`](result_spine.md)
- Figure-generation lineage: [`data-and-figures.md`](data-and-figures.md)
- Manuscript-number checks: `scripts/check_manuscript_numbers.py`
