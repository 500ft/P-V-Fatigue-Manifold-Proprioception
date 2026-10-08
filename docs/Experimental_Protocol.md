# Experimental Protocol & Test Plan

Historical protocol for the P-V fatigue / shared-manifold proprioception study.
The project is closed under [ROADMAP.md](../ROADMAP.md); the unexecuted hardware
steps below remain proposals and are not authorized work.
This is the "how to actually test it" companion to
[`Proposal_A01_A04_Combined.md`](https://github.com/500ft/soft-actuator-recalibration/blob/f67118d2598910d9913ccd372c90a60cb8752e6b/docs/Proposal_A01_A04_Combined.md). It encodes the
decisions forced by [`Gate0_Coupling_Simulation.md`](Gate0_Coupling_Simulation.md).

> The original gate ladder is retained below with its unsupported literature
> resolutions corrected. It does not reopen the proposed campaign.

---

## 0. Historical gate ladder

| Gate | Cost | Time | Kills/redirects if… | Status |
|---|---|---|---|---|
| **0 — coupling sim** | \$0 | done | cross-talk not monotone in compliance | ✅ PASS ([doc](Gate0_Coupling_Simulation.md)) |
| **0b: failure-mode scout** | Uncosted | Not run | no useful measured precursor | Unresolved ([review](Gate0b_Failure_Mode_Literature.md)) |
| **1: volume estimator** | Uncosted | Not run | volume uncertainty obscures loop changes | Unresolved ([review](Gate1_Volume_Estimation_Literature.md)) |
| **2 — equipment audit** | \$0 | ~1 day | no mocap / no rig access | ☐ TODO |
| **Week-3 hardware coupling** | (rig) | wk 3 | cross-talk doesn't track P-V feature on real HW | ☐ TODO |

> Gates 0b and 1 require evidence that the cited experiments do not supply.
> Their corrected reviews state the remaining measurement questions.

---

## Gate 0b: Failure-mode scout, unresolved

The [corrected failure-mode review](Gate0b_Failure_Mode_Literature.md) withdraws
the literature-based PASS. The Libby result cannot establish useful P-V warning
before rupture. The proposed feature choice and single-specimen spot-check were
not validated by that citation.

---

## Gate 1: Volume estimate, unresolved

The [corrected volume review](Gate1_Volume_Estimation_Literature.md) retains the
candidate methods and removes the claim that volume measurement was resolved.
Their performance on the intended actuator and their ability to resolve the
hypothesized precursor remain unmeasured.

---

## Gate 2 — Equipment audit (one afternoon, \$0)

The \$320 BOM silently assumes hardware that may not exist. Confirm, in writing:

- **Ground-truth pose:** Is OptiTrack/Vicon with <1 ms hardware sync actually available?
  - If **yes** → rigid distal-boss marker cluster → tip SE(3) (Proposal §5.1).
  - If **no** → calibrated single camera + ArUco/AprilTag on the distal boss. Adequate
    for 3-chamber tip pose, in-budget. Re-state ground-truth accuracy honestly.
- **Cycling rig:** regulator + solenoid valves + DAQ on hand? Teensy 4.1 at 100 Hz.
- **Pressure sensors:** Honeywell HSC ±0.5 % FS, one tee-fitted per chamber.

Produce a real bill of materials + availability table; replace the \$320 estimate with
the audited number.

---

## Study 1 — P-V fatigue leading indicator (RQ1)

**Specimens:** N = 10 Dragon Skin 20A actuators, single reusable mold (control casting
variance). **Within-actuator baselining** — each actuator is its own control — instead of
a cross-actuator 2σ threshold.

**Loading:** representative grasp loading (compliant contact), ~0.5 Hz cycle-to-failure.
Optionally a parallel free-inflation arm to report transfer. **State which regime each
result came from.**

**Mullins / recovery control (designed sub-experiment, not a footnote):**
- Establish each actuator's healthy baseline **after** stress-softening stabilizes
  (~first 5–10 cycles; Lavazza 2023).
- Fix a **rest-then-measure** procedure: identical rest interval before every reference
  P-V loop, because loop area depends on recovery time (Liao 2021).
- Run a **rest-recovery control arm**: pause a subset mid-life and confirm partial loop
  recovery → separates reversible softening from irreversible fatigue drift.

**Reference-loop cadence:** every 250–500 cycles, capture a clean P-V loop **probed at
the Gate-0 actuation band (~1–5 Hz)** — the band where compliance change is observable.

**Features:** loop area (hysteresis energy), peak pressure, pressure@80%-volume slope,
inflation/deflation asymmetry, PCA PC1 of loop shape.

**Model & metrics:** per-feature logistic/double-logistic degradation fit; health-
indicator quality (monotonicity, trendability, prognosability — Lei 2018); **per-actuator
lead-time distribution with CIs** (not a single number — N=10 is underpowered, say so);
early-warning AUC; false-alarm rate. Visual first-crack inspection = lead-time baseline.

---

## Study 2 — Shared-manifold cross-talk (RQ2) — *the safe publishable core*

**Cross-talk measurement:** measure the 3×3 coupling **in operating condition** — all
valves live, perturb one chamber across pressure levels. **Not** with neighbors sealed
(sealed neighbors are isometric → wrong coupling). Report the matrix as
**pressure-dependent** AND **frequency-dependent** — Gate 0 shows the coupling is dynamic,
so a single static matrix is insufficient; characterize across ~0.1–10 Hz.

**Correctors, compared on pose reconstruction (N ≈ 2000 labeled traces):**
1. **Ridge** — uncorrected static baseline. *Gate 0 predicts this is blind to the
   fatigue-induced coupling drift* — that prediction is now a result to confirm.
2. **ARX** — explicitly subtracts modeled cross-talk; interpretable, scientifically
   primary. (Run the defensive prior-art search on pneumatic ARX decoupling **now**, not
   before submission — see Proposal risk list.)
3. **ESN** (~100 nodes, hyperparameters reported) — black-box dynamic comparator.

**Metrics:** pose RMSE (mm + deg), contact F1, inference latency, and coupling-matrix
magnitude vs frequency.

---

## Study 3 — Coupled failure + recalibration (RQ3) — *the upside, not the schedule driver*

- Track the cross-talk matrix and pose RMSE as actuators age; test the refined Gate-0
  prediction: **dynamic** cross-talk coefficients (at 1–5 Hz) drift with the P-V compliance
  feature, while DC coupling stays fixed. Confirming result: ρ ≥ 0.5 (p < 0.05).
- Evaluate **P-V-triggered recalibration** (recalibrate when the health monitor crosses
  threshold) vs fixed calibration vs always-on continual learning (Kushawaha 2025 as the
  efficiency baseline-to-beat): triggers fired vs RMSE recovered.

---

## Minimum viable paper (internal descope)

If time/specimens run short, the guaranteed-result core is **Studies 1 + 2**:
a P-V leading-indicator characterization + the first shared-manifold cross-talk
characterization (with the Gate-0 dynamic-coupling finding). Study 3 (the coupling spine)
is the upside. **Do not let Study 3 set the timeline.** External fallback if the Week-3
hardware gate fails: **G02 kirigami force-stroke fatigue maps** — reuses the same cycling
rig and force/displacement instrumentation.

---

## Reporting standards (Zhang et al. 2023; Lei 2018)

Pose RMSE in mm **and** deg; contact precision/recall/F1; lead-time as a distribution
with CIs; HI monotonicity/trendability/prognosability; all model hyperparameters; raw
P-V loops and feature trajectories in supplementary. Curvature/PCC reported only as a
**modeled output validated against** rigid-cluster tip SE(3), never as measured truth.
