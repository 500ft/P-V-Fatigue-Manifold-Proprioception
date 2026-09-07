# P-V — CAD item list

Prepared 2026-09-06 (America/New_York). **A list of planned parts and assemblies—not completed CAD, hardware or approval to fabricate/test.**

Entire list is conditional on resolving manuscript decisions and choosing a one-specimen physical pilot with available apparatus. Reuse comes first; no new production mold or N=10 campaign is included.

## How to use this list

This is a parts inventory, not another task-status ledger or additional scope/budget. Each row maps to the [work-order definitions](CAD_PLAN.md) and [sole task ledger](CAD_TASKS.csv); several parts can belong to one work order. Bought parts and existing models should be reused/imported when authorized, not redesigned merely to fill a CAD folder. One part may serve multiple listed interfaces; avoid duplicating it.

## Conditional one-specimen pilot

| Item to model or import | Existing work order | Purpose / boundary |
| --- | --- | --- |
| Existing actuator/specimen and mold reference | `PV-CAD-03` | Import and verify authorized existing geometry: chamber walls, volume and mounting envelope. This is reuse/verification, not a new mold design. |
| Specimen base and clamp | `PV-CAD-04` | Hold the actuator repeatably without crushing active chambers or obstructing motion. |
| Pressure-tee and tubing supports | `PV-CAD-04` | Locate pneumatic fittings and strain relief; show routing and traceable dead-volume lengths. |
| Syringe/volumetric-drive mounting adapter | `PV-CAD-05` | Model only the adapter/support needed around the selected existing drive. Include plunger travel/stop interfaces where needed; do not redesign a working commercial drive. |
| Pose-target holder and camera/calibration support | `PV-CAD-06` | Show target attachment, reference frame, calibration scale and full-motion visibility. |
| Complete pilot-rig assembly | `PV-CAD-07` | Assemble the reused specimen, fixture, drive and pose supports for fit/access review and dimensioned assembly views. |

## What to deliver for each applicable part or assembly

- Editable/source CAD or an authorized immutable CAD-document version; identify reused vendor geometry and its source.
- STEP export, with dimensions/units checked after reimport. Parameter-driven families also need the planned numerical geometry tests before model acceptance.
- A dimensioned drawing for custom fabricated parts, with material/process, critical fits and inspection datums; vendor hardware can use its sourced drawing.
- An assembly/section view showing how the part fits and which problem it addresses. Label all visuals CAD/design-only until corresponding evidence exists.

If an existing specimen/mold cannot be reused, stop and rescope rather than treating custom mold development as already authorized. Syringe displacement is not automatically actual chamber volume.

## Policy and scope

This list is part of the existing draft CAD PR; the recorded main-branch planning-placement decision remains unresolved. No withheld details are restored, no model task is marked done and no hardware/fabrication/disclosure gate is closed by adding this list.
