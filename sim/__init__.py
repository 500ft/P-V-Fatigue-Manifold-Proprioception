"""Forward simulator for the shared-manifold P-V fatigue / proprioception study.

Modules (built incrementally per docs/Simulation_Plan.md):
  plant      Phase A -- nonlinear lumped pneumatic network with viscoelastic (SLS)
             chamber walls; generates realistic rate-dependent P-V hysteresis loops.
  fatigue    Phase B -- degradation trajectory + partial Mullins recovery + leak
  kinematics Phase D -- pressure -> tip SE(3) (TODO)
  sensors    Phase D -- noise / sampling / contact (TODO)
  dataset    Phase D -- labeled trace generator (TODO)

Analysis modules for completed Phase C live in the sibling ``pipeline`` package.
"""
