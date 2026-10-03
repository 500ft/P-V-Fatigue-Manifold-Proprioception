# Gate 1: Volume estimation, unresolved

Volume accuracy and P-V loop repeatability on the proposed actuator have not
been measured. The earlier claim that literature eliminated this risk is
withdrawn. This historical proposal is outside the closed project's scope in
[ROADMAP.md](../ROADMAP.md).

## Candidate methods in the earlier proposal

- Volumetric drive: [Simplifying Data-Driven Modeling of the Volume-Flow-Pressure
  Relationship in Hydraulic Soft Robotic Actuators](https://arxiv.org/html/2506.23326v1).
  This source concerns hydraulic actuators. Applying its method to a pneumatic
  chamber requires a measurement model and validation.
- Pressure-oscillation estimation: [Joshi and Paik, Sensorless force and
  displacement estimation in soft actuators](https://doi.org/10.1039/D2SM01197B).
  Performance on the source apparatus does not establish performance on an
  actuator undergoing fatigue.

The [Libby full-text check](A01_A04_Literature_Review.md#libby-full-text-check)
provides no volume validation. The [precursor review](Gate0b_Failure_Mode_Literature.md)
also leaves unresolved whether relative loop changes contain useful warning.
A volume proxy's repeatability alone cannot settle either question.

## Consequence

A future volume method would need an independent reference and uncertainty
small enough to resolve the proposed loop change under the operating conditions.
No method is accepted here, no hardware purchase is authorized, and no experiment
is scheduled. The prior commissioning targets were proposals, not measurements.
