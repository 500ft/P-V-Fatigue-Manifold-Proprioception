# Phase B Fatigue Model — Implementation Plan

Design: ./design.md
Status: done
Date: 2026-06-21

## Tasks

- [x] T01 — Encode fatigue-law acceptance tests in `tests/test_fatigue.py`. (22 focused tests pass.)
- [x] T02 — Implement `sim/fatigue.py` state law, validation, and immutable adapters.
- [x] T03 — Encode and implement closed-valve pressure-decay behavior in `sim/plant.py`.
- [x] T04 — Implement `scripts/phaseB_fatigue_demo.py` and generated artifacts. (Demo PASS.)
- [x] T05 — Update project-facing simulation documentation.
- [x] T06 — Run the complete test suite and record acceptance coverage. (See `test-report.md`.)

## Execution notes

Execute test-first. Treat monotonic trajectories as consistency checks, not physical
validation. Preserve the user's untracked `outreach/` directory.
