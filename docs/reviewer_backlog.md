# Reviewer-Hardening Backlog (STORM analysis, 2026-07-13)

Findings from a STORM multi-perspective review of `docs/preprint_v1.md`, captured
so they are not lost. **These are leads for author triage, not applied edits.**
Every proposed citation is marked *verify DOI against the primary source before
adding*. Nothing here changes a committed result number; the honest
health-indicator / negative-lead framing is preserved.

Scope note: arXiv v1 (tag `preprint-v1.3`) can post as-is. This backlog is
pre-**RoboSoft** hardening (Wave B), to run only if that deadline becomes real.

## Grounded — worth adding (peer-reviewed)

1. **Report the standard health-indicator quality metrics, not just Pearson r.**
   PHM judges a health indicator by monotonicity / trendability / prognosability.
   The paper already cites Lei et al. 2018 (MSSP), which codifies these, but
   never computes them. Computable from existing sim traces (no measurement
   claim). Honest caveat: trendability will look artificially high because the
   normalized health trajectory is near-identical across actuators (§5's own
   point) — report it anyway; it reinforces the single-generator caveat.
   Primary source to verify: Coble & Hines (optimal prognostic parameters).

2. **Cite direct experimental evidence of the micro-tear precursor window.**
   Torzini et al. 2024, *Int. J. Adv. Manuf. Technol.*, DOI 10.1007/s00170-024-14216-0:
   silicone pneumatic actuators show 0.2-0.4 mm micro-tears before critical
   rupture without heavy performance loss — real backing for the precursor window
   the model assumes. Referenced in the internal Gate0b doc but NOT in the
   preprint's §2. Turns "we assume gradual failure" into "gradual failure with a
   precursor window is experimentally established (Torzini 2024)."

3. **Position the sim-only scope against the soft-robotics sim-to-real body.**
   §5 lists real-silicone failure modes but does not cite the field that studies
   exactly this transfer. Candidates to verify: "Unsupervised Sim-to-Real
   Adaptation of Soft Robot Proprioception" (*Soft Robotics* 2024,
   DOI 10.1089/soro.2024.0025); residual-physics and zero-shot sim-to-real
   proprioception work. One sentence placing the hardware spot-check within
   sim-to-real methodology.

## Open questions — framing, not new citations

4. **Why a fixed fractional-growth trigger and not a principled change-point
   detector (CUSUM)?** Position the threshold as a deliberately simple,
   interpretable choice; optionally anchor to Page 1954. Do not add cross-domain
   arXiv cites.

5. **The pooled r bootstraps non-independent points** (6 actuators x 5 stages,
   repeated-measures). The per-actuator r (median 0.957) is the cluster-level
   check — say so explicitly; acknowledge non-independence. Interpretation of an
   existing number, not a change to it.

## Minor / framing

6. Name the actuator-identity split in ML vocabulary (leave-group-out /
   domain-generalization), and note the small held-out N.
7. Acknowledge single-segment PCC vs. multi-segment / Cosserat kinematics as a
   limitation-completeness item in §5.
