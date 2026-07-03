# Revision Plan — preprint v1.1 (pre-arXiv) and v2 (RoboSoft package)

_Written 2026-07-02, after the internal review that added the clock baseline,
the contact-F1 fix, and the §5 falsifiability bullet. This plan sequences the
remaining improvements into two waves with explicit gates. Wave A blocks the
arXiv upload; Wave B is the RoboSoft-deadline package and does NOT block it._

## Ground rules (apply to every item)

- Every number that appears in the manuscript is re-verified against the
  study JSONs after any dataset or study change (`data/sim/phaseD/*.json`).
- `python -m pytest` green before any commit; new analysis gets new tests.
- PDF re-rendered (`python scripts/make_preprint_pdf.py`) after any text edit.
- The 5-stage dataset and its committed results stay untouched until Wave B
  deliberately supersedes them — Wave A adds analysis, it does not regenerate.
- **Execute from updated `main`.** The owner's local checkout sits on
  `codex/phase-c-health-indicators` at `b45d162`, 5 commits behind origin/main
  (which carries the merged preprint, SUBMISSION.md, and this plan). Fix
  before touching anything locally:
  `git checkout main && git pull` (the codex branch is fully merged; safe to
  delete or leave).

---

## Wave A — before the arXiv upload (~half a day, all from existing data)

**Executed 2026-07-03.** A1/A2 were added from the existing 5-stage data; the
lead-time audit found no positive temporal lead under the deployed τ\*=0.05
threshold (6/6 held-out actuators nonpositive), so the manuscript wording was
downgraded from "leading indicator" to "health indicator" where temporal lead
was implied. A3/A4/A5 were completed with the v1.1 manuscript/PDF, number-check
script, and CI workflow.

### A1. Quantify the lead time (closes the "leading vs correlated" gap) — HIGHEST VALUE

**Why.** §2 promises a "cycle-resolved leading indicator with *quantified lead
behavior*"; §4.4 delivers a pooled same-stage correlation, which is symmetric
in time and demonstrates no lead. This is the strongest remaining referee
attack and it is answerable from existing data.

**Crossing definitions (fixed here so the code has no latitude):**
- *Trigger crossing* = the first life fraction where the fractional loop-area
  growth **from the young calibration** exceeds the policy's actual
  train-selected τ\* — i.e., exactly when the triggered policy takes its first
  recalibration. Not a re-derived threshold; the deployed one.
- *Budget crossing* = the first life fraction where the **young/fixed-
  calibration** pose error (`err[i][0]`) exceeds `accuracy_budget_mm`. This is
  the clean "indicator leads degradation" comparison: both trajectories start
  from the same young state and neither is contaminated by recalibration.

**How.**
1. New function in `pipeline/coupling.py`:
   `lead_time(health_norm, errors_fixed_cal, tau, budget_mm, life_fractions)`
   with crossings linearly interpolated between the 5 stages (state the
   interpolation honestly; the stage grid bounds resolution at ±0.1 life).
2. In `scripts/run_study3.py`: compute for the 6 held-out actuators; store
   **raw per-actuator records, not just summaries** —
   `lead_time_heldout: {per_actuator: [{actuator_id, rupture_cycles,
   trigger_life, budget_violation_life, lead_life, lead_cycles, status}],
   median_lead_life, min, max, n_excluded}` where `status` ∈
   {`ok`, `never_triggers`, `never_violates`, `nonpositive_lead`} and
   `lead_cycles = lead_life × rupture_cycles` (per-actuator, not median-life
   converted). Excluded statuses are counted, never silently dropped.
3. Manuscript §4.4: one added sentence + inline numbers — "the trigger fires at
   life X.XX [range] while the budget is violated at X.XX [range]; median lead
   ≈ X.X of normalized life (≈N–M cycles across the held-out rupture lives)".
   If any actuator shows `nonpositive_lead`, report it — that IS the result.
4. Tests: synthetic monotone health/error arrays with a known crossing gap;
   each degenerate status; interpolation correctness at an exact stage hit.

**Gate:** the word "leading" in the abstract/§2/§4.4 is backed by a reported
lead statistic, or the wording is downgraded. Either outcome closes the item.

### A2. Per-actuator correlations beside the pooled r

**Why.** Pooled r = 0.885 mixes within-actuator life trends with
across-actuator scatter (ecological-correlation objection).

**How.** In `run_study3.py`, compute Pearson r per held-out actuator (5 points
each) on (loop-area growth, fixed-cal error); store
`per_actuator_r: {values, median, min, max}`. Manuscript §4.4: one sentence,
**deliberately modest** — 5 points per actuator shows the within-actuator
*structure* is consistent with the pooled result; it cannot support strong
per-actuator inference and the sentence must not imply it. No per-actuator CIs
(they would be meaningless at n=5); just the six values' median and range.
Test: per-actuator r of a constructed dataset with one deviant actuator.

**Gate:** §4.4 reports both pooled and per-actuator statistics with the small-n
caveat inline.

### A3. "Pre-registered" → "pre-specified" (2 occurrences: lines ~81, ~339)

**Why.** The spine was frozen in-repo (self-specification), not externally
registered; the term invites a pointless fight.

**How.** Replace both with "pre-specified (frozen in `docs/result_spine.md`,
commit `d856455`, before result write-up)". **Precision note:** `d856455` adds
both the spine and the dataset generator/artifacts, so git alone cannot prove
"before dataset generation" — do not claim it. "Before result write-up" is
what the history does prove (the spine predates the study results and the
preprint commits) and is the part that matters for the pre-specification
claim. Keep the claim's substance; drop the loaded term and the unprovable
ordering.

**Gate:** `grep -c "pre-registered" docs/preprint_v1.md` returns 0, and the
replacement claims only git-provable ordering.

### A4. Kill the test-count drift (and the drift class)

**Why.** Three documents currently state three different test counts —
manuscript §7 says 125, `SUBMISSION.md` says 129, the suite is at 131. Nobody
lied; the counts were each true when written. Hardcoded volatile numbers in
prose are the bug.

**How.**
1. Remove exact test counts from *prose*: manuscript §7 → "the full unit-test
   suite gates the pipeline (count and status in CI)"; `SUBMISSION.md`
   pre-upload check → "`python -m pytest` fully green" with no number.
   Exact counts stay in commit messages, where they are timestamped claims.
2. New `scripts/check_manuscript_numbers.py`: asserts every load-bearing
   manuscript number against the study JSONs — r + CI bounds, the four-policy
   table values, τ\*, T\*, budget, and (after A1/A2) the lead and per-actuator
   figures. Exits nonzero on any mismatch. This automates the SUBMISSION.md
   verification step instead of trusting a human to re-grep.
3. Minimal CI (`.github/workflows/ci.yml`): pytest + the number-check script
   on push/PR. The repo currently has **no CI at all** — every "N tests pass"
   claim so far has been a local, unrepeated assertion. MechAudit's workflow
   is the in-portfolio template.

**Gate:** `check_manuscript_numbers.py` passes; CI green on main; no volatile
count remains in prose.

### A5. Wave-A wrap

- Re-render PDF; bump the status block to "Draft v1.1 (2026-07-0X)".
- Run `scripts/check_manuscript_numbers.py` as the verification step (A4).
- Commit, push, confirm CI green, then the owner uploads per
  `docs/SUBMISSION.md` — from **updated main**, not the stale codex branch.

---

## Wave B — the RoboSoft package (2–4 sessions; does not block arXiv)

Do these only when the RoboSoft deadline is real. Order matters: B1 first (it
changes no committed numbers), then B2 (which changes ALL of them), then B3–B4.

### B1. Study 5 — probe-robustness sweep (highest-value new experiment)

**Why.** §5 now *argues* that probe noise/quantization could have degraded r;
the natural referee follow-up is "so where does it die?" A sweep converts the
qualitative defense into an operating envelope — the same move study 4 made
for the cross-talk null.

**How.** New `scripts/run_study5.py`: hold the dataset fixed; recompute the
*observable* health trajectory under swept probe conditions — sensor-noise
multiplier ×{0.5, 1, 2, 4, 8}, quantization step ×{1, 2, 4}, drive amplitude
`amplitude_frac` ∈ {0.05, 0.1, 0.2} (`pv_loop_area` already parameterizes
amplitude; noise/quantization enter via the sensor model applied to the probe
signal — small extension to `pipeline/coupling.py`, seeded). For each
condition: pooled held-out r + CI, and whether the τ\*-triggered policy still
meets the budget. One figure (r vs condition, budget-pass shading) → Fig. 6;
one results JSON; tests for the probe-corruption path.

**Gate:** the manuscript can state "the indicator survives probe noise up to
×N and dies at ×M" with a figure behind it.

### B2. Densify life stages: 5 → 9 (regenerates the dataset — all numbers move)

**Entry condition (hard):** a real, dated RoboSoft deadline exists and the
decision to submit has been taken. 9 stages is scientifically better, but
after arXiv v1 is public every regeneration creates version-management
overhead (two citable number sets, an errata-shaped diff to explain). Without
an active venue deadline the cost is not worth paying — B1, B3 and even B4
are all doable against the 5-stage build.

**Why.** Five stages integer-quantizes recal counts, the clock comparison, and
the A1 lead statistic (±0.1 life). Nine stages ({0.1..0.9} step 0.1) roughly
halves the quantization at pure compute cost (2,000 → 3,600 traces).

**How.** `LIFE_FRACTIONS` in `scripts/phaseD_dataset.py` and `LIFE` in
`run_study2/3.py`; regenerate (deterministic, new manifest `npz_sha256`);
rerun studies 2, 3, 5; re-verify EVERY manuscript number (abstract r, CI,
policy table, τ\*, T\*, lead times, per-actuator r); regenerate Figs 1–4 and 6.
**Risk:** headline drift — if r or the policy ordering shifts materially,
report the new numbers and note the stage-count sensitivity; do not cherry-pick
the grid that looks better. Keep the 5-stage v1.1 numbers quotable via the
arXiv v1 record.

**Gate:** full re-verification checklist in `SUBMISSION.md` passes on the
9-stage build; a manuscript footnote states the stage-grid change from v1.

### B3. Orientation error metric

**Why.** Evaluation is tip-position only; PCC yields full SE(3); soft-robotics
reviewers ask by default.

**How.** `pcc_transform` already returns the rotation; add geodesic
orientation error (angle of R_predᵀR_true) to `pose_rmse`-style evaluation in
studies 2–3; report alongside position in Fig. 2 and the §4.5 table (or a
compact appendix table if it clutters). Tests: known curvature pairs → known
angle.

**Gate:** every place position RMSE is reported, orientation RMSE is available
(inline or appendix), and the §2 conventions sentence is updated to match —
no repeat of the F1 inconsistency.

### B4. IEEE two-column reflow (owner + Overleaf)

**Why.** RoboSoft requires ieeeconf LaTeX; the reportlab render is
arXiv-adequate only.

**How.** Owner creates an Overleaf ieeeconf project; port section-by-section
from `preprint_v1.md` (it is already IEEE-shaped: abstract/intro/related/
methods/results/discussion/conclusion/refs); figures drop in as the committed
vector PDFs (`data/sim/phaseD/*.pdf`); references have DOIs ready for BibTeX.
Expect a length pass — RoboSoft is 6+references; §3 phase summaries and §5
bullets are the compression targets. No local toolchain exists for this; it
cannot be automated here.

**Gate:** compiled ieeeconf PDF within page budget, numbers identical to the
9-stage build.

### Explicitly NOT in scope (decided, recorded)

Contact-state estimator (new scope; honestly descoped in §2) · additional
corrector architectures (Phase E settled it) · hardware anchor (separate
campaign, trigger-gated on lab access — see `ROADMAP.md`) · figure styling
beyond a budget line on Fig. 4.

---

## Sequence summary

| Wave | Items | Effort | Blocks |
|---|---|---|---|
| A | A1 lead time · A2 per-actuator r · A3 wording · A4 number/CI hygiene · A5 wrap | ~½ day | arXiv upload |
| B | B1 probe sweep → B2 9-stage regen (**only under an active RoboSoft deadline**) → B3 orientation → B4 IEEE reflow | 2–4 sessions + owner Overleaf | RoboSoft submission |

_Revised 2026-07-03 after owner review: A1 raw per-actuator schema + explicit
crossing definitions; A2 modesty constraint; A3 git-provable wording only;
A4 added (test-count drift + number-check script + CI — the repo had none);
B2 hard-gated on an active deadline; execute-from-main note added._
