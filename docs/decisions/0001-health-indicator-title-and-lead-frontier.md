# ADR 0001: Health-Indicator Title and Lead Frontier

## Status
Accepted 2026-07-03.

## Context
The original result spine expected P-V loop shape to be a positive leading
indicator of proprioception degradation. Wave A audited that claim at the
deployed train-selected threshold, `tau*=0.05`, and found no positive temporal
lead on held-out actuators. Wave A.2 then characterized a separate descriptive
frontier over lower thresholds without changing the deployed policy.

## Decision
The manuscript title and headline use "health indicator," not "leading
indicator." The deployed policy and selection grid remain frozen for arXiv
v1.2. Positive lead is reported as threshold-dependent via
`lead_frontier_heldout`: lower thresholds buy lead at higher recalibration cost,
while the deployed fewest-recalibration operating point fires late.

## Alternatives Considered
- Retitle back to "leading indicator": rejected because the frontier proves
  temporal lead is configuration-dependent.
- Refine the selection grid and move `tau*` to a nearby value: rejected because
  it would change reported numbers without changing the deployed schedule.
- Edit `docs/result_spine.md` to match the final outcome: rejected because the
  frozen spine is evidence that the pre-specified expectation was audited and
  downgraded honestly.

## Consequences
The arXiv v1.2 paper is more conservative but more defensible. Reviewers can see
the full lead-vs-recalibration trade-off, the failed deployed lead claim, and the
single-generator limitation around normalized health trajectories.
