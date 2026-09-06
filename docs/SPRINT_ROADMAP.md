# P-V-Fatigue-Manifold-Proprioception — Six-day evidence-integrity sprint

## Separate CAD phase — added 2026-09-06

Individual mechanical work orders now live in [CAD_PLAN.md](CAD_PLAN.md), with their own authoritative [CAD_TASKS.csv](CAD_TASKS.csv). They are additional, unexecuted work outside this original 30-hour integrity sprint. Existing physical-readiness and publication gates remain open until their actual evidence arrives.

Prepared: 2026-09-05. Budget: 30 focused hours; optional Day 7 adds at most 4 hours for owner review only. Days are effort groupings, not unattended calendar commitments. Status lives only in [SPRINT_TASKS.csv](SPRINT_TASKS.csv).

## A. Outcome and baseline identity

A reproducible, corrected interpretation of the v1.3 simulation record with a fail-closed publication-readiness boundary and a bounded prospective v2 scope; no new physical or generalization claim.

Publication-state update (2026-09-06): the owner authorized local commits, branch
pushes, and pull requests for this sprint. This does not authorize deployment,
research publication, outreach, spending, or any blocked physical/data action.

Audience: engineering/research reviewer and graduate-application portfolio reader.
Canonical sprint checkout: `/Users/redhose/Developer/research-sprints/2026-09-05/P-V-Fatigue-Manifold-Proprioception`.
Remote: https://github.com/500ft/P-V-Fatigue-Manifold-Proprioception. Base: `88d24358bc385dc66c2c0a9ab3c295b059d13427`.
Branch: `sprint/evidence-integrity-20260905`. Prepared from freshly fetched origin/main, not from original dirty drafts.
Original checkout: `/Users/redhose/P-V-Fatigue-Manifold-Proprioception`; preserved. New sprint checkout was clean before evidence capture. No commit, push, publication, purchase, deployment or outreach is claimed or planned as an automatic action.

## B. Verified baseline and priority gaps

Verified: Study 3 calls pipeline/coupling.py health_trajectory with rest=0 and clean pv_loop; docs/preprint_v1.md attributes noise/quantization/rest robustness to that signal. The baseline checker passes payload integrity while all publication identifiers are null. Original checkout contains uncommitted author drafts; none are incorporated automatically.

Sources inspected: [pipeline/coupling.py](../pipeline/coupling.py), [scripts/run_study3.py](../scripts/run_study3.py), [scripts/check_publication_fallback.py](../scripts/check_publication_fallback.py), [docs/preprint_v1.md](../docs/preprint_v1.md), [docs/zenodo-manifest.json](../docs/zenodo-manifest.json).
[Actual baseline command outputs](../evidence/sprint-2026-09-05/baseline.json) record working directories, runtime versions, outputs and exit statuses. Alleged defects become reproduced failures only when the red tests record them. Test counts are not research performance.

Verified existing commands (repository root; local Python may need the recorded readline workaround):

```sh
python -c 'import sys, types; sys.modules["readline"] = types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["-q"]))'
python -m scripts.check_manuscript_numbers
python -m scripts.check_pdf_arxiv
python -m scripts.check_publication_fallback
```

No separately configured typechecker/linter was found in this scoped configuration. Use compileall for changed Python, relevant tests, existing CI commands and `git diff --check`; do not call syntax compilation a typecheck. Proposed test/CLI paths below do not exist until implemented.

## C. Scope, ownership and critical path

Must-haves: repaired claim/validation boundary; regression evidence including original failures; consistent operative scope; reproducible local delivery/check commands; review index identifying unresolved external work.
Exclusions: No v1.3 numerical rerun, silent replacement of historical PDF, DOI publication, arXiv submission, hardware acquisition, or full seven-baseline v2 benchmark.
Owner/External dependencies: Author reconciliation of dirty drafts, final PDF approval and publication account action. Existing local v2 documents are reported uncommitted, not adopted as preregistration.
Critical path: baseline → regression failure → minimal correction → full affected checks → candidate identity/selection freeze → bounded evaluation → review packet. Prepare owner requests on Day1; replies do not block independent code fixes. External feedback is not presumed.

## D. Daily budget

| Day | Hours | Primary deliverable |
|---|---:|---|
| 1 | 5 | Baseline, scope and owner dependency checklist |
| 2 | 5 | Correct the active methods interpretation and fail-closed publication check |
| 3 | 6 | Prepare corrected manuscript text and bounded prospective design |
| 4 | 4 | Freeze a review candidate and verify delivery boundaries |
| 5 | 6 | Run bounded counterexample evaluation |
| 6 | 4 | Review packet (2 Agent hours) and owner feedback (2 Owner hours) |
| Total | 30 | Local evidence-ready candidate or explicitly partial handoff |

## E. Ordered tasks and done conditions

### PV-01 — Day 1: Capture baseline and reproduce audit hypotheses

Priority: P0 · Owner: Agent · Focused hours: 3 · Depends on: none.
Files: pipeline/coupling.py; scripts/run_study3.py; scripts/check_publication_fallback.py; docs/preprint_v1.md; docs/zenodo-manifest.json.
Deliverable / Done when: Record base identity, clean sprint start, versions, exact CI commands and observed outputs; preserve original worktree changes.
Verification: python -c 'import sys, types; sys.modules["readline"] = types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["-q"]))'
python -m scripts.check_manuscript_numbers
python -m scripts.check_pdf_arxiv
python -m scripts.check_publication_fallback
Evidence to retain: evidence/sprint-2026-09-05/baseline.json.

### PV-02 — Day 1: Freeze scope and evidence-first execution design

Priority: P0 · Owner: Agent · Focused hours: 2 · Depends on: PV-01.
Files: NEW docs/SPRINT_ROADMAP.md; NEW docs/SPRINT_TASKS.csv; NEW docs/SPRINT_PROGRESS.md; NEW docs/REVIEW_READY.md.
Deliverable / Done when: Six-day30h plan saved, requirements testable, user-provided plan-and-execute authorization recorded, external authority excluded.
Verification: Review this roadmap and parse task CSV; hours sum to30.
Evidence to retain: docs/SPRINT_ROADMAP.md.

### PV-03 — Day 2: Correct the active methods interpretation and fail-closed publication check

Priority: P0 · Owner: Agent · Focused hours: 5 · Depends on: PV-02.
Files: scripts/check_publication_fallback.py; README.md; docs/results.md; docs/data-and-figures.md; NEW tests/test_publication_readiness.py; NEW docs/corrections/v1.3-methods-2026-09-05.md; NEW docs/publication-readiness.json.
Deliverable / Done when: Regression proves historical integrity is not publication readiness; standalone historical PDF remains blocked; original PDF SHA unchanged; active wording distinguishes clean health probe from noisy pose channels.
Verification: python -m pytest tests/test_publication_readiness.py -q; python -m scripts.check_publication_fallback; python -m scripts.check_publication_fallback --for-publication (expected nonzero until owner gate)
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### PV-04 — Day 3: Prepare corrected manuscript text and bounded prospective design

Priority: P0 · Owner: Agent · Focused hours: 6 · Depends on: PV-03.
Files: NEW docs/preprint_v1_4_candidate.md; NEW docs/specs/v2-integrity-core/design.md; docs/results.md.
Deliverable / Done when: Corrected text removes unsupported noisy-probe/rest claims and defines macro-averaged RMSE; minimum scope covers three mechanisms/four policies and train-only selection; no backdated freeze or fabricated result.
Verification: Compare candidate with historical docs/preprint_v1.md; inspect code lineage; regression assertions cover the corrected paragraphs.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### PV-05 — Day 4: Freeze a review candidate and verify delivery boundaries

Priority: P1 · Owner: Agent · Focused hours: 4 · Depends on: PV-04.
Files: NEW evidence/sprint-2026-09-05/candidate.json; docs/REVIEW_READY.md.
Deliverable / Done when: Record source tree/diff identity and selected artifact hashes, preserve old PDF bytes; distinguish corrected Markdown from unrendered/unapproved submission PDF.
Verification: git diff --check; python -m scripts.check_manuscript_numbers; python -m scripts.check_pdf_arxiv
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### PV-06 — Day 5: Run bounded counterexample evaluation

Priority: P1 · Owner: Agent · Focused hours: 6 · Depends on: PV-05.
Files: NEW evidence/sprint-2026-09-05/evaluation-plan.md; NEW evidence/sprint-2026-09-05/evaluation.json; tests/test_publication_readiness.py.
Deliverable / Done when: Freeze candidate and input selection before new cases; exercise malformed readiness records, missing attachments, stale hashes and manipulated state fields; label all viewed cases development and any fixes invalidate that candidate evaluation.
Verification: python -m pytest tests/test_publication_readiness.py -q; independent reviewer repeats the recorded CLI negative cases.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### PV-07 — Day 6: Assemble review packet and reconcile remaining publication work

Priority: P1 · Owner: Agent · Focused hours: 2 · Depends on: PV-06.
Files: docs/REVIEW_READY.md; docs/SPRINT_PROGRESS.md; docs/SPRINT_TASKS.csv.
Deliverable / Done when: All implemented changes have checks; unresolved author/PDF/publication actions explicitly blocked, no claim of a released correction.
Verification: Run all baseline commands and git diff --check; review repository-relative evidence links.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### PV-08 — Day 6: Author review and publication decision

Priority: P1 · Owner: Owner · Focused hours: 2 · Depends on: PV-07.
Files: docs/publication-readiness.json; docs/preprint_v1_4_candidate.md.
Deliverable / Done when: Owner reconciles original drafts, reviews correction and decides corrected PDF/DOI path; no duplicate deposit; only reviewed new artifact may be cleared.
Verification: Owner compares original drafts and corrected candidate; publication account action is not authorized in this session.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.


## F. Evaluation and overrun policy

Existing audit counterexamples and all tests inspected while fixing are development evidence, not held-out evaluation. Before Day5, freeze a candidate source/diff identity and selection procedure; save expected judgments before predictions where meaningful. Any observed case used to fix the candidate becomes development material; record that and select new cases for a revised candidate. Hashes identify bytes, not independence. No AI peer is called an independent human reviewer.

If the implementation consumes extra time, cut optional model breadth, cosmetic changes and additional fixtures; never relax numerical thresholds, remove rejection checks or relabel missing measurements. Day7 may add up to4 owner-review hours (34 maximum) only by explicit rebaseline. Do not convert lab lead time into nominal coding hours. Stop affected work at missing authority; proceed with independent authorized tasks. Unavailable external evidence produces a partial handoff, not a completed empirical claim.

Follow-up review checks: reproduce original failures and repaired counterexamples, repeat real commands, inspect runtime and evidence provenance, distinguish local tests from hosted/deployed/physical outcomes, and assess scientific wording independently.

## G. Execution record and first action

[Ledger](SPRINT_TASKS.csv) · [Progress](SPRINT_PROGRESS.md) · [Review index](REVIEW_READY.md).
First behavior-changing action: PV-03; write its regression input, observe failure on baseline, then make the minimal correction. User has authorized plan-and-execute now. No additional start confirmation is required for this bounded scope.
