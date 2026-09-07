# Prospective integrity core — proposed, 2026-09-05

The optional physical-pilot CAD branch is decomposed in [CAD_PLAN.md](../../CAD_PLAN.md) and [CAD_TASKS.csv](../../CAD_TASKS.csv). It does not become a prerequisite for this simulation core or adopt the older hardware protocol's stronger health/early-warning claims. Owner reconciliation and actual equipment access precede pilot geometry release.

This is a development design, not a frozen preregistration. Do not backdate it or
describe any v2 result as accomplished. The separate original checkout contains
uncommitted owner drafts; author reconciliation precedes a pushed specification
commit and any confirmatory v2 result generation.

## Minimum publishable core, contingent on results

Three interventions: coupled compliance drift (positive control), a loss/viscosity
change that can alter loop area without comparable pose drift (false-positive
challenge), and an explicitly modeled pose-channel bias or local kinematic change
that can shift pose without comparable P-V drift (false-negative challenge).
First verify that each intervention actually decouples the endpoints; its label
is a design intention, not proof. Document equations, units and parameter support.

Four policies: fixed, always, cycle-count and P-V threshold. Keep initialization
separate from subsequent recalibrations. Generate noisy probe observations and
integrate those observations for area; never substitute the analytic latent
signal without labeling an oracle control. Evaluate rest and sampling assumptions
in development before freezing operating conditions.

Choose an application-linked pose tolerance and selection rule on training data
only. Report macro-averaged RMSE, maximum sampled error, budget-violation fraction,
trigger lead on a denser registered life grid, and counted calibration events.
Do not call a mean-error pass continuous safety. Keep task tolerances proposed
until an application requirement supplies them.

Hold out at least one supported degradation family with no tuning on its outputs.
Freeze candidate, seeds, family selection and metrics before evaluation. Use
actuator-cluster bootstrap plus leave-one-actuator-out sensitivity; report effect
sizes and the small identity denominator. If the held-out family exposes a flaw
and informs a fix, it becomes development data for the revised candidate.

## Scope and stop rules

New CUSUM baselines, six-family sweeps, exhaustive five-axis envelopes and hardware
are strengthening work, not prerequisites for this minimum comparison. A signal
that fails on a decoupled family remains a reportable conditional failure map.
No physical-health, general transfer or early-warning claim is permitted without
the corresponding evidence. The present sprint corrects evidence lineage and
publication readiness; it does not implement or freeze this new research campaign.
