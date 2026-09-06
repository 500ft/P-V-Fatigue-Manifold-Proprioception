# P-V-Fatigue-Manifold-Proprioception — individual CAD tasks

Prepared 2026-09-06. **Planning only: no CAD model, drawing, fabrication, calibration or physical result was produced by this amendment.**

[CAD_TASKS.csv](CAD_TASKS.csv) is the sole status ledger for this new CAD phase. The earlier [SPRINT_TASKS.csv](SPRINT_TASKS.csv) remains the authority for the separate 30-hour evidence-integrity sprint; its estimates and achieved software evidence are unchanged. This plan expands mechanical work orders, not publication or test permission. Scope tiers are in [scope.md](specs/cad-development/scope.md).

## Verified reason for the work

The physical protocol calls for cast actuators, volumetric drive and independent pose measurement but does not decompose the apparatus CAD. The newer prospective integrity core makes hardware optional. The older protocol's leading-indicator and guaranteed-result language is not evidence or the v2 claim contract.

Inspected source documents:

- [docs/Experimental_Protocol.md](Experimental_Protocol.md)
- [docs/specs/v2-integrity-core/design.md](specs/v2-integrity-core/design.md)

## Outcome and boundaries

A reviewer can reopen editable, version-pinned geometry; regenerate neutral STEP exports; understand the assembly, critical fits and measurement datums; and distinguish design assumptions from inspected hardware. STL is only a manufacturing derivative where appropriate, not the sole editable master. For hosted CAD retain a version-specific share reference and authorized portable source/export archive; record tool/version and export settings. Do not require a particular commercial tool before checking access.

**Entry decision:** Owner elects a physical pilot, reconciles the older protocol with the prospective core, and supplies apparatus access plus a reviewed measurement requirement.

**Excluded:** No CAD prerequisite for the simulation-only paper; no full ten-specimen campaign, new physiological/health claims, or automatic adoption of the older protocol's hardware assumptions.

Agent owns document preparation and modeling once inputs exist; Owner owns actual component/access choices and review authority; External fabricators/operators own quotes, manufacture and facility approval. No approval, purchase, fabrication booking, IP disclosure of third-party drawings, or test run is completed by checking in this plan. Unknown critical dimensions block fabrication; conceptual placeholders must be visible and cannot become as-built evidence.

## Focused-hour allocation

The initial CAD phase is **23 estimated focused hours**, additional to the earlier software sprint. All hardware work in this phase remains subject to the entry decision. These are estimates, not recorded work. Each day is a workload bucket after its prerequisites, not a calendar promise; quotes, calibration and facility lead times are not compressed into CAD hours.

| Workload day | Hours | Ordered tasks |
| --- | ---: | --- |
| 1 | 4 | PV-CAD-01 → PV-CAD-02 |
| 2 | 5 | PV-CAD-03 |
| 3 | 4 | PV-CAD-04 |
| 4 | 4 | PV-CAD-05 |
| 5 | 3 | PV-CAD-06 |
| 6 | 3 | PV-CAD-07 |

Critical path follows the explicit task dependencies below: input register → owner decisions → parts/fixtures → release review. Independent branches may proceed after their shared inputs close. The entire physical branch is optional to the simulation paper.

## Individual work orders

All output paths below are **proposed NEW deliverables**, not existing artifacts. Current task state appears only in the CSV; the headings below define acceptance, not completion.

### PV-CAD-01 — Reconcile physical-pilot geometry and measurement requirements

- Owner: Agent; priority: P1; estimate: 2 h; workload day: 1.
- Dependencies: none; source inspection is available now.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/requirements.md; cad/pilot/parameters.csv`.
- Done when: Separate chamber volume from syringe displacement, tubing dead volume, gas compressibility and leaks; identify critical geometry, camera accuracy and pressure limits as sourced values or unresolved inputs. Map each fixture to an observable endpoint, not a health claim.
- Verification and evidence to retain: Review against both source documents; retain a requirement-to-part table with units and unresolved decisions.

### PV-CAD-02 — Confirm pilot access, reference geometry and fabrication method

- Owner: Owner; priority: P1; estimate: 2 h; workload day: 1.
- Dependencies: PV-CAD-01.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/owner-inputs.md`.
- Done when: Approve the physical-pilot scope, camera or mocap access, actuator geometry source and reuse/new-mold decision, selected syringe/drive and manufacturing capability. Record actual dimensions or vendor references; unknown critical fits block fabrication.
- Verification and evidence to retain: Owner signs dated decisions and availability references; identify material/process, operator and laboratory approval still needed.

### PV-CAD-03 — Model reusable actuator mold and specimen interfaces

- Owner: Agent; priority: P1; estimate: 5 h; workload day: 2.
- Dependencies: PV-CAD-02.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/mold/ (editable source, STEP, drawings)`.
- Done when: Model mold split, core registration, chamber wall thickness, filling/venting, demolding access and casting datums; record shrinkage as an assumption until measured. If an existing released mold is reused, inspect/version that source and document no new mold needed instead of duplicating it.
- Verification and evidence to retain: Regenerate at nominal and reviewed wall-thickness bounds; inspect cross-sections, trapped geometry and mold opening; retain screenshots and dimension checks.

### PV-CAD-04 — Model specimen base and pneumatic-routing fixture

- Owner: Agent; priority: P1; estimate: 4 h; workload day: 3.
- Dependencies: PV-CAD-02.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/specimen-fixture/ (source, STEP, assembly drawing)`.
- Done when: Define repeatable clamping without crushing active chambers, pressure tee locations, strain relief and traceable tubing lengths. Preserve free/contact operating modes selected by the pilot; no fixture contact in the measured motion envelope.
- Verification and evidence to retain: Review assembly mates, full motion clearance and hose routing; retain interference and nominal/dead-volume inventory.

### PV-CAD-05 — Model volumetric-drive mounting and calibration interfaces

- Owner: Agent; priority: P1; estimate: 4 h; workload day: 4.
- Dependencies: PV-CAD-02.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/volume-drive/ (source, STEP, dimensioned assembly)`.
- Done when: Reference the selected commercial drive or model syringe restraints, plunger alignment, travel stops and pinch-zone shielding for a custom drive. Record stroke-to-displacement calibration interface; syringe displacement must not be labeled direct chamber volume.
- Verification and evidence to retain: Check full travel and connector access; produce an error-source diagram covering compliance and gas/tubing effects; qualified review remains necessary before pressurization.

### PV-CAD-06 — Model independent pose target and camera/calibration fixture

- Owner: Agent; priority: P1; estimate: 3 h; workload day: 5.
- Dependencies: PV-CAD-02, PV-CAD-04.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/pose-fixture/ (source, STEP, views)`.
- Done when: Define marker/target attachment, sensor coordinate frame, scale reference and camera or mocap clearance. Quantify added target mass from sourced density and note potential perturbation of actuator pose.
- Verification and evidence to retain: Retain field-of-view and full-motion checks plus target mass calculation; physical pose accuracy is deferred to calibration.

### PV-CAD-07 — Release a reproducible pilot CAD and fabrication-review packet

- Owner: Agent; priority: P1; estimate: 3 h; workload day: 6.
- Dependencies: PV-CAD-03, PV-CAD-04, PV-CAD-05, PV-CAD-06.
- Scope: initial CAD phase, subject to its input/owner gate.
- Proposed deliverables: `cad/pilot/release/ (BOM, drawings, export manifest, inspection checklist)`.
- Done when: Publish editable/version-pinned source, STEP solids, fabrication drawings, dimensions/material/process notes, supplier references, assembly and section visuals. Proposed assets remain labeled CAD/design-only; pressure-test permission and calibration are separate gates.
- Verification and evidence to retain: Second operator reopens exported geometry and checks units, dimensions, part count and assembly fit against source. Retain hashes and review issues; no build approval from this task alone.

## Release review and overrun rule

Every release includes an assembly/exploded view, a critical section/detail view and a measurement/inspection setup view. Captions identify the question illustrated, source revision, dimensions/units and **CAD prediction—not measured** state; cite vendor/hand-calculation references actually used. Render quality is not evidence of fit or performance.

Before marking a CAD task done, attach real source/export identities, regeneration instructions and the corresponding acceptance evidence in CAD_TASKS.csv. A second AI pass is a development check, not independent human or laboratory validation. Retain failed fits and unresolved assumptions; do not silently tune experimental geometry after observing confirmation data.

If the phase overruns, postpone decorative renders, optional variants and mechanism extensions first. Do not remove required fits, safety interfaces, reference controls, source traceability or measurement access. Fabrication-release review, apparatus commissioning and physical evaluation remain separate future actions; updated geometry may require a new prospective analysis/reference freeze. Preparing drawings does not close an existing physical-readiness or publication blocker.

## PR review scope

This amendment changes task planning and navigation only. It is stacked on the open evidence-integrity PR so its diff excludes earlier fixes. No software behavior or frozen scientific threshold is changed. Review task dependencies and claim boundaries now; actual CAD acceptance is assessed when those artifacts exist.
