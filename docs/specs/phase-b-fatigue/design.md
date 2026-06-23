# Phase B Fatigue Model — Design

Status: approved
Date: 2026-06-21

## Goal

Add a deterministic, configurable actuator-life model with partial Mullins recovery,
irreversible compliance/loss drift, late leak growth, and an independent closed-valve
pressure-decay leak observable. Synthetic parameters are ground truth for pipeline
verification, not empirical fatigue validation.

## Canonical actuator

- Rupture: 3500 cycles; acceleration onset: 70% life.
- Mullins: 4% amplitude, 3-cycle saturation constant, 30% permanent floor,
  24-hour recovery constant.
- Fatigue: 4% slow whole-life drift plus 8% quadratic post-onset acceleration.
- P-V loss couplings: 1.0 for Mullins and fatigue, giving about 16% no-rest
  compliance and loop-area growth at rupture.
- Leak: baseline through acceleration onset, quadratic growth to 20x conductance at
  rupture.

The 16% drift is an order-of-magnitude synthetic anchor motivated by Libby's reported
96% to 80% FEM-agreement change; it is not a conversion from model accuracy to
compliance. The 24-hour recovery constant is an order-of-magnitude protocol choice,
not a fit to Liao et al.

## Boundaries

- Volumetric P-V loops do not observe `R_l`; leakage is observed by pressure decay.
- Acceleration onset is an injected curvature change, not a detected warning time.
- Slow-drift detectability and acceleration-onset estimation are distinct Phase C/D
  quantities.
- Damage is cycle-only under a fixed loading protocol; arbitrary rest history is not
  represented.

## Acceptance

Cycle-zero identity, partial recovery with permanent floor, exact canonical terminal
multipliers, immutable adapters, onset-gated leak, analytic pressure decay for `k2=0`,
monotone operational half-life with leak, Phase B figures/results, and all Phase A
regressions passing.
