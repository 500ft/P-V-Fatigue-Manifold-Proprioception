# Novelty and Evidence Audit — 2026-08-03

## Scope and status

This audit applies to the RoboSoft-v2 development path. It does **not** alter the
frozen `preprint-v1.3` manuscript, PDF, result JSON, or Zenodo payload.

The supplied review is directionally correct: the broad physical premise is prior
art, while the narrower recalibration-policy question remains a defensible research
contribution. This document records what survives verification, what needs narrower
wording, and what new evidence v2 must generate.

## Corrected executive assessment

The current paper is a reproducible, simulation-only study of whether a P-V
loop-derived state signal can schedule recalibration of a pressure-only pose estimator
more effectively than a cycle-count clock. It does not discover that pneumatic
actuator P-V curves change with fatigue, establish pressure-only proprioception, or
experimentally validate a fatigue diagnostic.

Within one synthetic degradation generator, the current results show that:

- compliance-scale drift, rather than shared-manifold cross-talk, dominates the
  simulated loss of pose-estimation accuracy;
- the dynamic corrector does not outperform the static corrector under the tested
  network parameters;
- P-V loop-area growth is associated with fixed-calibration pose error;
- the deployed P-V threshold does not provide positive lead on the five-stage grid;
- the P-V-triggered policy satisfies the registered simulation budget with two
  calibrations per actuator, compared with five for always-on, while the train-tuned
  cycle-count schedule fails on the held-out parameter draws.

The strongest current conclusion is therefore:

> Within the committed simulation generator, a P-V-loop-derived state signal schedules
> recalibration more successfully than an absolute cycle-count clock across held-out
> actuator parameter draws, at lower recalibration frequency than always-on updating.

That is an integration, evaluation, and decision-policy result. It is not yet a new
physical discovery or a hardware-validated monitoring technology.

## Evidence-tier audit

### Confirmed evidence

- **P-V fatigue assessment predates this work.** Mosadegh et al. (2014), the associated
  low-strain PneuNet patent, and the repository's prior-art audit establish before/after
  P-V fatigue assessment. The manuscript correctly disclaims first use.
- **Pressure-only soft-robot proprioception predates this work.** The verified related
  work includes Wang et al., Joshi and Paik, Zou et al., and others.
- **The current study is synthetic and single-generator.** All twenty actuators share
  one mathematical degradation structure; the split tests unseen parameter draws, not
  unseen physical mechanisms.
- **The P-V/pose relationship is structurally favored.** Compliance and loss evolution
  enter the same generator that produces both the loop-area trajectory and the pose
  drift. Noise and estimator behavior add separation, but they do not provide external
  causal validation.
- **The v1 confidence interval uses observation-level resampling.**
  `bootstrap_correlation` resamples the thirty held-out actuator-stage pairs as if they
  were exchangeable. Because stages from one actuator are dependent, the interval
  `[0.835, 0.958]` is retained only as a frozen v1 descriptive result; v2 must use
  actuator-cluster resampling and leave-one-actuator-out sensitivity.
- **Temporal resolution is sparse.** Five life stages support a coarse frontier and
  interpolated crossing estimates, not a strong "cycle-resolved" timing claim.
- **The health probe is not the pose estimator's normal pressure-only input.** The pose
  estimator uses pressure and commands; the health signal uses an intermittent
  volumetric P-V probe. V2 must separate those operating modes explicitly.

### Reasonable inference requiring narrower wording

- The exact combination of a P-V-derived trigger, pressure-only pose-estimator drift,
  matched recalibration-cost comparison, and retained negative manifold result is a
  plausible integration contribution. The verified audit has not identified an exact
  collision, but that is not proof of universal novelty.
- Shared-manifold cross-talk is second-order **within the tested lumped-network model
  and parameter sweep**. The result cannot be generalized to all physical manifolds.
- A three-actuator physical pilot could establish repeatability and directional
  consistency. It would not establish population-level diagnostic performance.

### Open questions

- Does the trigger still help when the degradation law changes, rather than only its
  parameters?
- Which failure modes create P-V change without pose drift, or pose drift without P-V
  change?
- Does P-V loop area outperform simpler observables such as compliance slope,
  pressure-decay leakage, phase lag, CUSUM, or a matched cycle schedule?
- At what pressure/volume noise, quantization, sample rate, and probe amplitude does the
  trigger cease to satisfy the pose budget?
- Is the chosen accuracy budget meaningful for a real grasping or placement task?
- Do physical actuators reproduce the simulated direction, timing, and repeatability?

## Corrections to the supplied review

1. **Drop the numerical novelty score.** `61/100` is a useful private heuristic but is
   neither reproducible nor appropriate evidence. Replace it with the claim/evidence
   matrix below.
2. **Do not call the existing interval actuator-level evidence.** The point estimate
   `r = 0.885` remains descriptive; the interval must be recomputed by actuator cluster.
3. **Do not say cross-talk is generally second-order.** Say it is second-order under the
   tested simulated network regime and becomes larger as supply resistance increases.
4. **Do not call five life checkpoints cycle-resolved evidence.** Use
   `life-stage-resolved` until dense simulation or measurement is performed.
5. **Do not call P-V a validated health indicator.** For simulation-only v2, prefer
   `candidate health signal` or `P-V-loop-derived recalibration signal`.
6. **Do not present N=3 hardware as validation of generality.** It is a mechanism
   spot-check that can anchor direction and repeatability only.

## Claim/evidence matrix for v2

| Proposed claim | Evidence required | Current status |
|---|---|---|
| P-V state improves recalibration scheduling over a cycle clock | Family-held-out policy comparison at matched budget/cost | Only one generator; incomplete |
| Association is stable across actuator identities | Actuator-cluster interval plus leave-one-actuator-out analysis | Point-level interval only; incomplete |
| Signal is specific to relevant degradation | Decoupled intervention matrix with false-positive/false-negative reporting | Not run |
| Trigger is robust to probe limitations | Noise/quantization/frequency/amplitude envelope | Not run |
| Savings matter operationally | Task-tolerance sweep and normalized error | Not run |
| Physical P-V change tracks physical drift | Repeated bench data with uncertainty and external pose truth | Not run |
| Shared-manifold effect is bounded in the tested model | Existing Study 4 sensitivity envelope | Complete, simulation-only |

## Bottom line

The paper should pivot from "P-V hysteresis reveals fatigue" to "when does a
P-V-loop-derived state signal justify recalibration, and when does it fail?" The
negative manifold result remains valuable as a secondary boundary study. The v2 paper
becomes stronger by exposing false positives, false negatives, domain shift, and
measurement limits—not by adding more traces from the same generator.
