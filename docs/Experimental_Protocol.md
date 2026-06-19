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
| **0 — coupling sim** | \$0 | done | cross-talk not monotone in compliance | ✅ PASS |
| **0b — failure-mode scout** | ~\$30 | ~1 wk | sudden rupture dominates, no precursor | ☐ TODO |
| **1 — volume estimator bench** | ~\$60 | ~1 wk | no clean, repeatable *V* → no P-V loop | ☐ TODO |
| **2 — equipment audit** | \$0 | ~1 day | no mocap / no rig access | ☐ TODO |
| **Week-3 hardware coupling** | (rig) | wk 3 | cross-talk doesn't track P-V feature on real HW | ☐ TODO |

---

## Gate 0b — Failure-mode scout (run NOW, parallel to everything)

**Question this answers (binary):** do these actuators fail *gradually* (softening /
slow leak / delamination, with a compliance precursor) or by *sudden rupture* with no
warning? If sudden rupture dominates, the leading-indicator contribution (#1) is bounded
for that mode — and we'd rather know in week 1 than week 8.

**Procedure**
1. Cast 2–3 sacrificial Dragon Skin 20A actuators from the production mold.
2. Cycle each to death at ~0.5 Hz under representative grasp loading (against a
   compliant contact), logging chamber pressure continuously.
3. At every ~250 cycles, pause and capture: a photo of the chamber walls, and one slow
   reference inflation for a coarse compliance check.
4. Label end-of-life mode: **sudden rupture / slow leak / delamination**, and note
   whether *any* pressure or compliance change preceded it.

**Decision**
- Gradual modes dominate → leading indicator is viable; proceed.
- Sudden rupture dominates → scope contribution #1 honestly to the modes it *can* serve;
  shift weight to Study 2 (cross-talk) as the safe publishable core.

---

## Gate 1 — Volume estimator bench test (the silent killer)

The entire premise is a *P-V* loop, and **V is the least-specified, most load-bearing
measurement in the paper.** Validate it before trusting any loop.

**Procedure**
1. Build the candidate *V* estimators:
   - (a) flow integration: integrate a calibrated mass-flow / laminar-flow sensor;
   - (b) pressure-oscillation observer (Joshi & Paik 2023);
   - (c) optional ground truth: displaced-volume measurement (water column / syringe
     reference) over a known inflation.
2. Run 50 identical actuation cycles at the **actuation-band frequency chosen by Gate 0
   (~1–5 Hz)**, not quasi-statically.
3. Measure: drift of the integrated *V* over the 50 cycles (integration error
   accumulation), and RMSE of (a) and (b) against (c).

**Decision / acceptance**
- *V* drift over a measurement window < a few % of loop volume, repeatable → P-V loop
  is real; use it.
- Drift too large → **fallback:** periodic-reset flow integration, or work in
  **P-vs-commanded-displacement** / **P-vs-flow-integral** space instead of true volume.
  State the substitution explicitly in the paper; the loop-shape features (area, slope,
  asymmetry) survive the substitution.

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
