# P-V — tasks to completion

> **Objective.** Produce the strongest, most honestly-packaged evidence — not a completed
> project. Priority flows from leverage (does it unblock other work, or add decisive evidence)
> and from executability. Never from a calendar, and never from this project's ceiling.

Generated from an audit of the committed state of this repository. Every task is anchored to a
checked fact; no dates or estimates appear anywhere, by design.

## Two finish lines

**Ceiling.** A DOI'd submission accepted at RoboSoft 2027, with one physical specimen through the matched actuator protocol.

**Floor.** The simulation-only paper submitted with its scope stated by the authors rather than found by a reviewer — specifically the indicator invariance, in the abstract and limitations rather than only in section 4.4.

The floor is the realistic finish line for anything gated on a measurement, and its tasks are
listed alongside the ceiling's — so the project is presentable even if the measurement never
happens.

_12 tasks · 7 Tier 0 · 10 executable now._

**Gate types.** `preregister` — write the threshold down *before* the thing it judges;
`external` — needs a resource or a person outside this repo; `build` — new work;
`hygiene` — reproducibility debt.

**Tiers.** 0 finish · 1 package · 2 park. A task whose blocker is not secured cannot be Tier 0
however decisive it is, which is why several measurements sit in Tier 2 with their
preregistration in Tier 0 ahead of them.

---

## Tier 0 — finish

### PV-01 · Merge PR #1 (audit/cluster-aware-intervals)

`hygiene` · executable now

**Why it matters.** The committed interval resamples 30 points i.i.d. when the held-out sample is 6 actuator clusters, and the indicator-invariance check that explains the degenerate statistics is not yet on main.

**What it adds.** Intervals whose resampling unit matches the design, and a computed check that stops the saturated quality metrics being quoted as evidence.

**Done when.** main carries the cluster CI and check_manuscript_numbers.py gates four documents.

### PV-02 · Commit the widened cohort-dispersion coefficients to a hashed spec, before any rerun

`preregister` · executable now · after PV-01

**Why it matters.** The normalized indicator is invariant to every actuator parameter to ~1e-13, so the cohort has only 5 distinct x values. That single fact produces the degenerate recalibration interval, the near-identical per-actuator correlations and the saturated quality metrics a reviewer will catch. Choosing the spread after seeing the new r reads as p-hacking.

**What it adds.** Turns the interval from a post-hoc artifact into a defensible preregistered estimate.

**Done when.** Coefficients committed with a hash and their source (fabrication literature or your own specimens), no results generated.

### PV-03 · Rerun study 3 on the widened cohort and update every downstream number from the JSON

`build` · executable now · after PV-02

**Why it matters.** r, all three intervals, the per-actuator spread, the savings ratio and the lead frontier all move together; updating by hand is how they drift apart.

**What it adds.** A statistically meaningful interval rather than an artifact of the simulator.

**Done when.** Rerun committed and check_manuscript_numbers.py passes with every figure regenerated.

### PV-04 · Decide the tau-selection rule on the evidence in draft PR #2

`build` · executable now · after PV-03

**Why it matters.** The deployed rule warns on 0 of 14 training trajectories, and the only threshold that warns is the always policy - so on this cohort the trade is savings or prognosis, not a balance between them. Leaving it undecided leaves the paper recommending a threshold with negative lead.

**What it adds.** Either a defended operating point or an explicit statement that no threshold on this grid both warns and saves.

**Done when.** The rule is either changed with both rules reported, or kept with the trade stated in the manuscript.

### PV-06 · Commit the matched actuator protocol before fabricating a specimen

`preregister` · executable now · after PV-04

**Why it matters.** One specimen can only test the model if what counts as agreement is fixed first.

**What it adds.** Makes a single specimen decisive rather than illustrative.

**Done when.** Protocol and agreement band committed, nothing fabricated.

### PV-07 · State what a specimen disagreement would mean

`preregister` · executable now · after PV-06

**Why it matters.** A result that cannot embarrass the model is not evidence for it.

**What it adds.** A named falsification condition, which is what separates a validation from a demonstration.

**Done when.** The disagreement interpretation is committed alongside the protocol.

### PV-11 · Submit v2 to RoboSoft 2027

`external` · executable now · after PV-10

**Why it matters.** Submission is the external confirmation this project is aimed at.

**What it adds.** Peer review - the first judgement from outside the project.

**Done when.** Submitted, with the submitted commit tagged.

## Tier 1 — package

### PV-05 · Replace the dataset byte-hash pin with a per-array check

`hygiene` · executable now

**Why it matters.** The npz byte hash changes between runs from zip timestamps, so the manifest pin fails for a reason unrelated to the data.

**What it adds.** An integrity check that only fires when the data actually changes.

**Done when.** The check compares arrays, and two consecutive regenerations pass.

### PV-09 · Re-scope every simulation-only claim against the specimen

`build` · **blocked-on-fabrication** · after PV-08

**Why it matters.** After a measurement exists, unlabelled claims silently borrow its credibility.

**What it adds.** A manuscript in which each claim's evidence class is explicit.

**Done when.** Every claim marked simulation-only, specimen-anchored or contradicted.

### PV-10 · Package the simulation-only floor for submission

`build` · executable now · after PV-04

**Why it matters.** If no specimen is fabricated the paper must still be submittable, with the synthetic scope stated rather than glossed.

**What it adds.** A submittable paper whose limitations are stated by the authors rather than found by a reviewer - the honest finish line without a specimen.

**Done when.** The manuscript states the synthetic-cohort scope and the indicator invariance in the abstract and limitations.

### PV-12 · Obtain a DOI and keep arXiv in sync

`hygiene` · executable now · after PV-11

**Why it matters.** An uncitable paper cannot accumulate the citations the ceiling is defined by.

**What it adds.** A stable citable identifier.

**Done when.** DOI issued and the arXiv version matches the submitted commit.

## Tier 2 — park

### PV-08 · Run one physical specimen through the protocol

`external` · **blocked-on-fabrication** · after PV-07

**Why it matters.** Every number is simulation on a synthetic cohort. One specimen is the difference between a modelling paper and a validated one.

**What it adds.** The ceiling: physical evidence for the manifold claim.

**Done when.** Specimen data committed and scored against the PV-06 band unchanged.

---

## Cross-cutting

These span repositories and are tracked identically in the others they touch.

### XC-01 · Reconcile the repo, portfolio and resume headline numbers

`hygiene` · executable now

**Why it matters.** A reviewer clicks between the three, and a disagreement there is more damaging than any single wrong number because it looks like carelessness rather than a stale file. Checked so far: the portfolio quotes 174.7 Hz (matches the repo - 163.8 Hz was the 0.20 kg placeholder tip mass, not drift) and r = 0.885 (matches), and makes no drone-mass claim. The resume was not available to check.

**Done when.** Every headline number in the portfolio and resume traced to a committed artifact, with any disagreement fixed at the source.

