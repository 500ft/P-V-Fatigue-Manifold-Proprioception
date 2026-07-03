# P-V Fatigue Manifold Proprioception

## Overview
Simulation-only soft-robotics research package for pressure-volume loop health
monitoring and pressure-only proprioception in shared-manifold soft grippers.
The arXiv-facing manuscript is `docs/preprint_v1.md` / `docs/preprint_v1.pdf`.

## Commands
- Regenerate Study 3: `python -m scripts.run_study3`
- Render manuscript PDF: `python -m scripts.make_preprint_pdf`
- Check manuscript numbers against JSON: `python -m scripts.check_manuscript_numbers`
- Full tests in CI/Linux: `python -m pytest`
- Local Mac workaround: the `ENTER` Python environment segfaults during pytest's
  `readline` import; use `python -X faulthandler -c 'import sys, types; sys.modules["readline"] = types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main())'`.

## Conventions
- Keep `docs/result_spine.md` frozen; do not edit it to match post-audit wording.
- Keep the title as "health indicator"; temporal lead is threshold-dependent.
- Do not refine the deployed selection grid for arXiv v1.2: `tau_selected=0.05`,
  `TAU_GRID`, the policy table, `T*`, and budget claims are frozen.
- Every manuscript number must be asserted by `scripts/check_manuscript_numbers.py`
  against committed study JSONs.
- Exact test counts are volatile; keep them out of prose.

## Architecture Decisions
- [ADR 0001: Health-indicator title and lead frontier](docs/decisions/0001-health-indicator-title-and-lead-frontier.md)

## Current State (updated 2026-07-03)
- Goal: post the sim-only arXiv preprint after owner upload steps in `docs/SUBMISSION.md`.
- Done: Wave A and Wave A.2 landed on `main`; manuscript is Draft v1.2 with PDF rendered.
- Done: Study 3 now stores `lead_frontier_heldout`; CI verifies tests and manuscript numbers.
- Result: deployed `tau*=0.05` has no positive temporal lead, but lower thresholds buy lead
  at higher recalibration cost (`tau=0.01`: median lead +0.346 life, 3 recals/actuator).
- Next: owner uploads to arXiv, then records the arXiv ID in repo README/SUBMISSION/Progress.
- Gotchas: untracked `outreach/` may exist locally and is unrelated to paper commits.
