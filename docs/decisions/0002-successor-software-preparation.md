# Decision: separate local successor software preparation

## Authorized scope

On 2026-10-06 the owner authorized the reviewed v2 software task and repository
reconciliation in the existing session. The old simulation study remains closed
and v1.4 remains withdrawn. Public naming, physical start, work location, budget,
equipment and specimen availability, and endpoint selection remain pending.
This decision does not authorize a physical experiment or publication.

The successor question is whether qualified pressure retention adds predictive
value for independently measured functional failure beyond age and duty history
on unseen manufacturing batches. Initial defect screening and advance warning
are distinct questions. Blocked force is a proposed endpoint, subject to
specimen/application feasibility and owner selection.

## Executed local result

An independent git repository, with no remote, contains the calculations:

```text
/Users/redhose/Projects/critical-audit-20261002/implementation/pivot-v2-20261006/workspaces/soft-actuator-lifetime
branch: prep/pressure-metrology-20261006
commit: 98c4f299032f44d593f79774abdc3cc1ac3bfb14
```

This is a local review artifact. There is no public successor repository or
public download link. Relative to that directory:

| Artifact | Purpose |
|---|---|
| `parameters.json` | Source specifications and declared illustrative inputs |
| `sources/manifest.json` | Exact vendor/code URLs, versions, retrieval times and byte hashes |
| `metrology.py`, `results/metrology.json` | Executed sensor and gas-balance calculations, with input and implementation hashes |
| `plot_metrology.py`, `results/metrology-tradeoff.png` | Calculated resolution and temperature illustration, labeled theoretical and visually checked |
| `tests/test_metrology.py` | Independent equation, energy-balance, limiting-case and flow-conservation checks |
| `METHODS.md`, `README.md`, `ROADMAP.md` | Assumptions, reproduction commands, unresolved physical gates |

From that directory, use Python 3.11:

```sh
python metrology.py
python -m unittest discover -s tests -v
python -m pip install -r requirements-plot.txt
python plot_metrology.py
```

The source check distinguishes output-word size, transfer-dependent resolution,
error band, drift and repeatability. Pressure-decay calculations include thermal
and volume terms, flow sign and reference conditions. Closed compression and
rigid filling are separate examples; neither establishes a universal temperature
bound or waiting time. NAU7802 compatibility and pressure/force timing still
require the actual equipment configuration.

## Retained work and next gate

The [reference chamber](../../cad/reference-volume/DESIGN_NOTES.md) is CAD only;
physical ownership, manufacture and calibration are not established. The
[history index](../history/README.md) retains the original simulation outputs,
figure lineage, code, manuscript records and unrun proposals. No stored simulation
result or historical manuscript/PDF was changed by this successor work.

No measured blank, known leak, compliant-specimen response or independent
functional endpoint is available. The owner decisions in the [roadmap](../../ROADMAP.md)
precede physical qualification. The calculations do not establish a useful
failure precursor or authorize the later fatigue campaign.

## Dependency-plan adoption and cleanup

The owner subsequently authorized date-free dependency roadmaps and removal of
obsolete active work. The successor's full roadmap is now committed locally at
`93e40c9ff8ada334d83fe795fbd43de1206efa22`, branch `cleanup/dependency-roadmap`,
in the same independent repository above. Its metrology implementation, inputs,
results, sources and figure are unchanged from the executed result recorded here.

The adopted question is functional loss within N cycles on unseen batches.
Setup and endpoint decisions precede one-channel acquisition, independent probe
qualification, a development pilot, justified sizing and frozen whole-batch
confirmation. Each milestone states prerequisites and completion evidence.
The roadmap keeps the outgoing-flow sign and reference-state conditions,
conditional thermal waiting rule, proposed endpoint and unqualified sensor
specifications explicit.

The [retirement record](../history/README.md#retired-active-material) lists the
removed C2 extension, redundant plans and conceptual figure and links their
pre-cleanup source. Recorded results remain reproducible. This adoption leaves
all physical, funding, naming and publication decisions above unanswered.
