# Experimental Protocol & Test Plan

Operational runbook for the P-V fatigue / shared-manifold proprioception study.
This is the "how to actually test it" companion to
[`Proposal_A01_A04_Combined.md`](Proposal_A01_A04_Combined.md). It encodes the
decisions forced by [`Gate0_Coupling_Simulation.md`](Gate0_Coupling_Simulation.md).

> **Gating philosophy:** cheap, decisive tests first. Every gate can kill or redirect
> the project before the expensive N=10 campaign. Do them *in order*.

---

## 0. Gate ladder (do these before the full campaign)

| Gate | Cost | Time | Kills/redirects if… | Status |
|---|---|---|---|---|
| **0 — coupling sim** | \$0 | done | cross-talk not monotone in compliance | ✅ PASS ([doc](Gate0_Coupling_Simulation.md)) |
| **0b — failure-mode scout** | \$0 | done | sudden rupture dominates, no precursor | ✅ PASS — literature-resolved ([doc](Gate0b_Failure_Mode_Literature.md)) |
| **1 — volume estimator** | \$0 | done | no clean, repeatable *V* → no P-V loop | ✅ design-resolved ([doc](Gate1_Volume_Estimation_Literature.md)) |
| **2 — equipment audit** | \$0 | ~1 day | no mocap / no rig access | ☐ TODO |
| **Week-3 hardware coupling** | (rig) | wk 3 | cross-talk doesn't track P-V feature on real HW | ☐ TODO |

> **Gates 0b and 1 are now resolved from literature** (no own-hardware experiment needed
> to *decide* them): silicone PneuNets fail gradually with micro-tear precursors (Libby
> 2022, Torzini 2024), so the leading indicator is viable; and the volume signal is
> obtained by volumetric (syringe/stepper) drive + a pressure-oscillation observer
> (Joshi & Paik 2023, ~0.6 % RMS), not by drift-prone flow integration. Each leaves a
> small commissioning **spot-check** folded into rig bring-up — see the respective docs.

---

## Gate 0b — Failure-mode scout — RESOLVED FROM LITERATURE ([full doc](Gate0b_Failure_Mode_Literature.md))

**Question (binary):** do these actuators fail *gradually* (with a precursor) or by
*sudden rupture*? **Answer: gradual, with precursors.** Silicone PneuNets accumulate
microscale fractures that shift behavior measurably before failure — Libby 2022 reports
FEM agreement drifting 96 %→80 % with fatigue; Torzini 2024 reports 0.2–0.4 mm micro-tears
at the hump bases, tolerated *before* critical rupture (~3439 cycles, 1 bar). The leading
indicator is viable; **target compliance-slope / loop-area drift** (early) rather than
peak-pressure collapse (late). Scope the paper to the **gradual-degradation regime**.

**Remaining spot-check (folded into Study-1 bring-up, not a standalone gate):** cast one
actuator from the production mold, photograph the chamber walls every ~250 cycles, and
confirm *your* geometry reproduces hump-base micro-tear nucleation before rupture. If it
instead ruptures suddenly with no precursor, escalate; otherwise proceed.

---

## Gate 1 — Volume estimate — DESIGN-RESOLVED FROM LITERATURE ([full doc](Gate1_Volume_Estimation_Literature.md))

The entire premise is a *P-V* loop, and **V was the least-specified, most load-bearing
measurement in the paper.** Literature closes the *method choice*:

- **Reject naive flow integration** — Joshi & Paik confirm error accumulates from
  integration, noise, and leakage.
- **Acquire P-V loops by volumetric drive** — a stepper-driven syringe positions the air
  volume so *V* is known by construction (arXiv:2506.23326, 0.04 mm³/step). Clean,
  drift-free, cheap; this is standard practice for hysteresis characterization and is used
  for Study 1 and Study 2 ground truth.
- **Deployable in-loop estimator** — the pressure-oscillation observer (inject ~5 kPa
  high-freq oscillation; dP/dt ∝ 1/V) gives ~0.6 % volume RMS (Joshi & Paik), used where
  the gripper must self-sense without a syringe pump; validate it against the volumetric
  ground truth.

**Remaining spot-check (folded into rig bring-up):** confirm the syringe drive yields
repeatable P-V loops over ~50 cycles at the Gate-0 band (~1–5 Hz), and fit + validate the
oscillation observer on one actuator (target RMS ~ Joshi & Paik's 0.6 %).

**BOM consequence:** add a stepper-driven syringe / small volumetric pump (~tens of \$);
it replaces reliance on a precision flow sensor. Update Gate 2 accordingly.

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
