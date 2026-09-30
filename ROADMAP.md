# Roadmap

This is the plan for finishing the project. The review packet is
[docs/REVIEW_READY.md](docs/REVIEW_READY.md); publication status is recorded in
[docs/publication-readiness.json](docs/publication-readiness.json); work history
is in [docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md).

## Finish line

The project is finished when the corrected v1.4 manuscript has been reviewed by
the author, rendered as its own versioned PDF, approved, and deposited with a
DOI. The simulation work is complete; no new study is needed to finish.

## Where it stands (2026-09-30)

- The recalibration-policy studies are done. The headline result: the
  P-V-triggered policy meets the error budget with 2 recalibrations per
  actuator against 5 for always-on, but gives no early warning at the deployed
  threshold.
- The observability follow-ups are done. Study A passes only under an amended
  rule, which is a changed criterion rather than a better result. Study B's
  post-onset precision is not established, and its two resolution figures were
  withdrawn. Study C's life estimator fails its transfer test.
- The archived v1.3 manuscript overstated the method (the trigger read an
  idealized, noise-free probe). Publication has been on hold since 2026-09-05.
- The v1.4 candidate was refreshed on 2026-09-29 with all of the above and is
  ready for review.
- arXiv requires an endorser for a first submission. None has been found, so
  Zenodo is the deposit route ([fallback plan](docs/ZENODO_FALLBACK.md)).

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Review the [v1.4 candidate](docs/preprint_v1_4_candidate.md), mainly the abstract, §3.10, §4.6 and the conclusion, and fill in the [response fields](docs/COMPLETION_RECONCILIATION.md#owner-response--not-submitted) | Owner | Response submitted. **Current step.** |
| 2 | Apply the review edits and render the reviewed PDF as a separately versioned file | Agent | PDF, source and manifest hashes agree; readiness record updated |
| 3 | Approve that exact PDF, identified by its hash | Owner | Approval recorded in the readiness record |
| 4 | Deposit on Zenodo and tag the v1.4 release. Submit to arXiv as well only if an endorser is found | Owner deposits; agent prepares the metadata | DOI recorded |
| 5 | Point the README, `CITATION.cff` and the portfolio at v1.4 | Agent | Merged |

## Not in this version

- Study C2. It is designed and coded, but its grid has not been run.
- Physical actuators. The known-volume reference chamber is the only CAD part,
  kept for future hardware work; specimen and mould CAD stay deferred.
- The prospective v2 claim spine ([specs/robosoft-v2](docs/specs/robosoft-v2/claim-spine.md)).
