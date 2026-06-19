# Gate 0b — Failure-Mode Scout (resolved from literature)

**Status:** complete (literature-resolved) · **Date:** 2026-06-19 · **Verdict: PASS — gradual
degradation with precursors; contribution #1 (leading indicator) is viable.**

---

## Question

Do silicone PneuNet actuators fail **gradually** (softening / leak / delamination, with a
detectable precursor) or by **sudden rupture** with no warning? If sudden rupture
dominates, the P-V leading-indicator contribution is bounded for that mode regardless of
the Gate 0 simulation.

## Why this is answerable from literature

This is not a novel question — it is a documented property of the exact actuator class
(Dragon Skin / Ecoflex PneuNets) we plan to use. Two studies on this class settle it, so
the original ~$30 / one-week scouting experiment is **downgraded to a spot-check** rather
than a from-scratch gate.

## Evidence

| Source | Finding relevant to failure mode |
|---|---|
| **Libby et al. 2022** (*What Happens When Pneu-Net Soft Robotic Actuators Get Fatigued?*, arXiv:2212.03420) | Fatigue is **progressive, not sudden**: "microscale fractures in the elastomeric structure" develop during actuation and **accumulate** into macroscale damage and eventual failure. Quantitatively, FEM-model agreement degrades from **~96 % → 80 %** (16-pt drop) after repetitive high-angle (167°) bending — i.e. behavior drifts measurably *before* end of life. |
| **Torzini et al. 2024** (fatigue of fluidic elastomer actuators, DOI 10.1007/s00170-024-14216-0) | Silicone specimens reach **~3439 cycles** to failure at 1 bar (0.5 Hz, n=5). **Micro-tears (0.2–0.4 mm) appear as lacerations at the base of the humps *before* critical rupture** and "did not affect performance heavily before the critical point was reached" — an explicit precursor that exists but is sub-catastrophic. |
| **Mosadegh et al. 2014** (PneuNet definition) + general SPA reviews | Fatigue manifests as **leaks → decreased efficiency → changed actuator dynamics → failure**, concentrated at the **highest-local-stress** site (hump bases). A gradual leak/compliance pathway, consistent with Libby/Torzini. |

## Verdict and consequences

**PASS.** The dominant failure pathway for this actuator class is **gradual** —
micro-tears nucleate at predictable high-stress sites (hump bases), accumulate, shift the
actuator's mechanical behavior measurably, and only then proceed to rupture. There is a
real precursor window for a leading indicator to exploit. This is consistent with, and
independent confirmation of, the proposal's premise (and of Libby's own report that the
**P-V hysteresis shifts with fatigue**).

**What this changes in the plan:**
1. **Do not run Gate 0b as a standalone gate.** Cite Libby 2022 + Torzini 2024 for the
   gradual-failure premise. Reduce to a **single-specimen spot-check** folded into Study 1
   commissioning: confirm *your* mold/material reproduces hump-base micro-tear nucleation
   before rupture (one actuator, photographed every ~250 cycles). If it does, proceed; if
   your geometry ruptures suddenly with no precursor, *then* escalate.
2. **Honest scope statement for the paper.** The leading indicator targets the
   **gradual-degradation regime** (micro-tear accumulation → compliance/leak drift).
   State the operating envelope explicitly; do not claim coverage of any sudden-rupture
   mode, which the literature shows is the *terminal* event, not the precursor.
3. **Feature targeting.** Because precursors are sub-catastrophic and behavioral (Libby's
   16-pt model drift; Torzini's tolerated 0.2–0.4 mm tears), the P-V features most likely
   to carry early signal are **compliance slope and loop-area drift**, not peak-pressure
   collapse (which is a late, near-rupture event).

## Residual risk (small)

Cycles-to-failure and precursor size are geometry/material/loading specific. The
spot-check in (1) closes the residual. Sudden-rupture-dominant geometries (thin walls,
stress concentrations) remain possible — the spot-check is the cheap insurance.

## Sources
- Libby et al., *What Happens When Pneu-Net Soft Robotic Actuators Get Fatigued?*, arXiv:2212.03420 — https://arxiv.org/abs/2212.03420
- Torzini et al., *Characterization of fatigue behavior of 3D printed pneumatic fluidic elastomer actuators*, Int. J. Adv. Manuf. Technol. 134:2725–2736 (2024), DOI 10.1007/s00170-024-14216-0
- Mosadegh et al., *Pneumatic Networks for Soft Robotics that Actuate Rapidly*, Adv. Funct. Mater. 24(15):2163–2170 (2014), DOI 10.1002/adfm.201303288
