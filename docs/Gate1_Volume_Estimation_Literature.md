# Gate 1 — Volume Estimation (design-resolved from literature)

**Status:** design-resolved (one hardware spot-check remains) · **Date:** 2026-06-19
**Verdict: the "no clean V" risk is eliminated by adopting the field's established
practice — drive the actuator volumetrically for clean P-V loops, and use the
pressure-oscillation observer as the deployable in-loop estimator. Naive flow
integration is rejected.**

---

## Question

The entire premise is a *P-V* loop. *V* is the least-specified, most load-bearing
measurement in the paper. Can we obtain a clean, repeatable volume signal — or does
volume estimation drift kill the loop?

## What the literature settles (and what it doesn't)

Volume sensing in soft actuators is a **known-hard, actively-studied** problem. The
literature does **not** hand us a turnkey real-time volume sensor, but it *does* give two
validated, quantified paths — and rejects the naive one. That is enough to fix the
experimental design without inventing anything.

| Approach | Source | Quantified result | Role for us |
|---|---|---|---|
| **Naive flow integration** (∫Q dt) | Joshi & Paik 2023; general consensus | "Error accumulates due to numerical integration, noise, and **leakage**." Explicitly called unreliable over long durations. | **Rejected.** Do not build the P-V loop on raw flow integration. |
| **Direct volumetric drive** (syringe/stepper-pump positions the air volume) | "Volume-Flow-Pressure modeling…" arXiv:2506.23326 | Volume controlled to **0.04 mm³/step**; pressure is predicted *from* commanded volume. Ground-truth-grade. | **Primary acquisition method** for clean P-V loops on the bench and in the Study-1 fatigue rig. |
| **Pressure-oscillation observer** (inject ~5 kPa high-freq oscillation; dP/dt ∝ 1/V) | Joshi & Paik 2023 (PMC10074228) | Volume RMS error **0.522 mL on an 83 mL actuator (~0.6 %)** via a small per-actuator NN. (Force <10 %, displacement 11–16 % as by-products.) | **Deployable in-loop estimator** for the pressure-only gripper; validate it against the volumetric drive. |

## Resolution (the design decision this gate forces)

1. **Acquire P-V loops by volumetric actuation, not flow integration.** Drive each
   actuator with a **stepper-driven syringe / volumetric pump** so the commanded air
   volume is *known by construction* (cf. arXiv:2506.23326, 0.04 mm³/step). The P-V loop
   is then pressure (measured) vs volume (commanded) — clean, repeatable, drift-free,
   and cheap. This sidesteps the flow-integration drift problem entirely and is the
   field's standard practice for hysteresis characterization.
   - This is fully compatible with Study 1 (fatigue characterization) and Study 2
     ground-truth, where we control the rig.

2. **For the deployed pressure-only case, use the pressure-oscillation observer.** Where
   the gripper must self-sense without a syringe pump (the "no added sensors" thesis),
   estimate *V* from the injected-oscillation method (≈0.6 % RMS). Calibrate one NN per
   actuator; **validate it against the volumetric ground truth** from (1). This keeps the
   pressure-only claim honest: the deployable estimator is shown to track the
   ground-truth loop.

3. **Loop-shape features survive even if absolute V is imperfect.** Because the leading
   indicator uses *relative drift within an actuator* (loop area, compliance slope,
   asymmetry — see Gate 0b feature targeting), a consistent volume *proxy* is sufficient;
   absolute volumetric accuracy is a bonus, not a requirement. With volumetric drive we
   get both.

## What still needs a (small) hardware spot-check

Literature resolves the **method choice** but not the **numbers on our specific
actuator**. One short commissioning test remains (folded into rig bring-up, not a separate
campaign):
- Confirm the syringe/stepper drive produces repeatable P-V loops (loop-area
  repeatability across, say, 50 cycles at the Gate-0 actuation band ~1–5 Hz).
- Fit and validate the pressure-oscillation observer against the volumetric ground truth
  on one actuator; report its RMS error (target: same order as Joshi & Paik's ~0.6 %).

This is verification of a literature-validated method on our hardware — not an open
research risk. The "no clean V → no P-V loop" failure mode is **closed by design.**

## Consequence for the BOM

Add a **stepper-driven syringe / small volumetric pump** to the rig (a few tens of
dollars: NEMA-17 + lead screw + syringe, or a repurposed syringe-pump kit). This replaces
reliance on a precision flow sensor for the loop measurement and is cheaper and more
reliable. Update the equipment audit (Gate 2) accordingly.

## Sources
- Joshi & Paik, *Sensorless force and displacement estimation in soft actuators*, Soft Matter 19 (2023), DOI 10.1039/D2SM01197B — https://pmc.ncbi.nlm.nih.gov/articles/PMC10074228/
- *Simplifying Data-Driven Modeling of the Volume-Flow-Pressure Relationship in Hydraulic Soft Robotic Actuators*, arXiv:2506.23326 — https://arxiv.org/html/2506.23326v1
