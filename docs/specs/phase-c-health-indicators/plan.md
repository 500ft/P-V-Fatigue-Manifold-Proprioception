# Phase C Health Indicators — Implementation Plan

Design: ./design.md
Status: done
Date: 2026-06-23

## Tasks

- [x] T01 — Add analytic loop-feature tests and implement feature extraction. (8 tests pass.)
- [x] T02 — Add recovery-fit tests and implement five-minute normalization. (7 tests pass.)
- [x] T03 — Add HI-metric fixtures and implement metrics with undefined guards. (6 tests pass.)
- [x] T04 — Implement causal baseline HI, fusion, and PCA comparators. (5 tests pass.)
- [x] T05 — Implement null/validation cohorts, noise, and alternate onset generators. (6 tests pass.)
- [x] T06 — Add detector tests and implement sustained-3σ plus matched-FA CUSUM. (5 tests pass.)
- [x] T07 — Add degradation-fit tests and implement model/AICc/sample guards. (5 tests pass.)
- [x] T08 — Implement `run_study1.py`, registered grids, and synthetic artifacts. (144-condition PASS.)
- [x] T09 — Update project documentation and complete regression/test report.

## Execution notes

Execute test-first. Leave the untracked `outreach/` directory untouched. Phase B remains
a separate logical checkpoint even though its changes are not committed yet.
