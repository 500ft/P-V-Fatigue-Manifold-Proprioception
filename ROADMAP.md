# Roadmap

Work history is in [docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md); the
review record is [docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

Reached on 2026-10-02. The owner chose to stop the paper and keep the code. The
project ends as a reproducible simulation pipeline plus an audit of its own
headline: at matched recalibration cost, a cycle-count clock ties the P-V
trigger ([withdrawal note](docs/corrections/v1.4-withdrawn-2026-10-02.md)).

## Where it stands

- The recalibration-policy studies and the observability follow-ups are done,
  and their numbers are kept unchanged.
- A clock every 2,400 cycles gives the P-V trigger's exact recalibration
  schedule and error on all 20 actuators. The health signal is the simulator's
  compliance multiplier read back out.
- v1.4 is withdrawn: not rendered for release, not approved, not deposited.
  The archived v1.3 release keeps its methods correction.

## Close-out status

| Step | Status |
|---|---|
| Point the portfolio and resume at the audit result | Complete on [Portfolio main](https://github.com/500ft/Portfolio/tree/96da45f65e0748f40767ed473d1e81677dfcfdb1), including merged [PR #3](https://github.com/500ft/Portfolio/pull/3) |
| Correct the Libby citation and dependent measurement claims | Corrected in the manuscript sources and [literature review](docs/A01_A04_Literature_Review.md#libby-full-text-check); the precursor and volume gates remain unresolved |

No implementation work remains in this scope. Any new hardware study requires
an owner decision; the literature correction does not reopen the paper.

## Not in this version

- Any v1.4 release, Zenodo deposit or arXiv submission.
- Study C2. It is designed and coded, but its grid has not been run.
- Physical actuators. A hardware study (a real chamber cycled to failure, with
  rest time and temperature varied) is a separate decision about continuing
  the research. The known-volume reference chamber CAD is kept for it.
- The prospective v2 claim spine ([specs/robosoft-v2](docs/specs/robosoft-v2/claim-spine.md)).
